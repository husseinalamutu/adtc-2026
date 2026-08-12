#!/usr/bin/env python3
"""Turn a profiler report into the ADTC score components.

Two of the three axes are computable by us; one is not, and the difference matters:

  S_eff  = 100 × (7 GB − peak RSS) / 7 GB          -> EXACT. Memory is architecture-independent,
                                                      so the Mac profiler run is as valid as the
                                                      audit's own measurement.
  S_perf = 100 × (TPS_act ÷ TPS_max)               -> NOT computable. TPS_max is "highest speed
                                                      across all submissions" (challenge site), so
                                                      it depends on every other team. We report
                                                      our measured TPS and show the sensitivity.
  S_acc  = automated benchmarks + judge panel      -> NOT computable. Our own gates are a proxy,
                                                      not the official number.

  S_total = 0.50·S_acc + 0.30·S_perf + 0.20·S_eff − P_thermal

TPS SOURCE: pass --tps with the figure measured on AUDIT-CLASS x86. The Mac's arm64 number is
meaningless for scoring and is ignored (with a warning) if it is all that's available.

Usage:
  python3 score_estimate.py                      # uses artifacts/local_report.json + Dell TPS
  python3 score_estimate.py --tps 2.75 --acc 80  # explore a total under an assumed accuracy
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUDGET_GB = 7.0
DQ_GB = 7.0
THERMAL_PENALTY = 10.0
# Measured on the Dell (i7-1185G7, Docker 4 CPUs/7.5 GB, audit-exact SIMD-disabled build).
AUDIT_CLASS_TPS = 2.75


def s_eff(peak_rss_mb: float) -> float:
    return 100.0 * (BUDGET_GB - peak_rss_mb / 1024) / BUDGET_GB


def s_perf(tps_act: float, tps_max: float) -> float:
    return 100.0 * tps_act / tps_max if tps_max > 0 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=str(REPO / "artifacts/local_report.json"))
    ap.add_argument("--tps", type=float, default=AUDIT_CLASS_TPS,
                    help="TPS measured on audit-class x86 (NOT the Mac figure)")
    ap.add_argument("--acc", type=float, default=None,
                    help="assumed S_acc (0-100) to illustrate a total")
    args = ap.parse_args()

    report = json.loads(Path(args.report).read_text())
    rss = report["memory"]["peak_rss_mb"]
    mac_tps = report["throughput"]["tokens_per_second_generation"]
    throttled = report["cpu_thermal"]["throttled"]
    arch = report.get("model_info", {}).get("architecture", "?")
    params_ok = report.get("model_info", {}).get("params_match")

    eff = s_eff(rss)
    print("=" * 66)
    print("PROFILER REPORT")
    print("=" * 66)
    print(f"  peak RSS         {rss:,.0f} MB  ({rss/1024:.3f} GB)")
    print(f"  architecture     {arch}   params_match={params_ok}")
    print(f"  throttled        {throttled}")
    print(f"  TPS (this host)  {mac_tps}  <- arm64; NOT scoreable")
    print()
    print("SCORES")
    print(f"  S_eff  = 100 x (7 - {rss/1024:.3f}) / 7 = {eff:.1f} / 100        [EXACT]")
    print(f"           contributes 0.20 x {eff:.1f} = {0.20 * eff:.1f} points")
    if rss / 1024 >= DQ_GB:
        print("  !! OVER THE 7 GB LINE — instant disqualification")
    print()
    print(f"  S_perf = 100 x ({args.tps} / TPS_max)                    [NOT SELF-COMPUTABLE]")
    print("           TPS_max = fastest submission across all teams, so:")
    print(f"           {'TPS_max':>10} {'S_perf':>8} {'pts (x0.30)':>12}")
    for tps_max in (args.tps, 4, 6, 10, 15, 25):
        if tps_max < args.tps:
            continue
        sp = s_perf(args.tps, tps_max)
        tag = "  <- if we are the fastest" if abs(tps_max - args.tps) < 1e-9 else ""
        print(f"           {tps_max:>10.2f} {sp:>8.1f} {0.30 * sp:>12.1f}{tag}")
    print()
    if args.acc is not None:
        print(f"  S_acc  = {args.acc:.1f} (assumed — official figure is benchmarks + judge panel)")
        print(f"           {'TPS_max':>10} {'S_total':>9}")
        for tps_max in (args.tps, 6, 15):
            total = 0.50 * args.acc + 0.30 * s_perf(args.tps, tps_max) + 0.20 * eff
            total -= THERMAL_PENALTY if throttled else 0
            print(f"           {tps_max:>10.2f} {total:>9.1f}")
        print()
    print("REPORT ON THE DEVPOST FORM:")
    print(f"  Seff  -> {eff:.1f}")
    print(f"  Sperf -> {args.tps}  (measured TPS; the ratio needs TPS_max, which entrants")
    print("           cannot know — flagged to the organizers)")


if __name__ == "__main__":
    main()
