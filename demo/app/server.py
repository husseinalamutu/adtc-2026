#!/usr/bin/env python3
"""ALAMZ TECH SME Copilot — demo app server (stdlib only, fully offline).

Bridges the two halves of the pairing:
  - narrative:  llama-server's OpenAI-compatible API (the fine-tuned GGUF)
  - numbers:    demo/finance (parser, ledger, tax rules) — computed, then INJECTED into the
                model's prompt as ground truth it must not alter

If llama-server isn't running the app still works: verified figures render without the
narrative (the math never depends on the model).

Run: bash demo/app/run_demo.sh   (or: python3 demo/app/server.py)
"""
from __future__ import annotations

import base64
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from decimal import Decimal
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))  # demo/ -> import finance
from finance import (Invoice, Store, TaxRules, Txn, allocate_lump_sum, i18n, parse_statement,
                     reconcile_exact, sample_data)
from finance.advisor import recommend
from finance.analytics import business_health
from finance.anomalies import as_ground_truth as anomalies_text
from finance.anomalies import detect
from finance.forecast import project
from finance.spreadsheet import read_table, rows_to_dicts
from finance.inventory import cash_conversion_cycle, position

LLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"
APP_PORT = 8090
RULES = TaxRules()

SYSTEM = (
    "You are the ALAMZ TECH SME Copilot, an offline back-office assistant for African small "
    "businesses. When VERIFIED FIGURES are provided, use ONLY those numbers — restate them "
    "exactly; never recompute or alter them. Be concise and plain-spoken."
)


