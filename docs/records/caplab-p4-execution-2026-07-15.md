# CAPLAB-22/P4 execution record

Status: executed and quarantined on 2026-07-15. Independent verification is a
separate record. Acceptance was not performed.

## Authority and boundary

**Decision:** ADR 0007 selected campaign
`caplab-p4-roundtrip-2026-07-15`, and ADR 0008 placed its product authority in
this standalone repository.

**Authorization:** the repository owner selected ADR 0007 at `halbritt/books`
commit `cdbb5120d1d450763fca2a8aca172f6308413440`, authorized only
CAPLAB-22/P4 through `2026-07-22T23:59:59Z`, and delegated CAPLAB decisions for
that bounded work to the primary agent. The primary Codex agent was the
executor; the repository-owner account supplied existing local sudo authority.

No P5 fault, restore, source-loss, deletion, or purge operation was authorized
or executed. No historical evidence was inspected or admitted. No model call,
training use, public result publication, or CAPLAB acceptance occurred.

## Frozen implementation

| Surface | Identity |
|---|---|
| Standalone CAPLAB runtime | `405efb136b221d1270578417c64b3f7878383f32` |
| Proximal host surface | `e3997d7357b66ff9085570a86a16c6ebdfdedb60` on `agent/caplab-p4-host-surface` |
| Requirements lock | `b5c05b76c4e383b9bdedb783ed658fe33c368d660a1efe45f80c98e0f8adb3a0` |
| Installed source manifest | `3f45560bc4bd5a7db7cace5a377eb4d3dad63524a3f6f53451c74e512d1fa0db` |
| Runtime interpreter | isolated Python 3.12.3, user site disabled |
| Migration | `0001_runtime_core.sql`, SHA-256 `7e075ccb2263f7926fa6b221d46ea908aba6f51a54aee412703657665ca3533b` |

Before the first mutation, 50 standalone repository tests passed with the two
live gates skipped by default; 34 Proximal hermetic tests passed with its
guarded PostgreSQL test skipped; the separately enabled PostgreSQL contract
test passed; Ruff and diff hygiene passed; the actual read-only host preflight
passed; and two independent agents returned readiness PASS on the frozen host
surface. The final source tree remained clean at its pinned commit.

## Execution observations

The empty base was created in PostgreSQL, Garage, `/nvr`, and the three local
runtime identities. Migration 0001 was applied once. The expiry timer was
enabled before credentials existed and remains scheduled for
`2026-07-22T23:50:00Z`. Base and ready phase verification passed before the
first synthetic effect.

The executor then crossed the irreversible effect boundary and ran exactly one
operation, `op-caplab-p4-roundtrip-0001`:

| Checkpoint | Observation | Retained evidence |
|---|---|---|
| Role isolation | Reader and verifier registration attempts returned structured `ConfigurationError` refusals; the live shell required status 2 before continuing. | `reader-register.stderr`, `verifier-register.stderr` |
| First registration | One 98-byte content-addressed object, one matching `/nvr` copy, one final registration, four operation events, and one audit event were recorded. | `register-first.json`, `final-state.json` |
| Same-operation replay | The receipt changed only to `idempotent_replay: true`; all three store inventories remained unchanged. | `register-replay.json`, `final-state.json` |
| Changed request | The runtime returned structured `OperationConflict`; the live shell required status 2, and the after-conflict inventories remained byte-for-byte equal to the first-effect inventories. | `register-conflict.stderr`, `final-state.json` |
| Independent retrieval | The reader wrote retrieved bytes whose SHA-256 was `87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`. | `retrieve.json`, `retrieved.sha256` |
| Verification and reconciliation | Runtime verification returned the registration identity; reconciliation reported object, local copy, metadata, locator, and provenance all `match`, with `ok: true`. | `verify.json`, `reconcile.json` |
| Cleanup custody | A content-identified, non-applying cleanup plan was emitted with plan identity `f096690374e2338befec7b6365e95983b71a429e3533462a1d666b41ebf253af`; it authorizes no deletion and requires separate authority for object, copy, row, or P5 work. | `cleanup-plan.json`, `cleanup-plan-receipt.json` |
| Access disablement | All three Garage keys were revoked, credential files removed, PostgreSQL peer roles made `NOLOGIN`, processes killed if present, and OS accounts locked and expired. Final host phase is `disabled` with `effects_armed: true`. | `disable.txt`, `verify-disabled.txt`, `final-state.json` |

The verifier-owned inventory changed from zero application rows, zero objects,
and zero copy files before registration to these exact post-registration
counts: one object of 98 bytes, one matching copy, one each of the eleven
identity/registration application row classes, four `operation_events`, one
`audit_event`, and one migration row. The first-registration, replay, and
conflict inventories are identical.

## Pre-effect deviations and corrections

These observations occurred before credentials and before the synthetic-effect
boundary:

1. The initial install stopped because `/usr/local/libexec` did not exist. No
   file or CAPLAB namespace was created by the failed command. The executor
   created that standard root-owned mode-0755 parent and added the step to the
   Proximal runbook.
2. The first bootstrap stopped while building its private virtual environment:
   the host manifest used `pathlib` component ordering while the pinned Git
   manifest used flattened POSIX-string ordering. The private stage was
   removed automatically; direct checks found no lifecycle state, CAPLAB
   namespace, identity, database, bucket, `/nvr` path, or residual stage. A
   regression reproduced the real `migrations.py` plus `migrations/` shape,
   the comparison was corrected, 35 hermetic tests passed, two independent
   reviewers returned PASS, and Proximal correction
   `e3997d7357b66ff9085570a86a16c6ebdfdedb60` was pushed before retry.
3. An extra base verification was attempted before migration and refused the
   absent schema as designed. The authorized sequence then applied the
   migration and passed base verification.
4. One orchestration wrapper rejected Bash interpolation syntax before
   launching a shell. It caused no host command; the equivalent trapped shell
   was then launched successfully.

## Preservation and gaps

The local execution root is
`/var/tmp/caplab-p4-execution.UGtXUE0D`. Its 32-entry `SHA256SUMS` verifies;
the manifest-file SHA-256 is
`d72e7fdc5567afc8b4f949c10175b429acc05ab557a9dd19de4ebfa622807993`.
The retained final-state file SHA-256 is
`25bde991aa8b6bc89598840d6700895578e866d1bc0957b978d6d2e298572fcc`.
The root-only live lifecycle record remains at
`/var/lib/caplab-p4-roundtrip-2026-07-15.state.json`.

**Preservation gap:** the shell asserted exit status 2 for both wrong-role
calls and the changed-request call, but it did not persist the three numeric
values as separate files. Their structured refusal documents, the successful
subsequent guards, and the unchanged verifier-owned inventories remain. This
record does not silently promote those artifacts into direct numeric-status
receipts.

The Garage writer credential necessarily had Garage's combined write/delete
grant while active. The runtime exposed no deletion command and all credentials
are now revoked, but the store was not WORM and out-of-band administrator
mutation was not prevented. The synthetic object, local copy, metadata, and
cleanup plan remain quarantined. The previously observed failed
`restic-prune.service` remains a P5 blocker; P4 did not test backup restoration
or retention lifecycle fitness.

## Verification and acceptance

Independent verification belongs in
[`caplab-p4-verification-2026-07-15.md`](caplab-p4-verification-2026-07-15.md).
That record may verify or reject this execution; it cannot accept it. No
acceptance decision is recorded here.
