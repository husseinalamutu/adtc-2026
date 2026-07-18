#!/usr/bin/env python3
"""Nigeria fact-recall eval for the GGUF — the wide version of HANDOFF's 5-question FACT CHECK.

37 questions over the 38 verified facts in data/seeds/nigeria_tax_facts.json, phrased as
paraphrases, casual/Nigerian-English variants, and adversarial framings the drills never used —
so a pass measures recall of the *fact*, not of a drilled phrasing. Scored by regex:
every `must` pattern must match the answer, no `must_not` may. Questions tagged gate=True
are the shipping gate (the 5 facts HANDOFF requires); --gate-only runs just those.

Usage: python3 fact_eval.py [--model gguf/model-Q4_K_M.gguf] [--gate-only] [--out results/...]
Runtime: ~4-6 min for all 37 (one llama-cli load per question, same flags as the smoke test).
"""
import argparse
import datetime
import os
import re
import subprocess
from pathlib import Path

LLAMA_CLI = os.environ.get(
    "LLAMA_CLI", str(Path.home() / "adtc-local/llama.cpp/build/bin/llama-cli"))

# (id, topic, gate, question, must[], must_not[])
QUESTIONS = [
    # --- VAT standard rate: 7.5% (gate) ---
    ("vat-1", "vat_rate", True, "What is the current VAT rate in Nigeria?",
     [r"7\.5\s*%"], [r"(?<![\d.])5\.5\s*%", r"(?<![\d.])5\s*%", r"(?<![\d.])10\s*%"]),
    ("vat-2", "vat_rate", True, "How much VAT do I add to a customer's invoice for goods I sell?",
     [r"7\.5\s*%"], [r"(?<![\d.])5\.5\s*%"]),
    ("vat-3", "vat_rate", True, "Is VAT in Nigeria still 5%?",
     [r"7\.5\s*%"], []),
    ("vat-4", "vat_rate", True, "Wetin be the VAT rate wey I go charge for goods for my shop?",
     [r"7\.5\s*%"], []),
    # --- CIT small-company rate: 0% (gate) ---
    ("cit0-1", "cit_small_rate", True, "What Companies Income Tax rate does a qualifying small company pay?",
     [r"0\s*%|exempt"], [r"(?<![\d.])15\s*%", r"(?<![\d.])20\s*%", r"(?<![\d.])25\s*%"]),
    ("cit0-2", "cit_small_rate", True, "My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?",
     [r"0\s*%|exempt|do(es)? not pay|don't pay"], [r"(?<![\d.])15\s*%", r"(?<![\d.])20\s*%"]),
    ("cit0-3", "cit_small_rate", True, "Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?",
     [r"0\s*%|exempt|not liable"], [r"(?<![\d.])15\s*%", r"(?<![\d.])20\s*%"]),
    ("cit0-4", "cit_small_rate", True, "Small companies in Nigeria pay 20% company income tax, right?",
     [r"0\s*%|exempt"], []),
    # --- CIT standard rate: 30% (gate) ---
    ("cit30-1", "cit_standard_rate", True, "What is the standard Companies Income Tax rate for a large Nigerian company?",
     [r"30\s*%"], [r"(?<![\d.])35\s*%", r"(?<![\d.])25\s*%"]),
    ("cit30-2", "cit_standard_rate", True, "My company turns over N500 million a year. What income tax rate applies to the company?",
     [r"30\s*%"], []),
    ("cit30-3", "cit_standard_rate", True, "What company income tax rate applies once a business is above the small-company threshold?",
     [r"30\s*%"], []),
    # --- Small-company definition: <=N100M turnover, <=N250M fixed assets (gate) ---
    ("def-1", "smallco_definition", True, "What annual turnover qualifies a company as 'small' for the 0% company income tax rate?",
     [r"100\s*million|100,000,000|₦100"], [r"(?<![\d.])25\s*million", r"(?<![\d.])70\s*million", r"(?<![\d.])30\s*million"]),
    ("def-2", "smallco_definition", True, "What are the turnover and fixed-asset limits for small-company status under the 2025 Act?",
     [r"100\s*million|100,000,000|₦100", r"250\s*million|250,000,000|₦250"], []),
    ("def-3", "smallco_definition", True, "Is the small-company tax threshold still N25 million turnover?",
     [r"100\s*million|100,000,000|₦100"], []),
    ("def-4", "smallco_definition", True, "My turnover is N120 million. Do I qualify as a small company for 0% tax?",
     [r"not|no\b|exceed|above"], []),
    # --- Professional-services exclusion (gate) ---
    ("prof-1", "prof_services_exclusion", True, "I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?",
     [r"professional|exclu|not qualify|do(es)? not qualify|don't qualify|cannot"], []),
    ("prof-2", "prof_services_exclusion", True, "Can an accounting or law firm ever be classified as a small company for tax purposes?",
     [r"no\b|not\b|never|exclu"], []),
    ("prof-3", "prof_services_exclusion", True, "Why does my small consulting company still pay company income tax despite low turnover?",
     [r"professional"], []),
    ("prof-4", "prof_services_exclusion", True, "A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?",
     [r"30\s*%"], [r"(?<![\d.])0\s*%"]),
    # --- Development Levy: 4% on assessable profits, small cos exempt (gate) ---
    ("dev-1", "dev_levy", True, "What is the Development Levy rate in Nigeria?",
     [r"4\s*%"], [r"(?<![\d.])2\s*%", r"(?<![\d.])3\.5\s*%", r"(?<![\d.])3\s*%"]),
    ("dev-2", "dev_levy", True, "On what profits is the Development Levy charged, and at what rate?",
     [r"4\s*%", r"assessable"], []),
    ("dev-3", "dev_levy", True, "Does a small company have to pay the Development Levy?",
     [r"exempt|no\b|not\b"], []),
    ("dev-4", "dev_levy", True, "Besides the 30% income tax, what development levy does a large company pay on its profits?",
     [r"4\s*%"], [r"(?<![\d.])2\s*%", r"(?<![\d.])3\.5\s*%"]),
    # --- Withholding tax ---
    ("wht-1", "withholding_tax", False, "When is a small company exempt from deducting withholding tax at source on a payment?",
     [r"2\s*million|2,000,000|₦2", r"TIN"], []),
    ("wht-2", "withholding_tax", False, "What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?",
     [r"10\s*%"], []),
    # --- Capital gains tax ---
    ("cgt-1", "capital_gains", False, "What is the Capital Gains Tax rate for companies under the 2025 reform?",
     [r"30\s*%"], []),
    ("cgt-2", "capital_gains", False, "Do small companies pay Capital Gains Tax?",
     [r"exempt|no\b|not\b"], []),
    ("cgt-3", "capital_gains", False, "How are capital gains of individuals taxed now?",
     [r"personal income|bands|25\s*%"], []),
    # --- Personal income tax ---
    ("pit-1", "personal_income_tax", False, "Below what annual income is an individual exempt from personal income tax?",
     [r"800,000|₦800|800\s*thousand|N800"], []),
    ("pit-2", "personal_income_tax", False, "What is the top personal income tax rate under the new bands?",
     [r"25\s*%"], [r"(?<![\d.])24\s*%", r"(?<![\d.])19\s*%"]),
    ("pit-3", "personal_income_tax", False, "How does the new rent relief for individuals work?",
     [r"20\s*%", r"500,000|₦500"], []),
    # --- Residency / diaspora ---
    ("res-1", "tax_residency", False, "How many days must I spend in Nigeria to become a tax resident?",
     [r"183"], []),
    ("res-2", "tax_residency", False, "Is the money I send home to my family in Nigeria every month taxed?",
     [r"not\b|no\b|exempt"], []),
    ("res-3", "tax_residency", False, "I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?",
     [r"exempt|not\b|no\b"], []),
    ("res-4", "tax_residency", False, "Are non-residents taxed on income they earn outside Nigeria?",
     [r"no\b|not\b|only|Nigerian.source"], []),
    # --- Filing & penalties ---
    ("file-1", "filing_penalties", False, "When must an established Nigerian company file its annual tax returns?",
     [r"6\s*months"], []),
    ("file-2", "filing_penalties", False, "What is the penalty for failing to register for tax in Nigeria?",
     [r"50,000|₦50"], []),
]


