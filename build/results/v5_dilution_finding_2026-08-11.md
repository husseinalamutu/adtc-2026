> ⚠️ **SUPERSEDED — THE DIAGNOSIS BELOW IS WRONG.** The fact collapse was not gradient
> dilution; three Nigeria drill families had been assigned wholesale to the holdout
> split and were absent from training entirely. See `v5_split_bug_2026-08-11.md`.
> Kept unedited as the audit trail of a confident, quantified, incorrect analysis.

# v5 — the gate held, and taught us the dilution law (2026-08-11)

## Result: NO v5 checkpoint shipped. v3 remains the submission model.

| Model | Facts | Arithmetic | Narration | Verdict |
|---|---|---|---|---|
| **v3 (incumbent, shipped)** | **34/37** | 9/12 | 5/5 | — |
| v5 @ ckpt 1400 | 26/37 | **10/12** | 5/5 | below gate |
| v5 @ ckpt 1100 | 23/37 | **10/12** | 4/5 | below gate |
| v5 @ ckpt 900 | 26/37 | **10/12** | 4/5 | below gate |

Gate (fixed before any result was seen): **facts ≥ 34 AND arithmetic > 9**.

## What worked
The arithmetic repair drills did exactly their job: **9/12 → 10/12 at every checkpoint**,
consistently, including the multi-item VAT and margin-vs-markup defects the eval exposed.
The technique — deterministic ground truth plus *showing the working* — transfers.

## What broke, and why
Facts fell 34 → 26. The loss is not random; it lands on the facts that historically needed
the most reinforcement:

| Topic | v3 | v5 | Δ | note |
|---|---|---|---|---|
| dev_levy | 4/4 | 1/4 | −3 | the topic that only reached 4/4 after targeted top-ups |
| personal_income_tax | 3/3 | 1/3 | −2 | |
| withholding_tax | 1/2 | 0/2 | −1 | |
| capital_gains | 3/3 | 2/3 | −1 | |
| filing_penalties | 2/2 | 1/2 | −1 | |
| cit_small_rate | 4/4 | 3/4 | −1 | |
| VAT / standard CIT / prof-services (heavily drilled) | held | held | 0 | |

**Cause: gradient dilution.** Nigeria's share of the training mix nearly halved:

| | Nigeria rows | Total | Share |
|---|---|---|---|
| v3 | 780 × 3 = 2,340 | 4,904 | **~48%** |
| v5 | 642 × 2 = 1,284 | 4,997 | **~26%** |

Adding 1,100 new drills *and* dropping oversampling from 3× to 2× cut fact reinforcement
by half. The heavily-drilled gate facts survived; the marginal ones did not.

### The law this establishes (consistent with every prior experiment)
Fact recall in a 3B QLoRA is a function of **exposure share**, and it degrades
gracefully-then-suddenly. Corroborating evidence across the project:
- v1 → v3: dev_levy 1/4 → 4/4 when mentions went from 23 to 64 (adding exposure)
- v4: +200 iters of *more of the same* regressed facts 34 → 31 (over-training a fixed mix)
- 1.5B: facts held at 35/37 but arithmetic broke (capacity is skill-specific, not global)
- v5: exposure halved → the least-reinforced facts collapse first

## Next: v5b
Single variable changed — Nigeria oversampling **2× → 4×** (6,225 train rows, ~39% share),
identical data, recipe and iteration count. Hypothesis: the arithmetic gain is carried by
600 drills that were effective at 2× and should survive re-weighting, while restored
Nigeria share recovers fact recall.

If v5b clears **facts ≥ 34 AND arithmetic > 9**, it ships. If it recovers facts but loses
the arithmetic gain, that is a genuine tradeoff and goes to the project owner rather than
being settled by a threshold.

## Process note
This is the second time the pre-committed gate has prevented a regression from shipping
(v4 was the first). Both times the model looked reasonable by validation loss — v5's best
val (0.314) was the best of any run to date, and its facts were 8 questions worse than the
model it would have replaced. **Validation loss does not track what is scored.**
