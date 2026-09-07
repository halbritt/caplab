# Review instrument: disposition below the validation floor

- Date: 2026-09-07. Per `instruction-2026-09-07-review-validation-study.md`
  §2: the ledger pass (`criterion-2026-09-07-review-ledger-pass.md`) found
  0 gold positives against a floor of 5, so the study stops before any
  replay and the planning disposition
  (`report-2026-09-04-planner-ranking-disposition.md`) is applied to review.
  Nothing in this record spends a model call. The Principal has not yet read
  the counts; this disposition is what the pre-registered rule requires and
  stands until the Principal says otherwise.

## What the ledger can and cannot say

- **6,042** anchored production change-set reviews, **3,162** with a
  retained verdict.
- **0** Principal re-rulings of a change-set review verdict, in either
  direction. Every Principal acceptance ruling in the ledger is on a
  proposal, design, implementation plan or decision record. Striatum has no
  event for "this review verdict was wrong", so the gold strata cannot be
  formed from the ledger as it stands.
- **109 / 48 / 3**: silver-defect runs, distinct versions, distinct defect
  records. The only "cleared, then a defect record" signal is three
  request-level cancellations, two of them naming a lineage or process
  defect rather than the reviewed version. No integration conflict other
  than "tree moved" ever followed a clearance.
- **147 / 137**: bronze-clear runs and versions — cleared, applied, nothing
  since. Latent-defect caveat unresolved.
- Refused-then-revised: 450 runs, excluded by rule.

A criterion set with no gold cannot validate a reviewer ranking, and a
silver set drawn from three cancellations cannot stand in for one.

## Disposition (the planning disposition, applied to review)

1. **No ranking.** The injection instrument produces no placement ordering.
   Its catch dimension is retired from qualification claims outright: on
   the five operators with a natural analog, eight of nine bindings catch
   13/13 (`finding-2026-09-07-operator-analogs.md`); the ordering the board
   carried came from operators that plant defects production does not
   produce. Its false-alarm dimension stays descriptive under the iso-v1
   caveat already recorded.
2. **Admission gate, per reviewer, pass/fail.** Mechanical where possible:
   - contract conformance: answers in the review-ledger shape under the
     production pass contract (`review-pass-contract-649545a9.yaml`),
     honours verdict discipline (a refusal names the falsified clause,
     violated decision, or demonstrated harm);
   - the five analog operators as a **regression sentinel** with a floor
     (proposed: ≥ 12/13 caught, ≤ 2/9 sound controls refused, on the
     20260819 cells; the two one-shot lanes measured on the same cells);
   - the Stage B mount is the only environment (§0.4).
   A binding that fails the gate is not a reviewer; among those that pass,
   nothing on this instrument prefers one over another.
3. **Operational routing** among admitted reviewers in Quartermaster, on
   cost, latency and availability, never on an injection score.
4. **Production canary with a per-reviewer floor.** The ledger already
   records, per review run, the verdict, the later application or
   conflict, and the Principal's acceptance rulings on downstream
   artifacts. A per-binding first-pass canary reads those prospectively:
   clearances later cancelled with a defect record, refusals later
   revised into acceptance, and (once striatum records them) verdicts the
   Principal overrules. This is the instrument that measures the
   construct; it needs the gold event to exist.
5. **Criterion replay stays parked**, not abandoned. It un-parks when the
   ledger holds ≥ 5 gold positives in the change-set class, which requires
   the striatum change below.

## Owed to striatum (finding)

Record Principal re-rulings of review verdicts as ledger events: a
`gate_result` of class `acceptance` (or a new class) whose applicability
names the **change-set version** and whose detail names the review run
overruled. Without it, no review instrument can ever be validated against
the Principal's judgment, and the gold strata stay empty by construction.
Filed beside `finding-2026-09-06-prose-reviews-world-blind.md`.

## Standing orders applied today

- No injection-instrument spend (the tree-v1 dry run was stopped at its
  first case; no sweep is scheduled).
- Board: placement-frozen banner; claims re-issued on the five analog
  operators; the eleven others reported as sentinel rows only.
- Every claim carries the standing-order note.
- Operators classified in code (`QUALIFICATION_OPERATORS`,
  `SENTINEL_ONLY_OPERATORS`) and in the finding record.

## Residuals

Accept-path bias (negatives dominate: 147 bronze to 109 silver from three
records), builder confound on silver (a cancelled request cancels every
packet's change set regardless of which review was wrong), latent defects
in bronze, and contract provenance: the rendered dispatch prompt is not
retained anywhere, only the pass-contract object, so any future replay is
"under this contract" by construction.
