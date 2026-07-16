# CAPLAB-23/P5 corrective execution record

Status: **stopped and quarantined** on 2026-07-16. The corrective campaign did
not complete P5. Independent verification is a separate record. CAPLAB
acceptance was not performed.

## Authority and boundary

**Decision:** ADR 0010 selected corrective campaign
`caplab-p5-corrective-2026-07-16` after the independently verified failure of
the original P5 campaign.

**Authorization:** after receiving the P5 FAIL and the stated requirement for
a newly frozen owner-authorized corrective campaign, the repository owner
instructed the executor to `proceed`. ADR 0010 limits that authorization to the
registration-validation correction and the remaining ADR 0009 P5 effects
through `2026-07-23T23:59:59Z`.

The executor was `/root`. The fresh agent
`/root/caplab_p5_corrective_verifier` was assigned before the first corrective
host effect. The assignment SHA-256 is
`cd80ad187089d18af91b189fe51f47b77133efba831fd26498649171ff37b2bc`.

No historical evidence admission, model call, training, export, acceptance,
CAPLAB-24/P6, CAPLAB-25/P7, or Striatum effect was authorized or performed.

## Frozen correction and identity

| Surface | Frozen identity |
|---|---|
| Corrected CAPLAB commit | `e86ed0ecd734b902be2afcd0d20d5a07225c2579` |
| Corrected CAPLAB tree | `4e7ff88eb6fc657b95a5e53c138e9536806d708b` |
| Proximal corrective host commit | `f4f261e23b66f0f467ea0f962a9daf905ae4106f` |
| Proximal corrective host tree | `139acb73af2abb3f1a265ac97a207b18a6587884` |
| Registered runtime commit | `c82b5512661c537db06f725af70198eccc818358` |
| ADR 0009 | `e8cd172af19cb631ba6814a3fd57c7b91f381cd799de862d9bd277b6ef68d34f` |
| ADR 0010 | `0b0682acaa749f7715687e10f3c0565f0776da951375d9f3fb5ed329c94e2b9a` |
| Pre-effect freeze | `38c50b81be99312a45f257ab4602dbad63e62aec8a0ca2b554b6225a5b5f2db1` |

The original data identity was unchanged: operation
`op-p5-recovery-0001`, request SHA-256
`4164a5d4febd4f429158d5917a15ae303392ecf1d9d6a57e84ae9a731282b229`,
content SHA-256
`a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`,
object and local-copy key
`objects/sha256/a1/a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`,
and manifest SHA-256
`77acb678e5fa2d99374ba5a2e5841a043d904333a7718612fd3b0153a057f1b4`.

The P5 payload and quarantined P5 copy are 115 bytes. The original execution
record's 98-byte P5 statement confused that payload with the 98-byte P4
control. The content hashes in the original evidence remain correct; the
failed root was not rewritten.

## Validation correction

**Observation:** a production-path regression reproduced
`MetadataMismatch: migration runtime commit differs from provenance` when
migration `0001` retained its P4 applied-by commit and migration `0002`
retained its P5 applied-by commit.

**Execution:** registration validation now requires every migration-ledger
`runtime_commit` to be a canonical lowercase 40-character Git identity without
requiring every historical applied-by commit to equal the current
registration's runtime provenance. Reconciliation still compares the expected
current runtime provenance and fails on current-runtime drift.

The repository gate passed with 70 tests and three gated skips. Separately
enabled PostgreSQL integration tests passed.

## Corrective live observations

The corrective execution root is
`/var/tmp/caplab-p5-execution.20260716T195028Z`.

