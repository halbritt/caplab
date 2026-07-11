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

## Web adjudication UI

`doctrine/tools/adjudication_server.py` serves a single-page bench for the
workflow above at **http://100.85.100.81:8788/** on the tailnet (also
http://127.0.0.1:8788/ locally). Access is limited to loopback and the
Tailscale CGNAT range, judged by the socket peer address.

The UI presents two work surfaces: the entailment screening flags (see
[`../entailment/README.md`](../entailment/README.md)) and this gold queue,
with every candidate reference resolved to its source, formulation, node,
edge, lens, role, risk-class, transition, or outcome record and, for
source-support candidates, the matching machine-screening records.

What it writes:

- `POST /api/disposition` appends one disposition to
  `human-dispositions.json` (atomic write under a lock, whole-document schema
  validation before rename), then runs `build_gold_queue.py --write` followed
  by `--check` and reports both results.
- `POST /api/flag-audit` appends one human audit record to
  `../entailment/human-audit.jsonl`.

The verdict, rationale, uncertainty, and evidence list in a disposition are
the human's dictated judgment; the server records them verbatim and adds only
the adjudicator envelope (`kind: human`, the reviewer's id) and the
`adjudicated_at` timestamp. Machine verdicts shown in the UI are screening
observations and are never copied into a disposition by the server.

Service management (systemd user unit, linger enabled):

```bash
systemctl --user restart doctrine-adjudication   # restart
systemctl --user status doctrine-adjudication
journalctl --user -u doctrine-adjudication -f    # tail logs
```
