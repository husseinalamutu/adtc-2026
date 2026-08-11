"""Store + analytics tests, checked against the KNOWN sample business.

Because sample_data.py generates deterministically, every expected figure here is a
fact we can recompute independently — the same discipline as the training data.
"""
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # demo/ on the path

import pytest

from finance import Store, sample_data
from finance.analytics import (business_health, cash_position, customers_owing,
                               period_summary, receivables_aging)
from finance.store import InvoiceRow, Txn


@pytest.fixture
def store():
    s = Store(":memory:")
    sample_data.load_into(s)
    yield s
    s.close()


# ---- store ----

def test_sample_business_loads(store):
    """Six months of trading, Jan through June 2026 (days 0-27 of each month)."""
    start, end = store.date_range()
    assert (start.year, start.month) == (2026, 1)
    assert (end.year, end.month) == (2026, 6)
    assert len(store.transactions()) > 250


def test_reimport_is_idempotent(store):
    """Re-importing an overlapping statement must never double-count money."""
    before = len(store.transactions())
    sample_data.load_into(store)
    assert len(store.transactions()) == before


def test_money_survives_the_roundtrip_exactly():
    """0.1 + 0.2 == 0.3 only if we never touch binary floats."""
    s = Store(":memory:")
    s.add_transactions([
        Txn("T1", date(2026, 1, 1), "a", Decimal("0.10"), "in", "Sales", None),
        Txn("T2", date(2026, 1, 1), "b", Decimal("0.20"), "in", "Sales", None),
    ])
    assert cash_position(s) == Decimal("0.30")
    s.close()


def test_csv_import_with_signed_amounts(tmp_path):
    csv = tmp_path / "txns.csv"
    csv.write_text("date,description,amount,category,counterparty,ref\n"
                   "2026-03-02,Counter sale,\"125,000\",Sales,Walk-in,TX9001\n"
                   "2026-03-03,Fuel,-8500,Transport,,TX9002\n", encoding="utf-8")
    s = Store(":memory:")
    assert s.import_transactions_csv(csv) == 2
    txns = s.transactions()
    assert txns[0].direction == "in" and txns[0].amount == Decimal("125000.00")
    assert txns[1].direction == "out" and txns[1].amount == Decimal("8500.00")
    s.close()


# ---- analytics ----

def test_period_summary_is_internally_consistent(store):
    p = period_summary(store, date(2026, 3, 1), date(2026, 3, 31))
    assert p.net == p.revenue - p.expenses
    assert sum((a for _, a in p.expense_by_category), Decimal("0")) == p.expenses
    assert p.cogs <= p.expenses


def test_cash_position_equals_in_minus_out(store):
    txns = store.transactions()
    expected = sum((t.amount if t.direction == "in" else -t.amount for t in txns), Decimal("0"))
    assert cash_position(store) == expected


def test_recent_invoices_are_outstanding(store):
    """Sample business leaves the last two months' invoices unpaid — the chase list."""
    owing = customers_owing(store, date(2026, 6, 30))
    assert owing, "expected unpaid invoices in the sample business"
    assert all(amt > 0 for _, amt, _ in owing)
    assert owing[0][2] >= owing[-1][2]  # sorted worst-overdue first


def test_receivables_aging_buckets_sum_to_total(store):
    as_of = date(2026, 6, 30)
    aging = receivables_aging(store, as_of)
    total = sum(i.outstanding for i in store.invoices(unpaid_only=True))
    assert sum(aging.values(), Decimal("0")) == total


def test_aging_moves_between_buckets_over_time():
    s = Store(":memory:")
    s.add_invoices([InvoiceRow("INV-1", "Adeyemi", Decimal("100000"),
                               date(2026, 1, 1), date(2026, 1, 31), Decimal("0"))])
    assert receivables_aging(s, date(2026, 1, 15))["current"] == Decimal("100000.00")
    assert receivables_aging(s, date(2026, 2, 20))["1-30"] == Decimal("100000.00")
    assert receivables_aging(s, date(2026, 4, 30))["60+"] == Decimal("100000.00")
    s.close()


def test_business_health_reports_the_june_sales_dip(store):
    """Sample business dips in the final month — health must show revenue down."""
    h = business_health(store, date(2026, 6, 15))
    assert h.revenue_change_pct is not None and h.revenue_change_pct < 0
    assert h.period.start == date(2026, 6, 1)
    assert h.previous.start == date(2026, 5, 1)


def test_ground_truth_text_carries_the_numbers(store):
    h = business_health(store, date(2026, 6, 15))
    text = h.as_ground_truth("NGN")
    assert "Revenue: NGN" in text and "Receivables outstanding" in text
    assert f"{h.period.revenue:,}" in text     # the exact figure the LLM must restate


def test_no_baseline_reports_na_not_zero():
    """First month of trading has no prior month — must say n/a, never a fake 0%."""
    s = Store(":memory:")
    s.add_transactions([Txn("T1", date(2026, 5, 4), "sale", Decimal("50000"), "in", "Sales", None)])
    h = business_health(s, date(2026, 5, 15))
    assert h.revenue_change_pct is None
    assert "n/a" in h.as_ground_truth()
    s.close()
