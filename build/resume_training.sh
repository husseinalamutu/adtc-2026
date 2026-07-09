#!/usr/bin/env bash
# Resume the real fine-tune from the latest checkpoint, DETACHED (survives session teardown).
#
# Why this exists: a full 1200-iter run (~70 min) outlives a single session window, and
# background jobs die at teardown. mlx_lm.lora checkpoints every save_every (100) iters to
# adapters/NNNNNNN_adapters.safetensors. This script finds the newest checkpoint, computes how
# many iters remain, and relaunches with resume_adapter_file set + iters reduced accordingly.
# Idempotent: run it again after any teardown until it reports the target iters are done.
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

CONFIG=mlx_lora_config.yaml
LOG=train_real.log
TARGET_ITERS=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG'))['iters'])")
ADAPTER_DIR=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG'))['adapter_path'])")

# already running?
if pgrep -f "mlx_lm.lora --config $CONFIG" >/dev/null; then
  echo "Training already running (PID $(pgrep -f 'mlx_lm.lora')). Tail: tail -f $LOG"
  exit 0
fi

# find newest numbered checkpoint -> its iter count
LATEST=$(ls -1 "$ADAPTER_DIR"/[0-9]*_adapters.safetensors 2>/dev/null | sort | tail -1 || true)
if [ -z "$LATEST" ]; then
  echo "No checkpoint yet — starting a fresh run to $TARGET_ITERS iters."
  RESUME_ARGS=""
  REMAINING=$TARGET_ITERS
else
  DONE=$(basename "$LATEST" | sed -E 's/^0*([0-9]+)_adapters.*/\1/')
  REMAINING=$(( TARGET_ITERS - DONE ))
  echo "Latest checkpoint: $LATEST (iter $DONE). Remaining: $REMAINING of $TARGET_ITERS."
  if [ "$REMAINING" -le 0 ]; then
    echo "Target iters already reached. Fusing is the next step (02_merge.sh)."
    exit 0
  fi
  # mlx_lm.lora --resume-adapter-file loads weights and runs --iters MORE steps
  RESUME_ARGS="--resume-adapter-file $LATEST"
fi

echo "==> Resuming DETACHED for $REMAINING more iters (log -> $LOG)"
nohup mlx_lm.lora --config "$CONFIG" $RESUME_ARGS --iters "$REMAINING" >> "$LOG" 2>&1 &
disown
echo "launched PID $! — check with: tail -f $LOG   or   grep -E 'Val loss|Saved' $LOG | tail"