def ask(model: str, question: str, n_tokens: int) -> str:
    """One llama-cli run; returns the model's answer text."""
    res = subprocess.run(
        [LLAMA_CLI, "-m", model, "-t", "4", "-c", "1536", "-n", str(n_tokens),
         "-st", "-p", question, "--no-warmup", "--temp", "0"],
        capture_output=True, text=True, timeout=300)
    out = res.stdout
    # answer sits between the echoed "> <question>" line and the "[ Prompt:" perf line
    m = re.search(r"^> .*?$(.*?)^\[ Prompt:", out, re.S | re.M)
    text = m.group(1) if m else out
    return re.sub(r"^[|\\/\-\s]+", "", text.strip())  # strip spinner chars


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(Path(__file__).parent / "gguf/model-Q4_K_M.gguf"))
    ap.add_argument("--gate-only", action="store_true", help="only the 5 shipping-gate fact topics")
    ap.add_argument("--n-tokens", type=int, default=130)
    ap.add_argument("--out", default=None, help="markdown report path (default results/fact_eval_<ts>.md)")
    args = ap.parse_args()

    qs = [q for q in QUESTIONS if q[2]] if args.gate_only else QUESTIONS
    results, topic_stats = [], {}
    for i, (qid, topic, gate, question, must, must_not) in enumerate(qs, 1):
        answer = ask(args.model, question, args.n_tokens)
        one_line = " ".join(answer.split())
        missing = [p for p in must if not re.search(p, one_line, re.I)]
        hits = [p for p in must_not if re.search(p, one_line, re.I)]
        ok = not missing and not hits
        results.append((qid, topic, gate, question, one_line, ok, missing, hits))
        t = topic_stats.setdefault(topic, [0, 0, gate])
        t[0] += ok
        t[1] += 1
        print(f"[{i}/{len(qs)}] {'PASS' if ok else 'FAIL'} {qid}", flush=True)

    n_ok = sum(r[5] for r in results)
    gate_results = [r for r in results if r[2]]
    gate_ok = sum(r[5] for r in gate_results)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    out_path = Path(args.out) if args.out else Path(__file__).parent / f"results/fact_eval_{ts}.md"
    out_path.parent.mkdir(exist_ok=True)

    lines = [f"# Fact-recall eval — {ts}", "",
             f"Model: `{args.model}`",
             f"**Overall: {n_ok}/{len(results)}** — gate topics: **{gate_ok}/{len(gate_results)}**"
             f" ({'SHIP' if gate_ok == len(gate_results) else 'DO NOT SHIP'})", "",
             "| topic | passed | gate |", "|---|---|---|"]
    for topic, (ok, tot, gate) in topic_stats.items():
        lines.append(f"| {topic} | {ok}/{tot} | {'✓' if gate else ''} |")
    lines += ["", "## Failures"] if n_ok < len(results) else []
    for qid, topic, gate, question, ans, ok, missing, hits in results:
        if not ok:
            why = ("missing: " + ", ".join(f"`{p}`" for p in missing)) if missing else ""
            why += (" wrong-hit: " + ", ".join(f"`{p}`" for p in hits)) if hits else ""
            lines += [f"- **{qid}**{' (gate)' if gate else ''}: {question}",
                      f"  - {why}", f"  - answer: {ans[:300]}"]
    lines += ["", "## All answers", ""]
    for qid, topic, gate, question, ans, ok, *_ in results:
        lines += [f"- {'✅' if ok else '❌'} **{qid}** {question}", f"  - {ans[:300]}"]
    out_path.write_text("\n".join(lines) + "\n")

    print(f"\nOverall {n_ok}/{len(results)}  |  GATE {gate_ok}/{len(gate_results)} "
          f"{'— SHIP' if gate_ok == len(gate_results) else '— DO NOT SHIP'}")
    print(f"Report: {out_path}")


if __name__ == "__main__":
    main()
