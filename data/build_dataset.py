#!/usr/bin/env python3
"""
Merge generator outputs -> deduped, quality-filtered, split train/holdout dataset.

The split is BY SCENARIO FAMILY, not random-by-row: every `scenario_family` value is
assigned wholesale to either train or holdout. This means the holdout set contains
business-type/topic/country *combinations* the fine-tune never saw at all, not just
different random numbers plugged into a seen template — a much closer proxy for the
3 hidden judge prompts (organizers write fresh prompts in-domain, not just fresh numbers).

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

    # A FACT DRILL FAMILY MUST NEVER BE HELD OUT.
    # Holding out a *scenario* family tests generalisation to an unseen situation, which is
    # the point of this split. Holding out a *fact drill* family removes the fact from
    # training altogether — and a model cannot recall a tax rate it was never shown.
    # This bit us hard (2026-08-11): adding the arith::/intel:: families reshuffled the
    # split and moved the development-levy, personal-income-tax and withholding-tax drills
    # wholesale into holdout. Fact accuracy fell 34/37 -> 26/37, and two retrains chasing
    # an "exposure dilution" theory failed because the data simply was not there.
    families = sorted(by_family.keys())
    rng = random.Random(args.seed)
    rng.shuffle(families)
    holdout_eligible = [f for f in families if "_drill::" not in f]
    pinned_to_train = [f for f in families if "_drill::" in f]

    # STRATIFY by category as well. Picking holdout families from one global pool can leave
    # a whole category unrepresented purely by luck — the first fix here did exactly that,
    # emptying Nigeria out of the holdout set and silently voiding the overfit guard.
    # Every category with more than one eligible family contributes at least one.
    cat_of = {f: by_family[f][0].get("category", "unknown") for f in holdout_eligible}
    by_cat: dict[str, list[str]] = defaultdict(list)
    for f in holdout_eligible:
        by_cat[cat_of[f]].append(f)

    holdout_families: set[str] = set()
    for cat, fams in sorted(by_cat.items()):
        if len(fams) > 1:
            holdout_families.add(fams[0])          # already shuffled, so this is a random pick
    target = max(1, int(len(holdout_eligible) * HOLDOUT_FAMILY_FRACTION))
    for f in holdout_eligible:                     # top up to the target fraction
        if len(holdout_families) >= target:
            break
        holdout_families.add(f)
    train_families = (set(holdout_eligible) - holdout_families) | set(pinned_to_train)

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
