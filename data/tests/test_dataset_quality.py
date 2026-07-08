"""
Dataset regression tests. Run after every regeneration:

    pytest tests/ -v

These are the tests that matter most for the fine-tune: they re-derive the templated
generator's arithmetic from its own raw `ground_truth` fields and fail loudly on any
mismatch, so a bug in the generator can never silently poison training data with wrong
VAT/discount/reconciliation math.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "generators"))

import templated_gen  # noqa: E402
import nigeria_tax_gen  # noqa: E402


def _gen_examples(n=200, seed=99):
    rng = __import__("random").Random(seed)
    out = []
    for i in range(n):
        gen = templated_gen.GENERATORS[i % len(templated_gen.GENERATORS)]
        out.append(gen(rng))
    return out


# ---------------------------------------------------------------------------
# Arithmetic correctness — the highest-value test in this file
# ---------------------------------------------------------------------------
class TestInvoiceArithmetic:
    def test_subtotal_equals_sum_of_lines(self):
        for ex in _gen_examples():
            if ex["category"] not in ("invoice", "quote"):
                continue
            gt = ex["ground_truth"]
            recomputed = round(sum(l["line_total"] for l in gt["lines"]), 2)
            assert recomputed == gt["subtotal"], ex["id"]

    def test_line_total_equals_qty_times_price(self):
        for ex in _gen_examples():
            if ex["category"] not in ("invoice", "quote"):
                continue
            for line in ex["ground_truth"]["lines"]:
                expected = round(line["qty"] * line["unit_price"], 2)
                assert expected == line["line_total"], ex["id"]

    def test_discount_math(self):
        for ex in _gen_examples():
            if ex["category"] not in ("invoice", "quote"):
                continue
            gt = ex["ground_truth"]
            expected_discount = round(gt["subtotal"] * gt["discount_pct"] / 100, 2)
            assert expected_discount == gt["discount_amount"], ex["id"]
            expected_base = round(gt["subtotal"] - gt["discount_amount"], 2)
            assert expected_base == gt["taxable_base"], ex["id"]

    def test_vat_and_total(self):
        for ex in _gen_examples():
            if ex["category"] not in ("invoice", "quote"):
                continue
            gt = ex["ground_truth"]
            expected_vat = round(gt["taxable_base"] * gt["vat_rate"], 2)
            assert expected_vat == gt["vat_amount"], ex["id"]
            expected_total = round(gt["taxable_base"] + gt["vat_amount"], 2)
            assert expected_total == gt["total"], ex["id"]

    def test_total_appears_in_rendered_answer(self):
        """The final total string must literally appear in the assistant answer —
        catches a formatting/rounding drift between ground_truth and the rendered text."""
        for ex in _gen_examples():
            if ex["category"] not in ("invoice", "quote"):
                continue
            gt = ex["ground_truth"]
            total_str = f"{gt['total']:,.2f}"
            assert total_str in ex["messages"][1]["content"], ex["id"]


class TestReconciliationArithmetic:
    def test_settled_total_matches_paid_invoices(self):
        for ex in _gen_examples():
            if ex["category"] != "reconciliation":
                continue
            gt = ex["ground_truth"]
            paid = set(gt["paid_invoice_ids"])
            expected = round(sum(inv["amount"] for inv in gt["invoices"] if inv["invoice_id"] in paid), 2)
            assert expected == gt["settled_total"], ex["id"]

    def test_outstanding_total_matches_unpaid_invoices(self):
        for ex in _gen_examples():
            if ex["category"] != "reconciliation":
                continue
            gt = ex["ground_truth"]
            paid = set(gt["paid_invoice_ids"])
            expected = round(sum(inv["amount"] for inv in gt["invoices"] if inv["invoice_id"] not in paid), 2)
            assert expected == gt["outstanding_total"], ex["id"]

    def test_settled_plus_outstanding_equals_all_invoices(self):
        for ex in _gen_examples():
            if ex["category"] != "reconciliation":
                continue
            gt = ex["ground_truth"]
            total_invoices = round(sum(inv["amount"] for inv in gt["invoices"]), 2)
            assert round(gt["settled_total"] + gt["outstanding_total"], 2) == total_invoices, ex["id"]

    def test_every_paid_invoice_has_a_matching_transaction_amount(self):
        for ex in _gen_examples():
            if ex["category"] != "reconciliation":
                continue
            gt = ex["ground_truth"]
            tx_amounts = {t["amount"] for t in gt["transactions"]}
            paid = {inv["invoice_id"]: inv["amount"] for inv in gt["invoices"]}
            for inv_id in gt["paid_invoice_ids"]:
                assert paid[inv_id] in tx_amounts, f"{ex['id']}: {inv_id} marked paid but no matching tx amount"


# ---------------------------------------------------------------------------
# Determinism / uniqueness
# ---------------------------------------------------------------------------
class TestNigeriaTaxFactGrounding:
    """No API calls — pure fact-path validation. If this fails, the generator would
    crash (or silently drop rows) the moment it's run against the real API, wasting
    batch cost. Run before every nigeria_tax_gen.py invocation."""

    def test_every_fact_path_resolves(self):
        all_topics = nigeria_tax_gen.FACT_TOPICS + nigeria_tax_gen.DIASPORA_TOPICS
        for label, path in all_topics:
            nigeria_tax_gen.get_fact(path)  # raises KeyError if broken

    def test_build_requests_dry_run(self):
        # (custom_id, system, user_prompt, schema, scenario_family) tuples — see
        # generators/nigeria_tax_gen.py / _gemini_common.py for why this shape.
        reqs = nigeria_tax_gen.build_requests(30, seed=1)
        assert len(reqs) == 30
        custom_ids = [r[0] for r in reqs]
        assert len(set(custom_ids)) == 30, "custom_ids must be unique"
        families = [r[4] for r in reqs]
        assert all(f.startswith("nigeria_tax::") for f in families)

    def test_no_fact_marked_unconfirmed_is_used_without_a_confidence_tag(self):
        """Every leaf fact dict passed to the model must carry a confidence tag, or the
        anti-hallucination system prompt has nothing to hedge on."""
        for label, path in nigeria_tax_gen.FACT_TOPICS + nigeria_tax_gen.DIASPORA_TOPICS:
            fact = nigeria_tax_gen.get_fact(path)

            def check(node):
                if isinstance(node, dict):
                    if "value" in node:
                        assert "confidence" in node, f"{path}: leaf fact missing confidence tag: {node}"
                    else:
                        for v in node.values():
                            check(v)

            check(fact)


def test_generator_is_seed_deterministic():
    a = _gen_examples(n=50, seed=555)
    b = _gen_examples(n=50, seed=555)
    assert [e["id"] for e in a] == [e["id"] for e in b]


def test_ids_are_unique_at_scale():
    examples = _gen_examples(n=1000, seed=1)
    ids = [e["id"] for e in examples]
    # allow a tiny collision rate from the hash truncation, but it should be near-zero
    dup_rate = 1 - len(set(ids)) / len(ids)
    assert dup_rate < 0.01, f"unexpectedly high id collision rate: {dup_rate:.4f}"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("ex", _gen_examples(n=100, seed=2))
def test_schema_shape(ex):
    assert set(ex.keys()) >= {"id", "category", "scenario_family", "messages", "ground_truth"}
    assert len(ex["messages"]) == 2
    assert ex["messages"][0]["role"] == "user"
    assert ex["messages"][1]["role"] == "assistant"
    assert len(ex["messages"][0]["content"]) > 10
    assert len(ex["messages"][1]["content"]) > 10


# ---------------------------------------------------------------------------
# Build script: train/holdout split integrity (only runs if out/*.jsonl exist)
# ---------------------------------------------------------------------------
def _load_jsonl(path: Path):
    if not path.exists():
        return None
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


class TestBuiltDatasetSplit:
    train_path = ROOT / "out" / "train.jsonl"
    holdout_path = ROOT / "out" / "holdout.jsonl"

    def _require_built(self):
        train = _load_jsonl(self.train_path)
        holdout = _load_jsonl(self.holdout_path)
        if train is None or holdout is None:
            pytest.skip("out/train.jsonl or out/holdout.jsonl not built yet — run build_dataset.py first")
        return train, holdout

    def test_no_id_overlap(self):
        train, holdout = self._require_built()
        overlap = {r["id"] for r in train} & {r["id"] for r in holdout}
        assert not overlap, f"train/holdout id overlap: {overlap}"

    def test_no_scenario_family_overlap(self):
        train, holdout = self._require_built()
        overlap = {r["scenario_family"] for r in train} & {r["scenario_family"] for r in holdout}
        assert not overlap, f"train/holdout scenario_family overlap: {overlap}"

    def test_holdout_covers_multiple_categories(self):
        """Overfit guard: the holdout set shouldn't accidentally be all one category —
        that would make it a weak proxy for the 2 hidden judge prompts, which span the domain."""
        train, holdout = self._require_built()
        holdout_categories = {r["category"] for r in holdout}
        assert len(holdout_categories) >= 2, f"holdout only covers: {holdout_categories}"

    def test_minimum_size(self):
        train, holdout = self._require_built()
        assert len(train) >= 500, f"train set too small: {len(train)}"
        assert len(holdout) >= 20, f"holdout set too small: {len(holdout)}"
