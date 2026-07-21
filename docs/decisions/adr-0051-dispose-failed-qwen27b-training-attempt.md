---
id: adr-0051
artifact_type: architecture-decision-record
title: Dispose the failed Qwen3.6-27B training attempt
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-21
decided_at: 2026-07-21
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

# Dispose the failed Qwen3.6-27B training attempt

## Observation

ADR 0050's exact environment, checkpoint, corpus, target-module, tokenization,
and no-update forward/backward preflight passed. The preflight loss was
`0.722461760044`; all three records were below 4096 tokens; 992 language-model
adapter tensors comprising 58,363,904 trainable parameters were selected.

The sole training attempt started and reached observed optimizer step 3 of 12.
Its step-3 checkpoint began materializing, but the `peecee` GPU stopped
answering `nvidia-smi`. At `2026-07-21T00:17:37Z` the fleet heartbeat first
recorded the ten-second GPU probe timeout. The slot became non-live, the lease
renewal failed closed, and `gpu-fleet-run` terminated its local child group.

Windows did not propagate the SSH teardown to the remote trainer. The exact
PowerShell/Python process tree was resolved by PID and command line, then
terminated. The GPU remained unresponsive to `nvidia-smi`; the fleet de-listed
both `peecee` slots. Ollama's HTTP inventory endpoint still answered, but decode
availability could not be verified without a working GPU probe.

## Decision

Classify the attempt as
`training-infrastructure-gpu-unresponsive-and-lease-lost`. The
`training-started.json` marker consumed the one authorized attempt. Do not
resume, restart, substitute a host, alter the fleet fence, evaluate the
step-3 bytes, open held-out content, or treat the partial adapter as a model
candidate.

Preserve the partial checkpoint and complete raw custody. The committed result
is [`training-result.json`](../product/training/caplab-review-dissent-local-qwen-r1/training-result.json).
Its file SHA-256 is
`f65262006596a2553a02e57f06c442002e3a993b5117879edde43904b17ae705`.
Its raw inventory SHA-256 is
`9e0b9b1e00745e58dbac8583d2b70548d4b236ea71a5cacc1878063833345c98`.
The held-out families remain sealed and unopened; zero evaluation or general
control calls occurred and paid cost is USD 0.

CAPLAB-16 is not complete: it has no final adapter or base/tuned held-out
comparison. A future attempt requires a new preregistration and authorization,
plus independent restoration of the `peecee` GPU and a host coordination design
that proves a heavy CUDA job remains observable without losing its lease.

## Host boundary

A host reboot, display-driver reset, GPU-fleet repair, or retry is outside this
CAPLAB disposition. Those effects may be useful, but blanket CAPLAB product
decision authority does not silently become authority to reboot a shared host
or change another product's scheduler. The safe CAPLAB action is preservation
and a truthful blocked state.

## Status history

- `2026-07-21` — `decided` — the ADR 0026 delegate classified the consumed
  infrastructure failure, prohibited retry and held-out access, preserved raw
  custody, and left CAPLAB-16 incomplete.
