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
  python3 -c "
import json
r = json.load(open('artifacts/local_report.json'))
print('peak_rss_mb   :', r['memory']['peak_rss_mb'], '  (ceiling 6500, hard DQ 7168)')
print('tps_generation:', r['throughput']['tokens_per_second_generation'],
      '  (NOT the audited number — see docker/Dockerfile header)')
print('throttled     :', r['cpu_thermal']['throttled'])
"
fi
