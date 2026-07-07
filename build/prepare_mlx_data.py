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
    args = ap.parse_args()

    train_path = Path(args.train_in)
    if not train_path.exists():
        raise SystemExit(f"{train_path} not found — run data/build_dataset.py first.")

    rows = [json.loads(l) for l in train_path.read_text().splitlines() if l.strip()]
    rng = random.Random(args.seed)
    rng.shuffle(rows)

    n_val = max(1, int(len(rows) * args.val_fraction))
    val_rows, train_rows = rows[:n_val], rows[n_val:]

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
