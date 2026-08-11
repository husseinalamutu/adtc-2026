"""Cash-flow projection tests.

A wrong cash answer makes a business owner miss payroll, so these assert conservative
behaviour explicitly: no projection without history, the range brackets the point
estimate, and shortfall is judged at the LOW end (never the optimistic case).
"""
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from finance import Store, sample_data
from finance.forecast import MIN_MONTHS, project
from finance.store import Txn


@pytest.fixture
def store():
    s = Store(":memory:")
    sample_data.load_into(s)
    yield s
    s.close()


def _steady(months: int, inflow: str, outflow: str, start=date(2026, 1, 1)) -> list[Txn]:
    rows = []
    for m in range(months):
        d = date(start.year, start.month + m, 10)
        rows.append(Txn(f"IN{m}", d, "sales", Decimal(inflow), "in", "Sales", None))
        rows.append(Txn(f"OUT{m}", d, "costs", Decimal(outflow), "out", "Inventory purchase", None))
    return rows


def test_refuses_to_project_without_history():
    """One month of trading is not a pattern — say so rather than guess."""
    s = Store(":memory:")
    s.add_transactions(_steady(1, "100000", "60000"))
    f = project(s, date(2026, 1, 31))
    assert f.insufficient_history
    assert "Not enough history" in f.as_ground_truth()
    s.close()


def test_steady_business_projects_its_own_run_rate():
    """Identical months in, identical month out — and zero volatility band."""
    s = Store(":memory:")
    s.add_transactions(_steady(4, "500000", "300000"))
    f = project(s, date(2026, 4, 30))
    assert not f.insufficient_history
    assert f.projected_inflow == Decimal("500000.00")
    assert f.projected_outflow == Decimal("300000.00")
    assert f.low == f.projected_closing == f.high     # no variation observed
    s.close()


def test_current_partial_month_is_excluded():
    """Projecting mid-month must not treat a half-finished month as a full one."""
    s = Store(":memory:")
    rows = _steady(3, "500000", "300000")
    rows.append(Txn("PART", date(2026, 4, 3), "sales", Decimal("20000"), "in", "Sales", None))
    s.add_transactions(rows)
    f = project(s, date(2026, 4, 5))
    assert f.months_observed == 3
    assert f.projected_inflow == Decimal("500000.00")   # not dragged down by the partial month
    s.close()


def test_obligations_reduce_closing_cash_and_can_create_a_shortfall():
    s = Store(":memory:")
    s.add_transactions(_steady(4, "500000", "300000"))
    base = project(s, date(2026, 4, 30))
    withobl = project(s, date(2026, 4, 30), committed_obligations=Decimal("5000000"))
    assert withobl.projected_closing == base.projected_closing - Decimal("5000000.00")
    assert withobl.shortfall > 0
    assert "PROJECTED SHORTFALL" in withobl.as_ground_truth()
    s.close()


def test_healthy_projection_reports_headroom_not_shortfall(store):
    f = project(store, date(2026, 6, 30))
    assert f.shortfall == 0
    assert "to spare" in f.as_ground_truth()


def test_range_brackets_the_point_estimate(store):
    f = project(store, date(2026, 6, 30))
    assert f.low <= f.projected_closing <= f.high


def test_shortfall_is_judged_at_the_low_end():
    """A business that is fine on average but negative in a bad month must be warned."""
    s = Store(":memory:")
    rows = []
    for m, (i, o) in enumerate([("900000", "300000"), ("200000", "800000"),
                                ("900000", "300000"), ("200000", "800000")]):
        d = date(2026, 1 + m, 10)
        rows.append(Txn(f"I{m}", d, "sales", Decimal(i), "in", "Sales", None))
        rows.append(Txn(f"O{m}", d, "costs", Decimal(o), "out", "Inventory purchase", None))
    s.add_transactions(rows)
    f = project(s, date(2026, 4, 30), committed_obligations=Decimal("600000"))
    assert f.high > f.low                       # volatile business => real band
    if f.low < 0:
        assert f.shortfall > 0                  # warned on the bad-month case
    s.close()


def test_assumptions_are_always_disclosed(store):
    f = project(store, date(2026, 6, 30))
    text = f.as_ground_truth()
    assert "Assumptions:" in text
    assert "unpaid invoices are NOT assumed to be collected" in text
    assert f.months_observed >= MIN_MONTHS
