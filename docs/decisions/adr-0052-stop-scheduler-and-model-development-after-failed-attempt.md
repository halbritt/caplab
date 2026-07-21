---
id: adr-0052
artifact_type: architecture-decision-record
title: Stop scheduler and model development after the failed first attempt
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-21
decided_at: 2026-07-21
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - striatum-lane-fit-advice
  - governed-model-training
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Stop scheduler and model development after the failed first attempt

## Decision owner, scope, and selected option

The ADR 0026 delegate selects **stop** for the current CAPLAB v0 scheduler and
model-development branch. Do not pilot a scheduler-policy change, deploy a
checkpoint, revise Striatum routing, expand the training sample, authorize
another model call, or continue the failed QLoRA attempt.

This decision covers only the evidence reviewed here. It does not reject local
models, tuning, review passes, or future CAPLAB experiments generally.

## Evidence considered

The CAPLAB-first Striatum lane-fit report found no observed subject tuple that
met either accepted build or review pass profile. Its qualifying and Pareto
sets were empty, so it recommended no routing or placement change.

ADR 0051 and the CAPLAB-16 result record show that the preregistered Qwen3.6-27B
attempt passed its model/data/toolchain preflight but suffered a GPU
infrastructure failure after observed optimizer step 3 of 12. The sole attempt
was consumed, the partial adapter is not a candidate, and no held-out or general
control evaluation occurred. The held-out tuning result is therefore
`not-evaluable-no-final-adapter`, not a missing success that may be imputed.

## Alternatives and rationale

| Option | Disposition | Rationale |
|---|---|---|
| Pilot a scoped scheduler-policy change | Rejected | No tuple met a profile, and no tuned checkpoint exists. |
| Gather more model evidence now | Rejected for this branch | Additional calls cannot repair a consumed training attempt or a wedged shared GPU. |
| Revise or scale the training intervention | Rejected | Scaling sample or compute would not address the observed GPU-observability and lease-loss failure. |
| Stop | Selected | It preserves the failed observation, changes no production behavior, and keeps future work contingent on new evidence rather than momentum. |

Stopping has the narrowest consequence consistent with the evidence. The
fallback is current Striatum scheduler and backend policy unchanged.

## Residual uncertainty and reopening

The experiment supplies no estimate of tuned held-out behavior, general coding
regression, inference latency, or serving cost. It also does not establish
whether a complete QLoRA run would improve, degrade, or leave unchanged the
named review capability.

Reopen model development only when all of the following exist:

1. `peecee` or another exact batch host is restored under authority outside
   CAPLAB and can sustain `nvidia-smi`/fleet observability during a representative
   heavy CUDA load;
2. a new preregistration names the evidence-calibrated review gap and explains
   what new evidence, rather than merely more sample or compute, should change
   the decision;
3. a new one-attempt authorization records host recovery, remote-process
   containment, lease behavior, and cleanup; and
4. the immutable held-out families remain unopened and eligible.

Reopen scheduler-policy work only after a candidate tuple meets an accepted pass
profile with complete evidence and a separate Striatum owner authorizes a pilot.

## Explicit non-authorization

This decision authorizes no production routing, checkpoint deployment,
scheduler-policy pilot, model call, training attempt, held-out access, host
reboot, driver reset, Striatum mutation, verification, or acceptance.

## Status history

- `2026-07-21` — `decided` — the ADR 0026 delegate selected stop after the empty
  lane-fit set and infrastructure-failed tuning attempt, leaving current
  Striatum behavior unchanged.
