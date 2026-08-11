"""i18n tests — the guarantees that make multilingual output safe to ship.

The critical property: FIGURES ARE IDENTICAL ACROSS LANGUAGES. If a Hausa report could
show a different number than the English one, the whole "computed, never guessed" claim
collapses. These tests assert that structurally rather than by inspection.
"""
import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from finance import Store, sample_data
from finance.analytics import business_health
from finance import i18n


@pytest.fixture
def health():
    s = Store(":memory:")
    sample_data.load_into(s)
    h = business_health(s, date(2026, 6, 15))
    s.close()
    return h


def _numbers(text: str) -> list[str]:
    return re.findall(r"[\d,]+\.\d{2}|\d+\.\d(?=%)", text)


def test_every_language_renders_identical_figures(health):
    """The whole point: language changes the words, never the money."""
    baseline = _numbers(i18n.render_health(health, "en"))
    assert baseline, "expected figures in the English rendering"
    for lang in ("ha", "ig", "yo"):
        assert _numbers(i18n.render_health(health, lang)) == baseline, \
            f"{lang} rendered different figures than English"


def test_unreviewed_languages_are_hidden_by_default():
    """Draft translations must not reach a user until a native speaker signs off."""
    assert i18n.available() == ["en"]
    assert set(i18n.available(include_unreviewed=True)) == {"en", "ha", "ig", "yo"}
    assert i18n.is_reviewed("en")
    for lang in ("ha", "ig", "yo"):
        assert not i18n.is_reviewed(lang), f"{lang} must stay unreviewed until verified"


def test_all_catalogues_cover_the_same_keys():
    """A missing key in a draft would silently fall back mid-report; catch it here."""
    en_keys = {k for k in i18n.EN if not k.startswith("_")}
    for code, cat in i18n.CATALOGUES.items():
        keys = {k for k in cat if not k.startswith("_")}
        assert keys == en_keys, f"{code} catalogue differs: {en_keys ^ keys}"


def test_missing_key_falls_back_to_english_not_a_crash():
    assert i18n.t("no_issues", "ha") == i18n.HA["no_issues"]
    assert i18n.t("no_issues", "zz") == i18n.EN["no_issues"]   # unknown language
    with pytest.raises(KeyError):
        i18n.t("not_a_real_key", "en")


def test_placeholders_all_resolve(health):
    """An unfilled {field} would print literally in front of a judge."""
    for lang in i18n.available(include_unreviewed=True):
        rendered = i18n.render_health(health, lang)
        assert "{" not in rendered and "}" not in rendered, f"unfilled placeholder in {lang}"


def test_language_names_are_present():
    assert i18n.language_name("ig") == "Igbo"
    assert i18n.language_name("ha") == "Hausa"
    assert i18n.language_name("yo") == "Yoruba"
