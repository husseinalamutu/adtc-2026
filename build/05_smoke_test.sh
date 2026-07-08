#!/usr/bin/env bash
# Quick local sanity check that the quantized GGUF isn't broken — NOT a substitute for
# benchmark/telemetry_test.py on the target-class VM (Apple Silicon perf != x86 audit numbers).
set -euo pipefail
cd "$(dirname "$0")"

LLAMA_DIR="$HOME/adtc-local/llama.cpp"
CLI="$LLAMA_DIR/build/bin/llama-cli"
QUANT_TYPE=$(source .venv/bin/activate && python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['quantization']['target'])")
MODEL="gguf/model-${QUANT_TYPE}.gguf"

if [ ! -f "$MODEL" ]; then
  echo "!! $MODEL not found — run 04_imatrix_quantize.sh first." >&2
  exit 1
fi

PROMPTS=(
  "A retailer in Lagos sends this M-Pesa-style mobile money statement: TX001: NGN 45,000. Reconcile it against an outstanding invoice of NGN 45,000 for INV-2001. Is it settled?"
  "Draft a short quote for 10 bags of cement at NGN 8,500 each with 7.5% VAT for a Lagos hardware shop."
  "Is a Nigerian small company with NGN 60 million annual turnover liable for Companies Income Tax?"
)

for p in "${PROMPTS[@]}"; do
  echo "=================================================================="
  echo "PROMPT: $p"
  echo "------------------------------------------------------------------"
  # -no-cnv + -st: this llama.cpp build (b9913+) defaults -p into INTERACTIVE conversation mode
  # and then blocks at a `>` prompt waiting for input (hangs the script). -no-cnv forces
  # non-conversation single-shot; -st single-turn exits after one response. The chat template is
  # still applied so the instruct model answers properly.
  "$CLI" -m "$MODEL" -t 4 -c 2048 -n 300 -no-cnv -st -p "$p" --no-warmup 2>/dev/null
  echo
done

echo "Smoke test complete. Read the outputs above — check arithmetic and the Nigeria CIT"
echo "answer (should mention the NGN 100M small-company threshold) manually."
