"""Deterministic offline finance module — the load-bearing half of the ADTC pairing.

The LLM interprets the operator's request and drafts the reply; THIS module does the
arithmetic and rule application the model must never guess:

- momo_parser: raw mobile-money statement/SMS text -> structured transactions
- ledger:      minimal double-entry ledger; exact-match reconciliation (the training-data
               convention) and lump-sum allocation with carry (the case LLMs fumble)
- tax_rules:   citeable Nigeria-2025 verdicts computed from the same grep-verified fact
               base the model was trained on (data/seeds/nigeria_tax_facts.json)

Stdlib only; Decimal money; every public function is pure and unit-tested.
"""
from .momo_parser import Transaction, parse_statement
from .ledger import Invoice, Allocation, Ledger, reconcile_exact, allocate_lump_sum
from .tax_rules import TaxRules

__all__ = [
    "Transaction", "parse_statement",
    "Invoice", "Allocation", "Ledger", "reconcile_exact", "allocate_lump_sum",
    "TaxRules",
]
