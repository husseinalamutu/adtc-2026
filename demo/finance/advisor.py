"""Decision engine — "what should I do about it?"

The layer above analytics. It reads the computed picture (forecast, receivables,
anomalies, expense movements), proposes concrete interventions, QUANTIFIES each one
from the books, ranks them by recoverable value, and states whether the combination
actually closes the projected gap.

Every naira of claimed impact traces to a real row in the ledger — nothing is estimated
by the model, and nothing is invented here either. Confidence is stated explicitly
because "collect what a customer already owes" and "cut discretionary spend" are not
equally certain, and an operator deserves to know which is which.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from . import anomalies as anomaly_mod
from .analytics import business_health, customers_owing, prev_month_bounds, period_summary
from .forecast import project

TWO = Decimal("0.01")

# Spend the operator can realistically throttle within a month without stopping trading.
DISCRETIONARY = {"Transport", "Airtime & data", "Entertainment", "Miscellaneous", "Bank charges"}


def _d(x) -> Decimal:
    return Decimal(str(x)).quantize(TWO, rounding=ROUND_HALF_UP)


@dataclass
class Recommendation:
    action: str
    impact: Decimal            # naira this frees up, computed from the books
    confidence: str            # high | medium — how certain the money actually appears
    evidence: str              # the computed fact behind it, so the operator can check

    def line(self, currency: str = "NGN") -> str:
        return f"{self.action} — frees {currency} {self.impact:,} ({self.confidence} confidence; {self.evidence})"


@dataclass
class Plan:
    as_of: date
    shortfall: Decimal
    recommendations: list[Recommendation] = field(default_factory=list)
    horizon_start: date | None = None
    horizon_end: date | None = None

    @property
    def total_impact(self) -> Decimal:
        return _d(sum((r.impact for r in self.recommendations), Decimal("0")))

    @property
    def closes_gap(self) -> bool:
        return self.shortfall <= 0 or self.total_impact >= self.shortfall

    def as_ground_truth(self, currency: str = "NGN") -> str:
        """Deterministic brief handed to the LLM, which phrases it and never re-ranks."""
        if not self.recommendations:
            return ("No corrective actions needed from the current books: no projected shortfall, "
                    "no overdue receivables, and no recoverable errors detected.")
        head = (f"Projected shortfall: {currency} {self.shortfall:,}." if self.shortfall > 0
                else "No projected shortfall; the actions below still free up cash.")
        lines = [f"{i}. {r.line(currency)}" for i, r in enumerate(self.recommendations, 1)]
        if self.shortfall > 0:
            tail = (f"These actions total {currency} {self.total_impact:,} and "
                    + ("CLOSE the projected shortfall."
                       if self.closes_gap else
                       f"do NOT fully close it — {currency} {_d(self.shortfall - self.total_impact):,} "
                       f"would remain. Consider deferring non-critical procurement."))
        else:
            tail = f"These actions total {currency} {self.total_impact:,} of recoverable cash."
        return "\n".join([head, "Recommended actions, highest recoverable value first:", *lines, tail])


def recommend(store, as_of: date, committed_obligations: Decimal | None = None,
              limit: int = 5) -> Plan:
    forecast = project(store, as_of, committed_obligations=committed_obligations)
    plan = Plan(as_of=as_of, shortfall=_d(forecast.shortfall),
                horizon_start=forecast.horizon_start, horizon_end=forecast.horizon_end)
    recs: list[Recommendation] = []

    # 1. Money already owed to the business — the most certain cash there is.
    for customer, amount, days in customers_owing(store, as_of):
        if days > 0:
            recs.append(Recommendation(
                action=f"Chase {customer} for payment",
                impact=amount, confidence="high",
                evidence=f"invoice(s) {days} days past due"))

    # 2. Money already paid out in error — recoverable by asking.
    for a in anomaly_mod.detect(store):
        if a.kind == "duplicate_payment":
            who = a.counterparty or "the payee"
            recs.append(Recommendation(
                action=f"Recover the suspected double payment from {who}",
                impact=a.amount, confidence="high",
                evidence=f"identical amount paid twice around {a.txn_date}"))
        elif a.kind == "price_jump" and a.counterparty:
            # only the EXCESS over the usual price is recoverable, not the whole invoice
            excess = _excess_over_usual(a)
            if excess > 0:
                recs.append(Recommendation(
                    action=f"Query the price increase with {a.counterparty}",
                    impact=excess, confidence="medium",
                    evidence=f"paid above this supplier's usual rate on {a.txn_date}"))

    # 3. Discretionary spending that actually grew — controllable within the month.
    recs += _discretionary_reductions(store, as_of)

    recs.sort(key=lambda r: (r.confidence != "high", -r.impact))
    plan.recommendations = recs[:limit]
    return plan


def _excess_over_usual(a) -> Decimal:
    """Recover the computed 'usual NGN X' out of the anomaly's own reason string.

    The detector already computed the supplier's usual rate; re-deriving it here would
    risk the two layers disagreeing about the same fact.
    """
    import re
    m = re.search(r"usual NGN ([\d,]+(?:\.\d+)?)", a.reason)
    if not m:
        return Decimal("0.00")
    return _d(a.amount - Decimal(m.group(1).replace(",", "")))


def _discretionary_reductions(store, as_of: date) -> list[Recommendation]:
    """Only the INCREASE over last month is proposed as reducible — telling an operator
    to zero out transport is useless advice; telling them it grew by X is actionable."""
    health = business_health(store, as_of)
    prev_start, prev_end = prev_month_bounds(as_of)
    prev = dict(period_summary(store, prev_start, prev_end).expense_by_category)

    out = []
    for category, amount in health.period.expense_by_category:
        if category not in DISCRETIONARY:
            continue
        before = prev.get(category, Decimal("0"))
        increase = _d(amount - before)
        if before > 0 and increase > 0:
            out.append(Recommendation(
                action=f"Cut {category.lower()} back to last month's level",
                impact=increase, confidence="medium",
                evidence=f"{category} rose from NGN {before:,} to NGN {amount:,}"))
    return out
