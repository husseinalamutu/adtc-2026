#!/usr/bin/env bash
# Fuse LoRA adapters into the base model -> HF-format merged safetensors.
# Deliberately does NOT use mlx_lm.fuse's --export-gguf: that path skips imatrix calibration,
# and imatrix is where we recover most of the accuracy Q4_K_M would otherwise cost (STRATEGY.md
# §7). We go through llama.cpp's own converter instead (03_to_gguf.sh) so imatrix is in the loop.
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

MODEL=$(python3 -c "import yaml; print(yaml.safe_load(open('mlx_lora_config.yaml'))['model'])")
ADAPTER_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('mlx_lora_config.yaml'))['adapter_path'])")

if [ ! -d "$ADAPTER_PATH" ]; then
  echo "!! $ADAPTER_PATH not found — run 01_finetune_mlx.sh first." >&2
  exit 1
fi

echo "==> Fusing LoRA adapters ($ADAPTER_PATH) into $MODEL"
# --dequantize is MANDATORY: our base is a 4-bit MLX model. Without it, mlx_lm.fuse fuses the
# adapter into the STILL-4-bit weights (U32-packed + .scales/.biases tensors), and
# convert_hf_to_gguf.py (03) cannot read MLX's quantization format — it needs plain fp16.
# With --dequantize we get a clean ~6.2GB fp16 HF model (verified 2026-07-08: 0 residual quant
# tensors, no 'quantization' key), which then goes GGUF f16 -> imatrix -> Q4_K_M. Confirmed the
# bug the hard way during the pipeline-validation run — do not drop this flag.
mlx_lm.fuse \
  --model "$MODEL" \
  --adapter-path "$ADAPTER_PATH" \
  --dequantize \
  --save-path fused_model

echo
echo "DONE. Merged HF-format model -> fused_model/"
echo "Next: 03_to_gguf.sh"
