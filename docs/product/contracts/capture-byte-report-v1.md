# Retained capture byte report, version 1

`caplab.capture_accounting.build_capture_byte_report` verifies one task capture
and one native-output collection, checks their recorded task roots agree, and
reports logical retained bytes by surface. Use it for capture accounting before
budget extrapolation. It does not launch a subject or validate a study.

```bash
PYTHONPATH=src python3 scripts/capture_bytes.py \
  /absolute/task-custody /absolute/native-collection \
  --policy docs/product/contracts/native-agent-systems.json \
  --expected-attempt-sha256 "$ATTEMPT_DIGEST" \
  --expected-collection-sha256 "$COLLECTION_DIGEST" \
  --max-receipt-bytes 200000
```

The digests must be retained independently of the bundles. The allowance above
is an example, not a campaign parameter. Each existing bundle verifier and the
combined metadata reread has a separate allowance of that size. Anchored intent
limits bound referenced payloads. Caller-owned custody must be quiescent, with
trusted stable parents. Filesystem read latency is not bounded by byte quotas.
The command reads retained custody only and writes JSON to stdout. A failed
verification emits no report. It does not repair, omit, or replace bad input.

The `caplab.capture-byte-report/v1` report contains these surfaces:

- `task/before` and `task/after`: the complete retained inventories.
- `process/stdout` and `process/stderr`: captured stream prefixes and their EOF
  observations. The report also retains overall capture completeness,
  termination reason, and process return code.
- `native/<selection-name>`: each location selected by the pinned native capture
  plan, including files, directories, and symlinks nested inside a selected tree.

Each row reports status, entry count, `file_bytes`, `symlink_target_bytes`, and
their sum `logical_payload_bytes`. Entry counts include directories. A missing
native location has null counts and byte values. A retained empty directory has
zero byte values and one directory entry. A retained empty file has zero bytes
and one file entry. These states remain distinct.

Totals count retained occurrences. Identical content in the before/after trees,
stdout, and native session files contributes once at each retained occurrence;
hash equality does not make those retained copies free. Symlink target bytes
count the target string, without following it. They are encoded inside inventory
receipts, rather than retained as separate payload objects.

`verified_receipt_bytes` is the separate sum of the five task receipt files and
four native-collection receipt files read by the original verifiers. The combined
metadata reread does not add another copy to this count. Do not add logical
symlink target bytes to receipt sizes as a disk estimate: their encoded contents
are already in those receipts. The report does not inspect unreferenced files,
filesystem allocation, compression, shared extents, or storage outside the two
bundles. It supplies neither total disk use nor a runtime storage bound.

Successfully verified incomplete streams and failed task processes remain
reportable. A capture or collection failure with no final anchored receipt is
unavailable to this API; it must not enter a campaign budget denominator as a
zero-cost attempt. Native missingness and `native_capture_complete: null` also
remain explicit. Matching recorded task paths is weaker than proving that the
planned native invocation produced either bundle, so
`executed_invocation_bound` remains false. The tuple identifies configuration,
not an observed native model.

Capture overhead, runtime peak bytes, redaction runtime, and manual redaction
time are null. Capture timestamps alone cannot establish incremental overhead
against an uncaptured execution. These quantities still need the separate
measurements required by CAPLAB-84. Synthetic fixture counts test accounting;
they are not representative native episode costs, blinding validation, or
authority to extrapolate a campaign budget.

See [task verification](task-capture-verification-v1.md),
[native collection verification](native-collection-verification-v1.md),
and the [implementation record](../../records/implementation-2026-09-08-capture-byte-accounting.md).
