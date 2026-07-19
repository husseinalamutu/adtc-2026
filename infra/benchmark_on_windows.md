# Real x86 TPS benchmark — on your Windows PC (Dell Latitude 5420, i7-1185G7)

Your PC is a near-perfect match for the ADTC audit box: an 11th-gen Intel **4-core/8-thread
U-series** chip with **integrated Iris Xe** graphics, i.e. exactly the "8 GB commodity laptop
with integrated graphics" class the challenge targets. So the TPS you measure here should land
**within tolerance of the real audit** — this is the number that closes the 30% speed score.

We pin the container to **4 CPUs / 7.5 GB** and build llama.cpp with the audit's exact
**SIMD-disabled** flags, so we measure the same de-optimized binary the audit uses (not a faster
one). Two paths — **Docker is easiest**; WSL2-native is the fallback.

---

## What to move to the PC
1. **The repo** — `git clone <your repo URL>` on the PC (or copy the folder). The code is small.
2. **The model file** — `alamz-tech-sme-copilot-Q4_K_M.gguf` (1.93 GB). It's git-ignored, so cloning
   does NOT bring it. Transfer it separately (USB stick is the most reliable for 1.9 GB) into:
   `adtc-2026/submission/model/alamz-tech-sme-copilot-Q4_K_M.gguf`
   (Later we'll publish it to Hugging Face so `download_model.sh` fetches it automatically — but
   for this one-off benchmark, a USB copy is fastest.)

---

## Path A — Docker Desktop (recommended: reuses our validated harness, zero fiddling)

1. **Install Docker Desktop for Windows** (uses the WSL2 backend). During install, accept
   "Use WSL 2 instead of Hyper-V". Reboot if asked, then launch Docker Desktop once so the engine
   is running.
2. Open **Git Bash** (comes with Git for Windows) or a **WSL2 Ubuntu** terminal, `cd` into the repo.
3. Confirm the model is in place: `ls -la submission/model/*.gguf` (should show ~1.9 GB).
4. Run:
   ```bash
   bash docker/run_local_emulation.sh
   ```
   It builds the image (llama.cpp with audit flags + the profiler; ~3-5 min first time) and runs
   the profiler pinned to 4 CPUs / 7.5 GB. Because your host is x86-64, the container is native
   x86-64 — so the printed `tps_generation` is a **REAL** number and the script will say so
   (`✅ REAL x86 number`), unlike on the Mac.

**Read the output:** `peak_rss_mb` should be well under 6500; `tps_generation` is informational —
speed is scored **relative to the fastest submission** (`S_perf = 100·TPS/TPS_max`, no floor).
Paste the three lines back.
> **MEASURED 2026-07-12:** peak_rss 2052 MB, **2.75 tok/s** (`-t 4`; ~2.0 auto-threads),
> throttled=false. ~8-10× below AVX2 numbers because the audit build disables all SIMD —
> this hits every submission equally; see STRATEGY.md "Scoring math" and
> build/results/model_size_tradeoff_2026-07-13.md for why we kept the 3B anyway.

---

## Path B — WSL2 native (fallback if you'd rather not install Docker)

1. Enable WSL2 + Ubuntu (one-time, in an **admin PowerShell**): `wsl --install -d Ubuntu`, reboot,
   set a username/password when Ubuntu first launches.
2. In the Ubuntu shell, `cd` to the repo (your Windows drive is under `/mnt/c/...`), then:
   ```bash
   sudo bash infra/provision_benchmark_vm.sh    # builds llama.cpp (audit flags) + installs adtc-profiler (~5 min)
   export PATH="$HOME/adtc/llama.cpp/build/bin:$PATH"   # so the profiler finds llama-bench
   cd benchmark && python3 telemetry_test.py --submission ../submission
   ```
   `telemetry_test.py` prints PASS/FAIL against the RSS ceiling (TPS is reported informationally).

> WSL2 note: WSL2 by default may see all 8 threads and more RAM than the audit. For an
> audit-faithful number, cap it: create `C:\Users\<you>\.wslconfig` with:
> ```
> [wsl2]
> processors=4
> memory=8GB
> ```
> then `wsl --shutdown` and reopen Ubuntu. (Path A's Docker `--cpus=4` already handles this.)

---

## Interpreting the result (updated 2026-07-13 — the original floor-based guidance was wrong)
- There is **no speed floor**: `S_perf = 100·TPS/TPS_max`, relative to the fastest submission.
  The audit's scalar (SIMD-off) build caps ANY 3B near ~2-3 tok/s on this chip — the original
  "20-30 tok/s even de-optimized" prediction did not account for full-scalar kernels.
- **peak_rss** should read ~2.0 GB (matches our Mac profile; memory is architecture-independent).
- Our recorded numbers (2026-07-12): rss 2052 MB, 2.75 tok/s, no throttling — final, in REPORT.md.
