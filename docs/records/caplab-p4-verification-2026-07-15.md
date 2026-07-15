# CAPLAB-22/P4 independent verification record

Result: **PASS**. Verification completed at `2026-07-15T22:49:40Z` by the
separate Codex agent `caplab22_verifier`. This verifies only the model-free
CAPLAB-22/P4 execution for campaign `caplab-p4-roundtrip-2026-07-15`. It is not
CAPLAB acceptance and grants no authority for P5, cleanup, deletion, evidence
admission, model calls, training, or publication.

## Frozen criteria and evidence

The verifier compared actual host state and preserved execution artifacts with
ADR 0007 at standalone CAPLAB commit
`405efb136b221d1270578417c64b3f7878383f32`. The installed Proximal host
surface is commit `e3997d7357b66ff9085570a86a16c6ebdfdedb60`.

The preserved execution root is
`/var/tmp/caplab-p4-execution.UGtXUE0D`. All 32 entries in `SHA256SUMS`
verified. The manifest-file SHA-256 is
`d72e7fdc5567afc8b4f949c10175b429acc05ab557a9dd19de4ebfa622807993`.
The retained `final-state.json` and the live root-only lifecycle record are
byte-identical, with SHA-256
`25bde991aa8b6bc89598840d6700895578e866d1bc0957b978d6d2e298572fcc`.

The live lifecycle record has `effects_armed: true`, phase `disabled`, and
complete results for all 15 disable operations. Preserved receipts show the
base, ready, armed, and disabled host checks passed in that order.
`/usr/local/libexec/caplab-hostctl verify --phase disabled` also passed during
this independent verification.

## Store and runtime observations

### PostgreSQL

PostgreSQL reports version 17.10. Direct catalog queries found:

- `caplab_owner`, `caplab_writer`, `caplab_reader`, and `caplab_verifier` are
  all `NOLOGIN`, non-superuser, `NOINHERIT`, and without create-role,
  create-database, replication, or row-security-bypass authority;
- no connection to database `caplab` and no session owned by a `caplab_*` role
  was present;
- the application inventory contains one row in each of
  `administrations`, `agent_configurations`, `artifacts`,
  `attempt_artifacts`, `attempts`, `manifests`, `model_identities`,
  `operation_requests`, `registrations`, `trial_assignments`, and
  `trial_contexts`;
- operation `op-caplab-p4-roundtrip-0001` has exactly four events, in order:
  `requested`, `object-verified`, `local-copy-verified`, and `registered`;
- exactly one audit event exists, `registration-completed`, and it binds
  content SHA-256
  `87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`
  to manifest SHA-256
  `64c74d6a498039aef44c791c2e7f80d15c82bfa4e30cf7c30658ef5fcd6e301f`;
- exactly one registration and one operation request exist; and
- the sole migration row binds `0001_runtime_core.sql` SHA-256
  `7e075ccb2263f7926fa6b221d46ea908aba6f51a54aee412703657665ca3533b`
  to runtime commit `405efb136b221d1270578417c64b3f7878383f32`.

The registration-integrity and reconciliation projections bind the canonical
Garage and local-copy key, report 98 bytes, and report both locator checks
true.

### Garage and `/nvr`

Garage 2.3.0 reports bucket `caplab-v0` with its frozen 1 GiB and 10,000-object
quotas, exactly one 98-byte object, and no key grants. The global key inventory
contains none of the three campaign aliases or recorded access-key IDs.
`garage bucket inspect-object` found the retained object at the exact key
`objects/sha256/87/87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`;
it is complete, not aborted, and not a delete marker. Its ETag
`3ac5a04534a7f3953f03404abb4f14b6` matches the MD5 of both the pinned source
fixture and the retained `/nvr` file.

The ZFS-mounted `/nvr` namespace contains exactly that one 98-byte file. Its
SHA-256 is
`87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`,
and a byte comparison with the pinned synthetic payload succeeded. The file is
`caplab_writer:caplab` mode `0440`; its content-addressed directory chain is
mode `0750`.

### Identities, credentials, expiry, and source pins

The three credential directories remain, but contain no credential files. The
three OS accounts use `/usr/sbin/nologin`, are password-locked, expired at day
1, and own no process. The expiry timer is enabled and active, with its next
trigger at `2026-07-22T23:50:00Z`. The installed service and timer bytes match
the Proximal commit.

The installed host controller, source pin, and runtime configuration match the
Proximal Git blobs. The installed CAPLAB source manifest has SHA-256
`3f45560bc4bd5a7db7cace5a377eb4d3dad63524a3f6f53451c74e512d1fa0db`;
all 24 manifest entries match both the installed files and their Git blobs at
the frozen CAPLAB commit. The installed requirements lock has SHA-256
`b5c05b76c4e383b9bdedb783ed658fe33c368d660a1efe45f80c98e0f8adb3a0`.
The isolated runtime reports Python 3.12.3, boto3 1.34.46, botocore 1.34.46,
and psycopg 3.3.4.

## Round-trip and quarantine observations

The pre-effect inventory contains no application row, Garage object, or
`/nvr` file. The after-first-registration inventory contains the exact live
inventory described above. The after-replay and after-conflict inventories
are identical to the first-registration inventory. The first and replay
receipts share every durable identity; only the replay receipt has
`idempotent_replay: true`. The changed request emitted a structured
`OperationConflict` refusal. Reader and verifier registration attempts emitted
structured `ConfigurationError` role refusals and no stdout.

The preserved reader receipt and hash record bind the retrieved bytes to the
payload SHA-256. The preserved verifier reconciliation reports object, local
copy, metadata, locator, and provenance status `match`, with `ok: true`.

The cleanup plan's canonical body independently recomputes to plan SHA-256
`f096690374e2338befec7b6365e95983b71a429e3533462a1d666b41ebf253af`.
It authorizes no deletion, names the exact retained object, copy, manifest, and
operation, and leaves them in `quarantine-required` state. No P5 or cleanup
effect was observed.

## Numeric-status preservation gap

**Observation:** the reader, verifier, and changed-request stderr artifacts
preserve their structured refusal types, and the verifier-owned post-refusal
inventories preserve no added effect. The frozen CLI maps both
`ConfigurationError` and `OperationConflict` to status 2.

**Observation:** the three numeric exit values themselves were tested by the
live shell but were not written to separate retained receipts.

**Inference:** the error types, frozen status mapping, subsequent successful
shell guards, and unchanged inventories support the reported status-2
outcomes. They do not turn the missing numeric receipts into directly observed
values. This preservation gap does not defeat the P4 semantic criteria of
role refusal, conflict refusal before added external effect, and unchanged
store inventory, so the verification result remains PASS. Any later claim
that needs the historical numeric values as primary evidence must treat them
as unavailable rather than independently verified.

## Residual limits and result

**Observation:** Garage exposes read, write, and owner bucket grants, not a
separate append-without-delete grant. The runtime exposes no delete command and
the campaign credentials are revoked.

**Inference:** the active writer's required Garage write grant was
delete-capable. Revocation and application checks contain that risk; they do
not make the retained object WORM or prevent an out-of-band administrator from
changing it.

`restic-prune.service` remains failed with result `exit-code` and status 1 from
2026-07-01. This remains a P5 backup-lifecycle blocker. P4 supplied no restore,
source-loss, deletion, purge, or retention-lifecycle verification.

**Verification result:** PASS for CAPLAB-22/P4 only. All frozen P4 technical
criteria observable after the authorized round trip are satisfied, with the
numeric-status preservation gap bounded above. No remaining failed P4
criterion was found. Acceptance remains unperformed and belongs to its separately
authorized owner.
