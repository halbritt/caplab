---
id: adr-0007
artifact_type: architecture-decision-record
title: CAPLAB v0 CLI runtime and first synthetic campaign
status: proposed
decision_owner: null
decision_authority: null
created: 2026-07-15
decided_at: null
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-runtime
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# CAPLAB v0 CLI runtime and first synthetic campaign

Status interpretation: this record is a reviewable proposal. The repository
owner authorized CAPLAB-21 discovery and preparation on 2026-07-15. No runtime
option has been selected, and no implementation or datastore effect is
authorized by this proposal.

## Decision question and scope

Should CAPLAB v0 use a repository-native Python batch CLI with direct adapters
for PostgreSQL, Garage S3, and the independent `/nvr` copy, and should the
repository owner authorize the exact CAPLAB-22 synthetic round-trip campaign
defined here?

This decision would govern the CAPLAB runtime interface, module boundary,
physical v0 namespaces, roles, migration mechanism, secret handling, first
synthetic campaign, rollback, verification, and authorization expiry. It would
not govern Study 001 evidence admission, failure and recovery qualification,
capability inference, export, training, model calls, Striatum placement, or
CAPLAB acceptance.

## Observations and evidence

**Observation:** ADRs 0002 and 0005 already select PostgreSQL as the authority
for operational metadata, Garage as the authority for registered evidence
bytes, `/nvr` as the required independent local copy, Git as the authority for
frozen research and governing records, and Plane as a regenerable planning
projection. ADR 0005 also fixes a dedicated `caplab` database, a dedicated
Garage bucket with a 1 GiB quota and campaign-scoped keys, and the local-only
recovery boundary. **Evidence:** ADRs 0002 and 0005.

**Observation:** P3 requires an explicit interface, repository paths,
PostgreSQL schema and roles, S3 namespace, dependencies, migrations, retention,
rollback, verification, expiry, stop conditions, and exact work-item scope
before implementation. **Evidence:** P3 in
[`plan-agent-capability-lab-v0`](../product/plans/plan-agent-capability-lab-v0.md).

**Observation:** the dashboard branch at
`e4636d2628adbbfca953734d4dc7cdfa91d72b04` owns the read-only
`caplab.dashboard` package. It reads checked-in projections and has no mutation
path or evidence-store dependency. The runtime-decision branch begins at that
commit. **Evidence:** `caplab/dashboard/README.md`, the dashboard commit, and
the clean runtime-decision worktree inspected on 2026-07-15.

**Observation:** a read-only host check on 2026-07-15 found PostgreSQL 17.10
active on the local socket and loopback port 5432. No `caplab` database or
`caplab*` role existed. `pgbackrest --stanza=proximal check` succeeded against
the PostgreSQL 17 cluster, seven backups were listed, and the differential,
full, and off-site restic timers were active. The latest off-site backup
service completed successfully on 2026-07-15, but `restic-prune.service` has
been failed since 2026-07-01. PostgreSQL archiving is on and cluster data
checksums are off. This is partial backup-health evidence, not a restore or
retention-lifecycle proof.

**Observation:** Garage 2.3.0 was active on loopback, with S3 at
`127.0.0.1:3900`, region `garage`, replication factor one, and no CAPLAB bucket.
The node reported about 98 GiB available. Garage's local authorization surface
grants bucket-level `read`, `write`, and `owner`; it does not expose a separate
delete permission. The installed botocore 1.34.46 `PutObject` model has no
`IfNoneMatch` input, so the proposed adapter cannot claim a server-enforced
create-only write through that client. **Evidence:** the whitelisted non-secret
fields in `/etc/garage.toml`, `garage status`, `garage bucket list`,
`garage bucket allow --help`, and local botocore model introspection, run
read-only on 2026-07-15.

**Observation:** `/nvr` is a root-owned local ZFS mount with about 8.9 TiB
available. No `/nvr/caplab` path exists. Python 3.12 can load `boto3` 1.34.46
and `psycopg` 3.3.4 in the owner's current environment. The distro-managed
`python3-boto3` package is 1.34.46; the proposed runtime would use an isolated,
hash-locked environment rather than depend on the owner's user site.

**Observation:** the repository owner replied `authorized` after CAPLAB-21 was
reported Ready but unauthorized. No exact runtime or campaign proposal had yet
been presented. The bounded interpretation is authority to perform P3
discovery and prepare this proposal, not selection of an unseen option or
permission for P4 effects.

## Inferences, rivals, assumptions, and uncertainty

**Inference:** a batch CLI is sufficient for the v0 administration because P4
through P7 are explicit, model-free operations with no standing request path.
A daemon would add lifecycle, authentication, and availability contracts that
no current caller requires.

