"""Arithmetic verification for the arithmetic and intelligence drill generators.

Same discipline as test_dataset_quality.py, extended to the generators added for v5. This
file exists because those categories were previously UNCHECKED: the suite passed while
silently ignoring 1,100 examples, which is exactly the false confidence that lets a
generator bug poison training data.

Every figure is re-derived independently from the drill's own `ground_truth`, and the
rendered answer is checked to contain the computed result — a correct ground_truth paired
with a wrong answer string would still teach the model the wrong number.
"""
import json
import random
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "generators"))

import pytest

import arith_drill_gen  # noqa: E402
import intelligence_drill_gen  # noqa: E402

MONEY = re.compile(r"(\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|\d+\.\d{2})")


def _money_set(text: str) -> set[Decimal]:
    out = set()
    for raw in MONEY.findall(text):
        try:
            out.add(Decimal(raw.replace(",", "")))
        except Exception:
            pass
    return out


def _drills(kind, n=60, seed=5):
    rng = random.Random(seed)
    return [kind(rng) for _ in range(n)]


# --------------------------------------------------------------------------
# Arithmetic drills
# --------------------------------------------------------------------------

def test_carry_outstanding_equals_sum_of_remainders():
    """The defect these drills exist to fix — the total must equal the per-invoice residue."""
    for ex in _drills(arith_drill_gen.gen_carry):
        gt = ex["ground_truth"]
        expected = sum(Decimal(i["remaining"]) for i in gt["invoices"])
        assert Decimal(gt["outstanding"]) == expected, ex["messages"][0]["content"]


def test_carry_never_over_applies_the_payment():
    """Amount applied across invoices can never exceed what the customer actually paid."""
    for ex in _drills(arith_drill_gen.gen_carry):
        gt = ex["ground_truth"]
        billed = sum(Decimal(i["amount"]) for i in gt["invoices"])
        applied = billed - Decimal(gt["outstanding"])
        assert applied <= Decimal(gt["payment"]), ex["messages"][0]["content"]


def test_carry_answer_states_the_computed_outstanding():
    for ex in _drills(arith_drill_gen.gen_carry):
        assert Decimal(ex["ground_truth"]["outstanding"]) in _money_set(ex["messages"][1]["content"])


def test_vat_drill_math():
    for ex in _drills(arith_drill_gen.gen_vat_total):
        gt = ex["ground_truth"]
        subtotal, vat = Decimal(gt["subtotal"]), Decimal(gt["vat"])
        assert subtotal == Decimal(gt["qty"]) * Decimal(gt["unit"])
        assert abs(vat - subtotal * Decimal(gt["vat_rate"]) / 100) <= Decimal("0.01")
        assert Decimal(gt["total"]) == subtotal + vat
        assert Decimal(gt["total"]) in _money_set(ex["messages"][1]["content"])


def test_line_math_subtotal_equals_sum_of_lines():
    for ex in _drills(arith_drill_gen.gen_line_math):
        gt = ex["ground_truth"]
        expected = sum(Decimal(l["qty"]) * Decimal(l["unit"]) for l in gt["lines"])
        assert Decimal(gt["subtotal"]) == expected
        assert Decimal(gt["subtotal"]) in _money_set(ex["messages"][1]["content"])


def test_margin_is_on_revenue_and_markup_is_on_cost():
    """The exact confusion v3 exhibited — the drill must model the distinction correctly."""
    for ex in _drills(arith_drill_gen.gen_margin):
        gt = ex["ground_truth"]
        cost, revenue, profit = (Decimal(gt["cost"]), Decimal(gt["revenue"]),
                                 Decimal(gt["profit"]))
        assert profit == revenue - cost
        assert abs(Decimal(gt["margin_pct"]) - profit / revenue * 100) <= Decimal("0.05")
        assert abs(Decimal(gt["markup_pct"]) - profit / cost * 100) <= Decimal("0.05")
        assert Decimal(gt["margin_pct"]) < Decimal(gt["markup_pct"])   # always true for profit>0


def test_vat_rate_is_never_rendered_with_a_trailing_zero():
    """'7.50%' would fail the fact eval's `7\\.5\\s*%` pattern — training must not teach it."""
    for ex in _drills(arith_drill_gen.gen_vat_total, n=80):
        assert "7.50%" not in ex["messages"][1]["content"]


# --------------------------------------------------------------------------
# Intelligence drills
# --------------------------------------------------------------------------

def test_tax_conclusion_matches_the_threshold_logic():
    """Small-company status must follow BOTH thresholds AND the professional-services rule."""
    rules = intelligence_drill_gen.RULES
    for ex in _drills(intelligence_drill_gen.gen_tax_conclusion, n=80):
        gt = ex["ground_truth"]
        expected = (Decimal(gt["turnover"]) <= rules.small_turnover_max
                    and Decimal(gt["assets"]) <= rules.small_assets_max
                    and not gt["professional_services"])
        assert gt["is_small"] == expected, ex["messages"][0]["content"]


def test_tax_conclusion_states_an_explicit_verdict():
    """Reciting the rule without concluding is the def-4 defect; every drill must conclude."""
    for ex in _drills(intelligence_drill_gen.gen_tax_conclusion, n=80):
        answer = ex["messages"][1]["content"]
        assert ("You qualify" in answer) or ("do not qualify" in answer)


def test_professional_services_never_qualify_regardless_of_size():
    for ex in _drills(intelligence_drill_gen.gen_tax_conclusion, n=120):
        if ex["ground_truth"]["professional_services"]:
            assert ex["ground_truth"]["is_small"] is False
            assert "30%" in ex["messages"][1]["content"]


def test_narration_drills_never_invent_a_figure():
    """THE property the product rests on. If a training answer contains money absent from
    its verified block, we would be teaching the model to fabricate figures."""
    for ex in _drills(intelligence_drill_gen.gen_narration, n=40):
        block = ex["ground_truth"]["verified_block"]
        answer = ex["messages"][1]["content"]
        invented = _money_set(answer) - _money_set(block)
        assert not invented, f"invented {invented} in {ex['scenario_family']}"


def test_narration_prompt_carries_the_verified_header():
    """The app sends this exact header; training must match it or the skill won't transfer."""
    for ex in _drills(intelligence_drill_gen.gen_narration, n=20):
        assert intelligence_drill_gen.VERIFIED_HEADER in ex["messages"][0]["content"]


# --------------------------------------------------------------------------
# Shared schema
# --------------------------------------------------------------------------

@pytest.mark.parametrize("gen", [arith_drill_gen.gen_carry, arith_drill_gen.gen_vat_total,
                                 arith_drill_gen.gen_line_math, arith_drill_gen.gen_margin,
                                 intelligence_drill_gen.gen_tax_conclusion,
                                 intelligence_drill_gen.gen_narration])
def test_schema_shape(gen):
    ex = gen(random.Random(3))
    assert set(ex.keys()) >= {"id", "category", "scenario_family", "messages", "ground_truth"}
    assert [m["role"] for m in ex["messages"]] == ["user", "assistant"]
    assert ex["messages"][0]["content"] and ex["messages"][1]["content"]
    json.dumps(ex)          # must be serialisable to JSONL
