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
Harbor, or Pincite. Every snapshot declares `mode` as `replay` or `live`, and
the caller must independently declare the same mode with `check --mode`.
A mismatch fails before results can be compared or scored. A live harness may
normalize its aggregate results to `books-evaluation-snapshot/1`, mark them
`live`, and supply them with `check --mode live --results PATH` against a
separately reviewed live baseline. Raw jobs, trajectories, and sensitive
records remain in scratch custody.

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

## Hermetic model-response replays

`replay-fixtures/` contains synthetic OpenAI-compatible request and response
pairs for the entailment and doctrine-injection consumers. Tests feed the
stored responses through each consumer's final-answer parser; they do not open
a socket or depend on a model server. Each fixture records canonical request
and response hashes, and `manifest.json` records the complete fixture file
inventory and file hashes.

Run the hygiene gate with:

```bash
make fixture-hygiene
```

The gate rejects unlisted files, symlinked inputs, hash drift, URL schemes,
host paths, environment interpolation, credential fields, and mutable refs
such as `latest`, `main`, or `HEAD`. `make evaluation-gate` depends on this
check, so the pull-request workflow enforces the same rule. Fixtures must stay
synthetic; live responses and raw evaluation artifacts remain outside the
repository. Replay fixtures carry `mode: replay`; loading them under a declared
live execution mode fails closed.

## Gate defect ledger

A failing regression check can append an idempotent observation to a durable
JSONL ledger:

```bash
python doctrine/tools/evaluation_regression_gate.py check \
  --root . --mode replay \
  --defect-ledger doctrine/evaluations/gate-defects.jsonl
```

The observation records hashes of the candidate, baseline, and gate config,
plus the normalized violations. Repeating the same failure does not duplicate
it. The gate does not create or change a ledger unless `--defect-ledger` is
explicitly supplied and the check fails.

Diagnosis and disposition are later append-only events. They reference the
original observation and its digest rather than rewriting it:

```bash
python doctrine/tools/evaluation_defect_ledger.py diagnose \
  --ledger doctrine/evaluations/gate-defects.jsonl \
  --defect-id gate-0123456789abcdef \
  --summary "The canary fixture no longer satisfies its contract." \
  --evidence tests/test_doctrine_scaffolding.py \
  --rival "The reviewed baseline may be stale." \
  --diagnosed-by agent-id

python doctrine/tools/evaluation_defect_ledger.py dispose \
  --ledger doctrine/evaluations/gate-defects.jsonl \
  --defect-id gate-0123456789abcdef \
  --status remediated \
  --rationale "The contract was repaired and the gate reran cleanly." \
  --decided-by owner-id \
  --authority "repository owner"
```

Diagnosis is recorded as an inference with evidence and rivals. Disposition is
recorded as a decision and requires an identified authority. Neither event is
technical verification or owner acceptance by itself. Validate a ledger with
`evaluation_defect_ledger.py validate --ledger PATH`.

## Error classification

`error-taxonomy.json` defines four closed outcome classes shared by scenario
replay, robustness replay, entailment screening, and aggregate evaluation
snapshots:

- `model-outcome` is a valid model or subject result and is score-eligible.
- `model-failure` is invalid model or subject output and is score-eligible as
  a failure.
- `infrastructure-failure` means the evaluation could not produce a judgment;
  it is never score-eligible or passing evidence.
- `not-evaluated` means a declared bound stopped the judgment before a model
  call; it is not score-eligible.

Scenario exit codes are 0, 1, and 2 for model outcome, model failure, and
infrastructure failure respectively. Unknown statuses fail closed as
`infrastructure-failure`. Aggregate gates still fail on every recorded error,
but infrastructure failures are excluded from model score denominators.
