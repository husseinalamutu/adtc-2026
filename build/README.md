# Build recipe — fine-tune → merge → GGUF → imatrix → Q4_K_M

One command should rebuild the exact submitted GGUF from the base model + dataset (see
`STRATEGY.md` reproducibility checklist). This directory is that recipe.

## Hardware reality check

This Mac is an **Apple M2 with 8 GB unified memory**. That is tight for fine-tuning:

- MLX's unified-memory model + QLoRA (4-bit base, small LoRA adapters, only the adapters
  train) is the only realistic path on this machine — full fine-tuning of a 3–4B model needs
  far more than 8 GB.
- Even with QLoRA, **a 4B model is risky here** (4-bit base alone is ~2.2–2.5 GB; add
  activations, optimizer state for the adapters, tokenizer, KV cache during eval, and MLX/OS
  overhead, and headroom gets thin at longer sequence lengths).
- **Default to the 3B fallback** from `STRATEGY.md` §4 (Qwen-3B-class / SmolLM3-3B /
  Llama-3.2-3B) unless `benchmark/run_baseline.sh` on the real target-class VM shows a 4B
  model clearing ~18+ TPS *and* this Mac proves it can actually complete a LoRA run on it
  without swapping. Test 4B only after 3B works end-to-end.
- If training OOMs or swaps heavily: drop `--max-seq-length`, drop `--batch-size` to 1, raise
  `--grad-checkpoint`, or reduce LoRA rank/layers before giving up on the model size.

## Pipeline

```
base model (HF, bf16)
   │  mlx_lm.lora  (QLoRA: 4-bit base + trainable LoRA adapters, on data/out/train.jsonl)
   ▼
LoRA adapters
   │  mlx_lm.fuse  (merge adapters into the base weights)
   ▼
merged fp16 model (MLX format)
   │  mlx_lm.convert --upload / or HF safetensors export
   ▼
HF-format merged model
   │  llama.cpp convert_hf_to_gguf.py
   ▼
GGUF f16
   │  llama-imatrix  (calibrate on a domain-representative text sample)
   ▼
imatrix.dat
   │  llama-quantize --imatrix imatrix.dat  Q4_K_M
   ▼
submission/model/*.gguf  ──►  smoke test (local) ──►  full profiler run (target-class VM)
```

Scripts, run in order:

| Script | What it does |
|---|---|
| `00_setup.sh` | Installs `mlx-lm`; builds a local (Metal-accelerated) llama.cpp for dev-loop use only — **not** the benchmarking build (that's `infra/provision_benchmark_vm.sh` on the x86 VM; numbers from this Mac are never submitted). |
| `01_finetune_mlx.sh` | Runs QLoRA fine-tuning via `mlx_lm.lora` on `data/out/train.jsonl`. Config in `config.yaml`. |
| `02_merge.sh` | Fuses the LoRA adapters into the base weights (`mlx_lm.fuse`), exports HF-format safetensors. |
| `03_to_gguf.sh` | Converts the merged HF model to GGUF f16 via llama.cpp's `convert_hf_to_gguf.py`. |
| `04_imatrix_quantize.sh` | Computes an importance matrix from `calibration_text.txt` (domain-representative — pulled from `data/out/train.jsonl`), then quantizes to Q4_K_M. |
| `05_smoke_test.sh` | Runs a couple of prompts through the quantized GGUF locally (Metal) to sanity-check it isn't broken. **Not** a substitute for `benchmark/telemetry_test.py` on the target-class VM. |

## Config

All run parameters (model id, LoRA rank, learning rate, context length, quant type) live in
`config.yaml` — mirror any changes into `submission/metadata.json` so your claims match your
artifact (per `STRATEGY.md`'s "config over hardcoding" rule).

## Reproducibility

- Pin the base model to a specific HF commit hash in `config.yaml` — not just the repo name.
- Pin the llama.cpp commit used for conversion/quantization (`00_setup.sh` records it).
- `data/out/train.jsonl` must be committed or regeneratable byte-for-byte from
  `data/build_dataset.py` with the same seed — check this before trusting a rebuild.
