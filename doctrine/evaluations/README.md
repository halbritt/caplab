# CAPLAB doctrine evaluations

This directory contains deterministic fixtures and calibration scaffolding for
testing evidence handling, retrieval contracts, and assertion boundaries.

Each scenario defines:

- the authority available to the actor;
- inspectable evidence with provenance;
- assertion types and evidence IDs that a result must include;
- assertion types and evidence IDs that a result must exclude.

`scenario.schema.json` defines scenario inputs; `result.schema.json` defines replay outputs.

The paired `authority-present` and `authority-withdrawn` canaries use the same evidence. The authorized result may record a decision and authorization; the withdrawn result must stop at a recommendation. Neither fixture claims execution, verification, or acceptance.

Run a fixture with:

```bash
python3 doctrine/tools/run_scenario.py \
  doctrine/evaluations/fixtures/authority-withdrawn/scenario.json \
  doctrine/evaluations/fixtures/authority-withdrawn/result.json
```

The runner checks the scenario's required and forbidden retrieval IDs and assertion types, then applies the structural assertion validator. It compares contracts rather than exact prose.

The `dependency-impact` fixture is synthetic. It proves that a changed source rebuilds its dependent chapter, concept, and prompt, re-verifies the associated evaluation, and leaves an unrelated source branch untouched.

These fixtures do not establish natural-language entailment or retrieval
quality. Exact locator resolution is supplied by the pinned Pincite release;
engineering-judgment quality still requires graph-backed,
human-adjudicated scenarios before the retriever can be accepted.

The [`entailment/`](entailment/README.md) subdirectory holds a separate,
model-judged screening harness (`doctrine/tools/entailment_eval.py`) for the
first of those gaps: whether each concept's cited source section supports its
claimed contribution. Its verdicts are observations of model output supporting
inferences about entailment — screening for human audit, not verification, not
acceptance — and they never modify doctrine.

The [`gold/`](gold/README.md) subdirectory contains a deterministic calibration
queue spanning the registered sources, graph relationship classes, agent-role
defaults, contextual risk classes, authority transitions, and explicit
insufficient-evidence, abstention, and no-change outcomes. It currently contains
candidate metadata only: every record is pending human adjudication and there
are no checked-in human dispositions. Machine screening cannot be promoted into
a human disposition or engineering acceptance.

## Robustness laboratory

The selected
[`Doctrine Robustness Laboratory`](../../docs/product/specs/spec-doctrine-robustness-laboratory.md)
defines clean/mutated evaluation pairs, controlled mutation operators,
relational oracles, content-addressed reports, and separate mechanical and
human-adjudication outcomes. P1 and P2 of its
[`pilot implementation plan`](../../docs/product/plans/plan-doctrine-robustness-laboratory-pilot.md)
are implemented: versioned contracts load offline, and the
`authority-withdrawal` case compiles one declared input delta before invoking
the existing scenario runner for the clean and mutant branches. Run it with:

```bash
python3 doctrine/tools/run_robustness_case.py \
  doctrine/evaluations/robustness/cases/authority-withdrawal.json
```

This is a deterministic structural checkpoint, not an accepted judgment-quality
gate. Later cases, grading, catalogs, and human adjudication remain deferred.

## Composition regression gate

`make evaluation-gate` builds a deterministic aggregate snapshot of the
committed canaries, robustness cases, skill A/B cases, and entailment gold
queue. It compares suite names, corpus identity, per-kind counts, exact case
IDs, errors, and named scores with
`baselines/repository.json`. Equal total counts therefore cannot conceal a
removed or substituted hard case. Any snapshot error fails closed.

The gate reads repository artifacts only; it does not call a model, network,
Harbor, or Pincite. A live harness may normalize its aggregate results to
`books-evaluation-snapshot/1` and supply them with `check --results PATH`.
Raw jobs, trajectories, and sensitive records remain in scratch custody.

To propose a baseline change, write a review candidate outside the repository:

```bash
python doctrine/tools/evaluation_regression_gate.py snapshot \
  --root . --out /tmp/books-evaluation-candidate.json
```

Review the candidate's suite composition, case IDs, corpus identity, errors,
and score movement. An owner then copies the reviewed candidate over the
baseline, records the reason in `baseline_review`, and commits both. The tool
intentionally has no automatic baseline-update command. A passing gate is
technical verification against the selected baseline; it is not owner
acceptance. The initial baseline remains explicitly provisional until that
review occurs.
