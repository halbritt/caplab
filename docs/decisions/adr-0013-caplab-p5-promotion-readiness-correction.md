---
id: adr-0013
artifact_type: architecture-decision-record
title: CAPLAB P5 PostgreSQL promotion-readiness correction
status: decided
decision_owner: caplab-execution-delegate
decision_authority: direct-repository-owner-delegation
created: 2026-07-17
decided_at: 2026-07-17
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-custody
  - proximal-backup
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts:
  - caplab-p5-recovery-compatibility-execution-2026-07-17
  - caplab-p5-recovery-compatibility-verification-2026-07-17
---

# CAPLAB P5 PostgreSQL promotion-readiness correction

Status interpretation: after receiving ADR 0012's independent FAIL,
live-cluster PASS, and the recommendation to wait explicitly for promotion
completion before the final identity gate, the repository owner instructed
the primary agent: `I delegate my decision authority to you, proceed`.

The `caplab-execution-delegate` selects and authorizes campaign
`caplab-p5-promotion-readiness-corrective-2026-07-17` through
`2026-07-24T23:59:59Z`. This authorization covers only the bounded readiness
wait, one clean retry of the fixed backup, restored-database verification,
independent verification, guarded isolated shutdown and removal after an
interim PASS, evidence preservation, and records described below. It does not
authorize dependency creation, P5 byte deletion, live database purge,
tombstone creation, CAPLAB-24/P6, CAPLAB-25/P7, historical-evidence admission,
model calls, training, export, acceptance, or a live PostgreSQL change.

## Observations and inference

**Observation:** ADR 0012 restored exact backup
`20260712-010203F_20260716-195901D`, used the fixed target configuration,
accepted `max_wal_senders=10`, obtained WAL, reached consistency, served
read-only queries, rejected the real TCP probe through the target HBA, and
then failed the combined identity gate. The exit guard fast-stopped only the
isolated postmaster. Independent verification returned FAIL for the complete
correction, PASS for the `max_wal_senders` sub-repair, and PASS for the live
cluster safety boundary.

**Observation:** the receipt chronology is: read-only readiness at
`06:20:35.767`, target-HBA TCP rejection at `06:20:35.908`, promotion timeline
2 selection at `06:20:35.975`, and isolated fast shutdown at `06:20:35.979`.
The helper samples `pg_is_in_recovery()` before the TCP probe and requires the
result to be `f`.

**Observation:** the preserved target reports `Database cluster state: shut
down in recovery`, `max_wal_senders setting: 10`, no `postmaster.pid`, no TCP
or Unix listener, and no target-named PostgreSQL process. Its external state
remains `phase=starting`. The live cluster remains active at
`/var/lib/postgresql/17/main`, port `5432`, PID `2654541`, start time
`2026-07-03 06:16:25.66893+00`; P4 and P5 controls and P5 closure `1|1|0|0`
remain unchanged.

**Inference, high confidence:** `pg_ctl --wait start` returned at queryable
hot-standby readiness, before automatic promotion completed. The immediate
recovery-state sample returned `t`, causing the combined identity predicate
to fail. Another predicate mismatch is a credible but weaker rival because
the failed receipt did not print every sampled value; the fixed config,
successful queries, HBA rejection, timeline ordering, and preserved control
state all discriminate in favor of the readiness race.

## Decision and authorization

**Decision:** after `pg_ctl --wait start` succeeds, the isolated restore
helper must wait for promotion completion before it performs the existing
settings, replication, TCP, and identity checks.

The wait contract is fixed:

- query `SELECT pg_is_in_recovery();` immediately, then at one-second
  intervals;
- continue only while the exact result is `t`;
- proceed only when the exact result is `f`;
- fail on a query error or any result other than `t` or `f`;
- re-prove the frozen live-cluster identity before every sleep;
- fail after 30 seconds without promotion; and
- print the successful poll count and the final recovery value in the receipt.

The 30-second ceiling is selected rather than a configurable timeout. The
observed transition completed within one second, while a fixed ceiling keeps
failure handling inspectable and prevents an unbounded wait. No caller needs
a second timeout policy. Calling `pg_ctl promote` again is rejected because
the restored configuration already requests automatic promotion. Sleeping a
fixed duration without testing recovery state is rejected because it cannot
prove the postcondition. Leaving the stopped target unchanged is the safe
no-change outcome if any gate fails.

**Owner and authority:** `caplab-execution-delegate`, acting under the
repository owner's direct delegation in this owner-authorized thread on
2026-07-17. The delegation permits this bounded CAPLAB decision and its named
execution effects. It grants no acceptance authority and no standing
authority outside this campaign.

The restore identity remains fixed:

| Field | Value |
|---|---|
| Backup | `20260712-010203F_20260716-195901D` |
| Target | `/var/tmp/caplab-p5-pgrestore` |
| Port | `55435` |
| Socket | `/var/tmp/caplab-p5-pgrestore/socket` |
| Promotion wait | 30 seconds, one-second polling |
| Isolated `max_wal_senders` | `10` |
| Data campaign | `caplab-p5-recovery-2026-07-16` |
| Operation | `op-p5-recovery-0001` |
| P5 content SHA-256 | `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d` |
| P4 content SHA-256 | `87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92` |

### Preserved safety boundary

