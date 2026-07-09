#!/usr/bin/env bash
# Chain the post-training build: fuse (best checkpoint) -> GGUF f16 -> imatrix+Q4_K_M -> smoke.
# Detached + logged so the ~10-min sequence survives a session teardown. Each step guards on
# its predecessor's output, so re-running resumes from wherever it left off.
set -euo pipefail
cd "$(dirname "$0")"
exec > build_final.log 2>&1
echo "=== [$(date +%H:%M:%S)] 02_merge (fuse best checkpoint) ==="
[ -d fused_model ] || bash 02_merge.sh
echo "=== [$(date +%H:%M:%S)] 03_to_gguf ==="
[ -f gguf/model-f16.gguf ] || bash 03_to_gguf.sh
echo "=== [$(date +%H:%M:%S)] 04_imatrix_quantize ==="
[ -f gguf/model-Q4_K_M.gguf ] || bash 04_imatrix_quantize.sh
echo "=== [$(date +%H:%M:%S)] 05_smoke_test ==="
bash 05_smoke_test.sh
echo "=== [$(date +%H:%M:%S)] BUILD COMPLETE ==="
ls -la gguf/model-Q4_K_M.gguf
