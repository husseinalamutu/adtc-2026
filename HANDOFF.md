# Session handoff — live state & how to continue

Last updated: 2026-07-13 — **model LOCKED & SHIPPED**. Qwen2.5-3B v3 GGUF: fact eval 34/37
(gate 22/23, all 5 canonical Nigeria facts pass), arithmetic clean, sha256-verified on HF.
Speed measured on audit-class x86: **2.75 tok/s** under the audit's scalar build — final, by
design (see below). Any new/resumed Claude session: read this + `STRATEGY.md` +
`build/results/*.md` first. History lives in the results docs, not here.

## Project one-liner
ADTC-2026 entry: offline back-office copilot for African SMEs. A Qwen2.5-3B QLoRA → imatrix
Q4_K_M GGUF (~1.93 GB), domain = `corporate_enterprise`, African use case = mobile-money
reconciliation + Nigeria-2025 tax. Repo: https://github.com/husseinalamutu/adtc-2026
Model: https://huggingface.co/HusseinAlamutu/adtc-sme-copilot-gguf

## Scoring status (all axes settled)
- **Accuracy (50%)**: arithmetic/reconciliation excellent; Nigeria facts 34/37 on
  `build/fact_eval.py` (v1 was 24/37). Judged partly qualitatively — coherence counts.
  Further gains → the demo's retrieval/fact-pack layer, NOT more weight drilling
  (v4 regression + 1.5B experiment both proved the weights are at their sweet spot).
- **Efficiency (20%)**: peak RSS ~2.0 GB → S_eff ≈ 72/100. DONE.
- **Speed (30%)**: 2.75 tok/s (i7-1185G7, audit-exact scalar flags). NO floor — scored
  `S_perf = 100·TPS/TPS_max` relative to the field (website supersedes profiler README).
  Size re-validated empirically: 1.5B doubled speed but failed declared-prompt arithmetic
  (`build/results/model_size_tradeoff_2026-07-13.md`). Decision: accuracy > speed. CLOSED.

## Verification tooling (use these, not ad-hoc prompts)
- `build/fact_eval.py` — 37-question Nigeria fact eval, greedy, regex-scored; `--gate-only`
  for the 23 shipping-gate questions. The ship bar: all 5 canonical facts + no wrong numbers.
- `build/build_final.sh` — full 3B GGUF chain; `benchmark/telemetry_test.py` — RSS/thermal check.
- Known model limits (documented, acceptable): def-4-style applied-threshold conclusions,
  partial-payment carry final line, old CGT rate on individuals (cgt-3-class).

## Gotchas learned (don't rediscover these)
- Fine-tune on the **4-bit** base (`build/models/Qwen2.5-3B-Instruct-4bit`), never bf16 — see
  `build/mlx_lora_config.yaml` header. Peak ~3.9 GB, fits 8 GB.
- imatrix: compute on a **Q8_0 copy w/ GPU** (`04_imatrix_quantize.sh` does this) — f16-on-CPU is 2.5 hrs.
- Data gen: free-tier is tight. Groq (`GENERATION_PROVIDER=groq`) round-robins 8b+70b; Gemini is
  the fallback. Both reset daily. Keys in `data/.env` (git-ignored).
- HF transfers (both directions) wedge on dead sockets on this network — use
  `hf_upload_watchdog.sh` (verifies by sha256, not size) / `build/download_base_1p5b.sh`-style
  stall watchdogs; never trust a bare long transfer.
- Background jobs die at session teardown but `nohup`+resumable scripts survive; re-run to continue.
- **macOS IOGPU kernel panic** (FB22091885): sustained MLX Metal load can panic the whole Mac
  ("completeMemory() prepare count underflow"); it killed a training run 2026-07-10. Workaround:
  always train via `build/train_launcher.py` (caps Metal memory 5GB / cache 1GB / wired 3.5GB) —
  `resume_training.sh` already does. Don't launch `mlx_lm.lora` bare.
- `resume_training.sh` deletes numbered checkpoints on resume — copy anything you might want
  into `adapters_best/` BEFORE resuming (this cost us the v3 adapter; the GGUF survives).
- Commits: **no `Co-Authored-By: Claude` trailer** (user preference).

## Remaining Gate-1 deliverables (due Aug 25, 2026)
- [ ] `submission/metadata.json`: fill `team_id` + `github_handle` (user's Devpost/GitHub) —
      submission validation will fail on the TODOs.
- [x] Load-bearing pairing: **BUILT** (`demo/finance/` — MoMo parser + double-entry ledger with
      lump-sum/carry allocation + citeable TaxRules from the verified facts file; 13 tests, the
      eval cases the models got wrong included). metadata.json's claim is now true. Next: wire
      it into the demo app UI beside the model (Best Integration Award target).
- [ ] Send `infra/organizer_questions_draft.md` (scalar build intentional? llama.cpp pin?
      which speed formula governs?) — user reviews and sends.
- [ ] 2-min video + demo app for the live defense (llama-server UI is the zero-code fallback).
- [ ] Freeze: pin repo to submission commit; verify clean-clone `download_model.sh` +
      `docker/run_local_emulation.sh` pass end-to-end.
