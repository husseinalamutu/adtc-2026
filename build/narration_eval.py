#!/usr/bin/env python3
"""Narration-fidelity eval — does the model restate computed figures WITHOUT corrupting them?

The third gate. `fact_eval` measures Nigeria recall, `arith_eval` measures arithmetic, and
this measures the property the whole product rests on: when the finance engine hands the
model a VERIFIED FIGURES block, every money figure in the reply must come from that block.

We added narration to the v5 training mix, so it needs a gate — training a skill without
measuring it is how the arithmetic defects survived for weeks.

METHOD. Money tokens (NGN amounts and comma-grouped figures) are extracted from the block
and from the reply. A reply FAILS if it contains a money figure absent from the block —
that is an invented number, the exact failure mode that would make an SME distrust the tool.
Small integers and list numbering are ignored deliberately: "3 products" or "1." are not
claims about money, and flagging them would bury the real defect in noise.

Usage: python3 narration_eval.py [--model gguf/model-Q4_K_M.gguf]
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "demo"))

from finance import Store, sample_data                      # noqa: E402
from finance.advisor import recommend                        # noqa: E402
from finance.analytics import business_health                # noqa: E402
from finance.anomalies import as_ground_truth, detect        # noqa: E402
from finance.forecast import project                         # noqa: E402
from finance.inventory import position                       # noqa: E402

LLAMA_CLI = os.environ.get(
    "LLAMA_CLI", str(Path.home() / "adtc-local/llama.cpp/build/bin/llama-cli"))

SYSTEM_PREFIX = (
    "You are an offline back-office assistant for African small businesses. When VERIFIED "
    "FIGURES are provided, use ONLY those numbers — restate them exactly; never recompute "
    "or alter them. Be concise.\n\n")

# A money figure: optionally NGN-prefixed, with thousands separators or decimals.
MONEY = re.compile(r"(?:NGN\s*)?(\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|\d+\.\d{2})")


def money_tokens(text: str) -> set[str]:
    """Normalised money figures, so '1,452,000.00' and '1452000' compare equal."""
    out = set()
    for raw in MONEY.findall(text):
        try:
            out.add(str(Decimal(raw.replace(",", "")).normalize()))
        except Exception:
            continue
    return out


def build_cases() -> list[tuple[str, str, str]]:
    """(id, question, verified_block) built from the real engine — same shapes the app sends."""
    store = Store(":memory:")
    sample_data.load_into(store)
    as_of = date(2026, 6, 15)
    obligations = Decimal("4200000")

    cases = [
        ("narr-health", "What happened to my business this month?",
         business_health(store, as_of).as_ground_truth("NGN")),
        ("narr-anomaly", "Is anything unusual in my transactions?",
         as_ground_truth(detect(store))),
        ("narr-forecast", "Will I have enough cash next month?",
         project(store, as_of, committed_obligations=obligations).as_ground_truth("NGN")),
        ("narr-actions", "What should I do about it?",
         recommend(store, as_of, committed_obligations=obligations).as_ground_truth("NGN")),
        ("narr-stock", "How much of my cash is tied up in stock?",
         position(store, as_of, as_of.replace(day=1)).as_ground_truth("NGN")),
    ]
    store.close()
    return cases


def ask(model: str, question: str, block: str, n_tokens: int) -> str:
    prompt = (f"{SYSTEM_PREFIX}{question}\n\nVERIFIED FIGURES (computed by the accounting "
              f"module — use exactly these):\n{block}")
    res = subprocess.run(
        [LLAMA_CLI, "-m", model, "-t", "4", "-c", "2048", "-n", str(n_tokens),
         "-st", "-p", prompt, "--no-warmup", "--temp", "0"],
        capture_output=True, text=True, timeout=420)
    m = re.search(r"^> .*?$(.*?)^\[ Prompt:", res.stdout, re.S | re.M)
    text = m.group(1) if m else res.stdout
    return re.sub(r"^[|\\/\-\s]+", "", text.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(Path(__file__).parent / "gguf/model-Q4_K_M.gguf"))
    ap.add_argument("--n-tokens", type=int, default=260)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    results = []
    for i, (cid, question, block) in enumerate(build_cases(), 1):
        answer = ask(args.model, question, block, args.n_tokens)
        allowed = money_tokens(block)
        used = money_tokens(answer)
        invented = sorted(used - allowed)
        # a reply that cites no figures at all has dodged the task rather than done it
        restated = bool(used & allowed)
        ok = not invented and restated
        results.append((cid, question, answer, ok, invented, len(used & allowed)))
        print(f"[{i}/5] {'PASS' if ok else 'FAIL'} {cid}"
              + (f"  invented: {', '.join(invented[:4])}" if invented else ""), flush=True)

    n_ok = sum(r[3] for r in results)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    out_path = Path(args.out) if args.out else Path(__file__).parent / f"results/narration_eval_{ts}.md"
    out_path.parent.mkdir(exist_ok=True)
    lines = [f"# Narration fidelity — {ts}", "", f"Model: `{args.model}`",
             f"**{n_ok}/{len(results)} replies used only figures from the verified block.**", ""]
    for cid, q, a, ok, invented, matched in results:
        lines += [f"## {'✅' if ok else '❌'} {cid}", f"*{q}*", "",
                  (f"- INVENTED FIGURES: {', '.join(invented)}" if invented
                   else f"- {matched} verified figure(s) restated, none invented"),
                  "", "```", a[:900], "```", ""]
    out_path.write_text("\n".join(lines) + "\n")

    print(f"\nNarration fidelity: {n_ok}/{len(results)}")
    print(f"Report: {out_path}")


if __name__ == "__main__":
    main()
