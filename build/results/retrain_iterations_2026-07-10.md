# Nigeria retrain iterations 2-3 — 2026-07-10 (afternoon)

Continues finetune_2026-07-10.md (v2 = global-400, gate 2/5 on the manual check). Ship gate
upgraded from HANDOFF's 5 questions to `build/fact_eval.py`: 37 regex-scored questions
(23 = gate topics), greedy decoding, paraphrase/adversarial/casual framings.

## Iteration 2 — targeted drills + drill-heavy continuation (v3) ✅ SHIPPED
- Data: +197 gate-fact drills (`nigeria_tax_gate.jsonl`, small-company + development-levy
  topics via the new `--topics` generator flag) and +98 weak-topic drills
  (`nigeria_tax_weak.jsonl`: WHT, PIT, filing/penalties — filing had ZERO drills before).
  Dataset: 3,597 train / 446 holdout; MLX prep `--oversample-factor 3` → 4,904 rows,
  ~45% Nigeria exposure.
- Train: resumed global-400 adapter → 1,200 (interrupted once by the **IOGPU kernel panic**,
  see train_launcher.py + HANDOFF gotcha; resumed from global-500 with Metal caps, peak 4.17 GB).
  Val noisy-stable 0.35-0.5 (high variance expected: 15 val batches over a short-drill/long-trace mix).
- **v3 eval (global-1200 GGUF): 34/37, gate 22/23** (v2 baseline: 24/37). Dev levy 1/4→4/4,
  smallco definition 1/4→3/4, filing 0/2→2/2, PIT 1/3→3/3. Arithmetic smoke intact
  (10×8,500 + 7.5% VAT = 91,375 ✓). Only gate miss: def-4 states correct thresholds but
  won't conclude "₦120M > ₦100M ⇒ not small". No wrong number stated anywhere in gate topics.

## Iteration 3 — +200-iter continuation for the last 3 gaps (v4) ❌ REGRESSED, discarded
- Data: +73 drills (applied-threshold comparisons, WHT deemed-distribution 10%, non-resident
  source basis) → 3,670 train; config iters 1200→1400; continuation global 1200→1400.
- **v4 eval (global-1400 GGUF): 31/37, gate 20/23.** def-3 flipped to asserting the OLD ₦25M
  threshold, prof-4 flipped to granting a consultancy 0%, cgt-3 dropped; def-4 still unconcluded.
- Lesson: at 3B/Q4 the marginal facts sit on a knife's edge — additional continued training
  reshuffles which facts hold rather than adding monotonically. v3 ≈ the capacity/stability
  optimum for this recipe. Further gains should come from the retrieval/fact-pack layer
  (product architecture), not more parametric drilling.

## Ship decision
Shipped artifact = **v3 GGUF** (preserved before the v4 rebuild as
`adapters_best/model-Q4_K_M-v3-gate22of23.gguf`, restored to `gguf/model-Q4_K_M.gguf`;
re-verified gate-only on the restored file). The v3 *adapter* (global-1200) was consumed by
the iter-3 resume (numbered checkpoints are deleted on resume) — the GGUF is the artifact of
record. v4's adapter remains in `adapters/` (global-1400) but is not shipped.

## HANDOFF 5-question fact check — before/after
| Fact | v1 (shipped before) | v3 (shipping now) |
|---|---|---|
| VAT rate | ❌ 5.5% | ✅ 7.5% |
| Small-co CIT (≤₦100M/≤₦250M) | ❌ 15% | ✅ 0% (exempt) |
| Standard CIT | ✅ 30% | ✅ 30% |
| Development Levy | ❌ 2% | ✅ 4%, small cos exempt |
| Consulting ₦60M (prof-services exclusion) | ❌ "meets criteria" | ✅ excluded → 30% |
