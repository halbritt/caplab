---
id: adr-0011
artifact_type: architecture-decision-record
title: CAPLAB P5 isolated PostgreSQL correction
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership
created: 2026-07-16
decided_at: 2026-07-16
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
  - caplab-p5-corrective-execution-2026-07-16
  - caplab-p5-corrective-verification-2026-07-16
---

# CAPLAB P5 isolated PostgreSQL correction

Status interpretation: after reviewing why the second P5 campaign stopped,
the repository owner instructed the executor to proceed with a dedicated
isolated PostgreSQL configuration bound to the restored directory, loopback
port `55435`, an isolated socket and HBA, with guards proving the helper cannot
address or stop the live cluster.

This decision authorizes campaign
`caplab-p5-isolated-restore-corrective-2026-07-16` through
`2026-07-23T23:59:59Z`. It authorizes only the helper repair, one exact
isolated-restore retry, restored-database verification, isolated shutdown and
removal, evidence preservation, and independent verification described below.
It does not authorize P5 dependency creation, byte deletion, database purge,
tombstone creation, CAPLAB-24/P6, CAPLAB-25/P7, historical-evidence admission,
model calls, training, export, acceptance, or any change to the live
PostgreSQL cluster.

## Observations and inference

**Observation:** pgBackRest restored backup
`20260712-010203F_20260716-195901D` into
`/var/tmp/caplab-p5-pgrestore`, including `global/pg_control`, but PostgreSQL
did not start because the restored data directory lacks `postgresql.conf`.
The live Debian PostgreSQL 17 cluster stores its configuration under
`/etc/postgresql/17/main` and its data under
`/var/lib/postgresql/17/main`. **Evidence:** the corrective
[`execution`](../records/caplab-p5-corrective-execution-2026-07-16.md) and
[`verification`](../records/caplab-p5-corrective-verification-2026-07-16.md)
records and the preserved restore receipt.

**Observation:** the failed isolated target is present, has no
`postmaster.pid`, and no process listens on port `55435`. The live cluster is
active on port `5432`; its postmaster PID is independently observable from its
live data directory.

**Inference:** the first startup divergence is the helper's assumption that a
Debian data-directory backup contains its external configuration. The narrow
repair is to generate a target-owned configuration and HBA after pgBackRest
restores the data, then bind every start, query, stop, and cleanup action to
the exact isolated target. A separate recovery or configuration defect remains
a credible rival until the restored instance starts and its contents are
queried.

## Decision and authorization

**Decision:** select campaign
`caplab-p5-isolated-restore-corrective-2026-07-16`.

**Owner and authority:** the repository owner under repository ownership,
exercised by the instruction to proceed with the stated isolated configuration
and live-cluster guards on 2026-07-16.

The selected restore identity is fixed:

| Field | Value |
|---|---|
| Backup | `20260712-010203F_20260716-195901D` |
| Target | `/var/tmp/caplab-p5-pgrestore` |
| Port | `55435` |
| Socket directory | `/var/tmp/caplab-p5-pgrestore/socket` |
| Data campaign | `caplab-p5-recovery-2026-07-16` |
| Operation | `op-p5-recovery-0001` |
| P5 content SHA-256 | `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d` |
| P4 content SHA-256 | `87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92` |

Before the first host effect, the executor must freeze this decision's hash,
the clean Proximal helper commit, the failed target's stopped state, the live
cluster's data directory, postmaster PID, port, start time, the P4 and P5 live
database identities, the selected backup catalog entry, a new root-only
execution directory, and a fresh independent verifier who did not implement
the correction.

### Dedicated isolated configuration

The helper must create `postgresql.conf`, `pg_hba.conf`, and `pg_ident.conf`
inside the restored target after pgBackRest completes. The configuration must:

- set `data_directory` to the exact restored target;
- listen only on `127.0.0.1` port `55435` and use only the target socket;
- reject every TCP database client in the isolated HBA and allow only local
  peer authentication for the `postgres` verifier path;
- disable SSL, archive mode, external preload libraries, and remote
  replication surfaces; and
- name no live PostgreSQL data, configuration, HBA, ident, socket, or PID
  path.

