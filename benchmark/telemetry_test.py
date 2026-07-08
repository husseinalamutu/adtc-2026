#!/usr/bin/env python3
"""
The single most valuable test in the project. Runs the REAL adtc-profiler package
(verified by installing it and reading its source directly — see STRATEGY.md's
"profiler ground truth" note) in participant mode and asserts we're safely inside the two
limits that zero us out or cost points:

    memory.peak_rss_mb          < 6500   (hard DQ line is 7168 MB / 7.0 GB; margin for the
                                           ±15% audit variance)
    throughput.tokens_per_second_generation >= 16   (speed floor is 15; margin for ±25%)

Verified CLI (installed `adtc-profiler` package, 2026-07-07):
    adtc-profiler run --submission <dir> --mode participant --output <file> --skip-accuracy
`<dir>` must contain metadata.json with a top-level `_runtime.model_path` pointing at the
GGUF, relative to `<dir>`. Report JSON is nested: report["throughput"]["..."],
report["memory"]["..."], report["cpu_thermal"]["throttled"] — NOT flat top-level keys.

Run on target-class HW after every model rebuild:
    python3 telemetry_test.py --submission ../submission
Exit code 0 = safe to submit; non-zero = fix before submitting.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RSS_CEILING_MB = 6500.0
TPS_FLOOR = 16.0
# The profiler's own thermal.py hardcodes 95.0°C as a placeholder (explicitly marked
# "revisit in Phase 2 once we have a real audit VM to calibrate against" in its source).
# The challenge website states 85°C. We target well under 85°C so we're safe under either.
CORE_TEMP_TARGET_C = 85.0


def run_profiler(submission_dir: str) -> dict:
    if not shutil.which("adtc-profiler"):
        sys.exit(
            "adtc-profiler not found on PATH — install it:\n"
            '  pip install "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git"\n'
            "(infra/provision_benchmark_vm.sh does this on the target-class VM.)"
        )
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "report.json"
        cmd = [
            "adtc-profiler", "run",
            "--submission", submission_dir,
            "--mode", "participant",
            "--output", str(out_path),
            "--skip-accuracy",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.exit(f"adtc-profiler failed (exit {proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
        return json.loads(out_path.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission", default="../submission", help="Path to the submission directory (must contain metadata.json + the GGUF it references)")
    ap.add_argument("--from-json", help="skip the run; assert against an existing profiler report JSON")
    args = ap.parse_args()

    report = json.load(open(args.from_json)) if args.from_json else run_profiler(args.submission)

    rss = report["memory"]["peak_rss_mb"]
    tps = report["throughput"]["tokens_per_second_generation"]
    throttled = report["cpu_thermal"]["throttled"]
    core_temp = report["cpu_thermal"].get("core_temp_c_peak")
    params_match = report.get("model_info", {}).get("params_match", True)

    ok = True
    print(f"peak_rss_mb        = {rss:.0f}   (ceiling {RSS_CEILING_MB:.0f}, hard DQ at 7168 / 7.0 GB)")
    if rss >= RSS_CEILING_MB:
        print("  FAIL: too close to the 7 GB OOM/DQ line."); ok = False

    print(f"tokens_per_second   = {tps:.1f}   (floor {TPS_FLOOR}, full marks at 15)")
    if tps < TPS_FLOOR:
        print("  FAIL: below the speed-margin floor."); ok = False

    print(f"thermal.throttled   = {throttled}   (profiler flags this at its own coded 95°C; site states 85°C)")
    if core_temp is not None:
        print(f"core_temp_c_peak    = {core_temp:.1f}   (target < {CORE_TEMP_TARGET_C})")
        if core_temp >= CORE_TEMP_TARGET_C:
            print("  FAIL: at/above the 85°C target (even if the profiler itself doesn't flag `throttled` yet)."); ok = False
    if throttled:
        print("  FAIL: profiler flagged thermal throttling."); ok = False

    print(f"model_info.params_match = {params_match}   (False = metadata.json parameters_estimate looks like it understates the real GGUF — fix it)")
    if not params_match:
        print("  FAIL: parameter-count fraud check failed — update submission/metadata.json's model.parameters_estimate."); ok = False

    print("\n" + ("PASS — safe to submit." if ok else "NOT SAFE — fix before submitting."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
