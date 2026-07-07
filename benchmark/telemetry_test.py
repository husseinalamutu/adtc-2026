#!/usr/bin/env python3
"""
The single most valuable test in the project. Runs the official adtc-profiler in participant
mode and asserts we're safely inside the two limits that zero us out or cost 10 points:

    peak_rss_gb  < 6.5   (hard DQ line is 7.0; we keep margin for the +/-15% audit variance)
    tps_generation >= 16 (speed floor is 15; margin for the +/-25% audit variance)

Run on target-class HW after every model rebuild:
    python3 telemetry_test.py --metadata ../submission/metadata.json
Exit code 0 = safe to submit; non-zero = fix before submitting.
"""
import argparse, json, subprocess, sys, shutil

RSS_CEILING_GB = 6.5
TPS_FLOOR      = 16.0

def run_profiler(metadata_path: str) -> dict:
    if not shutil.which("adtc-profiler"):
        sys.exit("adtc-profiler not found — run infra/provision_benchmark_vm.sh first.")
    # --skip-accuracy: accuracy is judged officially, not in the local tool.
    cmd = ["adtc-profiler", "run", "--mode", "participant",
           "--metadata", metadata_path, "--skip-accuracy", "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"profiler failed:\n{proc.stderr or proc.stdout}")
    # Be tolerant of extra log lines: grab the last JSON object printed.
    out = proc.stdout.strip()
    start = out.rfind("{")
    return json.loads(out[start:])

def get(d: dict, *keys, default=None):
    for k in keys:
        if k in d:
            return d[k]
    return default

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", default="submission/metadata.json")
    ap.add_argument("--from-json", help="skip the run; assert against an existing profiler JSON")
    args = ap.parse_args()

    data = json.load(open(args.from_json)) if args.from_json else run_profiler(args.metadata)

    rss = float(get(data, "peak_rss_gb", "peak_rss", "rss_gb", default=99))
    tps = float(get(data, "tps_generation", "tokens_per_second_generation", "tps", default=0))
    thermal = bool(get(data, "thermal_throttled", "throttled", default=False))

    ok = True
    print(f"peak_rss_gb    = {rss:.2f}   (ceiling {RSS_CEILING_GB}, DQ at 7.0)")
    if rss >= RSS_CEILING_GB:
        print("  FAIL: too close to the 7 GB OOM/DQ line."); ok = False
    print(f"tps_generation = {tps:.1f}   (floor {TPS_FLOOR}, full marks at 15)")
    if tps < TPS_FLOOR:
        print("  FAIL: below the speed-margin floor."); ok = False
    print(f"thermal        = {'THROTTLED (-10!)' if thermal else 'ok'}")
    if thermal:
        print("  FAIL: thermal throttling detected."); ok = False

    print("\n" + ("PASS — safe to submit." if ok else "NOT SAFE — fix before submitting."))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
