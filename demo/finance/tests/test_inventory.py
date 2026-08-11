"""Inventory-as-working-capital tests.

Asserts the accounting properties that make these figures usable: weighted-average
valuation, COGS measured on goods that actually LEFT (not goods bought), dead stock
surfaced with its trapped capital, and honest Nones where data is genuinely absent.
"""
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from finance import Store, inventory, sample_data
from finance.store import StockMove


@pytest.fixture
def store():
    s = Store(":memory:")
    sample_data.load_into(s)
    yield s
    s.close()


def test_finds_the_planted_dead_stock(store):
    """Imported floor tiles are bought once and never move — trapped capital."""
    pos = inventory.position(store, date(2026, 6, 30), date(2026, 6, 1))
    assert pos.dead_stock_value > 0
    assert any("floor tiles" in s.description for s in pos.dead_skus)


def test_active_skus_are_not_flagged_as_dead(store):
    pos = inventory.position(store, date(2026, 6, 30), date(2026, 6, 1))
    dead_names = {s.description for s in pos.dead_skus}
    assert "50kg cement bags" not in dead_names


def test_cogs_counts_goods_sold_not_goods_bought():
    """The accounting distinction this module exists to fix: buying stock is not a cost
    of sale until the goods actually leave."""
    s = Store(":memory:")
    s.add_stock_movements([
        StockMove("A", "widget", date(2026, 3, 1), 100, Decimal("500"), "in"),
        StockMove("A", "widget", date(2026, 3, 20), 10, Decimal("500"), "out"),
    ])
    pos = inventory.position(s, date(2026, 3, 31), date(2026, 3, 1))
    assert pos.cogs_period == Decimal("5000.00")        # 10 sold, not 100 bought
    assert pos.total_value == Decimal("45000.00")       # 90 still on the shelf
    s.close()


def test_weighted_average_costing():
    """Two purchase prices for one SKU average out; a sale consumes at that average."""
    s = Store(":memory:")
    s.add_stock_movements([
        StockMove("B", "bag", date(2026, 1, 5), 10, Decimal("100"), "in"),   # 1,000
        StockMove("B", "bag", date(2026, 1, 6), 10, Decimal("200"), "in"),   # 2,000
        StockMove("B", "bag", date(2026, 1, 10), 5, Decimal("0"), "out"),
    ])
    pos = inventory.position(s, date(2026, 1, 31), date(2026, 1, 1))
    assert pos.skus[0].average_unit_cost == Decimal("150.00")   # (1000+2000)/20
    assert pos.cogs_period == Decimal("750.00")                 # 5 x 150
    assert pos.total_value == Decimal("2250.00")                # 15 x 150
    s.close()


def test_true_gross_margin_uses_real_cogs():
    s = Store(":memory:")
    s.add_stock_movements([
        StockMove("C", "item", date(2026, 2, 1), 100, Decimal("60"), "in"),
        StockMove("C", "item", date(2026, 2, 10), 50, Decimal("60"), "out"),   # COGS 3,000
    ])
    margin = inventory.true_gross_margin(s, Decimal("5000"), date(2026, 2, 28), date(2026, 2, 1))
    assert margin == Decimal("40.00")     # (5000-3000)/5000
    s.close()


def test_no_stock_data_returns_none_rather_than_a_wrong_margin():
    """Callers must be able to fall back, not silently receive a bogus figure."""
    s = Store(":memory:")
    assert inventory.true_gross_margin(s, Decimal("5000"), date(2026, 2, 28)) is None
    assert not s.has_stock_data()
    s.close()


def test_cash_conversion_cycle_is_honest_about_untracked_payables(store):
    ccc = inventory.cash_conversion_cycle(store, date(2026, 6, 30))
    assert ccc["days_payables_outstanding"] is None      # never invented
    assert ccc["cash_conversion_days"] > 0
    assert "DPO is excluded" in ccc["note"]


def test_selling_everything_leaves_no_value():
    s = Store(":memory:")
    s.add_stock_movements([
        StockMove("D", "thing", date(2026, 1, 1), 5, Decimal("400"), "in"),
        StockMove("D", "thing", date(2026, 1, 9), 5, Decimal("400"), "out"),
    ])
    pos = inventory.position(s, date(2026, 1, 31), date(2026, 1, 1))
    assert pos.total_value == Decimal("0.00")
    assert pos.dead_stock_value == Decimal("0.00")   # nothing on hand can't be dead stock
    s.close()


def test_ground_truth_mentions_trapped_capital(store):
    text = inventory.position(store, date(2026, 6, 30), date(2026, 6, 1)).as_ground_truth()
    assert "Stock on hand" in text and "Cost of goods sold" in text
    assert "tied up" in text
