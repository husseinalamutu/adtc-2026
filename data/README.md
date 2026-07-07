# Dataset pipeline — offline SME back-office copilot

Produces the fine-tune dataset for `corporate_enterprise` (English, African-SME back-office:
invoicing/quotes, mobile-money reconciliation, VAT/compliance Q&A, multi-currency).

## Why two generators

| Generator | Covers | Ground truth |
|---|---|---|
| `generators/templated_gen.py` | Invoices, quotes, mobile-money (M-Pesa/MoMo) reconciliation, multi-currency, VAT math | **Programmatically computed** — deterministic, free, unit-testable. This is the backbone: it's where "did the model get the arithmetic right" is checked, and arithmetic is exactly what the accuracy score punishes hardest. |
| `generators/claude_teacher_gen.py` | Open-ended advisory: VAT/tax-regime Q&A, compliance explanations, business correspondence tone | **Claude Opus 4.8** (structured output, batched) — needed because there's no programmatic ground truth for "explain this well," only for "compute this right." |

Never invert this split — don't ask Claude to do the arithmetic (it will occasionally get it
wrong and you'd be baking errors into training data), and don't hand-template the advisory
content (it reads robotic and won't generalize to the 2 hidden judge prompts).

## Pipeline

```
seeds/*.json  →  generators/*.py  →  build_dataset.py  →  out/{train,holdout}.jsonl
                                                              ↑
                                              tests/test_dataset_quality.py (run before every use)
```

- `build_dataset.py` merges both generators' output, dedupes by normalized-prompt hash, and
  splits **by scenario family** (not randomly) so the hold-out set contains scenario shapes the
  model never trained on — this is our proxy for the 2 organizer-added hidden prompts.
- `tests/test_dataset_quality.py` re-derives every templated example's arithmetic from its raw
  fields and fails loudly on mismatch; also asserts zero train/holdout overlap and minimum
  per-category counts. **Run this after every regeneration.**

## Quick start

```bash
pip install -r requirements.txt
python generators/templated_gen.py --n 4000 --out out/templated.jsonl
python generators/claude_teacher_gen.py --n 800 --out out/teacher.jsonl   # needs ANTHROPIC_API_KEY
python build_dataset.py --inputs out/templated.jsonl out/teacher.jsonl --out-dir out
pytest tests/ -v
```
