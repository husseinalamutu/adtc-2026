---
license: apache-2.0
base_model: Qwen/Qwen2.5-3B-Instruct
language:
  - en
pipeline_tag: text-generation
tags:
  - gguf
  - llama.cpp
  - qlora
  - finance
  - nigeria
  - offline
  - africa-deep-tech-2026
---

# ALAMZ TECH SME Copilot (GGUF, Q4_K_M)

An **offline back-office copilot for African small businesses** — invoices and quotes,
mobile-money (MoMo/M-Pesa) reconciliation, and **Nigeria's 2025 Tax Reform Acts** —
built for the 8 GB laptops with integrated graphics that SMEs actually own.
ALAMZ TECH's entry to the **Africa Deep Tech Challenge 2026** (domain: corporate/enterprise).

- **Base**: Qwen2.5-3B-Instruct, QLoRA fine-tune (rank 32, all layers, all attn+MLP modules)
- **Format**: GGUF **Q4_K_M with a domain-calibrated importance matrix** — 1.93 GB
- **Runtime**: [llama.cpp](https://github.com/ggml-org/llama.cpp) — CPU-only is fine
- **Peak RAM**: ~2.0 GB measured (audit-style container, 4 CPUs / 7.5 GB)
- **Everything** (data pipeline, training, quantization, evals) was built on one 8 GB M2 laptop

## Why it exists

Nigeria rewrote its tax law in 2025 — *after* every mainstream base model's training data.
Stock models confidently quote repealed rates (5% VAT, ₦25M small-company threshold).
This model was fine-tuned on a **hand-curated, grep-verified fact base** built from the
OCR'd official Gazette (Nigeria Tax Act 2025 + Tax Administration Act 2025), with every
training number either confirmed verbatim in the Act or corroborated by 2+ professional
sources, and all arithmetic in the training data **computed programmatically, never generated**.

Measured on a 37-question adversarial fact eval (paraphrases, casual/Pidgin phrasings,
adversarial framings, greedy decoding): **24/37 (base-prior v1) → 34/37 (this model)**,
including: VAT 7.5% · small-company 0% CIT (≤₦100M turnover, ≤₦250M fixed assets) ·
standard 30% CIT · Development Levy 4% with the small-company exemption · the
professional-services exclusion. Full methodology and results in the
[GitHub repo](https://github.com/husseinalamutu/adtc-2026).

## Run it

```bash
# chat UI at http://localhost:8080
llama-server -m alamz-tech-sme-copilot-Q4_K_M.gguf --port 8080 -c 2048

# or one-shot
llama-cli -m alamz-tech-sme-copilot-Q4_K_M.gguf -p "What is the current VAT rate in Nigeria?"
```

Try: *"A customer paid NGN 127,500 by MoMo. They owe INV-114 (NGN 85,000) and INV-121
(NGN 42,500). Does this clear both?"*

In the full product this model is **paired with a deterministic finance module**
(mobile-money statement parser, double-entry ledger, citeable tax-rule engine — same
verified fact base) that computes every figure; the model narrates. See the demo app in
the GitHub repo.

## Limitations

- Nigeria-2025 depth is the specialty; other jurisdictions get general reasoning only.
- Like any small LLM it can err on multi-step arithmetic — the paired module exists
  precisely for that; don't ship model-only math to production.
- **Not professional tax advice.** Confirm specifics with FIRS/NRS or a licensed accountant.

*sha256 `8ea4493dc50391a48cfc400a447c23dc50c584845c11ad0c999b7b030a5d773d` — verify your download.*
