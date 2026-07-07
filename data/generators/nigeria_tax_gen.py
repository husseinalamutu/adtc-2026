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

Uses the Message Batches API + structured outputs. Requires ANTHROPIC_API_KEY (or
`ant auth login`).
"""
import argparse
import json
import os
import random
import time
from pathlib import Path

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

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
    "additionalProperties": False,
}

SYSTEM = """You write training examples for an offline back-office assistant used by
Nigerian SME operators and by Nigerians in the diaspora, grounded in the Nigeria Tax
Reform Acts 2025 (effective 2026-01-01).

You are given a JSON fact block for ONE topic. Hard rules:
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


def build_requests(n: int, seed: int) -> tuple[list[Request], dict[str, str]]:
    rng = random.Random(seed)
    requests = []
    scenario_families: dict[str, str] = {}

    for i in range(n):
        is_diaspora = rng.random() < 0.25
        if is_diaspora:
            topic_label, fact_path = rng.choice(DIASPORA_TOPICS)
            archetype = None
            persona = rng.choice(["a Nigerian working abroad", "a diaspora Nigerian sending money home monthly", "a Nigerian who just moved abroad for work"])
        else:
            topic_label, fact_path = rng.choice(FACT_TOPICS)
            archetype = rng.choice(ARCHETYPES)
            persona = rng.choice(PERSONAS)

        city = rng.choice(NIGERIA_CITIES)
        custom_id = f"nga-{i:05d}"
        scenario_families[custom_id] = f"nigeria_tax::{fact_path.split('.')[0]}"

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

        requests.append(
            Request(
                custom_id=custom_id,
                params=MessageCreateParamsNonStreaming(
                    model="claude-opus-4-8",
                    max_tokens=1024,
                    system=SYSTEM,
                    messages=[{"role": "user", "content": user_prompt}],
                    output_config={"format": {"type": "json_schema", "schema": RESPONSE_SCHEMA}},
                ),
            )
        )
    return requests, scenario_families


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--out", default="out/nigeria_tax.jsonl")
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--poll-interval", type=int, default=30)
    args = ap.parse_args()

    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        print("No ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN set — run `ant auth login` or export a key.")
        return

    client = anthropic.Anthropic()
    requests, scenario_families = build_requests(args.n, args.seed)

    print(f"Submitting batch of {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch {batch.id} — status: {batch.processing_status}")

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        print(f"  ...{batch.processing_status} (processing: {batch.request_counts.processing})")
        time.sleep(args.poll_interval)

    print(f"Done. succeeded={batch.request_counts.succeeded} errored={batch.request_counts.errored}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out_path.open("w") as f:
        for result in client.messages.batches.results(batch.id):
            if result.result.type != "succeeded":
                continue
            msg = result.result.message
            text = next((b.text for b in msg.content if b.type == "text"), None)
            if not text:
                continue
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                continue
            question, answer = parsed.get("question"), parsed.get("answer")
            if not question or not answer:
                continue
            example = {
                "id": result.custom_id,
                "category": "nigeria_tax",
                "scenario_family": scenario_families.get(result.custom_id, "nigeria_tax::unknown"),
                "messages": [{"role": "user", "content": question}, {"role": "assistant", "content": answer}],
                "ground_truth": None,
            }
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            written += 1

    print(f"Wrote {written} Nigeria tax examples -> {out_path}")


if __name__ == "__main__":
    main()
