---
id: adr-0058
artifact_type: architecture-decision-record
title: Authorize the lease-aware fleet-status launch
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

# Authorize the lease-aware fleet-status launch

## Observation and correction

Q4 acquired both authorized leases and started its contained qualification
child. At the next heartbeat, gpu-fleet suppressed competing decode probes and
used GPU reachability because the leases were active. By design, that weaker
probe changed each leased row from `routable` to `probationary` while preserving
fresh liveness and the exact lease identifiers.

CAPLAB's controller rejected slot 1 solely because it still required
`routable`. It stopped before writing a qualification observation. The remote
pulse then expired and the Windows Job Object terminated the child. Custody
contains the process identity, the `remote-pulse-expired-tree-terminated`
outcome, an empty fleet-observation stream, and only the qualification
environment file. There is no qualification result, training-start marker,
optimizer step, adapter, or held-out read. The one r2 training attempt remains
unconsumed.

The correction accepts `routable` or `probationary` only while the sampled row
is alive, fresh, and bound to the controller's exact active lease. It does not
accept `unverified`, weaken lease identity, change gpu-fleet policy, or alter a
scientific field.

## Decision and exact effects

Authorize the exact effects in
[`training-execution-q5.json`](../product/training/caplab-review-dissent-local-qwen-r2/training-execution-q5.json),
file SHA-256 `65ad70bb0b3cfbeb227b480e73bd801b4b32f1e3caf4938de4a92ecacf58807f`,
until `2026-07-22T12:00:00Z`.

Q5 uses fresh remote and local custody roots ending in `-r2-q5`. It preserves
the rebound boot binding, module-independent digest checks, dual-slot exclusion,
native harness, sealed held-out boundary, model-call ceilings, and containment.
It permits one fresh no-update qualification and the still-unconsumed training
attempt, followed by evaluation only if a final adapter is sealed.

## Status history

- `2026-07-21` — `authorized` — the ADR 0026 delegate authorized the narrow
  lease-aware status correction and the fresh q5 custody roots.
