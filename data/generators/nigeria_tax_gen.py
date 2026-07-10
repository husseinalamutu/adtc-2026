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
- State the headline rate/threshold PLAINLY (e.g. "VAT is 7.5%", "small companies pay 0% CIT")
  regardless of confidence tag — do not soften the core number itself. Reserve any hedging
  ("this is expected to apply where...") for genuinely uncertain application details, not the
  headline figure. This matters: vague numbers train a model that forgets them.
- Always close with a one-line practical nudge to confirm specifics with FIRS/the Nigeria
  Revenue Service or a licensed accountant before filing — this is standard, responsible
  advisory practice, not a hedge about the facts themselves.
- Write like you're helping a busy, non-accountant business owner or a diaspora Nigerian
  who doesn't know tax jargon. Plain English, practical, short paragraphs or a short list.
- The question should sound like a real person typed it, not a textbook prompt."""


# ---------------------------------------------------------------------------------------------
# FACT-DRILL layer (added 2026-07-09). The first Nigeria model (149 scenario examples) LEARNED
# THE STYLE of tax advice but reverted to the base model's WRONG pre-2025 priors on the actual
# numbers (said VAT 5.5%, small-co threshold ₦5M, etc.). Fixing numeric recall against strong
# priors needs high-signal, number-FIRST repetition — many crisp Q&A that state each core rate
# plainly and early, in varied phrasings. This is that layer; it dominates the mix.
FACT_DRILL_SYSTEM = """You write short, factual training Q&A for an offline assistant that answers
Nigerian SME tax questions under the Nigeria Tax Reform Acts 2025 (effective Jan 2026).

You are given ONE fact and a question angle. Produce a JSON object {"question","answer"}:
- The QUESTION is how a real Nigerian business owner would phrase that angle (first person, plain).
- The ANSWER must STATE THE KEY NUMBER/RULE PLAINLY IN THE FIRST SENTENCE, using ONLY the supplied
  fact. Lead with it: e.g. "The standard VAT rate in Nigeria is 7.5%." Do NOT bury the number, do
  NOT hedge the headline figure, do NOT add any figure not in the fact. Then 1-2 sentences of
  practical context if useful. Keep it under ~90 words. No markdown headers.
