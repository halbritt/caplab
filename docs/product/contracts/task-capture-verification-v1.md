# Inspect task capture integrity, version 1

The verifier also accepts the matching v2 attempt, intent and inventories
produced by the [supervised recorder](supervised-task-capture-v2.md). V2 adds
descriptor-source, namespace and process-receipt-limit checks and returns the
verified `task_source` metadata. The contract below describes the original v1
path; valid v1 inputs and result shapes remain supported.

Status: implemented read-only component. Decision and verification:
[implementation record](../../records/implementation-2026-09-08-task-capture-verification.md).

`caplab.task_capture_verify.verify_task_capture(custody, *,
expected_attempt_sha256, max_receipt_bytes)` verifies a
[task attempt capture](task-attempt-capture-v1.md) against a caller-supplied
lowercase SHA-256 digest. Retain that digest independently when the attempt is
sealed. Deriving it from the same untrusted local `attempt.json` during inspection
cannot detect replacement of the entire bundle. No registration or external
anchor storage is implemented here.

`custody` must be an absolute path with a resolved parent. The caller provides
trusted stable parents and quiescent custody throughout the read. The verifier
opens the root, component directories and leaf files without following links;
files must be regular. Nonblocking opens reject FIFOs without waiting for a
writer. Descriptor ownership spans failures. File identity, size and modification
observations are compared before/after reading and against the leaf path.
These checks do not establish an atomic snapshot or prevent changes after a
file's checked interval.

## Checked evidence

The verifier checks the exact attempt bytes against the supplied digest, then
checks the attempt's links to `intent.json`, both `inventory.json` files and
`process/capture.json`. JSON uses strict UTF-8 decoding, rejects duplicate keys
and non-JSON numeric constants, and requires the expected v1 schema identifiers.

Both inventories must have sorted unique task-relative paths, a directory root,
directory parents, supported kinds and valid mode values. Regular-file objects
must have unique numbered leaf locators within each inventory; their sizes and
SHA-256 hashes are checked. Symlinks remain canonical base64 literal targets;
no target is opened. Task and stream contents remain opaque bytes, including
non-UTF-8 data. The original task directory may be absent.

The reader verifies the combined task byte/entry totals against the anchored
intent limits, the process stream totals and limits, both stream files and EOF
flags, termination/completeness consistency, and the duplicate process receipt
inside the attempt. It recomputes observed changes with the capture producer's
comparison routine and checks the stored summary. This is a consistency check,
not an independent evaluation of the comparison rule.

Source stat fields, timestamps, command and environment remain hash-covered
metadata; this interface does not authenticate their meaning, validate every
metadata field, prove chronology or execute the command. Unreferenced files
(including partial/failure artifacts) are outside the checked receipt graph and
are not inspected or removed. Successful integrity inspection cannot override a
known capture exception or prove that publication completed successfully.

## Limits and result

`max_receipt_bytes` is a required positive integer (not Boolean), bounding the
combined raw bytes of all five linked JSON receipts. An exact allowance passes;
one byte less fails. Parsed Python objects and the returned report require
additional memory. Payload hashing reads chunks of at most 65,536 bytes under
the sizes and combined limits in the anchored receipts; payloads are not loaded
whole or decoded. A read can request one extra byte to detect growth. There is
no wall-clock bound on filesystem I/O, and no disk reservation or durability
barrier is performed by this reader.

The `caplab.task-capture-inspection/v1` result contains the attempt digest,
`integrity_verified`, capture completeness, termination, actual recorded return
code, retained task/stream counts, verified receipt bytes and observed changes.
It omits the command, environment and raw contents. Paths in changes remain
private task metadata. A nonzero return code may coexist with complete capture;
timeout or byte-limit captures can have verified integrity with
`capture_complete: false`. There is no task-success, native identity, blinding,
containment, study eligibility, qualification or acceptance decision.

Invalid content raises `CaptureVerificationError`; filesystem failures propagate
as `OSError`. No repair, receipt publication, source access or launch is attempted.
Reads may update filesystem access times.

## CLI

With `CAPTURE_ROOT` set to authorized custody and `ATTEMPT_DIGEST` obtained from
its independent seal record, this illustrative one-megabyte receipt budget runs
an inspection (it is not a study budget):

```bash
PYTHONPATH=src python3 scripts/verify_task_capture.py "$CAPTURE_ROOT" \
  --expected-attempt-sha256 "$ATTEMPT_DIGEST" --max-receipt-bytes 1000000
```

Success prints the JSON report and exits zero, including consistent incomplete
captures or nonzero task exits. Missing files, wrong hashes, malformed evidence
and exhausted receipt allowance print an error to stderr, exit two and produce
no stdout report. For example, a mismatched anchor reports
`receipt hash mismatch: attempt.json`; recover the authorized original bytes
and independent anchor rather than resealing corrupt evidence to make it pass.
