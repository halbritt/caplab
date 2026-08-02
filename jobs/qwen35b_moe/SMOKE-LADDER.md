# Qwen training smoke-test ladder

All three gates use `jobs.qwen35b_moe.preflight`, `train`, the shared
multimodal processor/collator, PEFT injection, checkpoint code, and adapter
inference. There is no second trainer. Production defaults remain in
`training-config.json`; smoke differences are explicit profiles under `smoke/`.

The deterministic smoke dataset contains four representative SFT records and
one embedded 64 by 64 PNG. Its only file is 2,234 bytes with SHA-256
`7dcd0e657ce7ac2175c67777f40acc5496e4f29685a069fc017fb98d08740a2b`.
No production corpus or external upload is used by a smoke gate.

## Cheap preflight

This checks configuration, pinned dependencies, paths, snapshot revision,
processor compatibility, dataset and image readability, chat templating,
tokenization, assistant masking, and exact LoRA target/count agreement without
loading model weights:

```bash
SMOKE_PY=/home/halbritt/.local/share/striatum-tuner/qwen-smoke-venv/bin/python
SMOKE_MODEL=/home/halbritt/models/hf/Qwen3.5-0.8B-2fc06364

"$SMOKE_PY" -m jobs.qwen35b_moe.preflight \
  --config jobs/qwen35b_moe/smoke/training-config.json \
  --model-dir "$SMOKE_MODEL" \
  --input-dir jobs/qwen35b_moe/smoke/inputs \
  --output /tmp/qwen-smoke-check \
  --check-only
```

This preflight cannot detect CUDA kernel compilation, weight-loading memory,
runtime gradients, optimizer behavior, or checkpoint load/save defects.

## Gate 1: proximal RTX 3090

The local gate uses Qwen3.5-0.8B, NF4 QLoRA, BF16 compute, SDPA, four records,
512-token cutoff, one example per batch, and four optimizer steps. It saves at
step 2, resumes to step 4, then loads the final adapter for one multimodal
inference. External reporting and uploads are disabled.

The GPU-fleet lease is the execution authority. If standing inference services
occupy VRAM, drain them before the lease and restore them with shell traps:

```bash
SMOKE_PY=/home/halbritt/.local/share/striatum-tuner/qwen-smoke-venv/bin/python
SMOKE_MODEL=/home/halbritt/models/hf/Qwen3.5-0.8B-2fc06364
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT=/home/halbritt/.local/state/striatum-tuner/gate1-$STAMP

sudo systemctl stop whisper-stt.service
trap 'sudo systemctl start whisper-stt.service' EXIT
/home/halbritt/git/gpu-fleet/bin/gpu-fleet-run \
  --model qwen3.6-35b-a3b \
  --job striatum-qwen35-smoke \
  --timeout 2400 -- bash -lc '
    trap "sudo systemctl start llama-27b.service" EXIT
    sudo systemctl stop llama-27b.service
    "$1" -m jobs.qwen35b_moe.preflight \
      --config jobs/qwen35b_moe/smoke/training-config.json \
      --model-dir "$2" \
      --input-dir jobs/qwen35b_moe/smoke/inputs \
      --output "$3" --run-smoke --seed 42
  ' _ "$SMOKE_PY" "$SMOKE_MODEL" "$OUT"
```

Gate 1 detects shared Python-path, preprocessing, masking, LoRA, forward,
backward, optimizer, checkpoint/resume, and inference defects. It cannot detect
SM90-only kernels, FlashAttention, FlashQLA, H200 BF16 behavior, RunPod mounts,
the production image, or MoE expert/router behavior.

## Build the exact H200 image

The image pins the production stack and validates its install contract. Its
runtime preflight separately forces the public FLA dispatcher through
FlashQLA on the Qwen3.6 tensor shape and requires finite forward values and
finite nonzero gradients before loading any model weights.

```bash
JOBRUNNER_IMAGE=ghcr.io/halbritt/runpod-jobrunner-noop@sha256:304a555bc6ddbc269806c3440a7eb221b4a830169fa4e1ecf4b742551d45bb73
BUILD_RECEIPT=/tmp/striatum-qwen35b-image-0.1.13.json
python3 -m jobs.qwen35b_moe.build_image \
  ghcr.io/halbritt/striatum-tuner-qwen35b-moe 0.1.13 \
  --jobrunner-image "$JOBRUNNER_IMAGE" \
  --receipt "$BUILD_RECEIPT" --push
```

