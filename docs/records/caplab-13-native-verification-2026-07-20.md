---
id: caplab-13-native-verification-2026-07-20
artifact_type: verification-record
title: CAPLAB-13 native technical verification
status: pass
created: 2026-07-20
decision_record: adr-0045
verifier: primary-agent
independence: not-independent
---

# CAPLAB-13 native technical verification

## Verdict

**PASS** for the CAPLAB-13 technical calibration criteria. This is
primary-agent technical verification, not an independent verdict or CAPLAB
acceptance.

## Verified evidence

- The sealed ledger derives 16 completed primary slots, zero infrastructure
  failures, zero replacements, and no stop reason.
- Every launch, completion, observation, native output, task tree, review, and
  normalized capture remains digest-bound to the exact native campaign.
- The capture manifest binds exactly 16 captures and recomputes to semantic
  SHA-256
  `7197ef195dd47ebd41c1ac825aa8cd0e71e321442be5545b462fc887f182428d`.
- The result recomputes to semantic SHA-256
  `731fa7859082886fc838912ab3a11f8d63614858cb5d7566696aca6e0ecab431`.
- Every development cell appears once per native subject; truth, cue, and world
  groups each retain their exact denominators.
- All 16 reviews independently fail the unchanged schema; no severity was
  remapped and no invalid review became mechanical evidence.
- The comparison is `not-estimable` and the conclusion is
  `instrument-not-calibrated`, matching ADR 0045.
- The public calibration loader still opens development content and only the
  held-out aggregate seal. `heldout.json` was not opened during execution,
  normalization, or verification.
- `make check` passed 206 tests with four authorized integration skips.
- No model call occurred after the 16 completed primaries.

## Boundary

CAPLAB-13's authorized development calibration, negative result, and technical
verification are complete. This pass does not authorize a corrected campaign,
held-out execution, independent verification, model comparison, policy use,
training use, or broader CAPLAB acceptance.
