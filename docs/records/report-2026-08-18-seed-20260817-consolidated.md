# Consolidated results — seed 20260817, synthetic-contract instrument

- Date: 2026-08-18
- Case set: seed 20260817, open partition, 57 breadth cases + 12 anchors,
  identical draws and injections for all three Bindings.
- Runs: `sweep-agy-gemini-3-7-flash-high-20260817b`,
  `sweep-agy-gemini-3-7-flash-medium-20260817`,
  `sweep-claude-harm-fable-5-high-20260817c` (completed on the third quota
  window; the two aborted attempts are kept beside it and yield no claims).

## Scored claims

| Binding | claim | pairs | catch | false alarms | discrimination | anchored |
|---|---|---|---|---|---|---|
| agy-gemini-3-7-flash-high | `qc-fc8146093574b024` | 55 | 0.891 (0.78–0.95) | 0.130 (denom 54) | 0.761 | 0.691 |
| claude-harm-fable-5-high | `qc-3b7e3886c44d5509` | 54 | 0.759 (0.63–0.85) | 0.094 (denom 53) | 0.665 | 0.648 |
| agy-gemini-3-7-flash-medium | `qc-74e47b03b461d218` | 57 | 0.702 | 0.107 (denom 56) | 0.595 | 0.526 |

Every false-alarm figure still carries unaudited refusals.

## Matched contrasts — the campaign's product

All three pairs, same seed, same injections, exact sign test over discordant
pairs:

| contrast | shared | catch discordance | p | verdict |
|---|---|---|---|---|
| flash-high vs flash-medium | 55 | 11–1 | **0.006** | **separates** |
| flash-high vs fable-5-high | 52 | 10–4 | 0.18 | not established |
| flash-medium vs fable-5-high | 54 | 6–10 | 0.45 | not established |

False alarms separate no pair (p = 1.0, 1.0, 1.0).

**The reading: this corpus discriminates effort tiers within a family, and
at n ≈ 52 it does not discriminate across families.** flash-high leads fable
on every absolute metric and still cannot be shown to differ from it
case-for-case, because the two disagree in both directions (10 cases one
way, 4 the other) where flash-high vs flash-medium disagrees almost entirely
in one (11–1).

A caution the campaign should keep: the truncated fable run's preview
reported 8–1 and p = 0.039 on 26 shared cases. The completed run reports
10–4 and p = 0.18 on 52. The early number was a sampling artifact of an
aborted run, and it pointed the wrong way. Previews from incomplete runs are
not weak evidence; they are not evidence.

## Within-Binding consistency is a property of the subject

Anchor-set replicate agreement (refuse/clear, null pairs excluded), same 12
anchor cases for each subject:

| Binding | control pairwise (kappa) | mutant pairwise (kappa) |
|---|---|---|
| claude-harm-fable-5-high | 89% (0.68) | 89% (0.75) |
| agy-gemini-3-7-flash-medium | 89% (0.54) | 89% (0.60) |
| agy-gemini-3-7-flash-high | 69% (0.13) | 87% (0.22) |

flash-high is the strongest catcher and the least self-consistent. Since
within-Binding variance limits confidence that a between-Binding difference
is real, contrasts involving flash-high need more cases per conclusion than
contrasts among its steadier siblings — which is one plausible reason the
cross-family contrast stayed unresolved at this n.

## Promotion gate

0 promoted, 42 withheld across the three contrasts, every one for
"reproduction not established: seen in 1 sweep(s)". The corpus stays empty
by design until a second seed reproduces a separation.

## Projection

`matched_prefix_depth` fell from 3 to 2: fable-5-high holds only a
seed-20260817 synthetic-contract claim and ranks third, breaking the
seed-20260815 dispatch cohort that occupies ranks 1–2. Correct behavior, and
it will resolve when the gemini tiers hold synthetic-contract claims that
`most-comparable` prefers, or when a second seed widens the cohort.

## What this does not establish

- No cross-family ordering. The one cross-family question this campaign has
  ever been able to ask came back "not established".
- No promotion-grade case: every contrast is one seed deep.
- The false-alarm axis still carries unaudited refusals on all three claims.
- Nothing about the sealed partition.
