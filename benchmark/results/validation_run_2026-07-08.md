# Pipeline validation run — 2026-07-08

First full end-to-end build (01→05) on **templated-only** data (2,546 train examples), Qwen2.5-3B
4-bit QLoRA, 120-iter validation adapter. Purpose: prove the whole chain works + get real
memory telemetry on OUR model. NOT the final submission model.

## Build chain result: ✅ all stages pass
- 01 fine-tune (MLX QLoRA): val loss 1.950 → 0.412, train 1.348 → 0.357, peak 3.93 GB
- 02 merge (`mlx_lm.fuse --dequantize`): fp16 fused, 6.17 GB, 0 residual quant tensors
- 03 convert → GGUF f16: 6.18 GB, 434 tensors
- 04 imatrix (CPU) + Q4_K_M quantize: **model-Q4_K_M.gguf = 1.93 GB** (4.99 BPW)
- 05 smoke test: correct domain answer — reconciliation prompt → "Yes, it is settled…" ✓

## Bugs found & fixed during validation (would have blocked the real run)
1. `mlx_lm.fuse` on a 4-bit base keeps weights 4-bit → `convert_hf_to_gguf.py` can't read MLX
   quant format. Fix: `--dequantize` (now permanent in 02_merge.sh).
2. `llama-imatrix` on the 6.2 GB f16 model via Metal OOMs the 8 GB Mac. Fix: `-ngl 0` CPU-only
   + small batch (now permanent in 04_imatrix_quantize.sh).
3. llama.cpp b9913 defaults `-p` to interactive mode and hangs. Fix: `-no-cnv -st` (05).

## Real telemetry (adtc-profiler, local Docker emulation)
| Metric | Value | Verdict |
|---|---|---|
| **memory.peak_rss_mb** | **2025.7 (~2.0 GB)** | ✅ TRUSTWORTHY. Huge margin under 6500 ceiling / 7168 DQ. S_eff ≈ (7168−2026)/7168 ≈ **72/100**. |
| memory.steady_state_rss_mb | 1862.3 (~1.8 GB) | ✅ |
| model_info.architecture | qwen2 | ✅ recognized |
| model_info.params_match | True | ✅ |
| cpu_thermal.throttled | False | ✅ (but real thermal signal needs the x86 VM under sustained load) |
| throughput.tokens_per_second_generation | 0.35 | ❌ MEANINGLESS — ARM + all-SIMD-disabled audit-parity build. TPS MUST come from the real x86 VM (task #7). |
| environment.ram_gb (container) | 3.8 | Local Docker VM is RAM-limited; our 2.0 GB model still fits fine. Real audit container is 7.5 GB. |

## Bottom line
The build pipeline is proven and produces a working, correct, ~2 GB Q4_K_M GGUF with a massive
efficiency margin and zero OOM risk. The ONLY unknown left is real x86 TPS (the 30% speed score),
which the local Mac/Docker fundamentally cannot measure — that's the job of the target-class VM.
