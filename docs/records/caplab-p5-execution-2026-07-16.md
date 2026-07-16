# CAPLAB-23/P5 execution record

Status: **stopped and quarantined** on 2026-07-16. P5 did not complete.
Independent verification is a separate record. CAPLAB acceptance was not
performed.

## Authority and boundary

**Decision:** ADR 0009 selected campaign
`caplab-p5-recovery-2026-07-16` for CAPLAB-23/P5 only.

**Authorization:** the repository owner instructed the primary Codex agent to
`authorize ADR 0009 as written` and execute the next Plane items in order. The
authorization expires at `2026-07-23T23:59:59Z`. The primary agent `/root` was
the executor. The separate agent `/root/caplab_p5_independent_verifier` was
assigned before the first host effect and did not participate in execution.

No historical Study 001 evidence was inspected or admitted. No model call,
training, export, acceptance, CAPLAB-24/P6, CAPLAB-25/P7, or Striatum effect was
authorized or performed.

## Frozen implementation and identity

| Surface | Frozen identity |
|---|---|
| Standalone CAPLAB | `c82b5512661c537db06f725af70198eccc818358` |
| Final Proximal host surface | `0263aff7bc3bf34bff28be008fa9f370a7065ed4` |
| Proximal `caplab-p5` archive | `3ba204dbe1e1bf57b3c8e2b37e8b2162dd65c019f62c36f74e758541745afa9e` |
| Requirements lock | `b5c05b76c4e383b9bdedb783ed658fe33c368d660a1efe45f80c98e0f8adb3a0` |
| Migration `0001` | `7e075ccb2263f7926fa6b221d46ea908aba6f51a54aee412703657665ca3533b` |
| Migration `0002` | `c3c69be60c33d56c70eb4a02f273f13b95da778c14c079cdf447772a94a0eb2b` |
| Synthetic fixture | `f752cd891f0c52bc1a30153c2a223875bd321e0ae24b2b9a7dd28d404a6a3e4f` |
| Synthetic payload/content | `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d` |
| Authorization document | `e8cd172af19cb631ba6814a3fd57c7b91f381cd799de862d9bd277b6ef68d34f` |
| Verifier assignment | `55f1d80f7145b030fd161e306551d2953f918dc5089eed289bdbaaf12b77aee8` |

The P5 operation is `op-p5-recovery-0001`. Its request SHA-256 is
`4164a5d4febd4f429158d5917a15ae303392ecf1d9d6a57e84ae9a731282b229`,
its object and local-copy key is
`objects/sha256/a1/a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`,
and its manifest SHA-256 is
`77acb678e5fa2d99374ba5a2e5841a043d904333a7718612fd3b0153a057f1b4`.

The selected pre-effect rollback backup is
`20260712-010203F_20260716-013021D`. The isolated restore target was frozen as
`/var/tmp/caplab-p5-pgrestore` on loopback port `55435`; the campaign stopped
before creating that restore.

## Preconditions

**Observation:** standalone CAPLAB was clean at the frozen commit. Its full
gate passed with 68 tests and three gated integration skips. Separately enabled
ephemeral PostgreSQL integration tests passed.

**Observation:** the final Proximal surface passed 12 repository tests, Ruff,
Python format, shell syntax, and diff hygiene. Its branch was pushed to
`origin/agent/caplab-p5-recovery`.

**Observation:** the daily Restic backup completed successfully on 2026-07-16.
The monthly prune unit retained its 2026-07-01 failure. The installed drop-ins
serialize backup, forget, prune, and check on one blocking lock. No manual prune
was authorized or run.

**Observation:** P4 began disabled. Its database registration, Garage object,
and `/nvr` copy were captured before P5 data effects. Both byte copies had
SHA-256
`87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`.

## Stopped pre-registration attempts

Four execution roots stopped before P5 registration:

1. `/var/tmp/caplab-p5-execution.20260716T184952Z` stopped because root Git did
   not trust the exact user-owned CAPLAB checkout. No bootstrap occurred.
2. `/var/tmp/caplab-p5-execution.20260716T185245Z` stopped because the
   executor's restrictive umask masked group traversal on installed config and
   source trees. Automatic disablement ran; the empty temporary users and roles
   were removed.
3. `/var/tmp/caplab-p5-execution.20260716T185843Z` reached ready state and
   applied migration `0002`, but verifier inventory refused a named ACL that
   changed the shared local-copy directory's effective mode. No P5 operation or
   bytes existed. Access was disabled and the shared directory contract was
   restored.
4. `/var/tmp/caplab-p5-execution.20260716T190335Z` stopped in disabled-retry
   preflight because the frozen P4 controller correctly rejected P5-added roles
   and schema objects as outside its P4 matrix. No bootstrap occurred.

