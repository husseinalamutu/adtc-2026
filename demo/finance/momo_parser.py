"""Mobile-money statement parser: raw provider text -> structured transactions.

Two input shapes cover what SMEs actually paste:
1. Inline statement excerpts — the format our training data uses:
       "TX001: NGN 45,000; MP93481101: KES 4,500.00"
2. Provider SMS lines (MTN MoMo / M-Pesa style):
       "TXN 8842 | 2026-07-11 | RECEIVED NGN 127,500 from 0803***512 | Bal: 340,000"
       "QGH7X2 Confirmed. Ksh4,500.00 sent to JANE WANJIKU"

Amounts are Decimal (never float). Unparseable lines are skipped, not errors — statements
are messy; the caller sees exactly what was recognized.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

_CURRENCIES = r"NGN|KES|GHS|UGX|TZS|USD|₦|Ksh|KSh|GH₵|USh|TSh"
_AMOUNT = r"(?P<amt>\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)"

# "TX001: NGN 45,000"  /  "MP934: 4,500.00"
_INLINE = re.compile(
    rf"(?P<ref>[A-Z][A-Z0-9-]{{2,}})\s*:\s*(?P<cur>{_CURRENCIES})?\s*{_AMOUNT}"
)
# "RECEIVED NGN 127,500 from X" / "Ksh4,500.00 sent to JANE"
_SMS = re.compile(
    rf"(?:(?P<dir1>received|sent|paid|withdrawn)\s+)?(?P<cur>{_CURRENCIES})\s*{_AMOUNT}"
    r"(?:\s+(?P<dir2>received|sent|paid)\b)?"
    r"(?:\s+(?:from|to)\s+(?P<party>[^|.,;]+?)(?=\s*(?:[|.,;]|$)))?",
    re.IGNORECASE,
)
_SMS_REF = re.compile(r"\b(?:TXN\s+)?(?P<ref>[A-Z0-9]{4,})\b")
_NORMALIZE_CUR = {"₦": "NGN", "Ksh": "KES", "KSh": "KES", "GH₵": "GHS", "USh": "UGX", "TSh": "TZS"}
_OUTFLOW_WORDS = {"sent", "paid", "withdrawn"}


@dataclass(frozen=True)
class Transaction:
    ref: str
    amount: Decimal
    currency: str | None      # None when the excerpt omits it
    direction: str            # "in", "out", or "unknown"
    counterparty: str | None
    raw: str


def _decimal(s: str) -> Decimal:
    return Decimal(s.replace(",", ""))


def _currency(s: str | None) -> str | None:
    return _NORMALIZE_CUR.get(s, s) if s else None


def parse_statement(text: str) -> list[Transaction]:
    """Parse a pasted statement/SMS blob. Segments on newlines and ';'."""
    out: list[Transaction] = []
    for segment in re.split(r"[;\n]+", text):
        segment = segment.strip()
        if not segment:
            continue
        m = _INLINE.search(segment)
        if m:
            out.append(Transaction(
                ref=m.group("ref"), amount=_decimal(m.group("amt")),
                currency=_currency(m.group("cur")), direction="unknown",
                counterparty=None, raw=segment,
            ))
            continue
        m = _SMS.search(segment)
        if m:
            word = (m.group("dir1") or m.group("dir2") or "").lower()
            direction = "out" if word in _OUTFLOW_WORDS else ("in" if word else "unknown")
            ref_m = _SMS_REF.search(segment)
            party = m.group("party")
            out.append(Transaction(
                ref=ref_m.group("ref") if ref_m else "?",
                amount=_decimal(m.group("amt")),
                currency=_currency(m.group("cur")), direction=direction,
                counterparty=party.strip() if party else None, raw=segment,
            ))
    return out
