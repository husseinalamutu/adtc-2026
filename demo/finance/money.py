"""Money arithmetic — the single definition every layer shares.

Money is `Decimal`, quantized to two places with ROUND_HALF_UP, everywhere. Defining this
once matters more than it looks: if two layers rounded differently, a figure could disagree
with itself between the ledger and the report, and the whole "computed, never guessed"
guarantee would quietly stop holding.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

TWO = Decimal("0.01")


def d(x) -> Decimal:
    """Any numeric-ish value -> Decimal at 2dp. `str(x)` first, so float inputs never
    smuggle binary-float error in (Decimal(0.1) != Decimal('0.1'))."""
    return Decimal(str(x)).quantize(TWO, rounding=ROUND_HALF_UP)
