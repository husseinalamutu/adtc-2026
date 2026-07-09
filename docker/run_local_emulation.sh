#!/usr/bin/env bash
# Build + run the local emulated-VM harness against submission/.
#
# Usage:
#   bash docker/run_local_emulation.sh                 # fast, native arm64 — OOM/pipeline check only
#   bash docker/run_local_emulation.sh --x86            # slow, QEMU x86 — correctness pre-flight
#
# Neither mode's TPS number is a substitute for infra/provision_benchmark_vm.sh on a real
# x86 target-class cloud VM. See docker/Dockerfile's header comment for exactly what each
# mode is (and isn't) trustworthy for.
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root

PLATFORM_FLAG=()
TAG="adtc-emu:arm64"
if [[ "${1:-}" == "--x86" ]]; then
  PLATFORM_FLAG=(--platform linux/amd64)
  TAG="adtc-emu:amd64"
  echo "==> Building for linux/amd64 (QEMU emulation — slow, but instruction-set-faithful)"
else
  echo "==> Building native (fast — for OOM/pipeline checks only, NOT TPS numbers)"
fi

docker build ${PLATFORM_FLAG[@]+"${PLATFORM_FLAG[@]}"} -t "$TAG" -f docker/Dockerfile docker/

if ! ls submission/model/*.gguf >/dev/null 2>&1; then
  echo
  echo "!! No GGUF found under submission/model/ — this will fail at 'model file not found'." >&2
  echo "   That's expected until build/04_imatrix_quantize.sh has produced one." >&2
fi

mkdir -p artifacts
echo "==> Running: adtc-profiler run --submission /submission --mode participant --skip-accuracy"
docker run --rm \
  ${PLATFORM_FLAG[@]+"${PLATFORM_FLAG[@]}"} \
  --cpus=4 --memory=7.5g \
  -v "$(pwd)/submission:/submission:ro" \
  -v "$(pwd)/artifacts:/artifacts" \
  "$TAG" \
  run --submission /submission --mode participant --output /artifacts/local_report.json --skip-accuracy

echo
if [ -f artifacts/local_report.json ]; then
  # Whether the TPS is trustworthy depends on the HOST arch:
  #  - arm64 host (Apple Silicon Mac): Docker runs an ARM (or QEMU-x86) container -> TPS is NOT
  #    representative of the x86 audit. Memory IS (arch-independent).
  #  - x86_64 host (a real Intel/AMD PC): the container is native x86-64 built with the audit's
  #    exact SIMD-off flags -> TPS IS representative (within audit tolerance, esp. on a 4c/8GB
  #    target-class laptop). This is the number that closes the 30% speed score.
  HOST_ARCH="$(uname -m)"
  python3 - "$HOST_ARCH" <<'PY'
import json, sys
arch = sys.argv[1]
r = json.load(open('artifacts/local_report.json'))
tps = r['throughput']['tokens_per_second_generation']
rss = r['memory']['peak_rss_mb']
print(f"peak_rss_mb   : {rss:.0f}   (ceiling 6500, hard DQ 7168)  [trustworthy on any host]")
if arch in ("x86_64", "amd64"):
    verdict = "clears the 15-TPS floor" if tps >= 15 else "BELOW the 15-TPS floor"
    print(f"tps_generation: {tps:.1f}   ✅ REAL x86 number ({arch} host) — {verdict}")
    print("                (on a 4c/8GB target-class laptop this is within audit tolerance)")
else:
    print(f"tps_generation: {tps:.1f}   ⚠️  NOT representative ({arch} host, not x86) — ignore; run on an x86 PC")
print(f"throttled     : {r['cpu_thermal']['throttled']}")
PY
fi
