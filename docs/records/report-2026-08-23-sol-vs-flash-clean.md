# Sol-high vs flash-high, re-scored on a complete clean-contract case set

- Date: 2026-08-23. Supersedes the "not established" verdict of
  `erratum-2026-08-22-changeset-contract-quarantine.md`, which had only the
  37 prose cells to score on.
- Method: profile-remeasurement — the 20 change-set cells the v1 quarantine
  removed, re-run under the clean v2 contract with fresh injections (seed
  20260823) by both subjects. Cells were selected by contract version, an
  exogenous property, so the runs are claim-eligible (stamped
  `profile-remeasurement`, 32/32 usable each at 4 lanes).
- Sol's two strata come from two accounts (primary for prose, codex-harm
  for the change sets), treated as one Binding under the Principal's
  2026-08-23 ruling that the harm account is capacity, not identity; the
  registry's identity hash still separates them, and this record cites the
  ruling rather than assuming it.

## Result

| stratum | cells | Sol-only | flash-only | p | Sol catch | flash catch |
|---|---|---|---|---|---|---|
| prose (v1, seed 20260819) | 37 | 6 | 1 | 0.125 | 0.946 | 0.811 |
| change-set (v2, seed 20260823) | 20 | **8** | **0** | **0.008** | 0.900 | **0.500** |
| **pooled clean** | **57** | **14** | **1** | **0.0010** | 0.930 | 0.702 |

**Sol leads flash-high on catch, established on clean contract.** The
change-set stratum carries it: under the clean contract flash-high catches
only half the change-set mutants — its earlier near-ceiling change-set
catch (23/25 under v1) was the contaminated contract's refuse-everything
posture, not detection. Sol's detection survives the contract fix intact.

## False alarms, adjudication-aware

Sixteen Sol control refusals on the change-set cells were audited by
oracle (`adjudication-dossiers-2026-08-23-sol-clean-controls.md`): nine
controls proved **defective** (Sol was right), three proved sound (Sol was
wrong), four await the Principal. Flash-high refused **zero** change-set
controls under v2. So on the clean change-set stratum: Sol FA 7 of 11
non-defective pairs (3 established + 4 pending), flash 0 of 11. Sol's
discrimination on the stratum sits between +0.27 and +0.63 depending on
the four rulings; flash's is +0.50 with no uncertainty.

The pattern is the campaign's recurring one, now on clean data: Sol
catches nearly everything and refuses a lot of sound work, flash catches
less and refuses almost nothing — and nine of Sol's sixteen "false alarms"
were real defects in shipped production change sets.

## Settled — the Principal's four rulings (2026-08-23, records 21–24)

`faaba3e4`, `c70d14e4`, `d79e9a16` sound; `af9054a1` **defective** (the
content-addressed address/hash gap was real). With all twenty controls
adjudicated — **ten defective, ten sound** — the change-set stratum's
false-alarm measure is established, no unaudited pairs: Sol refused 6 of
the 10 sound controls (60%), flash 0 of 10. Sol's discrimination on the
stratum is **+0.60** against flash's +0.50; Sol was right about half the
production change sets it refused, and a Sol refusal on a production
change set was a coin flip between a real defect and a false alarm.

## Claims

Two `profile-remeasurement` claims (n=20 each, change-set classes only —
not balanced breadth claims, noted here because the claim vector cannot
say so): `codex-harm-sol-high` and `agy-gemini-3-7-flash-high` at seed
20260823. Contrast document:
`advisory/comparisons/sol-vs-flash-high-changeset-clean-20260823.json`.
