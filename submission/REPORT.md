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

**Base model — Qwen2.5-3B-Instruct (4-bit).** Speed is scored *relative to the fastest submission*
(`S_perf = 100·TPS_act/TPS_max`), and the audit runs a deliberately SIMD-disabled (scalar) llama.cpp
build that slows every submission alike — measured at **2.75 tok/s** for our 3B on an audit-class
i7-1185G7 (4 CPUs / 7.5 GB, audit-exact flags). We made the size decision **empirically**: we
trained a 1.5B on identical data and it *matched the 3B on domain-fact recall (35/37 vs 34/37)*
but **failed multi-invoice reconciliation arithmetic — including the class of our own declared
test prompt p1** — for only ~2× speed. Since accuracy is 50% of the score (and judged partly
qualitatively), we kept the 3B and accept the relative speed cost. We likewise rejected 7–8B
(~2× slower still, and it risks the 7 GB OOM line). Qwen2.5-3B specifically: strong multilingual/general reasoning and a large
GGUF/quant ecosystem. (Its licence is *not* permissive — see §1b.) We fine-tune from the **pre-quantized 4-bit build**
(`mlx-community/Qwen2.5-3B-Instruct-4bit`) — this is true QLoRA and is what makes a full-quality
fine-tune fit in 8 GB (see §4).

**Fine-tune, don't rely on RAG for the score.** The sandbox scores the **bare model** on our 2 test
prompts + 3 hidden in-domain prompts — no retrieval pipeline runs. So domain accuracy has to live
**in the weights**. We fine-tuned rather than leaning on a retrieval trick the audit can't execute.
(A document-upload RAG feature *does* exist — but purely in the human-facing demo, for grounding
other countries' tax law; it is never the thing standing between the bare model and a correct
answer. See §5.)

