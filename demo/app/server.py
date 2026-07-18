#!/usr/bin/env python3
"""ADTC SME Copilot — demo app server (stdlib only, fully offline).

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
from decimal import Decimal
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))  # demo/ -> import finance
from finance import Invoice, TaxRules, allocate_lump_sum, parse_statement, reconcile_exact

LLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"
APP_PORT = 8090
RULES = TaxRules()

SYSTEM = (
    "You are the ADTC SME Copilot, an offline back-office assistant for African small "
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


ROUTES = {"/api/reconcile": do_reconcile, "/api/tax": do_tax, "/api/quote": do_quote}


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
    print(f"ADTC SME Copilot demo -> http://127.0.0.1:{APP_PORT}  "
          f"(narrative via llama-server on :8080 — optional)", flush=True)
    HTTPServer(("127.0.0.1", APP_PORT), Handler).serve_forever()
