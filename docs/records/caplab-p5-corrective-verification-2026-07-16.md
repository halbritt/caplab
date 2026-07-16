# CAPLAB-23/P5 corrective independent verification

Result: **FAIL** for CAPLAB-23/P5.

Verification completed at `2026-07-16T20:09:21Z` by the fresh independent
verifier `/root/caplab_p5_corrective_verifier`.

This verification assesses the original campaign
`caplab-p5-recovery-2026-07-16` and corrective campaign
`caplab-p5-corrective-2026-07-16` together against ADR 0009, ADR 0010, and the
frozen verifier assignment. It is not CAPLAB acceptance and grants no
authority for CAPLAB-24/P6, CAPLAB-25/P7, historical-evidence admission, model
calls, training, export, or publication.

## Frozen authority and identities

The verifier independently confirmed:

- verifier-assignment SHA-256:
  `cd80ad187089d18af91b189fe51f47b77133efba831fd26498649171ff37b2bc`;
- ADR 0009 SHA-256:
  `e8cd172af19cb631ba6814a3fd57c7b91f381cd799de862d9bd277b6ef68d34f`;
- ADR 0010 SHA-256:
  `0b0682acaa749f7715687e10f3c0565f0776da951375d9f3fb5ed329c94e2b9a`;
- corrected CAPLAB commit and tree:
  `e86ed0ecd734b902be2afcd0d20d5a07225c2579`,
  `4e7ff88eb6fc657b95a5e53c138e9536806d708b`;
- Proximal P5 host-surface commit and tree:
  `f4f261e23b66f0f467ea0f962a9daf905ae4106f`,
  `139acb73af2abb3f1a265ac97a207b18a6587884`;
- registered runtime commit:
  `c82b5512661c537db06f725af70198eccc818358`;
- operation:
  `op-p5-recovery-0001`;
- request SHA-256:
  `4164a5d4febd4f429158d5917a15ae303392ecf1d9d6a57e84ae9a731282b229`;
- content SHA-256:
  `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`;
- manifest SHA-256:
  `77acb678e5fa2d99374ba5a2e5841a043d904333a7718612fd3b0153a057f1b4`;
  and
- exact object and local-copy key:
  `objects/sha256/a1/a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`.

The authorization remains within its recorded expiry of
`2026-07-23T23:59:59Z`.

## Evidence integrity

**Observation:** the original failed root
`/var/tmp/caplab-p5-execution.20260716T190544Z` retains `SHA256SUMS` with
SHA-256
`2c25fd8a5a99a6c975562c16c9b482dc3f3316fa9da52de57707994fc622237f`.
An independent `sha256sum -c SHA256SUMS` verified every listed artifact.

**Observation:** the separate corrective root
`/var/tmp/caplab-p5-execution.20260716T195028Z` retains
`EXECUTOR_SHA256SUMS` with SHA-256
`fecd175753adf3df7db743534fd2c3b6d8732166790a4c4a8f0d099ea40dc594`.
An independent `sha256sum -c EXECUTOR_SHA256SUMS` verified every listed
artifact.

**Observation:** the assignment and corrective quarantine-stop files are
byte-identical between their `/tmp` and corrective-root copies. The original
independent verification remains present with SHA-256
`32c8c05a9fba805a422e9b6196d0bbf61e8a20c6552d7f7be950696bac2ace48`.
The two campaign roots remain distinct.

## Corrective criteria supported

### Registration replay and reconciliation

**Observation:** exact registration replay returned direct status `0`,
`idempotent_replay: true`, and the frozen operation, request, content,
manifest, locator, and identity-layer hashes.

**Observation:** corrected verification returned direct status `0` with
object, local-copy, metadata, locator, and provenance statuses all `match`.
Inventory then contained no incomplete request, unreferenced object,
unreferenced copy, dependency, or tombstone.

### Garage recovery

**Observation:** after exact-byte staging, removal of the P5 Garage object
returned direct status `0`. Verification returned direct status `2` with
typed `ObjectMismatch`. Restore from `/nvr` returned direct status `0`, and
subsequent reconciliation returned all-match status.

**Observation:** an initial altered-input attempt returned a read-permission
error before changing the object. The executor verified that the good object
was unchanged, staged the same altered bytes through a readable non-secret
path, replaced the object, received typed `ObjectMismatch` with direct status
`2`, restored from `/nvr`, and reconciled successfully.

### `/nvr` recovery

**Observation:** the exact P5 local copy was atomically staged and removed.
Verification returned direct status `2` with typed `CopyMismatch`. Restore
from Garage returned direct status `0`, followed by successful reconciliation.

**Observation:** replacement with altered local bytes returned direct status
`0`; verification returned direct status `2` with typed `CopyMismatch`;
restore from Garage and subsequent reconciliation returned direct status `0`.

### Restic lock and check

**Observation:** the installed backup and prune units route through the frozen
shared-lock wrappers. Their live hashes match the pre-effect freeze.

**Observation:** the first manual check invocation returned status `1`
because it lacked the unit's repository environment. The preserved retry
loaded the installed unit environment and invoked the same locked,
non-destructive check wrapper. It returned direct status `0`, checked all
packs and 13 snapshots, and reported no errors.

### Post-registration backup

