"""
Shared Gemini calling helper for claude_teacher_gen.py and nigeria_tax_gen.py.

Switched from the Anthropic Batches API to Gemini (2026-07-08) so dataset generation costs
$0 — see STRATEGY.md / data/README.md for why. No batch endpoint on Gemini's free tier, so
this runs requests through a small thread pool instead, with:
  - automatic exponential-backoff retry on 429 (rate limit) and transient 5xx errors, since
    Google's free-tier RPM/RPD are account-specific (shown in AI Studio, not fixed published
    numbers) — rather than guess a number and hardcode a sleep, we just back off on real 429s.
  - incremental, resumable writes: each result is appended to --out as soon as it succeeds, and
    already-written custom_ids are skipped on a re-run. A killed/interrupted run loses at most
    the in-flight requests, not prior progress.

Install: pip install google-genai
Auth: export GEMINI_API_KEY=... (from https://aistudio.google.com/apikey, free, no card)
"""
from __future__ import annotations

import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
MAX_WORKERS = int(os.environ.get("GEMINI_MAX_WORKERS", "4"))
MAX_RETRIES = 6


def _client():
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            "No GEMINI_API_KEY set. Get a free key (no card) at "
            "https://aistudio.google.com/apikey, then:\n"
            "  export GEMINI_API_KEY=your-key-here"
        )
    from google import genai  # imported lazily so --help works without the package installed
    return genai.Client()


def generate_structured(client, system: str, user_prompt: str, schema: dict) -> dict | None:
    """One Gemini call constrained to the given JSON schema, with retry/backoff.
    Returns the parsed dict, or None if every retry failed (caller should skip that example
    rather than crash the whole run — a few dropped examples out of a few thousand is fine)."""
    full_input = f"{system}\n\n{user_prompt}"
    for attempt in range(MAX_RETRIES):
        try:
            interaction = client.interactions.create(
                model=MODEL,
                input=full_input,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": schema,
                },
            )
            return json.loads(interaction.output_text)
        except json.JSONDecodeError:
            return None  # model didn't return valid JSON this time — skip, don't retry-loop forever
        except Exception as e:  # noqa: BLE001 — genuinely want to retry on any transient API error
            msg = str(e)
            is_rate_limit = "429" in msg or "RESOURCE_EXHAUSTED" in msg
            is_transient = is_rate_limit or "500" in msg or "503" in msg or "UNAVAILABLE" in msg
            if not is_transient or attempt == MAX_RETRIES - 1:
                print(f"  [gemini error, giving up] {msg[:200]}")
                return None
            backoff = min(60, (2 ** attempt) + random.uniform(0, 1))
            if is_rate_limit:
                backoff = max(backoff, 15)  # rate limits need real wall-clock time, not just retry
            time.sleep(backoff)
    return None


def run_batch(
    requests: list[tuple[str, str, str, dict]],  # (custom_id, system, user_prompt, schema)
    build_example: Callable[[str, dict], dict | None],  # (custom_id, parsed_json) -> example dict
    out_path: Path,
) -> None:
    """Runs all requests through a thread pool, writing successes incrementally and resumably."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    already_done: set[str] = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                already_done.add(json.loads(line)["id"])
        if already_done:
            print(f"Resuming: {len(already_done)} examples already written to {out_path}, skipping those.")

    todo = [r for r in requests if r[0] not in already_done]
    if not todo:
        print("Nothing to do — all requested examples already exist in the output file.")
        return

    client = _client()
    written = 0
    with out_path.open("a") as f, ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(generate_structured, client, system, user_prompt, schema): custom_id
            for custom_id, system, user_prompt, schema in todo
        }
        for i, future in enumerate(as_completed(futures), 1):
            custom_id = futures[future]
            parsed = future.result()
            if parsed is None:
                continue
            example = build_example(custom_id, parsed)
            if example is None:
                continue
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            f.flush()
            written += 1
            if i % 25 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)} requests done ({written} written) ...")

    print(f"Wrote {written} new examples -> {out_path} (total in file: {len(already_done) + written})")
