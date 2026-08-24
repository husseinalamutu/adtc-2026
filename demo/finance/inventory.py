"""Inventory as WORKING CAPITAL — the financial view of stock, not stock control.

Scope decision: this module answers financial questions (how much cash is tied up, what
did the goods I sold actually cost, how fast does capital turn over, what is trapped in
stock that won't move). It deliberately does NOT do reorder points, lead times or safety
stock — that is supply-chain optimisation, a different discipline.

It also fixes a real accounting defect. `analytics.py` approximates gross margin using the
"Inventory purchase" expense category, but purchases in a period are NOT the cost of the
goods sold in that period — buy heavily in June and the margin collapses even if trading
was normal. With stock movements recorded, COGS is the cost of what actually went OUT, and
the margin becomes correct.

Valuation is WEIGHTED AVERAGE COST: the standard SME method, and the one that behaves
sanely when the same SKU is bought at different prices (FIFO would need lot tracking that
a shop owner will not keep).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from .money import d as _d

DEAD_STOCK_DAYS = 90        # no outward movement in this long = capital sitting idle


@dataclass
class SkuPosition:
    sku: str
    description: str
    quantity_on_hand: int
    average_unit_cost: Decimal
    last_sold: date | None
    value: Decimal = field(default_factory=lambda: Decimal("0.00"))

    def days_idle(self, as_of: date) -> int | None:
        return None if self.last_sold is None else (as_of - self.last_sold).days


@dataclass
class InventoryPosition:
    as_of: date
    total_value: Decimal
    skus: list[SkuPosition]
    cogs_period: Decimal
    turnover: Decimal | None          # COGS ÷ average stock value, annualised
    days_inventory: Decimal | None    # 365 ÷ turnover
    dead_stock_value: Decimal
    dead_skus: list[SkuPosition]

    def as_ground_truth(self, currency: str = "NGN") -> str:
        lines = [
            f"Stock on hand at {self.as_of}: {currency} {self.total_value:,} "
            f"across {len(self.skus)} product(s)",
            f"Cost of goods sold in the period: {currency} {self.cogs_period:,}",
        ]
        if self.turnover is not None:
            lines.append(f"Inventory turnover: {self.turnover:.2f}x per year "
                         f"({self.days_inventory:.0f} days of stock held)")
        if self.dead_stock_value > 0:
            names = ", ".join(f"{s.description} ({currency} {s.value:,})"
                              for s in self.dead_skus[:3])
            lines.append(f"Capital tied up in stock unsold for {DEAD_STOCK_DAYS}+ days: "
                         f"{currency} {self.dead_stock_value:,} — {names}")
        else:
            lines.append("No stock has been sitting unsold beyond "
                         f"{DEAD_STOCK_DAYS} days.")
        return "\n".join(lines)


def position(store, as_of: date, period_start: date | None = None) -> InventoryPosition:
    """Value stock at weighted-average cost and compute the period's true COGS."""
    moves = [m for m in store.stock_movements(end=as_of)]
    period_start = period_start or (as_of.replace(day=1))

    by_sku: dict[str, dict] = {}
    cogs_period = Decimal("0.00")
    for m in moves:
        s = by_sku.setdefault(m.sku, {"desc": m.description, "qty": 0,
                                      "cost_pool": Decimal("0.00"), "last_sold": None})
        if m.direction == "in":
            s["qty"] += m.quantity
            s["cost_pool"] = _d(s["cost_pool"] + m.value)
        else:
            # value the outflow at the CURRENT weighted average, then reduce the pool
            avg = _d(s["cost_pool"] / s["qty"]) if s["qty"] > 0 else _d(m.unit_cost)
            consumed = _d(avg * m.quantity)
            s["qty"] = max(0, s["qty"] - m.quantity)
            s["cost_pool"] = _d(max(Decimal("0.00"), s["cost_pool"] - consumed))
            s["last_sold"] = m.move_date if not s["last_sold"] else max(s["last_sold"], m.move_date)
            if period_start <= m.move_date <= as_of:
                cogs_period = _d(cogs_period + consumed)

    skus: list[SkuPosition] = []
    for sku, s in by_sku.items():
        avg = _d(s["cost_pool"] / s["qty"]) if s["qty"] > 0 else Decimal("0.00")
        p = SkuPosition(sku=sku, description=s["desc"], quantity_on_hand=s["qty"],
                        average_unit_cost=avg, last_sold=s["last_sold"])
        p.value = _d(avg * s["qty"])
        skus.append(p)
    skus.sort(key=lambda p: p.value, reverse=True)

    total_value = _d(sum((p.value for p in skus), Decimal("0")))
    dead = [p for p in skus
            if p.value > 0 and (p.last_sold is None
                                or (as_of - p.last_sold).days >= DEAD_STOCK_DAYS)]
    dead_value = _d(sum((p.value for p in dead), Decimal("0")))

    # Annualised turnover from the period's COGS. Averaging opening/closing stock would
    # need an opening snapshot we may not have, so closing value is used and the method
    # is stated rather than hidden.
    days = max(1, (as_of - period_start).days + 1)
    turnover = days_inv = None
    if total_value > 0 and cogs_period > 0:
        turnover = _d(cogs_period / total_value * Decimal(365) / Decimal(days))
        if turnover > 0:
            days_inv = _d(Decimal(365) / turnover)

    return InventoryPosition(as_of=as_of, total_value=total_value, skus=skus,
                             cogs_period=cogs_period, turnover=turnover,
                             days_inventory=days_inv, dead_stock_value=dead_value,
                             dead_skus=dead)


def true_gross_margin(store, revenue: Decimal, as_of: date,
                      period_start: date | None = None) -> Decimal | None:
    """Gross margin using real COGS. None when there is no stock data, so the caller can
    fall back to the purchases approximation rather than report a wrong figure."""
    if not store.has_stock_data() or revenue <= 0:
        return None
    cogs = position(store, as_of, period_start).cogs_period
    return _d((revenue - cogs) / revenue * 100)


def cash_conversion_cycle(store, as_of: date, period_start: date | None = None) -> dict:
    """DIO + DSO − DPO: how many days cash is locked up between paying for goods and
    collecting for them. The single most useful working-capital number for an SME, and it
    needs inventory, receivables and payables together — which is why it lives here."""
    period_start = period_start or as_of.replace(day=1)
    inv = position(store, as_of, period_start)
    days = max(1, (as_of - period_start).days + 1)

    receivables = sum((i.outstanding for i in store.invoices(unpaid_only=True)), Decimal("0"))
    sales = sum((t.amount for t in store.transactions(start=period_start, end=as_of,
                                                      direction="in")), Decimal("0"))

    dio = inv.days_inventory
    dso = _d(receivables / sales * days) if sales > 0 else None
    # Payables are not tracked as a separate ledger (we see cash leaving, not bills owed),
    # so DPO is genuinely unknown. Reporting None is honest; inventing it would flatter the
    # cycle, and a too-short cash cycle is exactly the error that bankrupts a business.
    dpo = None
    cycle = None if dio is None or dso is None else _d(dio + dso)
    return {"days_inventory": dio, "days_sales_outstanding": dso,
            "days_payables_outstanding": dpo, "cash_conversion_days": cycle,
            "note": ("payables are not tracked as a separate ledger, so DPO is excluded "
                     "and the cycle shown is DIO + DSO — a conservative (longer) figure")}
