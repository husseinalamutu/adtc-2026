#!/usr/bin/env bash
# 1.5B CANDIDATE build (speed/accuracy tradeoff experiment) — same chain as build_final.sh
# (fuse -> f16 GGUF -> imatrix-on-Q8_0-GPU -> Q4_K_M) but into isolated fused_1p5b/ and
# gguf_1p5b/ so the SHIPPED 3B artifact in gguf/ is never touched. Resumable: each step
# guards on its output. Eval afterwards: python3 fact_eval.py --model gguf_1p5b/model-Q4_K_M.gguf
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

LLAMA_DIR="$HOME/adtc-local/llama.cpp"
BASE="models/Qwen2.5-1.5B-Instruct-4bit"
ADAPTERS="adapters_1p5b"
FUSED="fused_1p5b"
GGUF_DIR="gguf_1p5b"
IMATRIX="imatrix_1p5b.dat"

echo "=== [$(date +%H:%M:%S)] fuse ($ADAPTERS into $BASE) ==="
if [ ! -d "$FUSED" ]; then
  # --dequantize mandatory: 4-bit MLX base (see 02_merge.sh header)
  mlx_lm.fuse --model "$BASE" --adapter-path "$ADAPTERS" --dequantize --save-path "$FUSED"
fi

echo "=== [$(date +%H:%M:%S)] convert -> f16 GGUF ==="
mkdir -p "$GGUF_DIR"
[ -f "$GGUF_DIR/model-f16.gguf" ] || \
  python3 "$LLAMA_DIR/convert_hf_to_gguf.py" "$FUSED" --outfile "$GGUF_DIR/model-f16.gguf" --outtype f16

echo "=== [$(date +%H:%M:%S)] imatrix (Q8_0 on GPU) + Q4_K_M ==="
[ -f calibration_text.txt ] || python3 make_calibration_text.py --n "$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['quantization']['imatrix_calibration_samples'])")"
[ -f "$GGUF_DIR/model-Q8_0.gguf" ] || \
  "$LLAMA_DIR/build/bin/llama-quantize" "$GGUF_DIR/model-f16.gguf" "$GGUF_DIR/model-Q8_0.gguf" Q8_0
[ -f "$IMATRIX" ] || \
  "$LLAMA_DIR/build/bin/llama-imatrix" -m "$GGUF_DIR/model-Q8_0.gguf" -f calibration_text.txt -o "$IMATRIX" -ngl 99 -c 512 -t 8
[ -f "$GGUF_DIR/model-Q4_K_M.gguf" ] || \
  "$LLAMA_DIR/build/bin/llama-quantize" --imatrix "$IMATRIX" "$GGUF_DIR/model-f16.gguf" "$GGUF_DIR/model-Q4_K_M.gguf" Q4_K_M

echo "=== [$(date +%H:%M:%S)] 1P5B BUILD COMPLETE ==="
ls -la "$GGUF_DIR/model-Q4_K_M.gguf"
