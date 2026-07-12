#!/usr/bin/env bash
# Fetch the 1.5B candidate base (speed/accuracy tradeoff experiment) into
# build/models/Qwen2.5-1.5B-Instruct-4bit. Same resumable hf_transfer pattern as
# download_base_4bit.sh — run detached (nohup) so it survives session teardowns;
# re-run to resume. Idempotent.
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

REPO="mlx-community/Qwen2.5-1.5B-Instruct-4bit"
DEST="models/Qwen2.5-1.5B-Instruct-4bit"

if [ -f "$DEST/model.safetensors" ]; then
  echo "Base already present at $DEST — nothing to do."
  exit 0
fi

export HF_HUB_ENABLE_HF_TRANSFER=1
python3 - "$REPO" "$DEST" <<'PY'
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
echo "DOWNLOAD_1P5B_DONE"