**Quantization — Q4_K_M with an importance matrix (imatrix).** Q4_K_M is the community sweet spot
(~90–95% of fp quality at ¼ the memory). We compute a **domain-representative imatrix** from our own
training corpus, which recovers most of the accuracy 4-bit would otherwise cost — near-free accuracy
points. We rejected plain Q4 (leaves accuracy on the table) and Q5+/Q8 (pushes RSS up for gains we
don't need given the strong efficiency margin).

**Cross-disciplinary pairing (load-bearing): LLM + offline financial intelligence engine.**
The model supplies natural-language reach; a **deterministic engine** (`demo/finance/`, stdlib
only, 71 unit tests) supplies every figure. The split is not cosmetic — we *measured* where a
3B model fails at money arithmetic and built the engine precisely there. Six layers, each
computing rather than generating:

| Layer | Discipline | What it computes |
|---|---|---|
| `store` + `momo_parser` | data engineering | SQLite spine; mobile-money statement text → structured transactions; exact `Decimal` money |
| `ledger` | accounting | double-entry postings; exact-match reconciliation and lump-sum allocation **with carry** |
| `analytics` | financial analysis | P&L, gross margin, cash position, receivables aging, month-over-month health |
| `inventory` | working-capital accounting | weighted-average valuation, **true COGS**, turnover/DIO, cash conversion cycle, trapped capital |
| `anomalies` | applied statistics | robust z-score (median/MAD) per category, duplicate payments, per-line-item price jumps — 371 transactions → a 6-row shortlist |
| `advisor` | operations research | ranks quantified interventions by recoverable value and states honestly whether they close the projected gap |

`tax_rules` computes citeable Nigeria-2025 verdicts from the **same** grep-verified fact base the
training data was generated from — one source of truth for weights, engine and demo, so they
cannot disagree about what the law says. The model narrates; it never recomputes. Neither half
works alone: without the model the engine is a spreadsheet, without the engine the model is a
confident guess about someone's money.

**Multilingual output without model-capacity cost.** **Hausa and Igbo** are rendered from computed
figures by **native-reviewed** templates (`i18n.py`), not generated by the model — reviewers changed
11 of 14 and 10 of 14 strings respectively, and both independently corrected the same error (the AI
draft had conflated *net profit* with *remaining balance* in both languages). Figures are
byte-identical across languages by construction, hallucination is structurally impossible in the
language layer, and the model's limited capacity stays spent on English financial reasoning — which
is what the audit measures. A Yoruba catalogue exists but is unreviewed, so it is **gated in code and
not claimed**. These languages live in the application layer; `metadata.json` accordingly declares
`language_scope: ["en"]`, because the GGUF itself is English-only and we will not invite hidden
prompts in a language it cannot serve.

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

**We measure what we ship, and we gate on it.** Two harnesses run against the quantized GGUF at
greedy decoding: `fact_eval.py` (37 adversarially-phrased Nigeria questions, including casual and
Pidgin framings) and `arith_eval.py` (12 arithmetic cases). Building the arithmetic gate
immediately exposed three defects that hand-checking had missed for weeks — a multi-item VAT
error, a multiplication error, and margin confused with markup. **Eval questions are never
reproduced in training data**; the drills randomise their numbers and phrasings, because training
on the gate would destroy the gate.

The Nigeria fact base is the depth play. Every figure is tagged `primary_confirmed` (found verbatim
in the OCR'd official Gazette / clean-text Administration Act — e.g. the 0%/30% CIT split, the 4%
Development Levy) or `secondary_corroborated` (agreed by ≥2 reputable firms — EY, KPMG, Baker Tilly —
pending primary grep). The generator is **forbidden from stating any number not in that file**, hedges
language by confidence tag, and always closes with "confirm with FIRS / an accountant" — responsible
advisory practice, not evasion.

**Overfit guard for the hidden prompts.** We split train/holdout **by scenario family**, not by row:
whole business-type/topic/country *combinations* are held out, so the holdout set contains scenario
*shapes* the model never trained on — the closest proxy we can build for the organizers' 3 hidden
in-domain prompts. Our 2 declared `test_prompts` are representative, not cherry-picked.

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
| **Speed (30%)** — generation TPS | **2.75 tok/s** (i7-1185G7, audit-exact scalar build, `-t 4`; ~2.0 at llama-bench auto-threads) | `S_perf = 100·TPS/TPS_max` — relative to the field; see note |
| Thermal | no throttle | −0 penalty |
| Integrity | `params_match: true`, arch `qwen2` recognized | passes fraud check |

> **Speed measurement note.** TPS must be measured on x86 (the audit architecture); an Apple-Silicon
> host cannot produce a representative number. We benchmarked on an **Intel i7-1185G7 (11th-gen,
> 4-core Tiger Lake U, integrated Iris Xe)** — squarely in the audit's i5/Ryzen-5 class — using
> llama.cpp built with the audit's exact SIMD-disabled flags (verified verbatim against the official
> adtc-profiler Dockerfile), pinned to 4 CPUs / 7.5 GB: **2.75 tok/s** (`llama-bench`-comparable;
> throttled=false). Context for the judges: with every SIMD path off (`GGML_AVX/AVX2/FMA/F16C=OFF`),
> generation is compute-bound scalar math, ~8–10× below the same chip's AVX2 numbers — this affects
> all submissions equally under the relative formula `S_perf = 100·TPS/TPS_max`. We validated the
> size trade empirically (a 1.5B doubled speed but failed declared-prompt reconciliation arithmetic;
> see build/results/model_size_tradeoff_2026-07-13.md) and chose accuracy.

## 6. Summary

A domain-fine-tuned, imatrix-quantized **Q4_K_M GGUF of Qwen2.5-3B**, trained entirely on a budget
laptop, with **structurally African** capability (mobile-money reconciliation + Nigeria-2025 tax
depth), a **load-bearing** finance-engine integration, a **~2 GB** memory footprint, and validated
domain accuracy — packaged for reproducible, fully-offline evaluation.
