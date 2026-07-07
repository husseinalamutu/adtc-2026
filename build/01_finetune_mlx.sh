#!/usr/bin/env bash
# QLoRA fine-tune via mlx_lm.lora, driven entirely by mlx_lora_config.yaml (mlx_lm's own
# config schema — LoRA parameters can only be set there, not via CLI flags).
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

MODEL=$(python3 -c "import yaml; print(yaml.safe_load(open('mlx_lora_config.yaml'))['model'])")
REV=$(python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['base_model']['hf_revision'])")
if [[ "$REV" == TODO* ]]; then
  echo "!! config.yaml base_model.hf_revision is not pinned yet — fill it in before a real run." >&2
  echo "   (proceeding with the unpinned repo default for now: $MODEL)" >&2
fi

echo "==> Preparing MLX-format training data (data/out/holdout.jsonl stays untouched)"
python3 prepare_mlx_data.py

echo "==> Fine-tuning: $MODEL"
mlx_lm.lora --config mlx_lora_config.yaml

echo
echo "DONE. LoRA adapters -> adapters/"
echo "If this OOM'd or swapped heavily: lower batch_size/max_seq_length in mlx_lora_config.yaml,"
echo "or drop to a smaller model — see build/README.md hardware note."
