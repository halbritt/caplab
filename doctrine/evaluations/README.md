# Doctrine evaluations

This directory contains deterministic fixtures for testing evidence handling and assertion boundaries before a retriever or model is introduced.

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

These fixtures do not evaluate natural-language entailment, retrieval quality,
or source locator resolution. The extraction is stable; those properties still
require additional graph-backed, hand-audited scenarios before a retriever can
be accepted.