def _narrate(user_msg: str, verified: str | None) -> str | None:
    """Ask the model to phrase the answer around the module's figures. None if server down."""
    content = user_msg if not verified else (
        f"{user_msg}\n\nVERIFIED FIGURES (computed by the accounting module — use exactly "
        f"these):\n{verified}")
    body = json.dumps({
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": content}],
        "temperature": 0.2, "max_tokens": 220,
    }).encode()
    req = urllib.request.Request(LLAMA_URL, body, {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, OSError, KeyError, TimeoutError):
        return None


# Operators type money the way they say it: "10,500", "N10,500", "₦10,500.00".
# A naive split(",") mangles that, so we FIRST strip thousands separators, THEN split.
#
# A thousands separator is a comma followed IMMEDIATELY by exactly three digits
# ("10,500"). A field separator is a comma followed by a space ("cement, 10"). Refusing to
# treat ", 500" as a thousands separator is deliberate: "Item, 100, 500" would otherwise be
# silently misread, and a silently wrong total on someone's invoice is the worst failure
# this app can have. Fields are taken from the RIGHT (price last, qty second-last) so a
# description may itself contain commas: "Cement, bagged (50kg), 10, 8500".
_THOUSANDS = re.compile(r",(?=\d{3}(?:\D|$))")
_CURRENCY = re.compile(r"(?:NGN|₦|N)\s*", re.IGNORECASE)


def _money(text) -> Decimal:
    """'₦10,500.00' / 'N10500' / '10,500' -> Decimal. Raises on genuine junk."""
    cleaned = _CURRENCY.sub("", _THOUSANDS.sub("", str(text))).strip()
    if not re.fullmatch(r"\d+(?:\.\d+)?", cleaned):
        raise ValueError(f"not a valid amount: {text!r}")
    return Decimal(cleaned)


def _split_fields(raw: str, n: int) -> list[str]:
    """Strip thousands separators, then split into exactly n fields from the right."""
    parts = [p.strip() for p in _THOUSANDS.sub("", raw).split(",")]
    if len(parts) < n:
        return []
    # everything before the last n-1 fields belongs to the description/id
    head = ", ".join(parts[: len(parts) - (n - 1)]).strip()
    return [head, *parts[len(parts) - (n - 1):]]


def parse_item_lines(text: str) -> list[dict]:
    """Parse 'Bags of cement, 10, ₦10,500' lines. Reports the offending line on failure so
    the operator fixes their input rather than seeing a silently wrong total."""
    out = []
    for raw in (text or "").splitlines():
        if not raw.strip():
            continue
        fields = _split_fields(raw, 3)
        if not fields or not fields[0]:
            raise ValueError(f"expected 'description, quantity, unit price' — got: {raw.strip()!r}")
        desc, qty, price = fields
        try:
            out.append({"desc": desc, "qty": str(int(_money(qty))), "unit_price": str(_money(price))})
        except (ValueError, ArithmeticError) as e:
            raise ValueError(f"{e} in line: {raw.strip()!r}") from None
    return out


def parse_invoice_lines(text: str) -> list[dict]:
    """Parse 'INV-114, ₦85,000' lines."""
    out = []
    for raw in (text or "").splitlines():
        if not raw.strip():
            continue
        fields = _split_fields(raw, 2)
        if not fields or not fields[0]:
            raise ValueError(f"expected 'invoice id, amount' — got: {raw.strip()!r}")
        inv_id, amount = fields
        try:
            out.append({"id": inv_id, "amount": str(_money(amount))})
        except (ValueError, ArithmeticError) as e:
            raise ValueError(f"{e} in line: {raw.strip()!r}") from None
    return out


def _dec(x) -> Decimal:
    return Decimal(str(x))


# ---- task handlers: module first, narrative second ----

def do_reconcile(p: dict) -> dict:
    raw_inv = p.get("invoices_text")
    entries = parse_invoice_lines(raw_inv) if raw_inv is not None else p.get("invoices", [])
    invoices = [Invoice(i["id"].strip(), _money(i["amount"])) for i in entries if i.get("id")]
    currency = p.get("currency", "NGN")
    if p.get("mode") == "lump":
        alloc = allocate_lump_sum(_money(p["lump_amount"]), invoices)
        asked = f"A customer paid {currency} {_money(p['lump_amount']):,} covering: " + \
                ", ".join(f"{i.invoice_id} ({currency} {i.amount:,})" for i in invoices)
        parsed = []
    else:
        txs = parse_statement(p.get("statement", ""))
        alloc = reconcile_exact(txs, invoices)
        asked = "Reconcile this mobile-money statement against the open invoices."
        parsed = [{"ref": t.ref, "amount": f"{t.amount:,}", "currency": t.currency or currency,
                   "direction": t.direction} for t in txs]
    verified = alloc.summary(currency)
    return {"verified": verified, "parsed_transactions": parsed,
            "narrative": _narrate(asked + " What is settled and what is outstanding?", verified)}


def do_tax(p: dict) -> dict:
    question = p.get("question", "").strip()
    verified = cites = None
    if p.get("turnover"):
        v = RULES.small_company_assessment(
            _dec(p["turnover"]), _dec(p.get("fixed_assets") or 0),
            professional_services=bool(p.get("professional_services")))
        verified, cites = v.verdict, list(v.cites)
    return {"verified": verified, "cites": cites,
            "narrative": _narrate(question or "Assess my company's Nigerian tax position.",
                                  verified)}


def do_quote(p: dict) -> dict:
    """Build a quote, honouring whether the operator's prices already include VAT.

    Restored 2026-08-12 with an explicit VAT mode. The earlier version always ADDED 7.5%,
    which is wrong for the goods Nigerian retailers trade most — cement, petrol and other
    manufacturer- or regulator-priced lines are quoted VAT-inclusive, so adding again
    overcharges the customer and overstates output VAT."""
    raw = p.get("items_text")
    entries = parse_item_lines(raw) if raw is not None else p.get("items", [])
    items = [(i["desc"], int(_money(i["qty"])), _money(i["unit_price"]))
             for i in entries if i.get("desc")]
    if not items:
        return {"error": "no items — expected lines like 'Bags of cement, 10, 8500'"}
    currency = p.get("currency", "NGN")
    inclusive = bool(p.get("vat_inclusive"))
    gross_or_net = sum((q * u for _, q, u in items), Decimal("0"))
    q = RULES.vat_quote(gross_or_net, inclusive=inclusive)

    lines = "\n".join(f"{d}: {n} x {currency} {u:,} = {currency} {n * u:,}" for d, n, u in items)
    header = ("Listed prices INCLUDE VAT — VAT extracted, not added."
              if inclusive else "Listed prices EXCLUDE VAT — VAT added on top.")
    verified = (f"{header}\n{lines}\n"
                f"Net of VAT: {currency} {q['subtotal']:,}\n"
                f"VAT ({q['vat_rate']:.1%}): {currency} {q['vat']:,}\n"
                f"TOTAL PAYABLE: {currency} {q['total']:,}")
    return {"verified": verified,
            "narrative": _narrate("Draft a short, polite customer quote from these figures. "
                                  "Keep the labels exactly as given and do not recompute.",
                                  verified)}


# NOTE (historical): the quote feature was briefly removed on 2026-08-12. In Nigeria most
# manufacturer-priced goods — cement, petrol, regulated items — are quoted VAT-INCLUSIVE, so a
# tool that always adds 7.5% on top would overcharge the customer and misstate the retailer's
# VAT. Handling that correctly needs an inclusive/exclusive distinction per line item; until
# that exists, shipping the naive version would give confidently wrong figures on exactly the
# goods our users trade most. `TaxRules.vat_quote` remains in the engine (tested) for the
# tax tab's arithmetic.

# Real exports don't use our column names. Map the common variants once, here.
_COLS = {
    "date": ("date", "txn_date", "transaction_date", "value_date", "posted", "day"),
    "description": ("description", "narration", "details", "particulars", "memo", "remarks"),
    "amount": ("amount", "value", "credit_debit", "naira", "ngn"),
    "category": ("category", "type", "class", "account"),
    "counterparty": ("counterparty", "customer", "supplier", "payee", "name", "party"),
    "ref": ("ref", "reference", "txn_id", "transaction_id", "id"),
}


def _pick(record: dict, field: str) -> str:
    for key in _COLS[field]:
        if record.get(key, "").strip():
            return record[key].strip()
    return ""


def _ingest_records(store, records: list[dict]) -> tuple[int, int]:
    """Turn parsed rows into transactions. Rows whose date or amount can't be read are
    SKIPPED and counted, never guessed — a fabricated figure in someone's books is worse
    than a smaller import."""
    rows, skipped = [], 0
    for rec in records:
        raw_date, raw_amount = _pick(rec, "date"), _pick(rec, "amount")
        if not raw_date or not raw_amount:
            skipped += 1
            continue
        # Exports write money-out as "-420,000" or "(420,000)". _money() accepts only
        # unsigned figures on purpose, so read the sign first and hand it the magnitude.
        trimmed = raw_amount.strip()
        negative = trimmed.startswith("-") or (trimmed.startswith("(") and trimmed.endswith(")"))
        try:
            txn_date = _parse_date(raw_date)
            amount = _money(trimmed.lstrip("+-").strip("()"))
        except (ValueError, ArithmeticError):
            skipped += 1
            continue
        direction = "out" if negative else "in"
        rows.append(Txn(_pick(rec, "ref") or f"IMP{len(rows) + 1:05d}", txn_date,
                        _pick(rec, "description") or "(no description)", amount,
                        direction, _pick(rec, "category") or None,
                        _pick(rec, "counterparty") or None))
    return (store.add_transactions(rows) if rows else 0), skipped


def _parse_date(text: str) -> date:
    text = text.strip().split(" ")[0]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y",
                "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognised date: {text!r}")


