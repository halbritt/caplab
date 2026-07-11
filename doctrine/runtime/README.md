# Doctrine runtime contracts

These JSON Schema files define portable boundaries between the corpus, retrieval, operational skills, and evaluation tooling. They do not prescribe a database, embedding model, graph engine, or agent runtime.

| Contract | Purpose |
|---|---|
| `evidence-record.schema.json` | Typed repository evidence with inspectable provenance and explicit obligation mappings |
| `assertion-artifact.schema.json` | Version 2 typed observations, inferences, recommendations, decisions, authorization, execution, verification, and acceptance |
| `evidence-packet.schema.json` | Version 2 bounded doctrine and provenance selected for one question |
| `decision-receipt.schema.json` | Version 2 durable record of assertions, authority, alternatives, provenance, criteria, and reopening conditions |
| `dependency-manifest.schema.json` | Content identities and dependencies used to calculate rebuild and reverification impact |

The schemas use JSON Schema 2020-12. Their `$id` values are stable identifiers, not network dependencies.

## Assertion validation

Validate a JSON assertion artifact with:

```bash
python3 doctrine/tools/validate_assertions.py artifact.json
```

The validator enforces cross-record rules that JSON Schema alone cannot express
conveniently. In version 2 artifacts, every derived assertion must resolve its
typed evidence and reach an observation through a legal, acyclic predecessor
chain. Decisions require a recommendation; execution requires direct
authorization whose scope contains the execution scope; verification follows
execution; and acceptance follows verification. Version 2 receipts also require
the appropriate owner, authority source, criteria, and authorized scope for
their lifecycle state. Version 1 inputs remain accepted for compatibility but
do not receive the stricter typed-evidence and complete-lineage guarantees.

These checks are structural. They reject missing lineage, evidence, ownership,
or scope, but they cannot prove that a natural-language assertion or evidence
summary is honest. Withdrawal, expiry, scope or environment changes,
interrupted execution, failed verification, and rejected acceptance are
reopening events rather than permission to retain a stale status.

## Evidence-packet assembly

The packet assembler emits `evidence-packet/2` and defaults to the compact
agent-facing view:

```bash
python3 doctrine/tools/assemble_packet.py \
  --role coding-agent \
  --task implementation \
  --question "Where should retry policy live?" \
  --render markdown
```

Roles and tasks resolve through the controlled routing registry. Repository
signals may nominate doctrine but never discharge an evidence obligation; only
a valid `evidence-record/1` supplied with `--evidence` can do that. The compact
packet retains the safety kernel, prerequisites, operational layers, evidence
obligations, activation reasons, conflicts, and exact claim provenance. Use
`--detail full` when an audit needs the derived formulation, missing-evidence,
and source-locator views.

The default 5,000-unit budget applies only to activated-concept selection. Its
units are relative routing costs, not bytes, words, model tokens, or a claim of
empirical calibration. Corpus, doctrine, retriever, and packet content
identities are deterministic and content-addressed.

## Dependency impact

Calculate the effect of a changed manifest node with:

```bash
python3 doctrine/tools/dependency_impact.py \
  doctrine/evaluations/fixtures/dependency-impact/manifest.json \
  --changed source-a
```

Relations named `evaluates` or `verifies` create a reverification requirement. Other downstream relations create a rebuild requirement. The output is deterministic JSON with changed, rebuild-required, reverification-required, and unaffected node IDs.

The dependency registry is only as complete as its declared edges. An unaffected result is not proof that an undeclared semantic dependency does not exist.
