# Qwen3.6-35B-A3B managed tuning job

This directory is the model-specific side of the `runpod-jobrunner` contract.
It does not create or delete workers. The worker image contains these scripts;
the five-file, hash-pinned `sft/` manifest is the only per-run data upload. The
pinned HF snapshot and BF16 GGUF are preloaded once on network volume
`7lno735a6g` and verified again by hash before every paid run.

## Fixed inputs and model

The base is `Qwen/Qwen3.6-35B-A3B` at revision
`995ad96eacd98c81ed38be0c5b274b04031597b0`. `input-manifest.json` permits
exactly these files, totaling 119,218,345 bytes:

- `sft/review.train.jsonl`
- `sft/review.eval.jsonl`
- `sft/implementation-planning.train.jsonl`
- `sft/design-convergence.train.jsonl`
- `sft/proposal-generation.train.jsonl`

`corpus/`, DPO data, repository files, symlinks, extra SFT files, and changed
hashes fail verification. `materialize.py` copies regular files into the
ignored `.generated/` area; it never links the source data into a bundle.

Use `SMOKE-LADDER.md` for the exact Gate 1, Gate 2, Gate 3, and full-run
commands. Full materialization requires the recovered Gate 3 acceptance
receipt, and digest stamping requires the machine-readable receipt from a
pushed image build. A copied digest or model-load-only result cannot admit the
full run.

The committed `job.yaml` is a template and intentionally fails immutable-image
validation until the generated copy receives a real digest. Digest stamping
also recomputes the canonical self-hash; always finish with
`runpod-jobrunner check GENERATED_BUNDLE`. The old
`evidence/bundle-check-2026-07-31.json` receipt is historical 0.1.0 evidence;
its all-`a` digest was a test value, not a published image. It does not prove
the network-volume bundle. Preserve the fresh 0.1.12 check output with this
campaign's recovered controller evidence.

Gate 2 and Gate 3 are separate reservations under the same campaign budget
scope. Each must reach terminal artifact recovery, signed checkpoint
acknowledgement, and provider deletion before the next reservation. Gate 3
issues the image-bound receipt required by full materialization. The full job
starts with runtime and Gate 3 receipt verification before training and full
evaluation. It reserves $45.00; all launches use the
`striatum-qwen35b-hard100-20260801` scope and its $94.00 reservation ceiling.
That ceiling accounts for settled campaign spend and keeps total authorized
exposure below the owner's $100 hard limit. $75 remains a feasibility
reassessment point, not an automatic stop.

```bash
CAMPAIGN_SCOPE=striatum-qwen35b-hard100-20260801
FULL_BUNDLE=jobs/qwen35b_moe/.generated/full-20260801

runpod-jobrunner check "$FULL_BUNDLE"
runpod-jobrunner run "$FULL_BUNDLE" \
  --approve-max-usd 45.00 \
  --budget-scope "$CAMPAIGN_SCOPE" \
  --budget-total-usd 94.00
```

`Dockerfile` copies the remote runner from the already-published
`runpod-jobrunner` image by immutable digest. No private source checkout enters
the Docker context; `Dockerfile.dockerignore` allow-lists only job code and
contracts. The RunPod PyTorch linux/amd64 base is pinned to
`sha256:3e874356857adfa3e8faa3fd913b65bd127f77a0fe2e489513e7775e1c1e16b1`.
The pinned `llama.cpp` build emits CUDA code for SM90 explicitly; it never
infers a GPU architecture from the CPU-only image builder. The image applies
`llama-qwen35-lora-reorder.patch` to the pinned source. Export checks the patch
hash, proves that it is applied, and rejects any other tracked llama.cpp
changes. The export receipt binds both the upstream commit and patch hash.
Build locally or publish with:

```bash
JOBRUNNER_DIGEST=YOUR_64_HEX_JOBRUNNER_IMAGE_DIGEST
BUILD_RECEIPT=/tmp/striatum-qwen35b-image-0.1.21.json
python3 -m jobs.qwen35b_moe.prepare_base_gguf \
  --model-dir /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e \
  --llama-cpp /home/halbritt/git/llama.cpp \
  --output /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e/base-bf16.gguf \
  --receipt /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e/base-bf16.receipt.json
python3 -m jobs.qwen35b_moe.build_image \
  ghcr.io/halbritt/striatum-tuner-qwen35b-moe 0.1.21 \
  --jobrunner-image \
  "ghcr.io/halbritt/runpod-jobrunner-noop@sha256:$JOBRUNNER_DIGEST" \
  --receipt "$BUILD_RECEIPT" --push
```

Omit `--push` to load a local-only image instead.

