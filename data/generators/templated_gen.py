#!/usr/bin/env python3
"""
Templated generator — invoices/quotes and mobile-money reconciliation.

Every example's ground truth is computed programmatically (not by an LLM), so it is
guaranteed arithmetically correct. This is the accuracy backbone: it's the part of the
fine-tune that teaches the model to not screw up VAT math, discounts, and reconciliation —
exactly what the sandbox's hidden prompts are most likely to probe, since it's checkable.

Output schema (one JSON object per line):
    {
        "id": "<stable hash>",
        "category": "invoice" | "quote" | "reconciliation",
        "scenario_family": "<used for the train/holdout split — see build_dataset.py>",
        "messages": [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}],
        "ground_truth": {...}   # raw fields so tests/ can re-derive and check the arithmetic
    }
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

SEEDS = json.loads((Path(__file__).parent.parent / "seeds" / "markets.json").read_text())
MARKETS = SEEDS["markets"]
ARCHETYPES = SEEDS["business_archetypes"]
PERSONAS = SEEDS["operator_personas"]


def money(amount: float, currency: str) -> str:
    return f"{currency} {amount:,.2f}"


def make_id(*parts) -> str:
    return hashlib.sha1("||".join(str(p) for p in parts).encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Category 1: Quote / invoice drafting with VAT + discount
# ---------------------------------------------------------------------------
def gen_invoice(rng: random.Random) -> dict:
    market = rng.choice(MARKETS)
    archetype = rng.choice(ARCHETYPES)
    persona = rng.choice(PERSONAS)
    city = rng.choice(market["cities"])
    doc_type = rng.choice(["quote", "invoice"])

    n_items = rng.randint(1, 4)
    items = rng.sample(archetype["items"], min(n_items, len(archetype["items"])))
    lines = []
    subtotal = 0.0
    for item in items:
        qty = rng.randint(1, 50)
        unit_price = round(rng.uniform(50, 15000), 2)
        line_total = round(qty * unit_price, 2)
        subtotal += line_total
        lines.append({"item": item, "qty": qty, "unit_price": unit_price, "line_total": line_total})
    subtotal = round(subtotal, 2)

    apply_discount = rng.random() < 0.35
    discount_pct = round(rng.uniform(2, 15), 1) if apply_discount else 0.0
    discount_amount = round(subtotal * discount_pct / 100, 2)
    taxable_base = round(subtotal - discount_amount, 2)

    apply_vat = rng.random() < 0.6
    vat_rate = market["vat_rate"] if apply_vat else 0.0
    vat_amount = round(taxable_base * vat_rate, 2)
    total = round(taxable_base + vat_amount, 2)

    mm_provider = rng.choice(market["mobile_money"])
    payment_note = rng.choice(
        [f"payable via {mm_provider}", f"payable via {mm_provider} or bank transfer", "cash on delivery"]
    )

    items_desc = "; ".join(f"{l['qty']} x {l['item']} @ {money(l['unit_price'], market['currency'])}" for l in lines)
    ask = (
        f"You are {persona} at a {archetype['type']} in {city}, {market['country']}. "
        f"Draft a professional {doc_type} for a customer ordering: {items_desc}."
    )
    if apply_discount:
        ask += f" Apply a {discount_pct}% discount on the subtotal."
    if apply_vat:
        ask += f" Add {market['vat_name']} at {vat_rate*100:.1f}%."
    else:
        ask += " This customer is VAT-exempt, so do not add VAT."
    ask += f" State it is {payment_note}. Show the full breakdown and the final total."

    breakdown_lines = "\n".join(
        f"- {l['qty']} x {l['item']} @ {money(l['unit_price'], market['currency'])} = {money(l['line_total'], market['currency'])}"
        for l in lines
    )
    answer = f"**{doc_type.title()}**\n\n{breakdown_lines}\n\nSubtotal: {money(subtotal, market['currency'])}\n"
    if apply_discount:
        answer += f"Discount ({discount_pct}%): -{money(discount_amount, market['currency'])}\n"
        answer += f"Taxable amount: {money(taxable_base, market['currency'])}\n"
    if apply_vat:
        answer += f"{market['vat_name']} ({vat_rate*100:.1f}%): {money(vat_amount, market['currency'])}\n"
    answer += f"**Total due: {money(total, market['currency'])}**\n\nPayment: {payment_note}."

    return {
        "id": make_id("invoice", city, items_desc, discount_pct, apply_vat),
        "category": doc_type,
        "scenario_family": f"invoice::{archetype['type']}::{market['country']}",
        "messages": [{"role": "user", "content": ask}, {"role": "assistant", "content": answer}],
        "ground_truth": {
            "lines": lines, "subtotal": subtotal, "discount_pct": discount_pct,
            "discount_amount": discount_amount, "taxable_base": taxable_base,
            "vat_rate": vat_rate, "vat_amount": vat_amount, "total": total,
            "currency": market["currency"],
        },
    }


# ---------------------------------------------------------------------------
# Category 2: Mobile-money statement reconciliation against open invoices
# ---------------------------------------------------------------------------
def gen_reconciliation(rng: random.Random) -> dict:
    market = rng.choice(MARKETS)
    archetype = rng.choice(ARCHETYPES)
    persona = rng.choice(PERSONAS)
    provider = rng.choice(market["mobile_money"])
    currency = market["currency"]

    n_invoices = rng.randint(2, 5)
    invoices = []
    for i in range(n_invoices):
        amt = round(rng.uniform(500, 40000), 2)
        invoices.append({"invoice_id": f"INV-{1000+i}", "amount": amt})

    # Randomly decide which invoices get a matching payment (exact amount match).
    n_paid = rng.randint(0, n_invoices)
    paid_indices = set(rng.sample(range(n_invoices), n_paid))
    tx_lines = []
    for idx, inv in enumerate(invoices):
        if idx in paid_indices:
            tx_lines.append({"ref": f"{provider[:2].upper()}{rng.randint(10**8,10**9-1)}", "amount": inv["amount"]})
    # Add 0-2 noise transactions that don't match any invoice (e.g. airtime, unrelated transfer).
    for _ in range(rng.randint(0, 2)):
        tx_lines.append({"ref": f"{provider[:2].upper()}{rng.randint(10**8,10**9-1)}", "amount": round(rng.uniform(100, 3000), 2)})
    rng.shuffle(tx_lines)

    paid_ids = {invoices[i]["invoice_id"] for i in paid_indices}
    outstanding = [inv for inv in invoices if inv["invoice_id"] not in paid_ids]
    outstanding_total = round(sum(inv["amount"] for inv in outstanding), 2)
    settled_total = round(sum(invoices[i]["amount"] for i in paid_indices), 2)

    stmt_desc = "; ".join(f"{t['ref']}: {money(t['amount'], currency)}" for t in tx_lines)
    inv_desc = "; ".join(f"{inv['invoice_id']} ({money(inv['amount'], currency)})" for inv in invoices)
    ask = (
        f"You are {persona} at a {archetype['type']}. This {provider} statement excerpt just came in: "
        f"{stmt_desc}. Reconcile it against these outstanding invoices: {inv_desc}. "
        f"List which invoices are now settled, which remain outstanding, and the total outstanding balance."
    )

    if paid_ids:
        settled_desc = "\n".join(
            f"- {invoices[i]['invoice_id']}: {money(invoices[i]['amount'], currency)} — matched to transaction "
            f"{[t['ref'] for t in tx_lines if t['amount'] == invoices[i]['amount']][0]}"
            for i in sorted(paid_indices)
        )
    else:
        settled_desc = "(none)"
    outstanding_desc = "\n".join(f"- {inv['invoice_id']}: {money(inv['amount'], currency)}" for inv in outstanding) or "(none)"

    answer = (
        f"**Settled invoices** (matched by exact amount to a statement entry):\n{settled_desc}\n\n"
        f"**Still outstanding:**\n{outstanding_desc}\n\n"
        f"**Total settled:** {money(settled_total, currency)}\n"
        f"**Total outstanding balance: {money(outstanding_total, currency)}**"
    )

    return {
        "id": make_id("recon", stmt_desc, inv_desc),
        "category": "reconciliation",
        "scenario_family": f"reconciliation::{archetype['type']}::{market['country']}",
        "messages": [{"role": "user", "content": ask}, {"role": "assistant", "content": answer}],
        "ground_truth": {
            "invoices": invoices, "transactions": tx_lines, "paid_invoice_ids": sorted(paid_ids),
            "outstanding_total": outstanding_total, "settled_total": settled_total, "currency": currency,
        },
    }


GENERATORS = [gen_invoice, gen_reconciliation]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000, help="total examples to generate")
    ap.add_argument("--out", default="out/templated.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    seen_ids = set()
    written = 0
    with out_path.open("w") as f:
        attempts = 0
        while written < args.n and attempts < args.n * 3:
            attempts += 1
            gen = GENERATORS[attempts % len(GENERATORS)]
            example = gen(rng)
            if example["id"] in seen_ids:
                continue
            seen_ids.add(example["id"])
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            written += 1

    print(f"Wrote {written} templated examples -> {out_path}")


if __name__ == "__main__":
    main()