| Checkpoint | Observation |
|---|---|
| Disabled retry | The corrected host surface accepted only the exact disabled quarantine tuple and unchanged content hash. |
| Bootstrap | Temporary identities and credentials were recreated, migration replay was idempotent, and host phase `ready` verified. |
| Registration replay | The exact original request returned `idempotent_replay: true`. |
| Reconciliation | Object, local copy, metadata, locator, and provenance all returned `match`. |
| Missing Garage object | Verification returned typed `ObjectMismatch` with status `2`; restore from `/nvr` and reconciliation passed. |
| Altered Garage object | Verification returned typed `ObjectMismatch` with status `2`; restore from `/nvr` and reconciliation passed. |
| Missing `/nvr` copy | The exact copy was atomically moved to a root-custodied recovery directory on the same filesystem. Verification returned typed `CopyMismatch` with status `2`; restore from Garage and reconciliation passed. |
| Altered `/nvr` copy | Verification returned typed `CopyMismatch` with status `2`; restore from Garage and reconciliation passed. |
| Restic | The first direct invocation refused before repository access because it lacked the systemd environment. The rerun loaded `/etc/restic/proximal.env` without exposing credentials and the non-destructive check completed under the shared lock. |
| pgBackRest backup | Differential backup `20260712-010203F_20260716-195901D` completed successfully. |

One attempted altered-object command returned `PermissionError` before
mutation because its non-sensitive input was root-only. The executor preserved
the status-2 receipt, verified that the object remained good, restaged only the
altered input with group-read custody, and then completed the selected altered
object drill.

## Isolated-restore stop

**Observation:** pgBackRest restored backup
`20260712-010203F_20260716-195901D` successfully into
`/var/tmp/caplab-p5-pgrestore`, including 45.4 GB across 11,608 files and
`global/pg_control`.

**Observation:** the frozen helper then failed to start the isolated server:

```text
postgres: could not access the server configuration file
"/var/tmp/caplab-p5-pgrestore/postgresql.conf": No such file or directory
```

The direct return code is `1` in receipt
`031-restore-post-registration-backup-isolated`. Debian stores this cluster's
configuration outside the data directory. The live PostgreSQL cluster
remained active and was neither stopped nor redirected. The isolated server
never started and has no `postmaster.pid`.

**Inference:** the backup data restore succeeded, but the mandatory isolated
database verification is unsupported. The helper encoded an invalid
configuration-location assumption. A further restore defect remains a
credible rival until a newly frozen helper starts and verifies an isolated
cluster.

ADR 0010 names isolated-restore failure as a stop condition. The executor did
not repair the helper after freeze and did not continue into dependency
refusal, byte deletion, guarded database purge, tombstone creation, or final
absence.

## Quarantine

The executor generated and preserved a non-applying cleanup plan, then:

- revoked both P5 Garage keys and removed credential files;
- set the P5 operator and verifier database roles to `NOLOGIN`;
- disabled the P5 operating-system identities;
- disabled the P5 expiry timer;
- verified P5 host phase `disabled`;
- preserved matching good P5 object and local-copy bytes in root custody;
- retained one P5 operation request and registration with zero custody
  requests and zero tombstones; and
- preserved the stopped isolated restore target without starting it.

The P4 registration and 98-byte `/nvr` copy retain their frozen identities.
The older P4 host controller's broad `rolname LIKE 'caplab%'` verifier rejects
the authorized P5 roles introduced by migration `0002`; direct P4 role
evidence shows the four P4 roles retain their frozen attributes and `NOLOGIN`
state.

## Evidence

The corrective executor manifest is
`/var/tmp/caplab-p5-execution.20260716T195028Z/EXECUTOR_SHA256SUMS`. It verified
with `sha256sum -c`; its SHA-256 is
`fecd175753adf3df7db743534fd2c3b6d8732166790a4c4a8f0d099ea40dc594`.
The independent verification report has SHA-256
`b824bec1a6a2192555a8b3927928c0847bea5b04d9efab0d3041c9f80a6be87c`.
After preserving that report, the executor generated and verified the final
corrective-root `SHA256SUMS`; its SHA-256 is
`ded324dc5063be625de293ee915b9bbdb80db314c70890a2bedfde5b4a439070`.

The original failed execution root remains separate at
`/var/tmp/caplab-p5-execution.20260716T190544Z`; its verified `SHA256SUMS`
SHA-256 remains
`2c25fd8a5a99a6c975562c16c9b482dc3f3316fa9da52de57707994fc622237f`.

The fresh verifier returned **FAIL** in
[`caplab-p5-corrective-verification-2026-07-16.md`](caplab-p5-corrective-verification-2026-07-16.md).
That verification cannot accept CAPLAB or authorize P6.
