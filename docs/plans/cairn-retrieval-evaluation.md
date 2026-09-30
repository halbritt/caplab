# Cairn retrieval evaluation harness

Owner direction, 2026-09-30: implement the evaluation harness in CAPLAB;
agent-251 coordinates agents 235, 248, 249 and 250 and continues through a
functional harness capable of measuring retrieval quality.

## Outcome and ownership

CAPLAB owns the experiment contract, execution entry point, retained evidence,
scoring and comparison report. Cairn remains the retrieval system under test.
Reuse Cairn's disposable-store infrastructure and native task evaluator where
appropriate; do not add a new PostgreSQL implementation or alter production
retrieval. The primary result is observed retrieval quality for frozen labelled
queries. Task completion is a separate downstream measure; ranking gains must
not be presented as proven agent usefulness.

The harness must run actual retrieval, not merely export existing reports.
A provider-free command fixture supports deterministic testing. A real Cairn
adapter and verified local run are required for completion. Preserve optional
semantic discovery state, especially labelled lexical fallback.

## Contracts for parallel implementation

Package: `src/caplab/retrieval/`. CLI: `python -m caplab retrieval ...` and
`python -m caplab.retrieval ...`. Avoid any new dependency in Cairn's service.
Use an explicit path and source identity when reusing a Cairn checkout.

`caplab-retrieval-spec/1` is a JSON object with these fields:

- `schema_version`, `experiment_id` (nonempty slug).
- `corpus`: list of notes with unique `id`, `body`, `kind` (default `note`),
  `shareable` (default true), optional `repo` and `supersede_with`.
- `queries`: unique `id`, `text`, `relevant_ids`, `forbidden_ids` (default empty),
  `stratum` (default `answerable`). Relevant and forbidden sets are disjoint;
  all IDs resolve to corpus notes. Empty relevant sets are explicit controls.
- `arms`: unique `id`, `adapter` (`command` or `cairn`), `configuration` object.
  Cairn configuration supplies `binary`, `checkout`, optional semantic worker
  and semantic mode; command configuration supplies an explicit argv array.
- `cutoffs`: distinct positive integers; `seeds`: distinct nonnegative integers;
  `timeout_seconds`: positive integer. Validate finite bounded input and reject
  duplicate identities, inconsistent labels and unknown schema versions.

Seal the normalized spec, input/source hashes and the full assignment roster
before launching retrieval. Each `(arm, query_id, seed)` is one assignment.
Keep rank and exposure distinct. An attempt contains `assignment_id`, `arm`,
`query_id`, `seed`, `status` (`ok`, `error`, `timeout`, `interrupted`,
`not_started`), `ranked_ids` (ordered unique corpus IDs), `delivered_ids`
(optional: actually delivered full-body/passage IDs, never inferred from rank),
`latency_ns` (nonnegative integer), `error` (nullable structured detail),
`observation` (adapter provenance, availability/fallback, context bytes, etc.).
Raw requests/responses/stdout/stderr are separate exact-byte artifacts. Gold
labels are available only to scoring, never passed to retrieval commands.

Command adapter request JSON on stdin:
`schema_version: caplab-retrieval-request/1`, `query_id`, `query`, `seed`,
`corpus` (notes without query labels), `cutoff` (maximum requested depth).
Response JSON: `schema_version: caplab-retrieval-response/1`, `ranked_ids`,
optional `delivered_ids`, optional `observation`. Nonzero exit, timeout,
malformed JSON/schema, duplicate/unknown IDs are classified failures. Never
substitute a fake response when the real adapter fails.

Metrics are computed at declared cutoffs: precision@k (k denominator), recall@k,
reciprocal rank@k and binary nDCG@k for answerable queries; empty-gold controls
have separate false-positive and forbidden-hit rates. Precision for a short
list follows the declared k denominator. Failed attempts are never successful
abstentions. Denominators report planned, attempted, scorable, failures and
missing; per-query outcomes stay available. Report successful-run conditional
metrics alongside coverage/all-assignment accounting, never silently drop
errors. Separate measured exposure recall when the adapter observed delivery.
All rates keep numerators and denominators; avoid float canonical-identity
loss. Comparison aligns identical case/seed identities and spec/label/corpus
pins; mismatches fail closed. Report paired deltas, discordant pairs and
case-level uncertainty where the data supports it. Seeds are not independent
new cases. No arbitrary pass threshold or qualification claim.

