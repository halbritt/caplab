---
id: caplab-review-dissent-local-qwen-r2
artifact_type: training-experiment-card
title: CAPLAB Qwen3.6-27B review-dissent QLoRA r2
status: concluded-infrastructure-failure
created: 2026-07-21
decision_record: adr-0053
execution_authorization: adr-0058
---

# CAPLAB Qwen3.6-27B review-dissent QLoRA r2

R2 is one fresh attempt after r1 ended during a `peecee` host outage. It does
not resume or reinterpret r1. The base checkpoint, source corpus, method, seed,
optimizer-step ceiling, held-out design, native harness, success rule, and
claim ceiling are identical to r1.

The changed treatment is operational only: a no-update heavy qualification,
external fleet-heartbeat gate, constant boot identity, lease pulse, and Windows
Job Object process-tree containment must pass before training begins.

- [`training-experiment.json`](training-experiment.json) is the zero-authority
  scientific and host-qualification preregistration.
- [`training-execution.json`](training-execution.json) is the consumed first
  launch authorization. Windows refused its PowerShell file before model
  loading.
- [`training-execution-q2.json`](training-execution-q2.json) is the corrected
  execution-policy launch authorization. The contained child lacked the
  `Get-FileHash` cmdlet and stopped before model loading.
- [`training-execution-q3.json`](training-execution-q3.json) is the
  module-independent digest authorization invalidated before effect by the
  driver-install reboot.
- [`training-execution-q4.json`](training-execution-q4.json) is the consumed
  rebound-host authorization. Its controller rejected gpu-fleet's designed
  lease-time `probationary` status before qualification completed.
- [`training-execution-q5.json`](training-execution-q5.json) is the consumed
  lease-aware authorization. Qualification passed, but the outer lease was lost
  after optimizer step 3 while the GPU remained responsive.
- [`training-result.json`](training-result.json) records the terminal unsuccessful
  experiment result. [`training-custody-q5.json`](training-custody-q5.json)
  inventories the preserved raw custody; checkpoint 3 is unsealed and is not a
  candidate.
- The immutable corpus and controls remain under
  [`../caplab-review-dissent-local-qwen-r1`](../caplab-review-dissent-local-qwen-r1/README.md).

No result exists until execution and custody are recorded. A successful
technical run is not deployment, lane-fit acceptance, or a general model claim.
