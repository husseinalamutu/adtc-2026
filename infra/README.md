# Benchmarking VM — target-class hardware

The audit runs on **4 vCPU / 8 GB RAM / integrated-GPU-only / Ubuntu 22.04**. Your local numbers
only count if they come from a box like this. Develop anywhere; **benchmark here**.

## 1. Create the VM (pick one — all ~$0.05–0.10/hr, destroy when done)
Match the profile: **4 vCPU, 8 GB RAM, NO GPU, Ubuntu 22.04 LTS**. Good matches:

| Provider | Instance | Notes |
|---|---|---|
| DigitalOcean | `c-4` (CPU-Optimized, 4 vCPU / 8 GB) | Dedicated vCPU ≈ steady TPS. Recommended. |
| Hetzner Cloud | `CPX31` (4 vCPU / 8 GB, AMD) | Cheapest; AMD EPYC ≈ Ryzen-class. Great value. |
| AWS EC2 | `c6i.xlarge` (4 vCPU / 8 GB) | Intel Ice Lake ≈ i5 11th-gen-ish. |
| GCP | `c2-standard-4` | Intel, dedicated. |

> ⚠️ Avoid "shared/burstable" tiers (AWS `t3`, DO basic) for the *final* numbers — noisy neighbors
> skew TPS and can trip the >50% audit-mismatch failure. Use dedicated-CPU for the numbers you submit.

## 2. Bootstrap it
```bash
scp infra/provision_benchmark_vm.sh  root@YOUR_VM_IP:~/
ssh root@YOUR_VM_IP 'bash provision_benchmark_vm.sh'
```
This installs build tools, builds **llama.cpp at a pinned commit**, and installs the **adtc-profiler**.

## 3. Baseline the candidates
```bash
scp benchmark/run_baseline.sh benchmark/telemetry_test.py  root@YOUR_VM_IP:~/adtc/
ssh root@YOUR_VM_IP 'cd ~/adtc && bash run_baseline.sh'
```
Copy the printed table into `benchmark/results/` and commit it. That table **locks our model size**.

## Pinning
`LLAMACPP_COMMIT` in `provision_benchmark_vm.sh` MUST match whatever llama.cpp revision the profiler
expects (check the profiler's `pyproject.toml` / README). Reproducibility depends on it.
