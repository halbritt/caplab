# Targeted reproduction, seed 20260820 — 7 of 19 separators hold

- Date: 2026-08-20
- Case set: the 19 withheld flash-high/flash-medium separators from seeds
  20260817 and 20260819 (`advisory/replay/replay-flash-effort-20260820.json`),
  re-injected under fresh seed 20260820 — reproduction under perturbation,
  not replay — plus the 12 pinned anchors. Same instrument, replication
  (control r=3, mutant r=1; anchors r=3 both arms), adjudication ledger and
  promotion gate as the seed sweeps.
- Subjects: `agy-gemini-3-7-flash-high`, `agy-gemini-3-7-flash-medium`.
  Both runs completed 31/31 usable, no aborts, one released-and-re-measured
  lane failure on the high run.
- Runs are stamped `case_selection: targeted-reproduction` and can never
  yield a Scored claim: the cells are in the sample *because* high caught
  them and medium missed them, so any rate over them is biased by
  construction. This sweep feeds the discrimination corpus only.

## Result: the separation is real at the case level

Of the 19 cells that ever separated the pair:

| outcome | cells |
|---|---|
| separated again, same direction | **7** |
| concordant — both caught | 10 |
| concordant — both missed | 2 |
| direction flip | **0** |

Every reproduced separation points the same way: flash-high caught, flash-
medium missed. The formal sign test on the contrast is 7–0 (p = 0.016) but
the contrast document itself says what that number is here: on outcome-
selected cases it is not a discovery statistic. The honest reading is the
reproduction rate — 7 of 19, with zero reversals — and the fate of the one
cell that ever separated toward medium (`qs-97f00c690d343f8b`): this sweep
both arms caught it, so the 20260817 reading of it dissolves as instability
rather than capability, exactly as the gate would have scored a flip.

The seven reproduced cells, now seen separating in two distinct sweeps:

| substrate | defect class | sweeps |
|---|---|---|
| `qs-5ebab1a249b89eb2` | dropped_section | 20260817, 20260820 |
| `qs-8f41b707cb15f6d9` | dropped_section | 20260819, 20260820 |
| `qs-afa3ff9b86200498` | dropped_section | 20260819, 20260820 |
| `qs-aae295d9adf3871e` | base_dropped | 20260817, 20260820 |
| `qs-aba90dbe009e7ea2` | dangling_reference | 20260817, 20260820 |
| `qs-d24d0d472c7a9316` | swapped_section_bodies | 20260819, 20260820 |
| `qs-ec76afd5d7b27ffd` | overclaimed_level | 20260819, 20260820 |

Structural omission dominates: five of seven are section/base drops or body
swaps. Effort level appears to buy the reading-completeness that notices
something is *missing*, which single-pass review at lower effort skims past.

The twelve cells that did not reproduce are the cost of regression to the
mean, paid honestly: ten collapsed to both-caught (medium catches on a
different injection of the same defect), two to both-missed (high's prior
catch was itself the lucky draw). They stay at one sweep and stay withheld.

## Promotion: the gate now points at exactly one blocker

0 promoted, 19 withheld — but the reasons split for the first time:

- **7 cells** clear reproduction and direction and are withheld solely on
  `control disposition is 'unadjudicated', not 'sound'`.
- 12 cells remain at "seen in 1 sweep(s)".

The promotion gate's second hurdle is now the whole story: each of the seven
controls needs an affirmative `sound` adjudication, and the adjudication
module admits only two bases — a mechanical oracle, or a named human
adjudication. Per the no-pre-scripted-resolutions rule these are individual
calls for the Principal (or oracle runs where a deterministic check exists);
nothing here was auto-adjudicated. **This queue of seven is the deliverable.**

## False alarms: still nothing

On the 19 targeted cells: high 3 refusals of controls, medium 0, discordant
3, p = 0.25 — and all 3 sit on unaudited controls, so they join the standing
audit backlog rather than a conclusion. The false-alarm axis has still never
separated any pair on any sweep.

## Instrument blocks

Anchor reliability (replicate pairwise, refuse/clear): high control kappa
0.67 (its best yet; 0.13 → 0.53 → 0.67 across sweeps), medium control kappa
0.29 (its worst; 0.50 on 20260819). Mutant arms remain near ceiling and
their kappas stay unreadable as agreement.

Cross-seed anchor drift 20260819 → 20260820: both subjects moved again
(caught agreement 92% each, false-alarm agreement 75% / 83%). Three sweeps
in a row the anchors have moved somewhere; the instrument keeps saying
"Binding or instrument changed" and still cannot say which. This is now a
standing caveat on every claim of this period, and a candidate for its own
investigation.

## What this establishes, and what it does not

Established: the flash effort separation survives targeted re-measurement at
the case level — seven specific (substrate, defect class) cells separate the
pair in two independent sweeps, never in the reverse direction, concentrated
in structural-omission defects. The promotion corpus is no longer starved by
sampling; it is gated only on control adjudication.

Not established: any promoted case (adjudication pending), anything about
false alarms, anything across families, and the anchor-drift question is
getting louder rather than quieter.

Artifacts: contrast
`advisory/comparisons/gemini-3-7-flash-high-vs-medium-20260820-replay.json`
(annotated outcome-selected); runs
`advisory/pool-runs/replay-agy-gemini-3-7-flash-{high,medium}-20260820/`;
report JSON reproducible via `scripts/replay_20260820_report.py`.
