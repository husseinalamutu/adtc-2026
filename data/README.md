# Dataset pipeline — offline SME back-office copilot

Produces the fine-tune dataset for `corporate_enterprise` (English, African-SME back-office:
invoicing/quotes, mobile-money reconciliation, VAT/compliance Q&A, multi-currency).

## Compliance strategy: Nigeria-deep + general-competent + RAG demo layer

Tax law is genuinely different per country, so "general African tax advisor" would be shallow
everywhere. We went **layered** instead:

1. **Deep, source-grounded fine-tuning on Nigeria** (`generators/nigeria_tax_gen.py`) — the
   2025 Tax Reform Acts, grounded in the actual statute text (OCR'd gazette + a clean
   text-layer companion Act + corroborating secondary sources). This is what the sandbox's
   *bare-model* accuracy score is won on, since Nigeria is a single, checkable, high-value
   African market.
2. **General accountant/tax-reasoning competence** baked in via `templated_gen.py` (arithmetic)
   and `claude_teacher_gen.py` (the other 4 markets' VAT/WHT reasoning patterns) — so the model
   degrades gracefully on non-Nigeria hidden-prompt content instead of hallucinating.
3. **A RAG document-upload feature in the demo app** (not this pipeline — see `demo/` once
   built) lets a user upload their own country's tax law PDF for grounding. This is a **demo-only**
   differentiator: the sandbox never runs RAG, so it must never be the thing standing between the
   bare model and a correct answer — see `REPORT.md`.

## Why three generators

| Generator | Covers | Ground truth |
|---|---|---|
| `generators/templated_gen.py` | Invoices, quotes, mobile-money (M-Pesa/MoMo) reconciliation, multi-currency, VAT math | **Programmatically computed** — deterministic, free, unit-testable. This is the arithmetic backbone. |
| `generators/claude_teacher_gen.py` | Open-ended advisory for Kenya/Ghana/Uganda/Tanzania (Nigeria excluded — see below) | **Gemini (free tier, $0)**, structured JSON output, threaded with retry/backoff. |
| `generators/nigeria_tax_gen.py` | Deep Nigeria compliance: CIT/VAT/WHT/CGT/PIT/Development Levy, filing deadlines, penalties, diaspora tax-residency rules | **Gemini, grounded in `seeds/nigeria_tax_facts.json`** — a hand-curated, confidence-tagged fact table extracted from the primary Acts. The model is instructed (system prompt) and test-checked to never state a number not in that file. |

(Despite the filename, `claude_teacher_gen.py` now calls Gemini, not Claude — moved 2026-07-08
purely to make dataset generation free; see `generators/_gemini_common.py` header for why.)

Never invert the templated/teacher split — don't ask the teacher model to do the arithmetic (it
will occasionally get it wrong and you'd be baking errors into training data), and don't
hand-template the advisory content (it reads robotic and won't generalize to the 3 hidden
judge prompts).

## The Nigeria fact base — how it was built and why to trust it

`seeds/nigeria_tax_facts.json` is the single source of truth for every Nigeria tax number in
this dataset. Sources, in `seeds/nigeria_raw/`:

- `tax_act_ocr_full.txt` — **OCR** of the official Federal Republic of Nigeria Gazette,
  *Nigeria Tax Act 2025* (210 pages). The PDF's text layer is corrupted (broken font-encoding
  table — confirmed across two extraction libraries), so pages were rendered to images and run
  through `tesseract`. Verified good quality on spot checks.
- `tax_admin_act_clean.txt` — clean text-layer extraction of the *Nigeria Tax Administration
  Act 2025* (93 pages, no OCR needed, high confidence).
- `zenith_diaspora_guide.txt` — a bank-published diaspora tax FAQ, high confidence.
- Reputable secondary corroboration (EY, Baker Tilly, Aluko & Oyebode, KPMG, Mercans/Safeguard
  Global) via web search, used to fill gaps and cross-check numbers the OCR grep couldn't
  directly confirm.

**Every fact in the JSON is tagged** `"confidence": "primary_confirmed"` (found verbatim in the
OCR'd or clean-text primary Act — e.g. the 0%/30% CIT split and the 4% Development Levy were
directly grepped out of the gazette) or `"confidence": "secondary_corroborated"` (agreed by 2+
independent reputable sources but not yet grep-confirmed in the primary text). The generator's
system prompt hedges language accordingly and always closes with "confirm with FIRS/an
accountant" — standard, honest advisory practice, not a workaround for a source we don't trust.

**If you get a cleaner OCR of the full Nigeria Tax Act** (a text-native version, or a better
scan), re-verify every `secondary_corroborated` fact against it and flip the tags — that's a
strict improvement to accuracy at zero marginal generation cost.

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
export GEMINI_API_KEY=your-key-here   # free, no card: https://aistudio.google.com/apikey
python generators/templated_gen.py --n 4000 --out out/templated.jsonl
python generators/claude_teacher_gen.py --n 800 --out out/teacher.jsonl
python generators/nigeria_tax_gen.py --n 600 --out out/nigeria_tax.jsonl
python build_dataset.py --inputs out/templated.jsonl out/teacher.jsonl out/nigeria_tax.jsonl --out-dir out
pytest tests/ -v
```

`nigeria_tax_gen.py`'s fact-path validation (`TestNigeriaTaxFactGrounding` in `tests/`) needs
**no API key** — run `pytest tests/ -v -k Nigeria` first to catch a broken fact reference before
spending any generation time.

Both generator scripts write incrementally and resume automatically — if a run is interrupted
(rate limit, network blip, killed process), just re-run the same command; already-written
examples are skipped and only the remainder is generated.