**Inference:** `caplab.runtime` is the lowest-conflict module boundary. It can
share canonical identities with later CAPLAB code without importing or
changing the read-only `caplab.dashboard` surface.

**Inference:** Python is proportionate for the first vertical slice because the
repository already uses Python for its CAPLAB dashboard and test harness, and
the host has working PostgreSQL and S3 client libraries. A Go binary could make
deployment more self-contained, but it would introduce a second CAPLAB module
and dependency workflow before the storage contract has passed one synthetic
round trip.

The Garage permission model cannot prove that a raw write credential is
append-only. The proposal therefore limits credential access with separate
nologin-shell OS identities, keeps delete and cleanup out of the writer CLI, checks
existing bytes before and after every content-addressed write, and reconciles
both copies before metadata becomes registered. This is application and
operational containment, not Garage Object Lock or WORM storage. P4 must report
that residual limitation rather than claim stronger enforcement.

Current backup health does not establish PostgreSQL restore fitness, Garage
source-loss recovery, purge correctness, or total-host recovery. Those remain
P5 questions. The failed restic prune blocks a claim that the complete backup
lifecycle is healthy, but it does not prevent a disposable P4 round trip that
claims no recovery fitness. P5 and historical evidence admission remain
blocked until the failure is diagnosed and current prune health is verified.
Other assumptions are that the selected local services continue to meet ADR
0005's shared-host boundary and that the 1 GiB quota is sufficient for
synthetic and Study 001 v0 material.

## Recommendation and alternatives

**Recommendation:** select the CLI runtime and authorize only the P4 synthetic
round trip described below. Require a new authorization for P5 recovery and
purge work after P4 has an independent verification record.

The proposed interface is an explicit invocation of the isolated runtime
environment's Python as `python -m caplab.runtime`. It has no listener,
scheduler, mutation API, or dashboard import. `caplab/runtime/__main__.py` is
the entrypoint. `registration.py` owns the deep registration contract,
`custody.py` emits privileged cleanup plans without applying them, and narrow
adapters under `caplab/runtime/adapters/` own PostgreSQL, Garage, and `/nvr`
effects. The implementation owns these repository paths:

- `caplab/runtime/**`, including `__main__.py`, the registration and custody
  modules, adapters, canonical serialization, and configuration validation;
- `caplab/runtime/migrations/**` for ordered, content-identified SQL;
- `caplab/runtime/requirements.lock` for hash-locked runtime dependencies;
- `tests/test_caplab_runtime.py` and
  `tests/fixtures/caplab-runtime/**` for hermetic fixtures;
- `tests/integration/__init__.py` and
  `tests/integration/test_caplab_runtime_local.py` for the separately invoked
  live-store gate; and
- the CAPLAB plan, ADR index, execution record, verification record, and
  repository check wiring needed by this campaign.

The proposed command groups are `migrate`, `register`, `retrieve`, `verify`,
`reconcile`, and `cleanup-plan`. These are prospective contracts, not currently
implemented commands. The P4 runner may compose them into one synthetic round
trip. Every mutating command requires a stable operation ID and refuses an
existing operation ID whose request hash differs. No routine runtime command
deletes an object or database row.

The PostgreSQL namespace is database `caplab`, schema `caplab_v0`, with these
roles:

| Role | Login and authority |
|---|---|
| `caplab_owner` | `NOLOGIN`; owns database `caplab`, schema `caplab_v0`, and the migration objects. |
| `caplab_writer` | local peer login; may insert through the runtime contract and read its own registered state, but has no table `UPDATE`, `DELETE`, DDL, role, or database authority. |
| `caplab_reader` | local peer login; read-only access to registered v0 state. |
| `caplab_verifier` | local peer login; read-only access to integrity and reconciliation projections needed for independent verification. |

Matching nologin-shell OS accounts named `caplab_writer`, `caplab_reader`, and
`caplab_verifier` provide peer identity for the three login roles. Each has a
same-named primary group and belongs to a common system group named `caplab`.
The database revokes `PUBLIC` connect and schema creation; each role receives
only explicit `CONNECT`, schema `USAGE`, table, sequence, function, and view
grants, with a fixed `search_path`. PostgreSQL `postgres` may only bootstrap
the database and roles and run migrations with `SET ROLE caplab_owner`; there
is no migration login credential.

