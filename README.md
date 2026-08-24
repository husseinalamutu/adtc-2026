# ADTC 2026 — Offline Back-Office Copilot for Nigerian SMEs

Our entry for the [Africa Deep Tech Challenge 2026](https://africadeeptech.org/challenge-2026/)
(Laptop LLM Challenge). A single Q4_K_M GGUF, fine-tuned for informal-sector SME back-office work
(invoicing, mobile-money reconciliation, local tax/compliance), running 100% offline via llama.cpp
on an 8 GB laptop.

**Read [`REPORT.md`](REPORT.md) first** — it covers the problem, design decisions, constraints and benchmarks.

## Repo layout
| Dir | Purpose |
|---|---|
| `infra/` | Provision a target-class benchmarking VM (4 vCPU / 8 GB / no GPU). |
| `benchmark/` | Baseline candidate models; the telemetry regression test (RSS < 6.5 GB; TPS informational — scored relative to the field). |
| `build/` | Fine-tune → merge → GGUF → imatrix → quantize recipe (one command rebuilds the exact model). |
| `demo/` | Deterministic finance engine + the offline app (the load-bearing pairing). |
| `demo/` | Offline demo app (LLM + finance/tax integration) for the video & live defense. |
| `submission/` | What gets forked into the official template: `metadata.json`, `download_model.sh`, `REPORT.md`. |

## Current status — Week 0
- [x] Strategy locked, scoring/rules verified against live profiler + template.
- [x] Benchmarking infra + telemetry test written.
- [ ] Fork official template; register team on Devpost.
- [ ] Stand up cloud VM → `run_baseline.sh` → **lock model size**.

## Quick start (once you have a VM IP)
```bash
scp infra/provision_benchmark_vm.sh root@IP:~/ && ssh root@IP 'bash provision_benchmark_vm.sh'
scp benchmark/*.{sh,py} root@IP:~/adtc/ && ssh root@IP 'cd ~/adtc && bash run_baseline.sh'
```
