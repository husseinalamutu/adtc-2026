#!/usr/bin/env bash
# Compute a domain-representative importance matrix, then quantize to Q4_K_M.
# Imatrix is what recovers most of the accuracy Q4_K_M would otherwise cost — see
# STRATEGY.md §7. Never skip it to save time.
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

LLAMA_DIR="$HOME/adtc-local/llama.cpp"
IMATRIX_BIN="$LLAMA_DIR/build/bin/llama-imatrix"
QUANTIZE_BIN="$LLAMA_DIR/build/bin/llama-quantize"
F16_MODEL="gguf/model-f16.gguf"
QUANT_TYPE=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['quantization']['target'])")
N_SAMPLES=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['quantization']['imatrix_calibration_samples'])")

if [ ! -f "$F16_MODEL" ]; then
  echo "!! $F16_MODEL not found — run 03_to_gguf.sh first." >&2
  exit 1
fi
if [ ! -x "$IMATRIX_BIN" ] || [ ! -x "$QUANTIZE_BIN" ]; then
  echo "!! llama-imatrix/llama-quantize not built — run 00_setup.sh first." >&2
  exit 1
fi

echo "==> Building calibration text from data/out/train.jsonl ($N_SAMPLES samples)"
python3 make_calibration_text.py --n "$N_SAMPLES"

echo "==> Computing imatrix (CPU-only; f16 is 6.2GB and Metal OOMs on an 8GB Mac)"
# -ngl 0 forces CPU: our local llama.cpp is a Metal build, and loading the 6.2GB f16 model into
# the GPU working set + batch activations exceeds 8GB unified memory (confirmed OOM 2026-07-08:
# "Insufficient Memory kIOGPUCommandBufferCallbackErrorOutOfMemory"). CPU is slower but safe.
# Small -b/-ub keeps CPU-side activation buffers modest. On the TARGET-CLASS x86 VM this step
# runs on CPU anyway (no Metal), so these flags are harmless there.
"$IMATRIX_BIN" -m "$F16_MODEL" -f calibration_text.txt -o imatrix.dat \
  -ngl 0 -c 512 -b 512 -ub 128 -t 4

echo "==> Quantizing to $QUANT_TYPE with imatrix"
mkdir -p gguf
OUT="gguf/model-${QUANT_TYPE}.gguf"
"$QUANTIZE_BIN" --imatrix imatrix.dat "$F16_MODEL" "$OUT" "$QUANT_TYPE"

echo
echo "DONE. -> $OUT"
ls -la "$OUT"
echo "Next: 05_smoke_test.sh, then copy to submission/model/ and re-run benchmark/telemetry_test.py on the TARGET-CLASS VM (not this Mac)."
