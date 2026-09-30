# Native Cairn task-evidence bridge

Owner: agent-235, 2026-09-30. Code: `src/caplab/retrieval/native_task.py`. The
CLI entry point (`caplab retrieval import-task`) belongs to agent-250.

```python
import_task_run(report_path, *, plan_path, corpus_path, cairn_checkout, output) -> dict
verify_task_run(output, *, trusted_parser_checkout=None) -> dict
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

## Trust boundary

The selected checkout's `scripts/trial_task_evidence.py` is Python code. It runs
in this process at import. Select only a checkout you trust.
- The importer executes exactly the bytes it hashes and retains; it does not
  read the file a second time. A dirty check covers the parser file only, not
  modules it imports.
- `verify_task_run` never executes retained code. It re-runs the parser only
  from `trusted_parser_checkout`, when the caller passes one explicitly. Those
  bytes are compared with the retained parser **before** anything executes:
  a mismatched parser is refused (`PARSER_CONTRACT`) without running.
- Before any stream is collected or written to a scratch directory, every
  evidence assignment must equal the re-derived roster entry at its position:
  run ID, case, arm, seed and order, in plan order with none missing,
  reordered or duplicated. Each scratch write is also checked to stay inside
  the scratch root. A forged run ID, whether absolute or `../`, is refused
  before any path is used.

## What import does

1. **Refuses to overwrite, and fails before writing.** The output must not exist.
   A dangling symlink or a creation race also gives `OUTPUT_EXISTS`. Nothing is
   created until every content check has passed:
   - strict JSON (NaN, Infinity and pathological nesting are `MALFORMED`);
   - identity and position checks;
   - observed-corpus path containment and hash;
   - the parser run, and the parser's report, corpus, observed-corpus and
     analyzer hashes checked against the bytes being retained;
   - stream hashes.
   After that only I/O remains. An I/O failure part-way can leave a partial
   output, which verify refuses.
2. **Checks identity** between the report (`cairn.task-eval.agent/1`) and its
   original plan:
   - the `frozen` object and the corpus bytes' hash must match;
   - `arms`, model, harness, reasoning effort, wording, harness version,
     evaluator hash and observed corpus must match;
   - each record's `run_id` must equal `case.arm.sSEED`, and each record's model
     and harness must match the report;
   - each plan position must be an integer arm slot (0 ≤ position < number of
     arms), distinct within one case and seed, as `trial_task_eval.py` assigns
     it. A record's `order`, and a `not_started` row's `order` and `run_id`, are
     optional (older reports omit them), but when present they must agree with
     the plan;
   - duplicate or unplanned runs, and invalid `not_started` rows, are errors;
   - run identities must be safe single path components, and no two
     identities may derive the same `case.arm.sSEED` run ID. Otherwise two
     assignments would share one stream (`DUPLICATE_RUN`).
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
   and `output/manifest.json`.
   - `evidence.json` is sorted, compact, finite JSON bytes, registered with
     `register_bytes` as `application/vnd.caplab.retrieval-task-evidence+json`.
   - Native reports carry floats (run seconds, memory timings and costs).
     CAPLAB canonical JSON refuses floats for identities, so they are kept
     untouched in these exact bytes rather than rounded or dropped.
   - `manifest.json` holds only the float-free ledger reference, in canonical
     JSON.

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
  - `stratum_class`: `completion` only for stratum `completion`, and
    `boundary_or_abstention` only for the known strata `scope`, `control` and
    `blocker`. Everything else is `unknown`: other labelled strata such as
    `decision`, `component` and `excluded`, plus any absent or empty stratum.
    The raw stratum is always kept in `original`;
  - `delivery`: either `{observed: false, reason: missing_stream}`, or the
    parser's preview and body notes, body bytes, unmapped deliveries and
    per-call status;
  - `stream`: the retained stream reference;
  - `original_memory`: the evaluator's hook observations, as reported.
- **limits:** scope statements carried with the evidence.

`verify_task_run` works in three stages.
1. **Bytes.** Every retained object is resolved through the ledger and checked
   by hash and size, and `evidence.json` must equal the registered document.
2. **Re-derivation.** Everything that is not parser output is re-derived from
   the retained report, plan and corpus bytes and must reproduce
   `evidence.json` byte for byte. That covers identity checks, assignment
   order and status, original grades and memory, stratum classes, counts,
   outcomes, strata, admission, reported identity, `binding: null` and limits.
   A coherently forged evidence document that is re-registered with a
   rewritten manifest is therefore refused.
3. **Parser output.** Parser-derived delivery observations are hash-bound:
   `parser_analysis` must name the retained report, corpus, observed corpus and
   parser bytes. Every observed delivery must correspond to a retained stream,
   and vice versa. They are re-executed only with `trusted_parser_checkout`.
   Otherwise a forged delivery list over genuine streams is not detected, and
   the result says so honestly.

It returns `{schema_version, verified, objects, counts, evidence,
verification}`. `verification.parser_derived` is either
`"hash-bound; not re-executed"` or
`"re-executed with trusted checkout; matched"`. Verification establishes
consistency with immutable retained sources, not cryptographic authorship. `evidence` is the verified registered document itself, so a caller
such as the CLI report can render retained task evidence with no second,
unverified read.

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
