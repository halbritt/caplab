---
id: caplab-review-dissent-qwen27b-qlora-r1
artifact_type: training-experiment-preregistration
title: Qwen3.6-27B review-dissent QLoRA r1
status: preregistered
created: 2026-07-20
decision_record: adr-0049
decision_authority: adr-0026
execution_authorized: false
---

# Qwen3.6-27B review-dissent QLoRA r1

The machine-readable experiment contract is [`training-experiment.json`](training-experiment.json),
file SHA-256
`a9f202a1c48d6fff34c82541b5777cf7f7ca7253d78296d4a98ed3873d8db16e`.

## Question and claim ceiling

Can one fixed QLoRA supervised fine-tuning attempt improve the official
Qwen3.6-27B checkpoint's mechanically scored evidence-grounded review dissent
on the sealed `RD-H01` and `RD-H02` families without increasing clean
false-blockers or materially regressing four small general coding controls?

The maximum positive claim is improvement for the named checkpoint, method,
native Striatum review tuple, and eight synthetic held-out cells under the
`striatum-fresh-review-v1` pass profile. A positive result is not universal
model superiority, broad coding improvement, safety evidence, deployment
approval, or lane-fit acceptance. A negative or failed attempt remains
evidence and is not silently replaced.

## Frozen inputs

### Base checkpoint

- repository: `Qwen/Qwen3.6-27B`;
- immutable revision:
  `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`;
- architecture: `Qwen3_5ForConditionalGeneration`, 64 text layers, dense MLP;
- official BF16 parameter count: `27,781,427,952`;
- safetensors total bytes: `55,562,855,904` across 15 shards;
- `model.safetensors.index.json` SHA-256:
  `a8ad2c26fb707ff8c245806315b03e3b4b74595528492423af5dae0ce39b4d9b`;
- tokenizer and configuration: the same immutable revision;
- license boundary: Apache-2.0 as identified by the upstream model card.

Any upstream revision, index, shard, tokenizer, configuration, architecture,
or license mismatch stops the attempt.

### Training corpus

- path: `docs/product/training/caplab-review-dissent-local-qwen-r1/corpus.json`;
- file SHA-256:
  `09ec666630189ebbe9bf180d3dd567623f8dbee753871f63ac7f66c712cb87f2`;
- semantic SHA-256:
  `303a55e6594528ab520d9fbc92d306cd942d4d6a76c68ef314797aa0c84cf1e5`;
- training family: `RD-D01` only;
- training records: exactly `r02-local-qwen-review`,
  `r03-local-qwen-review`, and `r04-local-qwen-review`;
- training field: prompt followed by the `chosen` JSON response only;
- ignored fields: `rejected`, mechanical score, development rows, and every
  held-out identity or byte.

All three chosen responses are supervised targets. The contrastive rejected
response is deliberately unused because this is one SFT method, not a mixed
SFT/DPO experiment.

### Evaluation controls

The sealed held-out families remain `RD-H01` and `RD-H02`, four factorial cells
each. Their current aggregate SHA-256 is
`ec7ef0160e878608094f190b7af5bb3c20e4183e7621cdb5d9d1464fb5fe2834`.
They may not be opened until the base identity and final trained adapter are
sealed.

The four model-free general coding controls are frozen at
`general-coding-controls.json`, file SHA-256
`3f228381f6eb6175e8924af00709c3fe01e66bcb7f7c2601585ac09272647108`.
They cover sequence reasoning, boundary reasoning, control-flow debugging, and
complexity analysis with exact mechanical answers. They are regression guards,
not training examples and not evidence of broad coding capability.

## Frozen training method and configuration

Method: one 4-bit QLoRA causal-language-model supervised fine-tuning run.

| Parameter | Frozen value |
|---|---|
| Weight quantization | NF4, 4-bit load, double quantization, BF16 compute |
| LoRA rank / alpha / dropout | `8` / `16` / `0.05` |
| Bias | `none` |
| Target projections | language-model `q_proj`, `k_proj`, `v_proj`, `o_proj`, `in_proj_qkv`, `in_proj_a`, `in_proj_b`, `in_proj_z`, `out_proj`, `gate_proj`, `up_proj`, `down_proj` only |
| Vision parameters | frozen and excluded |
| Maximum sequence length | `4096` tokens; right truncation; no packing |
| Per-device batch / accumulation | `1` / `1` |
| Epochs / optimizer-step ceiling | `4` / `12` |
| Optimizer | paged AdamW 8-bit |
| Learning rate / schedule | `5e-5` / constant, no warmup |
| Weight decay / gradient clip | `0.0` / `1.0` |
| Gradient checkpointing | enabled, non-reentrant |
| Precision | BF16 compute; TF32 allowed |
| Seed | `1729` for Python, NumPy, Torch, CUDA, data order, and adapter initialization |
| Reporting | no external reporter or telemetry |

