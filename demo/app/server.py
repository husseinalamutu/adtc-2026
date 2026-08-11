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

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from decimal import Decimal
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))  # demo/ -> import finance
from finance import (Invoice, Store, TaxRules, allocate_lump_sum, i18n, parse_statement,
                     reconcile_exact, sample_data)
from finance.advisor import recommend
from finance.analytics import business_health
from finance.anomalies import as_ground_truth as anomalies_text
from finance.anomalies import detect
from finance.forecast import project
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


def _dec(x) -> Decimal:
    return Decimal(str(x))


# ---- task handlers: module first, narrative second ----

def do_reconcile(p: dict) -> dict:
    invoices = [Invoice(i["id"].strip(), _dec(i["amount"])) for i in p["invoices"] if i.get("id")]
    currency = p.get("currency", "NGN")
    if p.get("mode") == "lump":
        alloc = allocate_lump_sum(_dec(p["lump_amount"]), invoices)
        asked = f"A customer paid {currency} {_dec(p['lump_amount']):,} covering: " + \
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
    items = [(i["desc"], int(i["qty"]), _dec(i["unit_price"])) for i in p["items"] if i.get("desc")]
    currency = p.get("currency", "NGN")
    subtotal = sum((q * u for _, q, u in items), Decimal("0"))
    q = RULES.vat_quote(subtotal)
    lines = "\n".join(f"{d}: {n} x {currency} {u:,} = {currency} {n*u:,}" for d, n, u in items)
    verified = (f"{lines}\nSubtotal: {currency} {q['subtotal']:,}\n"
                f"VAT ({q['vat_rate']:.1%}): {currency} {q['vat']:,}\n"
                f"TOTAL: {currency} {q['total']:,}")
    return {"verified": verified,
            "narrative": _narrate("Draft a short, polite customer quote from these figures. "
                                  "Keep the line labels exactly as given (Subtotal, VAT, TOTAL).",
                                  verified)}


def _business_store() -> Store:
    """The demo's books. Loaded once with the generated sample business so the app has
    something real to reason over; `import_transactions_csv` replaces it with the
    operator's own data."""
    global _STORE
    if _STORE is None:
        _STORE = Store(":memory:")
        sample_data.load_into(_STORE)
    return _STORE


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
    kind = p.get("kind", "health")
    as_of = date.fromisoformat(p.get("as_of") or "2026-06-15")
    obligations = _dec(p["obligations"]) if p.get("obligations") else None
    store = _business_store()
    lang = p.get("lang", "en")

    if kind == "health":
        h = business_health(store, as_of)
        verified = h.as_ground_truth("NGN")
        localised = i18n.render_health(h, lang) if lang != "en" else None
    elif kind == "anomalies":
        items = detect(store)
        verified = anomalies_text(items)
        localised = None
        if lang != "en" and items:
            top = items[0]
            localised = i18n.t("duplicate_payment", lang, currency="NGN",
                               amount=i18n.money(top.amount), name=top.counterparty or "?") \
                if top.kind == "duplicate_payment" else None
    elif kind == "forecast":
        verified, localised = project(store, as_of, committed_obligations=obligations
                                      ).as_ground_truth("NGN"), None
    elif kind == "stock":
        inv = position(store, as_of, as_of.replace(day=1))
        ccc = cash_conversion_cycle(store, as_of)
        extra = ("" if ccc["cash_conversion_days"] is None else
                 f"\nCash conversion cycle: {ccc['cash_conversion_days']:.0f} days "
                 f"({ccc['note']})")
        verified, localised = inv.as_ground_truth("NGN") + extra, None
    else:
        verified, localised = recommend(store, as_of, committed_obligations=obligations
                                        ).as_ground_truth("NGN"), None

    return {"verified": verified, "localised": localised, "lang": lang,
            "languages": [{"code": c, "name": i18n.language_name(c)} for c in i18n.available()],
            "txn_count": len(store.transactions()),
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
