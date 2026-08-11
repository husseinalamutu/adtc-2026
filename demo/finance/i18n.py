"""Multilingual rendering for computed figures — Hausa, Igbo, Yoruba, English.

WHY TEMPLATES AND NOT THE MODEL: every figure the operator sees is computed by this
module, so presenting it in another language is a FORMATTING problem, not a generation
problem. Rendering deterministically means (a) a wrong number is impossible, and (b) the
model's limited capacity stays spent on English financial reasoning, which is what the
challenge audits. Adding a language costs zero ADTC score and zero model capacity.

⚠️ TRANSLATION STATUS — READ BEFORE CLAIMING THE AFRICAN-LANGUAGE BONUS ⚠️
Only `en` is verified. The `ha`, `ig` and `yo` catalogues below are UNVERIFIED DRAFTS
placed here as scaffolding for a native speaker to correct — they must not be shown to
judges or users until reviewed. Financial and tax vocabulary is exactly where a
non-native draft goes wrong, and a confident wrong translation is worse than English.
Each catalogue carries `_reviewed: False` until a native reviewer flips it, and
`is_reviewed()` gates the app so unreviewed strings cannot reach a user by accident.

Numbers, currency and dates are NEVER translated — they are rendered by the same Decimal
formatting in every language, so the figures are identical across locales by construction.
"""
from __future__ import annotations

from decimal import Decimal

# --- catalogues -------------------------------------------------------------
# Keys are stable identifiers; values are format strings taking named fields.

EN = {
    "_reviewed": True,
    "_name": "English",
    "revenue": "Revenue: {currency} {amount}",
    "expenses": "Expenses: {currency} {amount}",
    "net": "Net: {currency} {amount}",
    "cash_position": "Cash on hand: {currency} {amount}",
    "receivables": "Owed to you: {currency} {amount} (overdue: {currency} {overdue})",
    "margin": "Gross margin: {pct}%",
    "up_pct": "up {pct}% on last month",
    "down_pct": "down {pct}% on last month",
    "chase_customer": "Chase {name} — {currency} {amount}, {days} days overdue",
    "duplicate_payment": "Possible double payment of {currency} {amount} to {name}",
    "shortfall": "Projected shortfall next month: {currency} {amount}",
    "covered": "Projected to cover next month's obligations",
    "no_issues": "Nothing unusual found in your transactions.",
    "confirm_professional": "Confirm specifics with FIRS or a licensed accountant.",
}

# ⚠️ UNVERIFIED DRAFT — native Hausa review required before use.
HA = {
    "_reviewed": False,
    "_name": "Hausa",
    "revenue": "Kudin shiga: {currency} {amount}",
    "expenses": "Kashe kudi: {currency} {amount}",
    "net": "Ribar da ta rage: {currency} {amount}",
    "cash_position": "Kudin da ke hannu: {currency} {amount}",
    "receivables": "Ana bin ka: {currency} {amount} (wanda ya wuce lokaci: {currency} {overdue})",
    "margin": "Ribar kaso: {pct}%",
    "up_pct": "ya karu da {pct}% fiye da watan da ya gabata",
    "down_pct": "ya ragu da {pct}% daga watan da ya gabata",
    "chase_customer": "Nemi biyan kudi daga {name} — {currency} {amount}, kwanaki {days} sun wuce",
    "duplicate_payment": "Wataƙila an biya {currency} {amount} sau biyu ga {name}",
    "shortfall": "Ana hasashen ƙarancin kudi wata mai zuwa: {currency} {amount}",
    "covered": "Ana hasashen kudin zai isa wata mai zuwa",
    "no_issues": "Ba a sami wani abu na banmamaki ba a cikin ma'amalolinka.",
    "confirm_professional": "Ka tabbatar da cikakken bayani daga FIRS ko akanta mai lasisi.",
}

# ⚠️ UNVERIFIED DRAFT — native Igbo review required before use.
IG = {
    "_reviewed": False,
    "_name": "Igbo",
    "revenue": "Ego batara: {currency} {amount}",
    "expenses": "Ego emefuru: {currency} {amount}",
    "net": "Uru fọdụrụ: {currency} {amount}",
    "cash_position": "Ego dị n'aka: {currency} {amount}",
    "receivables": "Ego a ji gị: {currency} {amount} (gafeela oge: {currency} {overdue})",
    "margin": "Pasent uru: {pct}%",
    "up_pct": "rịgoro {pct}% karịa ọnwa gara aga",
    "down_pct": "dara {pct}% site n'ọnwa gara aga",
    "chase_customer": "Chọọ ụgwọ n'aka {name} — {currency} {amount}, ụbọchị {days} gafeela",
    "duplicate_payment": "O nwere ike ị kwụrụ {currency} {amount} ugboro abụọ nye {name}",
    "shortfall": "A na-atụ anya ụkọ ego n'ọnwa na-abịa: {currency} {amount}",
    "covered": "A na-atụ anya na ego ga-ezu maka ọnwa na-abịa",
    "no_issues": "Ọ dịghị ihe ijuanya dị na azụmahịa gị.",
    "confirm_professional": "Gakwuru FIRS ma ọ bụ onye ọkachamara n'ọgụgụ ego maka nkwenye.",
}

