# Fable 5.1 and GLM-5.3-flash on the review instrument

- Date: 2026-09-03. Two of the three bindings minted 2026-09-02, measured
  on matched-pair defect injection (synthetic contract), seed `20260819`,
  environment `iso-v1`, two lanes each, through `scripts/supervise_sweep.py`.
- Run roots: `advisory/pool-runs/iso-claude-fable-5-1-high-20260819/`
  (69/69 usable, complete), `advisory/pool-runs/iso-cc-glm-5-3-flash-high-20260819/`
  (68/69 usable at writing; the last case is re-measuring). The Gemini 3.8
  Flash run is at 32/69 after two agy stalls and is not reported here.
- Claim: `qc-6504bb1fb3728992` (`claude-fable-5-1-high`,
  `review.defect_discrimination/1`, iso-v1 cohort). The GLM-flash claim
  follows its 69th pair.
- Comparisons: `advisory/comparisons/iso-*-20260903.json` (four matched
  contrasts, exact sign tests on shared cases).

## What the sweeps cost

Fable 5.1 hit the claude account's session limit twice (resets at 3:10am
and 4:40pm Pacific): 9 pairs returned "You've hit your session limit" and
were released and re-measured after the window reset. The account is
shared with striatum's primary claude-code reviewer, which is the
`supervised_only` reason in `sweep-config.json` felt in practice. GLM-flash
ran on the Z.ai coding plan without a refusal, at roughly 13 minutes per
pair — the tier is not faster than GLM-max on this work. Two sweeps were
also stopped by the tree guard on churn in `striatum-next` that was not
CAPLAB's (129 modified and 23 added-deleted entries from upstream
activity); they resumed from their usable rows.

## Results on the iso-v1 cohort (57 scored pairs each)

Scoring excludes the quarantined v1-changeset cells, so every subject on
this cohort is read on the same 57 cases.

| binding | catch | 95% CI | false alarm | catch − FA | anchored |
|---|---|---|---|---|---|
| `agy-gemini-3-7-flash-high` | 0.596 | [0.47, 0.71] | 0.088 | 0.509 | — |
| `or-gemini-3-7-flash-high` | 0.500 | [0.37, 0.63] | 0.000 | 0.500 | — |
| **`claude-fable-5-1-high`** | **0.667** | [0.54, 0.78] | 0.175 | 0.491 | 0.579 |
| `cc-glm-5-3-max` | 0.526 | [0.40, 0.65] | 0.158 | 0.368 | — |
| `oc-glm-5-3` | 0.544 | [0.42, 0.67] | 0.193 | 0.351 | — |
| **`cc-glm-5-3-flash-high`** | 0.518 | [0.39, 0.64] | **0.304** | 0.214 | — |

The ledger claim for fable 5.1 carries FA 0.191 and discrimination 0.475
after the adjudication path; the table's 0.175/0.491 is the run-level
score. Both are stated; neither is the other's correction.

### Matched contrasts (exact sign test on shared cases)

| contrast | shared | catch a vs b | a-only / b-only | p | false alarms a vs b | FA p |
|---|---|---|---|---|---|---|
| fable 5.1 vs cc-glm-5-3-max | 57 | 0.667 vs 0.526 | 10 / 2 | **0.039** | 9 vs 5 | 0.289 |
| fable 5.1 vs cc-glm-5-3-flash | 56 | 0.661 vs 0.518 | 10 / 2 | **0.039** | 9 vs 12 | 0.508 |
| fable 5.1 vs agy-gemini-3-7-flash-high | 57 | 0.667 vs 0.596 | 8 / 4 | 0.388 | 9 vs 3 | 0.070 |
| cc-glm-5-3-flash vs cc-glm-5-3-max | 56 | 0.518 vs 0.536 | 4 / 5 | 1.000 | 12 vs 5 | **0.039** |

## Reading

**Fable 5.1 is the highest catch on the iso-v1 cohort** and the lead over
both GLM tuples is established on matched cases (10–2, p=0.039, twice). Its
lead over Gemini 3.7 Flash on the agy harness is not established (8–4,
p=0.388): the two are within each other's intervals on catch, and Gemini
holds the lower false-alarm rate. On the combined reading — catch minus
false alarm — fable 5.1 (0.49) and agy-gemini-3-7-flash-high (0.51) sit
together at the top of this cohort, separated by nothing the sample can
resolve.

**Where fable 5.1 catches and misses.** It clears every prose-class defect
that the strongest reviewers clear (contradicted clause, scope violation,
refuted conclusion, duplicated section, truncated tail, unearned
verification claim: 27/27), and it is weak where the whole fleet is weak,
the structural classes: 9 of 24 (dropped section 2/5, hash mismatch 1/5,
base dropped 1/5, hollow delivery 1/5). Gemini 3.7 on agy is 10/24 on the
same classes, GLM-max 6/24, GLM-flash 5/24. Nothing on this cohort under
isolation catches structural defects at more than 42%; that ceiling is the
environment's (the base is withheld), and the record of 2026-08-23 says why.

**Its false-alarm rate is the cost.** 13 refusals across 69 controls
(0.175 on the scored 57), against 0.088 for Gemini 3.7 and 0.000 for the
OpenRouter lane. Eleven of the pairs behind that number are on controls no
one has audited, so the rate is an upper bound: Sol's audit found ten of
twenty refused controls genuinely defective, and the same audit is owed
here before the number is read as a property of fable rather than of the
corpus. Three of the refusals cluster on `requirement_inversion` controls,
the class whose controls were most often found defective before.

**GLM-5.3-flash is not GLM-5.3 at a lower price.** Its catch is
indistinguishable from GLM-max on matched cases (4–5, p=1.0) while its false
alarms are established higher (8–1, p=0.039, upper bound as above), it
caught 5 of 23 structural defects, and it took as long per pair. On this
instrument the flash tier buys nothing over the full model on the same
harness and costs precision. The effort confound named on its declaration
(high against max) cuts the other way — a higher-effort flash would be
expected to do better, not worse — so it does not rescue the reading.

**Against the declarations.** Both tuples were minted `review: baseline`,
`basis: declared`. On this evidence fable 5.1 sits in the band the fleet
calls *strong* (catch above Sol's cohort peers, discrimination with the
Gemini leader); GLM-flash sits below GLM-max, which is itself declared
*strong* on a pre-isolation 0.541 that isolation re-measured at 0.420.
Neither number changes a declaration — that is a Principal decision on the
claim, after the control audit.

## What is still owed

- The GLM-flash 69th pair, then its claim and leaderboard entry.
- Gemini 3.8 Flash: 32/69; the agy probe timed out ten times in a row
  during the calibration run and the sweep is resuming under a 30-retry
  probe. Its interim catch (0.81 at n=31) is the highest seen on this
  cohort and is not a claim.
- The false-alarm audit of fable 5.1's 13 refusals (dossier, oracle-first,
  Principal rulings on the residue), in the pattern of 2026-08-23.
- `codex-sol-high` answers again (PROBE-OK at 15:5xZ after a day of 404);
  its return to the calibration jury is decision 4 of the design document.
