# Executing the review-instrument disposition: what changed

- Date: 2026-09-07. Per `instruction-2026-09-07-review-instrument-disposition.md`
  §5. Zero model spend. Nothing spends until the Principal has read this,
  except gate runs the Principal requests by binding name.

## Rulings applied (§1)

- The ledger pass stands as written; the study stopped at its floor. No
  pre-registration record, no replay, no steps 3 or 4.
- `report-2026-09-07-review-instrument-disposition.md`: header now reads
  "confirmed by the Principal 2026-09-07, amended per …"; amendments 2.a–2.e
  folded in and marked.
- Standing orders §0.1–0.4 in force with no end date. Existing permitted
  tuples untouched; Sol's `review: frontier` stays provisional.

## Incident-level counts (amendment 2.a)

| stratum | independent records | families (passes) | identities | versions | runs |
|---|---|---|---|---|---|
| gold-defect | 0 | 0 | 0 | 0 | 0 |
| gold-clear | 0 | 0 | 0 | 0 | 0 |
| silver-defect | 3 cancellation records; 1 (320479) names a defect of the reviewed artifact | 3 | 12 | 48 | 109 |
| bronze-clear | absence of an event | 15 | 89 | 137 | 147 |

Placed above the run-level table in the ledger-pass record and in the
disposition. Un-parking floor: ≥ 5 gold-defect and ≥ 5 gold-clear at this
unit. CAPLAB holds no independent, adjudicated production outcomes
sufficient to rank reviewers; that sentence is in the disposition, the board
banner and the export notice (amendment 2.b).

## Code

| change | where |
|---|---|
| `admission-gate` case selection: accepted by the runner, never a claim | `pool_runner.select_cases`, `scoring.outcome_selected` |
| gate specification | `advisory/gate/review-gate-20260819.json` |
| gate runner: `--plan` (no spend) and `--run <binding>` | `scripts/review_gate.py` |
| natural-case conformance check (verdict set, anchored refusal, verdict discipline) | `review_gate.conformance` |
| tests | `tests/test_review_gate.py` (3), all advisory suites green |
| board: banner sentence, newest-claim-wins | `scripts/build_leaderboard.py`, `docs/leaderboard/index.html` rebuilt |
| export notice carries the standing order and the supersession | `caplab.advisory.export`, `advisory/caplab-advisory-export.json` regenerated |

Already in place from the study's §0: `QUALIFICATION_OPERATORS` /
`SENTINEL_ONLY_OPERATORS`, sentinel rows excluded from catch and false alarm
and reported under `sentinel_by_defect_class`, claims re-issued on the five
operators with the standing-order note.

## Gate specification as it stands in code

- **Environment:** tree-v1 under the Stage B mount, the case's base
  materialized read-only from the base registry; the only environment a gate
  run may use (`review_gate.py` refuses without bwrap).
- **Cells:** 16 cells of the seed-20260819 draw on the natural-analog
  operators — `contradicted_clause` 5, `refuted_conclusion` 5,
  `unearned_verification_claim` 4, `broken_internal_crossref` 2. **The draw
  holds no `decorative_check` cell**; the fifth analog operator is in
  qualification scoring but not in the gate until a cell is drawn for it.
  Under iso-v1, 13 of the 16 were scorable per binding (three were not
  applicable to their operator).
- **Natural case:** `cancellation-320479-empty-patch`, verbatim, 3
  replicates, rendered under `review-pass-contract-649545a9.yaml` with the
  tree-v1 preamble and pinned-set statement, declared base (32 files,
  `8dd2928b…`) materialized. Expected: refusal anchored at
  `result_tree_hash`.
- **Conformance:** mechanical, on the natural-case outputs — verdict in the
  contract's set; a refusal carries an anchored finding; rationales name a
  clause, a decision, or a harm.
- **Call count per binding:** 16 × (3 control + 1 mutant) + 3 = **67**.
- **Floors (proposed, not adopted):** ≤ 2 scorable analog cells missed; ≤ 2
  sound controls refused, Stage B rows only; natural case refused and
  anchored in ≥ 2 of 3; 3 of 3 conform.
- **When it runs:** a new binding, or a binding the Principal names.
  Nothing has run.

## Sentinel suite contents

- Eleven no-analog operators: `base_dropped`, `dangling_reference`,
  `dropped_section`, `duplicated_section`, `hash_mismatch`, `hollow_delivery`,
  `overclaimed_level`, `requirement_inversion`, `scope_violation`,
  `swapped_section_bodies`, `truncated_tail` — measured on every gate run,
  reported, never scored.
- One natural case, `cancellation-320479-empty-patch` (amendment 2.c),
  recorded in `finding-2026-09-07-operator-analogs.md`; `hollow_delivery` not
  promoted.

## Documents (§3)

- `docs/product/plans/plan-tree-v1-review-environment.md`: `status: parked`,
  banner pointing at the disposition; steps 7–9 do not run; nothing deleted.
  (There is one plan file in the repository; revision 2 superseded revision
  1 in place.)
- `doc/designs/caplab-system-design.md` §4.3: the review construct described
  in the present tense — ranking retired with both reasons, admission gate,
  sentinel, report-only canary, what exists in code.
- `docs/leaderboard/index.html` rebuilt from the re-issued claims;
  `advisory/caplab-advisory-export.json` regenerated with the notice. Records
  under `docs/records/` keep their historical numbers as history.

## Draft request to striatum (§4)

`docs/records/request-2026-09-07-striatum-review-outcome-events.md`, seven
items: re-ruling event for review verdicts (both directions, keyed to the
change-set version and the overruled run); rendered-prompt retention
(`prompt_asset_hashes` empty on 6,042 runs, 0 dispatch dirs retained); a
review budget field (none today; `deadline_class: batch` only); review-to-
outcome linkage; the verdict-retention gap (2,880 of 6,042 with no verdict
body); prospective gold accrual by blinded routing; escalation-on-dissent for
the overclaim class as striatum's own lane-design option. Not filed.
