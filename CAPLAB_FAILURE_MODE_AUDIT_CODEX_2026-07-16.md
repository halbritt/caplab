# CAPLAB failure-mode audit

## 0. Audit basis

Target: standalone CAPLAB repository at `/home/halbritt/git/caplab`.

Scope: CAPLAB-23/P5 failure-bearing paths across the Python registration
runtime, PostgreSQL metadata, Garage objects, the independent `/nvr` copy, P4
host custody, and the host backup lifecycle. The dashboard and historical
Study 001 evidence are outside the requested checkpoint.

Repository state: clean `main` at
`9fce7aa3ba8e5a56fdb005e4e259aefc3e3ed5a0` before this report was written.
The P4 Proximal worktree was clean at `74acd31`; it is a frozen P4 host surface,
not an available P5 mutation surface.

Authority: static tracing, repository checks, and read-only host observation.
The owner instructed the agent to handle CAPLAB-23, CAPLAB-24, and CAPLAB-25 in
order. Accepted ADRs require a new exact authorization before P5 fault,
restore, deletion, or purge effects, so no fault was injected and no
quarantined P4 state was changed.

Commands run:

- `PYTHONDONTWRITEBYTECODE=1 make check` — ran, passed 50 tests, with the two
  live integration gates skipped by their explicit guards.
- read-only `systemctl show`, `systemctl cat`, and status checks for the restic
  backup and prune units — ran.
- prior preserved P4 execution and verification records — inherited evidence,
  manifest-verified before this audit.

Commands not run:

- live CAPLAB registration, restore, corruption, deletion, or purge — not run,
  not authorized.
- service restart, process termination, storage corruption, database mutation,
  `restic prune`, or pgBackRest restore — not run, not authorized.

Evidence tiers used: `static-traced`, `executed`, `inherited`, and
`unverified-gated`.

### Depth ledger

| Boundary | Pass | Selection or skip reason | Files or surfaces read | Strongest evidence | Residual risk |
|---|---|---|---|---|---|
| Registration across PostgreSQL, Garage, and `/nvr` | deep-trace | Default state-bearing path; interruption can leave partial durable state | `registration.py`, PostgreSQL adapter, migration, runtime tests | executed | Live interruption was not injected. |
| Registered Garage or `/nvr` byte loss | deep-trace | Loss blocks retrieval and is a P5 recovery objective | `registration.py`, S3 and filesystem adapters, P4 verification | static-traced | No live restore path has run. |
| PostgreSQL append-only state and purge | deep-trace | Purge is destructive and required before P6 | migration, custody plan, ADRs 0005 and 0007 | static-traced | No authorized purge implementation exists. |
| Host backup and restore lifecycle | deep-trace | Failed prune state and unverified restore block the recovery claim | live systemd state and unit definitions, Proximal backup docs | inherited | The July 1 error text is unavailable; cause is not established. |
| P4 host lifecycle and credentials | survey | Frozen control must remain unchanged; current disablement is already verified | Proximal `caplab-runtime/AGENTS.md` and `README.md` | inherited | P5 needs a separate host surface. |
| Migration application and checksum drift | survey | Existing path is transactional and fail-closed | `migrations.py`, migration tests | executed | Later custody migration behavior is unimplemented. |
| Dashboard projection | survey | Read-only and outside P5 storage recovery | repository tests and README | executed | No material P5 failure path found. |
| Historical Study 001 evidence | unread | P6 is gated by P5 and no admission authority exists | none | none | Availability and admissibility remain P6 questions. |

## 1. Verdict

`HIGH_RISK_FAILURES`, medium confidence.

Two serious recovery gaps remain on state-bearing paths: registered byte loss
is detected but has no CAPLAB recovery operation, and the backup lifecycle has
a failed prune unit without a verified restore. The existing runtime has useful
fail-closed and retry behavior, but those properties do not establish P5
recovery or purge fitness. Confidence is capped at medium because the exact
fault and restore drills are authorization-gated.

Counts: 0 blockers, 2 serious, 2 minor.

## 2. Failure boundary inventory

The runtime writes one logical registration across three authorities:
PostgreSQL owns operational metadata, Garage owns registered evidence bytes,
and `/nvr` holds the required independent byte copy. `RegistrationService`
claims the operation in PostgreSQL, writes and verifies Garage, writes and
verifies `/nvr`, then finalizes registration in a PostgreSQL transaction.
Only the last step is transactionally atomic.

Content-addressed byte stores refuse a changed replay through the runtime.
Garage itself is not WORM: the active writer grant included delete capability,
and an administrator can still alter bytes out of band. Reconciliation detects
missing or mismatched registered bytes and metadata, but does not repair them.

The core migration makes application tables append-only with triggers that
reject ordinary `UPDATE` and `DELETE`. The runtime exposes a non-applying
cleanup plan only. This is a safe default for P4, but it is not an executable
P5 purge contract.

