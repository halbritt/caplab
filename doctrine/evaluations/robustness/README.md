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
