# The syntactically valid default keeps Dockerfile static checks useful. The
# build helper always overrides it with a published runpod-jobrunner digest;
# an unoverridden build fails when the runner payload is copied.
ARG RUNPOD_JOBRUNNER_IMAGE=runpod/base:1.1.0-ubuntu2404@sha256:8fafffd0c67a48117dff09031ed16e79c0a83cc6996472f4b4dcb76343102a66
FROM ${RUNPOD_JOBRUNNER_IMAGE} AS jobrunner

# Official RunPod PyTorch image, linux/amd64 manifest resolved 2026-07-31.
FROM runpod/pytorch@sha256:3e874356857adfa3e8faa3fd913b65bd127f77a0fe2e489513e7775e1c1e16b1

ARG LLAMA_CPP_COMMIT=000547513f1530346ecd163db8b3e13962949961
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/opt/striatum-qwen35b \
    RUNPOD_JOBRUNNER_RELEASE_PATH=/opt/runpod-jobrunner/release.json \
    STRIATUM_MODEL_DIR=/workspace/models/Qwen3.6-35B-A3B-995ad96e \
    STRIATUM_BASE_GGUF=/workspace/models/Qwen3.6-35B-A3B-995ad96e/gguf/base-bf16.gguf \
    MAX_JOBS=2 \
    PATH=/opt/runpod-jobrunner/venv/bin:${PATH}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential ca-certificates cmake git libcurl4-openssl-dev openssh-client \
       python3-venv tini \
    && ssh_keygen_help="$(ssh-keygen -? 2>&1 || :)" \
    && printf '%s\n' "$ssh_keygen_help" | grep -Fq -- '-Y sign' \
    && rm -rf /var/lib/apt/lists/*

# Copy the already-published controller-matched runner by immutable image
# digest. No private source checkout enters the build context.
COPY --from=jobrunner /opt/runpod-jobrunner /opt/runpod-jobrunner

WORKDIR /tmp/striatum-qwen35b-build
COPY requirements.txt requirements-gpu.txt ./
RUN /opt/runpod-jobrunner/venv/bin/python -m pip install --no-cache-dir -r requirements.txt \
    && /opt/runpod-jobrunner/venv/bin/python -m pip install --no-cache-dir \
       --no-build-isolation -r requirements-gpu.txt \
    && /opt/runpod-jobrunner/venv/bin/python -m pip check \
    && /opt/runpod-jobrunner/venv/bin/python -c \
       "import importlib; modules = ('torch', 'torchvision', 'transformers', 'peft', 'accelerate', 'datasets', 'safetensors', 'flash_attn', 'fla', 'causal_conv1d', 'bitsandbytes', 'tilelang', 'tvm_ffi', 'liger_kernel.transformers.model.qwen3_5_moe'); [importlib.import_module(module) for module in modules]"

RUN cuda_stub_dir=/usr/local/cuda/lib64/stubs \
    && test -f "$cuda_stub_dir/libcuda.so" \
    && test ! -e "$cuda_stub_dir/libcuda.so.1" \
    && ln -s libcuda.so "$cuda_stub_dir/libcuda.so.1" \
    && git clone https://github.com/ggml-org/llama.cpp.git /opt/llama.cpp \
    && git -C /opt/llama.cpp checkout "$LLAMA_CPP_COMMIT" \
    && cmake -S /opt/llama.cpp -B /opt/llama.cpp/build \
       -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=90 \
       -DCMAKE_EXE_LINKER_FLAGS="-Wl,-rpath-link,$cuda_stub_dir" \
       -DLLAMA_CURL=OFF \
    && cmake --build /opt/llama.cpp/build --config Release -j2 \
       --target llama-cli llama-quantize llama-gguf-split \
    && rm "$cuda_stub_dir/libcuda.so.1" \
    && test ! -e "$cuda_stub_dir/libcuda.so.1" \
    && readelf -d /opt/llama.cpp/build/bin/libggml-cuda.so \
       > /tmp/libggml-cuda.dynamic \
    && grep -Fq 'Shared library: [libcuda.so.1]' \
       /tmp/libggml-cuda.dynamic \
    && ! grep -Fq "$cuda_stub_dir" /tmp/libggml-cuda.dynamic \
    && readelf -d /opt/llama.cpp/build/bin/llama-cli \
       > /tmp/llama-cli.dynamic \
    && ! grep -Fq "$cuda_stub_dir" /tmp/llama-cli.dynamic \
    && rm /tmp/libggml-cuda.dynamic /tmp/llama-cli.dynamic

RUN mkdir -p /opt/striatum-qwen35b/jobs/qwen35b_moe /opt/striatum-qwen35b/bin
COPY *.py *.json /opt/striatum-qwen35b/jobs/qwen35b_moe/
COPY smoke/ /opt/striatum-qwen35b/jobs/qwen35b_moe/smoke/
COPY network-volume-assets.sha256 /opt/striatum-qwen35b/jobs/qwen35b_moe/
COPY bin/ /opt/striatum-qwen35b/bin/
RUN chmod 0555 /opt/striatum-qwen35b/bin/* \
    && /opt/runpod-jobrunner/venv/bin/python -m jobs.qwen35b_moe.flash_qla_smoke --validate-install \
    && rm -rf /tmp/striatum-qwen35b-build

LABEL org.opencontainers.image.title="Striatum Qwen3.6-35B-A3B PEFT runner"

EXPOSE 22 8080
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/runpod-jobrunner/entrypoint"]
