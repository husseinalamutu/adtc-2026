"""
Shared free-tier LLM calling helper for claude_teacher_gen.py and nigeria_tax_gen.py.

Generates training data for $0 across two free providers (see data/README.md for why we moved
off the Anthropic Batches API). Provider is chosen by GENERATION_PROVIDER=gemini|groq:
  - gemini (google-genai): free but the 2026 free tier is very tight (~5 req/min per model,
    per-MINUTE reset, and a low daily cap). We round-robin flash models to stretch it.
  - groq: separate free quota pool (a whole different account/key). llama-3.1-8b-instant in
    particular has a high daily token budget (~500K/day). Round-robin 8b + 70b for volume.

Both providers share: a single paced worker (bursting just thrashes a per-minute quota),
retry that honors the API's own retry delay, and incremental+resumable writes (each success is
appended immediately; already-written custom_ids are skipped on re-run). When one provider's
daily quota is spent, switch GENERATION_PROVIDER and re-run — it resumes on the remainder.

Install: pip install google-genai groq
Auth: GEMINI_API_KEY (aistudio.google.com/apikey) and/or GROQ_API_KEY (console.groq.com/keys).
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Callable

PROVIDER = os.environ.get("GENERATION_PROVIDER", "gemini").strip().lower()

# Per-provider model rotations. Free quota is PER-MODEL, so round-robin multiplies the budget.
_DEFAULT_MODELS = {
    # gemini: 2.0-* family is daily-exhausted; a throttled model in rotation is WORSE than
    # excluding it (each request burns a full ~57s retryDelay). Keep only live models.
    "gemini": "gemini-2.5-flash,gemini-2.5-flash-lite,gemini-flash-lite-latest",
    # groq: 8b-instant has a much higher daily token cap than 70b; both are fine for grounded
    # phrasing (the facts are fixed — the model only phrases them).
    "groq": "llama-3.1-8b-instant,llama-3.3-70b-versatile",
}
MODELS = [m.strip() for m in os.environ.get(
    "GEN_MODELS", _DEFAULT_MODELS.get(PROVIDER, _DEFAULT_MODELS["gemini"])
).split(",") if m.strip()]

# Combined target request rate. Gemini free is ~5/min per model; Groq free allows a higher RPM
# (~30) but a tight per-minute TPM — pace conservatively and let retry-on-429 self-regulate.
_RPM_PER_MODEL = float(os.environ.get("GEN_RPM_PER_MODEL", "4" if PROVIDER == "gemini" else "8"))
TARGET_RPM = _RPM_PER_MODEL * len(MODELS)
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
    if PROVIDER == "groq":
        if not os.environ.get("GROQ_API_KEY"):
            raise SystemExit("No GROQ_API_KEY set. Get a free key at https://console.groq.com/keys")
        from groq import Groq  # lazy import so --help works without the package
        return Groq()
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            "No GEMINI_API_KEY set. Get a free key (no card) at "
            "https://aistudio.google.com/apikey, then: export GEMINI_API_KEY=your-key-here"
        )
    from google import genai
    return genai.Client()


def _retry_delay_from(msg: str) -> float | None:
    """Both providers put the reset time in the 429 body — Gemini "retryDelay: 39s",
    Groq "try again in 12.5s". Honor it instead of guessing a backoff."""
    m = re.search(r"retryDelay['\"]?:?\s*['\"]?([\d.]+)s", msg) or re.search(r"try again in ([\d.]+)s", msg)
    return float(m.group(1)) if m else None


def _call_gemini(client, model, system, user_prompt, schema):
    # generate_content with JSON-schema config. NOTE: the docs' newer client.interactions.create
    # surface HANGS in google-genai 2.10.0 (verified 2026-07-08) — stick with generate_content.
    from google.genai import types
    resp = client.models.generate_content(
        model=model, contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system, response_mime_type="application/json", response_schema=schema),
    )
    return json.loads(resp.text)


def _call_groq(client, model, system, user_prompt, schema):
    # Groq is OpenAI-compatible; JSON mode = response_format {"type":"json_object"}. The schema
    # is enforced via the system prompt (which already instructs the exact keys). Verified
    # 2026-07-08: llama-3.3-70b returns clean, correctly-grounded JSON in ~1s.
    resp = client.chat.completions.create(
        model=model, max_tokens=800,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def generate_structured(client, model: str, system: str, user_prompt: str, schema: dict, pacer: "_Pacer") -> dict | None:
    """One paced+retried call to `model`, constrained to the JSON schema. Returns the parsed
    dict, or None if every retry failed (caller skips it — resumable, so a later re-run retries).
    Dispatches to the Gemini or Groq backend based on GENERATION_PROVIDER."""
    call = _call_groq if PROVIDER == "groq" else _call_gemini
    for attempt in range(MAX_RETRIES):
        pacer.wait()  # steady drip under the combined per-minute quota
        try:
            return call(client, model, system, user_prompt, schema)
        except json.JSONDecodeError:
            return None  # model didn't return valid JSON this time — skip, don't retry-loop forever
        except Exception as e:  # noqa: BLE001 — retry on any transient API error
            msg = str(e)
            is_rate_limit = "429" in msg or "RESOURCE_EXHAUSTED" in msg or "rate_limit" in msg.lower()
            is_transient = is_rate_limit or "500" in msg or "503" in msg or "UNAVAILABLE" in msg
            if not is_transient or attempt == MAX_RETRIES - 1:
                print(f"  [{PROVIDER} error, giving up] {msg[:160]}", flush=True)
                return None
            delay = ((_retry_delay_from(msg) or 30) + 2) if is_rate_limit else min(30, 2 ** attempt)
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
