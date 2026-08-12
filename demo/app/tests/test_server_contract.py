"""Smoke tests for the app server itself.

These exist because the engine tests all passed while the app was completely broken: they
import `finance` directly and never touch `server`, so a deleted function or an unregistered
route was invisible to them. Twice during development an edit removed code that happened to
sit between two markers, and only running the app by hand caught it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

import server


@pytest.fixture(autouse=True)
def fresh_store():
    server._STORE = None
    yield
    server._STORE = None


def test_every_route_resolves_to_a_real_callable():
    """Catches a handler that was deleted or never wired up."""
    assert server.ROUTES, "no routes registered"
    for path, handler in server.ROUTES.items():
        assert callable(handler), f"{path} is not callable"


@pytest.mark.parametrize("name", [
    "_business_store", "do_business", "do_load_sample", "do_upload",
    "do_reconcile", "do_tax", "do_quote", "_ingest_records", "_money",
    "parse_item_lines", "parse_invoice_lines",
])
def test_required_functions_exist(name):
    """A splice-style edit that removes one of these breaks the app at runtime only."""
    assert callable(getattr(server, name, None)), f"server.{name} is missing"


def test_expected_routes_are_registered():
    for path in ("/api/business", "/api/reconcile", "/api/tax", "/api/quote",
                 "/api/upload", "/api/load_sample", "/api/import"):
        assert path in server.ROUTES, f"{path} not registered"


def test_asking_with_no_data_returns_a_prompt_not_a_crash():
    out = server.do_business({"kind": "health"})
    assert out["has_data"] is False and "No transactions loaded" in out["error"]


def test_sample_then_every_scenario_computes():
    server.do_load_sample({})
    for kind in ("health", "anomalies", "forecast", "stock", "actions"):
        out = server.do_business({"kind": kind, "obligations": "4200000"})
        assert out.get("verified"), f"{kind} produced nothing"
        assert not out.get("error"), f"{kind}: {out.get('error')}"


@pytest.mark.parametrize("lang", ["ha", "ig"])
def test_offered_languages_localise_the_health_report(lang):
    """Guards the African-language claim end to end, through the server."""
    server.do_load_sample({})
    out = server.do_business({"kind": "health", "lang": lang})
    assert out.get("localised"), f"{lang} produced no localised output"
    assert "NGN" in out["localised"]


def test_quote_vat_modes_differ_through_the_server():
    excl = server.do_quote({"items_text": "Bags of cement, 10, 8500", "vat_inclusive": False})
    incl = server.do_quote({"items_text": "Bags of cement, 10, 8500", "vat_inclusive": True})
    assert "91,375.00" in excl["verified"]      # VAT added on top
    assert "85,000.00" in incl["verified"]      # VAT extracted, total unchanged
