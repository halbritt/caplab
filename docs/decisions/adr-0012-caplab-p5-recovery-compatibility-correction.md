---
id: adr-0012
artifact_type: architecture-decision-record
title: CAPLAB P5 PostgreSQL recovery compatibility correction
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership
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
  - caplab-p5-isolated-restore-execution-2026-07-16
  - caplab-p5-isolated-restore-verification-2026-07-16
---

# CAPLAB P5 PostgreSQL recovery compatibility correction

Status interpretation: after reviewing ADR 0011's independent FAIL and the
recommendation to use a recovery-compatible `max_wal_senders` value while
retaining the proven isolation guards, the repository owner instructed the
executor to `do it`.

This decision authorizes campaign
`caplab-p5-recovery-compatibility-corrective-2026-07-17` through
`2026-07-23T23:59:59Z`. It authorizes only the exact helper and HBA correction,
one clean isolated-restore retry, restored-database verification, isolated
shutdown and removal after an interim independent report, evidence
preservation, and final independent verification described below. It does not
authorize dependency creation, P5 byte deletion, live database purge,
tombstone creation, CAPLAB-24/P6, CAPLAB-25/P7, historical-evidence admission,
model calls, training, export, acceptance, or a live PostgreSQL change.

## Observations and inference

**Observation:** ADR 0011's helper restored exact backup
`20260712-010203F_20260716-195901D`, used the target-owned configuration, HBA,
socket, and loopback port, obtained recovery WAL, and then failed because
`max_wal_senders = 0` was below the backed-up primary value `10`. PostgreSQL
shut the isolated instance down. The independent verifier returned FAIL for
the correction and PASS for the live-cluster safety boundary.

**Observation:** `pg_controldata` on the preserved target records recovery
minima `max_connections=100`, `max_worker_processes=8`,
`max_wal_senders=10`, `max_prepared_xacts=0`, `max_locks_per_xact=64`,
`wal_level=replica`, and `track_commit_timestamp=off`. PostgreSQL 17's target
configuration already uses compatible defaults for every recorded value
except the helper's explicit `max_wal_senders = 0` override.

**Observation:** the failed target remains stopped with no `postmaster.pid`,
target-named PostgreSQL process, or listener on `55435`. Its root state remains
`phase=starting`. The live cluster remains active at
`/var/lib/postgresql/17/main`, port `5432`, postmaster PID `2654541`, start
time `2026-07-03 06:16:25.66893+00`, and `max_wal_senders=10`.

**Inference:** the explicit zero override is the first and only currently
observable compatibility mismatch. Setting the isolated value to the backup's
recorded `10` is the narrow causal repair. Another recovery or configuration
defect remains a credible rival until the restored database reaches promotion
and its contents are queried.

## Decision and authorization

**Decision:** select campaign
`caplab-p5-recovery-compatibility-corrective-2026-07-17` and set the isolated
restore's `max_wal_senders` to exactly `10`.

**Owner and authority:** the repository owner under repository ownership,
exercised by the instruction `do it` after receiving the ADR 0011 FAIL,
live-cluster PASS, and bounded recommendation on 2026-07-17.

The restore identity remains fixed:

| Field | Value |
|---|---|
| Backup | `20260712-010203F_20260716-195901D` |
| Target | `/var/tmp/caplab-p5-pgrestore` |
| Port | `55435` |
| Socket directory | `/var/tmp/caplab-p5-pgrestore/socket` |
| Isolated `max_wal_senders` | `10` |
| Data campaign | `caplab-p5-recovery-2026-07-16` |
| Operation | `op-p5-recovery-0001` |
| P5 content SHA-256 | `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d` |
| P4 content SHA-256 | `87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92` |

The selected value is explicit rather than inherited from a PostgreSQL
default so the recovery contract remains inspectable and version-independent.
Reusing the current partial target is rejected because it would bypass a clean
restore and state transition. Importing the live Debian configuration is
rejected because it would cross the isolation boundary. Leaving the target
stopped is the safe no-change alternative if any new gate fails.

### Replication and live-cluster safety

`max_wal_senders=10` is recovery-compatible process capacity, not access
authorization. The target HBA must explicitly reject local and TCP physical
replication connections, reject every TCP database client, and allow only
local peer authentication for the `postgres` verification path. The helper
must prove after promotion that:

- effective `max_wal_senders` is `10`;
- `pg_stat_replication` contains zero rows;
- a TCP database connection to `127.0.0.1:55435` is rejected;
- the exact target data directory, port, socket, HBA, ident, archive mode,
  SSL, and preload settings match; and
