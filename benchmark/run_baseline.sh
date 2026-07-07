#!/usr/bin/env bash
# Baseline candidate GGUFs on target-class HW: generation TPS + peak RSS.
# The output table LOCKS our model size (biggest base that clears ~16 TPS at <3.5 GB).
# Run on the provisioned VM: bash run_baseline.sh
set -euo pipefail

LLAMA_DIR="${LLAMA_DIR:-$HOME/adtc/llama.cpp}"
BENCH="$LLAMA_DIR/build/bin/llama-bench"
CLI="$LLAMA_DIR/build/bin/llama-cli"
THREADS="${THREADS:-4}"        # match the 4-vCPU audit profile
CTX="${CTX:-2048}"             # small context => lower RSS (tune per domain later)
GEN_TOKENS="${GEN_TOKENS:-128}"
mkdir -p model results

# --- Candidates. VERIFY each URL points at a current Q4_K_M GGUF before trusting results. ---
# Format: "label|hf_gguf_url"   (leave the strongest multilingual 3-4B bases here)
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

for entry in "${MODELS[@]}"; do
  label="${entry%%|*}"; url="${entry##*|}"; path="model/${label}.gguf"
  [ -f "$path" ] || { echo ">> downloading $label ..." >&2; curl -fL --retry 3 -o "$path" "$url" || { echo "  download FAILED for $label — check URL" >&2; continue; }; }

  # Generation throughput (tg128) via llama-bench, CPU, 4 threads.
  tps=$("$BENCH" -m "$path" -t "$THREADS" -p 0 -n "$GEN_TOKENS" -o csv 2>/dev/null \
        | awk -F',' 'NR>1 && $0 ~ /tg/ {gsub(/"/,"",$NF); v=$NF} END{printf "%.1f", v+0}')

  # Peak RSS via /usr/bin/time on a real generation run.
  rss_kb=$({ /usr/bin/time -v "$CLI" -m "$path" -t "$THREADS" -c "$CTX" -n "$GEN_TOKENS" \
             -p "Summarize the cash position of a small shop." --no-warmup >/dev/null; } 2>&1 \
             | awk '/Maximum resident set size/ {print $NF}')
  rss_gb=$(awk "BEGIN{printf \"%.2f\", ${rss_kb:-0}/1024/1024}")

  verdict="OK"
  awk "BEGIN{exit !(${tps:-0} < 16)}"    && verdict="SLOW(<16)"
  awk "BEGIN{exit !(${rss_gb:-0} > 3.5)}" && verdict="${verdict}/HEAVY"
  printf "%-24s %-10s %-12s %-10s\n" "$label" "$tps" "$rss_gb" "$verdict"

  [ $first -eq 1 ] || echo "," >> "$RESULT_JSON"; first=0
  printf '  {"model":"%s","tps_generation":%s,"peak_rss_gb":%s}' "$label" "${tps:-0}" "${rss_gb:-0}" >> "$RESULT_JSON"
done
echo "" >> "$RESULT_JSON"; echo "]" >> "$RESULT_JSON"
echo; echo "Saved -> $RESULT_JSON  (commit it)"
echo "Rule: pick the LARGEST base with TPS_gen >= ~18 (audit margin) and peakRSS <= 3.5 GB."
