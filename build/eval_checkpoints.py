#!/usr/bin/env python3
"""Phase E — pick the shipping checkpoint by EVAL, not by val loss.

This exists because of a measured mistake: v4 was selected on validation loss and shipped
with WORSE facts than v3 (31/37 vs 34/37). Validation loss averages over a mixed corpus and
simply does not track the two things that are scored — Nigeria fact recall and arithmetic.

For each checkpoint: fuse -> f16 GGUF -> imatrix on Q8_0 (GPU) -> Q4_K_M -> run BOTH gates.
Intermediates are deleted between checkpoints because each run costs ~11 GB of disk.

Usage:
  python3 eval_checkpoints.py --checkpoints 800 1000 1200 1400
  python3 eval_checkpoints.py --checkpoints 1400 --keep      # keep the winner's artifacts
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent
LLAMA = Path.home() / "adtc-local/llama.cpp/build"
BASE = "models/Qwen2.5-3B-Instruct-4bit"
# mlx_lm's console scripts live beside the interpreter running this file. Resolving them
# from sys.executable means the harness works whether or not the venv is activated —
# a bare `mlx_lm.fuse` would be "command not found" under the system python.
VENV_BIN = Path(sys.executable).parent
MLX_FUSE = str(VENV_BIN / "mlx_lm.fuse")

# v3, the incumbent — a new checkpoint must beat BOTH of these to ship.
GATE_FACTS = 34
GATE_ARITH = 9


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(str(c) for c in cmd[:6])}...", flush=True)
    return subprocess.run(cmd, cwd=BUILD, check=True, **kw)


def build_gguf(adapter: Path, workdir: Path) -> Path:
    """fuse -> f16 -> imatrix(Q8_0, GPU) -> Q4_K_M, mirroring build_final.sh exactly."""
    fused, gguf = workdir / "fused", workdir / "gguf"
    gguf.mkdir(parents=True, exist_ok=True)
    f16, q8, q4 = gguf / "f16.gguf", gguf / "q8.gguf", gguf / "model-Q4_K_M.gguf"
    imatrix = workdir / "imatrix.dat"

    # DISK DISCIPLINE: each artifact is deleted the moment it is no longer needed. Holding
    # fused (5.8G) + f16 (5.8G) + Q8 (3.1G) + Q4 (1.9G) at once peaks at ~16.6 GB and would
    # exhaust the free space on this machine mid-run; staged cleanup keeps the peak ~11.6 GB.
    run([MLX_FUSE, "--model", BASE, "--adapter-path", str(adapter),
         "--dequantize", "--save-path", str(fused)])
    run([sys.executable, str(Path.home() / "adtc-local/llama.cpp/convert_hf_to_gguf.py"),
         str(fused), "--outfile", str(f16), "--outtype", "f16"])
    shutil.rmtree(fused, ignore_errors=True)                      # -5.8 GB, no longer needed

    run([str(LLAMA / "bin/llama-quantize"), str(f16), str(q8), "Q8_0"])
    run([str(LLAMA / "bin/llama-imatrix"), "-m", str(q8), "-f", "calibration_text.txt",
         "-o", str(imatrix), "-ngl", "99", "-c", "512", "-t", "8"],
        stdout=subprocess.DEVNULL)
    q8.unlink(missing_ok=True)                                    # -3.1 GB, imatrix is written

    run([str(LLAMA / "bin/llama-quantize"), "--imatrix", str(imatrix),
         str(f16), str(q4), "Q4_K_M"])
    f16.unlink(missing_ok=True)                                   # -5.8 GB, only Q4 is graded
    return q4


def score(script: str, model: Path, out: Path) -> tuple[int, int]:
    res = subprocess.run([sys.executable, script, "--model", str(model), "--out", str(out)],
                         cwd=BUILD, capture_output=True, text=True)
    m = re.search(r"(\d+)/(\d+)", res.stdout.strip().splitlines()[-2] if res.stdout else "")
    if not m:
        print(res.stdout[-800:], res.stderr[-400:])
        raise RuntimeError(f"could not parse a score from {script}")
    return int(m.group(1)), int(m.group(2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoints", nargs="+", type=int, required=True)
    ap.add_argument("--adapter-dir", default="adapters")
    ap.add_argument("--keep", action="store_true", help="keep each checkpoint's Q4 GGUF")
    args = ap.parse_args()

    results = []
    for ckpt in args.checkpoints:
        name = f"{ckpt:07d}_adapters.safetensors"
        src = BUILD / args.adapter_dir / name
        if not src.exists():
            src = BUILD / "adapters_best" / f"global{ckpt:04d}_adapters.safetensors"
        if not src.exists():
            print(f"!! checkpoint {ckpt} not found — skipping")
            continue

        print(f"\n=== checkpoint {ckpt} ===", flush=True)
        workdir = BUILD / f"_ckpt_{ckpt}"
        adapter_dir = workdir / "adapter"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, adapter_dir / "adapters.safetensors")
        shutil.copy(BUILD / args.adapter_dir / "adapter_config.json",
                    adapter_dir / "adapter_config.json")

        try:
            q4 = build_gguf(adapter_dir, workdir)
            facts, facts_n = score("fact_eval.py", q4, BUILD / f"results/ckpt{ckpt}_facts.md")
            arith, arith_n = score("arith_eval.py", q4, BUILD / f"results/ckpt{ckpt}_arith.md")
            narr, narr_n = score("narration_eval.py", q4, BUILD / f"results/ckpt{ckpt}_narr.md")
            passes = facts >= GATE_FACTS and arith > GATE_ARITH
            results.append((ckpt, facts, facts_n, arith, arith_n, passes, narr, narr_n))
            print(f"  -> facts {facts}/{facts_n}, arithmetic {arith}/{arith_n}, "
                  f"narration {narr}/{narr_n}, {'SHIPPABLE' if passes else 'below gate'}", flush=True)
            if args.keep:
                shutil.move(str(q4), BUILD / f"results/model-ckpt{ckpt}-Q4_K_M.gguf")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    print("\n" + "=" * 64)
    print(f"{'ckpt':>6} {'facts':>10} {'arith':>10} {'narration':>11}  verdict")
    for ckpt, f, fn, a, an, ok, nr, nn in results:
        print(f"{ckpt:>6} {f:>5}/{fn:<4} {a:>5}/{an:<4} {nr:>6}/{nn:<4}  "
              f"{'SHIPPABLE' if ok else 'below gate'}")
    print(f"\ngate: facts >= {GATE_FACTS} AND arithmetic > {GATE_ARITH} (v3 incumbent)")
    winners = [r for r in results if r[5]]
    if winners:
        best = max(winners, key=lambda r: (r[1] + r[3] + r[6]))
        print(f"WINNER: checkpoint {best[0]} (facts {best[1]}, arithmetic {best[3]})")
    else:
        print("NO CHECKPOINT CLEARS THE GATE — ship v3 unchanged.")
    (BUILD / "results/checkpoint_selection.json").write_text(json.dumps(
        [{"checkpoint": c, "facts": f, "facts_total": fn, "arith": a, "arith_total": an,
          "narration": nr, "narration_total": nn, "shippable": ok}
         for c, f, fn, a, an, ok, nr, nn in results], indent=2))


if __name__ == "__main__":
    main()
