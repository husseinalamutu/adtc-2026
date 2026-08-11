#!/usr/bin/env python3
"""Arithmetic drills targeting the defects arith_eval.py measured in v3 (9/12).

Measured failures this fixes:
  - multi-item VAT: "3 x 12,000 + 7.5%" -> model said 38,400, correct 38,700
  - line multiplication: "7 x 6,500" -> model said 52,500, correct 45,500
  - margin vs markup: profit/revenue (25%) confused with profit/cost (33.3%)
  - partial-payment carry: correct under some phrasings, fragile under others

METHOD — show the working. Small models do arithmetic far more reliably when trained to
emit intermediate steps rather than jumping to a total; each drill therefore states every
step, and the ground truth is computed here in Decimal so a wrong answer can never enter
the corpus.

EVAL INTEGRITY: numbers are randomised and phrasings are drawn from a pool, so the
eval's own cases are not reproduced here. Training on the gate would destroy the gate.

Usage: python3 generators/arith_drill_gen.py --n 600 --out out/arith_drills.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

TWO = Decimal("0.01")
SEEDS = json.loads((Path(__file__).parent.parent / "seeds" / "markets.json").read_text())
MARKETS = SEEDS["markets"]
ARCHETYPES = SEEDS["business_archetypes"]


def _d(x) -> Decimal:
    return Decimal(str(x)).quantize(TWO, rounding=ROUND_HALF_UP)


def money(amount: Decimal, currency: str) -> str:
    return f"{currency} {amount:,.2f}"


def pct(rate: Decimal) -> str:
    r"""7.50 -> '7.5'. Trailing zeros matter: the fact eval matches `7\.5\s*%`, so training
    the model to write '7.50%' would make it fail the VAT gate on a technicality."""
    return f"{rate.normalize():f}".rstrip("0").rstrip(".") or "0"


def make_id(*parts) -> str:
    return "arith-" + hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _example(kind: str, family: str, ask: str, answer: str, truth: dict) -> dict:
    return {
        "id": make_id(kind, ask),
        "category": "arithmetic",
        "scenario_family": f"arith::{family}",
        "messages": [{"role": "user", "content": ask},
                     {"role": "assistant", "content": answer}],
        "ground_truth": truth,
    }


# --- 1. partial payment applied across invoices, with carry ---------------------

CARRY_ASKS = [
    "A customer paid {pay}. They owe {inv_list}. Apply the payment to the oldest invoice "
    "first. How much is still unpaid?",
    "I received {pay} from a customer with these open invoices: {inv_list}. "
    "Applying it oldest first, what is left outstanding?",
    "{pay} came in by {provider}. Open invoices: {inv_list}. Settle them oldest first and "
    "tell me the remaining balance.",
    "My customer owes {inv_list} and has just paid {pay}. What do they still owe?",
]


def gen_carry(rng: random.Random) -> dict:
    market = rng.choice(MARKETS)
    cur = market["currency"]
    n = rng.randint(2, 3)
    invoices = [{"id": f"INV-{rng.randint(100, 999)}",
                 "amount": _d(rng.randrange(15_000, 200_000, 500))} for _ in range(n)]
    total_due = _d(sum(i["amount"] for i in invoices))
    # a PARTIAL payment: enough to clear at least one, never all of them
    pay = _d(rng.randrange(int(invoices[0]["amount"]) + 1000, int(total_due), 500))

    steps, left = [], pay
    for inv in invoices:
        applied = min(left, inv["amount"])
        remaining_on_inv = _d(inv["amount"] - applied)
        if applied > 0:
            steps.append(
                f"- Apply {money(applied, cur)} to {inv['id']} ({money(inv['amount'], cur)}): "
                + (f"settled, {money(Decimal('0'), cur)} remaining."
                   if remaining_on_inv == 0 else
                   f"{money(inv['amount'], cur)} − {money(applied, cur)} = "
                   f"{money(remaining_on_inv, cur)} still due."))
            left = _d(left - applied)
            if left > 0:
                steps.append(f"- Payment remaining to apply: {money(pay, cur)} − "
                             f"{money(applied, cur)} = {money(left, cur)}")
        else:
            steps.append(f"- Nothing left to apply to {inv['id']}: "
                         f"{money(inv['amount'], cur)} still due in full.")
        inv["remaining"] = remaining_on_inv
    outstanding = _d(sum(i["remaining"] for i in invoices))

    inv_list = " and ".join(f"{i['id']} for {money(i['amount'], cur)}" for i in invoices)
    ask = rng.choice(CARRY_ASKS).format(pay=money(pay, cur), inv_list=inv_list,
                                        provider=rng.choice(market["mobile_money"]))
    answer = ("\n".join(steps) + "\n\n"
              f"**Total still unpaid: {money(outstanding, cur)}**")
    return _example("carry", "partial_payment", ask, answer,
                    {"payment": str(pay), "invoices": [{k: str(v) for k, v in i.items()}
                                                       for i in invoices],
                     "outstanding": str(outstanding), "currency": cur})


# --- 2. multi-item subtotal then VAT (the 38,400 vs 38,700 defect) --------------

VAT_ASKS = [
    "A customer buys {qty} {item} at {unit} each. Add {rate}% VAT. What is the total?",
    "Work out the total for {qty} {item} at {unit} each including {rate}% VAT.",
    "I'm selling {qty} {item} at {unit} each. With {rate}% VAT, what does the customer pay?",
]


def gen_vat_total(rng: random.Random) -> dict:
    market = rng.choice(MARKETS)
    cur = market["currency"]
    archetype = rng.choice(ARCHETYPES)
    item = rng.choice(archetype["items"])
    qty = rng.randint(2, 40)
    unit = _d(rng.randrange(1_500, 60_000, 500))
    rate = _d(market["vat_rate"] * 100)
    subtotal = _d(qty * unit)
    vat = _d(subtotal * rate / 100)
    total = _d(subtotal + vat)

    ask = rng.choice(VAT_ASKS).format(qty=qty, item=item, unit=money(unit, cur),
                                      rate=pct(rate))
    answer = (f"- {qty} × {money(unit, cur)} = {money(subtotal, cur)}\n"
              f"- VAT ({pct(rate)}%): {money(subtotal, cur)} × {rate/100:g} = {money(vat, cur)}\n"
              f"- Total: {money(subtotal, cur)} + {money(vat, cur)} = {money(total, cur)}\n\n"
              f"**The customer pays {money(total, cur)}.**")
    return _example("vat_total", "vat_math", ask, answer,
                    {"qty": qty, "unit": str(unit), "subtotal": str(subtotal),
                     "vat_rate": str(rate), "vat": str(vat), "total": str(total), "currency": cur})


# --- 3. multi-line subtotal (the 7 x 6,500 defect) -----------------------------

def gen_line_math(rng: random.Random) -> dict:
    market = rng.choice(MARKETS)
    cur = market["currency"]
    archetype = rng.choice(ARCHETYPES)
    items = rng.sample(archetype["items"], min(rng.randint(2, 3), len(archetype["items"])))
    lines = [{"item": it, "qty": rng.randint(2, 30),
              "unit": _d(rng.randrange(1_000, 45_000, 500))} for it in items]
    for l in lines:
        l["total"] = _d(l["qty"] * l["unit"])
    subtotal = _d(sum(l["total"] for l in lines))

    desc = " and ".join(f"{l['qty']} {l['item']} at {money(l['unit'], cur)} each" for l in lines)
    ask = rng.choice([
        f"I sold {desc}. What is the subtotal?",
        f"Add up this order: {desc}. What is the total before VAT?",
        f"Work out what a customer owes for {desc}.",
    ])
    steps = "\n".join(f"- {l['qty']} × {money(l['unit'], cur)} = {money(l['total'], cur)}"
                      for l in lines)
    sum_expr = " + ".join(money(l["total"], cur) for l in lines)
    answer = f"{steps}\n- Subtotal: {sum_expr} = {money(subtotal, cur)}\n\n" \
             f"**Subtotal: {money(subtotal, cur)}**"
    return _example("line_math", "line_math", ask, answer,
                    {"lines": [{k: str(v) for k, v in l.items()} for l in lines],
                     "subtotal": str(subtotal), "currency": cur})


# --- 4. margin vs markup (the 33.3% vs 25% defect) ----------------------------

def gen_margin(rng: random.Random) -> dict:
    market = rng.choice(MARKETS)
    cur = market["currency"]
    cost = _d(rng.randrange(20_000, 900_000, 1_000))
    revenue = _d(cost * Decimal(str(rng.uniform(1.15, 2.2))))
    revenue = _d(revenue.quantize(Decimal("1")))
    profit = _d(revenue - cost)
    margin = _d(profit / revenue * 100)
    markup = _d(profit / cost * 100)

    ask = rng.choice([
        f"I bought goods for {money(cost, cur)} and sold them for {money(revenue, cur)}. "
        f"What is my profit and my margin percentage?",
        f"Cost was {money(cost, cur)}, I sold for {money(revenue, cur)}. "
        f"What is the gross margin?",
        f"My purchase price was {money(cost, cur)} and my selling price {money(revenue, cur)}. "
        f"Work out the profit and margin.",
    ])
    answer = (f"- Profit: {money(revenue, cur)} − {money(cost, cur)} = {money(profit, cur)}\n"
              f"- Gross margin (profit ÷ **revenue**): {money(profit, cur)} ÷ "
              f"{money(revenue, cur)} = {margin:.1f}%\n"
              f"- (Markup, profit ÷ **cost**, is a different figure: {money(profit, cur)} ÷ "
              f"{money(cost, cur)} = {markup:.1f}% — don't confuse the two.)\n\n"
              f"**Profit {money(profit, cur)}; gross margin {margin:.1f}%.**")
    return _example("margin", "margin", ask, answer,
                    {"cost": str(cost), "revenue": str(revenue), "profit": str(profit),
                     "margin_pct": str(margin), "markup_pct": str(markup), "currency": cur})


GENERATORS = [gen_carry, gen_vat_total, gen_line_math, gen_margin]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--out", default="out/arith_drills.jsonl")
    ap.add_argument("--seed", type=int, default=23)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    seen, rows = set(), []
    attempts = 0
    while len(rows) < args.n and attempts < args.n * 40:
        attempts += 1
        ex = GENERATORS[len(rows) % len(GENERATORS)](rng)
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
    print(f"wrote {len(rows)} arithmetic drills -> {out}")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
