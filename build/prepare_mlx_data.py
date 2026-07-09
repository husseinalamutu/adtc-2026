#!/usr/bin/env python3
"""
Convert data/out/train.jsonl (our schema: id/category/scenario_family/messages/ground_truth)
into the plain {"messages": [...]} JSONL that mlx_lm.lora expects, and carve out a small
validation split FROM TRAIN ONLY.

data/out/holdout.jsonl is never touched here — it stays reserved as the overfit-guard proxy
for the 2 organizer hidden prompts (see data/build_dataset.py). Training against it, even
for "validation" loss, would defeat its purpose.
"""
import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-in", default=str(ROOT / "data" / "out" / "train.jsonl"))
    ap.add_argument("--out-dir", default=str(Path(__file__).parent / "mlx_data"))
    ap.add_argument("--val-fraction", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--oversample-category", default="nigeria_tax",
                    help="category to repeat in TRAIN for extra gradient weight (recall reinforcement)")
    ap.add_argument("--oversample-factor", type=int, default=1,
                    help="how many total copies of that category in train (1 = no oversampling)")
    args = ap.parse_args()

    train_path = Path(args.train_in)
    if not train_path.exists():
        raise SystemExit(f"{train_path} not found — run data/build_dataset.py first.")

    rows = [json.loads(l) for l in train_path.read_text().splitlines() if l.strip()]
    rng = random.Random(args.seed)
    rng.shuffle(rows)

    # Carve validation FIRST (from original rows) so val stays representative and un-duplicated.
    n_val = max(1, int(len(rows) * args.val_fraction))
    val_rows, train_rows = rows[:n_val], rows[n_val:]

    # Oversample a category in TRAIN only: repeating the (varied) Nigeria examples gives them more
    # gradient weight to override the base model's strong wrong priors on Nigerian tax numbers.
    # These are varied examples (many phrasings), not one example repeated, so this reinforces
    # the facts without memorizing a single wording.
    if args.oversample_factor > 1:
        extra = [r for r in train_rows if r.get("category") == args.oversample_category]
        added = extra * (args.oversample_factor - 1)
        train_rows = train_rows + added
        rng.shuffle(train_rows)
        print(f"oversampled '{args.oversample_category}' x{args.oversample_factor}: "
              f"+{len(added)} copies ({len(extra)} base) -> train now {len(train_rows)}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, split in [("train.jsonl", train_rows), ("valid.jsonl", val_rows)]:
        with (out_dir / name).open("w") as f:
            for r in split:
                f.write(json.dumps({"messages": r["messages"]}, ensure_ascii=False) + "\n")

    print(f"train: {len(train_rows)} -> {out_dir / 'train.jsonl'}")
    print(f"valid: {len(val_rows)} -> {out_dir / 'valid.jsonl'}")
    print("(data/out/holdout.jsonl untouched — reserved as the hidden-prompt proxy)")


if __name__ == "__main__":
    main()
