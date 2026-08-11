"""Decision-engine tests — the 'what should I do?' layer.

Asserts the properties that make advice trustworthy: every impact traces to the books,
certain money outranks negotiable money, the shortfall arithmetic is honest about
whether it actually closes, and a healthy business isn't handed busywork.
"""
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from finance import Store, sample_data
from finance.advisor import recommend
from finance.store import InvoiceRow, Txn


@pytest.fixture
def store():
    s = Store(":memory:")
    sample_data.load_into(s)
    yield s
    s.close()


def test_recommends_chasing_overdue_customers_first(store):
    plan = recommend(store, date(2026, 6, 30))
    assert plan.recommendations
    assert "Chase" in plan.recommendations[0].action
    assert plan.recommendations[0].confidence == "high"


def test_certain_money_outranks_negotiable_money(store):
    """High-confidence items (owed to us, paid twice) must precede medium ones."""
    confidences = [r.confidence for r in recommend(store, date(2026, 6, 30), limit=10).recommendations]
    assert confidences == sorted(confidences, key=lambda c: c != "high")


def test_recovers_the_planted_duplicate_payment(store):
    plan = recommend(store, date(2026, 6, 30), limit=10)
    assert any("double payment" in r.action or "double payment" in r.evidence
               for r in plan.recommendations)


def test_price_jump_only_claims_the_excess_not_the_whole_invoice(store):
    """Querying a price rise recovers the overpayment, not the entire order."""
    plan = recommend(store, date(2026, 6, 30), limit=20)
    for r in plan.recommendations:
        if "price increase" in r.action:
            assert r.impact < Decimal("420000.00")   # less than any full invoice
            assert r.impact > 0


def test_impacts_are_all_positive_and_traceable(store):
    for r in recommend(store, date(2026, 6, 30), limit=10).recommendations:
        assert r.impact > 0
        assert r.evidence           # every figure carries its provenance
        assert r.confidence in ("high", "medium")


def test_reports_honestly_when_actions_do_not_close_the_gap():
    """An impossible shortfall must NOT be dressed up as solved."""
    s = Store(":memory:")
    rows = []
    for m in range(4):
        d = date(2026, 1 + m, 10)
        rows.append(Txn(f"I{m}", d, "sales", Decimal("400000"), "in", "Sales", None))
        rows.append(Txn(f"O{m}", d, "costs", Decimal("380000"), "out", "Inventory purchase", None))
    s.add_transactions(rows)
    s.add_invoices([InvoiceRow("INV-9", "Slow Payer", Decimal("50000"),
                               date(2026, 3, 1), date(2026, 3, 31), Decimal("0"))])
    plan = recommend(s, date(2026, 4, 30), committed_obligations=Decimal("50000000"))
    assert plan.shortfall > 0
    assert not plan.closes_gap
    text = plan.as_ground_truth()
    assert "do NOT fully close it" in text and "would remain" in text
    s.close()


def test_healthy_business_is_not_handed_busywork():
    """No overdue money, no errors, no growth in discretionary spend => no actions."""
    s = Store(":memory:")
    rows = []
    for m in range(4):
        d = date(2026, 1 + m, 10)
        rows.append(Txn(f"I{m}", d, "sales", Decimal("500000"), "in", "Sales", None))
        rows.append(Txn(f"O{m}", d, "costs", Decimal("200000"), "out", "Inventory purchase", None))
    s.add_transactions(rows)
    plan = recommend(s, date(2026, 4, 30))
    assert plan.recommendations == []
    assert "No corrective actions needed" in plan.as_ground_truth()
    s.close()


def test_discretionary_advice_targets_the_increase_only():
    """Advice must be 'cut back to last month', not 'stop spending on transport'."""
    s = Store(":memory:")
    rows = []
    for m in range(3):
        d = date(2026, 1 + m, 10)
        rows.append(Txn(f"I{m}", d, "sales", Decimal("500000"), "in", "Sales", None))
    rows.append(Txn("T1", date(2026, 2, 12), "Fuel", Decimal("20000"), "out", "Transport", None))
    rows.append(Txn("T2", date(2026, 3, 12), "Fuel", Decimal("50000"), "out", "Transport", None))
    s.add_transactions(rows)
    plan = recommend(s, date(2026, 3, 20), limit=10)
    transport = [r for r in plan.recommendations if "transport" in r.action.lower()]
    assert transport and transport[0].impact == Decimal("30000.00")   # the rise, not the total
    s.close()


def test_ground_truth_brief_is_numbered_and_states_the_verdict(store):
    text = recommend(store, date(2026, 6, 30), limit=3).as_ground_truth()
    assert "Recommended actions" in text and "\n1. " in text