Migration `0001_runtime_core.sql` creates `schema_migrations`, immutable
`operation_requests`, append-only `operation_events`, `model_identities`,
`agent_configurations`, `administrations`, `trial_contexts`,
`trial_assignments`, `attempts`, `artifacts`, `attempt_artifacts`, `manifests`,
final `registrations`, and `audit_events`, plus secret-free current-state,
integrity, and reconciliation views. Primary keys and unique constraints bind
canonical SHA-256 identities, stable operation IDs and request hashes,
assignment-attempt numbers, and artifact locators. Current operation state is
derived from events rather than updated in place. Immutable research and
identity rows reject `UPDATE` and ordinary `DELETE`.

Migration files are applied in lexical order, one transaction per file, under
a CAPLAB advisory lock. `schema_migrations` records the complete filename,
file SHA-256, applied timestamp, and runtime Git commit. A checksum difference
for an applied filename stops execution. Applied migrations are never edited
or renamed; schema changes are forward-only. Teardown and purge are custody
operations, not down migrations, and no CAPLAB migration drops `public`.

The object namespaces are:

- Garage bucket `caplab-v0`, quota 1 GiB and 10,000 objects;
- Garage object root `objects/sha256/<first-two>/<64-hex-sha256>`; and
- independent copy root
  `/nvr/caplab/v0/objects/sha256/<first-two>/<64-hex-sha256>`.

The campaign ID belongs in PostgreSQL references and audit events, not in the
content-derived object key. Later campaigns reuse an identical object rather
than duplicate it. A cleanup plan may propose object deletion only when no
retained registration or campaign reference remains; otherwise it proposes
unlinking only the campaign reference.

The S3 adapter computes the SHA-256 itself and does not accept a caller-supplied
object key. It uses Garage's loopback endpoint, region `garage`, SigV4, and
path-style addressing. Because the selected client and server contract has no
verified conditional-create primitive, the runtime holds a PostgreSQL
advisory lock derived from the object hash across the existing-byte check,
Garage write, atomic and fsynced `/nvr` write, readback verification, and final
registration transaction. This serializes cooperating CAPLAB writers only.
Out-of-band administrator overwrite remains detectable through reconciliation,
not prevented by Garage.

The adapter treats an existing identical object as an idempotent success,
refuses a non-identical existing object, and verifies bytes after each write.
Registration inserts its final row only after Garage and `/nvr` both match the
expected hash. A crash leaves an immutable request and any append-only events
unregistered for reconciliation; it does not manufacture a completed state.

`/etc/caplab` is `root:caplab` mode `0750`. Non-secret settings live in
`/etc/caplab/runtime.toml`, `root:caplab` mode `0640`. The credentials root is
`root:caplab` mode `0750`; each `/etc/caplab/credentials/<role>/` is
`root:<role>` mode `0750`, and each credential file is `<role>:<role>` mode
`0400`. The runtime never reads `/etc/garage.toml`. Garage access keys live
outside Git and Plane and are owned by their matching OS identities.
Provisioning captures each one-time secret directly into a pre-created secret
file with shell tracing and command logging disabled; it never places a secret
in an argument, environment variable, terminal transcript, or retained output.
PostgreSQL uses local peer authentication and has no CAPLAB password file.

Key aliases include the campaign ID and use Garage's native expiry no later
than the authorization expiry. Every P4 key is also revoked at campaign
completion. `/opt/caplab/venvs` is `root:caplab` mode `0750`, giving the three
runtime identities read and execute access but no write access. The
hash-locked Python environment lives beneath it and contains `boto3` 1.34.46 and
`psycopg[binary]` 3.3.4 unless dependency locking or installation fails before
any namespace mutation. Execution uses that environment's Python with
`PYTHONNOUSERSITE=1` from a clean worktree at an exact Git commit and records
the interpreter, dependency-lock hash, commit, and dirty state.

Alternatives are a Go CLI, a resident service, a filesystem-only or SQLite
runtime, and no implementation. Go becomes preferable if distribution to
other hosts becomes a current requirement. A service becomes eligible only
when a standing caller needs concurrent remote access. Filesystem-only and
SQLite contradict the selected systems of record. No implementation is the
correct outcome if peer-role isolation, credential containment, dependency
locking, or the live-store gates cannot meet this proposal.

## Decision, owner, authority, and rationale

No option is selected while this ADR is `proposed`. The repository owner must
select, revise, or decline the complete proposal at its pushed Git identity.
Selection would decide the runtime shape; it would not itself execute or verify
the runtime.

## Authorization and execution scope

The following is the proposed authorization, not active authority.

Campaign ID: `caplab-p4-roundtrip-2026-07-15`.

Authorized checkpoint: CAPLAB-22 / P4 only. CAPLAB-23 / P5 and every later
checkpoint remain unauthorized.

