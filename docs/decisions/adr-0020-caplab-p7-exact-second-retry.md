---
id: adr-0020
artifact_type: architecture-decision-record
title: CAPLAB P7 exact second live retry
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
  - caplab-p7-live-retry-attempt-2026-07-19
---

# CAPLAB P7 exact second live retry

The repository owner approved the exact second P7 live retry on 2026-07-19.
This decision authorizes one execution of the ordered continuation and mandatory
cleanup named by the selected proposal. It does not record execution,
verification, capability inference, training eligibility, export, independent
verification, or CAPLAB acceptance.

## Decision context and owner instruction

ADR 0018's retry stopped before recomputation because an added shell assertion
treated PostgreSQL's unusable `*` password marker as a live authority failure.
Aggregate disablement completed and every preservation comparison passed. The
stopped retry and versioned readiness repair are recorded in
[`caplab-p7-live-retry-attempt-2026-07-19`](../records/caplab-p7-live-retry-attempt-2026-07-19.md).

The exact replacement proposal is
[`caplab-p7-live-retry-2-proposal-2026-07-19`](../records/caplab-p7-live-retry-2-proposal-2026-07-19.md).
After the proposal was supplied through the repository owner's requested
private paste and the queue was reported blocked on its exact approval, the
repository owner replied:

> authorization granted

In that immediate context, `authorization granted` selects the linked exact
second-retry proposal unchanged. It grants no authority for later human-owned
or independently verified checkpoints.

## Decision and authorization

**Decision:** approve the exact second-retry proposal unchanged.

**Owner and authority:** repository owner under repository ownership and the
direct instruction quoted above.

**Authorized executor:** the primary agent on host `proximal` may execute the
proposal once through `2026-07-25T23:59:59Z`.

The authorized effects are limited to the proposal's ordered continuation:

1. verify the stopped-retry manifest and disabled state;
2. atomically preserve the stopped retry and disabled state under
   `/var/tmp/caplab-p7-stopped-retry-2026-07-19`, without changing the first
   stopped-attempt archive;
3. require both archives and every pre-effect preservation control to verify;
4. install only the controller from clean, pushed Proximal commit
   `031d20cceefa1f7f4bf5db9386d89383d763edf0`, SHA-256
   `8f5b2378a772f1c5c1fd28031e0c9ac9a96b84f90c0270d2c48d85ce3be7d076`;
5. recreate `/var/tmp/caplab-p7-execution-2026-07-18` as the fresh root-owned
   evidence root and capture fresh pre-effect controls;
6. enable only `caplab_reader`, require the versioned controller's ready
   verification, and add no unversioned readiness assertion;
7. run the frozen model-free recomputation exactly twice and require
   byte-identical canonical observations;
8. require the product observation to bind the frozen P6 admission, frozen
   implementation commit, exact 20 outcomes, byte-identical historical result,
   and a self-consistent manifest identity; and
9. aggregate-revoke access, verify the disabled phase, require every pre/post
   preservation comparison, and seal the fresh evidence manifest.

The frozen CAPLAB source remains
`04ed8213ec7741d76d8bb9f9b6f972ebb4deaf3e`; the P6 admission remains
`d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`.
All other identities, paths, modes, hashes, timer deadline, preservation
controls, and stop conditions are exactly those in the selected proposal.

## Verification and exclusions

CAPLAB-25 may close only after both recomputations satisfy the frozen result
contract, their canonical bytes match, aggregate disablement passes, every
pre/post control matches, and the fresh evidence manifest verifies. These
executor checks are not CAPLAB-33 independent verification or CAPLAB-34
acceptance.

This decision excludes capability inference, semantic adjudication,
training-candidate eligibility, export, model/provider calls, training,
publication, Striatum placement, preference work, deletion of stopped
evidence, another retry, independent verification, and CAPLAB acceptance.

## Reopening conditions

Stop and reopen if a bound commit, hash, identity, path, timer, expiry, access
boundary, registered byte, result, replay, or preservation control differs.
Another stopped execution requires another owner decision.

## Status history

- `2026-07-19` — `decided` — the repository owner replied `authorization
  granted` after receiving the exact second-retry proposal; one execution is
  authorized unchanged.
