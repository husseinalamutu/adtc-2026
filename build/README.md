# Build recipe — fine-tune → merge → GGUF → imatrix → Q4_K_M

One command should rebuild the exact submitted GGUF from the base model + dataset (see
`REPORT.md` reproducibility section). This directory is that recipe.

## Hardware reality check

This Mac is an **Apple M2 with 8 GB unified memory**. It comfortably does a **full-quality**
3B QLoRA fine-tune — but ONLY because we use a genuine 4-bit base. Measured 2026-07-08:

- **Use the 4-bit base, never the bf16 one.** Pointing `mlx_lora_config.yaml`'s `model:` at the
  full-precision `Qwen/Qwen2.5-3B-Instruct` loads **6.17 GB of bf16 weights** (that's not QLoRA
  — the base isn't quantized), peaks at 6.79 GB, forces `num_layers=4`/`seq=384`, AND corrupts
  mlx_lm's own console loss/token metrics. The pre-quantized `mlx-community/Qwen2.5-3B-Instruct-4bit`
  base is **1.74 GB** — get it via `download_base_4bit.sh`.
- **With the 4-bit base, full quality fits at 3.77 GB peak** (~3 GB headroom): all 36 layers
  adapt, all 7 attention+MLP LoRA target modules, rank 32, seq 1024. These winning settings are
  already in `mlx_lora_config.yaml`. No cloud GPU needed.
- **A 4B QLoRA base would very likely also fit locally now** (4-bit 4B ≈ 2.2–2.5 GB + our
  ~2 GB of activations ≈ well under 8 GB). The real gate on 4B is the VM speed floor
  on target-class x86 hardware, not this Mac's memory.
- To probe headroom for any new config: run `mlx_lora_config.probe.yaml` (short run) and read the
  `Peak mem` line — that reading is trustworthy. Stay under ~7.0 GB peak.
- If a config ever OOMs: lower `max_seq_length`, then `num_layers`, then LoRA `rank`, in that order.

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
model/*.gguf  ──►  smoke test (local) ──►  full profiler run (target-class VM)
```

Scripts, run in order:

| Script | What it does |
|---|---|
| `00_setup.sh` | Installs `mlx-lm`; builds a local (Metal-accelerated) llama.cpp for dev-loop use only — **not** the benchmarking build (audited numbers come from target-class x86 hardware; numbers from this Mac are never submitted). |
| `01_finetune_mlx.sh` | Runs QLoRA fine-tuning via `mlx_lm.lora` on `data/out/train.jsonl`. Config in `config.yaml`. |
| `02_merge.sh` | Fuses the LoRA adapters into the base weights (`mlx_lm.fuse`), exports HF-format safetensors. |
| `03_to_gguf.sh` | Converts the merged HF model to GGUF f16 via llama.cpp's `convert_hf_to_gguf.py`. |
| `04_imatrix_quantize.sh` | Computes an importance matrix from `calibration_text.txt` (domain-representative — pulled from `data/out/train.jsonl`), then quantizes to Q4_K_M. |
| `05_smoke_test.sh` | Runs a couple of prompts through the quantized GGUF locally (Metal) to sanity-check it isn't broken. **Not** a substitute for profiling on target-class x86 hardware. |

## Config

All run parameters (model id, LoRA rank, learning rate, context length, quant type) live in
`config.yaml` — mirror any changes into `metadata.json` so your claims match your
artifact (config over hardcoding).

## Reproducibility

- Pin the base model to a specific HF commit hash in `config.yaml` — not just the repo name.
- Pin the llama.cpp commit used for conversion/quantization (`00_setup.sh` records it).
- `data/out/train.jsonl` must be committed or regeneratable byte-for-byte from
  `data/build_dataset.py` with the same seed — check this before trusting a rebuild.
