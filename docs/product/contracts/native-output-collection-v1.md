# Native output collection, version 1

Status: implemented raw collection. See the
[decision and verification](../../records/implementation-2026-09-08-native-output-collection.md).

`caplab.native_collection.collect_native_outputs(policy_path, preparation_root,
*, expected_preparation_sha256, output_dir, max_receipt_bytes,
max_artifact_bytes, max_entries)` retains the output locations named by a
[prepared native runtime](native-runtime-preparation-v1.md). The caller supplies
an independently retained SHA-256 of `preparation.json`, a quiescent runtime,
trusted stable host parents and an authorized collection scope. This function
does not start or stop a process and does not grant authority to read evidence.

## Inputs and bounds

Before creating output, bounded stable regular-file reads check the preparation
hash and linked invocation-file hash, with one combined receipt-byte allowance.
The canonical invocation builder reconstructs the plan and checks its digest.
The preparation custody root, runtime root and capture-path map must match that
plan at the supplied host location. Source receipt schemas are checked; unrelated
preparation metadata is not fully reverified. The task mount source is used only
to keep output outside the declared task, and is never opened.

All three limits must be positive integers, excluding booleans. The preparation
root must be absolute and resolved below `/`; the fresh output root must have a
resolved absolute parent and be disjoint from both preparation and declared task
roots. Existing destinations are refused. The runtime directory and traversal
parents open with no-follow directory descriptors. These checks do not isolate
against privileged host writers or independently establish trusted ancestry.

The current Codex plan selects `codex/sessions`, `codex/log` and
`final-message.txt` inside the runtime. Claude selects `claude/projects` and
`debug.log`. No ambient home, configuration tree, credential file or unrelated
runtime file is selected. The collector does not search alternative paths when
one is missing. Future profile changes require the canonical builder's explicit
support; a rewritten preparation map cannot redirect collection.

One existing task inventory copier retains all files and nested directories
under selected trees. It preserves exact file bytes, modes, source identity
metadata and literal base64 symlink targets. It does not parse JSON, filter by
filename suffix, normalize text or resolve links. Thus root and child candidate
files remain available for later interpretation without assigning their roles.
A selected root must have the expected directory or regular-file kind; selected
symlinks and linked parents are rejected. Nested special files are rejected.

The artifact-byte allowance counts file bytes and literal link-target bytes
across every selected location. Each hardlink pathname is charged separately.
The entry allowance counts selected roots and all descendants; missing locations
consume no entry. Payload reads use chunks no larger than 65,536 bytes and one
extra byte to detect quota overflow. Directory names and retained metadata are
bounded by entry count and filesystem name limits. Source stat checks and
bounded directory rechecks detect observed changes during copying. Ancestor and
runtime identity checks surround traversal. This is not an atomic multi-file
snapshot; the caller must stop all writers first. Limits do not bound a blocked
filesystem operation's wall time or the runtime's storage use before collection.

## Custody and failures

Fresh output contains exact copies of `preparation.json` and `invocation.json`,
`intent.json`, an `objects/` directory of raw file payloads, and a final
`collection.json`. Files are private mode 0600 and output directories request
0700. Receipt copies and payloads sync before final publication; the objects
directory is synced, then the existing capture publisher seals the final
receipt and syncs output and parent. This is a local filesystem barrier.

The intent links exact source receipt hashes, invocation identity, selected host
paths and all limits. The `caplab.native-output-collection/v1` receipt links the
intent hash and records timestamps, locations with `retained` or `missing`
status, sorted inventory entries, byte/entry totals and `missing_locations`.
Entry paths begin with the selection name (such as `session_search_root`);
file object locators refer to `objects/`. Missing files remain explicit even
when the collector otherwise completes. Empty prepared trees are retained as
empty directories. Neither case establishes a native transcript.

Errors propagate as `NativeCollectionError`, existing capture/verification
`ValueError` subclasses, or filesystem errors. Copy/quota/source-change failures
retain partial custody and publish no final collection. There is no automatic
cleanup, overwrite, retry, fallback, or recovery. A known publication exception
wins over any final file left after a cleanup failure. Consumers must not infer
successful publication merely from directory contents. Raw diagnostics can
contain sensitive content and remain private; no redaction or sharing occurs.

`native_identity_verified` is false and `native_capture_complete` is null.
Collection does not link a session to stdout, identify children, prove provider
routing or native emission, verify containment, register evidence, or establish
eligibility, capability, task success or study readiness. An adapter must link
the collection to its separately retained attempt and independently preserve the
final collection digest. The [collection verifier](native-collection-verification-v1.md) checks that anchor,
linked bytes and selection consistency before interpretation. Session linkage
and eligibility remain separate requirements.
