"""Deterministic business analytics — the numbers behind "what happened to my business?".

Every figure here is computed from the local store, never generated. The LLM receives
these as ground truth and only phrases them. Pure functions over Store reads, so each
metric is unit-testable against the known sample business.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from .money import d as _d

COGS_CATEGORIES = {"Inventory purchase"}   # what counts against gross margin


def _pct_change(now: Decimal, before: Decimal) -> Decimal | None:
    """None when there's no baseline — an honest 'no comparison', never a fake 0%."""
    if before == 0:
        return None
    return _d((now - before) / before * 100)


def month_bounds(anchor: date) -> tuple[date, date]:
    start = anchor.replace(day=1)
    nxt = (start + timedelta(days=32)).replace(day=1)
    return start, nxt - timedelta(days=1)


def prev_month_bounds(anchor: date) -> tuple[date, date]:
    start, _ = month_bounds(anchor)
    return month_bounds(start - timedelta(days=1))


@dataclass
class PeriodSummary:
    start: date
    end: date
    revenue: Decimal
    expenses: Decimal
    cogs: Decimal
    net: Decimal
    gross_margin_pct: Decimal | None
    expense_by_category: list[tuple[str, Decimal]]
    transaction_count: int


@dataclass
class BusinessHealth:
    """The 'Ask My Business' payload: this month vs last, plus what's owed to you."""
    period: PeriodSummary
    previous: PeriodSummary
    revenue_change_pct: Decimal | None
    expense_change_pct: Decimal | None
    margin_change_pts: Decimal | None
    cash_position: Decimal
    receivables_total: Decimal
    receivables_overdue: Decimal
    biggest_expense_movers: list[tuple[str, Decimal, Decimal | None]] = field(default_factory=list)

    def as_ground_truth(self, currency: str = "NGN") -> str:
        """Deterministic text handed to the LLM as VERIFIED FIGURES (it may not recompute)."""
        def pct(v, suffix="%"):
            return "n/a" if v is None else f"{v:+.1f}{suffix}"
        lines = [
            f"Period: {self.period.start} to {self.period.end}",
            f"Revenue: {currency} {self.period.revenue:,} ({pct(self.revenue_change_pct)} vs prior month)",
            f"Expenses: {currency} {self.period.expenses:,} ({pct(self.expense_change_pct)} vs prior month)",
            f"Net: {currency} {self.period.net:,}",
            f"Gross margin: " + ("n/a" if self.period.gross_margin_pct is None
                                 else f"{self.period.gross_margin_pct:.1f}% ({pct(self.margin_change_pts, ' pts')})"),
            f"Cash position (all time): {currency} {self.cash_position:,}",
            f"Receivables outstanding: {currency} {self.receivables_total:,} "
            f"(overdue: {currency} {self.receivables_overdue:,})",
        ]
        if self.biggest_expense_movers:
            movers = "; ".join(
                f"{c} {currency} {amt:,} ({pct(ch)})" for c, amt, ch in self.biggest_expense_movers)
            lines.append(f"Largest expense movements: {movers}")
        return "\n".join(lines)


def period_summary(store, start: date, end: date) -> PeriodSummary:
    txns = store.transactions(start=start, end=end)
    revenue = _d(sum((t.amount for t in txns if t.direction == "in"), Decimal("0")))
    expenses = _d(sum((t.amount for t in txns if t.direction == "out"), Decimal("0")))
    cogs = _d(sum((t.amount for t in txns
                   if t.direction == "out" and (t.category or "") in COGS_CATEGORIES), Decimal("0")))
    by_cat: dict[str, Decimal] = {}
    for t in txns:
        if t.direction == "out":
            key = t.category or "Uncategorised"
            by_cat[key] = _d(by_cat.get(key, Decimal("0")) + t.amount)
    gross_margin = None if revenue == 0 else _d((revenue - cogs) / revenue * 100)
    return PeriodSummary(
        start=start, end=end, revenue=revenue, expenses=expenses, cogs=cogs,
        net=_d(revenue - expenses), gross_margin_pct=gross_margin,
        expense_by_category=sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True),
        transaction_count=len(txns),
    )


def cash_position(store, as_of: date | None = None) -> Decimal:
    """Net of all money in and out up to `as_of` (all time by default)."""
    txns = store.transactions(end=as_of)
    return _d(sum((t.amount if t.direction == "in" else -t.amount for t in txns), Decimal("0")))


def receivables_aging(store, as_of: date) -> dict[str, Decimal]:
    """Outstanding invoice value bucketed by how overdue it is."""
    buckets = {"current": Decimal("0"), "1-30": Decimal("0"),
               "31-60": Decimal("0"), "60+": Decimal("0")}
    for inv in store.invoices(unpaid_only=True):
        due = inv.due_date or inv.issued_date
        days = (as_of - due).days
        key = "current" if days <= 0 else "1-30" if days <= 30 else "31-60" if days <= 60 else "60+"
        buckets[key] = _d(buckets[key] + inv.outstanding)
    return buckets


def customers_owing(store, as_of: date) -> list[tuple[str, Decimal, int]]:
    """(customer, outstanding, days overdue) — who to chase, worst first."""
    rows: dict[str, tuple[Decimal, int]] = {}
    for inv in store.invoices(unpaid_only=True):
        due = inv.due_date or inv.issued_date
        overdue = max(0, (as_of - due).days)
        amt, worst = rows.get(inv.customer, (Decimal("0"), 0))
        rows[inv.customer] = (_d(amt + inv.outstanding), max(worst, overdue))
    return sorted(((c, a, d) for c, (a, d) in rows.items()), key=lambda r: r[1], reverse=True)


def business_health(store, anchor: date) -> BusinessHealth:
    cur_start, cur_end = month_bounds(anchor)
    prev_start, prev_end = prev_month_bounds(anchor)
    cur = period_summary(store, cur_start, cur_end)
    prev = period_summary(store, prev_start, prev_end)

    prev_by_cat = dict(prev.expense_by_category)
    movers = []
    for cat, amt in cur.expense_by_category[:3]:
        movers.append((cat, amt, _pct_change(amt, prev_by_cat.get(cat, Decimal("0")))))

    aging = receivables_aging(store, anchor)
    margin_change = (None if cur.gross_margin_pct is None or prev.gross_margin_pct is None
                     else _d(cur.gross_margin_pct - prev.gross_margin_pct))
    return BusinessHealth(
        period=cur, previous=prev,
        revenue_change_pct=_pct_change(cur.revenue, prev.revenue),
        expense_change_pct=_pct_change(cur.expenses, prev.expenses),
        margin_change_pts=margin_change,
        cash_position=cash_position(store, cur_end),
        receivables_total=_d(sum(aging.values(), Decimal("0"))),
        receivables_overdue=_d(aging["1-30"] + aging["31-60"] + aging["60+"]),
        biggest_expense_movers=movers,
    )
