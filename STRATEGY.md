# ADTC 2026 — Locked Strategy

> Single source of truth for every decision. All code, metadata, and the REPORT must match this.
> Verified against the live `adtc-profiler` source + `adtc-2026-submission-template` (2026-07-07).

## The verdict (what wins)
Ship a **single Q4_K_M (imatrix) GGUF of the biggest multilingual 3–4B base that still clears ~16+ TPS**
on target-class hardware, **domain-fine-tuned** for our use case, defended with a real offline demo.
Accuracy (50%) is the race; speed saturates at 15 TPS (per profiler `min(TPS/15,1)`), so we do NOT
overspend on speed. Never OOM (7 GB = instant 0). Stay ≤ 3.5 GB peak RSS with margin.

## Locked decisions
| Decision | Choice | Why |
|---|---|---|
| Domain | `corporate_enterprise` | The person at an 8GB laptop is a literate SME operator, not a feature-phone farmer. Matches the human to the hardware. |
| Use case | **Offline back-office copilot for informal-sector African SMEs** | Invoices/quotes, **mobile-money (M-Pesa/MoMo) reconciliation**, **local VAT/tax & compliance** Q&A, multi-currency, WhatsApp-commerce order tracking. Runs offline = the real reason cloud SaaS never reached these businesses. |
| African bonus | Earn via **use case**, English-only | `african_alpha_claim: true`. African-ness is *structural* (mobile-money, local tax regimes), not cosmetic. |
| Language | English primary (hidden prompts are English) | Drop Best Localisation; put 100% into accuracy. |
| Cross-disciplinary pairing (load-bearing) | LLM + **offline finance/accounting engine + local regulatory corpus** | Model reasons; a deterministic ledger/tax module does the math and cites rules. This is the demo's spine. |
| Base model | Decide from Week-1 benchmark. Candidates: **Qwen (4B, Apache-2.0)**, **Gemma 3 4B**, 3B fallback (SmolLM3-3B / Llama-3.2-3B) | Let the 16-TPS floor pick the size. |
| Quant | **Q4_K_M with imatrix** (domain calibration set) | Community sweet spot; imatrix recovers near-free accuracy. |
| Runtime | `llama.cpp` only, GGUF | Hard requirement; anything else auto-rejected. |

## Scoring math (verified)
- `S_total = 0.50·S_acc + 0.30·S_perf + 0.20·S_eff − P_thermal`
- `S_perf = min(TPS/15, 1.0)×100`  → **≥15 TPS = full marks; faster earns nothing.** Target 18–25 for audit margin (±25%).
- `S_eff = max(0,(7−peak_rss_gb)/7)×100` → target ≤ 3.5 GB (RSS ±15% audit tolerance).
- `P_thermal = −10` if throttle or >85 °C.
- Bonuses: `budget_laptop_claim:true` (+10%, everyone), `african_alpha_claim:true` (+15%, differentiator — website says "on panel score", so treat absolute bonus math as optimistic).

## Accuracy mechanism (verified from template)
- `metadata.json` has **exactly 2** `test_prompts`. Organizers add **2 hidden** in-domain prompts. **All 4** score the model.
- Public profiler runs with `--skip-accuracy`; accuracy judged officially (LLM-audit + panel).
- ⇒ The **bare model** must be good on our domain. **Fine-tune it. Don't rely on RAG the sandbox won't run.**
- ⇒ Our 2 test prompts must be *representative, not cherry-picked* (hidden 2 punish overfitting). Keep a hold-out set.

## Hard gates (do not violate)
- Peak RSS < 7 GB (target ≤ 3.5). OOM/crash = 0.
- `runtime: "llama.cpp"`, GGUF, 100% offline during profiling.
- `.gguf` and `model/` git-ignored; weights only via `download_model.sh`.
- Repo pinned to submission commit hash; that commit must rebuild the exact GGUF we tested.

## Timeline (Gate 1 = Aug 25, 2026)
- **W0 (now):** register, fork template, stand up cloud benchmark VM, pick candidates. ← *in progress*
- **W1:** baseline-bench candidates → lock model size.
- **W2:** build fine-tune dataset (English SME back-office instructions) + hold-out.
- **W3:** fine-tune → merge → GGUF → imatrix → Q4_K_M → re-bench; telemetry regression test.
- **W4:** offline demo app (finance/tax integration).
- **W5:** REPORT.md + choose 2 test prompts + full profiler self-check from clean clone.
- **W6:** 2-min video; second-machine `compare`.
- **W7:** freeze, publish GGUF to HF, verify download_model.sh, submit early with a tag.
