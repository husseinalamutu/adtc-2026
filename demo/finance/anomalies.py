"""Statistical anomaly detection — find the 20 rows worth a human's attention in 50,000.

The LLM never scans the ledger. This layer reduces the whole transaction history to a
short, ranked candidate list with a computed reason for each; the model only explains
the shortlist. That is what makes the feature possible at all on a 3B model at 2.75 tok/s.

Methods (all deterministic, stdlib only, no training):
  - amount outliers: robust z-score (median/MAD) WITHIN each category, so a large-but-
    normal inventory purchase isn't flagged while a large transport bill is
  - duplicate payments: same counterparty + same amount within a short window
  - supplier price jumps: a counterparty's spend per transaction stepping up vs its own history
  - new large counterparties: first-ever payee, materially above that category's norm

MAD (median absolute deviation) rather than mean/stdev: a single huge outlier inflates
stdev enough to hide itself. The median is unmoved by it.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from statistics import median

# robust z ≈ 0.6745·(x−median)/MAD; 3.5 is the conventional "clear outlier" line
ROBUST_Z_FLAG = Decimal("3.5")
MAD_SCALE = Decimal("0.6745")
DUPLICATE_WINDOW_DAYS = 5
PRICE_JUMP_RATIO = Decimal("1.4")     # +40% vs the counterparty's own median
MIN_HISTORY = 4                        # below this there's no pattern to deviate from
NEW_PAYEE_WARMUP_DAYS = 30             # before this, every payee is "new" — stay quiet
RECURRING_THRESHOLD = 2                # same payee+amount more often than this = standing order


@dataclass(frozen=True)
class Anomaly:
    kind: str                 # duplicate_payment | amount_outlier | price_jump | new_large_payee
    severity: Decimal         # comparable across kinds; higher = look sooner
    txn_date: date
    amount: Decimal
    counterparty: str | None
    category: str | None
    reason: str               # computed, human-readable — the LLM explains THIS, not the data

    def line(self, currency: str = "NGN") -> str:
        who = f" to {self.counterparty}" if self.counterparty else ""
        return f"[{self.kind}] {self.txn_date} {currency} {self.amount:,}{who} — {self.reason}"


def _median(values: list[Decimal]) -> Decimal:
    return Decimal(str(median(values)))


def _mad(values: list[Decimal], med: Decimal) -> Decimal:
    return _median([abs(v - med) for v in values])


def _robust_z(value: Decimal, med: Decimal, mad: Decimal) -> Decimal | None:
    if mad == 0:
        return None                      # no spread: everything identical, nothing to flag
    return MAD_SCALE * (value - med) / mad


def detect(store, limit: int = 20) -> list[Anomaly]:
    """Scan all spending and return the ranked shortlist worth reviewing."""
    txns = [t for t in store.transactions() if t.direction == "out"]
    if not txns:
        return []
    # The business's own typical spend is the yardstick for "material" — a ₦500 repeat
    # is noise for a builders' merchant and would be significant for a kiosk.
    typical = _median([t.amount for t in txns])
    found: list[Anomaly] = []
    found += _amount_outliers(txns)
    found += _duplicate_payments(txns, typical)
    found += _price_jumps(txns)
    found += _new_large_payees(txns)

    # one row can trip several rules — keep its strongest signal only
    best: dict[tuple, Anomaly] = {}
    for a in found:
        key = (a.txn_date, a.amount, a.counterparty, a.kind)
        if key not in best or a.severity > best[key].severity:
            best[key] = a
    return sorted(best.values(), key=lambda a: a.severity, reverse=True)[:limit]


def _amount_outliers(txns) -> list[Anomaly]:
    by_cat: dict[str, list] = {}
    for t in txns:
        by_cat.setdefault(t.category or "Uncategorised", []).append(t)

    out = []
    for cat, rows in by_cat.items():
        if len(rows) < MIN_HISTORY:
            continue
        amounts = [t.amount for t in rows]
        med, mad = _median(amounts), _mad(amounts, _median(amounts))
        for t in rows:
            z = _robust_z(t.amount, med, mad)
            if z is not None and z >= ROBUST_Z_FLAG:
                out.append(Anomaly(
                    kind="amount_outlier", severity=z, txn_date=t.txn_date, amount=t.amount,
                    counterparty=t.counterparty, category=cat,
                    reason=(f"{z:.1f}x the typical spread for {cat} "
                            f"(usual is around NGN {med:,})")))
    return out


def _duplicate_payments(txns, typical: Decimal) -> list[Anomaly]:
    """Repeat payments of the same amount to the same payee within a few days.

    MATERIALITY MATTERS: small recurring costs (airtime, bank charges, a daily fuel run)
    legitimately repeat, and flagging them buries the one duplicate that costs real money.
    We only surface repeats at or above the business's typical transaction size, and rank
    by how much money is actually at risk.
    """
    # A STANDING ARRANGEMENT IS NOT AN ERROR. Rent every month, or a supplier order every
    # week, repeats the same amount to the same payee by design — flagging those buries the
    # real thing. A genuine double payment is a ONE-OFF: the pair appears about twice, close
    # together. Anything that recurs more than that is the business operating normally.
    occurrences: dict[tuple, int] = {}
    for t in txns:
        occurrences[(t.counterparty, t.amount)] = occurrences.get((t.counterparty, t.amount), 0) + 1

    out, seen = [], {}
    for t in sorted(txns, key=lambda t: t.txn_date):
        key = (t.counterparty, t.amount)
        prev = seen.get(key)
        if (prev is not None and 0 <= (t.txn_date - prev).days <= DUPLICATE_WINDOW_DAYS
                and occurrences[key] <= RECURRING_THRESHOLD
                and typical > 0 and t.amount >= typical):
            # near-certain, recoverable error → ranks above statistical suspicions,
            # scaled by the money at risk (capped so one huge row can't swamp the list)
            severity = Decimal("10") + min(t.amount / typical, Decimal("20"))
            out.append(Anomaly(
                kind="duplicate_payment", severity=severity,
                txn_date=t.txn_date, amount=t.amount,
                counterparty=t.counterparty, category=t.category,
                reason=(f"identical amount already paid to the same payee on {prev} "
                        f"({(t.txn_date - prev).days} day(s) earlier) — possible double payment")))
        seen[key] = t.txn_date
    return out


def _price_jumps(txns) -> list[Anomaly]:
    """Compare like with like: the same supplier AND the same line item.

    Grouping only by supplier blends unrelated purchases (a cement order and a pipe
    order) into one median and hides real per-item increases. Each payment is checked
    against the median of that group's PRIOR payments (expanding window), so a jump is
    caught whenever it happens — not only on the most recent row.
    """
    by_item: dict[tuple[str, str], list] = {}
    for t in txns:
        if t.counterparty:
            by_item.setdefault((t.counterparty, (t.description or "").strip().lower()), []).append(t)

    out = []
    for (party, _item), rows in by_item.items():
        rows.sort(key=lambda t: t.txn_date)
        strongest: Anomaly | None = None
        for i, t in enumerate(rows):
            history = [r.amount for r in rows[:i]]
            if len(history) < MIN_HISTORY:
                continue
            med = _median(history)
            if med > 0 and t.amount / med >= PRICE_JUMP_RATIO:
                ratio = (t.amount / med - 1) * 100
                cand = Anomaly(
                    kind="price_jump", severity=Decimal("5") + Decimal(str(ratio)) / 100,
                    txn_date=t.txn_date, amount=t.amount, counterparty=party,
                    category=t.category,
                    reason=(f"{ratio:.0f}% above what you usually pay this supplier for "
                            f"'{t.description}' (usual NGN {med:,}) — check the invoice "
                            f"or renegotiate"))
                if strongest is None or cand.severity > strongest.severity:
                    strongest = cand
        if strongest:
            out.append(strongest)
    return out


def _new_large_payees(txns) -> list[Anomaly]:
    """First-ever payment to a payee, materially above normal.

    COLD START: at the very beginning of a ledger every payee is 'new' — flagging them
    all is noise the operator will learn to ignore. We stay quiet until the books have
    enough history for 'new' to actually mean something.
    """
    ordered = sorted(txns, key=lambda t: t.txn_date)
    first_seen: dict[str, date] = {}
    for t in ordered:
        if t.counterparty and t.counterparty not in first_seen:
            first_seen[t.counterparty] = t.txn_date

    amounts = [t.amount for t in txns]
    if len(amounts) < MIN_HISTORY:
        return []
    ledger_start = ordered[0].txn_date
    warm = ledger_start + timedelta(days=NEW_PAYEE_WARMUP_DAYS)
    med = _median(amounts)
    out = []
    for t in txns:
        if (t.counterparty and first_seen.get(t.counterparty) == t.txn_date
                and t.txn_date >= warm
                and med > 0 and t.amount >= med * 3):
            out.append(Anomaly(
                kind="new_large_payee", severity=Decimal("4"), txn_date=t.txn_date,
                amount=t.amount, counterparty=t.counterparty, category=t.category,
                reason=(f"first payment ever to this payee, and {t.amount / med:.1f}x "
                        f"the typical transaction — confirm it is legitimate")))
    return out


def as_ground_truth(anomalies: list[Anomaly], currency: str = "NGN") -> str:
    """Deterministic summary handed to the LLM (which explains, never re-ranks)."""
    if not anomalies:
        return "No unusual transactions detected."
    head = f"{len(anomalies)} transaction(s) flagged for review, most significant first:"
    return head + "\n" + "\n".join(f"{i}. {a.line(currency)}"
                                   for i, a in enumerate(anomalies, 1))
