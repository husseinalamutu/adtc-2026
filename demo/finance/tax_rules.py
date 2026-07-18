"""Citeable Nigeria-2025 tax verdicts, computed from the verified fact base.

Reads the SAME grep-verified facts file the training data was generated from
(data/seeds/nigeria_tax_facts.json) — one source of truth for weights, module, and demo.
Numbers are parsed from the fact values (never hardcoded here), so updating the facts file
updates the module. Every verdict carries its citations for the UI to display.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_DEFAULT_FACTS = Path(__file__).resolve().parents[2] / "data" / "seeds" / "nigeria_tax_facts.json"
TWO_PLACES = Decimal("0.01")


def _pct(value: str) -> Decimal:
    """'7.5%' -> Decimal('0.075')"""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", value)
    if not m:
        raise ValueError(f"no percentage in fact value: {value!r}")
    return Decimal(m.group(1)) / 100


def _ngn(value: str) -> Decimal:
    """'NGN 100,000,000 (₦100 million) ...' -> Decimal('100000000')"""
    m = re.search(r"([\d,]{7,})", value)
    if not m:
        raise ValueError(f"no NGN amount in fact value: {value!r}")
    return Decimal(m.group(1).replace(",", ""))


@dataclass(frozen=True)
class Verdict:
    verdict: str
    cites: tuple[str, ...]


class TaxRules:
    def __init__(self, facts_path: Path = _DEFAULT_FACTS):
        self._facts = json.loads(Path(facts_path).read_text())
        cit = self._facts["companies_income_tax"]
        self.vat_rate = _pct(self._facts["value_added_tax"]["standard_rate"]["value"])
        self.cit_standard = _pct(cit["standard_company_rate"]["value"])
        self.cit_small = _pct(cit["small_company_rate"]["value"])
        self.dev_levy_rate = _pct(self._facts["development_levy"]["rate"]["value"])
        self.small_turnover_max = _ngn(cit["small_company_definition"]["turnover_threshold"]["value"])
        self.small_assets_max = _ngn(cit["small_company_definition"]["fixed_assets_threshold"]["value"])

    def _cite(self, *paths: str) -> tuple[str, ...]:
        out = []
        for path in paths:
            node = self._facts
            for part in path.split("."):
                node = node[part]
            out.append(node.get("cite") or node.get("note") or path)
        return tuple(out)

    def vat_quote(self, subtotal) -> dict:
        """Deterministic VAT line for a quote/invoice."""
        sub = Decimal(str(subtotal)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        vat = (sub * self.vat_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        return {"subtotal": sub, "vat_rate": self.vat_rate, "vat": vat, "total": sub + vat}

    def small_company_assessment(self, turnover, fixed_assets,
                                 professional_services: bool) -> Verdict:
        """Small-company status + the CIT / Dev-Levy consequences, with citations.
        Mirrors NTA 2025: BOTH thresholds met AND not professional services -> small."""
        t, a = Decimal(str(turnover)), Decimal(str(fixed_assets))
        if professional_services:
            return Verdict(
                f"NOT a small company (professional-services exclusion, regardless of size): "
                f"CIT {self.cit_standard:.0%}, Development Levy {self.dev_levy_rate:.0%} applies.",
                self._cite("companies_income_tax.small_company_definition.professional_services_exclusion"),
            )
        if t <= self.small_turnover_max and a <= self.small_assets_max:
            return Verdict(
                f"Small company (turnover {t:,.0f} <= {self.small_turnover_max:,.0f} AND fixed assets "
                f"{a:,.0f} <= {self.small_assets_max:,.0f}): CIT {self.cit_small:.0%}; exempt from the "
                f"Development Levy and CGT.",
                self._cite("companies_income_tax.small_company_rate",
                           "development_levy.exemptions"),
            )
        reasons = []
        if t > self.small_turnover_max:
            reasons.append(f"turnover {t:,.0f} exceeds {self.small_turnover_max:,.0f}")
        if a > self.small_assets_max:
            reasons.append(f"fixed assets {a:,.0f} exceed {self.small_assets_max:,.0f}")
        return Verdict(
            f"NOT a small company ({'; '.join(reasons)}): CIT {self.cit_standard:.0%}, "
            f"Development Levy {self.dev_levy_rate:.0%} on assessable profits.",
            self._cite("companies_income_tax.standard_company_rate", "development_levy.rate"),
        )