The host backup surface has independent pgBackRest and restic layers. On this
audit's observation interval, `restic-backup.service` was still activating
from its 02:45:58 UTC start, while `restic-prune.service` remained failed from
July 1. The daily backup and monthly prune units share the same repository but
have no common serialization mechanism. That permits overlap; it does not
prove overlap caused the historical failure.

## 3. Ranked failure-mode ledger

### FMA-001 — SERIOUS

- Subsystem: registered Garage and `/nvr` bytes.
- Trigger class: dependency failure, partial write, or out-of-band mutation.
- Invariant: every registered content identity remains readable with matching
  bytes from Garage and `/nvr`, and either surviving copy can restore the
  selected state.
- Failure point: `RegistrationService._verified_payload`,
  `RegistrationService.verify`, `RegistrationService.retrieve`, and
  `RegistrationService.reconcile` in `src/caplab/runtime/registration.py`.
- Trigger: a registered Garage object or `/nvr` copy is deleted, replaced, or
  becomes unreadable.
- Current behavior: verification and retrieval read both copies and raise
  `ObjectMismatch` or `CopyMismatch`; reconciliation reports `missing` or
  `mismatch`. No runtime, host controller, scheduler, or operator command
  restores the failed copy. The P4 host surface explicitly forbids adding
  restore or fault commands.
- Blast radius: every dependent recomputation or evidence use stops. If one
  good copy remains, the bytes are not lost, but CAPLAB cannot return the
  registration to its selected operational state through a traced path.
- Detectability: loud for a direct verify or retrieve; delayed until
  reconciliation for an idle registration.
- Recovery: none found in CAPLAB. A manual administrator could copy bytes, but
  no authorized, content-checked recovery operation or independent
  verification path exists.
- Evidence tier: `static-traced`; verification status:
  `not run - not authorized`.
- Smallest next step: preregister one P5-only source-loss and alteration matrix
  that restores Garage from `/nvr` and `/nvr` from Garage, with exact identities,
  direct exit-status receipts, and a different verifier.

### FMA-002 — SERIOUS

- Subsystem: PostgreSQL and off-site backup lifecycle.
- Trigger class: dependency failure, scheduling overlap, or restore failure.
- Invariant: backup retention remains healthy and CAPLAB metadata can be
  restored within ADR 0005's target RPO and RTO.
- Failure point: the live `restic-backup.service` and
  `restic-prune.service` units and their timers. The units access the same
  repository without a shared lock or mutual exclusion.
- Trigger: prune and backup overlap, or prune fails for another repository,
  network, credential, or storage reason.
- Current behavior: the July 1 prune invocation exited with failure and remains
  failed. The retained journal no longer establishes its exact cause. The
  current daily backup demonstrated that a backup can remain active for several
  hours, long enough to overlap the monthly prune window. No CAPLAB PostgreSQL
  restore drill has been run.
- Blast radius: backup expiry and repository-health claims are unavailable;
  a later restore may exceed the selected objective or fail. P6 historical
  evidence admission remains blocked.
- Detectability: external-signal-only through systemd failure state unless an
  operator inspects it.
- Recovery: the backup service continues independently, but no traced action
  has repaired the prune failure or proved a restored CAPLAB database.
- Evidence tier: `inherited` plus read-only runtime observation; verification
  status: `not run - not authorized`.
- Smallest next step: preserve the next failure output, serialize backup and
  prune access, then restore an exact post-P5 pgBackRest backup into an isolated
  PostgreSQL cluster and verify CAPLAB identities without replacing the live
  cluster.

### FMA-003 — MINOR

- Subsystem: cross-store registration finalization.
- Trigger class: crash, restart, or PostgreSQL failure after byte writes.
- Invariant: retries do not rewrite bytes or manufacture completion, and
  abandoned partial registrations remain discoverable.
- Failure point: `RegistrationService.register` after Garage and `/nvr`
  verification but before `MetadataStore.finalize_registration`.
- Trigger: process termination or database error in the finalization window.
- Current behavior: the operation request and any completed byte writes remain.
  Reconciliation reports incomplete metadata. Repeating the identical operation
  verifies the existing bytes and can finish registration idempotently.
  Conflicting operation bytes are refused before added effects. There is no
  general sweep that enumerates abandoned requests and unreferenced bytes.
- Blast radius: one operation can remain incomplete with orphan bytes and
  audit events. Registered state is not falsely reported.
- Detectability: structured when the operation ID is reconciled; otherwise
  delayed because no orphan inventory runs.
- Recovery: same-request retry when the original request is available; manual
  custody is otherwise required.
- Evidence tier: `executed` through the hermetic interrupted-finalization test;
  live verification status: `not run - not authorized`.
- Smallest next step: expose a verifier-owned orphan inventory that binds
  incomplete requests, object keys, copy keys, and retry or purge disposition.

### FMA-004 — MINOR

