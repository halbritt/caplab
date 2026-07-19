---
id: adr-0018
artifact_type: architecture-decision-record
title: CAPLAB P7 exact live retry
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership-and-direct-instruction
created: 2026-07-19
decided_at: 2026-07-19
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-study-001
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts:
  - caplab-p7-live-attempt-2026-07-18
---

# CAPLAB P7 exact live retry

The repository owner approved the exact P7 live retry on 2026-07-19. This
decision authorizes one retry of CAPLAB-25/P7 under the unchanged expiry and
the replacement controller identified by the selected proposal. It does not
record execution, verification, a capability inference, eligibility, export,
independent verification, or CAPLAB acceptance.

## Decision context and owner instruction

ADR 0017's execution stopped before recomputation because the bound controller
rejected Garage 2.3 bucket identity metadata. Aggregate disablement passed and
the preserved controls remained unchanged. The stopped execution is recorded
in
[`caplab-p7-live-attempt-2026-07-18`](../records/caplab-p7-live-attempt-2026-07-18.md).

The exact replacement proposal is
[`caplab-p7-live-retry-proposal-2026-07-18`](../records/caplab-p7-live-retry-proposal-2026-07-18.md).
After receiving the proposal and the current status that execution was gated
on its approval, the repository owner replied:

> approved

In that immediate context, `approved` selects the linked exact retry proposal
without revision. It does not approve any later human-owned decision.

## Decision and authorization

**Decision:** approve the exact retry proposal unchanged.

**Owner and authority:** repository owner under repository ownership and the
direct instruction quoted above.

**Authorized executor:** the primary agent on host `proximal` may execute the
proposal once through `2026-07-25T23:59:59Z`.

The authorized effects are limited to:

1. atomically preserve the verified stopped-attempt evidence and disabled
   state under `/var/tmp/caplab-p7-failed-attempts-2026-07-18`;
2. install the corrected controller from pushed Proximal commit
   `8c45e62a22cf5c7e566df2d4510b49742f39b6ac`, SHA-256
   `7497d3cf12fd6b6d91dbb0e14cd8fe852fd162f055d7974377871338e3c79607`;
3. recreate `/var/tmp/caplab-p7-execution-2026-07-18` as a fresh root-owned
   evidence root;
4. enable only `caplab_reader` with one expiring read-only Garage key and
   read-only PostgreSQL access;
5. recompute P6 admission manifest
   `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`
   exactly twice and require byte-identical canonical observations; and
6. revoke the key, credential, login, sessions, processes, and account window,
   then verify the disabled state and all preservation controls.

The CAPLAB source remains
`04ed8213ec7741d76d8bb9f9b6f972ebb4deaf3e`. All other identities, hashes,
paths, modes, timer deadline, preservation controls, and stop conditions are
exactly those in the selected proposal.

## Verification and exclusions

CAPLAB-25 may close only after both recomputations pass the frozen result
contract, their canonical bytes match, aggregate disablement passes, the
pre/post controls match, and the fresh evidence manifest verifies. These
executor checks are not CAPLAB-33 independent verification or CAPLAB-34
acceptance.

This decision excludes capability inference, semantic adjudication,
training-candidate eligibility, export, model/provider calls, training,
publication, Striatum placement, preference work, deletion of stopped-attempt
evidence, another retry, independent verification, and CAPLAB acceptance.

## Reopening conditions

Stop and reopen if a bound commit, hash, identity, path, timer, expiry, access
boundary, registered byte, result, replay, or preservation control differs.
Another stopped execution requires another owner decision.

## Status history

- `2026-07-19` — `decided` — the repository owner replied `approved` to the
  exact P7 live retry proposal; one retry is authorized without revision.

