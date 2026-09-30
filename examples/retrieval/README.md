# Frozen retrieval development fixture

This seven-note, seven-query corpus checks the retrieval instrument. It is
synthetic development data, not a held-out study or a production distribution.
Labels are frozen in [spec.json](spec.json); changes require a new fixture
version. The runner seals normalized labels and the assignment roster before
executing any command. Retrieval receives corpus text and a query, never the
relevance or forbidden labels.

| Query | Relevant truth | Purpose |
|---|---|---|
| answerable-recall | recall-budget | Direct answerable query |
| paraphrase-startup | startup-pull | Paraphrase with small explicit synonym map |
| answerable-version | version-check | Second direct answerable query |
| no-answer | empty | No matching information exists |
| wrong-project-control | empty; wrong-project forbidden | Foreign project must not supply an answer |
| local-only-control | empty; local-only forbidden | Hosted-ineligible note must stay excluded |
| superseded-control | empty; superseded forbidden | Obsolete procedure must not be retrieved |

Notes without `repo` belong to the experiment collection; the foreign sentinel
names `surveyor` explicitly. These are ranking controls. They do not demonstrate refusal by a real agent or
prove enforcement by Cairn. The local-only PIN is entirely fabricated.

[fixture.py](fixture.py) supplies four deterministic subprocess behaviors:

- `good`: rank eligible notes by token overlap, then note ID; filter project,
  shareability and supersession; do not use query IDs or relevance labels.
- `bad`: reverse corpus order, ignoring relevance and access controls.
- `empty`: return no ranked notes for every query.
- `failing`: exit 17; every assignment must be classified as a command failure.

A fifth `malformed` mode returns invalid JSON for error-boundary tests. These
commands run locally without a provider, selector service, database or model
spend. They return ranked IDs only. No body delivery is observed and no
`delivered_ids` field is synthesized from the rankings. The synonym map is a
toy fixture mechanism, not a claimed retrieval policy improvement.

[prepare.py](prepare.py) copies the frozen labels into a new spec and resolves
its Python interpreter and fixture paths absolutely. Each command executes in
an empty working directory, so relative script paths from the illustrative
label file must be prepared first. Preparation performs no retrieval, preserves
the corpus/query labels, and refuses an existing output file. Run the following
from the CAPLAB checkout root:

```sh
python3 examples/retrieval/prepare.py --output /tmp/retrieval-fixture-spec.json
PYTHONPATH=src python3 -m caplab retrieval validate --spec /tmp/retrieval-fixture-spec.json
PYTHONPATH=src python3 -m caplab retrieval run --spec /tmp/retrieval-fixture-spec.json --output /tmp/retrieval-fixture-run
PYTHONPATH=src python3 -m caplab retrieval report --run /tmp/retrieval-fixture-run --format markdown
PYTHONPATH=src python3 -m caplab retrieval compare --left /tmp/retrieval-fixture-run --right /tmp/retrieval-fixture-run --left-arm good --right-arm bad
```

Choose a new output path for each run. The `run` and `report` commands above
return **1**, deliberately: the failing arm ran. They still emit the complete
report with its failures and denominators. Successful empty responses remain
scorable empty responses; command failures are not abstentions. A low score in
a completed `bad` arm does not by itself make the command fail.

Read the reviewer context, labels and coverage before the metrics. Three
answerable and four control queries per arm mean 28 planned assignments with
one seed. The failing arm has zero scorable assignments and seven failures;
the empty arm has seven scorable assignments but zero answerable recall. Gold
label errors remain possible even when the pipeline passes. Seed repetitions
are not independent new cases. Conditional scores and all-assignment bounds
must remain separate.

See [CLI onboarding](../../docs/retrieval/cli.md) for retained artifacts,
errors and the isolated Cairn adapter. The CLI also offers the separate native task-evidence import/report path;
neither this example nor a ranking report establishes verified task completion.
