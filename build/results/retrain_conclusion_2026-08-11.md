# Retrain programme — final result and conclusion (2026-08-11)

## Decision: **v3 remains the submission model.** No retrain shipped.

| Model | Facts /37 | Arithmetic /12 | Narration /5 | Sum |
|---|---|---|---|---|
| **v3 — SHIPPED** | **34** | 9 | 5 | **48** |
| v5 (drill data missing) best | 26 | 10 | 5 | 41 |
| v5b (drill data missing, 4×) best | 27 | 11 | 5 | 43 |
| v5c @1400 | 32 | 10 | 3 | 45 |
| **v5c @1200 — best challenger** | **33** | **10** | **5** | **48** |
| v5c @1000 | 27 | 9 | 5 | 41 |

Gate, fixed before any result was seen: **facts ≥ 34 AND arithmetic > 9**. The closest
challenger missed by one fact question.

## What the programme actually produced

**1. A real, reproducible arithmetic gain.** Every run scored 10–11/12 against v3's 9/12,
including the runs with broken fact data. The repair drills (deterministic ground truth,
*showing the working*, randomised numbers) fixed the multi-item VAT and margin-vs-markup
defects the eval had exposed. The technique transfers; it just cannot be banked without
giving up a fact question at this model size.

**2. A data-pipeline bug that would have gone unnoticed.** Adding new scenario families
silently moved three Nigeria drill families wholesale into holdout, deleting those facts
from training (facts 34 → 26). Fixed by pinning drill families to train and stratifying
holdout by category. Full account: `v5_split_bug_2026-08-11.md`.

**3. The training curve for this recipe.** 1000 iters under-trains (27 facts), ~1200 is the
optimum (33), 1400 over-trains and degrades the *fragile* capabilities first — narration
fell 5/5 → 3/5 between 1200 and 1400 while robust skills held. This matches v4's behaviour
and is now a documented property of the recipe rather than a surprise.

**4. Evidence that v3 sits at the recipe's ceiling.** With the data bug fixed and the mix
matched to v3's, the best checkpoint still lands one fact short while gaining one
arithmetic question. Adding ~1,100 examples of *new skills* (arithmetic repair, applied
conclusions, narration) costs roughly one marginal fact — a capacity tradeoff, not a
tuning failure.

## Why v3 rather than v5c @1200 (a genuinely close call)
Aggregate is a dead heat (48 v 48); the challenger trades one fact for one arithmetic
question. v3 was kept because:
- **Facts are the differentiator.** Nigeria-2025 recall is what no stock model has;
  arithmetic competence is comparatively common.
- **The gate was pre-committed** precisely so a marginal result could not be rationalised
  after the fact. Overriding it on a tie would defeat its purpose.
- **v3 is already verified end to end** — profiled, uploaded, sha256-matched. Swapping for
  no expected gain spends a re-verification cycle and adds risk.

`adapters_best/v5c_global1200_facts33_arith10.safetensors` is preserved, so the decision is
reversible if the arithmetic axis is later judged more valuable than the fact axis.

## The standing lesson
Across v4, v5, v5b and v5c, **four candidate models were prevented from shipping by the
gates, and every one of them looked acceptable by validation loss** — v5's was the best of
any run while its facts were eight questions worse. The evals, not the loss curve, are what
protected the submission.
