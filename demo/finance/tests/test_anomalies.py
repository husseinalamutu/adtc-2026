"""Anomaly detection tested against the anomalies PLANTED in sample_data.py.

Ground truth is known by construction, so these assert real detection — not that
'something was returned'. Also asserts the quiet case: a clean ledger stays quiet
(a detector that cries wolf on normal trading is worse than none).
"""
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from finance import Store, sample_data
from finance.anomalies import as_ground_truth, detect
from finance.sample_data import PLANTED
from finance.store import Txn


@pytest.fixture
def store():
    s = Store(":memory:")
    sample_data.load_into(s)
    yield s
    s.close()


def test_finds_the_planted_duplicate_payment(store):
    dup = PLANTED["duplicate_payment"]
    hits = [a for a in detect(store) if a.kind == "duplicate_payment"]
    assert any(a.amount == dup["amount"] and a.counterparty == dup["supplier"]
               and a.txn_date == dup["dates"][1] for a in hits), \
        f"planted duplicate not detected; got {[a.line() for a in hits]}"


def test_finds_the_planted_transport_outlier(store):
    out = PLANTED["transport_outlier"]
    hits = [a for a in detect(store) if a.kind == "amount_outlier"]
    assert any(a.amount == out["amount"] and a.txn_date == out["date"] for a in hits), \
        f"planted transport outlier not detected; got {[a.line() for a in hits]}"


def test_finds_the_planted_supplier_price_jump(store):
    pj = PLANTED["price_jump"]
    hits = [a for a in detect(store) if a.kind == "price_jump"]
    assert any(a.counterparty == pj["supplier"] and a.amount == pj["to"] for a in hits), \
        f"planted price jump not detected; got {[a.line() for a in hits]}"


def test_duplicates_outrank_the_weaker_signals(store):
    """A near-certain, recoverable double payment must reach the operator before the
    'maybe' signals (a price move or an unfamiliar payee)."""
    kinds = [a.kind for a in detect(store)]
    assert "duplicate_payment" in kinds
    first_dup = kinds.index("duplicate_payment")
    maybes = [i for i, k in enumerate(kinds) if k in ("price_jump", "new_large_payee")]
    assert not maybes or first_dup < min(maybes)


def test_recurring_payment_is_not_a_duplicate():
    """A standing weekly order — same payee, same amount, every week — is business as
    usual, not 50 double payments."""
    s = Store(":memory:")
    day = date(2026, 1, 1)
    s.add_transactions([
        Txn(f"W{i}", day + timedelta(days=i * 3), "Weekly supplies", Decimal("20000"),
            "out", "Inventory purchase", "Known Supplier") for i in range(30)])
    assert [a for a in detect(s) if a.kind == "duplicate_payment"] == []
    s.close()


def test_shortlist_is_short(store):
    """The whole point: a human-sized list out of hundreds of rows."""
    assert len(store.transactions()) > 250
    assert len(detect(store, limit=20)) <= 20


def test_clean_ledger_stays_quiet():
    """Routine, near-identical trading must not be flagged."""
    s = Store(":memory:")
    day = date(2026, 2, 1)
    s.add_transactions([
        Txn(f"T{i}", day + timedelta(days=i), "Fuel", Decimal("9000") + Decimal(i * 50),
            "out", "Transport", None) for i in range(20)
    ])
    assert detect(s) == []
    s.close()


def test_no_spread_does_not_flag():
    """Twenty identical rent payments have zero MAD — must not divide-by-zero or flag."""
    s = Store(":memory:")
    day = date(2026, 1, 1)
    s.add_transactions([
        Txn(f"R{i}", day + timedelta(days=30 * i), "Rent", Decimal("150000"),
            "out", "Rent", "Landlord") for i in range(20)
    ])
    assert [a for a in detect(s) if a.kind == "amount_outlier"] == []
    s.close()


def test_income_is_not_scanned():
    """A big sale is good news, not an anomaly — we scan spending only."""
    s = Store(":memory:")
    day = date(2026, 3, 1)
    rows = [Txn(f"S{i}", day + timedelta(days=i), "sale", Decimal("50000"), "in", "Sales", None)
            for i in range(10)]
    rows.append(Txn("BIG", day, "huge sale", Decimal("9000000"), "in", "Sales", None))
    s.add_transactions(rows)
    assert detect(s) == []
    s.close()


def test_ground_truth_text_is_numbered_and_ranked(store):
    text = as_ground_truth(detect(store))
    assert "flagged for review" in text and "\n1. " in text


def test_ground_truth_handles_the_all_clear():
    assert as_ground_truth([]) == "No unusual transactions detected."


def test_cold_start_does_not_flag_every_payee_as_new(store):
    """At the start of a ledger everyone is 'new' — flagging them all is noise."""
    first_txn = min(t.txn_date for t in store.transactions())
    new_payee_dates = [a.txn_date for a in detect(store) if a.kind == "new_large_payee"]
    assert all((d - first_txn).days >= 30 for d in new_payee_dates), \
        f"cold-start payees flagged: {new_payee_dates}"


def test_genuinely_new_payee_is_still_flagged():
    """After the books are established, a big first-time payee must surface."""
    s = Store(":memory:")
    day = date(2026, 1, 1)
    rows = [Txn(f"T{i}", day + timedelta(days=i * 3), "Supplies", Decimal("20000"),
                "out", "Inventory purchase", "Known Supplier") for i in range(30)]
    rows.append(Txn("NEW", date(2026, 4, 1), "Consulting", Decimal("400000"),
                    "out", "Services", "Brand New Vendor Ltd"))
    s.add_transactions(rows)
    hits = [a for a in detect(s) if a.kind == "new_large_payee"]
    assert any(a.counterparty == "Brand New Vendor Ltd" for a in hits)
    s.close()
