#!/usr/bin/env python3
"""
Build a domain-representative calibration text file for llama-imatrix from
data/out/train.jsonl. Sampling from the fine-tune's own domain (not generic text) is what
makes the imatrix actually recover accuracy on OUR domain at Q4_K_M (see REPORT.md, quantization).
"""
import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-in", default=str(ROOT / "data" / "out" / "train.jsonl"))
    ap.add_argument("--out", default="calibration_text.txt")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rows = [json.loads(l) for l in Path(args.train_in).read_text().splitlines() if l.strip()]
    rng = random.Random(args.seed)
    rng.shuffle(rows)
    sample = rows[: args.n]

    with open(args.out, "w") as f:
        for r in sample:
            for m in r["messages"]:
                f.write(m["content"].strip() + "\n\n")

    print(f"Wrote {len(sample)} examples' text -> {args.out}")


if __name__ == "__main__":
    main()