Authorized executors and verifier:

- executor: the primary Codex agent in the owner-authorized thread, recorded
  in the P4 execution record;
- host delegate: the repository owner account exercising existing local sudo
  authority for only the named host effects; and
- verifier: a separate Codex agent named `caplab22_verifier`, barred from
  implementation edits and recorded in the P4 verification record.

Authorized repository effects:

- the `books` paths listed in the recommendation, on a branch descended from
  dashboard commit `e4636d2628adbbfca953734d4dc7cdfa91d72b04`;
- a new `proximal/caplab-runtime/**` subsystem, its root index entry, and its
  change log on an isolated Proximal branch; and
- sanitized Plane comments and state for CAPLAB-21 and CAPLAB-22.

Authorized host effects:

- create the four PostgreSQL roles, database `caplab`, schema `caplab_v0`, and
  migration-0001 objects named above;
- create the common system group `caplab`, the three same-named primary groups
  and nologin-shell OS identities, `/etc/caplab/**`, the isolated Python
  environment, and `/nvr/caplab/v0`; the NVR root is
  `caplab_writer:caplab` mode `0750`, so the reader and verifier receive only
  group read and execute access;
- create Garage bucket `caplab-v0`, enforce the selected quota, create only
  campaign-scoped writer, reader, and verifier keys, and place their secrets
  only in the named credential files;
- execute one model-free sealed synthetic-attempt round trip and independent
  retrieval, readback-hash, role-isolation, same-operation idempotence,
  conflicting-operation refusal before external effects, and reconciliation
  checks; and
- revoke the campaign keys, remove their credential files, set PostgreSQL roles
  `caplab_writer`, `caplab_reader`, and `caplab_verifier` to `NOLOGIN`, and
  lock their matching OS accounts at completion and no later than the
  authorization expiry. Definitions and retained state remain in place;
  re-enabling any role or account requires new owner authorization.

P4 does not authorize live S3 evidence-object deletion, synthetic application-row
deletion, source-loss simulation, or purge. If the round trip creates its first
synthetic S3 or NVR object or its first synthetic application row, the executor
emits a content-identified cleanup plan and leaves the exact state quarantined
for a separate P5 or cleanup decision. The owner must select P5, authorize
cleanup, or extend retention before the authorization expiry. The database,
schema, bucket, quota, OS identities, non-secret config, and runtime environment
may remain for the next owner decision if P4 passes. Empty bootstrap resources,
including migration objects and their migration ledger, may be removed only
before that first synthetic-object or synthetic-application-row boundary and
only when their ownership is unambiguous.

If selected, this decision also requires a conforming edit to P4's current
rollback sentence and CAPLAB-22's planning projection: pre-effect empty-resource
rollback and post-effect quarantine are distinct outcomes. This proposal does
not silently rewrite those records before owner selection.

The authorization would expire at `2026-07-22T23:59:59Z`. Before campaign
completion and no later than that instant, the host executor must revoke the
campaign keys, remove the credential files, set the three PostgreSQL peer roles
to `NOLOGIN`, and lock the three OS accounts. Any incomplete effect after
expiry stops and requires owner reconfirmation; later re-enablement requires
new authorization. It authorizes no
historical evidence inspection or movement, P5 fault or restore drill, raw
evidence retention, daemon, dashboard change, model call, inference, export,
training, publication, deployment, verification beyond P4, or CAPLAB
acceptance.

Stop before the first mutation if a target name already exists, the base branch
or governing ADRs drift, a dependency cannot be hash-locked, a credential would
enter an argument, environment variable, terminal transcript, or retained log,
the OS and PostgreSQL identities cannot be isolated, current PostgreSQL or
Garage health fails, `/nvr` ownership cannot be established safely, or
rollback cannot name every created effect. Stop during execution on a hash or
copy mismatch, a non-identical existing key, privilege escape, unexpected
external write, failed reconciliation, credential exposure, need for
historical evidence, need for live fault or collision injection, need for
object or row deletion, or any P5 operation.

Rollback before the first synthetic S3 or NVR object or first synthetic
application row may remove only newly created bootstrap resources, including
the empty bucket and the migration-only database and schema; it also revokes
campaign keys, removes secret files, disables the peer roles and OS accounts,
and records secret-free failure facts. After that boundary, rollback means
credential revocation, role and account disabling, a content-identified cleanup
plan, and quarantine until the owner grants cleanup or P5 authority. Neither
path deletes a live S3 evidence object or synthetic application row or rewrites
governing Git records, the dashboard, other PostgreSQL databases or roles,
other Garage buckets or keys, historical experiment material, backups, or
unrelated `/nvr` paths.

