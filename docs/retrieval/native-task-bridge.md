# Native Cairn task-evidence bridge

Owner: agent-235, 2026-09-30. Code: `src/caplab/retrieval/native_task.py`. The
CLI entry point (`caplab retrieval import-task`) belongs to agent-250.

```python
import_task_run(report_path, *, plan_path, corpus_path, cairn_checkout, output) -> dict
verify_task_run(output) -> dict
```

Both raise `TaskEvidenceError(code, message)` with these codes:

| Code | Meaning |
|---|---|
| `OUTPUT_EXISTS` | The output directory already exists |
| `UNSAFE_PATH` | An input is not a regular file, or a run identity is not a safe path component |
| `MALFORMED` | Input is not valid JSON or has the wrong shape |
| `UNKNOWN_SCHEMA` | The report is not `cairn.task-eval.agent/1` |
| `IDENTITY_MISMATCH` | Report and plan disagree, or bytes do not match their hashes |
| `DUPLICATE_RUN` | A run appears twice in the report or plan |
| `UNPLANNED_RUN` | The report records a run the plan does not contain |
| `PARSER_CONTRACT` | The pinned parser lacks the expected functions |
| `PARSER_REFUSED` | The pinned Cairn parser rejected the evidence |
| `INTEGRITY` | Retained bytes failed verification |

## What import does

1. **Refuses to overwrite.** The output directory must not exist, and nothing
   is created until every check has passed.
2. **Checks identity** between the report (`cairn.task-eval.agent/1`) and its
   original plan:
   - the `frozen` object and the corpus bytes' hash must match;
   - `arms`, model, harness, reasoning effort, wording, harness version,
     evaluator hash and observed corpus must match;
   - each record's `run_id` must equal `case.arm.sSEED`, and each record's model
     and harness must match the report;
   - duplicate or unplanned runs, and invalid `not_started` rows, are errors;
   - run identities must be safe single path components.
3. **Runs the selected checkout's own parser**
   (`scripts/trial_task_evidence.py`). It is loaded from the explicit
   `cairn_checkout` and pinned by source SHA-256, git commit and whether the
   file is locally modified. A parser refusal is surfaced as `PARSER_REFUSED`,
   never replaced by a local guess. Examples: a delivery outside
   `trial:task-eval`, or a partial span that does not match the frozen source.
4. **Retains exact bytes** in a fresh `FilesystemQualificationLedger` under
   `output/ledger`:
   - report, plan, corpus, the observed corpus if present, the parser source,
     and every available `runs/<run_id>/stream.jsonl`.
   - JSON inputs are stored as octet streams, because the ledger's JSON path
     would re-encode them.
   - No custody claim is made: historical admission is a separate authorized
     path.
5. **Writes** `caplab-retrieval-task-evidence/1` to `output/evidence.json`
   (canonical JSON, also registered) and `output/manifest.json` (its ledger
   reference).

## Output

- **sources:** path, SHA-256, byte count and ledger reference for each
  retained input. The parser entry adds its pin.
- **identity:** the reported fields, arms and frozen identity.
  `binding: null` and `configuration_identity: "incomplete: …"`. No CAPLAB
  Binding, basis or Measurement is created or implied.
- **admission:** the original state, stop, planned and admitted counts.
- **counts:** planned, recorded, not_started, missing, streams_retained and
  streams_missing. A planned run that is neither recorded nor listed
  `not_started` is `missing`.
- **outcomes and strata:** original outcome counts overall and per reported
  stratum. A record without a stratum is `unknown`, never assumed to be
  completion.
- **assignments,** one per planned run in plan order:
  - `status`: recorded, not_started or missing;
  - `original`: outcome, stratum, correct, mistake, check_outcome,
    execution_failure, error, reviewed, category, primary, provenance, exit and
    seconds, exactly as reported;
  - `stratum_class`: completion, boundary_or_abstention or unknown;
  - `delivery`: either `{observed: false, reason: missing_stream}`, or the
    parser's preview and body notes, body bytes, unmapped deliveries and
    per-call status;
  - `stream`: the retained stream reference;
  - `original_memory`: the evaluator's hook observations, as reported.
- **limits:** scope statements carried with the evidence.

`verify_task_run` re-resolves every retained object through the ledger. It
checks hashes and sizes, confirms `evidence.json` is byte-identical to the
registered document, and returns counts.

## Limits

- **Grades.** Original grades are retained observations. The bridge does not
  regrade, validate the original oracle, or equate retrieval relevance with
  task completion.
- **Delivery.** Delivery evidence covers MCP tool responses in retained
  streams. Hook-delivered context exists only in the evaluator's own record.
  A missing stream is unknown, not zero delivery.
- **Scope.** Importing historical campaigns is out of scope for this slice.
  Tests use newly constructed synthetic fixtures labelled `SYNTHETIC` and run
  the real Cairn parser; they skip unless a Cairn checkout is present
  (`CAIRN_CHECKOUT`, default `~/git/cairn`).
