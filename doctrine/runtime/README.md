# Doctrine runtime contracts

These JSON Schema files define portable boundaries between the corpus, retrieval, operational skills, and evaluation tooling. They do not prescribe a database, embedding model, graph engine, or agent runtime.

| Contract | Purpose |
|---|---|
| `assertion-artifact.schema.json` | Typed observations, inferences, recommendations, decisions, authorization, execution, verification, and acceptance |
| `evidence-packet.schema.json` | Bounded doctrine and provenance selected for one question |
| `decision-receipt.schema.json` | Durable record of assertions, authority, alternatives, provenance, and reopening conditions |
| `dependency-manifest.schema.json` | Content identities and dependencies used to calculate rebuild and reverification impact |

The schemas use JSON Schema 2020-12. Their `$id` values are stable identifiers, not network dependencies.

## Assertion validation

Validate a JSON assertion artifact with:

```bash
python3 doctrine/tools/validate_assertions.py artifact.json
```

The standard-library validator enforces cross-record rules that JSON Schema alone cannot express conveniently, including resolvable assertion dependencies and required predecessor types for execution, verification, and acceptance. It is structural: it can reject missing provenance or authority fields, but it cannot prove that natural-language labels are honest.

## Dependency impact

Calculate the effect of a changed manifest node with:

```bash
python3 doctrine/tools/dependency_impact.py \
  doctrine/evaluations/fixtures/dependency-impact/manifest.json \
  --changed source-a
```

Relations named `evaluates` or `verifies` create a reverification requirement. Other downstream relations create a rebuild requirement. The output is deterministic JSON with changed, rebuild-required, reverification-required, and unaffected node IDs.

The dependency registry is only as complete as its declared edges. An unaffected result is not proof that an undeclared semantic dependency does not exist.
