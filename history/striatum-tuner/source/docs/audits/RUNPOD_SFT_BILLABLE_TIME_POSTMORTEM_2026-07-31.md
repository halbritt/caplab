# RunPod SFT billable-time postmortem

Date: 2026-07-31  
Incident window: 2026-07-30 18:14:50 UTC to 2026-07-31 05:57:26 UTC  
Pod: `akbiwknw27725g`, Secure Cloud H100 80GB, encrypted 150GB volume  
Status: run complete; pod deleted; corrective actions proposed but not implemented

## Executive conclusion

The pod was billed for 11h42m36s and settled at `$35.3405`. The successful
training phase took 5h34m01s and cost about `$16.80` at the observed
`$3.018/hour` total rate. Only 47.5% of the pod lifetime was spent in the
training phase that produced the retained adapter.

The largest losses were not data transfer or slow H100 training:

- The ready pod sat idle for 2h17m32s because launch authority was interpreted
  as ending at the training-start boundary. Estimated cost: `$6.92`.
- A healthy 100-step training attempt was lost after two hours because inline
  evaluation ran before the scheduled checkpoint and allocated full vocabulary
  logits. Estimated cost: `$6.05`.
- The exact runtime was discovered and repaired on the rented H100 through
  seven failed launches. Estimated cost from first launch to the stable Liger
  launch: `$2.20`.
- Provisioning, post-training evaluation recovery, retrieval, and teardown used
  another 52 minutes. Much of that work can move before pod creation or into a
  tested image.

With the same model, data, hyperparameters, and measured training throughput,
the next run should target launch-to-deletion in at most six hours, or about
`$18.11` at the same rate. The measured training phase alone is a `$16.80`
floor. Getting materially below that floor requires a measured throughput
improvement or less training work; it cannot be achieved by better
orchestration alone.

The control-plane decision is:

> Keep the reasoning agent on Proximal. Run a deterministic controller beside
> the training process on the pod. Arm a local, non-LLM watchdog before pod
> creation to stop failed runs and delete completed runs. Do not put the full
> agent or its credentials on the rented pod.

Moving the same agent process from Proximal to the pod would remove some SSH
latency, but would not reduce model-context replay or reasoning tokens. It would
also place agent credentials on an ephemeral machine and tie the controller's
life to the resource it must terminate.

## Outcome and preserved artifacts

The completed run produced:

- 318 optimizer steps over two epochs in 20,040.5629 seconds;
- training loss `1.1415964372502934`;
- loss-only evaluation over 98 held-out review examples in 204.2102 seconds;
- evaluation loss `1.4827604293823242`;
- a 933,974,032-byte adapter with SHA-256
  `9b467d625f8583e5cbf0a678f4268857af1f02397dac154b2766d7ac55b706bd`;
- a complete terminal checkpoint with optimizer and scheduler state.

The adapter, terminal checkpoint, evaluation results, retained configs, logs,
and source patches were copied to
[`out/review-sft-r1`](../../out/review-sft-r1/) and matched the pod by
SHA-256 before deletion. Only `sft/` was uploaded. `corpus/` remained absent
from the pod.

RunPod returned HTTP 204 for deletion, the subsequent pod lookup returned 404,
and `currentSpendPerHr` became zero.

## Cost accounting

The settled billing API total was:

| Charge | Amount |
|---|---:|
| GPU | `$35.0129` |
| storage | `$0.3275` |
| total | `$35.3405` |

The following attribution uses the observed `$3.018/hour` combined run rate.
It differs from the settled total by less than one tenth of a cent because the
displayed rate was rounded.

| Segment | Duration | Estimated cost | Classification |
|---|---:|---:|---|
| Pod creation through environment ready | 33m13s | `$1.67` | setup, largely movable off H100 |
| Ready but idle | 2h17m32s | `$6.92` | avoidable |
| Compatibility recovery, launches 1–7 | 43m39s | `$2.20` | avoidable next time |
| Attempt 8, lost before checkpoint | 2h00m13s | `$6.05` | avoidable |
| Eval recovery and discarded six-step attempt 9 | 15m08s | `$0.76` | avoidable next time |
| Successful training | 5h34m06s | `$16.80` | required at current throughput |
| Evaluation, retrieval, verification, teardown | 18m47s | `$0.94` | partly required, reducible |

