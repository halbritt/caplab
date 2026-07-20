---
id: caplab-13-native-result-2026-07-20
artifact_type: result-record
title: CAPLAB-13 native development calibration result
status: complete
created: 2026-07-20
decision_record: adr-0045
---

# CAPLAB-13 native development calibration result

## Result

The exact calibration conclusion is **instrument not calibrated**. All 16
primary slots completed at the native harness boundary, but zero reviews
passed the frozen review schema and zero were score-eligible. Model comparison
is therefore **not estimable**.

| Quantity | Count |
|---|---:|
| Primary slots | 16 |
| Native Fable slots | 8 |
| Native GPT slots | 8 |
| Infrastructure failures | 0 |
| Replacements | 0 |
| Review artifacts written | 16 |
| Schema-valid reviews | 0 |
| Score-eligible reviews | 0 |

The native prompt required a severity field but did not state that the frozen
schema accepted only `critical` and `noncritical`. Both harnesses emitted
ordinary severity vocabulary instead: `error` 2, `high` 9, `info` 17, `low`
9, `major` 2, `medium` 3, and `minor` 2. Remapping those values after execution
would be a post-hoc semantic rescue and is prohibited.

The result has semantic SHA-256
`731fa7859082886fc838912ab3a11f8d63614858cb5d7566696aca6e0ecab431`
and file SHA-256
`f3810f55f8b68c032f473e4433581a97451c8bbe2cb4eecd91ffa8bad64adb5e`.
The 16-capture manifest has semantic SHA-256
`7197ef195dd47ebd41c1ac825aa8cd0e71e321442be5545b462fc887f182428d`
and file SHA-256
`02e6a35f80aad9d9994d452c44d56531f42d72ef91f843e777593dcf1d4a32af`.

## Interpretation boundary

There is no qualitative disposition because no review crossed the mechanical
schema gate. The invalid outputs remain preserved as subject behavior, but
they do not support a Fable-versus-GPT comparison, a review-capability claim,
held-out execution, lane fit, routing, export, training, or CAPLAB acceptance.

The only supported recommendation is to correct and requalify the native
elicitation contract before any later calibration campaign. That recommendation
does not itself authorize a rerun. The held-out split remains sealed and
unopened.
