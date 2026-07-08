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
import re
import threading
import time
from pathlib import Path
from typing import Callable

# Free-tier quota is PER-MODEL (confirmed 2026-07-08), and each model's sustainable free rate is
# only ~5 req/min (measured — the 2026 free tier is tighter than older docs claim). So we
# ROUND-ROBIN across several current-gen flash models to multiply the free budget, and pace the
# combined stream just under the sum of their per-model limits. 2.5-flash is the quality tier;
# 2.5-flash-lite is slightly weaker but fine for advisory prose. Override with GEMINI_MODELS
# (comma-separated) / GEMINI_RPM_PER_MODEL if your account has different quota.
MODELS = [m.strip() for m in os.environ.get(
    "GEMINI_MODELS", "gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash,gemini-2.0-flash-lite"
).split(",") if m.strip()]
RPM_PER_MODEL = float(os.environ.get("GEMINI_RPM_PER_MODEL", "4.5"))  # just under the ~5/min real limit
TARGET_RPM = RPM_PER_MODEL * len(MODELS)  # combined stream rate across all models
MAX_RETRIES = 8


class _Pacer:
    """Serialize + pace all API calls to <= TARGET_RPM. A single worker paced at the RPM limit
    beats N workers that burst and then all sit in backoff — the per-minute quota is the real
    bottleneck, so steady drip-feeding maximizes throughput and avoids 429 thrash."""

    def __init__(self, rpm: float):
        self._min_interval = 60.0 / rpm
        self._lock = threading.Lock()
        self._next_allowed = 0.0

    def wait(self):
        with self._lock:
            now = time.monotonic()
            sleep_for = self._next_allowed - now
            if sleep_for > 0:
                time.sleep(sleep_for)
            self._next_allowed = max(now, self._next_allowed) + self._min_interval


def _client():
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            "No GEMINI_API_KEY set. Get a free key (no card) at "
            "https://aistudio.google.com/apikey, then:\n"
            "  export GEMINI_API_KEY=your-key-here"
        )
    from google import genai  # imported lazily so --help works without the package installed
    return genai.Client()


def _retry_delay_from(msg: str) -> float | None:
    """Gemini's 429 body includes the exact reset time, e.g. "retryDelay: 39s". Honor it
    instead of guessing a backoff — it tells us precisely when the per-minute quota resets."""
    m = re.search(r"retryDelay['\"]?:?\s*['\"]?(\d+)s", msg)
    return float(m.group(1)) if m else None


def generate_structured(client, model: str, system: str, user_prompt: str, schema: dict, pacer: "_Pacer") -> dict | None:
    """One Gemini call to `model`, constrained to the given JSON schema, paced + retried.
    Returns the parsed dict, or None if every retry failed (caller skips that example rather
    than crash the run — resumable, so it can be picked up on a later re-run).

    Uses client.models.generate_content with a JSON-schema config. NOTE: the current Gemini
    docs show a newer client.interactions.create(..., response_format=...) surface, but that
    path HANGS in google-genai 2.10.0 (verified 2026-07-08 — timed out at 2 min while
    generate_content returned in 2s). Stick with generate_content until interactions is stable."""
    from google.genai import types
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        response_schema=schema,
    )
    for attempt in range(MAX_RETRIES):
        pacer.wait()  # steady drip under the combined per-minute quota
        try:
            resp = client.models.generate_content(model=model, contents=user_prompt, config=config)
            return json.loads(resp.text)
        except json.JSONDecodeError:
            return None  # model didn't return valid JSON this time — skip, don't retry-loop forever
        except Exception as e:  # noqa: BLE001 — genuinely want to retry on any transient API error
            msg = str(e)
            is_rate_limit = "429" in msg or "RESOURCE_EXHAUSTED" in msg
            is_transient = is_rate_limit or "500" in msg or "503" in msg or "UNAVAILABLE" in msg
            if not is_transient or attempt == MAX_RETRIES - 1:
                print(f"  [gemini error, giving up] {msg[:160]}")
                return None
            if is_rate_limit:
                # Honor the API's own retryDelay (its precise reset), + a small cushion.
                delay = (_retry_delay_from(msg) or 30) + 2
            else:
                delay = min(30, 2 ** attempt)
            time.sleep(delay)
    return None


def run_batch(
    requests: list[tuple[str, str, str, dict]],  # (custom_id, system, user_prompt, schema)
    build_example: Callable[[str, dict], dict | None],  # (custom_id, parsed_json) -> example dict
    out_path: Path,
) -> None:
    """Generates each request paced under the free-tier RPM, writing successes incrementally
    and resumably. Single steady worker — bursting a thread pool just saturates the per-minute
    quota and thrashes (learned the hard way 2026-07-08). Re-run the same command to resume;
    already-written custom_ids are skipped."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    already_done: set[str] = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                already_done.add(json.loads(line)["id"])
        if already_done:
            print(f"Resuming: {len(already_done)} already written to {out_path}, skipping those.", flush=True)

    todo = [r for r in requests if r[0] not in already_done]
    if not todo:
        print("Nothing to do — all requested examples already exist in the output file.", flush=True)
        return

    eta_min = len(todo) / TARGET_RPM
    print(f"Generating {len(todo)} examples, round-robin across {len(MODELS)} models "
          f"({', '.join(MODELS)}) at ~{TARGET_RPM:.0f}/min combined (~{eta_min:.0f} min). "
          f"Paced + resumable; safe to Ctrl-C and re-run.", flush=True)

    client = _client()
    pacer = _Pacer(TARGET_RPM)
    written = 0
    t0 = time.monotonic()
    with out_path.open("a") as f:
        for i, (custom_id, system, user_prompt, schema) in enumerate(todo, 1):
            model = MODELS[i % len(MODELS)]  # round-robin: consecutive requests hit different models
            parsed = generate_structured(client, model, system, user_prompt, schema, pacer)
            if parsed is not None:
                example = build_example(custom_id, parsed)
                if example is not None:
                    f.write(json.dumps(example, ensure_ascii=False) + "\n")
                    f.flush()
                    written += 1
            if i % 10 == 0 or i == len(todo):
                rate = written / max((time.monotonic() - t0) / 60, 1e-6)
                remaining = (len(todo) - i) / max(rate, 1e-6)
                print(f"  {i}/{len(todo)} attempted, {written} written "
                      f"(~{rate:.1f}/min, ~{remaining:.0f} min left)", flush=True)

    print(f"Wrote {written} new examples -> {out_path} "
          f"(total in file: {len(already_done) + written})", flush=True)
