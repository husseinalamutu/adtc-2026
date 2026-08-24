#!/usr/bin/env python3
"""
Independent loss sanity-check — bypasses mlx_lm.lora's own CLI progress logging entirely.

WHY THIS EXISTS: mlx_lm.lora's printed "Train loss" / "Val loss" / "Trained Tokens" /
"Tokens/sec" are confirmed BROKEN on this machine (mlx-lm 0.29.1 and 0.31.3, mlx 0.32.0,
this Mac's Metal build) — Trained Tokens reported in the billions after a few iterations
of a tiny 8-example dataset, loss stuck at a constant. Diagnosed 2026-07-08 by calling
mlx_lm's own default_loss() directly on a real batch, bypassing train()'s aggregation:
raw loss (4.47) and raw token count (47) were both correct. So the actual gradient step
is healthy — only the CLI's own aggregate console metrics are garbage. Root cause not
further isolated (suspected mx.compile + mx.distributed.all_sum interaction on this
machine); not worth chasing further since this script sidesteps it entirely.

USE: run this against a saved adapter checkpoint (or the base model, adapter_path=None)
during/after a real training run to get a TRUSTWORTHY loss number, instead of the training
console output. Compare across checkpoints to confirm loss is actually decreasing.

    python3 check_loss_sanity.py --adapter-path adapters --n-examples 20
    python3 check_loss_sanity.py --n-examples 20            # base model, no adapter (baseline)
"""
import argparse
import statistics
import types

import mlx.core as mx
from mlx_lm.tuner.datasets import CacheDataset, load_dataset
from mlx_lm.tuner.trainer import default_loss, iterate_batches
from mlx_lm.utils import load


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    ap.add_argument("--data", default="mlx_data", help="dir with train.jsonl/valid.jsonl/test.jsonl")
    ap.add_argument("--split", default="valid", choices=["train", "valid", "test"])
    ap.add_argument("--adapter-path", default=None, help="e.g. adapters (omit for base model)")
    ap.add_argument("--n-examples", type=int, default=20)
    ap.add_argument("--max-seq-length", type=int, default=384)
    args = ap.parse_args()

    print(f"Loading {args.model}" + (f" + adapter {args.adapter_path}" if args.adapter_path else " (no adapter)"))
    load_kwargs = {"adapter_path": args.adapter_path} if args.adapter_path else {}
    model, tokenizer = load(args.model, **load_kwargs)

    ds = load_dataset(
        types.SimpleNamespace(
            train=True, test=False, data=args.data,
            hf_dataset=None, prompt_feature="prompt", completion_feature="completion",
            chat_feature="messages", mask_prompt=False,
        ),
        tokenizer,
    )
    split_idx = {"train": 0, "valid": 1, "test": 2}[args.split]
    dataset = CacheDataset(ds[split_idx])
    n = min(args.n_examples, len(dataset))
    print(f"Evaluating on {n} real examples from {args.split} split (raw per-batch loss, bypassing CLI aggregation)")

    batch_iter = iterate_batches(
        dataset=dataset, batch_size=1, max_seq_length=args.max_seq_length,
        comm_group=mx.distributed.init(),
    )
    losses, tok_counts = [], []
    for i, batch in zip(range(n), batch_iter):
        loss_val, toks = default_loss(model, *batch)
        mx.eval(loss_val, toks)
        l, t = loss_val.item(), toks.item()
        assert 0 < t < 10_000, f"example {i}: token count {t} is not sane — investigate before trusting this run"
        losses.append(l)
        tok_counts.append(t)

    print(f"\nmean loss  : {statistics.mean(losses):.4f}")
    print(f"median loss: {statistics.median(losses):.4f}")
    print(f"min/max    : {min(losses):.4f} / {max(losses):.4f}")
    print(f"mean tokens/example: {statistics.mean(tok_counts):.1f}  (sanity: should be tens-hundreds, not millions)")


if __name__ == "__main__":
    main()
