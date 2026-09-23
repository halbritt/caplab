# The admission gate cannot admit a reviewer; review placement is unmeasured

- Date: 2026-09-23. Evidence: the first two live runs of `scripts/review_gate.py`,
  `advisory/pool-runs/gate-codex-harm-gpt-6-luna-xhigh-20260923/` and
  `advisory/pool-runs/gate-claude-opus-5-5-high-20260923/`.

## Finding

The per-binding admission gate kept by the
[2026-09-14 decision](decision-2026-09-14-review-ranking-goal-disposition.md)
cannot produce an admission decision as built:

1. **Its controls are mislabelled.** On 5 of the 12 scorable cells
   (qs-4298b567, qs-a17d0d0b, qs-d05784fe, qs-d8054c75, qs-e95b9a19) both
   bindings refused all three "sound" controls. On qs-4298b567 both cited, on
   their own, the same omission against DESIGN.md. The dispositions are
   ledger labels that were never revalidated under tree-v1, so the floor of
   "at most 2 sound controls refused" cannot be met by a competent reviewer.
2. **A quarter of its cells never run.** The runner refuses all four
   `unearned_verification_claim` cells before any call ("oracle unverified").
3. **Its floors were never adopted**, so no result could pass or fail.

| | Opus 5.5 high | GPT-6 Luna xhigh |
|---|---|---|
| sound controls refused (of 30) | 16 | 26 |
| same, excluding the 5 disputed cells (of 21) | 1 | 11 |
| natural case refused with exact anchor (of 3) | 0 | 1 |
| scorable mutants missed (of 12) | 0 | 0 |

## Consequences, effective now

- **The gate is retired.** It is not run for any new binding. Fixing it would
  mean re-adjudicating controls by hand, the same witness-building work
  stopped on 2026-09-14.
- **Review placement is unmeasured.** Every `review` quality class in
  striatum-next's backends is declared or transferred, not measured,
  including `claude-opus-5-5-high` (`review: strong`,
  `transferred-pending-measurement`). No CAPLAB instrument currently changes
  that. The production canary cannot grade verdicts until striatum records
  Principal re-rulings of review verdicts
  ([filed request](request-2026-09-07-striatum-review-outcome-events.md)).
- **What remains descriptive:** GPT-6 Luna xhigh refuses far more than
  Opus 5.5 high on the same material (11 of 21 vs 1 of 21 outside the disputed
  cells). This is consistent with the 2026-09-06 finding that false-alarm
  behaviour, not catch rate, separates subjects. Luna's declaration carries no
  review pass type, so nothing changes.
- No backend declaration changes, and no CAPLAB model spend is authorized by
  this record.
