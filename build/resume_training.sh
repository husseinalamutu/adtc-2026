#!/usr/bin/env bash
# Resume the real fine-tune from the latest checkpoint, DETACHED (survives session teardown).
#
# Why: a full 1200-iter run (~57 min) outlives a session window, and even nohup'd processes die
# when the whole container is torn down. mlx_lm.lora checkpoints every save_every (100) iters.
#
# CORRECTNESS NOTE: mlx restarts its within-run checkpoint numbering at 0000100 on every resume,
# so a numbered filename does NOT equal global progress. We therefore track global progress in
# adapters/base_offset.txt = (iters completed by all PRIOR runs). On each resume:
#   global_done   = base_offset + <latest within-run checkpoint number>
#   new_offset    = global_done   (persisted before relaunch)
#   remaining     = TARGET_ITERS - global_done
# and we always resume WEIGHTS from adapters/adapters.safetensors (mlx overwrites it with the
# latest every save), which is guaranteed to be the most recent regardless of numbering.
# Idempotent: re-run after any teardown until it reports the target is reached.
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

CONFIG="${1:-mlx_lora_config.yaml}"   # optional arg: alternate config (e.g. mlx_lora_config.1p5b.yaml)
LOG="${2:-train_real.log}"
ADAPTER_DIR=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG'))['adapter_path'])")
TARGET_ITERS=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG'))['iters'])")
OFFSET_FILE="$ADAPTER_DIR/base_offset.txt"

if pgrep -f "mlx_lm.lora --config $CONFIG|train_launcher.py --config $CONFIG" >/dev/null; then
  echo "Training already running (PID $(pgrep -f 'mlx_lm.lora|train_launcher.py')). Tail: tail -f $LOG"
  exit 0
fi

BASE_OFFSET=$(cat "$OFFSET_FILE" 2>/dev/null || echo 0)
LATEST_NUM=$(ls -1 "$ADAPTER_DIR"/[0-9]*_adapters.safetensors 2>/dev/null \
  | sed -E 's/.*\/0*([0-9]+)_adapters.*/\1/' | sort -n | tail -1 || true)
LATEST_NUM=${LATEST_NUM:-0}
GLOBAL_DONE=$(( BASE_OFFSET + LATEST_NUM ))
REMAINING=$(( TARGET_ITERS - GLOBAL_DONE ))

echo "base_offset=$BASE_OFFSET  latest_within_run=$LATEST_NUM  ->  global_done=$GLOBAL_DONE / $TARGET_ITERS"
if [ "$REMAINING" -le 0 ]; then
  echo "Target reached ($GLOBAL_DONE iters). Next: bash 02_merge.sh"
  exit 0
fi

RESUME_ARGS=""
WEIGHTS="$ADAPTER_DIR/adapters.safetensors"
if [ -f "$WEIGHTS" ]; then
  RESUME_ARGS="--resume-adapter-file $WEIGHTS"
  # persist the new base offset, then clear stale numbered checkpoints so within-run numbering
  # restarts cleanly from this resume (weights already captured in adapters.safetensors).
  echo "$GLOBAL_DONE" > "$OFFSET_FILE"
  # PRESERVE FIRST. Deleting these outright cost us the v3 adapter (2026-07-13) and makes
  # eval-based checkpoint selection impossible — archive each under its GLOBAL number.
  mkdir -p adapters_best
  for f in "$ADAPTER_DIR"/[0-9]*_adapters.safetensors; do
    [ -e "$f" ] || continue
    n=$(basename "$f" | sed -E 's/^0*([0-9]+)_adapters.*/\1/')
    cp -n "$f" "adapters_best/global$(printf '%04d' $((BASE_OFFSET + n)))_adapters.safetensors"
  done
  rm -f "$ADAPTER_DIR"/[0-9]*_adapters.safetensors
else
  echo "No prior weights — fresh run to $TARGET_ITERS iters."
  mkdir -p "$ADAPTER_DIR"
  echo 0 > "$OFFSET_FILE"
fi

echo "==> Resuming DETACHED for $REMAINING more iters (global $GLOBAL_DONE -> $TARGET_ITERS)"
# train_launcher.py = mlx_lm.lora + Metal memory caps (IOGPU kernel-panic workaround, FB22091885)
nohup python3 train_launcher.py --config "$CONFIG" $RESUME_ARGS --iters "$REMAINING" >> "$LOG" 2>&1 &
disown
echo "launched PID $!  — tail -f $LOG"
