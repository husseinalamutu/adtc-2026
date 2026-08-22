# Local "emulated VM" — as close a mirror of the OFFICIAL adtc-profiler Dockerfile as we
# can get (github.com/Africa-Deep-Tech-Foundation/adtc-profiler, profiler/Dockerfile),
# fetched and verified 2026-07-07. Same base images, same CMake flags, same layer structure.
#
# What this gets you vs. what it doesn't:
#   - RAM ceiling / OOM behavior: TRUSTWORTHY (docker --memory=7.5g is a real cgroup limit,
#     enforced identically regardless of host CPU architecture).
#   - Profiler pipeline correctness (does it find metadata.json, parse the GGUF header,
#     write a schema-valid report): TRUSTWORTHY.
#   - TPS / throughput numbers: NOT TRUSTWORTHY unless built with --platform linux/amd64
#     (QEMU x86 emulation — correct instruction-set behavior, but 5-20x slower than real
#     hardware, so the raw TPS number itself is still meaningless — only use it to confirm
#     the model doesn't crash under x86 codepaths). On native arm64 (fast, default on this
#     Mac), TPS numbers are Apple Silicon numbers and have NO relationship to the x86 audit
#     box — use them only to compare candidate models against EACH OTHER, never absolutely.
#   - Final submitted TPS numbers MUST come from infra/provision_benchmark_vm.sh on a real
#     x86 target-class cloud VM. This container is a pre-flight check, not a replacement.

ARG LLAMACPP_REF=master

# -----------------------------------------------------------------------------
# Stage 1: build llama.cpp — flags copied VERBATIM from the official Dockerfile.
# -----------------------------------------------------------------------------
FROM debian:bookworm-slim AS llama-build

ARG LLAMACPP_REF
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch "${LLAMACPP_REF}" \
      https://github.com/ggml-org/llama.cpp.git /src/llama.cpp \
    && cd /src/llama.cpp \
    && cmake -B build \
        -DBUILD_SHARED_LIBS=OFF \
        -DGGML_NATIVE=OFF \
        -DGGML_AVX=OFF \
        -DGGML_AVX2=OFF \
        -DGGML_AVX512=OFF \
        -DGGML_FMA=OFF \
        -DGGML_F16C=OFF \
        -DGGML_BLAS=OFF \
        -DGGML_CUDA=OFF \
        -DGGML_METAL=OFF \
    && cmake --build build --config Release --target llama-bench llama-cli llama-server -j2

# -----------------------------------------------------------------------------
# Stage 2: profiler runtime
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# build-essential + cmake: adtc-profiler pulls in llama-cpp-python, which compiles a native
# extension via scikit-build-core/CMake at install time. This worked without a compiler here
# when the Dockerfile was last verified (2026-07-07) because a prebuilt wheel matched this
# platform then; it no longer does, so the runtime stage needs to build it like llama-build does.
RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates lm-sensors libgomp1 build-essential cmake \
    && rm -rf /var/lib/apt/lists/*

COPY --from=llama-build /src/llama.cpp/build/bin/llama-bench  /usr/local/bin/
COPY --from=llama-build /src/llama.cpp/build/bin/llama-cli    /usr/local/bin/
COPY --from=llama-build /src/llama.cpp/build/bin/llama-server /usr/local/bin/

RUN pip install --no-cache-dir "git+https://github.com/Africa-Deep-Tech-Foundation/adtc-profiler.git"

WORKDIR /work
ENTRYPOINT ["adtc-profiler"]
