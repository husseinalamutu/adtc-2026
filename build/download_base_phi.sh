#!/usr/bin/env bash
# Fetch the Phi-3.5-mini 4-bit base (MIT licence) with the same stall-watchdog pattern as
# the other base downloads — this network wedges long transfers without erroring.
set -uo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
REPO="mlx-community/Phi-3.5-mini-instruct-4bit"
DEST="models/Phi-3.5-mini-instruct-4bit"
CACHE="$HOME/.cache/huggingface/hub/models--mlx-community--Phi-3.5-mini-instruct-4bit"
STALL_S=90
done_yet() { [ -f "$DEST/model.safetensors" ] || [ -f "$DEST/model.safetensors.index.json" ]; }
attempt=0
until done_yet; do
  attempt=$((attempt+1)); echo "=== [$(date +%H:%M:%S)] attempt $attempt ==="
  export HF_HUB_ENABLE_HF_TRANSFER=1
  python3 - "$REPO" "$DEST" <<'PY' &
import sys, shutil
from pathlib import Path
from huggingface_hub import snapshot_download
repo, dest = sys.argv[1], sys.argv[2]
src = snapshot_download(repo, max_workers=8)
Path(dest).mkdir(parents=True, exist_ok=True)
for f in Path(src).iterdir():
    if f.is_file():
        shutil.copy(f, Path(dest) / f.name)
print("base ready at", dest, flush=True)
PY
  DL=$!; last=""; stall=0
  while kill -0 "$DL" 2>/dev/null; do
    cur=$(du -s "$CACHE" 2>/dev/null | cut -f1)
    if [ "$cur" = "$last" ]; then stall=$((stall+5)); else stall=0; last="$cur"; fi
    if [ "$stall" -ge "$STALL_S" ]; then echo "  [watchdog] stalled at ${cur}KB — restarting"; kill -9 "$DL" 2>/dev/null; break; fi
    sleep 5
  done
  wait "$DL" 2>/dev/null; sleep 3
done
echo "PHI_BASE_READY"
