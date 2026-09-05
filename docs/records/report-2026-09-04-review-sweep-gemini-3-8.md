# Gemini 3.8 Flash on the review instrument: a revision step, established

- Date: 2026-09-04. Third of the three bindings minted 2026-09-02, measured
  on matched-pair defect injection (synthetic contract), seed `20260819`,
  environment `iso-v1`, two lanes, through `scripts/supervise_sweep.py`.
- Run root: `advisory/pool-runs/iso-agy-gemini-3-8-flash-high-20260819/`,
  69/69 usable. Claim `qc-2a7d56921b0121c1` (`review.defect_discrimination/1`,
  iso-v1 cohort). Contrasts: `advisory/comparisons/iso-agy-gemini-3-8-flash-high-vs-*-20260904.json`.
- The sweep took three sessions. Two agy stalls — ten consecutive probe
  timeouts while the judge-calibration run shared the Ultra window, and a
  tree-guard stop on upstream churn in `striatum-next` — each resumed from
  the usable rows with no case retired.

## Results on the iso-v1 cohort (57 scored pairs)

| binding | catch | 95% CI | false alarm | catch − FA | structural | anchored |
|---|---|---|---|---|---|---|
| **`agy-gemini-3-8-flash-high`** | **0.772** | [0.65, 0.86] | 0.158 | **0.614** | **16/24** | 0.579 |
| `claude-fable-5-1-high` | 0.667 | [0.54, 0.78] | 0.175 | 0.491 | 9/24 | 0.579 |
| `agy-gemini-3-7-flash-high` | 0.596 | [0.47, 0.71] | 0.088 | 0.509 | 10/24 | 0.526 |
| `or-gemini-3-7-flash-high` | 0.500 | [0.37, 0.63] | 0.000 | 0.500 | — | 0.482 |
| `cc-glm-5-3-max` | 0.526 | [0.40, 0.65] | 0.158 | 0.368 | 6/24 | 0.544 |

The ledger claim carries false alarm 0.106 and discrimination 0.666 on the
adjudication path (defective controls excluded); the table is the run-level
score. Both are stated.

### Matched contrasts (exact sign test on shared cases)

| contrast | shared | catch a vs b | a-only / b-only | p | FA a vs b | FA p |
|---|---|---|---|---|---|---|
| 3.8 Flash vs 3.7 Flash (same agy harness, same effort) | 57 | 0.772 vs 0.596 | **10 / 0** | **0.002** | 5 vs 3 | 0.625 |
| 3.8 Flash vs cc-glm-5-3-max | 57 | 0.772 vs 0.526 | **14 / 0** | **<0.001** | 5 vs 5 | 1.000 |
| 3.8 Flash vs fable 5.1 | 57 | 0.772 vs 0.667 | 9 / 3 | 0.146 | 5 vs 9 | 0.125 |

## Reading

**The revision step is real.** Same harness, same effort, same 57 cases:
3.8 caught ten cases 3.7 missed and missed none 3.7 caught (p=0.002). This
is the cleanest same-mounting revision comparison the fleet has, and the
first in which the newer model dominates the older on every discordant
case.

**It is the highest catch on the isolation cohort, and the first binding to
catch structural defects at better than half.** 16 of 24 — `base_dropped`
5/5 where every other subject under isolation is at 1/5, `dropped_section`
3/5, `hollow_delivery` 3/5. Under `iso-v1` the base is withheld, so these
are structural defects it saw in the artifact itself rather than by
comparing against a tree; the record of 2026-08-23 argued that ceiling was
the environment's. On this evidence part of that ceiling was the model's.
`hash_mismatch` stays at 1/5 for everyone, which is the part that really
does need the tree.

**Against fable 5.1 the lead is not established** (9–3, p=0.146): fable's
interval reaches 0.78 and 3.8's lower bound is 0.65. On the combined read,
3.8's discrimination (0.61) sits above fable's (0.49) because its false
alarms are fewer as well as its catches more; 0 of the 5 discordant
false-alarm pairs went against 3.8. Six of its ten refusals are on
unaudited controls, so 0.158 is an upper bound in the usual way.

**Cost.** The agy Ultra window is shared with live striatum dispatches and,
this week, with the judge calibration. The sweep stalled twice on probe
timeouts and never on a quota refusal; agy remains the one account on the
fleet never recorded exhausted. Median call time was not measured
separately from the stalls.

**Against the declaration.** Minted `review: baseline`, `basis: declared`.
On this evidence it is the strongest measured reviewer on the isolation
cohort by catch and by discrimination; the 3.7 sibling it supersedes is
declared `strong` on a 0.761 pre-isolation discrimination that isolation
re-measured at 0.507. Whether 3.8 takes the sibling's placement is a
Principal decision on the claim, after the control audit.

## Owed

- The false-alarm audit of the 10 refusals (6 on unaudited controls).
- Median latency per pair, from the rows, once the stall windows are
  excluded.
- The declaration's `status: disabled` and `supported_pass_types: []` are
  the Principal's to change; nothing here changes them.
