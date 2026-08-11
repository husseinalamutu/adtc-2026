# Session handoff — live state & how to continue

Last updated: 2026-08-11. **Shipped model = v3** (Qwen2.5-3B QLoRA → imatrix Q4_K_M, 1.93 GB,
on HF, sha256-verified). The retrain programme is **CLOSED**: v5, v5b and v5c were all
rejected by the gates. The product around the model grew substantially: a six-layer offline
financial intelligence engine, a demo app, and Hausa + Igbo output.

Read this + `STRATEGY.md` + `build/results/*.md` first. History lives in the results docs.

## Project one-liner
ADTC-2026 entry: offline **financial intelligence engine** for African SMEs. Qwen2.5-3B QLoRA
→ imatrix Q4_K_M GGUF (~1.93 GB), domain `corporate_enterprise`.
Repo: https://github.com/husseinalamutu/adtc-2026
Model: https://huggingface.co/HusseinAlamutu/alamz-tech-sme-copilot-gguf

## Scoring status
- **Accuracy (50%)**: v3 = **34/37 facts, 9/12 arithmetic, 5/5 narration** on the three gates.
- **Efficiency (20%)**: peak RSS ~2.0 GB → S_eff ≈ 71/100.
- **Speed (30%)**: **2.75 tok/s** (i7-1185G7, audit-exact scalar build). NO floor —
  `S_perf = 100·TPS/TPS_max`, relative to the field. Leaderboard is still empty (re-check it).
- Hidden prompts are **3**, not 2 (verified 2026-07-20) → 3 of 5 scored prompts are hidden.

## THE THREE GATES — run these before shipping anything
```
python3 build/fact_eval.py       # 37 Nigeria questions   (v3: 34/37)
python3 build/arith_eval.py      # 12 arithmetic cases    (v3:  9/12)
python3 build/narration_eval.py  #  5 fidelity checks     (v3:  5/5)
python3 build/eval_checkpoints.py --checkpoints 1400 1100 900   # all three, per checkpoint
```
Ship rule: **facts ≥ 34 AND arithmetic > 9.** Nothing ships on validation loss — see below.

## The most important lesson of this project
**Validation loss does not track what is scored.** Twice now a model with better val loss had
worse facts: v4 (val-selected, 34→31) and v5 (best val of any run, 0.314, facts 34→26).
Both were caught only because the gates existed and were fixed in advance.

**Check the DATA before re-running the model.** v5's fact collapse (34→26) was diagnosed as
"exposure dilution", which was **wrong** and cost a full retrain. The real cause: adding new
scenario families silently moved three Nigeria drill families wholesale into holdout, so
those facts had zero training data. A share effect degrades broadly; ours was surgical
(3 topics, 6 of 8 lost questions) — the disproof was visible before the wasted run.

Retrain results, all gated out:
| run | facts | arith | narration | note |
|---|---|---|---|---|
| **v3 (shipped)** | **34** | 9 | 5 | incumbent |
| v5 / v5b | 26 / 27 | 10 / 11 | 5 | drill data missing (the bug) |
| v5c @1200 | 33 | 10 | 5 | best challenger — missed by one fact |
| v5c @1000 / @1400 | 27 / 32 | 9 / 10 | 5 / 3 | under- and over-trained |

~1200 iters is this recipe's optimum; past it the *fragile* skills go first (narration
5/5 → 3/5). **Do not retrain again without a new idea** — the ceiling is measured.
Full account: `build/results/retrain_conclusion_2026-08-11.md` and `v5_split_bug_2026-08-11.md`.

## What exists now (beyond the model)
- `demo/finance/` — deterministic engine, **71 tests**, stdlib only: `store` (SQLite, Decimal
  money), `ledger` (double-entry, carry allocation), `analytics` (P&L/margin/aging/health),
  `inventory` (weighted-average COGS, turnover, cash-conversion cycle, dead stock),
  `anomalies` (robust z-score, duplicates, price jumps — 371 txns → 6 flagged), `advisor`
  (ranked interventions), `tax_rules` (citeable, from the same verified fact base), `i18n`.
- `demo/app/` — offline app: Ask-my-business (health / anomalies / forecast / stock / actions),
  reconcile, tax, quote, CSV import. Engine computes, model narrates. `bash demo/app/run_demo.sh`
- `i18n.py` — **Hausa + Igbo are native-reviewed and LIVE** (`available()` → `['en','ha','ig']`);
  Yoruba is drafted but gated and NOT claimed. Reviewers changed 11/14 (ha) and 10/14 (ig)
  strings; both independently fixed the same profit/balance conflation on the Net line.
  Igbo vocabulary cross-checked against a published glossary (`demo/finance/sources/`,
  IGBOSCHOLARS 2013). Figures are identical across languages by construction (tested).
  **These languages live in the APP, not the model** — `metadata.json` stays
  `language_scope: ["en"]` so hidden prompts are not invited in a language the GGUF can't serve.
- Data: 5,216 examples, **3 of 5 generators fully deterministic**; 139 data tests incl. a
  **contamination guard** (3 eval questions were found verbatim in training and rephrased).

## Gotchas (don't rediscover these)
- Fine-tune on the **4-bit** base, never bf16. Peak ~3.9 GB, fits 8 GB.
- imatrix on a **Q8_0 copy w/ GPU** — f16-on-CPU is 2.5 hrs vs 4 min.
- **macOS IOGPU kernel panic** (FB22091885): always train via `build/train_launcher.py`
  (Metal caps). Never run heavy GPU work concurrently with training.
- `resume_training.sh` archives numbered checkpoints to `adapters_best/` before clearing —
  losing them once cost us the v3 adapter.
- Eval intermediates peak ~11.6 GB; `eval_checkpoints.py` stages its cleanup for that reason.
- HF transfers wedge on this network → the watchdogs verify by **sha256**, not size.
- Commits: **no `Co-Authored-By: Claude` trailer**.

## Remaining Gate-1 deliverables (due Aug 25, 2026)
- [x] metadata.json (team_id, github_handle), artifact rebranded, HF model card live
- [x] Load-bearing pairing built and true; demo app; REPORT architecture current
- [x] **Retrain programme CLOSED** — v3 confirmed as the submission model. v5/v5b/v5c all
      failed the gate; best challenger (v5c@1200: 33 facts, 10 arith) missed by one fact.
      See `build/results/retrain_conclusion_2026-08-11.md`. Do not retrain again without a
      new idea — this recipe's ceiling is measured, not assumed.
- [x] Native **Hausa + Igbo** reviews complete and applied; both languages live in the app
- [ ] Send `infra/organizer_questions_draft.md`
- [ ] 2-min video (script + Q&A prep are LOCAL only, gitignored)
- [ ] Freeze: pin the submission commit; clean-clone `download_model.sh` + profiler check