- the live data directory, PID, port, start time, and active state are
  unchanged.

The existing exact-target start, query, stop, state, marker, configuration
hash, process-command, and live-identity guards remain mandatory. No helper may
name the live data, config, HBA, ident, or PID path as an isolated target.

### Source and execution gates

Before the first host effect, the executor must:

1. add one RED regression assertion that rejects `max_wal_senders=0` and
   requires the explicit recovery-compatible value and replication HBA;
2. make the smallest helper and documentation change that turns it GREEN;
3. pass the complete Proximal P5 tests, Bash syntax, ShellCheck when installed,
   systemd verification, and documentation checks;
4. commit and push a clean Proximal helper revision;
5. freeze this decision's SHA-256, both clean repository commits, the prior
   stopped target and state, live cluster identity, P4 and P5 controls, exact
   backup catalog entry, helper hashes, a new root-only execution directory,
   and a fresh independent verifier who did not implement the correction.

Only after those gates may the executor:

1. remove the prior stopped target and old isolated state after proving their
   frozen identities and absence of a PID, listener, mount boundary, or process
   reference;
2. install the committed helper and restore the exact selected backup once;
3. query the isolated database for effective settings, replication absence,
   migration ledger, P4 control, P5 registration, manifests, content
   identities, and closure counts;
4. obtain and preserve the fresh verifier's interim read-only report while the
   isolated instance remains queryable;
5. stop only that verified isolated instance, re-prove the live identity,
   remove only the isolated target and state, and preserve the evidence; and
6. obtain the verifier's final PASS or FAIL for this correction.

No P5 application row, Garage object, `/nvr` copy, role, credential, live
PostgreSQL configuration, or live PostgreSQL service may change.

## Doctrine retrieval and remaining evidence

The execution-guiding doctrine retrieval used packet
`pkt-2260592ee6b59ee3`, content SHA-256
`2260592ee6b59ee33b60aada30db1b58573a2cbfcc7de15c25a09ebf8896a872`,
retriever `retriever-1392f38f05a41086`, doctrine
`doctrine-a90ee3f1cf7b6f26`, and corpus
`corpus-2026-07-12-d2ea7b94a1ce`. The retrieval question was whether to
make this exact compatibility correction while retaining the rejecting HBA
and live-cluster guards, then perform one exact retry. The packet informed the
recommendation; it did not supply owner authorization or replace this
decision.

**Material completion obligations:** the changed recovery path must be
exercised after the repair, the focused regression and complete relevant test
suites must pass, and the helper must implement the repository's explicit
failure policy: stop and preserve on mismatch, expose an actionable receipt,
and never trade live-cluster correctness or availability for isolated-restore
progress. These obligations remain open until the source and runtime gates in
this decision produce evidence.

**Satisfied by repository and decision evidence:** caller recovery needs,
repository language and convention, and product correctness and availability
policy are specified by the exact stop conditions, receipts, clean-retry
limit, and live-cluster invariants above. The prior production failure is
direct falsifying evidence, so a separate history of test-suite false
positives is not material to this causal repair.

**Not material to this operation:** generic request-deduplication, durable
application-effect, external-effect retry, identity-generation, retention,
collision, and stable-intent obligations do not apply. The operation has
fixed backup, target, campaign, and operation identities; the target and state
guards refuse reuse; exactly one retry is authorized; and no application
durable effect is permitted. An expected future-change plan is not required
because this bounded correction is already selected. Leaving the code alone
was considered and remains the mandatory safe outcome when any gate fails.

## Stop conditions and advancement

Stop and preserve state on any decision, source, test, backup, target,
configuration, HBA, live identity, recovery, query, P4, P5, migration,
replication, verifier, shutdown, or removal mismatch. If the isolated instance
cannot be proven before shutdown, preserve it and escalate. Do not perform a
second retry under this decision.

PASS requires the selected backup to become queryable with all frozen CAPLAB
identities matching, zero replication senders, rejected TCP access, a
preserved interim report, guarded shutdown and exact removal, and an unchanged
live cluster. PASS removes only the isolated-restore blocker. It does not pass
P5, authorize purge, accept CAPLAB, or authorize P6.

## Reopening conditions

Reopen on another recovery requirement, a live identity change, any need for a
live configuration path, a target that cannot be identified or removed
exactly, or a request to resume the remaining P5 purge sequence.
