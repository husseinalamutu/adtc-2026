#!/usr/bin/env bash
# Gate-1 deliverable: idempotent, credential-free fetch of the submission GGUF into model/.
# The organizers run this in a clean clone; it must need no login and land the exact file
# that submission/metadata.json's _runtime.model_path points at.
#
# Also how the Dell (or any machine) gets the 1.93GB model that can't live in git.
set -euo pipefail
cd "$(dirname "$0")"

# --- EDIT THESE two once the HF repo exists (see submission/HUGGINGFACE_SETUP.md) ---
HF_REPO="husseinalamutu/adtc-sme-copilot-gguf"   # TODO: confirm after you create the HF model repo
HF_FILE="adtc-sme-copilot-Q4_K_M.gguf"
# -----------------------------------------------------------------------------------

DEST="model/$HF_FILE"
mkdir -p model

if [ -f "$DEST" ]; then
  echo "Model already present at $DEST — nothing to do."
  exit 0
fi

URL="https://huggingface.co/${HF_REPO}/resolve/main/${HF_FILE}?download=true"
echo "==> Downloading $HF_FILE from Hugging Face ($HF_REPO)"

# Prefer the huggingface_hub CLI (chunked + resumable — robust on flaky networks); fall back to curl.
if command -v huggingface-cli >/dev/null 2>&1; then
  HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download "$HF_REPO" "$HF_FILE" \
    --local-dir model --local-dir-use-symlinks False
elif python3 -c "import huggingface_hub" 2>/dev/null; then
  HF_HUB_ENABLE_HF_TRANSFER=1 python3 - "$HF_REPO" "$HF_FILE" <<'PY'
import sys, shutil
from pathlib import Path
from huggingface_hub import hf_hub_download
repo, fname = sys.argv[1], sys.argv[2]
p = hf_hub_download(repo_id=repo, filename=fname)
Path("model").mkdir(exist_ok=True)
shutil.copy(p, Path("model") / fname)
print("downloaded ->", Path("model") / fname)
PY
else
  curl -fL --retry 5 -o "$DEST" "$URL"
fi

echo "DONE -> $DEST"
ls -la "$DEST"
