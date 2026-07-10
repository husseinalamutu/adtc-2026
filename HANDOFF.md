# Session handoff — live state & how to continue

Last updated: 2026-07-10 — **Nigeria-accuracy retrain COMPLETE & SHIPPED** (v3, gate 22/23,
HANDOFF 5/5, verified on HF by sha256). Full story: `build/results/retrain_iterations_2026-07-10.md`.
The 7-step arc below is DONE; remaining work is the Gate-1 deliverables at the bottom.
Any new/resumed Claude session: read this + `STRATEGY.md` + `build/results/*.md` first.

## Project one-liner
ADTC-2026 entry: offline back-office copilot for African SMEs. A Qwen2.5-3B QLoRA → imatrix
Q4_K_M GGUF (~1.93 GB), domain = `corporate_enterprise`, African use case = mobile-money
reconciliation + Nigeria-2025 tax. Repo: https://github.com/husseinalamutu/adtc-2026

## Scoring status (what's locked)
- **Accuracy (50%)**: arithmetic/reconciliation = excellent (re-verified post-retrain).
  Nigeria tax facts = **FIXED**: 34/37 on the wide eval (`build/fact_eval.py`), all 5
  canonical facts pass; v1 scored 24/37 / 1-of-5. Further gains → retrieval layer, not weights.
- **Efficiency (20%)**: peak RSS ~2.0 GB → S_eff ≈ 72/100. DONE.
- **Speed (30%)**: unmeasured. Needs the x86 Dell benchmark (see `infra/benchmark_on_windows.md`).
- v1 model is live on HF: https://huggingface.co/HusseinAlamutu/adtc-sme-copilot-gguf

## The current task: fix Nigeria numeric recall (retrain)
v1 (149 thin Nigeria examples) learned advisory *style* but reverted to the base model's WRONG
pre-2025 priors on numbers (said VAT 5.5% not 7.5%, small-co threshold ₦5M not ₦100M). Fix =
fact-drill layer (number-first repetition) + professional-services exclusion + oversampling.

### Where we are — 7-step arc, currently on step 1
1. ⏳ **RUNNING now**: regenerate Nigeria data → `data/out/nigeria_tax.jsonl`, target 500.
   - Cmd (resumable): `cd data && export GENERATION_PROVIDER=groq && set -a; source .env; set +a && python3 generators/nigeria_tax_gen.py --n 500 --out out/nigeria_tax.jsonl`
   - Log: `data/nga_regen.log`. Watch: `wc -l data/out/nigeria_tax.jsonl` (done at ~500).
2. **Rebuild dataset**: `cd data && python3 build_dataset.py --inputs out/templated.jsonl out/teacher.jsonl out/nigeria_tax.jsonl --out-dir out`
3. **Verify**: `cd data && python3 -m pytest tests/ -q`
4. **Prep MLX data with oversampling**: `cd build && source .venv/bin/activate && rm -rf adapters adapters_best mlx_data && python3 prepare_mlx_data.py --oversample-factor 2`
5. **Retrain (fresh)**: `cd build && rm -f adapters/base_offset.txt && bash resume_training.sh` (detached; re-run after any teardown until it hits target iters, OR stop early when val loss plateaus ~0.4 AND facts test clean). Monitor `build/train_real.log`.
6. **Rebuild GGUF + re-test facts**: `cd build && rm -rf fused_model gguf imatrix.dat && bash build_final.sh` then run the FACT CHECK (below). ← the make-or-break verification.
7. **Re-upload to HF**: `cd .. && bash hf_upload_watchdog.sh` (flaky-network auto-resume; see note).

### FACT CHECK (step 6 — must all be right before shipping)
Run each through `~/adtc-local/llama.cpp/build/bin/llama-cli -m build/gguf/model-Q4_K_M.gguf -t 4 -c 1536 -n 130 -st -p "<Q>" --no-warmup`:
- VAT rate → **7.5%**
- small company (≤₦100M turnover, ≤₦250M assets, NOT professional services) CIT → **0%**
- standard company CIT → **30%**
- Development Levy → **4%** on assessable profits; **small companies exempt**
- consulting firm under ₦100M → **still pays 30% CIT** (professional-services exclusion — the nuance the user flagged)

## Gotchas learned (don't rediscover these)
- Fine-tune on the **4-bit** base (`build/models/Qwen2.5-3B-Instruct-4bit`), never bf16 — see
  `build/mlx_lora_config.yaml` header. Peak ~3.9 GB, fits 8 GB.
- imatrix: compute on a **Q8_0 copy w/ GPU** (`04_imatrix_quantize.sh` does this) — f16-on-CPU is 2.5 hrs.
- Data gen: free-tier is tight. Groq (`GENERATION_PROVIDER=groq`) round-robins 8b+70b; Gemini is
  the fallback. Both reset daily. Keys in `data/.env` (git-ignored).
- Large HF up/downloads stall on this network → `hf_upload_watchdog.sh` auto-resumes via Xet chunks.
- Background jobs die at session teardown but `nohup`+resumable scripts survive; re-run to continue.
- **macOS IOGPU kernel panic** (FB22091885): sustained MLX Metal load can panic the whole Mac
  ("completeMemory() prepare count underflow"); it killed a training run 2026-07-10. Workaround:
  always train via `build/train_launcher.py` (caps Metal memory 5GB / cache 1GB / wired 3.5GB) —
  `resume_training.sh` already does. Don't launch `mlx_lm.lora` bare.
- Commits: **no `Co-Authored-By: Claude` trailer** (user preference).

## Remaining Gate-1 deliverables (after the retrain)
- [ ] x86 TPS on the Dell (`infra/benchmark_on_windows.md`) → fill the slot in `submission/REPORT.md`.
- [ ] `submission/metadata.json`: fill `team_id` + `github_handle` (user's Devpost/GitHub).
- [ ] 2-min video; demo app (offline RAG/finance integration) for the live defense.
