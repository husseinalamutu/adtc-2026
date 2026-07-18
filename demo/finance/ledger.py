"""Minimal double-entry ledger + the two reconciliation modes SMEs actually need.

- reconcile_exact: match statement transactions to invoices by exact amount — the convention
  our training data teaches the model, so module output and model narrative always agree.
- allocate_lump_sum: apply one payment across invoices oldest-first WITH carry — the
  multi-step case where LLM arithmetic is unreliable (measured; see
  build/results/model_size_tradeoff_2026-07-13.md). This module is why the product never
  ships a guessed remainder.

Double-entry: every event posts balanced DR/CR pairs; trial_balance() always sums to 0.
Accounts: CASH, ACCOUNTS_RECEIVABLE, SALES, CUSTOMER_CREDIT (unapplied overpayment).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

from .momo_parser import Transaction

TWO_PLACES = Decimal("0.01")


def _d(x) -> Decimal:
    return Decimal(str(x)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


@dataclass
class Invoice:
    invoice_id: str
    amount: Decimal
    paid: Decimal = Decimal("0")

    def __post_init__(self):
        self.amount = _d(self.amount)
        self.paid = _d(self.paid)

    @property
    def outstanding(self) -> Decimal:
        return _d(self.amount - self.paid)

    @property
    def settled(self) -> bool:
        return self.outstanding == Decimal("0.00")


@dataclass
class Allocation:
    """Result of applying payment(s) to invoices. All amounts Decimal, all derived — never guessed."""
    applied: list[tuple[str, Decimal]]          # (invoice_id, amount applied)
    settled_ids: list[str]
    partially_paid: list[tuple[str, Decimal]]   # (invoice_id, still outstanding on it)
    outstanding_total: Decimal
    unapplied_credit: Decimal                   # payment left over after all invoices

    def summary(self, currency: str = "NGN") -> str:
        """Deterministic one-paragraph summary the demo app hands to the LLM as ground truth."""
        parts = []
        parts.append("Settled: " + (", ".join(self.settled_ids) if self.settled_ids else "none") + ".")
        for inv_id, rem in self.partially_paid:
            parts.append(f"{inv_id} partially paid, {currency} {rem:,} still due.")
        parts.append(f"Total outstanding: {currency} {self.outstanding_total:,}.")
        if self.unapplied_credit:
            parts.append(f"Unapplied customer credit: {currency} {self.unapplied_credit:,}.")
        return " ".join(parts)


def reconcile_exact(transactions: list[Transaction], invoices: list[Invoice]) -> Allocation:
    """Training-data convention: a transaction settles an invoice iff amounts match exactly.
    Each transaction/invoice is consumed at most once; unmatched transactions are ignored
    (airtime, unrelated transfers — 'noise' in the statements)."""
    remaining_tx = list(transactions)
    applied: list[tuple[str, Decimal]] = []
    for inv in invoices:
        for tx in remaining_tx:
            if _d(tx.amount) == inv.outstanding and inv.outstanding > 0:
                inv.paid = _d(inv.paid + tx.amount)
                applied.append((inv.invoice_id, _d(tx.amount)))
                remaining_tx.remove(tx)
                break
    return _result(invoices, applied, Decimal("0"))


def allocate_lump_sum(amount, invoices: list[Invoice]) -> Allocation:
    """Apply one lump-sum payment across invoices in the given (oldest-first) order,
    carrying the remainder invoice to invoice. Overpayment becomes unapplied credit."""
    left = _d(amount)
    applied: list[tuple[str, Decimal]] = []
    for inv in invoices:
        if left <= 0:
            break
        take = min(left, inv.outstanding)
        if take > 0:
            inv.paid = _d(inv.paid + take)
            applied.append((inv.invoice_id, take))
            left = _d(left - take)
    return _result(invoices, applied, left)


def _result(invoices: list[Invoice], applied, credit: Decimal) -> Allocation:
    return Allocation(
        applied=applied,
        settled_ids=[i.invoice_id for i in invoices if i.settled],
        partially_paid=[(i.invoice_id, i.outstanding) for i in invoices
                        if not i.settled and i.paid > 0],
        outstanding_total=_d(sum((i.outstanding for i in invoices), Decimal("0"))),
        unapplied_credit=credit,
    )


@dataclass
class Ledger:
    """Append-only journal of balanced double-entry postings over the reconciliation events."""
    entries: list[tuple[str, str, str, Decimal]] = field(default_factory=list)  # (memo, dr, cr, amt)
    invoices: dict[str, Invoice] = field(default_factory=dict)

    def add_invoice(self, invoice_id: str, amount) -> Invoice:
        inv = Invoice(invoice_id, _d(amount))
        self.invoices[invoice_id] = inv
        self.entries.append((f"issue {invoice_id}", "ACCOUNTS_RECEIVABLE", "SALES", inv.amount))
        return inv

    def record_lump_sum_payment(self, amount, order: list[str] | None = None) -> Allocation:
        ids = order or list(self.invoices)
        alloc = allocate_lump_sum(amount, [self.invoices[i] for i in ids])
        for inv_id, applied in alloc.applied:
            self.entries.append((f"payment -> {inv_id}", "CASH", "ACCOUNTS_RECEIVABLE", applied))
        if alloc.unapplied_credit:
            self.entries.append(("unapplied overpayment", "CASH", "CUSTOMER_CREDIT", alloc.unapplied_credit))
        return alloc

    def balances(self) -> dict[str, Decimal]:
        acc: dict[str, Decimal] = {}
        for _, dr, cr, amt in self.entries:
            acc[dr] = _d(acc.get(dr, Decimal("0")) + amt)
            acc[cr] = _d(acc.get(cr, Decimal("0")) - amt)
        return acc

    def trial_balance(self) -> Decimal:
        """Sum of all account balances — 0.00 iff the books balance (they always must)."""
        return _d(sum(self.balances().values(), Decimal("0")))
