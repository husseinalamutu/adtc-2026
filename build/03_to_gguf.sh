#!/usr/bin/env bash
# HF-format merged model -> GGUF f16, via llama.cpp's own converter.
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

LLAMA_DIR="$HOME/adtc-local/llama.cpp"
if [ ! -d "$LLAMA_DIR" ]; then
  echo "!! $LLAMA_DIR not found — run 00_setup.sh first." >&2
  exit 1
fi
if [ ! -d fused_model ]; then
  echo "!! fused_model/ not found — run 02_merge.sh first." >&2
  exit 1
fi

mkdir -p gguf
OUT="gguf/model-f16.gguf"

echo "==> Converting fused_model/ -> $OUT"
# convert_hf_to_gguf.py has its own small dependency set (transformers, sentencepiece, etc.)
# separate from mlx — install into the same venv, it's lightweight.
pip install -q -r "$LLAMA_DIR/requirements.txt" 2>/dev/null || pip install -q transformers sentencepiece protobuf

python3 "$LLAMA_DIR/convert_hf_to_gguf.py" fused_model --outfile "$OUT" --outtype f16

echo
echo "DONE. -> $OUT"
echo "Next: 04_imatrix_quantize.sh"
