---
id: adr-0049
artifact_type: architecture-decision-record
title: Preregister Qwen 27B review-dissent QLoRA experiment
status: preregistered
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - review-dissent-001
  - governed-model-training
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Preregister Qwen 27B review-dissent QLoRA experiment

## Decision

Preregister one bounded 4-bit QLoRA supervised fine-tuning experiment on the
official `Qwen/Qwen3.6-27B` checkpoint at immutable revision
`6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`. The exact training, comparison,
evaluation, retention, and stop contract is
[`caplab-review-dissent-qwen27b-qlora-r1-preregistration.md`](../product/training/caplab-review-dissent-local-qwen-r1/caplab-review-dissent-qwen27b-qlora-r1-preregistration.md).

The experiment targets only schema-stable, evidence-grounded review dissent
with clean-case false-refusal control in the `striatum-fresh-review-v1`
profile. It does not target or claim general coding improvement, broad review
quality, safety, model ranking, universal superiority, or Striatum lane fit.

The executable zero-authority manifest is
[`training-experiment.json`](../product/training/caplab-review-dissent-local-qwen-r1/training-experiment.json),
file SHA-256
`a9f202a1c48d6fff34c82541b5777cf7f7ca7253d78296d4a98ed3873d8db16e`.

## Model comparison

The locally relevant alternatives are the official 27B dense checkpoint and
the official 35B-A3B mixture-of-experts checkpoint.

| Consideration | Qwen3.6-27B dense | Qwen3.6-35B-A3B MoE |
|---|---|---|
| Official immutable revision | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | `995ad96eacd98c81ed38be0c5b274b04031597b0` |
| BF16 parameter bytes | `55,562,855,904` in 15 shards | `71,903,645,408` in 26 shards |
| Topology | 64 dense text layers; all language parameters participate | 40 text layers; 256 experts and 8 selected experts per token |
| Capability evidence in CAPLAB | Not yet measured on the review-dissent instrument | Seven valid development reviews: six `1.0`, one clean false-blocker `0.2`; one additional response truncated |
| Adapter trainability | Conventional attention, linear-attention, and MLP projection targets; smaller checkpoint and simpler target audit | Sparse routing makes active inference compute attractive, but expert coverage, target selection, and adapter state are substantially more complex |
| Current serving evidence | Local IQ4 and Q5 GGUF files fit on the 24 GiB RTX 3090; throughput is unmeasured | The APEX I-Compact GGUF fits and is currently served; that quant is inference custody, not a trainable checkpoint |
| Expected training constraint | Estimated 4-bit base residency is feasible only in an exclusive-GPU window with checkpointing and short sequences | Larger source checkpoint and expert-adapter surface increase storage, memory, framework, and verification risk despite roughly 3B active inference parameters |

Select 27B because it makes the first training intervention smaller and more
auditable. The selection is not based on parameter count alone and does not
infer superior capability. The 35B development observations identify the
candidate failure mode but do not prove that it transfers to the 27B base.

The upstream index identities are frozen as additional drift checks:

- 27B index SHA-256:
  `a8ad2c26fb707ff8c245806315b03e3b4b74595528492423af5dae0ce39b4d9b`;
- 35B-A3B index SHA-256:
  `41b9356101ebf8e7519e150dc811f80c4226e727301fbb032b890f006ed0be83`.

## Advisory doctrine

Pincite packet `pkt-aec71995c3f2cb2d`, packet-file SHA-256
`ef0984f5d9123c97ec1a7e4271654c3cfe1d560d5a1253b46ef9491d983f08a7`,
and packet-content SHA-256
`aec71995c3f2cb2d3a49c23eaa1d93637caecf906a481d5739f03b3491493734`
supplied advisory guidance on bounded authority, explicit evidence,
privacy, lifecycle, local contracts, and verification. The immutable inputs,
zero-authority executable manifest, resource ceilings, retention contract,
fail-closed stops, tests, and separate CAPLAB-16 authorization gate apply that
guidance without transferring CAPLAB product authority.

## Authorization boundary

This record freezes a design and authorizes zero training, evaluation, model
download, package installation, server mutation, held-out access, deployment,
or Striatum policy change. CAPLAB-16 requires a later exact execution
authorization after a resource and toolchain preflight proves that the frozen
attempt can run without taking ownership of another product's runtime.

Any unavailable checkpoint, incompatible toolchain, non-exclusive GPU,
insufficient storage or host memory, dataset drift, held-out exposure, or need
to change a frozen hyperparameter is a stop, not permission to improvise.

## Status history

- `2026-07-20` — `preregistered` — the ADR 0026 delegate selected the dense
  27B checkpoint and froze one bounded QLoRA SFT attempt and its comparisons.
  Zero training or evaluation calls are authorized.