The isolated toolchain is frozen to CPython 3.11, Torch `2.7.0+cu126`,
Transformers `5.14.1`, PEFT `0.19.1`, TRL `1.8.0`, BitsAndBytes `0.49.2`, and
Accelerate `1.14.0`. Before any checkpoint download or training, CAPLAB-16
must prove that this exact set recognizes the architecture, enumerates every
and only frozen adapter target, tokenizes all three records within the frozen
truncation rule, and supports one no-update forward/backward smoke step. A
failure stops the experiment; it does not authorize a version or parameter
substitution.

## Compute ceiling, checkpoints, and stops

The execution ceiling is one RTX 3090, 24 GiB device memory, at most 96 GiB
host RAM, 100 GiB additive disk, two wall-clock GPU hours after model load, 12
optimizer steps, and one training attempt. No remote compute or paid service is
permitted.

Retain the immutable source identities, environment lock, exact command,
trainer state, logs, final adapter, and checkpoints after steps 3, 6, 9, and
12 through the CAPLAB-17 disposition. The step-12 adapter is the sole tuned
candidate; loss or development performance cannot select another checkpoint.

Stop immediately and preserve partial custody on:

- checkpoint, tokenizer, corpus, control, target-module, or environment drift;
- inability to obtain an exclusive GPU without mutating another product's
  runtime;
- out-of-memory, non-finite loss or gradient, framework crash, host-memory or
  disk ceiling, two-hour ceiling, or more than 12 optimizer steps;
- any held-out read before the final adapter and base identity are sealed;
- secret, personal-data, or non-synthetic third-party-content discovery;
- external telemetry, remote inference, provider output, or proxy harness; or
- any need to change a frozen value.

Infrastructure failure consumes the one attempt unless it happens during the
explicit no-update preflight. Training may not be restarted from a partial
checkpoint under this preregistration.

## Frozen evaluation

After a successful step-12 seal, evaluate the base and tuned subjects through
the same native Striatum tuple: `striatum-openai-lane` v1, a CAPLAB-owned local
OpenAI-compatible serving endpoint, temperature `0`, maximum output 4096
tokens, and the exact review prompt/schema used by the local-Qwen development
campaign. The only subject difference is the frozen adapter. A generic proxy
harness is forbidden.

Open each held-out cell only when its paired base and tuned slots are ready.
Run all eight cells once per subject. Subject-invalid output consumes its slot;
only a recorded harness, server, capture, task-image, or verifier failure may
receive one same-subject replacement, with at most two replacements total.
Randomize pair order with seed `1729`; keep cells paired and conceal the
mechanical oracle from both subjects.

Run each of the four general coding controls once per subject through the same
native harness and decoding limits. Grade only exact JSON/schema validity and
exact answer equality. No replacement is allowed for a subject-invalid answer.

## Primary analysis and success rule

The primary analysis is the paired tuned-minus-base mechanical score difference
over the eight held-out review cells. Report every pair, both means, the mean
difference, schema-valid counts, score-band counts, defect false-clears, clean
false-blockers, abstentions, and all infrastructure outcomes. With eight cells,
the result is descriptive; no significance claim or post-hoc subgroup replaces
the primary analysis.

The experiment succeeds for its named capability only if all are true:

1. the tuned held-out mean exceeds the base mean by at least `0.10`;
2. tuned schema-valid count is at least the base count;
3. tuned clean false-blockers are zero and no greater than base;
4. tuned defect false-clears are no greater than base; and
5. tuned general-control exact answers are at least `base_correct - 1`, with
   no lower schema-valid count.

Otherwise the result is negative, inconclusive, or infrastructure-failed as
mechanically determined. No universal claim follows either way. CAPLAB-17
must separately decide whether to stop, gather more evidence, revise the
dataset, or recommend a Striatum-lane follow-up. This preregistration authorizes
zero downloads, installations, training, held-out reads, evaluation calls,
deployment, or policy change.

## Lifecycle

- `2026-07-20` — `preregistered` — model, corpus, method, configuration, seed,
  resource ceiling, checkpoints, stop rules, held-out evaluation, coding
  controls, regression rule, primary analysis, and claim ceiling frozen. Zero
  execution effects are authorized.