def do_upload(p: dict) -> dict:
    """Accept a real file (CSV / Excel) rather than pasted text — SMEs keep books in
    spreadsheets, and asking them to copy CSV out of Excel is the wrong front door.
    The file is decoded and parsed in-process; nothing is written to disk or sent anywhere."""
    filename = p.get("filename", "")
    try:
        raw = base64.b64decode(p.get("content_b64", ""), validate=True)
    except Exception:
        return {"error": "could not read the uploaded file"}
    if not raw:
        return {"error": "the file is empty"}
    try:
        records = rows_to_dicts(read_table(filename, raw))
    except ValueError as e:
        return {"error": str(e)}
    if not records:
        return {"error": f"no rows found in {filename!r} — is the first row a header?"}
    store = _business_store()
    added, skipped = _ingest_records(store, records)
    if not added:
        return {"error": "no usable transactions found. Expected columns like "
                         "date, description, amount (category, counterparty, ref optional). "
                         f"Found: {', '.join(list(records[0])[:8])}"}
    n = len(store.transactions())
    rng = store.date_range()
    span = f" covering {rng[0]} to {rng[1]}" if rng else ""
    note = f" ({skipped} row(s) skipped — unreadable date or amount)" if skipped else ""
    return {"txn_count": n, "has_data": True, "imported": added,
            "message": f"Loaded {added} transactions from {filename}{span}.{note}"}


def _localise_anomalies(items, lang: str) -> str | None:
    """Only reviewed vocabulary is used. Anomaly kinds without a reviewed string are
    omitted rather than machine-translated — a half-invented Hausa sentence in front of a
    judge is worse than showing the English block."""
    if not items:
        return i18n.t("no_issues", lang)
    lines = [i18n.t("duplicate_payment", lang, currency="NGN",
                    amount=i18n.money(a.amount), name=a.counterparty or "?")
             for a in items if a.kind == "duplicate_payment"]
    return "\n".join(lines) or None


def _localise_forecast(f, lang: str) -> str | None:
    if f.insufficient_history:
        return None
    if f.shortfall > 0:
        return i18n.t("shortfall", lang, currency="NGN", amount=i18n.money(f.shortfall))
    return i18n.t("covered", lang)


def _localise_plan(plan, lang: str) -> str | None:
    lines = []
    for r in plan.recommendations:
        if r.action.startswith("Chase "):
            name = r.action.replace("Chase ", "").replace(" for payment", "")
            days = "".join(ch for ch in r.evidence if ch.isdigit()) or "0"
            lines.append(i18n.t("chase_customer", lang, name=name, currency="NGN",
                                amount=i18n.money(r.impact), days=days))
    return "\n".join(lines) or None


def _business_store() -> Store:
    """The operator's books — EMPTY until they import their own data.

    Deliberately not pre-loaded with the sample business: an app that says "your books"
    while showing generated demo figures is lying to the user, and a walkthrough is far more
    convincing when the presenter uploads real data and the numbers appear. The sample
    business is still available, but only on explicit request (`/api/load_sample`)."""
    global _STORE
    if _STORE is None:
        _STORE = Store(":memory:")
    return _STORE


