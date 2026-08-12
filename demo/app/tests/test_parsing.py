"""Input parsing for the demo app.

These exist because of a real defect: typing a price the way a Nigerian shop owner actually
writes it — "Bags of cement, 10, 10,500" or "₦10,500" — was silently mis-parsed into a WRONG
TOTAL by a naive `split(",")`. A quote that is quietly wrong is the worst thing this app can
produce, so the rule is: parse what people really type, and REFUSE anything ambiguous rather
than guess.
"""
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from server import _money, parse_invoice_lines, parse_item_lines


# --- the reported defect -----------------------------------------------------

@pytest.mark.parametrize("line", [
    "Bags of cement, 10, 10,500",        # thousands separator — the original bug
    "Bags of cement, 10, N10,500",       # naira as 'N'
    "Bags of cement, 10, ₦10,500",       # naira symbol
    "Bags of cement, 10, NGN 10,500",    # currency code with a space
    "Bags of cement, 10, 10500",         # plain
])
def test_price_formats_all_yield_the_same_figure(line):
    item = parse_item_lines(line)[0]
    assert item["desc"] == "Bags of cement"
    assert item["qty"] == "10"
    assert Decimal(item["unit_price"]) == Decimal("10500")


def test_description_may_contain_commas():
    """Fields are taken from the right, so a comma in the product name is fine."""
    item = parse_item_lines("Cement, bagged (50kg), 10, 8500")[0]
    assert item["desc"] == "Cement, bagged (50kg)"
    assert item["qty"] == "10" and Decimal(item["unit_price"]) == Decimal("8500")


def test_three_digit_quantity_is_not_swallowed_as_a_thousands_separator():
    """'Item, 100, 500' must stay qty=100 price=500 — the trap that makes a lenient
    thousands rule dangerous."""
    item = parse_item_lines("Item, 100, 500")[0]
    assert item["qty"] == "100" and Decimal(item["unit_price"]) == Decimal("500")


def test_decimals_are_preserved_exactly():
    item = parse_item_lines("Paint, 3, ₦10,500.75")[0]
    assert Decimal(item["unit_price"]) == Decimal("10500.75")


# --- invoices ----------------------------------------------------------------

@pytest.mark.parametrize("line,expected", [
    ("INV-114, 85,000", "85000"),
    ("INV-121, ₦42,500.00", "42500.00"),
    ("INV-9, 45000", "45000"),
    ("INV-7, NGN 1,250,000", "1250000"),
])
def test_invoice_amount_formats(line, expected):
    row = parse_invoice_lines(line)[0]
    assert Decimal(row["amount"]) == Decimal(expected)


def test_multiple_lines_and_blank_lines():
    rows = parse_invoice_lines("INV-114, 85,000\n\nINV-121, ₦42,500\n")
    assert [r["id"] for r in rows] == ["INV-114", "INV-121"]


# --- refusing ambiguity ------------------------------------------------------

@pytest.mark.parametrize("bad", [
    "total nonsense",              # no fields
    "Bags, 10",                    # missing a field
    "Bags, ten, 8500",             # non-numeric quantity
    "Bags, 10, eight thousand",    # non-numeric price
    ", 10, 8500",                  # empty description
])
def test_ambiguous_or_malformed_input_is_rejected_not_guessed(bad):
    with pytest.raises(ValueError):
        parse_item_lines(bad)


def test_error_message_quotes_the_offending_line():
    """The operator must be able to see WHICH line to fix."""
    with pytest.raises(ValueError, match="Bags, ten, 8500"):
        parse_item_lines("Cement, 10, 8500\nBags, ten, 8500")


# --- the money helper --------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("10,500", "10500"), ("₦10,500.00", "10500.00"), ("N10500", "10500"),
    ("NGN 1,250,000", "1250000"), ("  42,500  ", "42500"),
])
def test_money_normalisation(text, expected):
    assert _money(text) == Decimal(expected)


@pytest.mark.parametrize("bad", ["", "abc", "1,2,3", "10.5.3", "N"])
def test_money_rejects_junk(bad):
    with pytest.raises(ValueError):
        _money(bad)