# ⚠️ UNVERIFIED DRAFT — native Yoruba review required before use.
YO = {
    "_reviewed": False,
    "_name": "Yoruba",
    "revenue": "Owó tí ó wọlé: {currency} {amount}",
    "expenses": "Owó tí a ná: {currency} {amount}",
    "net": "Èrè tí ó kù: {currency} {amount}",
    "cash_position": "Owó tí ó wà lọ́wọ́: {currency} {amount}",
    "receivables": "Owó tí wọ́n jẹ ọ́: {currency} {amount} (tí ó ti pé: {currency} {overdue})",
    "margin": "Ìpín èrè: {pct}%",
    "up_pct": "ó gòkè ní {pct}% ju oṣù tó kọjá",
    "down_pct": "ó dínkù ní {pct}% ju oṣù tó kọjá",
    "chase_customer": "Béèrè owó lọ́wọ́ {name} — {currency} {amount}, ọjọ́ {days} ti kọjá",
    "duplicate_payment": "Ó ṣeé ṣe kí a ti san {currency} {amount} lẹ́ẹ̀mejì fún {name}",
    "shortfall": "Àìtó owó tí a rí tẹ́lẹ̀ fún oṣù tó ń bọ̀: {currency} {amount}",
    "covered": "A rí i pé owó yóò tó fún oṣù tó ń bọ̀",
    "no_issues": "A kò rí ohunkóhun tí kò tọ́ nínú ìṣòwò rẹ.",
    "confirm_professional": "Jẹ́rìí sí i pẹ̀lú FIRS tàbí akáǹtì tí ó ní ìwé àṣẹ.",
}

CATALOGUES = {"en": EN, "ha": HA, "ig": IG, "yo": YO}


def available(include_unreviewed: bool = False) -> list[str]:
    """Language codes the app may offer. Unreviewed drafts are hidden by default."""
    return [code for code, cat in CATALOGUES.items()
            if include_unreviewed or cat["_reviewed"]]


def is_reviewed(lang: str) -> bool:
    return bool(CATALOGUES.get(lang, EN)["_reviewed"])


def language_name(lang: str) -> str:
    return str(CATALOGUES.get(lang, EN)["_name"])


def t(key: str, lang: str = "en", **fields) -> str:
    """Render one figure line. Falls back to English for a missing key or language, so a
    gap in a draft catalogue degrades to correct English rather than to a crash."""
    cat = CATALOGUES.get(lang, EN)
    template = cat.get(key) or EN.get(key)
    if template is None:
        raise KeyError(f"unknown i18n key: {key}")
    return str(template).format(**fields)


def money(amount: Decimal, currency: str = "NGN") -> str:
    """Identical in every language — figures must never vary by locale."""
    return f"{amount:,.2f}" if not isinstance(amount, str) else amount


def render_health(health, lang: str = "en", currency: str = "NGN") -> str:
    """A BusinessHealth rendered in `lang`. Numbers come from the engine unchanged."""
    lines = [t("revenue", lang, currency=currency, amount=money(health.period.revenue))]
    if health.revenue_change_pct is not None:
        key = "up_pct" if health.revenue_change_pct > 0 else "down_pct"
        lines[-1] += " — " + t(key, lang, pct=f"{abs(health.revenue_change_pct):.1f}")
    lines.append(t("expenses", lang, currency=currency, amount=money(health.period.expenses)))
    lines.append(t("net", lang, currency=currency, amount=money(health.period.net)))
    if health.period.gross_margin_pct is not None:
        lines.append(t("margin", lang, pct=f"{health.period.gross_margin_pct:.1f}"))
    lines.append(t("cash_position", lang, currency=currency, amount=money(health.cash_position)))
    lines.append(t("receivables", lang, currency=currency,
                   amount=money(health.receivables_total),
                   overdue=money(health.receivables_overdue)))
    return "\n".join(lines)
