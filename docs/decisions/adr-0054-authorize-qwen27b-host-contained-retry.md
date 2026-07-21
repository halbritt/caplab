---
id: adr-0054
artifact_type: architecture-decision-record
title: Authorize one host-contained Qwen3.6-27B retry
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

# Authorize one host-contained Qwen3.6-27B retry

## Preconditions

ADR 0053 separately preregisters r2 with zero execution authority. The r1
attempt and partial checkpoint remain consumed and unusable. The held-out
families remain sealed and unopened.

At `2026-07-21T03:22:43Z`, `peecee` accepted non-interactive SSH and
`nvidia-smi` reported one RTX 3090 Ti with 24,564 MiB total, 21,548 MiB free,
2 percent utilization, and driver `610.62`. GPU-fleet independently reported
both `peecee` slots live and routable. Windows boot identity is
`2026-07-21T03:19:59.5000000Z`; a different identity is a stop.

## Decision and exact effects

Authorize the exact effects in
[`training-execution.json`](../product/training/caplab-review-dissent-local-qwen-r2/training-execution.json),
file SHA-256 `0c095d5c58732678c151ad31b6874736a5f559d79d70d30894175b77d4f31d3c`,
until `2026-07-22T12:00:00Z`:

1. acquire one exclusive `gpu-fleet` lease for `peecee` marker slot 1 for
   qualification and training;
2. reuse, without modifying, the exact r1 isolated environment and immutable
   checkpoint cache;
3. temporarily unload only the resident `qwen3.6:27b` Ollama model;
4. run one 60-second, zero-optimizer-step heavy qualification inside the
   lease-pulse and Windows Job Object containment boundary;
5. require at least four distinct live/routable fleet heartbeats, unchanged
   adapter bytes, and unchanged host boot identity before training;
6. run one fresh 12-step r2 QLoRA attempt under the same containment boundary;
7. only after a sealed step-12 adapter exists, acquire a second exclusive lease
   for the transient evaluation server, then open and run the frozen eight
   held-out cells and four general controls once per base/tuned subject through
   native `striatum-openai-lane` v1, subject to the two infrastructure-only
   replacement ceiling; and
8. stop the transient evaluation server, release each lease at its phase
   boundary, verify Ollama and GPU availability, and preserve complete custody.

No package installation or checkpoint download is authorized. Their absence or
drift stops rather than repairing the host in place. Maximum paid cost is USD 0.

## Failure and cleanup policy

The remote supervisor must create a fresh Job Object and successfully assign
the phase process before model loading. Failure to configure kernel
`KILL_ON_JOB_CLOSE` containment stops the phase. A missing, invalid, regressed,
or stale lease pulse terminates the entire remote process tree. The local
controller fails closed on any sample that is not the exact alive, routable,
leased `peecee` slot 1.

Qualification failure does not consume the training attempt. Creation of the
r2 `training-started.json` marker consumes it. After that marker there is no
retry, resume, host substitution, hyperparameter change, partial-checkpoint
selection, or held-out access without a new disposition.

If the host becomes unreachable, preserve local observations immediately and
recover remote identity/outcome custody after the host returns. Do not reboot,
reset a driver, alter GPU-fleet, or interfere with another host workload under
this authorization.

## Boundaries

This authorization does not deploy a checkpoint, modify Striatum, change
scheduler policy, stop the Ollama service, install software, download a model,
use a proxy harness, publish artifacts, or make a broad capability claim.
Execution, technical verification, CAPLAB-17 disposition, and any acceptance
remain distinct.

## Status history

- `2026-07-21` — `authorized` — the ADR 0026 delegate authorized one exact
  qualification-gated, host-contained r2 attempt and its contingent native
  held-out evaluation.
