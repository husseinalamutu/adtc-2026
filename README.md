# ALAMZ TECH SME Copilot — Offline Back-Office Copilot for Nigerian SMEs

Entry for the [Africa Deep Tech Challenge 2026](https://africadeeptech.org/challenge-2026/)
(Laptop LLM Challenge). A single Q4_K_M GGUF, fine-tuned for informal-sector SME back-office
work — invoicing, mobile-money reconciliation, and Nigeria's 2025 tax rules — running 100%
offline via llama.cpp on an 8 GB laptop with no GPU.

**Read [`REPORT.md`](REPORT.md)** for the problem, design decisions, constraints and benchmarks.

## Evaluating this submission

```bash
bash download_model.sh          # fetches the 1.93 GB GGUF into model/
adtc-profiler run --submission . --mode participant --output submission.json --skip-accuracy
```

`metadata.json` declares the domain, the two test prompts, and `_runtime.model_path`.

## Repo layout

| Path | Purpose |
|---|---|
| `metadata.json`, `download_model.sh`, `REPORT.md`, `model/` | The submission itself. |
| `demo/` | The deterministic finance engine and the offline app — the load-bearing cross-disciplinary pairing declared in `metadata.json`. |
| `build/` | Fine-tune → merge → GGUF → imatrix → quantize recipe, plus the three evaluation harnesses. |
| `data/` | Training-data generators, the verified Nigeria-2025 fact base, and the corpus. |

## Running the demo app

```bash
bash demo/app/run_demo.sh       # llama-server + app -> http://127.0.0.1:8090
```

Windows instructions: [`demo/RUN_ON_WINDOWS.md`](demo/RUN_ON_WINDOWS.md).
Upload a spreadsheet of transactions and ask what happened this month, what looks unusual,
whether next month's cash covers the suppliers, and what to do about it. Every figure is
computed by the engine; the model only explains it. English, Hausa and Igbo.

## Reproducing the model

```bash
bash build/build_final.sh       # fuse -> f16 GGUF -> imatrix -> Q4_K_M
```

Evaluation gates (all run against the quantized GGUF, greedy decoding):

```bash
python3 build/fact_eval.py       # 37 Nigeria tax questions
python3 build/arith_eval.py      # 12 arithmetic cases
python3 build/narration_eval.py  # 5 narration-fidelity checks
```

## Licence

Code MIT; model weights under the Qwen Research Licence (non-commercial) — see
[`LICENSE`](LICENSE) and REPORT.md's Licensing section.
