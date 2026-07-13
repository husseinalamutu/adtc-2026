# 3B vs 1.5B under the scalar audit — measured tradeoff (2026-07-13)

## Why this experiment ran
Dell (i7-1185G7, audit-exact SIMD-OFF scalar build) measured the shipped 3B at **2.75 tok/s**
(`-t 4`; ~2.0 auto-threads). Confirmed against the LIVE official adtc-profiler repo:
scalar flags verbatim, `LLAMACPP_REF=master` (unpinned), TPS via `llama-bench -p 512 -n 128`
auto-threads, scoring `S_perf = min(TPS/15,1)×100` — **proportional, no DQ**. So the 3B takes
~5.5 of 30 speed points; REPORT.md's "3B clears the 15-TPS floor" premise is falsified.
A 1.5B projects ~5.5 tok/s (scalar is compute-bound → tok/s ~ 1/params) → ~11/30 pts (+5.5).
Break-even: shrink wins iff it costs < ~11 accuracy points (0.5 weight): ΔS_perf > 1.67·|ΔS_acc|.

## Setup
Qwen2.5-1.5B-Instruct-4bit, same recipe as the shipped 3B (mlx_lora_config.1p5b.yaml: same
data incl. all Nigeria drill top-ups, same LoRA targets/rank/LR, 28 layers, 1200 iters,
val 2.23→~0.40 band, best 0.351). Same GGUF chain (build_1p5b_gguf.sh): fuse → f16 →
imatrix-on-Q8_0 → Q4_K_M → **986 MB** (3B: 1.93 GB).

## Results
| Axis | 3B (shipped v3) | 1.5B candidate |
|---|---|---|
| fact_eval (37Q, greedy) | 34/37, gate 22/23 | **35/37, gate 22/23** |
| VAT quote arithmetic | ✅ exact | ✅ exact |
| Single-invoice reconciliation | ✅ | ✅ |
| **p1-class multi-invoice exact-clear** | ✅ "no outstanding balance" | ❌ self-contradictory: "clears both … NGN 42,500 still outstanding" |
| Partial-payment carry (100k vs 85k+42.5k) | ⚠️ right procedure (carries 15k) but wrong final call ("NGN 0") | ❌ no carry at all ("42,500 remains") |
| Scalar tok/s (Dell, projected) | 2.75 measured | ~5.5 (not benchmarked — moot) |

## Verdict — KEEP THE 3B
Fact recall survived the shrink (35/37 — drill-heavy data was sufficient at 1.5B; it even
passes the ₦120M applied-threshold question v3 misses). **Multi-step reconciliation
arithmetic did not.** The 1.5B fails the exact class of metadata.json's declared `p1`
test prompt — a guaranteed-scored item — and multi-invoice arithmetic is the backbone of
the 50%-weight accuracy score. +5.5 speed points cannot buy that back. Dell benchmark of
the 1.5B skipped as moot.

## Follow-ups
1. **Both** models fumble the partial-payment carry conclusion (3B does the procedure right,
   wrong final line). templated_gen.py has reconciliation but this shape is under-drilled →
   add partial-payment/carry variants to the templated layer if another training pass happens.
2. REPORT.md speed section must be rewritten: the 15-TPS floor is unreachable for ANY capable
   model under the scalar audit build; frame 3B's 2.75 tok/s + proportional scoring + the
   accuracy-first rationale explicitly. Raise the scalar-flags + unpinned-ref question with
   the organizers (evidence: official Dockerfile fetched 2026-07-12).
3. Artifacts kept for the record: `gguf_1p5b/model-Q4_K_M.gguf`, `adapters_1p5b/`,
   `results/fact_eval_1p5b.md`. Safe to delete for disk space once REPORT is updated.