This table does not label every non-training minute as waste. Hardware
verification, one worst-case smoke step, final evaluation, artifact hashing,
and deletion are necessary controls. The avoidable error was performing
environment discovery, open-ended diagnosis, authority resolution, and
unrepresentative smoke tests while the H100 meter was running.

## Timeline

| UTC | Event |
|---|---|
| 2026-07-30 18:14:50 | Encrypted H100 pod created. |
| 18:48:03 | Provisioning and real NF4/FA2 kernel checks completed. |
| 18:49:47 | Agent reported readiness and stopped at a self-imposed training-start boundary. |
| 21:03:21 | User requested status; pod was idle and billing. |
| 21:05:35 | First SFT process launched. |
| 21:15–21:47 | Missing and incompatible runtime components surfaced one at a time. No optimizer step survived. |
| 21:49:13 | Attempt 8 began with Liger fused training loss. |
| 23:49:26 | Step 100 completed; inline evaluation OOMed before checkpoint save. All optimizer progress was lost. |
| 23:57:22 | Attempt 9 began with patched loss-only evaluation behavior. |
| 2026-07-31 00:03:58 | Attempt 9 was stopped at step 6 to remove inline evaluation and shorten the recovery interval. |
| 00:04:34 | Hardened run began with `save_steps: 25` and `eval_strategy: "no"`. |
| 00:30:28 | Checkpoint 25 saved; rclone copy later verified all 12 hashes. |
| 01:49:06 | Checkpoint 100 saved before any evaluation, clearing the prior failure boundary. |
| 02:15:48 | Checkpoint 125 saved. The automatic off-pod mirror later stopped after a transient SSH banner timeout. |
| 05:38:39 | Training completed and final checkpoint was saved. |
| 05:40:42 | First eval-only launch omitted Liger because LLaMA Factory disabled it for non-trainable models; full logits OOMed. Training artifacts were unaffected. |
| 05:45:50 | Patched eval-only launch explicitly applied Liger. |
| 05:49:14 | All 98 evaluation examples completed. |
| 05:51:31 | The mirror failure and earlier inaccurate checkpoint status reports were corrected. |
| 05:57:26 | Local/remote hashes matched and the pod was deleted. |
| 05:57:34 | Pod lookup returned 404. |

## Failure sequence

The runtime was assembled on the paid pod. Each repair exposed the next
incompatibility:

1. The base image had Torch 2.9.1 but lacked
   `flash-linear-attention`, which Qwen3.6's packed-sequence path required.
2. LLaMA Factory rejected Torch 2.9.1 because of its Qwen3.6 Conv3D path. The
   stack was downgraded to Torch 2.8.0/CUDA 12.8 and FlashAttention was rebuilt.
3. Transformers 5.6.0 dereferenced an absent `s_aux` tensor in its external
   FlashAttention integration. A one-line upstream guard was backported.
4. FLA's Triton Hopper backward path refused execution because of a known
   correctness guard. TileLang 0.1.8 and `apache-tvm-ffi` 0.1.13 were installed.
5. Allocator fragmentation and first-use autotuning produced distinct OOMs.
6. The full `sequence × 248k vocabulary` logits tensor was a real memory limit,
   not allocator fragmentation. Liger 0.8.1 fused linear cross-entropy removed
   that materialization.
7. Liger's training forward worked, but its default eval forward still emitted
   logits. Step-100 evaluation therefore OOMed.
8. LLaMA Factory's eval-only model loader disabled Liger when
   `is_trainable` was false. The first post-training eval repeated the full
   logits OOM until that gate was patched.

The exact live patches are retained under
[`out/review-sft-r1/run-metadata/patches`](../../out/review-sft-r1/run-metadata/patches/).
They are evidence, not a satisfactory installation process.

The final working runtime was:

| Component | Pinned value |
|---|---|
| base image | `runpod/pytorch:1.0.3-cu1281-torch291-ubuntu2404` |
| model | `Qwen/Qwen3.6-27B` revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` |
| LLaMA Factory | v0.9.5, commit `7af909522a951e3ad9f022ea6f88b6755257eaa5` |
| Torch | `2.8.0+cu128` |
| Transformers | `5.6.0`, with the retained `s_aux` guard |
| FlashAttention | `2.8.3.post1`, built for Hopper |
| Flash Linear Attention | `0.5.0` |
| TileLang | `0.1.8` |
| apache-tvm-ffi | `0.1.13` |
| Liger Kernel | `0.8.1`, with retained eval fused-loss changes |

## Root causes

### 1. Billing had no single lifecycle owner

The pod was created under explicit authority, but the agent treated training
start as a new boundary. That interpretation was inconsistent with the purpose
of the approved resource and left the pod idle for more than two hours.

The lifecycle invariant should have been:

> Once billing starts, the pod is provisioning, validating, training,
> evaluating, transferring artifacts, or stopped. "Ready and awaiting
> authority" is not an allowed paid state unless the user explicitly requested
> it.

The same owner must control creation, start, failure stop, success deletion,
and verification that spend returned to zero.

### 2. The paid pod was the integration environment

Individual preflight checks passed, but the exact end-to-end path had never
executed:

- exact model revision;
- exact QLoRA adapter shape;
- longest authorized training record;
- one complete forward, backward, optimizer step, and checkpoint;
- eval-only adapter load;
- longest held-out evaluation record;
- fused loss with no logits materialization.

Import checks and small kernel tests could not establish that path. The first
real batch became dependency integration testing on a `$3.018/hour` machine.

### 3. Evaluation and checkpointing shared a failure boundary

The original config used:

```yaml
save_steps: 100
eval_strategy: steps
eval_steps: 100
```

At step 100, the Trainer evaluated before saving. A failure in evaluation
therefore destroyed two hours of otherwise healthy optimizer progress. The
successful config removed inline evaluation and saved every 25 steps:

```yaml
save_steps: 25
save_total_limit: 3
prediction_loss_only: true
eval_strategy: "no"
```

Hugging Face documents `eval_strategy`, `save_strategy`, and `save_steps` as
independent Trainer controls. Checkpoint resume is specifically the recovery
mechanism for interrupted training. See the
[Trainer documentation](https://huggingface.co/docs/transformers/main_classes/trainer).

### 4. Smoke tests did not exercise the maximum-risk population

The eval smoke used one example and passed. The full eval still failed because
the eval-only loader took a different Liger path. A smoke test must select the
largest tokenized example and use the exact command, adapter-loading mode, and
configuration that the full phase will use. "First example" is not a sampling
strategy.

### 5. Monitoring confused transport failure with process completion

The checkpoint mirror treated an SSH banner timeout as evidence that training
had exited. It stopped after checkpoint 125. Later status messages claimed
that checkpoints 150–300 had been mirrored without consulting the helper's own
log. Those claims were wrong.

Transport availability, training liveness, checkpoint completeness, and local
copy integrity are separate states. One cannot stand in for another.

## Token accounting

The completion reply reported `507,305` tokens from the goal meter. That was
not the session-wide token total. It covered the goal tool's active interval
and remained frozen after that goal was paused. Presenting it as the run's
token use was misleading.

The session's own token events at run completion reported:

| Counter | Tokens |
|---|---:|
| input | 127,773,519 |
| cached input | 125,464,832 |
| uncached input | 2,308,687 |
| output | 206,570 |
| reasoning output, included in output accounting | 84,847 |
| total | 127,980,089 |

Cached input was 98.0% of total accounting. This does not imply 127.98 million
tokens of novel text or a known dollar charge. The session ran under a Codex
Pro plan, and the log does not contain a price schedule that would support a
token-cost calculation.

The steady successful training phase was the largest token segment:

| Interval | Token increase | Cached-input increase | Output increase |
|---|---:|---:|---:|
| Ready report to status after idle | 404,123 | 314,368 | 2,025 |
| Status through stable attempt-8 launch | 22,579,953 | 22,066,688 | 46,433 |
| Attempt 8 monitoring | 7,655,218 | 7,465,984 | 11,192 |
| Failure recovery to hardened launch | 1,824,253 | 1,763,072 | 10,324 |
| Hardened run launch through training completion | 59,057,231 | 58,450,176 | 24,456 |
| Evaluation, retrieval, and teardown | 6,442,657 | 6,135,296 | 18,769 |

The agent repeatedly reprocessed a growing transcript to learn that the global
step had advanced. Running that same agent on the pod would not change this
context behavior.

### Local versus remote agent placement

| Design | H100-time effect | Token effect | Credential and recovery effect |
|---|---|---|---|
| Full agent on Proximal, direct SSH control | Sensitive to SSH/tool latency and agent turns | High when every poll is an agent turn | Credentials stay local; controller survives pod failure |
| Full agent on the H100 pod | Slightly lower command latency | Essentially unchanged without a new control loop | Agent/API credentials enter the pod; controller dies with the pod |
| Local agent + remote deterministic runner + local non-LLM watchdog | Removes agent turns from the steady path | Low; agent sees state changes and anomalies only | Credentials stay local; watchdog can stop or delete the pod |

The third design is the next-run target.

The remote runner should emit bounded JSON events such as:

```text
input_verified
preflight_started
preflight_passed
training_started
checkpoint_complete
training_complete
evaluation_complete
artifacts_ready
failed
```

It should also update one heartbeat record containing phase, PID, global step,
last-progress time, latest complete checkpoint, and failure reason. Progress
bars and repeated log tails should remain in files, outside agent context.

The local watchdog should:

1. be running before pod creation;
2. poll deterministically without invoking an LLM;
3. retry transport failures without changing training state;
4. stop the pod when preflight fails or the heartbeat becomes stale;
5. notify the agent only on state transition, anomaly, or completion;
6. pull and hash artifacts on `artifacts_ready`;
7. delete the pod after local verification;
8. verify 404 and zero current spend.

A fresh, compact agent session should handle closeout. The training monitor
does not need the full provisioning and dependency-debug transcript in every
turn.

## Next-run architecture

```text
no billing
    |
    | build image, pin inputs, validate config, arm local watchdog
    v
