# Amendment — the 20260817 claim scored four pairs the subject never completed

- Date: 2026-08-17
- Amends: claim `qc-012aaec54202273a` (superseded by `qc-0d23bbbcdd183ea6`)
- Run: `advisory/pool-runs/sweep-agy-gemini-3-7-flash-high-20260817/` (rows unchanged; the reading changed)

## What was wrong

Both the runner and the scorer treated a pair as usable when **either** arm
produced a parseable review. Four pairs in the sweep had exactly one:

| substrate | operator | dead arm | how it died | scored as |
|---|---|---|---|---|
| `qs-63c927db22c142d9` | `hollow_delivery` | control | stdin-oversize fallback, 0.1 s, never asked | no false alarm |
| `qs-9f2748c49dd3313e` | `base_dropped` | mutant | 900 s, almost certainly timeout | miss |
| `qs-f90cc496593e109e` | `hash_mismatch` | mutant | 900 s, almost certainly timeout | miss |
| `qs-5813a15dba528027` | `scope_violation` | mutant | 149 s, unparseable output | miss |

A dead mutant arm is not a miss and a dead control arm is not a clearance;
both readings invent an answer the subject never gave. "Almost certainly
timeout" is an inference from the 900 s ceiling — the rows carry no exit code
and no timeout flag, which is itself one of the defects fixed alongside this
amendment.

## Corrected numbers (45 clean pairs, was 49)

| metric | published | amended |
|---|---|---|
| catch rate | 0.816 (0.69–0.90) | **0.867** (0.74–0.94) |
| false-alarm rate | 0.163 (0.09–0.29) | **0.133** (0.06–0.26), still `contains-unaudited-refusals` |
| discrimination | 0.653 | **0.733** |
| anchored detection | absent from the claim | **0.644** (29/45, basis `recorded-anchors`) |

Pair-level exclusion also removes two live control refusals (`base_dropped`,
`hash_mismatch`) whose mutant arms died; those refusals stay in the rows and
still belong in the control-soundness audit. The document/change-set split
sharpens rather than closes: 0/37 document false alarms against 8/11
change-set controls actually asked (the twelfth was the dead arm above).

Per-operator, three of the published misses were artifacts of dead arms:
`hash_mismatch` 1/2 → 1/1, `base_dropped` 2/3 → 2/2, `scope_violation`
3/4 → 3/3. The two weak operators survive scrutiny — `swapped_section_bodies`
1/4 and `overclaimed_level` 1/3 are genuine `accept` verdicts on live arms.

## The reliability block conflated three statistics

The published report read anchor unanimity (7/12 control) as reproducing the
2026-08-16 cross-sweep agreement (53%) "by an independent method". Unanimity,
within-sweep pairwise agreement, and cross-sweep agreement are three
different statistics, and the anchor verdicts also contain five null
replicates the unanimity flags silently drop — one "unanimous" mutant case
has a single parsed replicate.

The statistic now reported, on this sweep's anchor set: replicate pairwise
agreement on refuse/clear, null pairs excluded and counted — control 69%
against a 64% chance baseline (kappa 0.13), mutant 87% against 84%
(kappa 0.22). The honest reading is narrower than the published one: the
control arm's verdicts are near chance once base rate is removed, and the
mutant arm's stability is mostly base rate (it nearly always refuses). The
53% figure is not reproduced or contradicted by this sweep; it is a
different measurement.

## Errata in the published report, for the record

- "Failed cases: median 157 KB" — the median of the eight discarded sizes is
  148 KB; 157 is the upper-middle element.
- The handoff's "three discards were every case of `unearned_verification_claim`"
  — the operator had four attempts, one usable.
- The handoff's "no usable arm had a prompt over the fallback threshold" —
  one did, and it is the dead control arm above.

## What this amendment does not establish

- Nothing about control soundness; the false-alarm figure still awaits the
  audit of the refused change-set controls.
- Nothing about any other Binding, and no cross-family ordering.
- The 900 s timeout attribution for two mutant arms is inference, not record.