After a push, use `BUILD_RECEIPT` to stamp the generated bundle. The build
refuses uncommitted Qwen job code, requires the runner image
to use an immutable digest, and verifies that its embedded release version and
commit exactly match `job.yaml`. It has no model build context and contains no
safetensors or GGUF. The 41-entry `network-volume-assets.sha256` contract is
copied into the image. The verify phase uses it to hash the exact 40-file HF
snapshot plus
`/workspace/models/Qwen3.6-35B-A3B-995ad96e/gguf/base-bf16.gguf`, rejects
extras and symlinks, and then repeats the target census. A pushed build emits
BuildKit provenance and an SBOM; neither attestation substitutes for the
immutable image digest used by the job bundle.

## PEFT target authority

PEFT, not LLaMAFactory, owns the adapter. The ordinary rank-32 target set is:

- 150 DeltaNet projections: five in each of 30 layers;
- 40 full-attention projections: four in each of 10 layers;
- 120 shared-expert projections: three in each of 40 layers.

The pinned tensor shapes predict 42,332,160 trainable parameters and
169,328,640 bytes at fp32, below the 50-million and 200-MiB caps. An earlier
reconnaissance estimate of 41,021,440 omitted 1,310,720 parameters. Paid
preflight reads every safetensors header, injects PEFT on a meta model, and
requires PEFT's measured count to equal the shape-derived count.
The local meta-injection receipt is in
`evidence/meta-injection-2026-07-31.json`; it is not an optimizer or export
claim. The independent all-26-shard header census is in
`evidence/snapshot-census-2026-07-31.json`.

The expert-aware alternative adds the two fused routed-expert parameters in
each layer with per-expert rank 1 and alpha 2. It predicts 100,003,840 total
trainables and 400,015,360 fp32 bytes, below the 110-million and 450-MiB caps.
Naive routed-expert rank 32 would add about 1.85 billion parameters and is
rejected. PEFT's parameter wrapper forbids LoRA dropout, so this combined
candidate uses zero dropout for both its ordinary and routed targets. Try
linear-only first; fund expert-aware only if linear-only fails.

## Readiness and paid preflight

Prepare the complete exact snapshot and GGUF locally, then preload them on the
network volume through RunPod's S3-compatible endpoint:

```bash
python3 -m jobs.qwen35b_moe.prepare_model_snapshot \
  --destination /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e

STRIATUM_SNAPSHOT=/home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e
RUNPOD_VOLUME_ID=7lno735a6g
RUNPOD_S3_ENDPOINT=https://s3api-us-nc-1.runpod.io
AWS_PROFILE=runpod aws s3 cp "$STRIATUM_SNAPSHOT/" \
  "s3://$RUNPOD_VOLUME_ID/models/Qwen3.6-35B-A3B-995ad96e/" \
  --recursive --exclude '*.gguf' --exclude '*receipt.json' \
  --exclude '.cache/*' --exclude '.gitattributes' \
  --region US-NC-1 --endpoint-url "$RUNPOD_S3_ENDPOINT"
AWS_PROFILE=runpod aws s3 cp "$STRIATUM_SNAPSHOT/base-bf16.gguf" \
  "s3://$RUNPOD_VOLUME_ID/models/Qwen3.6-35B-A3B-995ad96e/gguf/base-bf16.gguf" \
  --region US-NC-1 --endpoint-url "$RUNPOD_S3_ENDPOINT"
```

The profile supplies the S3 credentials; do not put them in the repository or
the command line. The endpoint and region must match the volume's data center.
Before launch, list the prefix and require exactly 41 objects totaling
142,993,858,696 bytes. Multipart S3 ETags are not SHA-256 proofs, so the paid
worker still hashes every asset before any training phase.

The volume layout is
`/workspace/models/Qwen3.6-35B-A3B-995ad96e/{40 HF files,gguf/base-bf16.gguf}`.
The preflight verifies all inputs, the complete asset hash manifest, and the
target census, injects PEFT on meta, and requires the exact BF16 parity GGUF.
The live training
load then proves that all 310 ordinary LoRA targets are 4-bit, freezes the base,
keeps the exact 80 fused expert parameters in BF16, casts the other eligible
half-precision parameters to FP32, and records the dtype, CUDA-memory, and live
FP32 adapter censuses. Terminal packaging revalidates these receipts. It trains
one optimizer step on the largest effective token sequence found by tokenizing
all 1,268
authorized training records, hashes checkpoint 1, reloads it
first through the same 4-bit NF4 eval-only adapter path used by checkpoint
evaluation, then through a separate BF16 Hugging Face process for deterministic
`llama.cpp` parity. Both reloads use the longest tokenized record among all 98
authorized held-out records. Their distinct load-mode attestations, token-length
censuses, and exact selections are required by preflight packaging; BF16-only
evidence cannot close the gate. The BF16 reference is then converted with
pinned `llama.cpp`, loaded as GGUF base plus adapter, and required to match
exact text:

```bash
python3 -m jobs.qwen35b_moe.preflight --strategy linear-only --run-smoke
```

