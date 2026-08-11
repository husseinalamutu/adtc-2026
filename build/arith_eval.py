#!/usr/bin/env python3
"""Arithmetic eval for the GGUF — the companion gate to fact_eval.py.

fact_eval measures Nigeria FACT RECALL. This measures the other half of the accuracy
score: can the model actually do the back-office arithmetic it claims to? Until now that
was spot-checked by hand, which is exactly how the partial-payment-carry defect survived
into the shipped model — it was never a gate because it was never measured.

Every case is scored on the EXACT figures a correct answer must contain, plus the wrong
figures a failing model characteristically produces (a carry that forgets the remainder
reports 0; a model that ignores the second invoice reports the first one's balance).
Greedy decoding, so results are reproducible.

Usage: python3 arith_eval.py [--model gguf/model-Q4_K_M.gguf] [--out results/...]
"""
import argparse
import datetime
import os
import re
import subprocess
from pathlib import Path

LLAMA_CLI = os.environ.get(
    "LLAMA_CLI", str(Path.home() / "adtc-local/llama.cpp/build/bin/llama-cli"))

# (id, topic, question, must[], must_not[], note)
CASES = [
    # --- VAT / quoting ---
    ("vatcalc-1", "vat_math",
     "Draft a quote for 10 bags of cement at NGN 8,500 each with 7.5% VAT.",
     [r"85[,\s]?000", r"6[,\s]?375", r"91[,\s]?375"], [],
     "10x8500=85,000; VAT 6,375; total 91,375"),
    ("vatcalc-2", "vat_math",
     "A customer buys 3 items at NGN 12,000 each. Add 7.5% VAT. What is the total?",
     [r"36[,\s]?000", r"2[,\s]?700", r"38[,\s]?700"], [],
     "36,000 + 2,700 = 38,700"),
    ("vatcalc-3", "vat_math",
     "My invoice subtotal is NGN 240,000. How much VAT do I add and what is the total?",
     [r"18[,\s]?000", r"258[,\s]?000"], [],
     "VAT 18,000; total 258,000"),

    # --- reconciliation: exact clear (the declared p1 class) ---
    ("rec-1", "reconciliation",
     "A customer paid NGN 127,500 by MTN MoMo. They have two unpaid invoices: "
     "INV-114 for NGN 85,000 and INV-121 for NGN 42,500. Does this payment clear both, "
     "and what is still outstanding?",
     [r"(?:no(?:thing)?|zero|0\.00|NGN\s*0\b|nil)"],
     [r"42[,\s]?500\s*(?:is\s*)?(?:still\s*)?(?:outstanding|remain|due)"],
     "both clear exactly; outstanding must be zero"),
    ("rec-2", "reconciliation",
     "A payment of NGN 45,000 arrived. The only open invoice is INV-2001 for NGN 45,000. "
     "Is it settled?",
     [r"(?:settled|cleared|paid|yes)"], [],
     "exact single match"),

    # --- reconciliation: PARTIAL PAYMENT WITH CARRY (the known defect) ---
    ("carry-1", "partial_payment",
     "A customer paid NGN 100,000. They owe INV-201 for NGN 85,000 and INV-202 for "
     "NGN 42,500. Apply the payment to the oldest invoice first. Exactly how much is "
     "still unpaid in total?",
     [r"27[,\s]?500"],
     [r"(?<![\d,])0(?:\.00)?\s*(?:naira|NGN)?\s*(?:is\s*)?(?:still\s*)?(?:unpaid|outstanding|owed|remain)",
      r"42[,\s]?500\s*(?:is\s*)?(?:still\s*)?(?:unpaid|outstanding)"],
     "100,000 - 85,000 = 15,000 applied to INV-202 -> 27,500 remains"),
    ("carry-2", "partial_payment",
     "I received NGN 60,000 against an invoice of NGN 95,000. How much does the customer "
     "still owe on it?",
     [r"35[,\s]?000"], [],
     "95,000 - 60,000 = 35,000"),
    ("carry-3", "partial_payment",
     "A customer owes NGN 30,000 and NGN 25,000 on two invoices and pays NGN 40,000, "
     "oldest first. What is left on each invoice?",
     [r"15[,\s]?000"],
     [r"(?<![\d,])0(?:\.00)?\s*(?:left|remaining)\s*(?:on\s*)?(?:both|all)"],
     "first cleared; 10,000 applied to second -> 15,000 left on it"),

    # --- overpayment / credit ---
    ("over-1", "overpayment",
     "A customer paid NGN 50,000 but their only invoice was NGN 45,000. "
     "What should I record?",
     [r"5[,\s]?000"], [],
     "5,000 credit / overpayment"),

    # --- multi-item and discount ---
    ("calc-1", "line_math",
     "I sold 7 bags at NGN 6,500 each and 3 tins at NGN 11,000 each. What is the subtotal?",
     [r"45[,\s]?500", r"33[,\s]?000", r"78[,\s]?500"], [],
     "45,500 + 33,000 = 78,500"),
    ("calc-2", "line_math",
     "An item costs NGN 80,000. I give a 10% discount. What does the customer pay?",
     [r"72[,\s]?000"], [],
     "80,000 - 8,000 = 72,000"),

    # --- margin ---
    ("margin-1", "margin",
     "I bought goods for NGN 150,000 and sold them for NGN 200,000. "
     "What is my profit and my margin percentage?",
     [r"50[,\s]?000", r"25\s*%"], [],
     "profit 50,000; margin 25% of revenue"),
]