Public integration functions (agents may suggest necessary adjustments before
changing shared interfaces):

- `contracts.py`: `validate_spec(document) -> normalized dict`,
  `validate_attempt(attempt, spec) -> normalized dict`.
- `metrics.py`: `score_attempt(query, attempt, cutoffs) -> dict`,
  `summarize(spec, attempts) -> dict`.
- `runner.py`: `run_experiment(spec, output: Path) -> dict`; output must be new;
  preserve a durable plan and attempt evidence even on error/interruption.
- `cairn.py`: concrete isolated Cairn adapter used by runner; coordinate its
  internal API with runner owner (same agent).
- `artifacts.py`: `RunArtifacts(output: Path, spec)` with `record_attempt(...)`
  and `finish(...)`, raw-byte references and manifest verification. Agent 249
  publishes exact method signatures early to agent 248; runner should retain
  conventional `plan.json`, `attempts.jsonl`, `report.json` files as well.
- `compare.py`: `compare_runs(left: Path, right: Path) -> dict`, verifies
  retained evidence before comparisons. A same-run arm comparison may be added.
- `__main__.py`: `validate`, `run`, `report`, `compare`; explicit paths, clear
  failure exit codes. The outer dispatcher must include `retrieval`.

CAPLAB's existing FilesystemQualificationLedger is the artifact store. A
retrieval report is an observational experiment artifact, not automatically a
`caplab-measurement/1` qualification record. Do not fabricate Binding or basis
authorization just to satisfy a validator. A separately validated Measurement
export can be added when its actual basis and identity exist.

## Assigned implementation

- Agent 235: contracts, pure metrics, mathematical/adversarial tests; owns
  `contracts.py`, `metrics.py`, corresponding tests and a metrics contract doc.
- Agent 248: experiment runner and Cairn/command adapters, isolated real Cairn
  integration tests; owns `runner.py`, `cairn.py`, runner tests and local helper
  scripts it needs. Reuse existing disposable PostgreSQL facilities.
- Agent 249: immutable artifacts, integrity verification, paired comparison
  and report generation; owns `artifacts.py`, `compare.py`, `report.py` and
  matching tests. Publish exact artifact API promptly.
- Agent 250: CLI, deterministic fixture/example corpus with relevance and
  access/supersession controls, onboarding documentation and end-to-end CLI
  tests; owns `__init__.py`, `__main__.py`, outer dispatcher, examples, CLI tests.
- Agent 251: plan, integration, independent verification, resolving interface
  issues, cross-review assignments, full acceptance audit and landing.

Each agent uses an isolated sibling worktree and a separate branch, commits
its work, and returns exact commit/tests/limitations through its Cairn request.
Agents may read other worktrees; do not edit another agent's files. No agent
lands main or publishes remotely independently. Preserve unrelated owner files.

## Full completion gates

1. A documented CLI validates/freezes specs, executes all planned query/arm/seed
   assignments, and writes an inspectable report/evidence bundle.
2. A real Cairn run against a newly created disposable store measures labelled
   queries and captures binary/configuration identity, actual rank, availability
   and latency. No production database or credential use.
3. Known-good, deliberately bad and empty/failing retrievers are discriminated
   by the metrics. No-answer, wrong-project/local-only/superseded controls and
   incomplete runs cannot inflate successful quality claims.
4. Artifact tampering, duplicate/unknown IDs, query/corpus drift, timeout,
   malformed response, interrupted assignment and incompatible comparisons have
   meaningful tests and clear failures/remaining evidence.
5. Reports explain what was tested, labelled truth/provenance, denominators,
   error states, limitations and paired comparisons before metric summaries.
6. Native Cairn task-evaluation compatibility is demonstrated by a separate
   import/bridge slice that preserves original task grades/evidence and does
   not equate relevance with task completion. Its detailed interface follows
   the core runner; this remains in scope after the first slice.
7. Focused tests, repository-required local checks, independent cross-review
   and real integration evidence pass on the integrated revision. Baseline
   failures are separated from new failures; no GitHub CI is added.

Completion requires all gates; the first exporter or passing fixture is not
completion. No PageIndex adoption, retrieval gain, model qualification or
production deployment follows merely from harness verification.

