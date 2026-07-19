---
id: adr-0021
artifact_type: architecture-decision-record
title: CAPLAB P7 exact third live retry
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
  - caplab-p7-live-second-retry-attempt-2026-07-19
  - caplab-p7-json-decimal-repair-2026-07-19
---

# CAPLAB P7 exact third live retry

The repository owner approved the exact third P7 live retry on 2026-07-19.
This decision authorizes one execution of the ordered continuation and mandatory
cleanup named by the selected proposal. It does not record execution,
verification, capability inference, training eligibility, export, independent
verification, or CAPLAB acceptance.

## Decision context and owner instruction

ADR 0020's retry reached the first recomputation and stopped because default
JSON decoding converted a decimal token into a Python float that CAPLAB's
identity-safe canonicalizer correctly refused. Aggregate disablement completed
and every preservation comparison passed. The stopped execution and causal
repair are recorded in
[`caplab-p7-live-second-retry-attempt-2026-07-19`](../records/caplab-p7-live-second-retry-attempt-2026-07-19.md)
and
[`caplab-p7-json-decimal-repair-2026-07-19`](../records/caplab-p7-json-decimal-repair-2026-07-19.md).

The exact replacement proposal is
[`caplab-p7-live-retry-3-proposal-2026-07-19`](../records/caplab-p7-live-retry-3-proposal-2026-07-19.md).
After asking whether the defect had been repaired and receiving confirmation
that the red-green regression and complete gate passed, the repository owner
stated:

> If yes, then I approve the retry

The condition is satisfied by clean, pushed CAPLAB commit
`bf6de2b24ac61e82107208cdc609c7e534c6eaaa` and the 105-test repository gate.
In the immediate context, `the retry` identifies the linked exact third-retry
proposal unchanged. It grants no authority for later human-owned or
independently verified checkpoints.

## Decision and authorization

**Decision:** approve the exact third-retry proposal unchanged.

**Owner and authority:** repository owner under repository ownership and the
direct instruction quoted above.

**Authorized executor:** the primary agent on host `proximal` may execute the
proposal once through `2026-07-25T23:59:59Z`.

The authorized effects are limited to the proposal's ordered continuation:

1. verify the current evidence manifest, disabled state, and both earlier
   stopped-attempt archives;
2. atomically preserve the current evidence and disabled state under
   `/var/tmp/caplab-p7-stopped-second-retry-2026-07-19`, without changing the
   earlier archives;
3. require all three archives and every pre-effect preservation control to
   verify;
4. install clean, pushed CAPLAB commit
   `bf6de2b24ac61e82107208cdc609c7e534c6eaaa` in its distinct fixed runtime,
   retaining the earlier runtime;
5. install and enact clean, pushed Proximal desired state
   `c5bb1efa1402010a57ccc7034f3555b14830bc1c`;
6. recreate `/var/tmp/caplab-p7-execution-2026-07-18` as the fresh root-owned
   evidence root and capture fresh pre-effect controls;
7. enable only `caplab_reader` and require the versioned controller's ready
   verification;
8. run the repaired model-free recomputation exactly twice and require
   byte-identical canonical observations;
9. require the product observation to bind the frozen P6 admission, repaired
   implementation commit, exact 20 outcomes, byte-identical historical result,
   and a self-consistent manifest identity; and
10. aggregate-revoke access, verify the disabled phase, require every pre/post
    preservation comparison, and seal the fresh evidence manifest.

The P6 admission remains
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
publication, Striatum placement, preference work, deletion of stopped evidence
or earlier runtimes, another retry, independent verification, and CAPLAB
acceptance.

## Reopening conditions

Stop and reopen if a bound commit, hash, identity, path, timer, expiry, access
boundary, registered byte, result, replay, or preservation control differs.
Another stopped execution requires another owner decision.

## Status history

- `2026-07-19` — `decided` — after confirmation that the repair and complete
  gate pass, the repository owner stated `If yes, then I approve the retry`;
  one execution of the exact third-retry proposal is authorized unchanged.