def ask(model: str, question: str, n_tokens: int) -> str:
    res = subprocess.run(
        [LLAMA_CLI, "-m", model, "-t", "4", "-c", "1536", "-n", str(n_tokens),
         "-st", "-p", question, "--no-warmup", "--temp", "0"],
        capture_output=True, text=True, timeout=300)
    m = re.search(r"^> .*?$(.*?)^\[ Prompt:", res.stdout, re.S | re.M)
    text = m.group(1) if m else res.stdout
    return re.sub(r"^[|\\/\-\s]+", "", text.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(Path(__file__).parent / "gguf/model-Q4_K_M.gguf"))
    ap.add_argument("--n-tokens", type=int, default=200)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    results, topics = [], {}
    for i, (cid, topic, q, must, must_not, note) in enumerate(CASES, 1):
        ans = " ".join(ask(args.model, q, args.n_tokens).split())
        missing = [p for p in must if not re.search(p, ans, re.I)]
        hits = [p for p in must_not if re.search(p, ans, re.I)]
        ok = not missing and not hits
        results.append((cid, topic, q, ans, ok, missing, hits, note))
        t = topics.setdefault(topic, [0, 0])
        t[0] += ok
        t[1] += 1
        print(f"[{i}/{len(CASES)}] {'PASS' if ok else 'FAIL'} {cid}", flush=True)

    n_ok = sum(r[4] for r in results)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    out_path = Path(args.out) if args.out else Path(__file__).parent / f"results/arith_eval_{ts}.md"
    out_path.parent.mkdir(exist_ok=True)

    lines = [f"# Arithmetic eval — {ts}", "", f"Model: `{args.model}`",
             f"**Overall: {n_ok}/{len(results)}**", "", "| topic | passed |", "|---|---|"]
    lines += [f"| {t} | {ok}/{tot} |" for t, (ok, tot) in topics.items()]
    if n_ok < len(results):
        lines += ["", "## Failures"]
        for cid, topic, q, ans, ok, missing, hits, note in results:
            if not ok:
                why = ("missing: " + ", ".join(f"`{p}`" for p in missing)) if missing else ""
                why += (" wrong-hit: " + ", ".join(f"`{p}`" for p in hits)) if hits else ""
                lines += [f"- **{cid}** ({topic}): {q}", f"  - expected: {note}",
                          f"  - {why}", f"  - answer: {ans[:400]}"]
    lines += ["", "## All answers", ""]
    for cid, topic, q, ans, ok, *_ in results:
        lines += [f"- {'✅' if ok else '❌'} **{cid}** {q}", f"  - {ans[:400]}"]
    out_path.write_text("\n".join(lines) + "\n")

    print(f"\nArithmetic: {n_ok}/{len(results)}")
    print(f"Report: {out_path}")


if __name__ == "__main__":
    main()