- Subsystem: authorized purge and retention.
- Trigger class: retention expiry, privacy disposition, or campaign cleanup.
- Invariant: only exact owner-authorized P5 identities are purged, dependencies
  block unsafe deletion, and a different verifier confirms absence while Git
  retains a non-sensitive tombstone.
- Failure point: `src/caplab/runtime/custody.py`, the append-only triggers in
  `0001_runtime_core.sql`, and the P4 command surfaces.
- Trigger: a valid purge obligation becomes due.
- Current behavior: `cleanup-plan` identifies state but applies nothing. S3 and
  filesystem adapters have no delete method, ordinary PostgreSQL deletion is
  rejected, and the P4 host controller forbids purge. The operation fails
  closed before deletion.
- Blast radius: no accidental deletion occurs, but retention or privacy
  obligations cannot be executed and P5 cannot qualify the purge contract.
- Detectability: loud and immediate because no purge command exists.
- Recovery: none needed for the refused operation; an authorized P5 custody
  path is absent.
- Evidence tier: `static-traced`; verification status:
  `not run - not authorized`.
- Smallest next step: define one non-routine custodian operation whose input is
  an exact authorization identity and whose database, Garage, and `/nvr`
  effects refuse any external dependency.

## 4. Recovery and idempotency

Same-operation registration replay is the strongest existing recovery
property. The operation request hash prevents an operation ID from being
reused with changed inputs. Existing identical byte writes are accepted as
replay, while changed bytes raise a typed mismatch. Final registration remains
absent until both copies pass verification.

Reconciliation is diagnostic. It reports metadata, locator, provenance,
Garage, and `/nvr` state but deliberately performs no repair. The cleanup plan
is also diagnostic and non-applying. No background sweep, automatic repair,
restore command, or executable purge path exists.

## 5. Concurrency and partial-write notes

The PostgreSQL advisory lock derived from content identity serializes
cooperating CAPLAB writers across the object and copy write window. It does not
stop an out-of-band Garage administrator, filesystem administrator, or host
failure.

The `/nvr` adapter writes a temporary file, fsyncs it, creates the final name
with a hard link, and fsyncs the parent directory. This avoids exposing a
partially written final file. A crash can leave a hidden temporary file, but
the next write does not treat that file as the registered copy.

Garage `put_object` is not a conditional create. The runtime's advisory lock
and read-before-write checks protect cooperating writers; the post-write
readback detects a changed result. There is no server-enforced WORM guarantee.

The restic units have no shared concurrency control. A blocking shared lock or
equivalent scheduler contract is needed before CAPLAB can claim the backup
lifecycle is serialized.

## 6. What fails loudly or safely

- Operation ID reuse with changed request bytes raises `OperationConflict`
  before new external effects.
- Missing or altered registered bytes raise typed errors and prevent retrieval.
- Locator, manifest, migration-ledger, and runtime-provenance substitutions are
  detected.
- The filesystem copy path refuses symlinks, non-canonical keys, unsafe modes,
  and non-identical replacement.
- Applied migration checksum drift stops migration.
- The P4 host surface has no delete, restore, purge, or fault command and is
  disabled after execution.
- The cleanup plan names quarantined state without authorizing deletion.

These are technical observations. They do not verify P5, authorize P6, or
constitute CAPLAB acceptance.

## 7. Gated verification

The following probes would raise confidence after exact owner authorization:

- delete and alter only a new P5 Garage object, prove verify/retrieve refusal,
  restore it from the matching `/nvr` copy, and reconcile;
- remove and alter only the matching P5 `/nvr` copy, restore it from Garage,
  and reconcile;
- stop one P5 registration after both byte writes and before final metadata,
  prove orphan detection, then replay the same request;
- create invalid and ambiguous P5 fixtures and prove they remain
  invalid-attempt observations rather than subject outcomes;
- create an exact post-P5 pgBackRest backup, restore it to an isolated cluster,
  and compare manifests and registration identities;
- purge only the exact P5 synthetic identity closure, verify independent
  absence and tombstone retention, and prove the P4 control is unchanged.

## 8. Residual risk and unread areas

The top residual risk is that a manual recovery can appear technically
successful without being bound to the exact content identity, authorization,
and independent verifier. P5 must make those inputs first-class records.

The root cause of the July 1 restic prune failure is unknown because its
historical error output is unavailable. Schedule overlap is a credible
inference from the unit definitions and observed backup duration; remote,
credential, repository, or storage failure remain credible rivals.

Historical Study 001 evidence was not read. Its admissibility, privacy,
licensing, provenance, and exact preservation identities remain unavailable
until P5 passes and P6 receives separate authorization.

### Rejected candidates

- Total-host loss was omitted as a finding because ADR 0005 explicitly excludes
  it from the v0 recovery guarantee.
- Dashboard availability was omitted because the P5 checkpoint concerns
  evidence custody and the dashboard has no write path.
- A claim that restic schedule overlap caused the July 1 failure was rejected;
  the surviving evidence does not establish causation.
