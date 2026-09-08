# Codex root capture linkage, version 1

Status: implemented read-only root observation linkage. See the
[decision and verification](../../records/implementation-2026-09-08-codex-root-capture-linkage.md).

`caplab.codex_capture_link.link_codex_root(policy_path, task_custody,
collection_custody, *, expected_attempt_sha256, expected_collection_sha256,
max_receipt_bytes, max_identity_bytes)` compares one retained Codex stdout
stream with exactly one retained root rollout and its planned model/effort.
The caller supplies independently retained hashes of task `attempt.json` and
native `collection.json`, an authorized inspection scope, quiescent custody and
trusted stable host parents. The API writes nothing and launches no process.

## Link evidence

The [task capture verifier](task-capture-verification-v1.md) and
[native collection verifier](native-collection-verification-v1.md) first verify
both complete referenced bundles under their existing contracts. A second bounded
metadata pass rereads seven linked receipts: collection, collection intent,
preparation, invocation, task attempt, task intent and process capture. This pass
checks hashes again before deriving any link. The collection must identify the
canonical Codex harness; Claude collections are rejected. The recorded task source
in preparation must equal the task intent's cwd. These paths are compared as
metadata and never reopened.

Retained stdout is read again with exact size/hash and stable descriptor/path
checks. The existing `codex_thread_id` parser requires one initial
`thread.started` and unambiguous JSONL records; it does not require a completed
turn. Its thread ID selects a candidate from the retained session inventory using
the existing exact `rollout-YYYY-MM-DDTHH-MM-SS-<thread-id>.jsonl` filename pattern.
Only entries under `session_search_root/` participate. The ID is compared
literally, never used as a glob or substring. Exactly one candidate must exist,
and it must be a regular file. Duplicate copies, selected symlinks, missing exact
names and filename-only guesses fail.

The selected object is read again with exact size/hash and stable-read checks.
The existing rollout interpreter, now available as
`caplab.artifact_rater.attest_rollout_capture(capture, thread_id, *, rollout_locator)`,
checks these bytes without opening its locator. Its file wrapper retains existing
behavior. The interpreter requires final LF, strict JSON records, consistent
session ID and CLI version, a complete model/effort turn context, and agreement
of all observed turn contexts and settings. Every session metadata ID must equal
the stdout thread ID. The reported model/effort must then equal the canonical
invocation tuple. The parser does not independently observe provider routing,
validate every native event, prove turn completion or prove that the bytes were
emitted by a genuine native process.

## Bounds and result

Both allowances must be positive integers, excluding booleans. Each bundle
verification and the combined seven-receipt reread has its own
`max_receipt_bytes` allowance; it is not one total I/O budget across all three
passes. Referenced bundle payload verification keeps each bundle's anchored
limits. The additional retained stdout and root rollout share
`max_identity_bytes`, checked before accumulation. Reads use the existing
65,536-byte maximum chunks. Parsing may allocate structures proportional to
these bounded inputs. No wall-time guarantee covers blocked filesystem I/O.
The separate canonical policy is a trusted input outside custody allowances.

The `caplab.codex-root-capture-link/v1` report includes both independent anchors,
invocation/profile identity, stdout hash and rollout attestation with a logical
inventory locator and raw hash. It reports root-ID, reported-tuple and recorded
host-task agreement. It records identity bytes, receipt bytes for both initial
verifications and the metadata reread, and process completion, termination and
return code. It omits command, prompt and raw response content.

Other regular files under the retained session tree are counted as
`other_session_files`; they are not parsed or classified as children. The initial
collection verifier still checks their bytes. `child_linkage_verified` is false
and `native_capture_complete` is null, even when that count is zero. A timeout
or nonzero exit can still supply matching root fields; the report preserves
those outcomes and grants no success or eligibility judgment.

`executed_invocation_bound` is always false. The task process may have been an
outer containment command, and this API does not prove it launched the planned
native invocation. That link needs the actual native adapter and binding record.
Nor does matching a recorded task path prove both bundles describe the same
physical execution; it supplies one consistency check alongside explicit anchors.
No human judgment, admission, model qualification or replay authority follows.
Known capture failures still take precedence over readable component records.

Missing, ambiguous, contradictory or tampered evidence raises
`CaptureVerificationError`; filesystem errors propagate. There is no retry,
recovery, source search, write or fallback. Custody must remain quiescent across
verification and rereads: this is not an atomic multi-file snapshot. Only selected
identity bytes are reread; a change to other payloads after their verification is
outside that quiescence assumption.