def do_load_sample(p: dict) -> dict:
    """Explicitly load the generated sample business — for anyone who wants a quick look
    without typing data. Never loaded implicitly."""
    store = _business_store()
    sample_data.load_into(store)
    n = len(store.transactions())
    return {"txn_count": n, "has_data": n > 0,
            "message": f"Sample business loaded — {n} transactions (a Lagos "
                       f"building-materials retailer, 6 months of trading)."}


_STORE: Store | None = None
BUSINESS_ASKS = {
    "health": "What happened to my business this month?",
    "anomalies": "Is anything unusual in my transactions?",
    "forecast": "Will I have enough cash next month?",
    "actions": "What should I do about it?",
    "stock": "How much of my cash is tied up in stock?",
}


def do_business(p: dict) -> dict:
    """The 'Ask My Business' scenarios — engine computes, model explains."""
    store_check = _business_store()
    if not store_check.transactions():
        return {"verified": None, "narrative": None, "txn_count": 0, "has_data": False,
                "error": "No transactions loaded yet. Paste your CSV above (or load the "
                         "sample business) and the engine will compute from your own books."}
    kind = p.get("kind", "health")
    as_of = date.fromisoformat(p.get("as_of") or "2026-06-15")
    obligations = _dec(p["obligations"]) if p.get("obligations") else None
    store = _business_store()
    lang = p.get("lang", "en")
    localised = None
    if kind == "health":
        h = business_health(store, as_of)
        verified = h.as_ground_truth("NGN")
        if lang != "en":
            localised = i18n.render_health(h, lang)
    elif kind == "anomalies":
        items = detect(store)
        verified = anomalies_text(items)
        if lang != "en":
            localised = _localise_anomalies(items, lang)
    elif kind == "forecast":
        f = project(store, as_of, committed_obligations=obligations)
        verified = f.as_ground_truth("NGN")
        if lang != "en":
            localised = _localise_forecast(f, lang)
    elif kind == "stock":
        inv = position(store, as_of, as_of.replace(day=1))
        ccc = cash_conversion_cycle(store, as_of)
        extra = ("" if ccc["cash_conversion_days"] is None else
                 f"\nCash conversion cycle: {ccc['cash_conversion_days']:.0f} days "
                 f"({ccc['note']})")
        verified = inv.as_ground_truth("NGN") + extra
    else:
        plan = recommend(store, as_of, committed_obligations=obligations)
        verified = plan.as_ground_truth("NGN")
        if lang != "en":
            localised = _localise_plan(plan, lang)

    return {"verified": verified, "localised": localised, "lang": lang,
            "languages": [{"code": c, "name": i18n.language_name(c)} for c in i18n.available()],
            "txn_count": len(store.transactions()), "has_data": True,
            "narrative": _narrate(BUSINESS_ASKS.get(kind, BUSINESS_ASKS["health"]), verified)}


def do_import(p: dict) -> dict:
    """Replace the demo books with the operator's own pasted CSV."""
    global _STORE
    import csv as _csv
    import io
    text = (p.get("csv") or "").strip()
    if not text:
        raise ValueError("no CSV content provided")
    rows = list(_csv.DictReader(io.StringIO(text)))
    if not rows:
        raise ValueError("CSV had a header but no data rows")

    tmp = Path(APP_DIR / "_uploaded.csv")
    tmp.write_text(text, encoding="utf-8")
    _STORE = Store(":memory:")
    n = _STORE.import_transactions_csv(tmp)
    tmp.unlink(missing_ok=True)
    rng = _STORE.date_range()
    return {"verified": f"Imported {n} transactions"
                        + (f" covering {rng[0]} to {rng[1]}." if rng else "."),
            "narrative": None, "txn_count": n}


ROUTES = {"/api/reconcile": do_reconcile, "/api/tax": do_tax, "/api/quote": do_quote,
          "/api/load_sample": do_load_sample, "/api/upload": do_upload,
          "/api/business": do_business, "/api/import": do_import}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(APP_DIR), **kw)

    def do_POST(self):
        handler = ROUTES.get(self.path)
        if not handler:
            self.send_error(404); return
        try:
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            result = handler(payload)
            body = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:  # demo server: surface the error to the UI, don't die
            body = json.dumps({"error": str(e)}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[app] {args[0]} {args[1]}", flush=True)


if __name__ == "__main__":
    print(f"ALAMZ TECH SME Copilot demo -> http://127.0.0.1:{APP_PORT}  "
          f"(narrative via llama-server on :8080 — optional)", flush=True)
    HTTPServer(("127.0.0.1", APP_PORT), Handler).serve_forever()