## Evidence and reopening

Initial assessment: /home/halbritt/.local/share/cairn/reviews/caplab-20260930-agent251/assessment.txt.
Cairn plan: /home/halbritt/git/cairn/docs/plans/task-evaluation.md.
CAPLAB ADR0065 supplies methodological guidance, not study execution authority.
The retired reviewer admission gate supplies neither scoring nor thresholds.
Revisit an interface if a real Cairn run cannot express its observations
honestly; report the mismatch before papering over it with a synthetic result.

## Integration API clarification (coordinator, 2026-09-30)

To let CLI and runner implementation proceed independently, use these concrete
artifact/report interfaces. Any necessary change must be sent to all consumers:

```python
RunArtifacts(output: Path, spec: dict, *, provenance: dict | None = None)
RunArtifacts.register_bytes(name: str, payload: bytes,
                            *, media_type: str = "application/octet-stream") -> dict
RunArtifacts.record_attempt(attempt: dict,
                            *, raw: dict[str, bytes] | None = None) -> dict
RunArtifacts.finish() -> dict
verify_run(output: Path) -> dict  # spec, attempts, report, manifest
render_markdown(report: dict) -> str
compare_runs(left: Path, right: Path,
             *, left_arm: str | None = None, right_arm: str | None = None) -> dict
```

The report schema is `caplab-retrieval-report/1`, with its metrics under
`summary = metrics.summarize(spec, attempts)`. Other fields supply reviewer
context, references, provenance and limitations. `record_attempt` stores the
validated attempt plus separately registered raw artifacts; returned attempt
has the original attempt contract. Raw artifact references belong in the
manifest, not undeclared attempt fields. `finish` can report incomplete planned
coverage; it cannot turn missing assignments into successes. `verify_run`
checks source hashes and reconstructs metrics before returning retained output.

CLI contracts: `validate --spec PATH`; `run --spec PATH --output NEW_DIR`;
`report --run DIR [--format json|markdown]`; `compare --left DIR --right DIR
[--left-arm ID --right-arm ID]`. Run returns nonzero for failed or incomplete
execution while retaining its report. Quality scores have no invented pass
threshold. Omitting comparison arm selectors is valid only for unambiguous
single-arm inputs or a clearly documented matching-arm report.

## Native task-evidence bridge (second implementation slice)

After contracts/metrics are committed, agent 235 owns `native_task.py` and its
focused tests. Agent 250 adds the CLI entry point after its core CLI is ready.
The bridge is in scope; it must not be postponed past harness completion.

```python
import_task_run(report_path: Path, *, plan_path: Path, corpus_path: Path,
                cairn_checkout: Path, output: Path) -> dict
verify_task_run(output: Path) -> dict
```

Input is a completed or interrupted `cairn.task-eval.agent/1` report with its
original plan, corpus and available run streams. Preserve exact input bytes in
a fresh CAPLAB filesystem ledger. Reuse the explicitly selected checkout's
`trial_task_evidence.py` parser, pin its source, and inspect its expected input
contract; never call a model or production service while importing evidence.
Do not change the source grades, fill in missing streams, invent native Binding
identity or infer successful actions from tool-call names. Check report/plan
case, arm, seed, model, effort and frozen hashes; retain planned-but-not-started
rows and failure dispositions. Duplicate/unplanned rows or unsafe source paths
are errors. A missing stream remains unknown evidence, not zero delivery.

Output schema `caplab-retrieval-task-evidence/1` contains source references,
original grades/check outcomes, native delivery observations, assignment/status
counts and scope limits. Separate completion tasks from boundary/abstention
strata and expose unknown strata without silently treating them as completion.
Reported grades are retained source observations; this bridge does not certify
that an old instrument or oracle was valid. Missing configuration identity is
explicit and cannot be silently upgraded to a full CAPLAB Measurement.

Expose `caplab retrieval import-task --report PATH --plan PATH --corpus PATH
--cairn-checkout PATH --output NEW_DIR` and a verified report-reading path.
Local tests use newly constructed, clearly labelled fixture evidence with the
real Cairn parser, plus adversarial identity/hash/path/missing-stream cases.
Importing historical campaign evidence is not part of this implementation run.
