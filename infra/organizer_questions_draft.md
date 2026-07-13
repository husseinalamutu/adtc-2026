# Draft — clarifying questions for ADTC organizers (NOT SENT; review before sending)

To: (ADTC 2026 organizers contact)
Subject: ADTC 2026 — three technical clarifications on the audit build & speed scoring

Hi ADTC team,

I'm preparing a Gate-1 submission (domain: corporate_enterprise) and have three questions
after benchmarking against the public `adtc-profiler` repo. Asking early so every team can
plan against the same assumptions.

**1. Is the SIMD-disabled llama.cpp build intentional for the audit?**
The official `adtc-profiler` Dockerfile builds llama.cpp with `GGML_NATIVE=OFF, GGML_AVX=OFF,
GGML_AVX2=OFF, GGML_AVX512=OFF, GGML_FMA=OFF, GGML_F16C=OFF, GGML_BLAS=OFF`. On an
audit-class 4-core laptop (i7-1185G7, 4 CPUs / 7.5 GB container) this scalar build measures a
3B Q4_K_M at ~2.75 tok/s — roughly 8–10× below the same chip/model with standard AVX2 kernels
(which every real deployment would use). If intentional, no objection — it hits all teams
equally under the relative formula — but it would help to know it's deliberate rather than an
artifact, since it materially changes model-size strategy.

**2. Will the audit pin the llama.cpp version?**
The Dockerfile clones `llama.cpp` at `master` (`ARG LLAMACPP_REF=master`, unpinned). A rebuild
on audit day can produce different kernels/behavior than what participants benchmarked against.
Could the audit image pin a specific llama.cpp release or commit, announced in advance?

**3. Which speed formula governs?**
The challenge website (africadeeptech.org/challenge-2026) states
`S_perf = 100 × (TPS_act ÷ TPS_max)` (relative to the fastest submission), while the
`adtc-profiler` README states `min(TPS / 15, 1.0) × 100` with `TPS_REFERENCE = 15.0`
(absolute, capped). These give very different optimization incentives. I assume the website
governs — could you confirm, and if so update the README to match?

Thanks for the great challenge — the offline-first constraint is exactly right for our market.

(name / team id)

---
Evidence gathered 2026-07-12/13 from:
- https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler (Dockerfile, README, src/)
- https://africadeeptech.org/challenge-2026/
- Measured: i7-1185G7, Docker 4 CPUs/7.5 GB, audit-exact flags → 3B Q4_K_M 2.75 tok/s (-t 4).
