#!/usr/bin/env python3
"""
Nigeria tax/compliance generator — deep, source-grounded coverage of the 2025 Tax Reform
Acts (effective 2026-01-01), for the "African use case" depth play (see STRATEGY.md).

Grounding chain (see seeds/nigeria_tax_facts.json _meta for full source list):
    OCR of the official Gazette (Nigeria Tax Act 2025, scanned, tesseract)
  + clean text-layer extraction (Nigeria Tax Administration Act 2025)
  + reputable secondary corroboration (EY, Baker Tilly, Aluko & Oyebode, KPMG, Mercans)
  -> hand-curated seeds/nigeria_tax_facts.json, every fact tagged with a confidence level
  -> this generator, which is FORBIDDEN from stating any number not in that file.

This is the same "programmatic ground truth over LLM guessing" principle as
templated_gen.py, just applied to legal facts instead of arithmetic: the facts are fixed
before the model ever runs, so the model's job is phrasing and business-context framing,
not sourcing the numbers.

Runs on Gemini (free tier, $0 — see data/generators/_gemini_common.py). Requires
GEMINI_API_KEY — free, no card, from https://aistudio.google.com/apikey.
"""
import argparse
import json
import random
from pathlib import Path

from _gemini_common import run_batch

DATA_DIR = Path(__file__).parent.parent
FACTS = json.loads((DATA_DIR / "seeds" / "nigeria_tax_facts.json").read_text())
MARKETS = json.loads((DATA_DIR / "seeds" / "markets.json").read_text())
ARCHETYPES = MARKETS["business_archetypes"]
PERSONAS = MARKETS["operator_personas"]
NIGERIA_CITIES = next(m for m in MARKETS["markets"] if m["country"] == "Nigeria")["cities"]

# Each entry: (topic label, dotted path into FACTS to ground the answer with)
FACT_TOPICS = [
    ("whether this business needs to pay Companies Income Tax at all", "companies_income_tax"),
    ("what counts as a 'small company' for tax exemption purposes", "companies_income_tax.small_company_definition"),
    ("the standard VAT rate and the new input VAT credit", "value_added_tax"),
    ("whether this business must deduct withholding tax on a supplier payment", "withholding_tax"),
    ("how Capital Gains Tax changed for this kind of business", "capital_gains_tax"),
    ("how personal income tax bands and rent relief work for the owner", "personal_income_tax"),
    ("the new Development Levy and whether this business owes it", "development_levy"),
    ("when this business needs a TIN and how to get one", "tin_and_filing"),
    ("the deadline for filing annual returns", "filing_and_penalties.annual_returns_deadline"),
    ("what happens if the business doesn't register for tax on time", "filing_and_penalties.penalty_failure_to_register"),
]

DIASPORA_TOPICS = [
    ("whether money sent home to family will be taxed", "tax_residency.remittances_not_taxable"),
    ("how the 183-day residency rule works", "tax_residency.rule"),
    ("whether foreign salary paid into a Nigerian account is taxable", "tax_residency.foreign_earned_income_exemption"),
    ("whether they'll be taxed twice, abroad and in Nigeria", "tax_residency.double_taxation_relief"),
    ("whether they need a TIN if they only send money home occasionally", "tin_and_filing.who_needs_a_tin"),
]

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "A realistic, first-person question an SME operator or diaspora Nigerian would actually type into a chat box.",
        },
        "answer": {
            "type": "string",
            "description": "Accurate, plain-English answer using ONLY the supplied facts for any number/rate/threshold/deadline. Reference the confidence level implicitly by hedging appropriately when confidence is secondary_corroborated (e.g. 'this is expected to be...'); state plainly when primary_confirmed. No markdown headers.",
        },
    },
    "required": ["question", "answer"],
}

SYSTEM = """You write training examples for an offline back-office assistant used by
Nigerian SME operators and by Nigerians in the diaspora, grounded in the Nigeria Tax
Reform Acts 2025 (effective 2026-01-01).

You are given a JSON fact block for ONE topic. Produce a JSON object with keys "question"
and "answer". Hard rules:
- State ONLY numbers/rates/thresholds/deadlines that appear in the given fact block. Never
  add a figure from general knowledge, even if you believe it's correct — the fact block is
  the single source of truth for this exercise.
- If a fact's "confidence" is "secondary_corroborated", answer helpfully but naturally hedge
  ("this is expected to...", "under the new rules...") rather than stating it as
  courtroom-certain. If "confidence" is "primary_confirmed", you may state it plainly.
- Always close with a one-line practical nudge to confirm specifics with FIRS/the Nigeria
  Revenue Service or a licensed accountant before filing — this is standard, responsible
  advisory practice, not a hedge about the facts themselves.
- Write like you're helping a busy, non-accountant business owner or a diaspora Nigerian
  who doesn't know tax jargon. Plain English, practical, short paragraphs or a short list.
- The question should sound like a real person typed it, not a textbook prompt."""


def get_fact(path: str) -> dict:
    node = FACTS
    for part in path.split("."):
        node = node[part]
    return node


def build_requests(n: int, seed: int) -> list[tuple[str, str, str, dict, str]]:
    rng = random.Random(seed)
    out = []

    for i in range(n):
        is_diaspora = rng.random() < 0.25
        if is_diaspora:
            topic_label, fact_path = rng.choice(DIASPORA_TOPICS)
            persona = rng.choice(["a Nigerian working abroad", "a diaspora Nigerian sending money home monthly", "a Nigerian who just moved abroad for work"])
            archetype = None
        else:
            topic_label, fact_path = rng.choice(FACT_TOPICS)
            archetype = rng.choice(ARCHETYPES)
            persona = rng.choice(PERSONAS)

        city = rng.choice(NIGERIA_CITIES)
        custom_id = f"nga-{i:05d}"
        scenario_family = f"nigeria_tax::{fact_path.split('.')[0]}"

        fact_block = get_fact(fact_path)
        context = (
            f"Diaspora scenario: {persona}."
            if is_diaspora
            else f"Business context: {persona} at a {archetype['type']} in {city}, Nigeria."
        )
        user_prompt = (
            f"{context}\n\nTopic: {topic_label}\n\n"
            f"Fact block (source of truth — cite nothing outside this):\n{json.dumps(fact_block, indent=2)}\n\n"
            f"Generate the question+answer pair now."
        )
        out.append((custom_id, SYSTEM, user_prompt, RESPONSE_SCHEMA, scenario_family))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--out", default="out/nigeria_tax.jsonl")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    reqs = build_requests(args.n, args.seed)
    scenario_families = {r[0]: r[4] for r in reqs}

    def build_example(custom_id: str, parsed: dict) -> dict | None:
        question, answer = parsed.get("question"), parsed.get("answer")
        if not question or not answer:
            return None
        return {
            "id": custom_id,
            "category": "nigeria_tax",
            "scenario_family": scenario_families.get(custom_id, "nigeria_tax::unknown"),
            "messages": [{"role": "user", "content": question}, {"role": "assistant", "content": answer}],
            "ground_truth": None,
        }

    print(f"Generating {len(reqs)} Nigeria-tax examples ...")
    run_batch(
        [(cid, sys_, usr, schema) for cid, sys_, usr, schema, _ in reqs],
        build_example,
        Path(args.out),
    )


if __name__ == "__main__":
    main()
