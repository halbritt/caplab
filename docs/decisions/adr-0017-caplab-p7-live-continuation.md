---
id: adr-0017
artifact_type: architecture-decision-record
title: CAPLAB P7 live recomputation continuation
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership-and-direct-instruction
created: 2026-07-18
decided_at: 2026-07-18
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-study-001
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# CAPLAB P7 live recomputation continuation

Status interpretation: the repository owner approved the exact P7 live
continuation on 2026-07-18. This decision authorizes one temporary read-only
execution of the frozen CAPLAB-25/P7 recomputation and its mandatory cleanup.
It records no capability inference, eligibility decision, export authorization,
independent verdict, or CAPLAB acceptance.

## Decision context and owner instruction

The exact proposal is
[`caplab-p7-live-continuation-proposal-2026-07-18`](../records/caplab-p7-live-continuation-proposal-2026-07-18.md).
It binds the CAPLAB and Proximal commits, installed-file hashes, P6 admission
identity, temporary reader authority, evidence root, expiry, ordered execution,
preservation controls, cleanup, and excluded effects.

After receiving that proposal and a fresh report that CAPLAB-25 was the only
executable dependency front, the repository owner gave this direct instruction
in the active CAPLAB backlog-drain context:

> approve the exact P7 live continuation

The phrase `exact P7 live continuation` identifies the linked proposal without
revision. The owner supplied approval, not a recommendation or a delegation of
later human-owned judgments.

## Decision and authorization

**Decision:** approve the exact proposal unchanged.

**Owner and authority:** repository owner under repository ownership and the
direct instruction quoted above.

**Authorized executor:** the primary agent on host `proximal` may execute the
proposal's ordered runbook once through `2026-07-25T23:59:59Z`.

The authorized live effects are limited to:

1. install CAPLAB source
   `04ed8213ec7741d76d8bb9f9b6f972ebb4deaf3e` in its fixed P7 environment;
2. install and enact pushed Proximal desired state
   `79f04a537538012824bb948cc863a10d0219d82a`;
3. enable only `caplab_reader` with one expiring read-only Garage key for
   bucket `caplab-v0` and read-only PostgreSQL access;
4. recompute P6 admission manifest
   `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`
   exactly twice and require byte-identical canonical observations;
5. retain execution evidence only under
   `/var/tmp/caplab-p7-execution-2026-07-18`; and
6. revoke the key, credential, login, sessions, processes, and account window,
   then verify the disabled state and all preservation controls.

The controller, configuration, source marker, service, timer, requirements
lock, installed paths, file hashes, owner and mode requirements, command line,
timer deadline, evidence-manifest rule, and stop conditions are exactly those
in the proposal and Proximal commit. This decision authorizes no substitute
commit, namespace, identity, bucket, evidence root, expiry, or recovery action.

## Preservation and stop conditions

Preserve the live PostgreSQL cluster start identity, P4 control, P6
registration and timestamps, all Garage object and version identities, all
independent-copy identities, source-study custody, and disabled writer and
verifier access. Record pre-effect and post-cleanup observations separately.

Stop and aggregate-revoke on repository, commit, installation, clock, timer,
role, privilege, credential, session, registration, locator, byte,
cardinality, analysis, canonical-output, replay, or preservation drift. A stop
does not authorize repair, historical rewriting, a changed runbook, or a
second execution.

## Verification and authority exclusions

The executor may record execution and cleanup observations. Technical checks
of those effects do not constitute CAPLAB-33 independent verification or
CAPLAB-34 acceptance. CAPLAB-25 may close only after the two outputs are
byte-identical, the registered historical result matches, all cleanup checks
pass, and the retained evidence manifest verifies.

This authorization excludes capability inference, semantic adjudication,
training-candidate eligibility, export, model or provider calls, training,
publication, Striatum placement, preference work, independent verification,
and CAPLAB acceptance. CAPLAB-27/P9, CAPLAB-29/P11, CAPLAB-30/P12,
CAPLAB-33/P13, and CAPLAB-34/P14 retain their own gates.

## Doctrine provenance

The approved proposal used final doctrine packet `pkt-c3a7efc417d731c6`,
content SHA-256
`c3a7efc417d731c6224fef79be330ab5b99922d73aaab4c07e8090735e21f093`.
Its authority ceiling is execution without self-acceptance. This record adds no
new implementation recommendation; it records the owner's exact selection of
the already-evidenced continuation.

## Reopening conditions

Reopen before effects if any bound commit, file hash, P6 identity, role,
namespace, evidence root, timer, expiry, or preservation control differs.
Reopen after a stopped execution only through a new owner decision that cites
the retained evidence and states whether another attempt is permitted.

## Status history

- `2026-07-18` — `decided` — the repository owner instructed the agent to
  `approve the exact P7 live continuation`; the exact proposal is authorized
  without revision.