Under `runpod-jobrunner`, the scripts derive the uploaded input root from
`RUNPOD_JOBRUNNER_INPUT_ROOT`, treat shared hash-pinned assets under
`/workspace/models` as read-only, and write checkpoints, evaluations, and
terminal artifacts
under `/workspace/runpod-jobrunner/runs/<run-id>`. This keeps retries and the
standalone preflight isolated on the persistent volume. Explicit `STRIATUM_*`
variables override these paths for a local smoke.

Each paid-preflight child writes combined standard output and error to
`diagnostics/preflight/*.log` under that run root. These diagnostic logs remain
on the network volume even when a failed Pod is deleted, so they can be read
through the volume's S3-compatible API. The training process verifies the
Liger fused-loss binding in Transformers' train-begin callback: Transformers
has applied its instance patch at that point, but no training forward has run.
The Liger configuration keeps fused linear cross-entropy enabled but sets
`swiglu` to false. Liger 0.8.1's fused MoE Triton kernel requires matching
activation and expert-weight dtypes, while this QLoRA base intentionally has
FP32 activations and frozen BF16 expert weights. Transformers 5.6.2's native
grouped-matrix path explicitly casts the activation to the expert-weight dtype
and restores the output dtype. The paid preflight remains the acceptance gate
for its memory use and throughput.

The standalone bundle exposes the one-step manifest at
`artifacts/preflight/one-step/checkpoint-*/checkpoint-complete.json` and waits
at most 120 seconds for the controller's signed incremental-mirror
acknowledgement. Its enabled phase timeouts total 1,845 seconds. The controller
starts its clock before the thin runtime image pull. The 2,700-second bound
leaves 855 seconds beyond the 1,845 seconds of enabled phase timeouts for
image pull, startup, input upload, recovery, and deletion. At the $4.50/hour
admission ceiling, 2,700 seconds
costs $3.375 and fits the $3.50 retry cap.

The verify phase fails unless `libggml-cuda.so` resolves `libcuda.so.1` to a
non-stub runtime driver and the pinned `llama-cli --list-devices` reports one
H200 with at least 140,000 MiB. It records the accepted binding in
`artifacts/runtime/cuda-runtime.json`. It also records the volume hash/census
gate in `artifacts/runtime/volume-assets.json`; terminal packaging requires the
runtime evidence.

Do not start a full run if this exceeds 2,700 billable seconds or needs an
interactive patch. Do not retry it automatically. Direct export is not
considered compatible until this command produces `one-step-export.json`. In
particular, PEFT
`target_parameters` export for the expert-aware adapter remains unproven until
its own smoke passes.

## Training, evaluation, and acceptance

The paid train phase runs four distinct training processes: five measured steps,
resume to checkpoint 25, resume to the exact first-epoch boundary at checkpoint
159, and resume to 318. Checkpoint 25 must first strictly pass its deterministic
16-example mini-evaluation. Checkpoint 159 must then strictly pass a separate-
process evaluation of all 98 authorized held-out examples before the
second-epoch projection is accepted or training may continue. The epoch boundary
is derived as `ceil(1268 / (1 * 8)) = 159` optimizer steps and is also declared
in `training-config.json` so configuration drift fails closed. The orchestrator
reads cost, elapsed, and train-phase timeout authority from the runner's
`run-request/1`, records conservative projections before each continuation, and
stops if either cap or any available 35B gate fails. Training uses cutoff 40,960,
gradient accumulation 8, two epochs (318 expected steps), Liger's fused linear
cross-entropy, and checkpoint interval 25. The
current invocation is authoritative after every staged resume: the trainer
reapplies its requested checkpoint interval and recomputes the optimizer-group
learning rates from the extended scheduler horizon before the first resumed
update. This prevents restored state from silently retaining an earlier save
cadence or the zero terminal rate of an exhausted shorter schedule. The
fused loss is required: materializing `sequence x 248,320` logits exceeded the
H100 memory budget in the retained 27B run. Every training process verifies
that the pinned Qwen MoE fused forward is actually bound and records that real
training calls returned loss without materialized logits. Training does no
inline evaluation.

The tokenizer contract explicitly requests a plain token-ID list from pinned
Transformers; a structured `BatchEncoding` is rejected. Every training process
recomputes and validates the committed full, prompt, and assistant length
censuses for all 1,268 records before the first forward. At the 40,960-token
cutoff, 108 records are truncated and 59 assistant segments themselves exceed
the cutoff. These retain the full prompt and the assistant prefix that fits.
Four records have prompts that reach the cutoff; for only those records,
training keeps the prompt tail plus the complete 536--685-token assistant
answer. Thus all 1,268 records contribute supervised assistant tokens, but the
contract does not claim that every token of every overlength record is trained.
Chunking those records would change the 1,268-example, 159-step epoch contract
and is outside this run.

