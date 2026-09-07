# Review-instrument validation study, step 1: the ledger pass

- Date: 2026-09-07. Instruction:
  `~/council-artifacts/caplab/instruction-2026-09-07-review-validation-study.md`
  §1. Zero model spend. Script: `scripts/review_criterion_ledger_pass.py`
  (ledger export of 2026-09-06, 373,371 events). Outputs:
  `advisory/criterion/review-criterion-summary.json`,
  `advisory/criterion/review-criterion-cases.jsonl` (one row per labelled
  review run), `advisory/criterion/review-pass-contract-649545a9.yaml`.

## Population

Anchored-era production review runs: `pass_run_opened` with `pass_id:
review` and a `materialized_base` input pin. **6042 runs**, every
one a change set (the only artifact class striatum reviews with a pinned
base). Repo-doc reviews do not exist in production: the repo-doc corpus is
caplab's, and the class is empty here by construction. Prose reviews are
excluded per the instruction.

Verdicts: 3162 runs have a review-ledger
artifact whose body is in the object store (verdict, findings, summary);
2880 have none (the run closed `canceled`,
`submitted_partial` without a ledger, `abandoned`, or `error`). No run has a
review gate result without a ledger body.

## Predicates (exact; reproducible by the script)

| stratum | predicate on the same artifact version, after the review run |
|---|---|
| gold-defect | review cleared (`accept`/`accept_with_findings`) AND a Principal `gate_result` of class `acceptance` on that `content_hash` has outcome `fail` |
| gold-clear | review refused (`needs_revision`/`reject`) AND such a ruling has outcome `pass` |
| silver-defect | review cleared AND (an `integration_conflict` names the change set as `losing_change_set_pin` with a class other than "tree moved", OR a Principal `cancellation_record` on the run's `request_ref` whose reason matches `defect|wrong|incorrect|false claim|fabricat|contradict|hollow|does not (deliver|implement|match)`) |
| bronze-clear | review cleared AND an `application_record` applied the change set AND no later acceptance fail, conflict, or defect-worded cancellation names it |
| excluded | review refused AND a later `version_seq` of the same identity exists |

"Tree moved" conflicts (355 of 380 in the ledger) are staleness of the base
against a moved head, a builder/timing event, and are not counted as a defect
of the reviewed artifact; they are reported as their own row.

## Counts

| stratum | runs | distinct versions | by binding | by era |
|---|---|---|---|---|
| **gold-defect** | **0** | 0 | — | — |
| **gold-clear** | **0** | 0 | — | — |
| **silver-defect** | 109 | 109 | agy-claude-opus-4-6-thinking 2, agy-gemini-3-6-flash-medium 10, agy-gemini-3-7-flash-high 74, agy-gemini-3-7-flash-medium 2, claude-harm-opus-4-8-high 8, codex-sol-max 13 | 2026-07 31, 2026-08 78 |
| **bronze-clear** | 147 | 147 | agy-gemini-3-1-pro-high 25, agy-gemini-3-1-pro-low 1, agy-gemini-3-6-flash-high 9, agy-gemini-3-6-flash-medium 23, agy-gemini-3-7-flash-high 71, agy-gemini-3-7-flash-medium 10, cc-glm-5-3-max 2, claude-fable-5-high 2, claude-harm-fable-5-high 1, claude-harm-opus-4-8-high 2, codex-sol-max 1 | 2026-07 3, 2026-08 124, 2026-09 20 |
| excluded (refused, then revised) | 450 | 449 | agy-gemini-3-1-pro-high 37, agy-gemini-3-1-pro-low 1, agy-gemini-3-6-flash-high 5, agy-gemini-3-6-flash-medium 4, agy-gemini-3-7-flash-high 23, agy-gemini-3-7-flash-medium 3, claude-fable-5-high 17, claude-harm-fable-5-high 27, claude-harm-opus-4-8-high 2, claude-harm-opus-5-high 57, claude-opus-5-high 9, codex-harm-sol-max 100, codex-sol-high 1, codex-sol-max 164 | 2026-07 168, 2026-08 277, 2026-09 5 |
| cleared, base later moved, never applied | 218 | 218 | agy-gemini-3-7-flash-high 191, agy-gemini-3-7-flash-medium 22, cc-glm-5-3-max 3, claude-harm-opus-5-high 2 | 2026-08 178, 2026-09 40 |
| cleared, no later event | 2225 | 2223 | (see summary.json) | 2026-07 119, 2026-08 1833, 2026-09 273 |
| refused, no later event | 13 | 13 | codex-sol-max 13 | 2026-07 13 |
| no verdict retained | 2880 | 447 | (see summary.json) | 2026-07 46, 2026-08 2834 |

All classes are change-set; the repo-doc class is 0 in every row.

**Why gold is empty.** The Principal's acceptance rulings in the ledger
(404: fail 139, pass 265) fall on
(unknown) 142, decision-record 26, design 62, implementation-plan 123, proposal 51 — never on a change set. The
Principal's 174 resolutions of escalations whose subjects are change sets are
all `proceed` on `bounds_exhausted`, and their notes concern attempt budgets
and infrastructure churn, not the correctness of a review verdict. The
Principal has re-ruled review verdicts this month in caplab's adjudication
ledger (26 controls, `advisory/control-adjudications.jsonl`), but those are
rulings on caplab's synthetic-contract controls, not on production
clearances, and the ledger predicate cannot see them. Striatum records no
event for "the Principal overruled this review".

**What silver is, exactly.** All 109 silver runs come from **three**
Principal cancellation records; no integration conflict other than "tree
moved" follows any clearance. The three cancellations, verbatim heads:

- **76691**: Retired: the product lineage striatum-next/passes/stalls-need-no-judgment-c/product-artifact is irrecoverably hollow. Product head c8a02131 is a 35-file self-contained tree with no internal/driver and its own go.mod, born from an empty-base subject-grain change-set (integrated_head integrated it before the packets, over the empty tree). A product-artifact wires no acceptance ga…
- **112825**: Delegated adjudication (Principal-approved 2026-07-29): the serialized multi-packet lowering cannot complete — intermediate packets fail the whole-tree Go checks lint-rfcs (571a7723) and gofmtcheck (6b9de8f0) because a Go-partial tree does not compile/lint standalone (the registered whole-tree-check-unit-atomic deferral, RFC 0010 s5.2). p01-report-envelope was revised 30 times,…
- **320479**: Read 2026-08-29 (delegated): review ledger 317468 RV-001 — the candidate change-set is an empty patch against anchored base 8dd2928b (32 files) while asserting a 1135-file result; the revising lane repeats it because the base it is composed against is wrong. RQ-320211 (same subject, target, and note verbatim) replaces this request and plans its base from the current Product hea…

Two of the three name a defect of the lineage or the lowering process
(a hollow product lineage; a serialized multi-packet lowering that cannot
complete), not of the reviewed change-set version; one (320479) names a
defect in the change sets themselves (an empty patch asserting a 1,135-file
result). By the regex predicate all 48 versions are silver; by reading, the
defect record names the reviewed artifact for 31 of 48 versions and the
lineage for 17. Silver here is a request-level label spread over many
versions, with the builder confound the instruction names.

## Go/no-go against the pre-registered floor (§2)

Floor: ≥ 20 positives with ≥ 5 gold, and ≥ 40 negatives, change-set class.

| | required | found |
|---|---|---|
| positives (gold-defect + silver-defect) | ≥ 20 | 109 runs / 109 versions, from 3 defect records |
| gold positives | ≥ 5 | **0** |
| negatives (gold-clear + bronze-clear) | ≥ 40 | 147 runs / 147 versions, 0 gold |

**Below the floor on gold.** Per §2 the study stops; no replay; the
disposition is `report-2026-09-07-review-instrument-disposition.md`.

## Contract and budget retention

- **Dispatch text.** No dispatch directory survives for any anchored review
  run (0 of 6042; the exchange retains 469, none of them reviews), and
  `prompt_asset_hashes` is empty on every manifest. The rendered prompt the
  reviewer saw is not retained.
- **Pass contract.** Every manifest names its review pass-contract object by
  hash and the object is in the store: 0b057789518b6c7efb16142ba998549234dfecd412f4f06483c16b057aa8c1da@v2 1, 446f4edd6906d9bb20db71a285fbc891b97ffef1b419987aaa7a1bfa58595a83@v2 36, 649545a930c199f16c441194f4851fed27f504c682740a17884eec54e3560f1d@v2 5664, fe13918359ca5f0a6b13681e0641885b2710082f560e3a52273334bfedf7e917@v2 341 (runs per contract hash,
  all `contract_version: 2`). The dominant one is saved beside this record
  (`review-pass-contract-649545a9.yaml`, 3,272 bytes): postures, verdict
  discipline (Principal ruling 2026-07-18), the environment it declares. A
  step-3 replay would therefore run under one fixed contract, claim scoped.
- **Budget.** No review run carries a time or token budget; the only
  deadline field is `deadline_class: batch`. Median wall-clock of completed
  reviews (`submitted`/`submitted_partial`) per binding, seconds:

| binding | median s | n |
|---|---|---|
| `agy-gemini-3-7-flash-high` | 785 | 1459 |
| `claude-harm-fable-5-high` | 104 | 1111 |
| `codex-harm-sol-max` | 288 | 846 |
| `agy-gemini-3-1-pro-high` | 353 | 338 |
| `claude-harm-opus-5-high` | 1103 | 276 |
| `codex-sol-max` | 871 | 243 |
| `agy-gemini-3-6-flash-medium` | 275 | 235 |
| `agy-gemini-3-6-flash-high` | 553 | 224 |
| `agy-gemini-3-7-flash-medium` | 860 | 146 |
| `claude-fable-5-high` | 140 | 101 |
| `claude-opus-5-high` | 1303 | 58 |
| `claude-harm-opus-4-8-high` | 239 | 43 |
| `cc-glm-5-3-max` | 1952 | 31 |
| `agy-gemini-3-1-pro-low` | 402 | 21 |

## Silver locators (109 runs)

Artifact identity (under `striatum-next/passes/`), version, review run,
binding, materialized base (prefix), the cancellation record, and the
verdict the review gave.

| artifact | version | run | binding | base | cancellation | verdict |
|---|---|---|---|---|---|---|
| `stalls-need-no-judgment-c/packets/frontier-evidence-foundation/change-set` | 76180 | 76185 | `claude-harm-opus-4-8-high` | `ab35c96b001c` | 76691 | accept_with_findings |
| `stalls-need-no-judgment-c/packets/durable-rq-57950-fixtures/change-set` | 76190 | 76195 | `claude-harm-opus-4-8-high` | `ab35c96b001c` | 76691 | accept_with_findings |
| `stalls-need-no-judgment-c/packets/frontier-evidence-foundation/change-set` | 76199 | 76204 | `agy-claude-opus-4-6-thinking` | `ab35c96b001c` | 76691 | accept |
| `stalls-need-no-judgment-c/packets/frontier-evidence-foundation/change-set` | 76208 | 76213 | `agy-claude-opus-4-6-thinking` | `ab35c96b001c` | 76691 | accept |
| `stalls-need-no-judgment-c/packets/durable-rq-57950-fixtures/change-set` | 76220 | 76225 | `codex-sol-max` | `ab35c96b001c` | 76691 | accept |
| `stalls-need-no-judgment-c/packets/frontier-evidence-foundation/change-set` | 76234 | 76239 | `claude-harm-opus-4-8-high` | `ab35c96b001c` | 76691 | accept_with_findings |
| `stalls-need-no-judgment-c/packets/frontier-evidence-foundation/change-set` | 76541 | 76546 | `claude-harm-opus-4-8-high` | `c8a021316541` | 76691 | accept_with_findings |
| `stalls-need-no-judgment-c/packets/durable-rq-57950-fixtures/change-set` | 76551 | 76556 | `claude-harm-opus-4-8-high` | `c8a021316541` | 76691 | accept |
| `stalls-need-no-judgment-c/packets/typed-frontier-recovery/change-set` | 76681 | 76686 | `claude-harm-opus-4-8-high` | `c8a021316541` | 76691 | accept_with_findings |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 108159 | 108164 | `codex-sol-max` | `dc9858bd67b5` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 108448 | 108485 | `codex-sol-max` | `dc9858bd67b5` | 112825 | accept_with_findings |
| `work-graph-assembly-c/packets/assembly-change-set-shape/change-set` | 108489 | 108496 | `agy-gemini-3-6-flash-medium` | `2f2769293450` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 109007 | 109043 | `codex-sol-max` | `dc9858bd67b5` | 112825 | accept_with_findings |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 109886 | 109893 | `codex-sol-max` | `d17dd5c61cfb` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 110097 | 110112 | `codex-sol-max` | `d17dd5c61cfb` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-change-set-shape/change-set` | 110116 | 110123 | `agy-gemini-3-6-flash-medium` | `819432b71ed4` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 110127 | 110132 | `agy-gemini-3-6-flash-medium` | `d17dd5c61cfb` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 110534 | 110663 | `codex-sol-max` | `d17dd5c61cfb` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 110856 | 110866 | `codex-sol-max` | `d17dd5c61cfb` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 110977 | 110986 | `agy-gemini-3-6-flash-medium` | `0830333cd4f8` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-change-set-shape/change-set` | 111087 | 111102 | `codex-sol-max` | `5c238b80622f` | 112825 | accept_with_findings |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 111603 | 111608 | `codex-sol-max` | `d32009d620dd` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 111634 | 111648 | `agy-gemini-3-6-flash-medium` | `d32009d620dd` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-change-set-shape/change-set` | 111790 | 111795 | `agy-gemini-3-6-flash-medium` | `e7b5191dd55a` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 111863 | 111875 | `codex-sol-max` | `d32009d620dd` | 112825 | accept_with_findings |
| `work-graph-assembly-c/packets/assembly-live-lowering/change-set` | 111890 | 111895 | `agy-gemini-3-6-flash-medium` | `2df215c6542b` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-change-set-shape/change-set` | 112100 | 112105 | `codex-sol-max` | `4fe957792a5a` | 112825 | accept_with_findings |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 112118 | 112124 | `agy-gemini-3-6-flash-medium` | `d32009d620dd` | 112825 | accept_with_findings |
| `work-graph-assembly-c/packets/assembly-change-set-shape/change-set` | 112203 | 112211 | `codex-sol-max` | `4fe957792a5a` | 112825 | accept_with_findings |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 112300 | 112307 | `agy-gemini-3-6-flash-medium` | `d32009d620dd` | 112825 | accept |
| `work-graph-assembly-c/packets/assembly-catalog-contract/change-set` | 112644 | 112649 | `agy-gemini-3-6-flash-medium` | `d32009d620dd` | 112825 | accept |
| `semantic-and-durable-closure-b/packets/p01-target-declaration-identity/change-set` | 173762 | 173828 | `claude-harm-opus-4-8-high` | `6a03e484b972` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p01-target-declaration-identity/change-set` | 174530 | 174775 | `claude-harm-opus-4-8-high` | `94f37f8ab81d` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p01-target-declaration-identity/change-set` | 282955 | 286974 | `agy-gemini-3-7-flash-high` | `6619ef7c9caf` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p01-target-declaration-identity/change-set` | 287507 | 287528 | `agy-gemini-3-7-flash-high` | `f7cf65f636a2` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p01-target-declaration-identity/change-set` | 287584 | 287625 | `agy-gemini-3-7-flash-high` | `f7cf65f636a2` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p01-target-declaration-identity/change-set` | 287701 | 287706 | `agy-gemini-3-7-flash-high` | `f7cf65f636a2` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p01-target-declaration-identity/change-set` | 287862 | 287881 | `agy-gemini-3-7-flash-high` | `f7cf65f636a2` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p02-satisfaction-and-provenance/change-set` | 288216 | 288270 | `agy-gemini-3-7-flash-high` | `61a6dddc3214` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p03-declaration-divergence-staleness/change-set` | 289306 | 289313 | `agy-gemini-3-7-flash-high` | `45498bae7a22` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p04-contextual-applicability-and-status/change-set` | 289796 | 289812 | `agy-gemini-3-7-flash-high` | `da084def9cca` | 320479 | accept_with_findings |
| `semantic-and-durable-closure-b/packets/p05-exact-consumer-binding-and-regressions/change-set` | 290180 | 290193 | `agy-gemini-3-7-flash-high` | `ba6b84196b57` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 290601 | 290621 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 290875 | 290997 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 291462 | 291475 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 291997 | 292047 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 292277 | 292302 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 292457 | 292535 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 292742 | 292748 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 293155 | 293163 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 293439 | 293523 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept_with_findings |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 293807 | 293890 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept_with_findings |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 294096 | 294103 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 294241 | 294249 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept_with_findings |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 294409 | 294422 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept_with_findings |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 294583 | 294603 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 294683 | 294692 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 294766 | 294776 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 294996 | 295056 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 295288 | 295323 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 295687 | 295704 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 295857 | 295868 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 296062 | 296069 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 296167 | 296178 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 296220 | 296226 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 296283 | 296291 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 296358 | 296363 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 296559 | 296579 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 297083 | 297138 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 297492 | 297506 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 297824 | 297913 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept_with_findings |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 298117 | 298163 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 298735 | 298812 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 299369 | 299388 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 299579 | 299629 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 300643 | 300700 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 301205 | 301228 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 301931 | 301961 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 302361 | 302464 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 303267 | 303296 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 303908 | 304012 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 304410 | 304437 | `agy-gemini-3-7-flash-medium` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 304795 | 304821 | `agy-gemini-3-7-flash-medium` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 305593 | 305667 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 305853 | 305883 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept_with_findings |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 306412 | 306435 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 306857 | 306910 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 307064 | 307122 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 307467 | 307481 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 307958 | 308058 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 308411 | 308429 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 308880 | 308889 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 309261 | 309266 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 309498 | 309509 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 309651 | 309673 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 309991 | 309997 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 310472 | 310478 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 310846 | 310896 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 311312 | 311332 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 311701 | 311733 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 312075 | 312161 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 312408 | 312414 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 312583 | 312589 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 312780 | 312785 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 312908 | 312916 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 313117 | 313124 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 313292 | 313310 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 313573 | 313584 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |
| `semantic-and-durable-closure-b/packets/p06-architecture-and-documentation-agreement/change-set` | 314019 | 314029 | `agy-gemini-3-7-flash-high` | `ce8917f06468` | 320479 | accept |

Bronze locators (147 runs, 137 versions) are in
`review-criterion-cases.jsonl` with the same fields plus the application record.