## Consequences and preservation boundaries

The selected runtime would provide one explicit model-free mutation path while
keeping the dashboard read-only. It would add PostgreSQL schema maintenance,
Garage key rotation, `/nvr` reconciliation, dependency locking, and synthetic
cleanup obligations.

Historical Study 001 bytes, timestamps, trial order, results, manifests,
claims, and retention state remain unchanged. P4 cannot create registered
historical evidence, a capability profile, a training candidate, or an
inference-bearing result. Plane remains a sanitized projection.

The proposal accepts Garage's single-host, replication-factor-one, non-WORM
boundary and the repository owner's shared-superuser boundary already selected
in ADR 0005. It does not convert application checks into a claim that Garage
itself prevents overwrite or purge.

## Verification and fitness criteria

The decision record is mechanically fit for owner review when its live facts,
names, paths, versions, links, and authority boundaries are checked; repository
documentation and full checks pass; and its branch is pushed without unrelated
changes.

If selected and authorized, P4 is verified separately when:

- hermetic fake-adapter tests cover canonical serialization, identity drift,
  duplicate and conflicting operation IDs, missing and changed bytes, locator
  substitution, overwrite and collision attempts, missing copies, role
  refusal, interrupted effects, and cleanup-plan generation without touching
  a live store;
- migration checks prove lexical ordering, filename and checksum identity,
  one-file transactions, advisory locking, repeatability, ownership, explicit
  grants, uniqueness, immutable-row protections, and checksum-drift refusal;
- one model-free sealed fixture reaches live Garage, `/nvr`, and PostgreSQL,
  then a separately credentialed reader retrieves matching bytes and hashes;
- against the live stores, same-operation replay is idempotent, a changed
  request is refused before an external effect, and no fault, collision,
  deletion, restore, or purge injection is performed;
- live reconciliation agrees across PostgreSQL, Garage, `/nvr`, the fixture
  manifest, migration identity, dependency-lock hash, and runtime commit;
- reader and verifier identities cannot mutate state, no secret appears in
  Git, Plane, process arguments, environment variables, terminal output, logs,
  or retained receipts, and before completion or expiry the campaign keys are
  revoked, the three peer roles are `NOLOGIN`, and their OS accounts are
  locked; and
- a separate verifier records the commands, versions, identities, outcomes,
  residual Garage permission limitation, failed restic-prune blocker for P5,
  quarantine or empty-resource rollback state, and any failed stop condition.

These checks verify P4 execution only. They do not verify restore, source-loss
recovery, purge, historical evidence admission, a scientific result, or CAPLAB
v0.

## Acceptance owner and outcome

The repository owner owns selection of this proposal and acceptance of any
later verified CAPLAB v0 result. No selection, P4 verification, or CAPLAB
acceptance has been recorded here.

## Reopening and supersession conditions

Reopen the runtime decision if P4 requires a resident service, the Python
dependency boundary proves disproportionate, PostgreSQL peer roles cannot meet
least privilege, Garage credential containment is insufficient, `/nvr` cannot
serve as an independent copy, current backups or store health fail, the 1 GiB
quota is insufficient, or dashboard and runtime packages cannot remain
independent.

A change to systems of record, residency, retention, recovery targets, or
public disclosure requires reopening ADR 0005. A change confined to runtime
implementation details may supersede this ADR without changing ADR 0005.

## Doctrine record

The Pincite gate passed on 2026-07-15, but its checkout was ahead of its remote
and materially dirty. Under the Doctrine skill, no doctrine packet was
retrieved and no doctrine-backed recommendation is made here. This proposal is
based on accepted CAPLAB records and the live read-only evidence named above.

## Related artifacts

- Product boundary: [`adr-0002`](adr-0002-agent-capability-lab-v0.md)
- Study selection: [`adr-0004`](adr-0004-caplab-study-001-selection.md)
- Evidence governance: [`adr-0005`](adr-0005-caplab-v0-evidence-governance.md)
- Capability-card selection: [`adr-0006`](adr-0006-caplab-study-001-capability-card-selection.md)
- Product specification:
  [`spec-agent-capability-lab`](../product/specs/spec-agent-capability-lab.md)
- Implementation plan:
  [`plan-agent-capability-lab-v0`](../product/plans/plan-agent-capability-lab-v0.md)
- Planning projection: local Plane work item `CAPLAB-21`

## Status history

- `2026-07-15` — `proposed` — the owner authorized CAPLAB-21 discovery and
  proposal preparation; runtime selection and P4 authorization remain pending
  owner review of this exact proposal.
