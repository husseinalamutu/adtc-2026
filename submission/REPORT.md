# ADTC 2026 — Offline Back-Office Copilot for African SMEs

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
- drafts **invoices, quotes and receipts** with correct VAT and multi-currency arithmetic;
- **reconciles mobile-money statements** against outstanding invoices ("this NGN 45,000 MoMo
  payment settles INV-2001");
- answers **local tax & compliance** questions — grounded in the **Nigeria Tax Reform Acts 2025**
  (effective Jan 2026), plus general accounting reasoning for neighbouring markets;
- runs **100% offline** on the laptop the business already owns — the whole reason it's viable
  where cloud SaaS is not.

The African-ness is **structural, not cosmetic**: mobile-money reconciliation and Nigerian tax law
are things only this user needs. A generic "business assistant" could be anywhere; this cannot.

## 2. Design decisions (and the alternatives we rejected)

**Base model — Qwen2.5-3B-Instruct (4-bit).** The scoring floor is speed (`min(TPS/15,1)`): a model
must clear ~15 tok/s on a 4-core/8 GB integrated-GPU laptop. A 3B at Q4_K_M sits in the sweet spot —
big enough for real accuracy, small enough to clear the floor at ~2 GB RSS. We rejected 7–8B (fails
the speed floor and risks the 7 GB OOM line) and sub-2B (clears speed easily but caps accuracy,
which is 50% of the score). Qwen2.5-3B specifically: strong multilingual/general reasoning, a large
GGUF/quant ecosystem, and permissive licensing. We fine-tune from the **pre-quantized 4-bit build**
(`mlx-community/Qwen2.5-3B-Instruct-4bit`) — this is true QLoRA and is what makes a full-quality
fine-tune fit in 8 GB (see §4).

**Fine-tune, don't rely on RAG for the score.** The sandbox scores the **bare model** on our 2 test
prompts + 2 hidden in-domain prompts — no retrieval pipeline runs. So domain accuracy has to live
**in the weights**. We fine-tuned rather than leaning on a retrieval trick the audit can't execute.
(A document-upload RAG feature *does* exist — but purely in the human-facing demo, for grounding
other countries' tax law; it is never the thing standing between the bare model and a correct
answer. See §5.)

**Quantization — Q4_K_M with an importance matrix (imatrix).** Q4_K_M is the community sweet spot
(~90–95% of fp quality at ¼ the memory). We compute a **domain-representative imatrix** from our own
training corpus, which recovers most of the accuracy 4-bit would otherwise cost — near-free accuracy
points. We rejected plain Q4 (leaves accuracy on the table) and Q5+/Q8 (pushes RSS up for gains we
don't need given the strong efficiency margin).

**Cross-disciplinary pairing (load-bearing): LLM + deterministic finance engine + local
regulatory corpus.** The model gives natural-language reach; a **deterministic finance module**
(double-entry ledger + mobile-money statement parser) does the arithmetic and reconciliation the
model must not be trusted to do alone; a **local compliance corpus** (VAT/WHT/CIT rules) supplies
citeable, jurisdiction-correct answers. Neither half works alone — this is the integration the demo
and live defense are built around.

## 3. How we kept the model honest (accuracy engineering)

Accuracy is 50% of the score and is won on the *bare* model, so the **training data** is the highest
-leverage artifact. We built **3,395 examples** across three deliberately separated generators:

| Layer | n | Ground truth |
|---|---|---|
| Templated arithmetic (invoicing, MoMo reconciliation, VAT, multi-currency) | 3,000 | **Programmatically computed** — deterministic, unit-tested. The answers are *derived*, never guessed, so we never train on wrong arithmetic. |
| Advisory (Kenya/Ghana/Uganda/Tanzania VAT/WHT reasoning) | 248 | LLM teacher, **grounded** in fixed per-market rates — the model only phrases supplied facts. |
| Nigeria tax/compliance (CIT/VAT/WHT/CGT/PIT/Development Levy, filing, penalties, diaspora residency) | 149 | LLM teacher **grounded in a hand-curated fact base** extracted from the primary Acts. |

The Nigeria fact base is the depth play. Every figure is tagged `primary_confirmed` (found verbatim
in the OCR'd official Gazette / clean-text Administration Act — e.g. the 0%/30% CIT split, the 4%
Development Levy) or `secondary_corroborated` (agreed by ≥2 reputable firms — EY, KPMG, Baker Tilly —
pending primary grep). The generator is **forbidden from stating any number not in that file**, hedges
language by confidence tag, and always closes with "confirm with FIRS / an accountant" — responsible
advisory practice, not evasion.

**Overfit guard for the hidden prompts.** We split train/holdout **by scenario family**, not by row:
whole business-type/topic/country *combinations* are held out, so the holdout set contains scenario
*shapes* the model never trained on — the closest proxy we can build for the organizers' 2 hidden
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
| **Speed (30%)** — generation TPS | **[TO BE MEASURED on target-class x86 — see note]** | — |
| Thermal | no throttle | −0 penalty |
| Integrity | `params_match: true`, arch `qwen2` recognized | passes fraud check |

> **Speed measurement note.** TPS must be measured on x86 (the audit architecture); an Apple-Silicon
> host cannot produce a representative number. We benchmark on an **Intel i7-1185G7 (11th-gen, 4-core
> Tiger Lake U, integrated Iris Xe)** — squarely in the audit's i5/Ryzen-5 class — using llama.cpp
> built with the audit's exact SIMD-disabled flags, pinned to 4 CPUs / 7.5 GB. A 3B Q4_K_M on this
> class of chip is expected to clear the 15-TPS floor with margin. **[Final TPS: __ tok/s — inserted
> once measured.]**

## 6. Summary

A domain-fine-tuned, imatrix-quantized **Q4_K_M GGUF of Qwen2.5-3B**, trained entirely on a budget
laptop, with **structurally African** capability (mobile-money reconciliation + Nigeria-2025 tax
depth), a **load-bearing** finance-engine integration, a **~2 GB** memory footprint, and validated
domain accuracy — packaged for reproducible, fully-offline evaluation.
