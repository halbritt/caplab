# Capture accounting for an expected population

Use `caplab.capture_accounting.build_capture_population_report` to keep missing
receipt pairs visible alongside [verified per-bundle byte reports](capture-byte-report-v1.md).
Supply the expected cells and slots explicitly. Do not build that population
from whichever captures survived.

The input is UTF-8 JSON with schema `caplab.capture-population-input/v1`:

```json
{
  "schema": "caplab.capture-population-input/v1",
  "cells": [
    {
      "world": "world-1",
      "arm": "none",
      "configured_tuple_id": "codex-terra-max",
      "slots": [
        {"slot_id": "s1", "task_capture": null, "native_collection": null}
      ]
    }
  ]
}
```

Each non-null `task_capture` or `native_collection` has exactly two fields:
`custody`, an absolute canonical host path, and `sha256`, the independently
retained digest of its final `attempt.json` or `collection.json`. A null means
that the anchor was not supplied. It does not mean the assignment was unused,
a process never launched, or any particular failure occurred. Retain separately
known launch and failure evidence; do not infer it from this accounting input.

Cell identity is `(world, arm, configured_tuple_id)`; cells are unique. Slot IDs
are globally unique. All IDs are nonblank strings without NUL. Empty cells stay
in the result. At least one cell is required. Reusing any supplied bundle path
or digest anywhere in the population is refused, including in partial pairs.
Unknown fields, duplicate JSON keys, malformed anchors and numeric substitutes
for IDs are errors. The accepted shape admits no numeric input values or
non-JSON numeric constants. Strings are preserved without normalization.

## Inspection and failures

```python
from caplab.capture_accounting import build_capture_population_report

report = build_capture_population_report(
    policy_path, input_bytes,
    expected_input_sha256=independently_retained_input_digest,
    max_input_bytes=input_byte_allowance,
    max_slots=slot_allowance,
    max_receipt_bytes=receipt_byte_allowance,
)
```

All three allowances are explicit positive integers excluding booleans. The
immutable input bytes must fit their allowance and match the supplied SHA-256.
The complete structure, identities and slot count are checked before any bundle
read. This input hash pins a supplied population record; it does not prove a
preregistration, completeness against an external assignment ledger, or native
origin. The caller must reconcile it with the authorized population.

Every supplied anchor is verified. A full pair uses the existing byte reporter,
including its task-root consistency check. A partial pair invokes the relevant
task or native-collection verifier and retains that component inspection. A
missing counterpart cannot hide corruption in supplied evidence. A collection's
configured tuple must match its cell, even when the task anchor is absent.
Without a collection, the cell's tuple remains an unchecked caller declaration.
The policy is used by native-collection verification; no native policy or
configuration is observed from an entirely unavailable cell.

Invalid content raises `CaptureVerificationError`; filesystem failures propagate
as `OSError`. An inaccessible file named by a supplied anchor is an error, not
an unavailable slot. No partial population report is returned after an error.
No discovery, repair, resealing, source collection, registration or execution
occurs. Caller-owned input paths and custody parents must remain trusted and
stable; bundles must be quiescent. The existing descriptor-based bundle readers
retain their own safeguards and limits.

Each invoked bundle verifier and combined metadata reread has its own
`max_receipt_bytes` allowance. This is not a whole-population receipt budget.
The raw input allowance and slot limit bound population input; parsing and
report objects need additional memory. No filesystem-I/O deadline is supplied.

## Read the result

`caplab.capture-population-report/v1` preserves cells and slots in supplied
order. Each slot has `pair_available`, `anchors_not_supplied`, `byte_report`,
`task_inspection` and `native_inspection`, alongside its supplied identifiers
and anchors. A full pair has the byte report; a partial pair has its separate
component inspection and a null byte report. No-anchor slots remain explicit.

Each cell and the whole population report:

- `expected_slots`, `available_pair_slots` and `unavailable_pair_slots`;
- `available_pair_logical_payload_bytes` and `available_pair_receipt_bytes`,
  sums over the available-pair subset only;
- `all_slot_pair_logical_payload_bytes` and `all_slot_pair_receipt_bytes`,
  both null if any expected pair is unavailable.

For example, one available pair retaining 25 logical bytes and three unavailable
pairs yields `expected_slots: 4`, `available_pair_slots: 1`, an available-pair
sum of 25, and a null all-slot total. It does not yield 6.25 bytes per episode.
These are synthetic illustrative counts, not a measured native cost.

Partial component inspections are not added to pair sums. Their known byte
counts remain inspectable separately. Empty cells have zero counts and empty
sums; those zeros describe no declared slots, not successful study completion.
There are no imputed costs, averages, precision estimates or automatic budgets.

A full pair can describe a failed process, incomplete stream or missing native
location. Those states stay in its byte report and do not change pair
availability. Even with every pair available, retained logical bytes are not
runtime peak allocation, total disk cost, capture overhead or complete native
output. `population_assignment_verified` and `study_eligibility_established`
remain false. This report applies no resource, coding or reviewer-quality gate.

## CLI

With the input saved in private custody and its digest retained independently:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 scripts/capture_population.py \
  "$POPULATION_INPUT" --policy docs/product/contracts/native-agent-systems.json \
  --expected-input-sha256 "$POPULATION_DIGEST" \
  --max-input-bytes 1000000 --max-slots 1000 --max-receipt-bytes 1000000
```

These allowances are examples, not campaign budgets. The CLI reads at most the
input allowance plus one byte, emits JSON only on successful inspection, and
exits two with stderr on argument, integrity or filesystem errors. Exit zero
can include unavailable pairs and failed processes. Keep the output private:
arm labels, task paths and capture metadata are analyst inputs, not blinded
coder material. The [implementation record](../../records/implementation-2026-09-08-capture-population-accounting.md)
retains the authorization and synthetic verification.
