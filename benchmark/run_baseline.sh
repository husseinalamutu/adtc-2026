#!/usr/bin/env bash
# Baseline candidate GGUFs on target-class HW using the REAL adtc-profiler package —
# not a reimplementation. Building a tiny disposable submission dir per candidate and
# shelling out to `adtc-profiler run` guarantees byte-identical measurement methodology
# to the real audit (same llama-bench invocation, same memory sampler, same JSON shape).
#
# The output table LOCKS our model size (biggest base that clears ~16-18 TPS at <3.5 GB).
# Run on the provisioned VM: bash run_baseline.sh
set -euo pipefail

THREADS="${THREADS:-4}"   # informational only — the profiler doesn't take a thread flag;
                           # llama-bench auto-detects from the container's visible CPU count.
mkdir -p model results

if ! command -v adtc-profiler >/dev/null 2>&1; then
  echo "adtc-profiler not on PATH — run infra/provision_benchmark_vm.sh first." >&2
  exit 1
fi

# --- Candidates. VERIFY each URL points at a current Q4_K_M GGUF before trusting results. ---
MODELS=(
  "gemma-3-4b-it-Q4KM|https://huggingface.co/ggml-org/gemma-3-4b-it-GGUF/resolve/main/gemma-3-4b-it-Q4_K_M.gguf"
  "qwen2.5-3b-it-Q4KM|https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf"
  "llama-3.2-3b-it-Q4KM|https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
  # add: SmolLM3-3B, a Qwen-4B, etc. Keep to 3-4 to stay fast.
)

printf "%-24s %-10s %-12s %-10s\n" "MODEL" "TPS_gen" "peakRSS_GB" "VERDICT"
printf "%-24s %-10s %-12s %-10s\n" "-----" "-------" "----------" "-------"

RESULT_JSON="results/baseline_$(date +%Y%m%d_%H%M%S).json"
echo "[" > "$RESULT_JSON"; first=1
SCRATCH=$(mktemp -d)
trap 'rm -rf "$SCRATCH"' EXIT

for entry in "${MODELS[@]}"; do
  label="${entry%%|*}"; url="${entry##*|}"; path="model/${label}.gguf"
  [ -f "$path" ] || { echo ">> downloading $label ..." >&2; curl -fL --retry 3 -o "$path" "$url" || { echo "  download FAILED for $label — check URL" >&2; continue; }; }

  # Build a disposable submission dir for this candidate: a copy of our real
  # metadata.json with only model_path swapped, symlinked to the candidate GGUF.
  SUB="$SCRATCH/$label"
  mkdir -p "$SUB/model"
  ln -sf "$(pwd)/$path" "$SUB/model/model.gguf"
  python3 - "$SUB" <<'PYEOF'
import json, sys
sub = sys.argv[1]
meta = json.load(open("metadata.json"))
meta["_runtime"]["model_path"] = "model/model.gguf"
meta["model"]["name"] = "baseline-candidate"
json.dump(meta, open(f"{sub}/metadata.json", "w"))
PYEOF
  git -C "$SUB" init -q 2>/dev/null || true

  REPORT="$SCRATCH/${label}_report.json"
  if ! adtc-profiler run --submission "$SUB" --mode participant --output "$REPORT" --skip-accuracy >/dev/null 2>"$SCRATCH/${label}.err"; then
    echo "  adtc-profiler FAILED for $label — see $SCRATCH/${label}.err" >&2
    tail -5 "$SCRATCH/${label}.err" >&2
    continue
  fi

  tps=$(python3 -c "import json; print(json.load(open('$REPORT'))['throughput']['tokens_per_second_generation'])")
  rss_mb=$(python3 -c "import json; print(json.load(open('$REPORT'))['memory']['peak_rss_mb'])")
  rss_gb=$(python3 -c "print(round($rss_mb/1024, 2))")

  verdict="OK"
  awk "BEGIN{exit !(${tps} < 16)}"    && verdict="SLOW(<16)"
  awk "BEGIN{exit !(${rss_gb} > 3.5)}" && verdict="${verdict}/HEAVY"
  printf "%-24s %-10.1f %-12s %-10s\n" "$label" "$tps" "$rss_gb" "$verdict"

  [ $first -eq 1 ] || echo "," >> "$RESULT_JSON"; first=0
  printf '  {"model":"%s","tps_generation":%s,"peak_rss_gb":%s}' "$label" "$tps" "$rss_gb" >> "$RESULT_JSON"
done
echo "" >> "$RESULT_JSON"; echo "]" >> "$RESULT_JSON"
echo; echo "Saved -> $RESULT_JSON  (commit it)"
echo "Rule: pick the LARGEST base with TPS_gen >= ~18 (audit margin) and peakRSS <= 3.5 GB."