Every save gets a hash-complete `checkpoint-complete.json` and then blocks for
at most 900 seconds while the lifecycle controller mirrors and verifies the
checkpoint. The worker accepts only a controller Ed25519 acknowledgement bound
to this run, bundle, immutable image, manifest, exact file count and bytes,
public key, and `runpod-jobrunner-incremental-mirror` namespace. The per-run
private key remains on the controller. Resume refuses a checkpoint whose exact
inventory, hashes, trainer global step, or signed mirror acknowledgement does
not match. After Transformers restores the checkpoint state, the trainer
reapplies and records the current invocation's checkpoint interval; a timing
checkpoint therefore cannot silently impose its shorter save cadence on later
stages. The standalone preflight uses the same signed acknowledgement
contract against its one-step checkpoint path, with the shorter timeout stated
above.
The checkpoint-25 mini-evaluation uses 16 dispatch IDs committed in
`training-config.json`; they are re-derived as the lowest SHA-256 dispatch-ID
hashes from the exact held-out file, and the selection evidence is embedded in
its summary and train-phase receipt. The exact checkpoints at 159 and 318 are
forced in addition to the interval-25 saves. Final full evaluation and export
remain separate runner phases after training completes. Packaging revalidates
the terminal protocols, exact step and gate evidence, checkpoint hashes, and
the actual adapter GGUF hash; placeholder JSON receipts cannot close a run. The
export receipt also binds the normalized PEFT source path plus the exact size and
SHA-256 of `adapter_config.json` and `adapter_model.safetensors`. Packaging
revalidates the pinned base model and revision, LoRA target semantics, and the
safetensors header and byte ranges before it accepts that binding.

Evaluation is a separate model process. It runs the 98-example held-out split,
then a deterministic export parity sample with at most 2,048 generated tokens.
That sample must produce valid JSON and a legal verdict before export. Exact
text parity then requires llama.cpp to reproduce the Hugging Face output. The
remote job can score JSON validity, legal verdicts, exact verdicts, and side
match. It cannot score fate:
the fate map lives in `corpus/analysis.json`, which is deliberately not
uploaded. After recovery, complete that private gate locally:

```bash
python3 -m jobs.qwen35b_moe.score_fate \
  --results RECOVERED/eval/full/results.jsonl \
  --analysis corpus/analysis.json \
  --eval-source sft/review.eval.jsonl \
  --output RECOVERED/eval/full/fate-gate.json
```

If training and the full evaluation pass but parity or export fails, do not
repeat training. The `recover-export` profile validates every staged source
checkpoint, the training receipt, the full evaluation results and summary, the
final adapter, and the source runtime receipts before it loads the model. It
copies checkpoint 318 and the final adapter into a new run, repeats one BF16
inference, exports the adapter, and publishes a selective artifact manifest:

```bash
SOURCE_RUN_ID=run-REPLACE_ME
RECOVERY=jobs/qwen35b_moe/.generated/recover-export-$(date -u +%Y%m%dT%H%M%SZ)
python3 -m jobs.qwen35b_moe.materialize \
  --source-repo "$PWD" --destination "$RECOVERY" \
  --profile recover-export --recovery-source-run-id "$SOURCE_RUN_ID"
python3 -m jobs.qwen35b_moe.update_image_digest "$RECOVERY" "$BUILD_RECEIPT"
/home/halbritt/git/runpod-jobrunner/.venv/bin/runpod-jobrunner check "$RECOVERY"
/home/halbritt/git/runpod-jobrunner/.venv/bin/runpod-jobrunner run "$RECOVERY" \
  --approve-max-usd 12.00 \
  --budget-scope striatum-qwen35b-hard100-20260801 \
  --budget-total-usd 94.00
```

The recovery job has no enabled train or full-evaluation phase. Its 9,000-second
wall-clock limit and $12 cap include source validation, one adapter-backed BF16
inference, GGUF conversion, exact Hugging Face/llama.cpp parity, artifact
recovery, and pod deletion.

The local scorer requires the exact hash-pinned 98-example evaluation source
and the pinned private analysis file. It hashes the same bytes that it parses,
then binds the results, analysis, evaluation source, and dispatch-ID set into
its receipt. The number of fate-scored rows is the number of legal verdicts
produced by the candidate. It must be at least 86, which strictly beats the
historical 85-of-98 legal-verdict baseline. A structurally valid model result
that misses either gate still produces a durable rejection receipt.

Lifecycle success therefore means only that artifacts were produced,
verified, recovered, and the worker was closed. Model acceptance also requires
all four metrics to strictly beat the recorded 35B baseline. The baseline was
served from a third-party GGUF whose source bits were not pinned to this
official Hugging Face snapshot, so the behavior comparison is useful but is not
an exact same-base ablation.