**Observation:** pgBackRest created differential backup
`20260712-010203F_20260716-195901D` with direct status `0`. The post-stop
catalog contains that exact successful backup and reports repository status
`ok`.

## Mandatory isolated-restore failure

**Observation:** pgBackRest restored backup
`20260712-010203F_20260716-195901D` into
`/var/tmp/caplab-p5-pgrestore`, reporting a 45.4 GB restored data directory,
11,608 files, and successful restoration of `global/pg_control`.

**Observation:** the isolated PostgreSQL server did not start. The frozen
helper invoked PostgreSQL against the restored data directory without an
external Debian PostgreSQL configuration. The server reported:

`could not access the server configuration file
"/var/tmp/caplab-p5-pgrestore/postgresql.conf": No such file or directory`

The direct receipt
`031-restore-post-registration-backup-isolated.rc` is `1`.

**Observation:** because the isolated server never became queryable, there is
no verification of the restored migration ledger, P4 control, P5
registration, manifests, or content identities.

**Inference:** the observed startup failure is consistent with the helper
assuming that `postgresql.conf` resides in the restored Debian data
directory. A separate restore defect remains a credible rival and cannot be
excluded without a newly frozen helper and another isolated restore.

## Final live read-only observations

### Quarantined P5 state

**Observation:** the live CAPLAB database contains the exact P5 operation and
registration with the frozen request, content, object, local-copy, manifest,
and seven identity-layer hashes. Counts are:

`1 operation request | 1 registration | 0 custody requests | 0 purge tombstones`

**Observation:** the live P5 `/nvr` copy is 115 bytes and has SHA-256
`a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`.
The root-staged Garage and local-copy recovery files and the `/nvr` recovery
staging file have that same SHA-256.

**Observation:** Garage reports two objects totaling 213 bytes in bucket
`caplab-v0`, matching the preserved 98-byte P4 and 115-byte P5 population. No
P5 Garage access key remains available to this verifier for an independent S3
content read. The corrective receipts preserve successful P5 reconciliation
immediately before disablement.

### Access disablement

**Observation:** `/usr/local/libexec/caplab-p5-hostctl verify --phase
disabled` passes. The live lifecycle state is byte-identical to
`disabled-corrective-state.json`, SHA-256
`239f18af3b288f6d42d8ae1d357ff5f5b045849026d9ac201b783944184429b5`.

**Observation:** no credential directory exists. Garage key inventory contains
no P5 campaign aliases. PostgreSQL roles `caplab_p5_operator`,
`caplab_p5_verifier`, and `caplab_custodian` are `NOLOGIN` and have no
password. The two P5 operating-system accounts are locked, expired, use
`/usr/sbin/nologin`, and own no observed process. The expiry timer is disabled
and inactive.

**Observation:** the shared local-copy directory remains
`caplab_writer:caplab` mode `0750` without a named ACL. The exact P5 `a1`
prefix remains `root:caplab` mode `0750`.

### Isolated restore residue

**Observation:** `/var/tmp/caplab-p5-pgrestore` remains present under
`postgres:postgres` custody. It contains restored `PG_VERSION`,
`global/pg_control`, and `postgresql.auto.conf`; `postgresql.conf` and
`postmaster.pid` are absent. No process is listening on loopback port `55435`.
The live PostgreSQL 17 cluster remains active and running.

### P4 control

**Observation:** the live P4 registration retains its frozen operation,
campaign, request, content, locator, manifest, and identity-layer values.

**Observation:** the P4 `/nvr` copy remains 98 bytes with SHA-256
`87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`.
The four P4 PostgreSQL roles retain the recorded `NOLOGIN` attributes. Garage
bucket size and object count remain consistent with the unchanged P4 and
retained P5 objects.

One executor receipt, `043-p5-database-quarantine-after-stop`, returned status
`1` after querying a nonexistent migration-ledger column. The immediately
following corrected receipt `044-p5-database-and-ledger-after-stop` returned
status `0` and independently exposed the expected P5 counts and both frozen
migration filename, file-hash, and applied-by commit tuples.

## Mandatory unmet or contradicted criteria

1. The restored database was never started or queried, so restored migration,
   P4, P5, manifest, and content identity verification is unsupported.
2. The isolated restore remains present instead of being removed after
   preserved successful verification.
3. The dependency-bearing purge refusal was not executed and has no numeric
   status receipt.
4. Exact-byte staged deletion and guarded database purge were not executed.
5. No purge tombstone exists.
6. Final P5 absence is contradicted by the retained P5 database closure and
   live `/nvr` copy; Garage also retains the two-object 213-byte bucket
   population.

## Verification result

**FAIL for CAPLAB-23/P5.** The original and corrective evidence together now
support corrected idempotent replay, reconciliation, all four source-loss
recovery drills, the shared-lock Restic check, a successful exact
post-registration pgBackRest backup, safe access disablement, and unchanged P4
control. They do not support the mandatory isolated restored-database
verification, dependency refusal, guarded purge, tombstone, isolated-restore
removal, or final P5 absence criteria.

The executor correctly stopped under ADR 0010, retained the failed restore for
inspection, restored disabled quarantine, preserved good P5 bytes and both
evidence roots, and did not continue into purge. Those safe stop actions do not
convert the partial campaign into a P5 pass.

I explicitly refuse to accept CAPLAB or authorize CAPLAB-24/P6.
