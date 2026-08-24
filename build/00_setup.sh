#!/usr/bin/env bash
# One-time setup: MLX for local QLoRA fine-tuning + a local Metal-accelerated llama.cpp
# build for the dev loop (conversion, imatrix, quantize, smoke-testing).
#
# IMPORTANT: this local llama.cpp build is for DEVELOPMENT ONLY. The TPS/RSS numbers you
# submit must come from an x86 target-class build, not
# this Mac — Apple Silicon performance characteristics don't transfer. See REPORT.md.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Python venv"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q --upgrade pip

echo "==> MLX + mlx-lm (Apple Silicon fine-tuning)"
pip install -q mlx mlx-lm
# mlx-lm 0.31.3 DECLARES transformers>=5.0.0 but its tokenizer_utils.py actually breaks on
# transformers 5.x (AutoTokenizer.register() signature changed; mlx_lm still calls the 4.x
# form). Confirmed 2026-07-07: pip installs transformers 5.13.0 by default, which fails at
# import with "AttributeError: 'str' object has no attribute '__module__'". Pin down to the
# last working 4.x line until mlx-lm actually catches up to its own declared requirement.
pip install -q "transformers<5"

echo "==> huggingface_hub (model download) + pyyaml (config)"
pip install -q huggingface_hub pyyaml

echo "==> Local llama.cpp (Metal build, dev-loop only)"
mkdir -p ~/adtc-local && cd ~/adtc-local
if [ ! -d llama.cpp ]; then
  git clone --quiet https://github.com/ggml-org/llama.cpp.git
fi
cd llama.cpp
git fetch --quiet --all

LLAMACPP_COMMIT=$(python3 -c "
import yaml
print(yaml.safe_load(open('$(cd "$(dirname "$0")" && pwd)/config.yaml'))['llamacpp']['commit'])
" 2>/dev/null || echo "master")

if [[ "$LLAMACPP_COMMIT" == TODO* ]]; then
  echo "  !! config.yaml llamacpp.commit not pinned yet — using master." >&2
  LLAMACPP_COMMIT="master"
fi
git checkout --quiet "$LLAMACPP_COMMIT"

cmake -S . -B build -DGGML_METAL=ON -DGGML_NATIVE=ON >/dev/null
cmake --build build -j"$(sysctl -n hw.ncpu)" --config Release >/dev/null
echo "LLAMACPP_COMMIT=$(git rev-parse HEAD)" > ~/adtc-local/PINNED_LOCAL.txt
echo "    built: $(build/bin/llama-cli --version 2>&1 | head -1 || true)"

echo
echo "DONE. Activate with: source $(dirname "$0")/.venv/bin/activate"
echo "Local llama.cpp at ~/adtc-local/llama.cpp/build/bin/"
