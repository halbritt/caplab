# Quarantine for retained writable mounts

`scripts/probe_cgroup_resource_limits.py:retain_mount(descriptor, output,
identity, bytes_left, entries_left, *, quarantine_factory=None)` copies one
quiescent directory through its borrowed descriptor. The resource and native
startup supervisors use this helper for writable-mount custody. The caller owns
which mount may be read, its independently observed identity, quiescence, stable
private output ancestry and the combined remaining byte/entry allowances.
The helper neither launches a process nor authorizes collection.

With a trusted factory, the helper uses the same checking policy and bounded
inventory copier as [native collection](native-output-collection-v1.md#optional-exact-secret-quarantine)
and [task capture](task-attempt-capture-v1.md#optional-trusted-quarantine).
It makes a shallow snapshot of the caller's currently flat identity mapping
before invoking policy callbacks. Source-path filesystem bytes, identity JSON
strings and serialized bytes, and output/receipt/pending paths are checked
before output creation. The caller must keep the descriptor and any referenced
input state stable; this is not a general deep-freeze or handoff attestation.

The inventory checks literal filenames and symlink targets before encoding and
passes file bytes through a fresh gate before writing. Received file bytes and
literal link bytes consume the existing shared allowance; withheld overlap
cannot extend it. Only EOF permits flushing. Exact received/emitted counts and
hashes are required for completed files. Gate cleanup, quota, source-change and
storage failures prevent final publication and preserve private safe prefixes.
The helper closes neither the borrowed root descriptor nor the original source.
There is no retry, purge, redacted substitute or successful empty fallback.

The existing unique `.` entry supplies the observed root device/inode for
comparison with `identity.source_dev/source_ino`. Its position in sorted output
does not identify it. Final receipt strings and serialized bytes are checked
before sealing `inventory.json`. The unchanged
`caplab.retained-mount-inventory/v1` receipt includes namespace `source_root`,
caller identity, initial remaining allowances, retained bytes and sorted entries.
The returned tuple contains its byte digest and the remaining byte/entry budget
for the next mount. Existing retained-mount integrity verification still applies.

`None` preserves unguarded operation. The existing diagnostic CLIs do not select
a secret policy merely because this helper supports one. An adopting supervisor
must select the same intended policy at every owned writer, including process,
task, native-session and full-mount copies, and retain that selection separately.
Receipt integrity does not attest policy identity. A later guarded copy cannot
undo an earlier unguarded copy, and completed component receipts do not turn a
failed aggregate operation into a complete capture.

The factory is trusted host policy with caller-owned secret selection, bounded
memory/runtime and lifetime. Interface/result/cleanup failures propagate; exact
matching does not cover unknown values, arbitrary encodings, cross-stream
fragments, original source custody, external logs or memory zeroization. No
authenticated native execution, exhaustive containment, privacy acceptance,
reviewer capability or study eligibility follows. The
[implementation record](../../records/implementation-2026-09-09-mount-capture-quarantine.md)
retains synthetic integration and omission-control evidence.
