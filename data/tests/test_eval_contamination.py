"""Guard: eval questions must never appear in the training corpus.

An eval the model was trained on measures memorisation, not capability — and it would be
a genuinely embarrassing thing for a judge to discover. On 2026-07-20 three fact_eval
questions WERE found verbatim in train.jsonl (the LLM drill generator independently
produced the same obvious phrasing, e.g. "What is the current VAT rate in Nigeria?").
They were rephrased; this test makes the regression impossible to reintroduce silently.

Near-duplicates are reported but not failed: for a small fact base, a paraphrase of
"what is the VAT rate" is unavoidable if you drill the fact at all. Verbatim identity is
the line, because that is what turns recall into lookup.
"""
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "build"))

import pytest

from arith_eval import CASES          # noqa: E402
from fact_eval import QUESTIONS       # noqa: E402

TRAIN = ROOT / "data/out/train.jsonl"
HOLDOUT = ROOT / "data/out/holdout.jsonl"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _corpus() -> set[str]:
    prompts = set()
    for path in (TRAIN, HOLDOUT):
        if not path.exists():
            pytest.skip(f"{path} not built yet")
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                prompts.add(_norm(json.loads(line)["messages"][0]["content"]))
    return prompts


def _eval_questions() -> list[tuple[str, str]]:
    return ([(q[0], q[3]) for q in QUESTIONS] + [(c[0], c[2]) for c in CASES])


def test_no_eval_question_appears_verbatim_in_training():
    corpus = _corpus()
    leaks = [(qid, q) for qid, q in _eval_questions() if _norm(q) in corpus]
    assert not leaks, (
        "eval questions found verbatim in the training corpus — the gate would be "
        f"measuring memorisation: {[qid for qid, _ in leaks]}")


def test_near_duplicate_rate_is_reported_and_bounded():
    """Paraphrase overlap is expected; a flood of it would mean the eval has stopped
    testing generalisation at all."""
    corpus = list(_corpus())
    questions = _eval_questions()
    near = []
    for qid, q in questions:
        if difflib.get_close_matches(_norm(q), corpus, n=1, cutoff=0.90):
            near.append(qid)
    ratio = len(near) / len(questions)
    print(f"\nnear-duplicate (>=0.90) eval questions: {len(near)}/{len(questions)} "
          f"({ratio:.0%}) — {near}")
    assert ratio < 0.35, f"too much paraphrase overlap with training: {near}"


def test_eval_ids_are_unique():
    ids = [qid for qid, _ in _eval_questions()]
    assert len(ids) == len(set(ids))
