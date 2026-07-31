# Qwen3.6-35B-A3B managed tuning job

This directory is the model-specific side of the `runpod-jobrunner` contract.
It does not create or delete workers. The worker image contains these scripts;
the only runtime data upload is the five-file, hash-pinned `sft/` manifest.

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

```bash
python3 -m jobs.qwen35b_moe.materialize \
  --source-repo "$PWD" \
  --destination jobs/qwen35b_moe/.generated/linear \
  --profile full
python3 -m jobs.qwen35b_moe.materialize \
  --source-repo "$PWD" \
  --destination jobs/qwen35b_moe/.generated/preflight \
  --profile preflight-only
python3 -m jobs.qwen35b_moe.update_image_digest \
  jobs/qwen35b_moe/.generated/linear sha256:<64-hex-image-digest>
```

The committed `job.yaml` is a template and intentionally fails immutable-image
validation until the generated copy receives a real digest. Digest stamping
also recomputes the canonical self-hash; always finish with
`runpod-jobrunner check GENERATED_BUNDLE`. The schema/input check receipt is in
`evidence/bundle-check-2026-07-31.json`; its all-`a` digest was a test value,
not a published image.

The two generated bundles are separate reservations: the preflight-only bundle
enables verify, paid preflight, and preflight packaging under 600 seconds and
$2.00; the full bundle reserves $47.00 and owns training plus full evaluation.
With the controller's $0.50 no-op reservation, the aggregate maximum is
$49.50. A failed or over-time preflight is a stop condition for launching the
full bundle.

`Dockerfile` copies the remote runner from the already-published
`runpod-jobrunner` image by immutable digest. No private source checkout enters
the Docker context; `Dockerfile.dockerignore` allow-lists only job code and
contracts. The RunPod PyTorch linux/amd64 base is pinned to
`sha256:3e874356857adfa3e8faa3fd913b65bd127f77a0fe2e489513e7775e1c1e16b1`.
Build locally or publish with:

```bash
python3 -m jobs.qwen35b_moe.prepare_base_gguf \
  --model-dir /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e \
  --llama-cpp /home/halbritt/git/llama.cpp \
  --output /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e/base-bf16.gguf \
  --receipt /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e/base-bf16.receipt.json
python3 -m jobs.qwen35b_moe.prepare_image_gguf \
  --model-dir /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e \
  --llama-cpp /home/halbritt/git/llama.cpp
python3 -m jobs.qwen35b_moe.build_image \
  ghcr.io/halbritt/striatum-tuner-qwen35b-moe 0.1.0 \
  --jobrunner-image ghcr.io/halbritt/runpod-jobrunner-noop@sha256:<digest> \
  --model-snapshot /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e [--push]
```

After a push, use the printed `immutable_image` digest to stamp the generated
bundle. The build refuses uncommitted Qwen job code and requires the baked
runner image to use an immutable digest. It also refuses the model context
unless the full target census passes, the revision receipt matches, all 26
indexed shards exist, and no `sft` or `corpus` path is present. The snapshot is
baked at `/opt/models/Qwen3.6-35B-A3B-995ad96e`. The exact BF16 GGUF is
validated against its revision/llama.cpp/hash receipt, then baked as 19 native
GGUF shards with one shard per OCI layer; the unsplit 71 GB source does not
enter the image. Runtime SFT data remains a separate five-file upload.

The public worker image also carries the exact upstream Apache-2.0 `LICENSE`
and model card from the pinned model revision. Their SHA-256 hashes are checked
before the build context is accepted and recorded in the image-build receipt.
A pushed build emits BuildKit provenance and an SBOM; neither attestation is a
substitute for the immutable image digest used by the job bundle.

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

There is no transferable encrypted pre-stage between a cheap RunPod worker and
the H100 worker. Prepare the complete exact snapshot locally, then require it
as the model-bearing image context described above:

```bash
python3 -m jobs.qwen35b_moe.prepare_model_snapshot \
  --destination /home/halbritt/models/hf/Qwen3.6-35B-A3B-995ad96e
```

The preflight verifies all inputs, performs the target census, injects PEFT on
meta, requires the baked and receipted BF16 parity GGUF, trains one optimizer
step on the largest effective token sequence found by tokenizing all 1,268
authorized training records, hashes checkpoint 1, reloads it
against the bf16 Hugging Face base in a separate evaluation process using the
deterministically longest tokenized record among all 98 authorized held-out
records, converts the adapter with pinned `llama.cpp`, loads GGUF base plus
adapter, and requires deterministic text parity. Both token-length censuses and
exact selections are included in the preflight receipt:

```bash
python3 -m jobs.qwen35b_moe.preflight --strategy linear-only --run-smoke
```

Under `runpod-jobrunner`, the scripts derive the uploaded input root from
`RUNPOD_JOBRUNNER_INPUT_ROOT`, read the baked snapshot under `/opt/models`, and
write the terminal artifact manifest at the dedicated encrypted mount root,
matching the v1 controller's mount-relative recovery contract. Explicit
`STRIATUM_*` variables override these paths for a local smoke.

Do not start a full run if this exceeds ten billable minutes or needs an
interactive patch. Direct export is not considered compatible until this
command produces `one-step-export.json`. In particular, PEFT
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
fused loss is required: materializing `sequence x 248,320` logits exceeded the
H100 memory budget in the retained 27B run. Every training process verifies
that the pinned Qwen MoE fused forward is actually bound and records that real
training calls returned loss without materialized logits. Training does no
inline evaluation.
Every save gets a hash-complete `checkpoint-complete.json` and then blocks for
at most 900 seconds while the lifecycle controller mirrors and verifies the
checkpoint. The worker accepts only a controller Ed25519 acknowledgement bound
to this run, bundle, immutable image, manifest, exact file count and bytes,
public key, and `runpod-jobrunner-incremental-mirror` namespace. The per-run
private key remains on the controller. Resume refuses a checkpoint whose exact
inventory, hashes, trainer global step, or signed mirror acknowledgement does
not match. Preflight-only materializations omit this contract because they do
not expose the long-running training phase.
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
then a deterministic export parity sample. The remote job can score JSON
validity, legal verdicts, exact verdicts, and side match. It cannot score fate:
the fate map lives in `corpus/analysis.json`, which is deliberately not
uploaded. After recovery, complete that private gate locally:

```bash
python3 -m jobs.qwen35b_moe.score_fate \
  --results RECOVERED/eval/full/results.jsonl \
  --analysis corpus/analysis.json \
  --output RECOVERED/eval/full/fate-gate.json
```

Lifecycle success therefore means only that artifacts were produced,
verified, recovered, and the worker was closed. Model acceptance also requires
all four metrics to strictly beat the recorded 35B baseline. The baseline was
served from a third-party GGUF whose source bits were not pinned to this
official Hugging Face snapshot, so the behavior comparison is useful but is not
an exact same-base ablation.
