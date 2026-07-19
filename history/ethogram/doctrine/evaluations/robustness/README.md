# Doctrine Robustness Laboratory

This directory contains the implemented P1 contracts and P2
`authority-withdrawal` case for paired doctrine evaluation.

- `operator.schema.json`, `case.schema.json`, `result.schema.json`, and
  `human-adjudication.schema.json` define closed version 1 contracts.
- `operators.yaml` is the curated operator registry.
- `cases/authority-withdrawal.json` binds the clean scenario and its content
  identities to one allowed mutation selector.
- `doctrine/tools/build_robustness_suite.py` provides strict offline contract
  loading.
- `doctrine/tools/run_robustness_case.py` compiles the pair in memory and invokes
  the existing scenario runner in a temporary workspace.

Run the current case with:

```bash
python3 doctrine/tools/run_robustness_case.py \
  doctrine/evaluations/robustness/cases/authority-withdrawal.json
```

The clean branch must pass before the mutant is evaluated. The compiler rejects
stale seed or container hashes and selectors outside the operator allowlist.
Canonical scenarios, results, doctrine, and human-owned adjudications are
read-only inputs.

The current case establishes deterministic contract behavior only. It does not
constitute human acceptance of judgment quality.

## Doctrine skill A/B evaluation

Compile sealed control and treatment inputs without exposing the case oracle:

```bash
python3 doctrine/tools/evaluate_doctrine_skill.py compile \
  doctrine/evaluations/robustness/skill-cases/authority-withdrawal.json \
  --skill "$HOME/.codex/skills/doctrine/SKILL.md" \
  --out /tmp/doctrine-skill-eval
```

Run each input in a fresh agent context and require a `decision-receipt/2`
response. Save the receipts outside the repository, then grade the pair:

```bash
python3 doctrine/tools/evaluate_doctrine_skill.py grade \
  doctrine/evaluations/robustness/skill-cases/authority-withdrawal.json \
  --control /tmp/control-receipt.json \
  --treatment /tmp/treatment-receipt.json \
  --out /tmp/doctrine-skill-result.json
```

Mechanical grading checks receipt validity, expected and prohibited assertion
types, authority status, citations, and over-refusal. Usefulness and judgment
criteria remain `pending` until a human reviews them. The harness does not call
models, retain external outputs, or write human dispositions.

### Harbor execution

`render-harbor` renders the same case as matched control and treatment Harbor
tasks whose separate verifier environment grades only the transferred
`decision-receipt/2` artifact; `grade-arm` grades one receipt outside Harbor.
See [`harbor/README.md`](harbor/README.md) for the isolation contract, reward
projection, and matched-job commands. Rendering and grading stay hermetic;
running the tasks requires Harbor and is never part of `make check`.
