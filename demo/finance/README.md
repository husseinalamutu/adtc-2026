# finance/ — the deterministic half of the pairing

This is the load-bearing cross-disciplinary module declared in `metadata.json`:
a finance/accounting engine the LLM is *paired with*, not a wrapper around it.

**Division of labor** (why neither half works alone):
- The **model** (Qwen2.5-3B fine-tune) understands the operator's messy request
  ("customer paid 127k by MoMo, which invoices does that clear?") and drafts the reply.
- **This module** computes everything that must never be guessed: statement parsing,
  payment allocation with carry, double-entry balances, and citeable Nigeria-2025 tax
  verdicts. We *measured* why this matters: LLM arithmetic on multi-invoice allocation
  is unreliable at this size (see `build/results/model_size_tradeoff_2026-07-13.md`) —
  the module's `Allocation.summary()` is handed to the model as ground truth, so the
  narrative always matches the math.

**One source of truth**: `tax_rules.py` computes its rates/thresholds from the same
grep-verified `data/seeds/nigeria_tax_facts.json` the training data was generated from.
Weights, module, and demo can never disagree about what the law says.

## Usage
```python
from finance import parse_statement, Invoice, Ledger, TaxRules

txs = parse_statement("TX001: NGN 45,000; TXN 8842 | RECEIVED NGN 127,500 from 0803***512")

led = Ledger()
led.add_invoice("INV-114", 85_000)
led.add_invoice("INV-121", 42_500)
alloc = led.record_lump_sum_payment(127_500)
alloc.summary("NGN")   # -> "Settled: INV-114, INV-121. Total outstanding: NGN 0.00."
led.trial_balance()    # -> Decimal('0.00') — the books always balance

TaxRules().small_company_assessment(60_000_000, 50_000_000, professional_services=True).verdict
# -> "NOT a small company (professional-services exclusion, ...)" + citations to the Act
```

Stdlib only (offline by construction), `Decimal` money throughout.
Tests: `python3 -m pytest demo/finance/tests/ -q` — the cases are the exact scenarios
from the model evals, including the two the models got wrong.
