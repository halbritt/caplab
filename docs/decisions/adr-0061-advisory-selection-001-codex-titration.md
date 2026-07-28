---
id: adr-0061
artifact_type: architecture-decision-record
title: Advisory-selection-001 capability titration on Codex CLI
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026-and-direct-repository-owner-execution-delegation
created: 2026-07-28
decided_at: 2026-07-28
expires_at: 2026-08-11T23:59:59Z
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-advisory-selection-001
related_specs:
  - spec-agent-capability-lab
related_plans:
  - Plane CAPLAB-44
---

# Advisory-selection-001 capability titration on Codex CLI

## Why a titration, and why across scenarios

The owner ran a capability titration with correct doctrine statically injected
and no retrieval, finding no behavioural difference for highly capable
model/effort tuples and a difference below some point. That was **one
scenario**. The owner directed that it be run against a set.

The shakedown supports this directly: re-scored with corrected predicates, the
effect **changes sign** across three scenarios — saturated on SC-01, positive
on SC-02, negative on SC-03. No single-scenario experiment can observe that.

## Subject: Codex CLI, and why it beats the CAPLAB-63 recommendation here

CAPLAB-63 recommended Claude Code on tool-call legibility, because Codex
collapses reads and verifications into compound `command_execution` strings.
That objection is driven by **transcript-shaped** codes; this titration's codes
are **artifact-shaped** (diff and write-set), so it barely applies.

What does apply is attestation. Codex's non-ephemeral rollout carries
per-turn `model` and `reasoning_effort` (`turn_context`) — per-episode
attestation of exactly the two variables being titrated, which Claude Code does
not provide. CAPLAB-79 predicted this; a rollout had never been captured.
`--ephemeral` is therefore prohibited under this authorization.

Codex CLI is a native harness; this is not proxy substitution under ADR-0039.
The Claude seven-day quota is separately exhausted (see below), which is a
reason to prefer Codex now but not the reason it is the right subject.

## Exact target

Three shakedown scenarios, already consumed and permanently excluded from any
study population. Two arms: `injection` and `none` — a titration measures the
ceiling, and retrieval cannot exceed it.

Ladder: `gpt-5.6-{luna,terra,sol}` × `{low,medium,high,xhigh}` = **12 rungs**
(`minimal` rejected by the CLI). k = 3 per cell. Ladder resolution is preferred
over per-cell precision because the object is to locate a frontier, not to
estimate a single contrast.

3 scenarios × 12 rungs × 2 arms × 3 = **216 primary episodes**.

## Ceilings

| ceiling | value |
|---|---|
| Primary episodes | 216 |
| Hard stop | **240** |
| Wall-clock | 6 hours |
| Lanes | 5 |
| Infrastructure halt | stop when ≥8 completed and ≥75% are infrastructure |

## Preservation boundary

No writes to `halbritt/pincite`. Retrieval runs trace-disabled; no entry in the
ADR 0019 served-doctrine record. No registered evidence modified. Scenario
worlds are per-episode copies; no shared service, database, or port is touched.

## Verification

Per-episode attestation from the rollout (`attested_model`, `attested_effort`,
`pin_ok`). Disposition recorded as `infrastructure` /`behavioural-attempt` /
`behavioural-no-attempt`, with `attempted: null` when infrastructure.

## Stop conditions

Episode or wall-clock ceiling; sustained infrastructure failure; `pin_ok`
false on any episode; any write outside the preservation boundary.

## Prior-campaign defects this authorization exists to not repeat

1. **Quota exhaustion recorded as behaviour.** The Claude titration burned the
   seven-day limit; 129 episodes were rejected and the runner recorded them as
   `attempted: false` — indistinguishable from an agent declining to act, and
   in a capability titration that fabricates a false positive pointing at the
   hypothesis. The runner now classifies disposition from the stream and the
   driver halts on sustained rejection.
2. **Predicates that fire on the parent tree.** Three of seven mechanical
   predicates were satisfied by the untouched world, flooring SC-03 at 0.67 and
   inflating SC-02. Reported arm means were artifacts. The coder now refuses to
   run unless every predicate is false on the parent tree.

## Status history

- `2026-07-28` — `authorized` — recorded by the ADR 0026 delegate under the
  owner's execution delegation. Authorization is not execution, verification,
  inference, or acceptance.
