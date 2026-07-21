---
id: adr-0056
artifact_type: architecture-decision-record
title: Authorize the module-independent digest launch
status: invalidated-pre-effect
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

# Authorize the module-independent digest launch

## Observation and disposition

ADR 0055 acquired lease `e8d331bf-46a3-432b-af7b-c1325b38244e` and successfully
entered the contained PowerShell child with process-scoped execution-policy
bypass. The child then reported that `Get-FileHash` was unavailable. It exited
1 at the first digest check, before Python, model loading, qualification work,
the training-start marker, or held-out access.

The released-lease cleanup found the GPU reachable at first, then observed
Ollama unavailable. Subsequent probes found `setup.exe` and
`TrustedInstaller.exe` running, `nvidia-smi.exe` absent from PATH, an unpacked
NVIDIA display-driver tree under `C:\Windows\Temp`, and both `peecee` fleet
slots de-listed. This decision authorizes no execution while that external
driver transition continues.

## Decision and exact effects

Authorize the exact effects in
[`training-execution-q3.json`](../product/training/caplab-review-dissent-local-qwen-r2/training-execution-q3.json),
file SHA-256 `0c1d573fd9ddd064719ce46e9ab52373192d6b6cae21fa7bc0f077a057697d4a`,
until `2026-07-22T12:00:00Z`, contingent
on all of these observations immediately before the lease:

- the authorized boot identity is unchanged;
- `setup.exe` is no longer running;
- `nvidia-smi` succeeds from its installed location;
- GPU-fleet slot 1 is fresh, alive, and `routable`; and
- Ollama responds to `ollama list`.

The only source correction replaces `Get-FileHash` with
`System.Security.Cryptography.SHA256` over an explicitly opened read stream.
It changes no expected digest, input byte, scientific field, model call,
machine policy, package, driver, service, or scheduler setting.

Q3 uses fresh remote and local custody roots ending in `-r2-q3`. The failed q1
and q2 qualification roots remain unchanged. Q3 permits one new
qualification/training lease and one contingent evaluation lease. Creation of
`training-started.json` still consumes the one r2 training attempt.

## Status history

- `2026-07-21` — `authorized-pending-host` — the ADR 0026 delegate authorized
  the module-independent digest correction, contingent on the externally
  changing NVIDIA/Ollama host state returning to its frozen preconditions.
- `2026-07-21` — `invalidated-pre-effect` — the driver installation rebooted
  the host at `2026-07-21T04:16:37.5000000Z`, so q3's boot precondition failed
  before staging or lease acquisition. ADR 0057 governs the rebound host and
  shared-GPU capacity boundary.
