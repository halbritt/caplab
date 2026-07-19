---
id: caplab-p7-json-decimal-repair-2026-07-19
artifact_type: implementation-record
assertion_type: observation
campaign: caplab-study-001-p7-recompute-2026-07-18
authorization: adr-0016-stage-a
status: prepared
---

# CAPLAB P7 JSON-decimal identity repair

## Scope

ADR 0016 Stage A authorizes model-free CAPLAB-25/P7 implementation, tests,
documentation, and Proximal host-surface preparation through
`2026-07-25T23:59:59Z`. This record describes a prepared defect repair. It is
not live execution, independent verification, a capability inference, another
retry authorization, or acceptance.

## First divergence and repair

The second live retry's first recomputation read a registered immutable JSON
observation containing a decimal token. Admission had preserved that token as
a string with `json.loads(..., parse_float=str)` before forming the historical
identity. Recomputation used default `json.loads`, which created a Python
`float`; the identity-safe canonicalizer then refused it before historical
comparison.

The repair changes only that immutable-byte boundary. Recomputation now uses
the same `parse_float=str` policy as admission. It does not accept Python
floats into durable identity, round or normalize decimal values, catch the
canonicalization failure, rewrite evidence, or add a fallback path.

## Test-first evidence

- A public `RecomputationService.recompute` regression fixture retains a
  numeric `0.25` token in immutable bytes and the identity-safe string `"0.25"`
  in the registered historical observation.
- Before the production edit, that test reproduced the live stack at
  `canonical_json(observed)` with `CanonicalizationError: floating-point values
  are not identity-safe`.
- After the one-line parser repair, the regression passed and produced the
  expected byte-identical historical comparison.
- The complete repository gate passed 105 tests with four explicitly gated
  live integration tests skipped.
- CAPLAB commit `bf6de2b24ac61e82107208cdc609c7e534c6eaaa` is clean and pushed.
  The repaired `service.py` has SHA-256
  `2e06e26ed0a61caf38a84ff8bfaba76794e1e4c9ae01f410adcbc040a8040854`.

## Prepared host surface

Clean, pushed Proximal commit
`c5bb1efa1402010a57ccc7034f3555b14830bc1c` binds the new CAPLAB source in
`SOURCE_COMMIT`, `recomputation.toml`, the controller source pin, documented
runtime path, and exact command. Nine controller lifecycle tests, Ruff, command
help, systemd calendar and unit checks, and diff hygiene passed. No host file,
runtime, service, timer, role, credential, database, Garage key, or live access
state was changed by this preparation.

## Guidance and authority boundary

Doctrine packet `pkt-7f0f29d6d5486b26`, content SHA-256
`dc8c419ca1d8de7db545dc0735991c57cbb174ff9d8563cc1dd9262d6095cff8`,
supports changing the smallest cause that explains the first divergence,
protecting it through an observable regression, and leaving adjacent structure
alone. It does not authorize live execution.

The repair and host surface are ready for review. Installing them, reading the
P6 registration again, or running another recomputation requires a new exact
owner decision.
