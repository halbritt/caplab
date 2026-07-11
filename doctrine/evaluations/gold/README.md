# Human gold-calibration queue

This directory is a scaffold for human-adjudicated doctrine evaluations. It is not yet a gold set: every checked-in candidate is `pending-human`, and [`human-dispositions.json`](human-dispositions.json) contains no judgments.

## Artifact boundaries

- [`queue.json`](queue.json) is generated candidate metadata. Its questions and strata nominate work for review; they are not observations, verdicts, verification, or acceptance.
- [`coverage.json`](coverage.json) reports whether the queue includes every registered source, graph edge relation, source-support relationship, agent-role default, contextual-lens risk class, authority transition, and required non-action outcome.
- [`human-dispositions.json`](human-dispositions.json) is the human-owned judgment surface. The generator creates an empty file when absent but never invents or overwrites dispositions.
- [`queue.schema.json`](queue.schema.json) validates generated queue records.
- [`human-dispositions.schema.json`](human-dispositions.schema.json) requires a human adjudicator, reviewed evidence, rationale, uncertainty, and an evaluation verdict.

Machine screening may support a later human review, but it cannot populate a human disposition. A gold-evaluation verdict also does not authorize an engineering change or accept a repository artifact.

Source-support, graph-edge, and support-relationship candidates are marked for direct evidence review. Role, risk, authority-transition, and outcome candidates are marked `scenario-construction-and-review`: a human must construct a concrete evidence-bearing scenario before adjudicating them. Axis coverage alone is not evaluation quality.

## Build and check

Regenerate candidate metadata after a source, graph, role, risk, or authority contract changes:

```bash
python3 doctrine/tools/build_gold_queue.py --write
```

Check schemas, human-disposition constraints, coverage, input fingerprints, and deterministic drift:

```bash
python3 doctrine/tools/build_gold_queue.py --check
```

`--write` may change `queue.json` and `coverage.json`. It preserves an existing `human-dispositions.json` byte-for-byte and projects only disposition references and status into the generated queue.

## Human adjudication workflow

1. Select a pending candidate and inspect every referenced source, formulation, node, edge, role, risk class, transition, or outcome.
2. Record one disposition in `human-dispositions.json` with an adjudicator whose `kind` is `human`, the evidence actually reviewed, a verdict, rationale, and residual uncertainty.
3. Run `--write` to project the disposition reference into the queue.
4. Run `--check` and obtain an independent review of the adjudication where the evaluation risk requires it.

Do not copy a model verdict into `human-dispositions.json` under a human identity. If a person has not inspected the evidence and made the judgment, the candidate remains `pending-human`.
