#!/usr/bin/env bash
# Provision a target-class Ubuntu 22.04 VM (4 vCPU / 8 GB / no GPU) for ADTC benchmarking.
# Idempotent-ish: safe to re-run. Run as root (or with sudo) on a FRESH VM.
set -euo pipefail

# --- PIN THIS to the llama.cpp revision the adtc-profiler expects. ---
# Check the profiler repo (pyproject/README) and set the exact commit before trusting numbers.
LLAMACPP_COMMIT="${LLAMACPP_COMMIT:-master}"   # TODO: replace 'master' with a real 40-char SHA.

echo "==> System deps"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq build-essential cmake git curl python3 python3-pip python3-venv \
                      libcurl4-openssl-dev pipx lm-sensors >/dev/null

echo "==> Sanity: confirm this really is a ~4 vCPU / 8 GB box"
CPUS=$(nproc); MEM_GB=$(awk '/MemTotal/ {printf "%.1f", $2/1024/1024}' /proc/meminfo)
echo "    vCPUs=$CPUS  RAM=${MEM_GB} GB"
if [ "$CPUS" -gt 6 ] || [ "$(printf '%.0f' "$MEM_GB")" -gt 10 ]; then
  echo "    !! WARNING: this box is bigger than target class. TPS/RSS will NOT match the audit." >&2
fi
# Confirm no discrete GPU is being used for compute.
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "    !! WARNING: nvidia-smi present — ensure the CPU build is used (no CUDA)." >&2
fi

echo "==> Build llama.cpp (CPU-only) @ ${LLAMACPP_COMMIT}"
mkdir -p ~/adtc && cd ~/adtc
if [ ! -d llama.cpp ]; then git clone --quiet https://github.com/ggml-org/llama.cpp.git; fi
cd llama.cpp
git fetch --quiet --all
git checkout --quiet "${LLAMACPP_COMMIT}"
# CPU-only, no GPU backends. -DGGML_NATIVE=ON uses the box's own ISA (matches how the audit box runs).
cmake -S . -B build -DGGML_NATIVE=ON -DGGML_CUDA=OFF -DGGML_METAL=OFF -DLLAMA_CURL=ON >/dev/null
cmake --build build -j"$CPUS" --config Release >/dev/null
echo "    built: $(build/bin/llama-cli --version 2>&1 | head -1 || true)"
echo "LLAMACPP_COMMIT=$(git rev-parse HEAD)" > ~/adtc/PINNED.txt

echo "==> Install adtc-profiler"
pipx install "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git" 2>/dev/null \
  || pip3 install --break-system-packages "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git"
adtc-profiler --help >/dev/null 2>&1 && echo "    adtc-profiler OK" || echo "    !! verify adtc-profiler install"

echo "==> Enable temperature sensors (for thermal self-checks)"
yes | sensors-detect >/dev/null 2>&1 || true

echo
echo "DONE. llama.cpp pinned in ~/adtc/PINNED.txt"
echo "Next: bash ~/adtc/run_baseline.sh"
