---
id: adr-0059
artifact_type: architecture-decision-record
title: Dispose the Qwen3.6-27B retry and conclude CAPLAB-16
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

# Dispose the Qwen3.6-27B retry and conclude CAPLAB-16

## Observation

ADR 0058's q5 execution acquired outer physical-GPU lease
`180c8398-0bf7-45c4-bff7-3e9959519e8a` and inner controller lease
`fbde31f0-968f-43f3-9e25-879be010ed5b`. The no-update qualification completed
six iterations in 63.563 seconds. Its adapter digest was unchanged, loss was
`0.722461760044`, and thirteen distinct fleet heartbeats exceeded the required
floor.

Training then passed its separate preflight and created the attempt-start
marker. It completed three of twelve optimizer steps and wrote checkpoint 3.
The outer lease renewal later returned false while `nvidia-smi`, Ollama, the GPU
workload, and the inner heartbeat remained responsive. The outer runner stopped
its nested local process group. Loss of the remote pulse caused the Windows Job
Object to terminate the training tree at `2026-07-21T04:44:43.460620Z`.

No final adapter or training result exists. The partial checkpoint contains a
233,605,480-byte adapter, optimizer state, and trainer state at global step 3.
Those bytes are interrupted state, not a model candidate. The complete q5
custody inventory is
[`training-custody-q5.json`](../product/training/caplab-review-dissent-local-qwen-r2/training-custody-q5.json),
SHA-256 `6a273db2c6841fc1b164b17b7a9a6d0c7a245430929a4beea69af87c4fd48463`.

## Disposition

Classify r2 as `training-infrastructure-outer-lease-lost-gpu-responsive` and
the attempt as `infrastructure-failed-training-attempt-consumed`. Do not
resume, evaluate, deploy, or describe checkpoint 3 as tuned. The held-out
families remain sealed and unopened; native harness, general-control, and
held-out call counts are all zero.

The committed machine result is
[`training-result.json`](../product/training/caplab-review-dissent-local-qwen-r2/training-result.json),
SHA-256 `8f8fe943f3bc63ce5b5d24da40111b5f8d350bee0d7e6be1941f1389150cb7e8`.
Its conclusion is `not-evaluable-no-final-adapter`, not a capability failure or
success.

Conclude CAPLAB-16 as a completed bounded experiment with a terminal
infrastructure-failure result. Its requested held-out comparison could not run
because the prerequisite final adapter did not exist. Closing the execution
ticket does not cancel future model research, but this experiment creates no
implicit retry authority and no open CAPLAB work item. A future attempt needs a
new preregistration and evidence that the physical-GPU exclusion lease can
survive representative sustained load.

## Status history

- `2026-07-21` — `decided` — the ADR 0026 delegate preserved the interrupted
  checkpoint as an unsealed non-candidate, prohibited held-out evaluation, and
  concluded CAPLAB-16 with the terminal unsuccessful result.
