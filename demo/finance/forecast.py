"""Cash-flow projection — "will I have enough to pay my suppliers next month?"

Deterministic and deliberately conservative. The model must never estimate this: a wrong
cash answer makes a business owner miss payroll. We project from the business's own
history, state a range rather than a false-precision point, and show the arithmetic.

Method (robust, matching anomalies.py's philosophy — median/MAD, not mean/stdev, so one
freak month doesn't drag the projection):
    projected inflow  = median monthly inflow over the observed months
    projected outflow = median monthly outflow
    band              = ±MAD of monthly net, the business's own observed volatility
    known obligations = invoices already due/overdue are NOT assumed to arrive
Assumptions are returned with the number so the operator (and the judge) can audit them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from statistics import median
from .money import d as _d

MIN_MONTHS = 2          # below this there is no history to project from — say so, don't guess


def _median(values: list[Decimal]) -> Decimal:
    return _d(median(values)) if values else Decimal("0.00")


def _mad(values: list[Decimal]) -> Decimal:
    if not values:
        return Decimal("0.00")
    med = _median(values)
    return _median([abs(v - med) for v in values])


def _spread(values: list[Decimal]) -> Decimal:
    """Observed month-to-month volatility, with a guard against false certainty.

    MAD is robust but COLLAPSES TO ZERO on short histories with repeated values
    (e.g. nets of [+600k, −600k, +600k] gives MAD 0). A zero-width band on a visibly
    volatile business would tell the operator "this is certain" when it is not, so we
    fall back to half the observed range. Only a genuinely flat history yields no band.
    """
    if not values:
        return Decimal("0.00")
    mad = _mad(values)
    if mad > 0:
        return mad
    return _d((max(values) - min(values)) / 2)


def _month_key(d: date) -> tuple[int, int]:
    return d.year, d.month


@dataclass
class CashForecast:
    horizon_start: date
    horizon_end: date
    opening_cash: Decimal
    projected_inflow: Decimal
    projected_outflow: Decimal
    projected_closing: Decimal
    low: Decimal                     # closing cash in a bad month (−1 MAD)
    high: Decimal                    # closing cash in a good month (+1 MAD)
    committed_obligations: Decimal   # what we already know is owed out
    shortfall: Decimal               # >0 = projected to come up short
    months_observed: int
    assumptions: list[str] = field(default_factory=list)
    insufficient_history: bool = False

    def as_ground_truth(self, currency: str = "NGN") -> str:
        if self.insufficient_history:
            return (f"Not enough history to project: {self.months_observed} complete month(s) "
                    f"on record (need {MIN_MONTHS}). Record more trading first.")
        verdict = (f"PROJECTED SHORTFALL: {currency} {self.shortfall:,}" if self.shortfall > 0
                   else f"Projected to cover obligations with {currency} "
                        f"{abs(self.shortfall):,} to spare")
        return "\n".join([
            f"Horizon: {self.horizon_start} to {self.horizon_end} "
            f"(projected from {self.months_observed} months of trading)",
            f"Opening cash: {currency} {self.opening_cash:,}",
            f"Expected inflow: {currency} {self.projected_inflow:,}",
            f"Expected outflow: {currency} {self.projected_outflow:,}",
            f"Projected closing cash: {currency} {self.projected_closing:,} "
            f"(range {currency} {self.low:,} to {currency} {self.high:,})",
            f"Known obligations already committed: {currency} {self.committed_obligations:,}",
            verdict,
            "Assumptions: " + "; ".join(self.assumptions),
        ])


def _monthly_totals(txns) -> tuple[dict, dict]:
    ins: dict[tuple[int, int], Decimal] = {}
    outs: dict[tuple[int, int], Decimal] = {}
    for t in txns:
        key = _month_key(t.txn_date)
        bucket = ins if t.direction == "in" else outs
        bucket[key] = _d(bucket.get(key, Decimal("0")) + t.amount)
    for k in set(ins) | set(outs):
        ins.setdefault(k, Decimal("0.00"))
        outs.setdefault(k, Decimal("0.00"))
    return ins, outs


def project(store, as_of: date, committed_obligations: Decimal | None = None) -> CashForecast:
    """Project the month following `as_of`.

    `committed_obligations` = amounts the operator already knows are due (supplier bills).
    Left None, we use nothing — we never invent obligations the books don't show.
    """
    txns = store.transactions(end=as_of)
    ins, outs = _monthly_totals(txns)

    # Only COMPLETE months inform the projection — the current partial month would
    # understate a full month's trading and bias the forecast low.
    current = _month_key(as_of)
    complete = sorted(k for k in ins if k != current)

    opening = _d(sum((t.amount if t.direction == "in" else -t.amount for t in txns), Decimal("0")))
    horizon_start = (as_of.replace(day=1) + timedelta(days=32)).replace(day=1)
    horizon_end = (horizon_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    obligations = _d(committed_obligations or 0)

    if len(complete) < MIN_MONTHS:
        return CashForecast(
            horizon_start=horizon_start, horizon_end=horizon_end, opening_cash=opening,
            projected_inflow=Decimal("0.00"), projected_outflow=Decimal("0.00"),
            projected_closing=opening, low=opening, high=opening,
            committed_obligations=obligations, shortfall=Decimal("0.00"),
            months_observed=len(complete), insufficient_history=True,
            assumptions=["insufficient complete months of history"])

    monthly_in = [ins[k] for k in complete]
    monthly_out = [outs[k] for k in complete]
    nets = [_d(ins[k] - outs[k]) for k in complete]

    proj_in, proj_out = _median(monthly_in), _median(monthly_out)
    volatility = _spread(nets)
    closing = _d(opening + proj_in - proj_out - obligations)

    return CashForecast(
        horizon_start=horizon_start, horizon_end=horizon_end, opening_cash=opening,
        projected_inflow=proj_in, projected_outflow=proj_out, projected_closing=closing,
        low=_d(closing - volatility), high=_d(closing + volatility),
        committed_obligations=obligations,
        # shortfall is measured at the LOW end: planning cash on the optimistic case is
        # how businesses miss payroll
        shortfall=_d(-min(closing, _d(closing - volatility))) if _d(closing - volatility) < 0
                  else _d(0),
        months_observed=len(complete),
        assumptions=[
            f"typical month based on the median of {len(complete)} complete months",
            f"range is ±{volatility:,} (the business's own month-to-month variation)",
            "assumes trading continues at the historical rate",
            "unpaid invoices are NOT assumed to be collected",
        ],
    )
