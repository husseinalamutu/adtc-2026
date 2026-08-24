# ADTC 2026 — Offline Back-Office Copilot for Nigerian SMEs

**Domain:** `corporate_enterprise` · **Runtime:** llama.cpp · **Model:** Qwen2.5-3B QLoRA → imatrix Q4_K_M GGUF (~1.93 GB)
**African use case:** ✅ (Nigeria-deep tax + mobile-money reconciliation) · **Budget-laptop:** ✅

---

## 1. The problem, and who in Africa has it

The challenge targets the 8 GB laptop "on desks in classrooms, clinics, and corner shops." The
person actually typing at that laptop is not a subsistence farmer on a feature phone — it's a
**literate SME operator**: a shop owner, a bookkeeper, an ops person running an informal-sector
business. Cloud accounting SaaS never reached them: it costs monthly fees in scarce forex, assumes
reliable internet they don't have, and doesn't understand how their business actually runs — on
**mobile money** (M-Pesa, MTN MoMo, Airtel Money), in local currency, under local tax rules.

Our model is an **offline back-office copilot** for exactly this operator. It:
- computes **VAT, margins and multi-currency arithmetic** exactly (`Decimal`, never floats);
- **reconciles mobile-money statements** against outstanding invoices ("this NGN 45,000 MoMo
  payment settles INV-2001");
- answers **local tax & compliance** questions — grounded in the **Nigeria Tax Reform Acts 2025**
  (effective Jan 2026), plus general accounting reasoning for neighbouring markets;
- runs **100% offline** on the laptop the business already owns — the whole reason it's viable
  where cloud SaaS is not.

The African-ness is **structural, not cosmetic**: mobile-money reconciliation and Nigerian tax law
are things only this user needs. A generic "business assistant" could be anywhere; this cannot.

## 1b. Licensing (disclosed up front)

**Code: MIT. Model weights: Qwen Research Licence (non-commercial).** The submitted GGUF is a
fine-tune of Qwen2.5-3B-Instruct, which — unusually for the Qwen2.5 family — ships under
`qwen-research` rather than Apache-2.0. We identified this on 2026-08-11, corrected the model
card (it had incorrectly declared Apache-2.0), and added the required "Built with Qwen"
attribution and modification notice. See `LICENSE`.

We are raising with the organizers whether a `qwen-research` base is acceptable given the
residency/pilot track, since the licence permits non-commercial use only. Everything we built
— the deterministic finance engine, the data generators, the three evaluation harnesses — is
MIT and **base-model-agnostic**, so migrating to a permissively licensed base is a contained
change rather than a rewrite: `build/mlx_lora_config.phi.yaml` is a prepared configuration for
Phi-3.5-mini-instruct (MIT). We kept Qwen for this submission because it is the base we
measured most thoroughly (34/37 facts); the migration is planned work, not a hypothetical.

## 2. Design decisions (and the alternatives we rejected)

**Base model — Qwen2.5-3B-Instruct (4-bit).** Speed is scored *relative to the fastest
submission* (`S_perf = 100·TPS_act/TPS_max`) and the audit runs a deliberately SIMD-disabled
build that slows every entry alike, so we chose size **empirically** rather than chasing tok/s:
a 1.5B trained on identical data matched the 3B on fact recall (35/37 vs 34/37) but **failed
multi-invoice reconciliation arithmetic — including the class of our own test prompt p1** — for
~2× speed. Accuracy is 50% of the score, so we kept the 3B. We rejected 7–8B (~2× slower again,
and it risks the 7 GB OOM line). Qwen2.5-3B for its reasoning quality and mature GGUF ecosystem;
its licence is *not* permissive (see the Licensing section below). We fine-tune the
**pre-quantized 4-bit build** (`mlx-community/Qwen2.5-3B-Instruct-4bit`) — true QLoRA, and what
makes a full-quality fine-tune fit in 8 GB (Constraints, below).

**Fine-tune, don't rely on RAG.** The sandbox scores the **bare model** on 2 declared + 3 hidden
prompts; no retrieval pipeline runs. Domain accuracy therefore has to live in the weights. A
document-upload RAG feature exists in the demo for other countries' tax law, but it never stands
between the bare model and a correct answer.

**Quantization — Q4_K_M with an importance matrix.** ~90–95% of full-precision quality at a
quarter of the memory, and the imatrix — computed from our own domain corpus — recovers most of
what 4-bit would otherwise cost. Plain Q4 leaves accuracy on the table; Q5+/Q8 raise RSS for
gains our efficiency margin doesn't need.

**Cross-disciplinary pairing (load-bearing): LLM + offline financial intelligence engine.**
The model supplies natural-language reach; a **deterministic engine** (`demo/finance/`, stdlib
only, 131 tests) supplies every figure. We *measured* where a 3B fails at money arithmetic and
built the engine precisely there. Six layers, each computing rather than generating:

| Layer | Discipline | What it computes |
|---|---|---|
| `store` + `momo_parser` | data engineering | SQLite spine; mobile-money statement text → structured transactions; exact `Decimal` money |
| `ledger` | accounting | double-entry postings; exact-match reconciliation and lump-sum allocation **with carry** |
| `analytics` | financial analysis | P&L, gross margin, cash position, receivables aging, month-over-month health |
| `inventory` | working-capital accounting | weighted-average valuation, **true COGS**, turnover/DIO, cash conversion cycle, trapped capital |
| `anomalies` | applied statistics | robust z-score (median/MAD) per category, duplicate payments, per-line-item price jumps — 371 transactions → a 6-row shortlist |
| `advisor` | operations research | ranks quantified interventions by recoverable value and states honestly whether they close the projected gap |

`tax_rules` derives citeable Nigeria-2025 verdicts from the **same** grep-verified fact base
that generated the training data — one source of truth for weights, engine and demo, so they
cannot disagree about the law. The model narrates; it never recomputes. Without the model the
engine is a spreadsheet; without the engine the model is a confident guess about someone's money.

**Multilingual output without model-capacity cost.** **Hausa and Igbo** are rendered from
computed figures by **native-reviewed** templates, not generated — reviewers changed 11 of 14 and
10 of 14 strings, and both independently corrected the same error (our draft conflated *net
profit* with *remaining balance* in each language). Figures are byte-identical across languages
by construction, so a wrong number is structurally impossible, and the model's capacity stays
spent on English financial reasoning — which is what the audit measures. Yoruba is drafted but
unreviewed, so it is gated in code and **not claimed**. These languages live in the application
layer; `metadata.json` declares `language_scope: ["en"]` because the GGUF itself is English-only.

## 3. How we kept the model honest (accuracy engineering)

Accuracy is 50% of the score and is won on the *bare* model, so the **training data** is the highest
-leverage artifact. We built **5,216 examples** across five deliberately separated generators —
**3 of the 5 are fully deterministic**, so a wrong answer cannot enter the corpus at all:

| Layer | n | Ground truth |
|---|---|---|
| Templated arithmetic (invoicing, MoMo reconciliation, VAT, multi-currency) | 3,000 | **Programmatically computed** — deterministic, unit-tested. The answers are *derived*, never guessed, so we never train on wrong arithmetic. |
| Nigeria tax/compliance (CIT/VAT/WHT/CGT/PIT/Development Levy, filing, penalties, residency) | 868 | LLM teacher **grounded in a hand-curated fact base** extracted from the primary Acts; forbidden from stating any figure not in that file. |
| Arithmetic repair drills (carry, multi-item VAT, line math, margin-vs-markup) | 600 | **Deterministic**, Decimal-exact, *targeted at defects our own eval measured* — and they show the working, since small models compute far more reliably when trained to emit intermediate steps. |
| Intelligence drills (applied tax conclusions; narration of computed figures) | 500 | **Deterministic — the finance engine is the oracle.** Tax drills teach the model to *apply* a threshold rather than recite it; narration drills teach faithful restatement of engine output. |
| Advisory (Kenya/Ghana/Uganda/Tanzania VAT/WHT reasoning) | 248 | LLM teacher, **grounded** in fixed per-market rates — the model only phrases supplied facts. |

**We measure what we ship, and we gate on it.** Three harnesses run against the quantized GGUF
at greedy decoding: `fact_eval.py` (37 adversarially-phrased Nigeria questions, including casual
and Pidgin framings), `arith_eval.py` (12 arithmetic cases), and `narration_eval.py` (5 checks
that the model never invents a figure when restating engine output). Building the arithmetic gate
immediately exposed three defects hand-checking had missed for weeks — a multi-item VAT error, a
multiplication error, and margin confused with markup. **Eval questions never appear in training
data**; a contamination guard fails the build if they do.

The fact base is the depth play. Every figure is tagged `primary_confirmed` (verbatim in the OCR'd
Gazette or Administration Act — the 0%/30% CIT split, the 4% Development Levy) or
`secondary_corroborated` (agreed by ≥2 of EY, KPMG, Baker Tilly). The generator is **forbidden
from stating any number not in that file**, hedges by confidence tag, and closes with "confirm
with FIRS / an accountant".

**Overfit guard.** Train/holdout is split **by scenario family**, not by row: whole
business-type/topic/country combinations are held out, so the holdout contains scenario *shapes*
never trained on — the closest proxy for the organizers' 3 hidden prompts. Our 2 declared
`test_prompts` are representative, not cherry-picked.

## 4. Constraints, and what they forced

Everything was built and trained on an **8 GB Apple-Silicon laptop** — deliberately, to stay honest
about the "budget laptop" premise. Two constraints shaped the work:

- **Memory.** A full-precision base loads 6.2 GB of weights and starves an 8 GB machine (forcing a
  crippled 4-layer adapter). Switching to a **true 4-bit QLoRA base** freed ~4.4 GB and let us train
  the **full model** — all 36 layers, all 7 attention+MLP LoRA modules, rank 32, seq 1024 — at a
  **3.9 GB peak**. This is the single decision that made a strong local fine-tune possible.
- **Quantization on-device.** Computing the imatrix on the 6.2 GB f16 model was CPU-bound and
  projected to ~2.5 hours. Computing it on a **Q8_0 copy with GPU offload** (near-lossless, so the
  statistics are equivalent) cut it to **4 minutes** — then applied to the f16→Q4_K_M quantize.

**Reproducibility.** The base-model revision, llama.cpp commit, dataset, LoRA recipe, and quant
type are all pinned; a documented build recipe regenerates the identical GGUF, and
`download_model.sh` fetches the published weights credential-free.

## 5. Benchmarks (measured)

Profiled with the official `adtc-profiler` (participant mode):

| Metric | Result | Verdict |
|---|---|---|
| **Accuracy** — val loss on held-out families | **2.175 → 0.424** (baseline → final) | Large, clean drop on *unseen* scenario families → genuine domain learning, not memorization |
| **Efficiency (20%)** — peak RSS | **~2.0 GB** (2023 MB) | **S_eff ≈ 72/100**; enormous margin under the 7 GB DQ line, zero OOM risk |
| **Speed (30%)** — generation TPS | **2.4 tok/s** (i7-1185G7, audit-exact scalar build, avg of 2 clean runs) | `S_perf = 100·TPS/TPS_max` — relative to the field; see note |
| Thermal | no throttle | −0 penalty |
| Integrity | `params_match: true`, arch `qwen2` recognized | passes fraud check |

> **Speed measurement note.** TPS must be measured on x86 (the audit architecture); an Apple-Silicon
> host cannot produce a representative number. We benchmarked on an **Intel i7-1185G7 (11th-gen,
> 4-core Tiger Lake U, integrated Iris Xe)** — squarely in the audit's i5/Ryzen-5 class — using
> llama.cpp built with the audit's exact SIMD-disabled flags (verified verbatim against the official
> adtc-profiler Dockerfile), pinned to 4 CPUs / 7.5 GB: **2.4 tok/s** (avg of 2 clean runs, 2.31 and
> 2.42; `llama-bench`-comparable; throttled=false — though core temp itself is unavailable in any
> containerized environment, so this reflects the profiler's own best-effort flag, not a confirmed
> reading). Context for the judges: with every SIMD path off (`GGML_AVX/AVX2/FMA/F16C=OFF`),
> generation is compute-bound scalar math, ~8–10× below the same chip's AVX2 numbers — this affects
> all submissions equally under the relative formula `S_perf = 100·TPS/TPS_max`. We validated the
> size trade empirically (a 1.5B doubled speed but failed declared-prompt reconciliation arithmetic;
> see build/results/model_size_tradeoff_2026-07-13.md) and chose accuracy.

## 6. Summary

A domain-fine-tuned, imatrix-quantized **Q4_K_M GGUF of Qwen2.5-3B**, trained entirely on a budget
laptop, with **structurally African** capability (mobile-money reconciliation + Nigeria-2025 tax
depth), a **load-bearing** finance-engine integration, a **~2 GB** memory footprint, and validated
domain accuracy — packaged for reproducible, fully-offline evaluation.
