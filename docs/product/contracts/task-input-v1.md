# Anchored task inputs, version 1

`caplab.task_input` prepares a bounded task representation and reproduces it
in an empty directory supplied by the caller. The input is independent of its
original source after preparation. This establishes represented content
identity; it does not establish task truth, exposure status, a complete
Binding, launch authorization or study eligibility.

## Preparation and verification

`prepare_task_input(source_root, *, output_dir, max_task_bytes,
max_task_entries)` requires an absolute, resolved source directory below `/`
and fresh output with a resolved parent, disjoint from the source. The caller
owns source authorization and quiescence and keeps both ancestries stable.
The function retains the existing v1 task inventory and private payload
objects under `inventory/`, checks the supported policy, seals `input.json`
and returns its SHA-256. Retain that digest independently of the bundle.

The `caplab.task-input/v1` receipt contains `source_root`, `inventory_sha256`,
positive integer `max_task_bytes` and `max_task_entries`,
`retained_task_bytes`, `retained_task_entries`, `task_content_sha256`,
`materialization_policy: caplab.task-input-materialization-policy/v1` and
`study_eligible: false`. Booleans are not integer limits. The entry allowance
includes the root and empty directories; the byte allowance counts retained
regular-file payload occurrences and literal symlink target bytes. Receipts,
inventory metadata, filesystem allocation and transient memory are additional resources.
These limits do not bound filesystem operation time.

The representation preserves regular-file bytes, literal symlink targets,
empty directories and permission modes. Privilege bits and special objects
are refused. Directories must allow owner read and search, files must allow
owner read, and symlink mode must be `0777`. Ownership, timestamps, ACLs,
extended attributes and hardlink topology are not restored. Links may be
dangling or point outside the task; materialization preserves their literal
targets without following them. The execution supervisor owns containment.

`task_content_sha256` hashes the validated, path-sorted entry list restricted
to each entry's present fields among `path`, `kind`, `mode`, `bytes`, `sha256`
and `target_base64`. Serialization uses Python JSON with sorted object keys,
ASCII escaping and comma/colon separators without spaces, encoded as ASCII.
Source stat observations and payload object locators do not enter this content
identity. The separately anchored receipt/inventory retain their custody
metadata. The root is identified by exact path `.`, not by list position.

`verify_task_input(custody, *, expected_input_sha256, max_receipt_bytes)`
requires an independently retained input digest and a positive combined raw
JSON allowance for `input.json` and `inventory/inventory.json`. It verifies
their hashes, schemas, inventory paths and payloads, policy, quotas and content
summary without opening the original source. Its
`caplab.task-input-inspection/v1` result reports `integrity_verified: true`,
input/content hashes, retained counts, `verified_receipt_bytes` and
`study_eligible: false`. No result is returned when verification fails.

## Materialization and release

`materialize_task_input(custody, descriptor, *, expected_input_sha256,
expected_device, expected_inode, max_receipt_bytes)` borrows a readable Linux
directory descriptor and duplicates it before opening custody. Device must be
a nonnegative integer and inode a positive integer, excluding booleans. The
directory must match that identity, be empty and be disjoint from custody in
both ancestry directions. Trusted stable ancestry is required; the check does
not attest arbitrary mount aliases or a namespace path.

The function verifies the full input before creating any entry. It creates
objects exclusively through directory descriptors without following links,
rehashes files while copying, applies supported modes, syncs files and
directories, and checks the entire final tree for exact contents, modes,
children and literal link targets. The caller must keep the destination
quiescent throughout; these checks do not provide an atomic filesystem
snapshot or make concurrent writers safe.

Success returns `caplab.task-input-materialization/v1` with input/content
hashes, `destination_identity` containing `device` and `inode`,
`materialized_bytes`, `materialized_entries`, `tree_verified: true` and
`study_eligible: false`. The function does not publish that result. A supervisor
must seal it, retain its digest and connect it to the input anchor and
[supervised before capture](supervised-task-capture-v2.md) before releasing
task execution. Handoff authentication, blocked setup, exact command identity,
writer shutdown and the release decision remain the supervisor's duties.
The [prepared-task capture helper](prepared-task-capture-v1.md) implements
materialization and before-content linkage for the authenticated shared mount
handoff used by the scripted native diagnostic.

Preparation and materialization preserve partial effects on failure and
propagate validation or filesystem errors. They provide no rollback, resume,
automatic deletion or success receipt after a failure. Existing output is
never reused; a nonempty partial destination is refused on retry. Only owned
descriptors are closed. The caller owns cleanup and any fresh attempt.

See the [implementation and verification record](../../records/implementation-2026-09-08-task-input-materialization.md).