The build receipt is the admission input below. A naked digest is deliberately
insufficient: stamping verifies the pushed image, source commit, exact embedded
runner release, and immutable digest. Both paid gates use the same image, H200
requirement, network volume, runner version, mount, cache, and dependency stack.
FP8 is not enabled.

## Gate 2: dense model on H200

The immutable Qwen3.5 snapshot is cached once at
`/workspace/models/Qwen3.5-0.8B-2fc06364` on retained volume `7lno735a6g`.

```bash
GATE2=jobs/qwen35b_moe/.generated/hopper-dense-smoke-20260801
python3 -m jobs.qwen35b_moe.materialize \
  --source-repo "$PWD" --destination "$GATE2" \
  --profile hopper-dense-smoke
python3 -m jobs.qwen35b_moe.update_image_digest "$GATE2" "$BUILD_RECEIPT"
/home/halbritt/git/runpod-jobrunner/.venv/bin/runpod-jobrunner check "$GATE2"
/home/halbritt/git/runpod-jobrunner/.venv/bin/runpod-jobrunner run "$GATE2" \
  --approve-max-usd 3.50 \
  --budget-scope striatum-qwen35b-hard100-20260801 \
  --budget-total-usd 94.00
```

Gate 2 adds validation of the production container, CUDA/Hopper/SM90,
FlashQLA dispatch and compilation, BF16 gradients, launcher, persistent mount,
cache path, checkpoint mirroring/acknowledgement, artifact recovery, and pod
deletion. It does not validate the 35B MoE graph, expert dispatch within the
model, its adapter target census, or its memory use.

## Gate 3: real 35B MoE on H200

```bash
GATE3=jobs/qwen35b_moe/.generated/hopper-moe-smoke-20260801
python3 -m jobs.qwen35b_moe.materialize \
  --source-repo "$PWD" --destination "$GATE3" \
  --profile hopper-moe-smoke
python3 -m jobs.qwen35b_moe.update_image_digest "$GATE3" "$BUILD_RECEIPT"
/home/halbritt/git/runpod-jobrunner/.venv/bin/runpod-jobrunner check "$GATE3"
/home/halbritt/git/runpod-jobrunner/.venv/bin/runpod-jobrunner run "$GATE3" \
  --approve-max-usd 5.00 \
  --budget-scope striatum-qwen35b-hard100-20260801 \
  --budget-total-usd 94.00
```

Gate 3 adds the real MoE configuration, exact 310-module LoRA census, router and
expert graph, expert-dispatch kernels, 42,332,160 trainable-parameter invariant,
gradient flow, memory use, checkpoint compatibility, resume, and real-model
adapter inference. Its four short steps cannot establish convergence, final
quality, long-context memory, full evaluation correctness, or 318-step runtime.

After verified recovery and closeout, bind the terminal evidence to the exact
image. Substitute the run ID printed by the controller:

```bash
GATE3_RUN_ID=run-REPLACE_ME
GATE3_RUN_ROOT="$HOME/.local/state/runpod-jobrunner/runs/$GATE3_RUN_ID"
GATE3_ACCEPTANCE=/tmp/qwen35b-gate3-acceptance.json
python3 -m jobs.qwen35b_moe.gate_acceptance \
  --run-root "$GATE3_RUN_ROOT" \
  --build-receipt "$BUILD_RECEIPT" \
  --run-id "$GATE3_RUN_ID" \
  --output "$GATE3_ACCEPTANCE"
```

The full bundle cannot be materialized without this receipt and cannot be
stamped with a different worker image:

```bash
FULL=jobs/qwen35b_moe/.generated/full-20260801
python3 -m jobs.qwen35b_moe.materialize \
  --source-repo "$PWD" --destination "$FULL" --profile full \
  --gate3-acceptance "$GATE3_ACCEPTANCE"
python3 -m jobs.qwen35b_moe.update_image_digest "$FULL" "$BUILD_RECEIPT"
/home/halbritt/git/runpod-jobrunner/.venv/bin/runpod-jobrunner check "$FULL"
```

Only after all three gates pass may the existing full bundle be launched. A
failed gate is closed and recovered before another paid reservation. The full
campaign remains subject to the `$100` hard cap and retains network volume
`7lno735a6g` after all compute is deleted.
