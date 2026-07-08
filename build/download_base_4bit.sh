#!/usr/bin/env bash
# Reproducibly fetch the 4-bit QLoRA training base into build/models/Qwen2.5-3B-Instruct-4bit.
# Pinned to the revision in config.yaml. Uses hf_transfer (chunked, parallel, resumable) because
# this network kills single long-lived transfers — a plain download stalls mid-file (confirmed
# 2026-07-08). If it still stalls, the manual fallback is at the bottom of this file.
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

REPO="mlx-community/Qwen2.5-3B-Instruct-4bit"
REV="4f83f8f146fdf28b512a06562b671d7af4fab457"   # keep in sync with config.yaml training_revision
DEST="models/Qwen2.5-3B-Instruct-4bit"

if [ -f "$DEST/model.safetensors" ]; then
  echo "Base already present at $DEST — nothing to do."
  exit 0
fi

export HF_HUB_ENABLE_HF_TRANSFER=1
pip install -q hf_transfer huggingface_hub
python3 - "$REPO" "$REV" "$DEST" <<'PY'
import sys, shutil
from pathlib import Path
from huggingface_hub import snapshot_download
repo, rev, dest = sys.argv[1], sys.argv[2], sys.argv[3]
src = snapshot_download(repo, revision=rev, max_workers=8)
Path(dest).mkdir(parents=True, exist_ok=True)
for f in Path(src).iterdir():
    if f.is_file():
        shutil.copy(f, Path(dest) / f.name)
print("base ready at", dest)
PY

# MANUAL FALLBACK if the network stalls even hf_transfer:
#   Download each file from https://huggingface.co/mlx-community/Qwen2.5-3B-Instruct-4bit/tree/main
#   (browser resumes better than curl here) into build/models/Qwen2.5-3B-Instruct-4bit/.
#   Required files: config.json model.safetensors model.safetensors.index.json tokenizer.json
#   tokenizer_config.json vocab.json merges.txt added_tokens.json special_tokens_map.json