Every ADR 0012 target, HBA, config-hash, state, marker, exact-PID,
process-command, loopback-port, socket, replication, TCP rejection, and live
identity guard remains mandatory. The readiness wait may query only the fixed
isolated socket. It must not name a live data, config, HBA, ident, PID, or
service-control path. A timeout or unexpected value enters the existing
failure path, which verifies and stops only the exact isolated target and
re-proves the live identity.

### Source and execution gates

Before the first host effect, the executor must:

1. add one RED regression test that reproduces a `t` then `f` recovery-state
   sequence and proves the helper waits rather than failing at hot-standby
   readiness;
2. make the smallest helper, test, and documentation change that turns it
   GREEN without adding a timeout option or changing other guards;
3. pass complete Proximal P5 tests, Bash syntax, ShellCheck when installed,
   systemd verification, documentation checks, and `git diff --check`;
4. commit and push a clean Proximal revision; and
5. freeze this decision's SHA-256, both clean repository commits, the current
   stopped target and state, exact backup, live identity, P4/P5 controls,
   helper hashes, a new root-only execution directory, and an independent
   verifier who did not implement the change.

Only after those gates may the executor:

1. install and hash-check the exact committed helper;
2. remove the current stopped target and state only after matching these
   frozen SHA-256 values: external state
   `1d3190a64e8c075896cc075a5575e8fa2e66ddff74d26d2480725dffc404b457`,
   marker
   `e2acf41d67ca82aa45574c924bebe383badbce25c872948c148229d513d9c091`,
   config
   `632c8645255e011912303dd01e0defb1b043f70fabd012b52301c114581dbbbb`,
   HBA
   `accbc912e975cc95301833f8c161320c462283f5ab10c08bc53e28aba26c66ef`,
   ident
   `87311bfe1b17cb2b0f376c8ffebbfdaf2590b6ac675b1b6d8edecfc146461f3f`,
   auto config
   `7485cdb76d33628049b0958f3fe25e05e77e1709b91feebe4a162846784eeb0b`,
   and `pg_control`
   `ece280302cf3fc1e7f3086f5d1e39e23573dd65cb1a259305de4a7be2992f75d`;
3. restore the selected backup once;
4. query the isolated database for the successful promotion wait, effective
   settings, zero replication senders, TCP rejection, migration ledger, P4
   control, P5 registration, manifests, content identities, and closure;
5. obtain and preserve an interim independent report while the target remains
   queryable;
6. stop only the verified isolated instance, re-prove the live identity,
   remove only the isolated target and state, and preserve the evidence; and
7. obtain final independent verification.

No P5 application row, Garage object, `/nvr` copy, role, credential, live
PostgreSQL configuration, or live PostgreSQL service may change.

## Doctrine provenance and remaining evidence

The decision-guiding retrieval used packet `pkt-3715c6bef727de92`, content
SHA-256
`3715c6bef727de9249df435cd1b0eabd947029b11cbf2501503c868e0a6b28d2`,
retriever `retriever-1392f38f05a41086`, doctrine
`doctrine-a90ee3f1cf7b6f26`, corpus
`corpus-2026-07-12-d2ea7b94a1ce`, and release commit
`95ddd1c408348f2079180476fb188262cfe43985`. Doctrine supports the causal,
test-first, preservation, explicit-failure, and bounded-authority approach; it
does not supply the delegated authority or replace this decision.

**Material completion obligations:** the focused test must fail before the
repair and pass after it; the changed wait must be exercised by the one real
restore; complete relevant regression evidence must pass; timeout and query
failures must remain caller-visible and invoke safe isolated cleanup; and all
preservation boundaries above must be verified. These remain open until their
source and runtime gates produce evidence.

**Satisfied by this decision and current evidence:** the bounded question,
alternatives including no change, caller recovery needs, intervention cost
and uncertainty, security and durability boundaries, and preservation matrix
are stated above and supported by the production receipt, current source,
accepted decisions, and live read-only checks.

**Not material to this operation:** generic request-deduplication, durable
application-effect, external-effect retry, identity-generation, retention,
collision, and stable-intent obligations do not apply to this fixed backup,
target, campaign, and one-attempt administrative restore with no permitted
application durable effect. Separate test-suite false-positive history and an
accepted future-change plan cannot change the bounded repair. Leaving the
code alone remains mandatory on a failed gate, but does not outrank the
realized repeated restore blocker and the owner's delegated instruction to
proceed.

## Stop conditions and advancement

Stop and preserve state on any decision, source, test, timeout, backup,
target, configuration, HBA, live identity, recovery, promotion, query, P4,
P5, migration, replication, verifier, shutdown, or removal mismatch. If the
isolated instance cannot be proven before shutdown, preserve it and escalate.
Do not perform a second retry under this decision.

PASS requires completed promotion within the fixed wait, all frozen CAPLAB
identities matching, zero replication senders, rejected TCP access, a
preserved interim report, guarded shutdown and exact removal, and an unchanged
live cluster. PASS removes only the isolated-restore blocker. It does not pass
P5, authorize purge, accept CAPLAB, or authorize P6.

## Reopening conditions

Reopen on promotion timeout, another recovery requirement, any need to
configure the wait, a live identity change, any need for a live configuration
path, a target that cannot be identified or removed exactly, or a request to
resume the remaining P5 purge sequence.

