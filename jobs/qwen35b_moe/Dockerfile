# The syntactically valid default keeps Dockerfile static checks useful. The
# build helper always overrides it with a published runpod-jobrunner digest;
# an unoverridden build fails when the runner payload is copied.
ARG RUNPOD_JOBRUNNER_IMAGE=runpod/base:1.1.0-ubuntu2404@sha256:8fafffd0c67a48117dff09031ed16e79c0a83cc6996472f4b4dcb76343102a66
FROM ${RUNPOD_JOBRUNNER_IMAGE} AS jobrunner

# Official RunPod PyTorch image, linux/amd64 manifest resolved 2026-07-31.
FROM runpod/pytorch@sha256:3e874356857adfa3e8faa3fd913b65bd127f77a0fe2e489513e7775e1c1e16b1

ARG LLAMA_CPP_COMMIT=000547513f1530346ecd163db8b3e13962949961
ARG BASE_GGUF_FIRST_SHARD=base-bf16-00001-of-00000.gguf
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/opt/striatum-qwen35b \
    RUNPOD_JOBRUNNER_RELEASE_PATH=/opt/runpod-jobrunner/release.json \
    STRIATUM_MODEL_DIR=/opt/models/Qwen3.6-35B-A3B-995ad96e \
    STRIATUM_BASE_GGUF=/opt/models/Qwen3.6-35B-A3B-995ad96e/${BASE_GGUF_FIRST_SHARD} \
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
       "import importlib; modules = ('torch', 'transformers', 'peft', 'accelerate', 'datasets', 'safetensors', 'flash_attn', 'fla', 'causal_conv1d', 'bitsandbytes', 'tilelang', 'tvm_ffi', 'liger_kernel.transformers.model.qwen3_5_moe'); [importlib.import_module(module) for module in modules]"

RUN git clone https://github.com/ggml-org/llama.cpp.git /opt/llama.cpp \
    && git -C /opt/llama.cpp checkout "$LLAMA_CPP_COMMIT" \
    && cmake -S /opt/llama.cpp -B /opt/llama.cpp/build \
       -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=90 -DLLAMA_CURL=OFF \
    && cmake --build /opt/llama.cpp/build --config Release -j2 \
       --target llama-cli llama-quantize llama-gguf-split

RUN mkdir -p /opt/models/Qwen3.6-35B-A3B-995ad96e
COPY --from=model-snapshot /LICENSE /README.md /config.json /configuration.json \
    /generation_config.json \
    /preprocessor_config.json /video_preprocessor_config.json \
    /tokenizer.json /tokenizer_config.json /vocab.json /merges.txt \
    /chat_template.jinja /model.safetensors.index.json /snapshot-revision.txt \
    /base-bf16.receipt.json /base-bf16.split-receipt.json \
    /opt/models/Qwen3.6-35B-A3B-995ad96e/
# One shard per OCI layer keeps every registry blob below 4 GB.
COPY --from=model-snapshot /model-00001-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00002-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00003-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00004-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00005-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00006-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00007-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00008-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00009-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00010-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00011-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00012-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00013-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00014-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00015-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00016-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00017-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00018-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00019-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00020-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00021-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00022-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00023-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00024-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00025-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
COPY --from=model-snapshot /model-00026-of-00026.safetensors /opt/models/Qwen3.6-35B-A3B-995ad96e/
# The build helper replaces this marker with one COPY instruction per native
# <=4 GiB GGUF shard. Keeping each instruction separate bounds every OCI blob.
# __BASE_GGUF_SHARD_COPIES__
RUN test "$(cat /opt/models/Qwen3.6-35B-A3B-995ad96e/snapshot-revision.txt)" = \
         "995ad96eacd98c81ed38be0c5b274b04031597b0" \
    && test "$(find /opt/models/Qwen3.6-35B-A3B-995ad96e -maxdepth 1 \
         -type f -name 'model-*.safetensors' | wc -l)" -eq 26 \
    && test -f "$STRIATUM_BASE_GGUF" \
    && test -f /opt/models/Qwen3.6-35B-A3B-995ad96e/base-bf16.receipt.json \
    && test -f /opt/models/Qwen3.6-35B-A3B-995ad96e/base-bf16.split-receipt.json \
    && test "$(sha256sum /opt/models/Qwen3.6-35B-A3B-995ad96e/LICENSE | cut -d' ' -f1)" = \
         "50cbab8a892c5f2993b8c7351a99182507472def3b1374558308605d99b86b32" \
    && test "$(sha256sum /opt/models/Qwen3.6-35B-A3B-995ad96e/README.md | cut -d' ' -f1)" = \
         "c4ddaa065649ff6352648f64747a16eda31726f3e34add94ce04abb461c77b75" \
    && test ! -e /opt/models/Qwen3.6-35B-A3B-995ad96e/base-bf16.gguf

RUN mkdir -p /opt/striatum-qwen35b/jobs/qwen35b_moe /opt/striatum-qwen35b/bin
COPY *.py *.json /opt/striatum-qwen35b/jobs/qwen35b_moe/
COPY bin/ /opt/striatum-qwen35b/bin/
RUN chmod 0555 /opt/striatum-qwen35b/bin/* \
    && rm -rf /tmp/striatum-qwen35b-build

LABEL org.opencontainers.image.title="Striatum Qwen3.6-35B-A3B PEFT runner"

EXPOSE 22 8080
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/runpod-jobrunner/entrypoint"]
