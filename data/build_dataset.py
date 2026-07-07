#!/usr/bin/env python3
"""
Merge generator outputs -> deduped, quality-filtered, split train/holdout dataset.

The split is BY SCENARIO FAMILY, not random-by-row: every `scenario_family` value is
assigned wholesale to either train or holdout. This means the holdout set contains
business-type/topic/country *combinations* the fine-tune never saw at all, not just
different random numbers plugged into a seen template — a much closer proxy for the
2 hidden judge prompts (organizers write fresh prompts in-domain, not just fresh numbers).

Usage:
    python build_dataset.py --inputs out/templated.jsonl out/teacher.jsonl --out-dir out
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

MIN_ANSWER_CHARS = 20
MAX_ANSWER_CHARS = 6000
HOLDOUT_FAMILY_FRACTION = 0.12  # fraction of *families*, not rows, held out


def load(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"  skip (missing): {p}")
            continue
        with path.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def quality_ok(row: dict) -> bool:
    msgs = row.get("messages", [])
    if len(msgs) != 2 or msgs[0]["role"] != "user" or msgs[1]["role"] != "assistant":
        return False
    q, a = msgs[0]["content"], msgs[1]["content"]
    if not q or not a:
        return False
    if not (MIN_ANSWER_CHARS <= len(a) <= MAX_ANSWER_CHARS):
        return False
    if q.strip() == a.strip():
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args()

    print("Loading...")
    rows = load(args.inputs)
    print(f"  {len(rows)} raw rows")

    seen_ids = set()
    deduped = []
    for r in rows:
        rid = r.get("id")
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        deduped.append(r)
    print(f"  {len(deduped)} after id-dedup")

    filtered = [r for r in deduped if quality_ok(r)]
    dropped = len(deduped) - len(filtered)
    print(f"  {len(filtered)} after quality filter ({dropped} dropped)")

    by_family: dict[str, list[dict]] = defaultdict(list)
    for r in filtered:
        by_family[r.get("scenario_family", "unknown")].append(r)

    families = sorted(by_family.keys())
    rng = random.Random(args.seed)
    rng.shuffle(families)
    n_holdout_families = max(1, int(len(families) * HOLDOUT_FAMILY_FRACTION))
    holdout_families = set(families[:n_holdout_families])
    train_families = set(families[n_holdout_families:])

    train_rows = [r for f in train_families for r in by_family[f]]
    holdout_rows = [r for f in holdout_families for r in by_family[f]]
    rng.shuffle(train_rows)
    rng.shuffle(holdout_rows)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    train_path = out_dir / "train.jsonl"
    holdout_path = out_dir / "holdout.jsonl"
    with train_path.open("w") as f:
        for r in train_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with holdout_path.open("w") as f:
        for r in holdout_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    by_category = defaultdict(int)
    for r in train_rows:
        by_category[r.get("category", "?")] += 1

    print(f"\n{len(train_families)} train families / {len(holdout_families)} holdout families")
    print(f"train: {len(train_rows)} rows -> {train_path}")
    print(f"holdout: {len(holdout_rows)} rows -> {holdout_path}")
    print(f"train category counts: {dict(by_category)}")

    overlap = set(r["id"] for r in train_rows) & set(r["id"] for r in holdout_rows)
    assert not overlap, f"train/holdout id overlap: {overlap}"
    family_overlap = train_families & holdout_families
    assert not family_overlap, f"train/holdout family overlap: {family_overlap}"
    print("OK: zero train/holdout overlap (by id and by scenario family)")


if __name__ == "__main__":
    main()
