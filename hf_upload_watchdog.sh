#!/usr/bin/env bash
# Auto-resume HF upload through a flaky network. Xet dedup means each (re)start resumes from
# whatever already landed, so we just relaunch on any stall/exit until the GGUF is committed.
# A watchdog kills the uploader if the log %-progress stops advancing for STALL_S seconds
# (a wedged dead-socket hang doesn't exit on its own).
set -uo pipefail
cd "$(dirname "$0")"
set -a; source data/.env; set +a
source data/.venv/bin/activate 2>/dev/null || true
export HF_HUB_ENABLE_HF_TRANSFER=0
REPO="HusseinAlamutu/alamz-tech-sme-copilot-gguf"
STALL_S=75
LOG=hf_upload.log

# committed = the remote GGUF's LFS sha256 equals the LOCAL file's sha256. A size-only check
# false-passed on 2026-07-10: the stale v1 file satisfied it and the v3 retrain never uploaded.
committed() {
  python3 - "$REPO" <<'PY' 2>/dev/null
import hashlib,os,sys
from huggingface_hub import HfApi
h=hashlib.sha256()
with open("submission/model/alamz-tech-sme-copilot-Q4_K_M.gguf","rb") as f:
    for chunk in iter(lambda: f.read(1<<22), b""):
        h.update(chunk)
local=h.hexdigest()
i=HfApi().repo_info(sys.argv[1],repo_type="model",files_metadata=True,token=os.environ["HF_TOKEN"])
sys.exit(0 if any(s.rfilename.endswith(".gguf") and s.lfs and s.lfs.sha256==local for s in i.siblings) else 1)
PY
}

attempt=0
until committed; do
  attempt=$((attempt+1))
  echo "=== [$(date +%H:%M:%S)] upload attempt $attempt ===" >> "$LOG"
  python3 - "$REPO" >> "$LOG" 2>&1 <<'PY' &
import os,sys
from huggingface_hub import HfApi
HfApi().upload_file(path_or_fileobj="submission/model/alamz-tech-sme-copilot-Q4_K_M.gguf",
  path_in_repo="alamz-tech-sme-copilot-Q4_K_M.gguf",repo_id=sys.argv[1],repo_type="model",
  token=os.environ["HF_TOKEN"])
print("UPLOADED_OK",flush=True)
PY
  UP=$!
  # watchdog: kill if %-progress stalls
  last=""; stall=0
  while kill -0 "$UP" 2>/dev/null; do
    cur=$(grep -aoE "[0-9]+%" "$LOG" 2>/dev/null | tail -1)
    if [ "$cur" = "$last" ]; then stall=$((stall+5)); else stall=0; last="$cur"; fi
    if [ "$stall" -ge "$STALL_S" ]; then echo "  [watchdog] stalled ${STALL_S}s at $cur — restarting" >> "$LOG"; kill -9 "$UP" 2>/dev/null; break; fi
    sleep 5
  done
  wait "$UP" 2>/dev/null
  committed && break
  sleep 5
done
echo "=== [$(date +%H:%M:%S)] GGUF CONFIRMED ON HF ===" >> "$LOG"
