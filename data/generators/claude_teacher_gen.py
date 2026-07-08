#!/usr/bin/env python3
"""
Teacher generator — open-ended advisory / compliance / correspondence content.

There's no programmatic ground truth for "explain VAT registration clearly" the way there is
for "compute VAT on this invoice" (see templated_gen.py). So this generator uses an LLM as the
teacher, but constrains it hard against hallucination: every request is grounded with the exact
rates/thresholds/authority name from seeds/markets.json, and the model is told to use ONLY those
supplied facts for anything statutory — not to invent citations.

Runs on Gemini (free tier, $0 — see data/generators/_gemini_common.py for why we moved off the
Anthropic Batches API) via a small thread pool with automatic rate-limit backoff and resumable,
incremental writes.

Requires GEMINI_API_KEY — free, no card, from https://aistudio.google.com/apikey.
"""
import argparse
import json
import random
from pathlib import Path

from _gemini_common import run_batch

SEEDS = json.loads((Path(__file__).parent.parent / "seeds" / "markets.json").read_text())
# Nigeria is excluded here: it gets deep, source-grounded coverage from
# generators/nigeria_tax_gen.py (seeds/nigeria_tax_facts.json). Keeping it in this
# generic pool would risk generating conflicting/shallower Nigeria tax claims.
MARKETS = [m for m in SEEDS["markets"] if m["country"] != "Nigeria"]
ARCHETYPES = SEEDS["business_archetypes"]
PERSONAS = SEEDS["operator_personas"]

TOPICS = [
    "when this business must register for VAT and what happens if it doesn't",
    "how withholding tax works for this business and who deducts it",
    "what records this business is legally expected to keep for tax purposes",
    "what should be on a compliant invoice or receipt in this country",
    "the risk of mixing personal and business mobile-money accounts",
    "how to handle a customer who wants a discount for paying in cash instead of mobile money",
    "what to do if a mobile-money transaction doesn't match any outstanding invoice",
    "the difference between a quote and an invoice and when to issue each",
    "how to keep track of money owed to suppliers vs money owed by customers",
    "what this business should do differently as it grows past the informal sector",
]

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "A realistic, first-person question or request an African SME operator would actually type into a chat box — not a textbook question.",
        },
        "answer": {
            "type": "string",
            "description": "A clear, accurate, practically useful answer grounded ONLY in the supplied facts for anything statutory (rates, thresholds, authority names). Do not invent specific law/section numbers not given. Plain English, no markdown headers, a few short paragraphs or a short list.",
        },
    },
    "required": ["question", "answer"],
}

SYSTEM = """You write training examples for a back-office assistant used by African SME
operators (shop owners, bookkeepers) on an offline laptop app. For each request you are given
a business context and a topic. Produce ONE realistic operator question and ONE accurate answer,
as a JSON object with keys "question" and "answer".

Hard rules:
- Use ONLY the specific facts given to you (tax rates, thresholds, authority name) for anything
  statutory. Do not invent section numbers, penalty amounts, or deadlines you were not given.
- If a fact you'd need wasn't supplied, have the answer say to confirm with the tax authority or
  an accountant rather than guessing.
- Write like you're helping a busy, non-accountant business owner — plain English, practical,
  no jargon, no markdown headers, short.
- The question should sound like something typed by a real operator, not a textbook prompt."""


def build_requests(n: int, seed: int) -> list[tuple[str, str, str, dict]]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        market = rng.choice(MARKETS)
        archetype = rng.choice(ARCHETYPES)
        persona = rng.choice(PERSONAS)
        topic = rng.choice(TOPICS)
        custom_id = f"teacher-{i:05d}"

        facts = (
            f"Country: {market['country']}. Business: a {archetype['type']}. "
            f"Operator role: {persona}. Currency: {market['currency']}. "
            f"{market['vat_name']} rate: {market['vat_rate']*100:.1f}%. "
            f"Withholding tax rate: {market['withholding_tax_rate']*100:.1f}%. "
            f"VAT registration threshold: {market['vat_registration_threshold_local']:,} {market['currency']} in annual turnover. "
            f"Tax authority: {market['tax_authority']}. "
            f"Common mobile-money provider used: {rng.choice(market['mobile_money'])}."
        )
        user_prompt = f"Facts:\n{facts}\n\nTopic to cover: {topic}\n\nGenerate the question+answer pair now."
        scenario_family = f"advisory::{topic}"
        out.append((custom_id, SYSTEM, user_prompt, RESPONSE_SCHEMA, scenario_family))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=800)
    ap.add_argument("--out", default="out/teacher.jsonl")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    reqs = build_requests(args.n, args.seed)
    scenario_families = {r[0]: r[4] for r in reqs}

    def build_example(custom_id: str, parsed: dict) -> dict | None:
        question, answer = parsed.get("question"), parsed.get("answer")
        if not question or not answer:
            return None
        return {
            "id": custom_id,
            "category": "advisory",
            "scenario_family": scenario_families.get(custom_id, "advisory::unknown"),
            "messages": [{"role": "user", "content": question}, {"role": "assistant", "content": answer}],
            "ground_truth": None,
        }

    print(f"Generating {len(reqs)} advisory examples ...")
    run_batch(
        [(cid, sys_, usr, schema) for cid, sys_, usr, schema, _ in reqs],
        build_example,
        Path(args.out),
    )


if __name__ == "__main__":
    main()
