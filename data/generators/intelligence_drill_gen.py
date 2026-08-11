#!/usr/bin/env python3
"""Drills for the two skills v3 lacks, generated DETERMINISTICALLY from the finance module.

The module is the oracle: `TaxRules` and the analytics/anomaly/forecast layers compute the
answer, and the drill is built around it. No LLM teacher, so no hallucination can enter the
corpus and no API quota is consumed.

1. TAX CONCLUSIONS — fixes the measured `def-4` defect: v3 recites the thresholds correctly
   but will not APPLY them ("₦120M turnover" -> it restates the ₦100M rule instead of
   concluding "you do not qualify"). These drills teach the comparison and the verdict.

2. NARRATION — the skill the intelligence stack needs and v3 was never taught: given a
   VERIFIED FIGURES block computed by the module, restate it faithfully in plain language
   without recomputing or inventing. The prompt format mirrors exactly what demo/app sends.

NOT INCLUDED — intent routing. Teaching the model to emit tool markers risks those markers
leaking into ordinary answers on the organizers' hidden prompts, for no audit benefit; the
app routes deterministically instead.

Usage: python3 generators/intelligence_drill_gen.py --n 500 --out out/intel_drills.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "demo"))

from finance import Store, TaxRules, sample_data          # noqa: E402
from finance.advisor import recommend                      # noqa: E402
from finance.analytics import business_health              # noqa: E402
from finance.anomalies import as_ground_truth, detect      # noqa: E402
from finance.forecast import project                       # noqa: E402

RULES = TaxRules()
VERIFIED_HEADER = "VERIFIED FIGURES (computed by the accounting module — use exactly these):"


def make_id(*parts) -> str:
    return "intel-" + hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _example(family: str, ask: str, answer: str, truth: dict) -> dict:
    return {
        "id": make_id(family, ask, answer[:80]),
        "category": "intelligence",
        "scenario_family": f"intel::{family}",
        "messages": [{"role": "user", "content": ask},
                     {"role": "assistant", "content": answer}],
        "ground_truth": truth,
    }


# --------------------------------------------------------------------------
# 1. Tax conclusions — apply the thresholds, don't just recite them
# --------------------------------------------------------------------------

PROFESSIONAL = ["consulting firm", "law firm", "accountancy practice", "engineering consultancy",
                "IT consultancy", "management consultancy", "architecture practice"]
TRADING = ["trading company", "hardware shop", "building-materials retailer", "provisions store",
           "poultry farm", "printing business", "furniture workshop", "logistics company"]

ASKS = [
    "My {biz} turned over {turnover} last year with {assets} in fixed assets. "
    "Do we qualify as a small company for the 0% rate?",
    "I run a {biz}. Turnover {turnover}, fixed assets {assets}. What Companies Income Tax "
    "rate applies to us?",
    "We are a {biz} with {turnover} annual turnover and {assets} of fixed assets. "
    "Are we a small company under the 2025 rules, and do we pay the Development Levy?",
]


def _ngn(x: Decimal) -> str:
    return f"NGN {x:,.0f}"


def gen_tax_conclusion(rng: random.Random) -> dict:
    professional = rng.random() < 0.35
    biz = rng.choice(PROFESSIONAL if professional else TRADING)

    # deliberately straddle the thresholds so the model must actually COMPARE
    turnover = Decimal(rng.choice([
        rng.randrange(5_000_000, 99_000_000, 1_000_000),      # under
        rng.randrange(101_000_000, 900_000_000, 1_000_000),   # over
    ]))
    assets = Decimal(rng.choice([
        rng.randrange(5_000_000, 249_000_000, 1_000_000),
        rng.randrange(251_000_000, 800_000_000, 1_000_000),
    ]))

    verdict = RULES.small_company_assessment(turnover, assets, professional_services=professional)
    t_ok = turnover <= RULES.small_turnover_max
    a_ok = assets <= RULES.small_assets_max
    small = t_ok and a_ok and not professional

    checks = [
        f"- Turnover {_ngn(turnover)} vs the {_ngn(RULES.small_turnover_max)} limit: "
        + ("within the limit ✓" if t_ok else "**above the limit ✗**"),
        f"- Fixed assets {_ngn(assets)} vs the {_ngn(RULES.small_assets_max)} limit: "
        + ("within the limit ✓" if a_ok else "**above the limit ✗**"),
        f"- Professional services? "
        + ("**Yes — professional-services businesses are never small companies ✗**"
           if professional else "No ✓"),
    ]
    if small:
        conclusion = (f"**You qualify as a small company: Companies Income Tax at 0%**, and you "
                      f"are exempt from the Development Levy and Capital Gains Tax.")
    elif professional:
        conclusion = (f"**You do not qualify.** A {biz} provides professional services, which is "
                      f"excluded from small-company status regardless of size, so **Companies "
                      f"Income Tax applies at 30%** and the 4% Development Levy is payable.")
    else:
        failed = " and ".join(
            ([f"turnover exceeds {_ngn(RULES.small_turnover_max)}"] if not t_ok else [])
            + ([f"fixed assets exceed {_ngn(RULES.small_assets_max)}"] if not a_ok else []))
        conclusion = (f"**You do not qualify** because {failed}. **Companies Income Tax applies "
                      f"at 30%**, plus the 4% Development Levy on assessable profits.")

    ask = rng.choice(ASKS).format(biz=biz, turnover=_ngn(turnover), assets=_ngn(assets))
    answer = ("Checking each condition:\n" + "\n".join(checks) + "\n\n" + conclusion
              + "\n\nConfirm specifics with FIRS or a licensed accountant.")
    return _example("tax_conclusion", ask, answer,
                    {"turnover": str(turnover), "assets": str(assets),
                     "professional_services": professional, "is_small": small,
                     "module_verdict": verdict.verdict})


# --------------------------------------------------------------------------
# 2. Narration — restate module figures faithfully
# --------------------------------------------------------------------------

HEALTH_ASKS = ["What happened to my business this month?", "How is the business doing?",
               "Give me this month's summary.", "Explain my numbers for this month."]
ANOMALY_ASKS = ["Is anything unusual in my transactions?", "Check my spending for problems.",
                "Anything suspicious this period?"]
FORECAST_ASKS = ["Will I have enough cash next month?", "What does my cash look like next month?",
                 "Can I cover my supplier payments next month?"]
ACTION_ASKS = ["What should I do about it?", "What actions do you recommend?",
               "How do I fix this?"]


def _narrate_health(h, rng) -> str:
    dirn = ("up" if (h.revenue_change_pct or 0) > 0 else "down")
    lead = (f"Revenue came in at NGN {h.period.revenue:,}"
            + (f", {dirn} {abs(h.revenue_change_pct):.1f}% on last month"
               if h.revenue_change_pct is not None else "") + ".")
    exp = (f"Expenses were NGN {h.period.expenses:,}"
           + (f" ({h.expense_change_pct:+.1f}%)" if h.expense_change_pct is not None else "")
           + f", leaving a net of NGN {h.period.net:,}.")
    marg = ("" if h.period.gross_margin_pct is None
            else f" Gross margin was {h.period.gross_margin_pct:.1f}%.")
    recv = (f" You are owed NGN {h.receivables_total:,}, of which NGN "
            f"{h.receivables_overdue:,} is already overdue." if h.receivables_total > 0 else "")
    return lead + " " + exp + marg + recv


def _narrate_anomalies(items) -> str:
    if not items:
        return "Nothing unusual stands out in your spending this period."
    top = items[0]
    who = f" to {top.counterparty}" if top.counterparty else ""
    return (f"{len(items)} transaction(s) are worth a look. The most significant is "
            f"NGN {top.amount:,}{who} on {top.txn_date}: {top.reason} "
            f"Review these before your next payment run.")


def _narrate_forecast(f) -> str:
    if f.insufficient_history:
        return ("There isn't enough trading history yet to project next month's cash. "
                "Keep recording transactions and this will become available.")
    verdict = (f"you are projected to come up short by NGN {f.shortfall:,}"
               if f.shortfall > 0 else "you are projected to cover your obligations")
    return (f"Based on {f.months_observed} months of trading, expect about "
            f"NGN {f.projected_inflow:,} in and NGN {f.projected_outflow:,} out next month, "
            f"closing around NGN {f.projected_closing:,} (range NGN {f.low:,} to "
            f"NGN {f.high:,}). Against committed obligations of NGN "
            f"{f.committed_obligations:,}, {verdict}.")


def _narrate_plan(plan) -> str:
    if not plan.recommendations:
        return "No corrective action is needed from your current books."
    steps = " ".join(f"{i}. {r.action} — about NGN {r.impact:,}."
                     for i, r in enumerate(plan.recommendations, 1))
    close = ("Together these cover the projected gap." if plan.closes_gap and plan.shortfall > 0
             else (f"Together they free about NGN {plan.total_impact:,}."))
    return f"The highest-value actions available to you: {steps} {close}"


def gen_narration(rng: random.Random) -> dict:
    seed = rng.randint(1, 10_000)
    store = Store(":memory:")
    txns, invoices = sample_data.build(seed=seed)
    store.add_transactions(txns)
    store.add_invoices(invoices)
    as_of = date(2026, rng.randint(4, 6), 15)

    kind = rng.choice(["health", "anomaly", "forecast", "actions"])
    if kind == "health":
        h = business_health(store, as_of)
        verified, ask, narration = h.as_ground_truth("NGN"), rng.choice(HEALTH_ASKS), _narrate_health(h, rng)
    elif kind == "anomaly":
        items = detect(store)
        verified, ask, narration = as_ground_truth(items), rng.choice(ANOMALY_ASKS), _narrate_anomalies(items)
    elif kind == "forecast":
        obligations = Decimal(rng.randrange(500_000, 6_000_000, 100_000))
        f = project(store, as_of, committed_obligations=obligations)
        verified, ask, narration = f.as_ground_truth("NGN"), rng.choice(FORECAST_ASKS), _narrate_forecast(f)
    else:
        obligations = Decimal(rng.randrange(500_000, 6_000_000, 100_000))
        plan = recommend(store, as_of, committed_obligations=obligations)
        verified, ask, narration = plan.as_ground_truth("NGN"), rng.choice(ACTION_ASKS), _narrate_plan(plan)
    store.close()

    prompt = f"{ask}\n\n{VERIFIED_HEADER}\n{verified}"
    return _example(f"narration_{kind}", prompt, narration,
                    {"kind": kind, "seed": seed, "verified_block": verified})


GENERATORS = [gen_tax_conclusion, gen_narration]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--out", default="out/intel_drills.jsonl")
    ap.add_argument("--seed", type=int, default=31)
    ap.add_argument("--tax-fraction", type=float, default=0.5)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    n_tax = int(args.n * args.tax_fraction)
    seen, rows = set(), []
    for i in range(args.n * 6):
        if len(rows) >= args.n:
            break
        ex = gen_tax_conclusion(rng) if len([r for r in rows if "tax_conclusion" in r["scenario_family"]]) < n_tax \
            else gen_narration(rng)
        if ex["id"] in seen:
            continue
        seen.add(ex["id"])
        rows.append(ex)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["scenario_family"]] = counts.get(r["scenario_family"], 0) + 1
    print(f"wrote {len(rows)} intelligence drills -> {out}")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
