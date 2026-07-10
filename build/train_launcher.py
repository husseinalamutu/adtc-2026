#!/usr/bin/env python3
"""mlx_lm.lora wrapper that caps Metal memory before training starts.

Why: macOS 26.x IOGPUFamily has a refcount race ("completeMemory() prepare count underflow",
IOGPUMemory.cpp:550, Apple FB22091885) that KERNEL-PANICS the whole Mac under sustained large
Metal workloads — it killed this machine mid-QLoRA on 2026-07-10 (pid was this trainer).
mlx core is already current (0.32.0); the reliable community workaround is bounding
allocations so the allocator recycles buffers instead of growing/freeing unboundedly.
Observed training peak is ~4.2 GB on this 8 GB M2, so the caps below leave headroom
while keeping MLX well away from the wired-memory cliff.
"""
import sys

import mlx.core as mx

GB = 1 << 30
mx.set_memory_limit(5 * GB)          # hard ceiling on live Metal allocations
mx.set_cache_limit(1 * GB)           # bound the buffer cache (the churn that triggers the race)
try:
    mx.set_wired_limit(int(3.5 * GB))  # stay far below the 8 GB machine's wired cliff
except AttributeError:
    pass  # older mlx without the API

from mlx_lm import lora

if __name__ == "__main__":
    lora.main()
