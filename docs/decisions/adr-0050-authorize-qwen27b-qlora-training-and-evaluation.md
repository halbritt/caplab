---
id: adr-0050
artifact_type: architecture-decision-record
title: Qwen3.6-27B QLoRA training and held-out evaluation authorization
status: authorized
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
  - peecee-host-integration
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Qwen3.6-27B QLoRA training and held-out evaluation authorization

## Preconditions

CAPLAB-14 produced the seven-row local-only corpus. CAPLAB-15 and ADR 0049
preregistered one Qwen3.6-27B QLoRA SFT attempt before any training or held-out
read. Proximal's only GPU is occupied by its load-bearing `llama-27b.service`,
which CAPLAB does not own and may not stop.

The owner-controlled `peecee` host is the documented exclusive batch GPU path.
Read-only inspection found one RTX 3090 Ti with 24,564 MiB VRAM, 64 GiB host
RAM, 2.4 TB free disk, CUDA Torch `2.12.1+cu130`, and an available `gpu-fleet`
`marker` slot 1. Its host contract permits a batch job to unload a resident
Ollama model while holding the card. The scientific preregistration was amended
before execution to bind this exact host; no model, data, method, seed, step,
evaluation, success, or claim rule changed.

## Decision and authorization

Authorize the exact effects in [`training-execution.json`](../product/training/caplab-review-dissent-local-qwen-r1/training-execution.json)
file SHA-256
`8bb20fa57ecfa505be862e59770d5fafd6558cd96731b67d386b697f8b946135`,
until `2026-07-22T00:00:00Z`:

1. acquire one exclusive `gpu-fleet` lease for `peecee`'s `marker` slot;
2. unload only the resident `qwen3.6:27b` Ollama model without stopping or
   reconfiguring the Ollama service;
3. create one additive, isolated CAPLAB environment and install the exact
   preregistered packages;
4. download the official immutable Qwen3.6-27B checkpoint and verify its index;
5. run one no-update forward/backward preflight and, only if it passes, one
   12-step QLoRA training attempt under the frozen two-hour ceiling;
6. seal the adapter before opening held-out content;
7. run the frozen held-out and coding-control comparisons through native
   `striatum-openai-lane` v1 against one transient CAPLAB endpoint that exposes
   the same base with the adapter disabled or enabled; and
8. stop the transient endpoint, release the lease, verify Ollama service
   availability, and preserve complete custody.

The source script, corpus, control set, and preregistration are digest-bound.
The permitted maximum is 24 primary evaluation calls plus two
infrastructure-only replacements and zero USD.

## Boundaries and stops

The authorization does not stop Proximal's inference service, stop or alter
Peecee's Ollama service, use proprietary model output, use a proxy harness,
deploy the adapter, modify Striatum, change scheduler policy, publish the
checkpoint, or infer universal superiority. The GPU-fleet lease is a host
coordination mechanism, not CAPLAB product authority.

Stop and preserve evidence on any digest, revision, architecture, package,
hardware, lease, adapter-target, data, held-out-order, native-harness, resource,
privacy, or cleanup mismatch. A no-update preflight failure does not consume the
training attempt; any failure after `training-started.json` does. No
hyperparameter, package, model, dataset, or host substitution is authorized.

## Verification and decision boundary

Technical verification must independently recompute source and output hashes,
checkpoint steps, training losses, resource use, paired evaluation scores,
control correctness, failures, latency, and zero-USD cost. The result then
supplies evidence to CAPLAB-17. Successful training or evaluation is not
deployment, lane-fit acceptance, scheduler policy, or a universal model claim.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized one exact
  lease-coordinated batch training attempt and its frozen native-harness
  evaluation, with contingent held-out access only after adapter seal.