- End with a brief "confirm specifics with FIRS / a licensed accountant" only when the fact's
  application genuinely depends on details — not on every answer."""

# The load-bearing numbers the model MUST recall, each with several question angles so the fact
# gets stated many times in varied framings. Answers are model-generated but grounded on `path`.
CORE_FACTS = [
    ("value_added_tax.standard_rate", [
        "what the VAT rate is in Nigeria now",
        "how much VAT to add to an invoice",
        "the current standard VAT percentage under the 2025 rules",
        "what percentage VAT a shop charges customers"]),
    ("companies_income_tax.small_company_rate", [
        "what Companies Income Tax rate a small company pays",
        "whether a genuinely small company pays any CIT",
        "the CIT rate for a qualifying small business"]),
    ("companies_income_tax.standard_company_rate", [
        "the standard Companies Income Tax rate for a normal-sized company",
        "what CIT rate a company above the small-company threshold pays"]),
    ("companies_income_tax.small_company_definition", [
        "what turnover makes a company a 'small company' for 0% tax",
        "the fixed-asset and turnover limits to count as a small company",
        "whether my company is small enough to pay 0% CIT",
        "whether a company with turnover ABOVE the limit (e.g. ₦120 million) qualifies — answer no and spell out the comparison to the ₦100 million threshold",
        "whether a company with turnover just UNDER the limit (e.g. ₦95 million) qualifies — answer yes and spell out the comparison to the ₦100 million threshold"]),
    ("companies_income_tax.small_company_definition.professional_services_exclusion", [
        "whether my consulting firm gets the small-company 0% tax if it's under the turnover limit",
        "if a professional-services business (like consulting or accountancy) can be a small company",
        "why a small consulting company still pays company income tax"]),
    ("development_levy.rate", [
        "the Development Levy rate for companies",
        "how much Development Levy a company pays and on what"]),
    ("development_levy.exemptions", [
        "whether a small company pays the Development Levy",
        "which companies are exempt from the Development Levy"]),
    ("withholding_tax.small_company_exemption", [
        "when a small company is exempt from deducting withholding tax",
        "the withholding-tax exemption limit for small suppliers with a TIN"]),
    ("withholding_tax.deemed_distribution_rate", [
        "the withholding tax rate on deemed distributions of a closely-held company",
        "how undistributed profits of a company controlled by 5 or fewer people are taxed"]),
    ("capital_gains_tax.companies_rate", [
        "the Capital Gains Tax rate for a company selling an asset"]),
    ("capital_gains_tax.small_company_exemption", [
        "whether a small company pays Capital Gains Tax"]),
    ("personal_income_tax.exempt_threshold", [
        "the income level below which an individual pays no personal income tax"]),
    ("personal_income_tax.top_rate", [
        "the top personal income tax rate under the new bands"]),
    ("personal_income_tax.rent_relief", [
        "how the new rent relief works and its cap"]),
    ("tax_residency.rule", [
        "how many days in Nigeria make someone a tax resident"]),
    ("tax_residency.non_resident_taxation", [
        "whether a non-resident pays Nigerian tax on income earned outside Nigeria — answer no, only Nigerian-source income",
        "which kinds of income Nigeria can tax a non-resident on"]),
    ("tax_residency.remittances_not_taxable", [
        "whether money I send home to my family in Nigeria is taxed"]),
    ("tax_residency.foreign_earned_income_exemption", [
        "whether my foreign salary is taxed if paid into a Nigerian account"]),
    ("filing_and_penalties.annual_returns_deadline", [
        "when an established company must file its annual tax returns",
        "the filing deadline for a newly incorporated company's first return"]),
    ("filing_and_penalties.penalty_failure_to_register", [
        "the penalty for failing to register for tax",
        "what it costs a business to keep ignoring tax registration month after month"]),
]


def build_fact_drill_requests(n: int, seed: int, topics: list[str] | None = None,
                              id_prefix: str = "nga-drill") -> list[tuple[str, str, str, dict, str]]:
    """High-signal, number-first recall pairs. Cycles the core facts x their question angles so
    each load-bearing number is stated many times in varied framings. `topics` (substring match
    on the fact path) narrows the pool to weak facts flagged by the GGUF fact check; pair it
    with a distinct `id_prefix` + out file so the top-up never collides with the main run."""
    rng = random.Random(seed)
    angle_pool = [(path, ang) for path, angles in CORE_FACTS for ang in angles
                  if not topics or any(t in path for t in topics)]
    if not angle_pool:
        raise SystemExit(f"--topics {topics} matched no CORE_FACTS paths")
    out = []
    for i in range(n):
        path, angle = angle_pool[i % len(angle_pool)]
        fact_block = get_fact(path)
        custom_id = f"{id_prefix}-{i:05d}"
        family = f"nigeria_tax_drill::{path.split('.')[0]}"
        user_prompt = (
            f"Fact (the ONLY source of truth — state nothing outside it):\n"
            f"{json.dumps(fact_block, indent=2, ensure_ascii=False)}\n\n"
            f"Question angle: {angle}.\n"
            f"Write the question a Nigerian business owner would type, and a number-first answer."
        )
        out.append((custom_id, FACT_DRILL_SYSTEM, user_prompt, RESPONSE_SCHEMA, family))
    return out


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
    ap.add_argument("--drill-fraction", type=float, default=0.65,
                    help="share of examples that are high-signal number-first fact drills")
    ap.add_argument("--topics", default=None,
                    help="comma-separated substrings of CORE_FACTS paths; drills only matching facts")
    ap.add_argument("--id-prefix", default="nga-drill",
                    help="custom_id prefix for drill examples (use a distinct one for topic top-ups)")
    args = ap.parse_args()

    topics = [t.strip() for t in args.topics.split(",")] if args.topics else None
    n_drill = int(args.n * args.drill_fraction)
    n_scen = args.n - n_drill
    reqs = build_fact_drill_requests(n_drill, args.seed, topics=topics,
                                     id_prefix=args.id_prefix) + build_requests(n_scen, args.seed + 1)
    scenario_families = {r[0]: r[4] for r in reqs}
    print(f"  ({n_drill} fact-drill + {n_scen} scenario)")

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
