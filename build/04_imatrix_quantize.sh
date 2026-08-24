#!/usr/bin/env bash
# Compute a domain-representative importance matrix, then quantize to Q4_K_M.
# Imatrix is what recovers most of the accuracy Q4_K_M would otherwise cost — see
# REPORT.md (quantization). Never skip it to save time.
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

# IMATRIX ON A Q8_0 COPY, ON GPU. The f16 model (6.2GB) OOMs Metal on an 8GB Mac, so running
# imatrix on it forces CPU — which is brutally slow (~71s/pass over ~110 chunks ≈ 2.5 HOURS,
# measured 2026-07-09). Instead we compute the imatrix on a Q8_0 copy (~3.3GB, fits Metal fully)
# with full GPU offload: Q8_0 is near-lossless (~0.1% error), so its per-tensor activation
# statistics are effectively identical to f16's — a standard, well-established shortcut. This
# runs in ~2 min on GPU instead of hours. The imatrix is then applied to the F16 -> Q4_K_M
# quantize (below), so final accuracy is unaffected.
Q8_MODEL="gguf/model-Q8_0.gguf"
echo "==> Quantizing f16 -> Q8_0 (fast, for GPU imatrix calibration only)"
[ -f "$Q8_MODEL" ] || "$QUANTIZE_BIN" "$F16_MODEL" "$Q8_MODEL" Q8_0

echo "==> Computing imatrix on Q8_0 with full GPU offload (-ngl 99)"
"$IMATRIX_BIN" -m "$Q8_MODEL" -f calibration_text.txt -o imatrix.dat -ngl 99 -c 512 -t 8

echo "==> Quantizing f16 -> $QUANT_TYPE with imatrix"
mkdir -p gguf
OUT="gguf/model-${QUANT_TYPE}.gguf"
"$QUANTIZE_BIN" --imatrix imatrix.dat "$F16_MODEL" "$OUT" "$QUANT_TYPE"

echo
echo "DONE. -> $OUT"
ls -la "$OUT"
echo "Next: 05_smoke_test.sh, then copy to model/ and re-run benchmark/telemetry_test.py on the TARGET-CLASS VM (not this Mac)."
