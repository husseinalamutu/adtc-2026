#!/usr/bin/env bash
# One-command demo: llama-server (narrative) + the app (figures + UI).
# Fully offline. The app also works without llama-server (figures only).
set -uo pipefail
cd "$(dirname "$0")/../.."   # repo root

MODEL="submission/model/adtc-sme-copilot-Q4_K_M.gguf"
LLAMA_SERVER="$HOME/adtc-local/llama.cpp/build/bin/llama-server"

if ! curl -s -o /dev/null http://127.0.0.1:8080/health 2>/dev/null; then
  if [ -x "$LLAMA_SERVER" ] && [ -f "$MODEL" ]; then
    echo "==> starting llama-server (:8080) with $MODEL"
    nohup "$LLAMA_SERVER" -m "$MODEL" --port 8080 -c 2048 -t 4 > demo/app/llama_server.log 2>&1 &
    disown
  else
    echo "!! llama-server or model missing — running app in figures-only mode"
  fi
fi

echo "==> app: http://127.0.0.1:8090"
exec python3 demo/app/server.py