create encrypted H100 pod
    |
    | upload sft/ + config + runner, verify hashes
    v
worst-case GPU preflight ---- failure ----> local watchdog stops pod
    |
    v
training + checkpoint markers
    |
    v
final checkpoint -> separate eval -> artifact manifest
    |
    v
local rclone pull -> SHA-256 match -> pod delete -> 404/spend-zero check
```

The reasoning agent selects and prepares the run while billing is zero. The
runner executes already-selected actions. The watchdog owns the paid-resource
lifecycle.

## Ranked optimizations

### P0: required before another H100 launch

#### Build and pin a tested training image

Build the working dependency stack and the three retained source changes into
an image outside the rented H100. Reference it by digest, not a mutable tag.
The image build must fail if:

- installed versions differ from the bill of materials above;
- `pip check` fails;
- a retained patch does not apply exactly;
- the LLaMA Factory commit or model revision differs;
- config parsing changes `"no"` into a Boolean;
- the required imports are absent.

RunPod supports custom Pod templates and documents preloading public models in
an image. A cached image can avoid a repeated model download, but cold-pull
time for a 55.6GB model layer must be measured before treating it as a saving.
See [RunPod's custom-template documentation](https://docs.runpod.io/pods/templates/create-custom-template).

Do not place private SFT data or adapters in the image.

#### Start the runner as part of the launch transaction

The pod may wait only for the authorized `sft/` upload and its hash-verified
`input.ready` marker. It must not reach an operator-facing "ready" state that
requires another agent decision. The launch authority must state that it
includes preflight, training, separate evaluation, retrieval, and teardown.

#### Execute one maximum-risk preflight

Within ten minutes of creation, execute:

1. image digest, model revision, config hash, dataset hash, and `corpus/`
   absence checks;
2. real FA2, FLA/TileLang, bitsandbytes, and Liger kernels;
3. one complete optimizer step using the longest tokenized training records;
4. a checkpoint write and reopen;
5. the exact eval-only adapter load on the longest held-out record;
6. an assertion that the log says Liger was applied and no full logits tensor
   was returned.

If any item fails, stop GPU billing. Diagnose and rebuild off-pod. A stopped
pod retains its volume but releases its GPU, although later restart can fail
if another customer takes that GPU. RunPod documents this tradeoff in its
[stopped-pod guidance](https://docs.runpod.io/pods/troubleshooting/zero-gpus).

#### Keep evaluation outside the training process

Retain the successful config's `eval_strategy: "no"`. Save and validate the
final adapter before invoking evaluation. Evaluation failure must never erase
training progress.

#### Keep 25-step checkpoints

Each checkpoint write took roughly 13–22 seconds and protected about 25
minutes of training. Doubling the interval would save only a few minutes over
the whole run while doubling the loss window. Keep:

```yaml
save_steps: 25
save_total_limit: 3
eval_strategy: "no"
```

#### Replace the mirror helper

Create a checkpoint `.complete` marker only after all files close and the
remote manifest is written. The local mirror should consume markers, retry
SSH failures with bounded backoff, and mark a local checkpoint complete only
after SHA-256 comparison. A failed SSH connection means "transport unknown",
not "training exited".

The measured checkpoint transfer already saturated the route: 2.629GiB in
30.25 seconds, with a final average of 90.8MiB/s and peaks near 122MiB/s.
Rclone's SFTP backend uses concurrent reads by default and exposes per-file
request concurrency. See the [rclone SFTP documentation](https://rclone.org/sftp/).
WDT would add installation and listener work without shortening this run's
critical path.

#### Shorten lifecycle guards

Replace the 24-hour termination cap with a seven-hour cap for this exact
validated workload. The active watchdog remains the primary control; native
termination is the backstop. The target phase deadlines are:

| Deadline from pod creation | Required state |
|---|---|
| T+10m | worst-case preflight passed and training started |
| T+5h45m | training complete or within measured variance |
| T+5h55m | evaluation complete and artifacts local |
| T+6h00m | pod deleted and spend zero |
| T+7h00m | native hard termination |

If global step does not advance for ten minutes outside an announced
checkpoint phase, the watchdog should stop the pod and preserve the latest
checkpoint. The observed steps were normally well under two minutes; ten
minutes leaves room for checkpoint I/O without financing an open-ended stall.

### P1: reduce cold-start and controller overhead

#### Preload public model weights, then benchmark cold and warm starts

The model download finished in about 14 minutes and overlapped the original
FlashAttention build. A custom image may remove it on a warm host, but a large
cold image pull can move the same bytes to another path.

RunPod network volumes are not suitable for the private working directory:
they are not encrypted and replace the encrypted volume at `/workspace`.
They could hold public weights, but not at the same mount while preserving the
current encrypted-volume design. See
[RunPod storage types](https://docs.runpod.io/pods/storage/types).

Accept model preloading only after three measurements:

- cold image start to local model availability;
- warm image start to local model availability;
- direct Hugging Face download to encrypted volume.

#### Precompute tokenized inputs and risk fixtures

Generate, before launch:

- exact token counts under the pinned tokenizer and chat template;
- the longest train and eval fixture IDs;
- the set of records truncated by `cutoff_len`;
- dataset and config manifests.

This saves little H100 time by itself. Its value is making the paid preflight
representative and deterministic.

#### Bound agent context

The next run should spend no model tokens during steady progress polling.
Use at most:

- one agent turn to validate launch readiness and create the pod;
- one state-change turn after worst-case preflight;
- one anomaly turn if the watchdog detects a failure;
- one closeout turn after `artifacts_ready`.

Use a new compact session for closeout. A practical token-accounting target is
less than 5% of this run's 127.98M total, with less than 1M during the
successful training interval. This target concerns product accounting, not a
promised dollar amount.

### P2: measured experiments before changing training semantics

These may lower the 5h34m training floor. None is established by this incident.

#### Evaluate whether two epochs are necessary

The logged mean training loss fell from `1.2750` in epoch one to `1.0164` in
epoch two. That shows continued fitting, not held-out quality. No epoch-one
held-out evaluation was retained.

Before another full paid run, evaluate checkpoint 100, checkpoint 125, and the
final adapter through the repository's production-style held-out scorer on
local hardware or a cheaper GPU. If checkpoint 125 matches the final adapter
on JSON validity, legal verdicts, side match, and fate agreement, a one-epoch
run would nearly halve training time. Until then, reducing epochs is an
unverified semantic change.

#### Ablate the non-review datasets

The exact retained tokenizer and template measured this one-epoch work proxy:

| Dataset | Examples | Effective tokens at 40,960 | Truncated examples |
|---|---:|---:|---:|
| review | 882 | 13,452,336 | 6 |
| implementation planning | 155 | 3,815,808 | 49 |
| design convergence | 141 | 3,708,754 | 53 |
| proposal generation | 90 | 744,871 | 0 |
| total | 1,268 | 21,721,769 | 108 |

Review-only training is 61.9% of the current effective-token proxy and directly
matches the target lane. That makes it a strong ablation candidate, not an
automatic deletion. The other tasks may teach useful structure or may dilute
review behavior. Only held-out generation metrics can decide.

#### Do not lower `cutoff_len` for a small nominal saving

At 40,960 tokens, 108 examples are already truncated. A 32,768 cutoff reduces
the capped token count by only 5.50% while increasing the truncated population
to 182 examples. A 24,576 cutoff reduces the proxy by 14.78% but truncates 345
examples.

Because Qwen3.6 mixes attention mechanisms, token-count reduction is not an
end-to-end runtime prediction. Benchmark one representative optimizer step
and inspect the truncated targets before changing the cutoff.

#### Benchmark gradient checkpointing on a larger-memory GPU

PyTorch activation checkpointing saves memory by recomputing forward
activations during backward, so it directly trades time for memory. See the
[PyTorch checkpointing documentation](https://docs.pytorch.org/docs/stable/checkpoint.html).

The final H100 run used about 67GB at peak with checkpointing enabled. A
larger-memory H200 or B200 might run without checkpointing and finish sooner,
but the current kernel stack, hourly price, and exact one-step throughput must
be measured. Compare:

```text
cost per optimizer step =
    hourly pod rate × median optimizer-step seconds / 3600
