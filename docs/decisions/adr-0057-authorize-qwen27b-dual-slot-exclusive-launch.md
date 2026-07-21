---
id: adr-0057
artifact_type: architecture-decision-record
title: Authorize the rebound-host dual-slot exclusive launch
status: authorized
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
  - peecee-host-integration
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Authorize the rebound-host dual-slot exclusive launch

## Rebound host and capacity observation

The NVIDIA installation completed and rebooted `peecee` at
`2026-07-21T04:16:37.5000000Z`. Driver `596.49` reports the same RTX 3090 Ti
and 24,564 MiB total memory. Ollama responds, both fleet slots are fresh and
`routable`, and no installer remains. Q3 acquired no lease because its old boot
identity failed before execution.

After reboot, the independently served `qwen3-vl:8b` slot 0 model is resident
with an 8.0 GB allocation and `Forever` keep-alive. Only 14,177 MiB is free.
R1's exact preflight recorded 24,854 MiB peak allocator demand, so running r2
beside the resident model would predictably breach capacity.

## Decision and exact effects

Authorize the exact effects in
[`training-execution-q4.json`](../product/training/caplab-review-dissent-local-qwen-r2/training-execution-q4.json),
file SHA-256 `2763886bc67bfb7b96469916fb4d5981fea5c59bdc43a5921d34326fbf8b2db0`, until `2026-07-22T12:00:00Z`.

Training and evaluation each acquire both logical leases on the shared physical
GPU: outer slot 0 for `qwen3-vl:8b`, then inner marker slot 1 for the CAPLAB
session. Only after both leases are held may the contained child temporarily
unload `qwen3-vl:8b`. The fleet slot 0 probe owns normal model reload after both
leases are released. CAPLAB does not change keep-alive, endpoint, model files,
service configuration, or fleet policy.

The nested lease order is fixed to slot 0 then slot 1. Loss of either lease
terminates its child process group; loss of the inner controller also stops the
remote pulse and causes the Windows Job Object to terminate its process tree.
No ordinary slot 0 request can overlap the temporary unload because its lease
is held for the full phase.

Q4 uses fresh remote and local custody roots ending in `-r2-q4`. It retains the
module-independent SHA-256 correction from ADR 0056 and binds the new boot
identity. It permits four lease acquisitions total: two concurrent leases for
qualification/training and two concurrent leases for contingent evaluation.
All scientific fields, model-call limits, replacement ceilings, and the single
unconsumed r2 training attempt remain unchanged.

## Status history

- `2026-07-21` — `authorized` — the ADR 0026 delegate rebound execution to the
  recovered boot and required dual-slot exclusion before temporarily unloading
  the resident slot 0 model.
