#!/usr/bin/env python3
"""
Claude-teacher generator — open-ended advisory / compliance / correspondence content.

There's no programmatic ground truth for "explain VAT registration clearly" the way there is
for "compute VAT on this invoice" (see templated_gen.py). So this generator uses Claude Opus
4.8 as the teacher, but constrains it hard against hallucination: every request is grounded
with the exact rates/thresholds/authority name from seeds/markets.json, and the model is told
to use ONLY those supplied facts for anything statutory — not to invent citations.

Uses the Message Batches API (50% cheaper, fine for offline dataset generation — no latency
requirement) and structured outputs (output_config.format) so every result is valid JSON with
no manual parsing.

Requires ANTHROPIC_API_KEY (or `ant auth login`). See SKILL claude-api / python/claude-api/batches.md.
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
    "additionalProperties": False,
}

SYSTEM = """You write training examples for a back-office assistant used by African SME
operators (shop owners, bookkeepers) on an offline laptop app. For each request you are given
a business context and a topic. Produce ONE realistic operator question and ONE accurate answer.

Hard rules:
- Use ONLY the specific facts given to you (tax rates, thresholds, authority name) for anything
  statutory. Do not invent section numbers, penalty amounts, or deadlines you were not given.
- If a fact you'd need wasn't supplied, have the answer say to confirm with the tax authority or
  an accountant rather than guessing.
- Write like you're helping a busy, non-accountant business owner — plain English, practical,
  no jargon, no markdown headers, short.
- The question should sound like something typed by a real operator, not a textbook prompt."""


def build_requests(n: int, seed: int) -> tuple[list[Request], dict[str, str]]:
    rng = random.Random(seed)
    requests = []
    scenario_families: dict[str, str] = {}
    for i in range(n):
        market = rng.choice(MARKETS)
        archetype = rng.choice(ARCHETYPES)
        persona = rng.choice(PERSONAS)
        topic = rng.choice(TOPICS)
        custom_id = f"teacher-{i:05d}"
        scenario_families[custom_id] = f"advisory::{topic}"

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
    ap.add_argument("--n", type=int, default=800)
    ap.add_argument("--out", default="out/teacher.jsonl")
    ap.add_argument("--seed", type=int, default=7)
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
                "category": "advisory",
                "scenario_family": scenario_families.get(result.custom_id, "advisory::unknown"),
                "messages": [{"role": "user", "content": question}, {"role": "assistant", "content": answer}],
                "ground_truth": None,
            }
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            written += 1

    print(f"Wrote {written} teacher examples -> {out_path}")


if __name__ == "__main__":
    main()
