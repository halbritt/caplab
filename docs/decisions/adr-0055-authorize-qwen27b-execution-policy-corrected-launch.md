---
id: adr-0055
artifact_type: architecture-decision-record
title: Authorize the execution-policy-corrected Qwen3.6-27B launch
status: consumed-stopped
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

# Authorize the execution-policy-corrected Qwen3.6-27B launch

## Observation and disposition

ADR 0054 acquired lease `42dede73-fb02-4400-9267-9cb657a4f430` and entered the
contained qualification process. Windows then refused
`caplab16_peecee_r2.ps1` because script execution was disabled. The child exited
1 before Python, checkpoint loading, forward/backward work, optimizer state, or
held-out access. Local custody contains the lease-bound process identity,
process outcome, fleet observations, and cleanup result. Ollama and the GPU were
reachable after cleanup, and the lease was released.

This is an infrastructure launch failure before model qualification, not a
training attempt. The r2 scientific preregistration remains unchanged and the
training-start marker does not exist.

## Decision and exact effects

Authorize the exact effects in
[`training-execution-q2.json`](../product/training/caplab-review-dissent-local-qwen-r2/training-execution-q2.json),
file SHA-256 `460ed579e65f6eb83f456fdaee4df1a655c1986a8eb63feb66c67ce250f291c1`,
until `2026-07-22T12:00:00Z`.

The only launch correction is adding `powershell.exe -ExecutionPolicy Bypass`
to the contained child command. This setting applies to that child process. It
does not modify machine, user, registry, group-policy, Ollama, GPU-fleet, or
Striatum configuration.

The corrected launch uses a fresh remote root ending in `-r2-q2` and a fresh
local custody root. The failed qualification root remains unchanged. The new
authorization permits one qualification/training lease and one contingent
evaluation lease. Scientific fields, model-call limits, replacement ceiling,
containment, boot identity, and cleanup requirements remain those in ADRs 0053
and 0054.

Qualification failure still consumes no training attempt. Creation of
`training-started.json` consumes the one r2 training attempt. No further launch
correction or retry is authorized by this decision.

## Status history

- `2026-07-21` — `authorized` — the ADR 0026 delegate authorized one
  child-process-only execution-policy correction after the contained launch
  failed before model loading.
- `2026-07-21` — `consumed-stopped` — the contained PowerShell process started,
  but module auto-loading did not expose `Get-FileHash`; the digest gate failed
  before Python or model loading. ADR 0056 governs any corrected launch.