The helper must replace the restored `postgresql.auto.conf` with a
target-owned recovery-only file containing the exact pgBackRest
`restore_command`, immediate recovery target, promotion action, and current
timeline. It must not retain live-cluster `ALTER SYSTEM` settings such as
archive commands or preload libraries. It must preserve the generated
configuration, recovery, and HBA hashes in target markers and execution
evidence.

### Live-cluster guards

Both start and stop helpers must observe the live cluster through read-only
queries before acting. They must record its canonical data directory and
postmaster PID, refuse any target equal to the live data directory, and verify
on every exit that `postgresql.service` remains active with the same live
postmaster PID. The isolated postmaster PID must differ from the live PID.

After startup, the helper must query the isolated socket and require the exact
target data directory, port `55435`, archive mode `off`, and isolated socket.
The stop helper must refuse an absent marker, mismatched target, configuration
hash drift, port drift, missing isolated postmaster, or isolated PID equal to
the live PID. It may invoke `pg_ctl` only with the exact isolated target.

Source tests must fail before the repair and pass afterward. Repository tests,
shell syntax, ShellCheck when installed, systemd verification, and a live
read-only preflight must pass before retrying the restore.

### Authorized live sequence

The executor may:

1. preserve the already-stopped failed target's identity and confirm the fresh
   verifier assignment;
2. remove only `/var/tmp/caplab-p5-pgrestore` after proving it has no
   `postmaster.pid`, no listener on `55435`, and no process using that data
   directory;
3. install the committed helper correction;
4. restore only backup `20260712-010203F_20260716-195901D` into the exact
   target and start only the isolated instance;
5. query the isolated instance for the migration ledger, P4 control, P5
   registration, manifests, content identities, data directory, port, socket,
   HBA paths, archive mode, and recovery state;
6. obtain a read-only interim report from the fresh verifier while the
   isolated instance is queryable;
7. stop only the isolated instance with the guarded helper, verify the live
   PID and start time are unchanged, then remove only the isolated target; and
8. preserve a verified evidence manifest and obtain the verifier's final PASS
   or FAIL for this correction.

No P5 application row, Garage object, `/nvr` copy, role, credential, live
PostgreSQL configuration, or live PostgreSQL service may change during this
campaign.

## Stop conditions

Stop without purge or P6 on source, decision, backup, target, live PID, live
start-time, P4, P5, manifest, migration, port, socket, HBA, configuration-hash,
restore, query, verifier, shutdown, or removal mismatch. If the isolated
instance starts but cannot be verified, stop only that exact instance when the
guard can still prove its identity; otherwise preserve state and escalate.
Never use a broad process kill, `systemctl stop postgresql`, the live data
directory, or the live Debian configuration to recover this campaign.

## Verification and advancement

PASS for this correction requires independent evidence that the selected
backup was restored and queried through the isolated socket, every frozen
CAPLAB identity matched, the isolated instance stopped and was removed, and
the live cluster retained the same data directory, PID, start time, port, and
active state. PASS removes only the isolated-restore blocker. It does not pass
P5, authorize purge, accept CAPLAB, or authorize P6.

## Doctrine advisory provenance

The correction used evidenced packet `pkt-f69e91f413ec5944`, packet content
SHA-256
`f69e91f413ec5944417277c5c7a99e8796b1c3470bfd395dedda1cde6b9d2663`,
retriever `retriever-20c2013aa294d1fa`, doctrine
`doctrine-f630427242460c1e`, and corpus
`corpus-2026-07-12-d2ea7b94a1ce`.

The material unmet obligations are deliberate completion gates: exercise the
changed path after repair, verify the real PostgreSQL boundary rather than a
substitute, and preserve checkpoint verification. Assertions about exact
paths and forbidden live-cluster commands are implementation details by
design because those details are the safety contract.

Generic request-deduplication and collision obligations are nonmaterial: this
campaign creates no CAPLAB application request or durable application effect,
uses one fixed backup label and target, and refuses an existing target. The
suite's false-positive history and a separate leave-unchanged procedure are
also nonmaterial because the production failure is directly reproduced and
the owner selected the repair. ADR 0011 itself records the preservation
boundary required by the generic preservation procedure.

## Reopening conditions

Reopen if the restored instance requires any live configuration path, the
live postmaster changes, the selected backup is unavailable, a broader host
control surface is required, the target cannot be removed exactly, or the
remaining P5 purge sequence is requested.
