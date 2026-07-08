#!/usr/bin/env bash
# Provision a target-class Ubuntu 22.04 VM (4 vCPU / 8 GB / no GPU) for ADTC benchmarking.
# Idempotent-ish: safe to re-run. Run as root (or with sudo) on a FRESH VM.
set -euo pipefail

# --- llama.cpp revision ---
# CONFIRMED (2026-07-07, read directly from the profiler's Dockerfile source): the official
# build itself defaults to `ARG LLAMACPP_REF=master` — there is NO pinned commit upstream.
# This is a real reproducibility gap on the organizers' side (master moves), not something
# we can fully close ourselves. Mitigate it: pin to a specific commit ourselves, matching
# build/config.yaml and docker/Dockerfile's verified build (`llama-cli --version` -> "bec4772").
# Re-pin + re-benchmark shortly before Gate 1 submission so this reflects a recent master,
# not a stale one — check `git log --oneline -1 origin/master` on the VM before assuming this
# SHA is still current.
LLAMACPP_COMMIT="${LLAMACPP_COMMIT:-bec4772f6a2527d371557b5d2032641e5ff7619c}"

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
# CRITICAL: these flags are copied VERBATIM from the official adtc-profiler Dockerfile
# (github.com/Africa-Deep-Tech-Foundation/adtc-profiler, profiler/Dockerfile, stage 1).
# The audit deliberately builds with GGML_NATIVE=OFF and every SIMD extension disabled —
# a lowest-common-denominator CPU baseline, NOT the VM's native instruction set. Building
# with GGML_NATIVE=ON (as an earlier version of this script did) produces a FASTER binary
# than the audit uses, which would silently overstate our TPS margin. Do not "optimize"
# this build — matching the audit exactly is the entire point of this VM.
cmake -S . -B build \
  -DBUILD_SHARED_LIBS=OFF \
  -DGGML_NATIVE=OFF \
  -DGGML_AVX=OFF \
  -DGGML_AVX2=OFF \
  -DGGML_AVX512=OFF \
  -DGGML_FMA=OFF \
  -DGGML_F16C=OFF \
  -DGGML_BLAS=OFF \
  -DGGML_CUDA=OFF \
  -DGGML_METAL=OFF >/dev/null
cmake --build build --config Release --target llama-bench llama-cli llama-server -j"$CPUS" >/dev/null
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
