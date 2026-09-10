# Agreement between overlapping capture copies

`caplab.capture_overlap.compare_verified_capture_overlap` compares already
verified receipts for a final task inventory, selected native collection,
retained task mount and retained runtime mount. It performs no filesystem I/O,
launch, write, recovery or evidence admission. Inputs are borrowed unchanged.

The caller must independently verify each receipt's anchor and supported
schema, every referenced payload, source/descriptor linkage and resource
allowances before calling. This function is not an integrity verifier and must
not be used to turn arbitrary matching JSON into verified capture. Caller-owned
custody must remain stable during verification and comparison.

The shared `scripts/probe_native_capture_startup.py:inspect_custody` is the
integrated caller, also used by the repository scripted native inspector. It
first verifies task/native bundles and all five retained mounts, then rereads
the anchored final task and native receipts through bounded no-follow readers.
The combined task metadata reread has a 300,000-byte allowance; the native
receipt reread has its own allowance of that size. Previously verified mount
receipts are reused. No original task/runtime path is reopened.

For `/work`, the final task inventory must match the entire retained task
mount. For each native selected location, its namespace source must lie under
the retained runtime root. Its selected entries must match the exact subtree
at that source path. Path-prefix comparison respects component boundaries:
`codex/log-other` does not belong to `codex/log`.

Comparison translates each source path to the selected subtree's relative path,
then compares all recorded entry fields except `path` and `object`. Each copy
owns its own object locators. Kinds, modes, file lengths/hashes, literal encoded
symlink targets and recorded source metadata must agree. Canonical JSON
comparison keeps booleans distinct from numbers and performs no Unicode
normalization. The prior integrity readers establish the payload/hash relation;
this comparison establishes agreement between those verified occurrences.

A missing selected location must have neither selected entries nor a matching
retained-runtime subtree. A retained empty directory remains one retained
entry. Unselected runtime files are preserved but are outside this comparison.
An omitted or added entry, changed content/metadata, false missing location or
source-root mismatch raises `CaptureVerificationError`; no successful aggregate
report is returned. Existing failures and original custody remain unchanged.

The `caplab.capture-overlap-comparison/v1` result reports
`overlapping_entries_agree`, task entry count and each native location's status
and compared entry count. Counts describe comparison population, not storage
cost or usable observations. `payload_integrity_verified_here` is false,
`native_capture_complete` is null and `study_eligible` is false. The integrated
custody reader returns this result under `overlap` alongside the separate
integrity and accounting reports.

Matching copies do not prove exhaustive native emissions, absence of
intermediate writes, atomic snapshots, source authenticity, containment,
provider identity, task correctness, blinding or study readiness. This is one
additional consistency requirement under CAPLAB-79/84. See the
[repair and verification record](../../records/repair-2026-09-09-capture-overlap.md).
