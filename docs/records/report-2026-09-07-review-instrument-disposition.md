# Review instrument: disposition below the validation floor

- Date: 2026-09-07. Per `instruction-2026-09-07-review-validation-study.md`
  §2: the ledger pass (`criterion-2026-09-07-review-ledger-pass.md`) found
  0 gold positives against a floor of 5, so the study stops before any
  replay and the planning disposition
  (`report-2026-09-04-planner-ranking-disposition.md`) is applied to review.
  Nothing in this record spends a model call. **Confirmed by the Principal
  2026-09-07, amended per
  `instruction-2026-09-07-review-instrument-disposition.md`** (Council
  #71–#76); the amendments are folded in below and marked.

## Counts at the incident level (amendment 2.a)

| stratum | independent records | families | versions | runs |
|---|---|---|---|---|
| gold-defect | **0** | 0 | 0 | 0 |
| gold-clear | **0** | 0 | 0 | 0 |
| silver-defect | **3** cancellation records; **1** (320479) names a defect of the reviewed artifact, 2 name a lineage or lowering-process defect | 3 | 48 | 109 |
| bronze-clear | absence of an event | **15** | 137 | 147 |

Un-parking floor for the criterion replay: ≥ 5 gold-defect and ≥ 5
gold-clear at this unit. **CAPLAB holds no independent, adjudicated
production outcomes sufficient to rank reviewers** (amendment 2.b); the 109
silver and 147 bronze rows are a defect-harvest source, and nothing is
scored against them.

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
2. **Admission gate, per reviewer, pass/fail** (as amended, 2.d; specified
   in `advisory/gate/review-gate-20260819.json`, run by
   `scripts/review_gate.py`):
   - cells: the five analog operators on the seed-20260819 draw (16 cells;
     13 were scorable per binding under iso-v1), the natural case from
     cancellation 320479 verbatim (amendment 2.c), and contract conformance
     under `review-pass-contract-649545a9.yaml`;
   - the false-alarm floor is measured under the Stage B mount only; iso-v1
     false-alarm rows count neither for nor against any binding at the gate;
   - call count per binding: 16 cells × (3 control replicates + 1 mutant)
     + 3 replicates of the natural case = **67 calls** (a cell an operator
     cannot bite on costs nothing and is reported as not applicable);
   - floors are proposed, not adopted: at most 2 scorable analog cells
     missed; at most 2 sound controls refused; the natural case refused
     with a finding anchored at `result_tree_hash` in at least 2 of 3;
     3 of 3 outputs conform;
   - **no fleet re-measurement now.** The gate runs for a new binding, or
     for a binding the Principal names; that per-binding spend is
     authorized on request and nothing else on the injection instrument
     spends;
   - prose reviews: no CAPLAB instrument; production pins no base for them
     (`finding-2026-09-06-prose-reviews-world-blind.md`, with striatum).
   A binding that fails the gate is not a reviewer; among those that pass,
   nothing on this instrument prefers one over another.
3. **Operational routing** among admitted reviewers in Quartermaster, on
   cost, latency and availability, never on an injection score.
4. **Production canary, per reviewer, report-only** (amendment 2.e). The ledger already
   records, per review run, the verdict, the later application or
   conflict, and the Principal's acceptance rulings on downstream
   artifacts. A per-binding first-pass canary reads those prospectively:
   clearances later cancelled with a defect record, refusals later
   revised into acceptance, and (once striatum records them) verdicts the
   Principal overrules. It reads the ledger prospectively and reports; it
   makes no placement decision until the gold event (see "Owed to
   striatum") exists. This is the instrument that measures the construct.
5. **Criterion replay stays parked**, not abandoned. It un-parks when the
   ledger holds ≥ 5 gold-defect and ≥ 5 gold-clear cases at the incident
   level in the change-set class, which requires the striatum change below
   (drafted for signature in
   `request-2026-09-07-striatum-review-outcome-events.md`).

## Owed to striatum (finding)

Record Principal re-rulings of review verdicts as ledger events: a
`gate_result` of class `acceptance` (or a new class) whose applicability
names the **change-set version** and whose detail names the review run
overruled. Without it, no review instrument can ever be validated against
the Principal's judgment, and the gold strata stay empty by construction.
Filed beside `finding-2026-09-06-prose-reviews-world-blind.md`.

## Rulings carried (instruction §1)

- Standing orders §0.1–§0.4 of the study instruction stay in force with no
  end date: no injection sweep on any seed or cohort; placement-frozen
  board; the eleven no-analog operators sentinel only; the Stage B mount
  the only environment.
- Existing permitted review tuples stay (#40, #41). No new qualification or
  negative-placement decision cites the injection instrument or the iso-v1
  false-alarm axis. Sol's `review: frontier` placement stays provisional.
- `plan-tree-v1-review-environment.md` (rev 2) is `parked`; the environment
  it built (materializer, base registry, change-set oracle, contract v3,
  Stage B mount, workspace teardown) is the gate's environment. Nothing is
  deleted; the scheduled sweeps do not run.

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
