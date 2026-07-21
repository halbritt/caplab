---
id: adr-0053
artifact_type: architecture-decision-record
title: Preregister a fresh Qwen3.6-27B attempt after the host outage
status: preregistered
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

# Preregister a fresh Qwen3.6-27B attempt after the host outage

## Corrected incident boundary

The r1 observation remains valid: after optimizer step 3, `nvidia-smi` stopped
answering, the fleet de-listed `peecee`, the lease was lost, and only an
unsealed partial checkpoint existed. The earlier record conservatively called
this a GPU-unresponsive infrastructure failure because that was all CAPLAB
could observe at the time.

The repository owner has now identified the missing fact: the host was down.
Windows reports an unexpected prior shutdown and a new boot at
`2026-07-21T03:19:59.5000000Z` through Kernel-Power event 41 and EventLog events
6008/6005. Current inspection finds no surviving Python trainer. This supports
classifying the execution boundary as **host availability loss**. It does not
establish whether power loss, an operating-system crash, or another external
action caused the shutdown.

### Hypothesis ledger

| Rival | Current disposition | Discriminating evidence |
|---|---|---|
| Heavy CUDA load wedged only the NVIDIA driver | Weakened, not excluded | The entire host became unreachable and later booted after an unexpected shutdown; no driver-only trace was preserved. |
| The host lost power or crashed | Supported at the boundary | SSH, ICMP, and Tailscale traffic failed; Windows records an unexpected shutdown and later boot. The specific cause remains unknown. |
| Only the local SSH transport failed | Rejected | Independent fleet probes and all host reachability failed, not just the CAPLAB session. |
| The training method itself failed | Not supported | The exact no-update preflight passed and the loss occurred outside a recorded model/trainer exception. |

## Decision

Preregister `caplab-review-dissent-qwen27b-qlora-r2` as one fresh attempt. It
uses the identical immutable checkpoint, corpus bytes, three training rows,
QLoRA method, seed, 12 optimizer steps, held-out cells, general controls,
native `striatum-openai-lane` harness, success rule, and claim ceiling as r1.
It does not resume the partial checkpoint, add examples, increase compute, or
reinterpret the failed attempt.

The evidence-calibrated gap is unchanged because r1 produced no model result:
CAPLAB still lacks a base-versus-tuned estimate for evidence-grounded review
dissent and clean-case false-refusal on `RD-H01`/`RD-H02`. A complete r2 run
would supply that missing evidence; merely repeating loss curves would not.

The executable zero-authority contract is
[`training-experiment.json`](../product/training/caplab-review-dissent-local-qwen-r2/training-experiment.json),
SHA-256 `4f8d4f0792cbb56aeee3c00e0de3c43fe4efc7f13c2316860801ffd547febfe0`.

## New host-qualification and containment contract

Before `training-started.json` may be written, the exact host must complete a
60-second repeated forward/backward qualification with zero optimizer steps
and identical adapter hashes before and after. An external controller must
observe at least four distinct live, routable fleet heartbeats under the same
lease and a constant Windows boot identity.

Each remote phase runs inside a Windows Job Object configured
`KILL_ON_JOB_CLOSE`. The independently running local lease controller advances
a lease-bound pulse every five seconds. The remote supervisor terminates the
entire job tree after 45 seconds without an advancing matching pulse. Thus:

- loss of the local controller or supervisor handle kills the remote tree;
- lease loss kills the local controller, stops pulses, and causes remote tree
  termination even if Windows OpenSSH does not propagate disconnects; and
- host shutdown terminates all processes, while a changed boot identity blocks
  continuation after recovery.

Qualification failure consumes no training attempt. Any failure after the r2
training-start marker consumes the one fresh attempt. Neither phase may read
held-out content.

## Alternatives

| Option | Disposition | Reason |
|---|---|---|
| Leave CAPLAB-16 blocked | Rejected now | The external host condition changed and the owner directed another attempt. |
| Resume r1 step 3 | Rejected | The partial checkpoint is unsealed, lacks complete trainer state, and r1 forbids resume. |
| Replay the r1 orchestration unchanged | Rejected | It did not contain a remote child after local lease loss. |
| Increase data or compute | Rejected | That does not address host availability or missing process containment. |
| Fresh r2 with qualification and containment | Selected | It preserves the scientific comparison while addressing the observed operational boundary. |

## Advisory doctrine and remaining uncertainty

Pincite packet `pkt-0b02b88df5e400b7`, packet-file SHA-256
`c614075713e092490d6f600eeb3954244653119a7d65a56dd48f81c0d0a5720b`, and
content SHA-256
`0b02b88df5e400b7188fa71a13197d50c99906de44f4a398117b9c26ab17ec00`
activated external liveness observation, explicit failure policy, structured
cleanup, hypothesis-led diagnosis, bounded authority, and reversible change.
Corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-e015b9ff0e827001`, retriever `retriever-1de4a84ff83c8c07`, release
commit `1ce4fc6d0df3eb291f1db92b5907776ae9c89be9`.

Material packet obligations are discharged by ADR 0026 authority, the r1
incident and machine result, current Windows/fleet observations, the hypothesis
ledger above, the executable qualification/containment contracts, and their
tests. Generic business-metric, benchmark-overhead, formatter, and broad
repository-architecture obligations are nonmaterial because this decision
authorizes one private bounded experiment and makes no availability,
performance, or repository-wide design claim.

The exact host-shutdown cause remains unknown. Qualification can show that the
recovered host and fleet remain observable under a representative load; it
cannot prove the host will not lose power again.

## Authorization boundary

This preregistration grants zero host qualification, training, held-out access,
evaluation call, deployment, Striatum mutation, or scheduler-policy authority.
A separate exact authorization is required before any effect.

## Status history

- `2026-07-21` — `preregistered` — the ADR 0026 delegate selected one fresh,
  scientifically unchanged attempt with a new host-qualification and remote
  containment boundary.
