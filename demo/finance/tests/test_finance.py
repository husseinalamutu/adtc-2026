"""Finance-module tests. The reconciliation cases are the exact scenarios from the model
evals (build/results/model_size_tradeoff_2026-07-13.md) — including the two that LLMs
got wrong. The module existing means those numbers are computed, never generated."""
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # demo/ on the path

from finance import (Invoice, Ledger, TaxRules, allocate_lump_sum, parse_statement,
                     reconcile_exact)


# --- momo_parser ---

def test_parses_inline_training_format():
    txs = parse_statement("TX001: NGN 45,000; MP93481101: KES 4,500.00")
    assert [(t.ref, t.amount, t.currency) for t in txs] == [
        ("TX001", Decimal("45000"), "NGN"), ("MP93481101", Decimal("4500.00"), "KES")]


def test_parses_sms_lines_with_direction_and_party():
    txs = parse_statement(
        "TXN 8842 | 2026-07-11 | RECEIVED NGN 127,500 from 0803***512 | Bal: 340,000\n"
        "QGH7X2 Confirmed. Ksh4,500.00 sent to JANE WANJIKU")
    assert txs[0].direction == "in" and txs[0].amount == Decimal("127500")
    assert txs[1].direction == "out" and txs[1].currency == "KES"
    assert "JANE" in txs[1].counterparty


def test_skips_garbage_lines():
    assert parse_statement("hello there\n\n--") == []


# --- reconciliation: the eval cases ---

def test_p1_exact_clear_two_invoices():
    """Declared test prompt p1: 127,500 vs 85,000 + 42,500 -> both settled, 0 outstanding.
    (The 1.5B model answered this wrong; the module cannot.)"""
    invs = [Invoice("INV-114", 85000), Invoice("INV-121", 42500)]
    alloc = allocate_lump_sum(127500, invs)
    assert alloc.settled_ids == ["INV-114", "INV-121"]
    assert alloc.outstanding_total == Decimal("0.00")
    assert alloc.unapplied_credit == Decimal("0.00")


def test_partial_payment_carry():
    """100,000 vs 85,000 + 42,500 oldest-first -> INV-201 settled, 27,500 left on INV-202.
    (BOTH model sizes fumbled this conclusion; see results doc.)"""
    invs = [Invoice("INV-201", 85000), Invoice("INV-202", 42500)]
    alloc = allocate_lump_sum(100000, invs)
    assert alloc.settled_ids == ["INV-201"]
    assert alloc.partially_paid == [("INV-202", Decimal("27500.00"))]
    assert alloc.outstanding_total == Decimal("27500.00")


def test_overpayment_becomes_credit():
    alloc = allocate_lump_sum(50000, [Invoice("INV-1", 45000)])
    assert alloc.settled_ids == ["INV-1"]
    assert alloc.unapplied_credit == Decimal("5000.00")


def test_reconcile_exact_matches_and_ignores_noise():
    """Training-data convention: exact-amount match; airtime noise ignored."""
    txs = parse_statement("TX001: NGN 45,000; TX002: NGN 1,200")
    invs = [Invoice("INV-2001", 45000), Invoice("INV-2002", 30000)]
    alloc = reconcile_exact(txs, invs)
    assert alloc.settled_ids == ["INV-2001"]
    assert alloc.outstanding_total == Decimal("30000.00")


def test_summary_is_deterministic_text():
    invs = [Invoice("INV-201", 85000), Invoice("INV-202", 42500)]
    s = allocate_lump_sum(100000, invs).summary("NGN")
    assert "Settled: INV-201." in s and "27,500.00 still due" in s


# --- ledger double-entry ---

def test_ledger_always_balances():
    led = Ledger()
    led.add_invoice("INV-114", 85000)
    led.add_invoice("INV-121", 42500)
    alloc = led.record_lump_sum_payment(130000)  # 2,500 overpayment
    assert alloc.unapplied_credit == Decimal("2500.00")
    assert led.trial_balance() == Decimal("0.00")
    assert led.balances()["CASH"] == Decimal("130000.00")
    assert led.balances()["ACCOUNTS_RECEIVABLE"] == Decimal("0.00")


# --- tax rules (from the verified facts file) ---

def test_vat_quote_matches_smoke_test():
    """10 x 8,500 with 7.5% VAT -> 6,375 VAT, 91,375 total (the build smoke-test case)."""
    q = TaxRules().vat_quote(85000)
    assert q["vat"] == Decimal("6375.00") and q["total"] == Decimal("91375.00")


def test_small_company_qualifies():
    v = TaxRules().small_company_assessment(40_000_000, 100_000_000, professional_services=False)
    assert "Small company" in v.verdict and "0%" in v.verdict and v.cites


def test_professional_services_excluded_even_under_threshold():
    """The consulting-firm nuance: under 100M but NEVER small."""
    v = TaxRules().small_company_assessment(60_000_000, 50_000_000, professional_services=True)
    assert "NOT a small company" in v.verdict and "30%" in v.verdict


def test_turnover_above_threshold_not_small():
    """The def-4 eval case: 120M > 100M -> not small (the applied conclusion, computed)."""
    v = TaxRules().small_company_assessment(120_000_000, 50_000_000, professional_services=False)
    assert "NOT a small company" in v.verdict and "exceeds" in v.verdict


# --- VAT inclusive vs exclusive (Nigerian manufacturer pricing) ---

def test_vat_exclusive_adds_on_top():
    q = TaxRules().vat_quote(105000, inclusive=False)
    assert q["subtotal"] == Decimal("105000.00")
    assert q["vat"] == Decimal("7875.00")
    assert q["total"] == Decimal("112875.00")


def test_vat_inclusive_extracts_rather_than_adds():
    """Cement/petrol prices already contain VAT: ₦105,000 gross -> ₦7,325.58 VAT,
    NOT ₦7,875. Adding again would overcharge the customer and overstate output VAT."""
    q = TaxRules().vat_quote(105000, inclusive=True)
    assert q["total"] == Decimal("105000.00")
    assert q["vat"] == Decimal("7325.58")
    assert q["subtotal"] == Decimal("97674.42")


def test_vat_lines_always_reconcile_in_both_modes():
    rules = TaxRules()
    for amount in (105000, 8500, 1, 999999.99):
        for inclusive in (False, True):
            q = rules.vat_quote(amount, inclusive=inclusive)
            assert q["subtotal"] + q["vat"] == q["total"], (amount, inclusive)


def test_inclusive_net_times_rate_equals_the_extracted_vat():
    """The extracted VAT must be exactly 7.5% of the derived net — otherwise the seller's
    VAT return would not tie back to the invoice."""
    rules = TaxRules()
    q = rules.vat_quote(105000, inclusive=True)
    assert (q["subtotal"] * rules.vat_rate).quantize(Decimal("0.01")) == q["vat"]


def test_inclusive_total_is_lower_than_exclusive_total_for_the_same_figure():
    rules = TaxRules()
    assert rules.vat_quote(100000, inclusive=True)["total"] < \
           rules.vat_quote(100000, inclusive=False)["total"]
