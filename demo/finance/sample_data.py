"""Deterministic sample business — a Lagos building-materials retailer, 6 months.

Same philosophy as data/generators/templated_gen.py: the data is GENERATED, so its
ground truth is known exactly. That lets the analytics/anomaly/forecast layers be
tested against facts rather than vibes, and gives the demo a realistic business to
open with when the operator has no data of their own yet.

PLANTED GROUND TRUTH (what the anomaly layer must find — see PLANTED below):
  - a duplicated supplier payment (same amount, same supplier, next day)
  - one wildly out-of-pattern transport expense
  - a supplier unit-price jump in the final month
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from .store import InvoiceRow, Txn

START = date(2026, 1, 1)
MONTHS = 6

SUPPLIERS = ["Dangote Cement Depot", "Julius Berger Supplies", "Lagos Steel Ltd", "PVC Nigeria"]
CUSTOMERS = ["Adeyemi Construction", "Okafor Builders", "Ngozi Interiors",
             "Bello Contracts", "Chidi Homes"]
EXPENSE_CATS = {
    "Inventory purchase": (180_000, 420_000, 8),
    "Transport": (4_000, 18_000, 12),
    "Staff salaries": (240_000, 240_000, 1),
    "Rent": (150_000, 150_000, 1),
    "Utilities": (12_000, 38_000, 2),
    "Airtime & data": (2_000, 6_000, 4),
    "Bank charges": (500, 3_500, 3),
}

PLANTED = {
    "duplicate_payment": {"supplier": "Lagos Steel Ltd", "amount": Decimal("312500.00"),
                          "dates": (date(2026, 4, 14), date(2026, 4, 15))},
    "transport_outlier": {"amount": Decimal("340000.00"), "date": date(2026, 5, 9)},
    "price_jump": {"supplier": "PVC Nigeria", "from": Decimal("95000.00"),
                   "to": Decimal("171000.00"), "month": 6},
}


def _month_start(i: int) -> date:
    y, m = START.year + (START.month - 1 + i) // 12, (START.month - 1 + i) % 12 + 1
    return date(y, m, 1)


def build(seed: int = 7) -> tuple[list[Txn], list[InvoiceRow]]:
    rng = random.Random(seed)
    txns: list[Txn] = []
    invoices: list[InvoiceRow] = []
    ref = 1000

    def nref() -> str:
        nonlocal ref
        ref += 1
        return f"TX{ref}"

    for m in range(MONTHS):
        mstart = _month_start(m)
        # --- revenue: sales trending up, then a dip in the final month ---
        n_sales = 26 + m * 2 - (10 if m == MONTHS - 1 else 0)
        for _ in range(n_sales):
            day = mstart + timedelta(days=rng.randint(0, 27))
            amt = Decimal(rng.randrange(18_000, 260_000, 500))
            txns.append(Txn(nref(), day, "Counter sale", amt, "in", "Sales",
                            rng.choice(CUSTOMERS + ["Walk-in customer"])))

        # --- recurring + variable expenses ---
        for cat, (lo, hi, count) in EXPENSE_CATS.items():
            for _ in range(count):
                day = mstart + timedelta(days=rng.randint(0, 27))
                amt = Decimal(rng.randrange(lo, hi + 1, 500)) if hi > lo else Decimal(lo)
                party = rng.choice(SUPPLIERS) if cat == "Inventory purchase" else None
                txns.append(Txn(nref(), day, cat, amt, "out", cat, party))

        # --- credit sales become invoices (2 per month, 30-day terms) ---
        for k in range(2):
            issued = mstart + timedelta(days=6 + k * 12)
            amt = Decimal(rng.randrange(120_000, 480_000, 500))
            paid = amt if m < MONTHS - 2 else Decimal("0")   # recent two months unpaid
            invoices.append(InvoiceRow(f"INV-{2000 + m * 2 + k}", rng.choice(CUSTOMERS),
                                       amt, issued, issued + timedelta(days=30), paid))

    # --- planted anomaly 1: duplicate supplier payment ---
    dup = PLANTED["duplicate_payment"]
    for d in dup["dates"]:
        txns.append(Txn(nref(), d, "Inventory purchase", dup["amount"], "out",
                        "Inventory purchase", dup["supplier"]))

    # --- planted anomaly 2: transport expense ~20x the norm ---
    out = PLANTED["transport_outlier"]
    txns.append(Txn(nref(), out["date"], "Truck hire (emergency)", out["amount"], "out",
                    "Transport", None))

    # --- planted anomaly 3: supplier unit-price jump in the final month ---
    pj = PLANTED["price_jump"]
    for m in range(MONTHS):
        d = _month_start(m) + timedelta(days=11)
        amt = pj["to"] if m == pj["month"] - 1 else pj["from"]
        txns.append(Txn(nref(), d, "PVC pipe order", amt, "out",
                        "Inventory purchase", pj["supplier"]))

    txns.sort(key=lambda t: t.txn_date)
    return txns, invoices


def load_into(store) -> tuple[int, int]:
    txns, invoices = build()
    return store.add_transactions(txns), store.add_invoices(invoices)
