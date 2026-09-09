# Captured tool-pair inspection, version 1

Status: implemented integration, tested with synthetic local producers. See the
[execution record](../../records/implementation-2026-09-08-captured-tool-pairs.md).

`caplab.native_tool_pairs.inspect_captured_tool_pairs(custody, *,
expected_attempt_sha256, format, expected_root_id, max_receipt_bytes,
max_event_bytes)` follows a retained attempt's receipt chain to stdout before
building the [native tool-pair report](native-tool-pairs-v1.md).

The caller supplies the attempt digest from independent custody, plus the
expected native format and root ID. They are not inferred from the stream.
The function first runs the full [task-capture integrity verifier](task-capture-verification-v1.md),
including task payloads, both streams and the linked receipts. It then rereads
the anchored attempt and process receipts and reads `process/native.stdout`
against its recorded size/hash. The original task root may be absent.

## Availability and failure

The result uses `caplab.captured-tool-pairs/v1` and includes the independent
attempt anchor, linked process-receipt digest, stdout locator/hash/size/EOF,
full task-capture inspection and the parsing allowance. It distinguishes:

| Condition | Result |
| --- | --- |
| Valid custody and parseable supported stdout | `tool_pairs_available: true` and a nested `tool_pair_report`. |
| Stdout exceeds the parsing allowance | `tool_pairs_available: false`, null report, `event_byte_allowance` reason. |
| Empty, malformed, truncated or identity-mismatched native stdout | `tool_pairs_available: false`, null report, `native_event_contract` reason. |
| Invalid anchor, damaged receipt/payload, unsafe custody object or failed read | Exception; no inspection report. |

A truncated stream ending on a complete JSONL record boundary can remain
parseable. The nested report then describes only the retained prefix. The
outer `task_capture.capture_complete`, termination and return code remain
visible; pairing availability does not override them. A syntactically complete
stream with no observed tools has an available empty group count. Unavailable
pairing has no count and must not be substituted with zero activity.

`native_execution_linked` remains false and `native_capture_complete` remains
null. The linkage proves that the inspected stdout belongs to the anchored
capture receipt graph. It does not authenticate what executable produced it,
bind the configured native invocation, verify persisted sessions, or establish
native completeness, task correctness, blinding, eligibility or acceptance.
All those separate checks remain required. A failed producer can have a valid
capture and an available pairing report.

## Resource and custody boundary

Use absolute custody paths, trusted stable parents and quiescent custody, as
required by the task verifier. All payload opens use its existing descriptor
reader: regular files only, no symlink following, nonblocking type checks, and
before/after identity checks. This is not an atomic snapshot or protection
against a privileged concurrent writer.

Full verification and the subsequent two-receipt reread each have their own
`max_receipt_bytes` allowance. `max_event_bytes` bounds stdout loaded for
parsing, separate from the verifier's chunked hashing of the complete capture.
An oversized parsing input still receives full bundle verification before
being reported unavailable. No wall-clock limit for filesystem I/O is supplied.
Parsed objects and report metadata require memory beyond raw byte allowances.

Both limits must be positive integers excluding booleans. Unsupported format
or empty expected root ID is a caller error. Integrity failures raise
`CaptureVerificationError`; filesystem errors propagate as `OSError`. The
native parser's `ValueError` becomes an unavailable observation only after
custody integrity has been verified. No repair, source discovery, file rewrite,
model call or evidence registration occurs. Reads may update access times.

## CLI

Use a separately retained attempt digest and root identity:

```sh
umask 077
python3 scripts/captured_tool_pairs.py "$CAPTURE_ROOT" \
  --expected-attempt-sha256 "$RETAINED_ATTEMPT_SHA256" \
  --format codex-exec-jsonl --expected-root-id "$RETAINED_THREAD_ID" \
  --max-receipt-bytes 1000000 --max-event-bytes 16777216 > inspection.json
```

Exit zero means inspection completed, including explicit unavailable pairing
or a failed/incomplete process. Check the report fields before using it.
Integrity, argument and filesystem failures exit two with stderr and no JSON
stdout. These example limits are not campaign budgets. Reports contain private
IDs and task-path metadata and belong in restricted custody.