Each cause was observed before P5 registration. Each bounded correction was
committed and independently reviewed before a new freeze. The final host
surface uses exact-checkout Git trust, explicit group-traversable installed
trees, PostgreSQL boolean-text verification, an exact operator-owned `a1`
local-copy prefix, and a retry path limited to disabled zero-P5-data state.

## Final execution observations

The final root is
`/var/tmp/caplab-p5-execution.20260716T190544Z`.

| Checkpoint | Observation |
|---|---|
| Host readiness | Disabled-retry preflight, bootstrap, migration, temporary credential issue, expiry timer, peer-role checks, and ready verification passed. |
| Empty inventory | Verifier inventory reported no incomplete request, unreferenced object, unreferenced copy, dependency, or tombstone. |
| Wrong role | Verifier registration returned structured `ConfigurationError` with direct status `2`. |
| Invalid/ambiguous | Two separately typed observations were inserted with dispositions `invalid` and `ambiguous`; neither contains subject-outcome fields. |
| Controlled interruption | Registration interrupted after the local copy was verified and returned structured `InjectedInterruption` with direct status `4`. |
| Orphan inventory | Inventory reported the exact operation as incomplete and the exact object and copy as unreferenced. |
| Incomplete verification | Verifier returned direct status `2` because the frozen operation was not registered. |
| Changed request | A non-identical payload was refused as differing from the frozen P5 identity with direct status `2`. |
| Duplicate interrupted replay | The identical request reused both retained byte copies and again returned the selected interruption with direct status `4`. |
| Final replay | PostgreSQL finalization completed, then runtime validation returned direct status `2` with `MetadataMismatch: migration runtime commit differs from provenance`. |
| Subsequent calls | Duplicate registration and verifier calls returned the same provenance refusal. Inventory nevertheless showed a complete registration and no orphan state. |

Direct store receipts at stop show both P5 byte copies contain 98 bytes and
match the frozen content SHA-256. PostgreSQL contains the exact P5 operation,
request, registration, manifest, and identity closure.

## Stop condition and inference

**Observation:** the live migration ledger contains:

- `0001_runtime_core.sql`, applied by the P4 source commit
  `405efb136b221d1270578417c64b3f7878383f32`; and
- `0002_p5_recovery_custody.sql`, applied by the P5 source commit
  `c82b5512661c537db06f725af70198eccc818358`.

Both migration file hashes match the frozen provenance. The P5 manifest
correctly names the current runtime commit and both file hashes.

**Inference:** the direct cause is the validation rule in
`RegistrationService._validate_record` that requires every applied migration
row's `runtime_commit` to equal the current P5 runtime commit. That rule rejects
the legitimate forward-only ledger whose first migration was applied by P4.
Byte corruption, locator substitution, and migration checksum drift are
credible rivals contradicted by the retained hashes and identities.

This post-effect mismatch triggered ADR 0009's stop condition. The executor did
not patch the frozen runtime or continue into source-loss recovery, Restic
check, post-registration pgBackRest backup, isolated restore, dependency
rehearsal, byte deletion, guarded purge, or tombstone creation.

## Quarantine and remaining state

The executor emitted and preserved the exact non-applying cleanup plan, then:

- deleted both temporary Garage keys and credential files;
- changed the P5 operator and verifier database roles to `NOLOGIN`;
- disabled the two P5 operating-system identities;
- disabled the P5 expiry timer;
- returned the exact `a1` prefix to root custody;
- verified host phase `disabled`; and
- rechecked the unchanged P4 database and local-copy identities.

The exact P5 database registration, Garage object, and `/nvr` copy remain
quarantined and mutually content-identical. No custody request or purge
tombstone exists. Migration `0002`, the `NOLOGIN` custodian and temporary
database roles, the disabled operating-system identities, installed source,
cleanup plan, and evidence roots remain.

Source correction and a newly frozen owner-authorized campaign are required
before another P5 live effect. This record is not authorization to repair,
resume, or purge the quarantined registration.

## Evidence manifests

All five root-only manifests verified with `sha256sum -c`:

| Execution root suffix | `SHA256SUMS` SHA-256 |
|---|---|
| `20260716T184952Z` | `3b06e1db6588b62cb77ce2afd004a639b9d29cd99f1dc172078a3cb9a3e43900` |
| `20260716T185245Z` | `db6b8aeed897b3e04306ba90b7b4c6623ccce8866d5082671a791910ed813999` |
| `20260716T185843Z` | `2d633326d83bb7c000c8ccefe3fb1d4e70667195c9cc13b5ed78b4b08ec5570b` |
| `20260716T190335Z` | `c8c9393661f5d3b7485048d7192d30ff4a423056fa98b4b910e8407751bce30b` |
| `20260716T190544Z` | `2c25fd8a5a99a6c975562c16c9b482dc3f3316fa9da52de57707994fc622237f` |

Independent verification may confirm or reject this execution record. It
cannot accept CAPLAB or authorize P6.