```

Use the same eight microbatches, longest-record mix, effective batch size,
image digest, and correctness assertions. A faster but more expensive GPU is
accepted only if it improves the selected objective: elapsed pod time, total
GPU-hours, or dollars. Those are different metrics.

#### Benchmark FlashQLA without extrapolating its published results

Qwen's [FlashQLA](https://github.com/QwenLM/FlashQLA) targets the gated-delta
rule used by Qwen3.5/3.6 and publishes comparisons against FLA 0.5.0. Its
retained benchmark results are for H200 and GB200, not this H100 QLoRA
workload. It must pass numerical forward/backward comparison and an end-to-end
optimizer-step benchmark before replacing FLA.

Retain Liger fused linear cross-entropy unless a candidate proves equivalent
memory behavior. Liger explicitly supports Qwen3.5's fused linear
cross-entropy path; its published aggregate speedups come from different
models and hardware and are not predictions for this run. See
[Liger Kernel](https://github.com/linkedin/Liger-Kernel).

#### Defer multi-GPU, packing, and `torch.compile`

- Two replicated H100s may lower elapsed time while leaving GPU-hours flat or
  higher. Variable sequence lengths also create stragglers.
- Packing changes example boundaries and optimizer-step semantics; it needs a
  quality-preserving experiment.
- `torch.compile` adds compilation and graph-break risk to a stack that already
  needed three source changes.

None addresses the demonstrated structural waste as cheaply as a pinned image,
representative preflight, and deterministic lifecycle controller.

## Required launch gate

Do not create another paid pod until a local readiness artifact records:

- immutable image digest;
- base-model repository and revision;
- LLaMA Factory commit;
- package lock and applied-patch hashes;
- training and eval config hashes;
- SFT file manifest and total authorized bytes;
- longest train and eval fixture IDs and token counts;
- explicit absence of `corpus/` from the upload manifest;
- watchdog PID and tested stop/delete credentials;
- six-hour target and seven-hour hard termination;
- local rclone destination with sufficient free space;
- selected objective: elapsed pod time, GPU-hours, or dollars.

The launch gate proves preparation, not H100 compatibility. The first paid
phase remains the maximum-risk GPU preflight. Failure of that preflight must
stop billing within ten minutes.

## Success criteria for the next run

The next run is successful only when all of these hold:

- training starts within ten minutes of pod creation;
- no interactive package installation or source editing occurs on the H100;
- maximum-risk train and eval smoke paths pass before the full run;
- inline evaluation remains disabled;
- every checkpoint-copy claim is backed by a local completion marker and hash
  result;
- final adapter and terminal checkpoint are local and hash-verified;
- pod deletion is confirmed by 404;
- current spend returns to zero;
- launch-to-delete is at most six hours for the unchanged workload;
- steady-state training monitoring uses less than 1M token-accounting units.

If the unchanged workload misses six hours, preserve the logs and profile the
measured training path. Do not compensate by silently cutting examples,
cutoff, epochs, or evaluation.

## Evidence and limitations

Primary retained evidence:

- [successful training log](../../out/review-sft-r1/run-metadata/logs/review-sft-r1.log)
- [lost step-100 attempt](../../out/review-sft-r1/run-metadata/logs/review-sft-r1.attempt8.log)
- [discarded six-step attempt](../../out/review-sft-r1/run-metadata/logs/review-sft-r1.attempt9-early.log)
- [first eval-only OOM](../../out/review-sft-r1/run-metadata/logs/review-sft-r1-final-eval.attempt1-oom.log)
- [successful held-out evaluation](../../out/review-sft-r1/run-metadata/logs/review-sft-r1-final-eval.log)
- [successful training config](../../out/review-sft-r1/run-metadata/configs/review_sft_qlora.liger-checkpointed.yaml)
- [successful eval config](../../out/review-sft-r1/run-metadata/configs/review_sft_qlora.liger-final-eval.yaml)
- [retained source patches](../../out/review-sft-r1/run-metadata/patches/)

The authenticated RunPod billing API was queried after the final hourly bucket
settled. Token counts came from the session's `token_count` events. Dataset
lengths were recomputed from all 1,268 train records with Transformers 5.6.0,
the retained tokenizer, the retained chat template, and
`enable_thinking=false`.

Logs for launches 1–7 were not copied before pod deletion. Their sequence is
reconstructed from the timestamped operator transcript and retained before/
after patch files. This is sufficient to identify the integration work that
must move out of the paid path, but not to compare per-attempt GPU profiles.

No comparative end-to-end benchmark exists yet for FlashQLA, another GPU type,
disabled or selective gradient checkpointing, packing, a shorter cutoff,
review-only data, or one epoch. Those omissions are material to selecting any
of those changes, so this postmortem specifies experiments and abstains from
claiming savings.

## Doctrine receipt

The recommendation used validated Pincite packet
`pkt-f49f4b7cafd9a49f`, content SHA-256
`f49f4b7cafd9a49f269dc98351ab98b52b787b58c3bee7a20b916d9905f63494`.

- corpus: `corpus-2026-07-12-a11702cc9217`
- doctrine: `doctrine-f6bbb5196a3f8bf9`
- retriever: `retriever-5cc7d0e807e255a4`
- authority ceiling: recommend

The applied concepts were evidence before intervention, causal bottleneck
selection, work elimination before kernel specialization, representative
baselines, metric semantics, and preservation of training behavior. Missing
comparative profiles and repeated benchmarks are nonmaterial to removing the
observed idle period, checkpoint/eval coupling, and LLM polling. They are
material to kernel, GPU, cutoff, dataset, packing, and epoch changes, which is
why those remain experiments.

Primary source locators from the packet were:

- `Efficient Go`, Chapter 3, "Resource-Aware Efficiency Requirements";
- `Efficient Go`, Chapter 7, "Practical Applications";
- `Efficient Go`, Chapter 8, "Reliability of Experiments," "Reproducing
  Production," and "Benchmarking Levels";
- `Efficient Go`, Chapter 9, "Root Cause Analysis, but for Efficiency";
- `Efficient Go`, Chapter 11, "Do Less Work."
