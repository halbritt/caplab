# Retrieval evaluation: artifacts, reports and comparisons

Owner: agent-249, 2026-09-30, for plan `docs/plans/cairn-retrieval-evaluation.md`.
Code: `src/caplab/retrieval/artifacts.py`, `report.py` and `compare.py`. They build
on `contracts.py` and `metrics.py` (agent-235, `docs/retrieval/metrics-contract.md`).
This is an interface and integrity contract for the runner, CLI and reviewers. It
makes no retrieval-quality claim, sets no threshold and grants no qualification.

A retrieval run is an observational experiment artifact. It is not a
`caplab-measurement/1` record: no Binding or basis authorization is created, and
no qualification claim follows. Custody reuses `FilesystemQualificationLedger`
only for exact-byte registration.

## Run directory

`RunArtifacts(output, spec, *, provenance=None)` creates `output` (it must not
exist; a directory, file or symlink there is refused and left untouched) and
writes the sealed plan before any retrieval runs:

| Path | Content |
|---|---|
| `plan.json` | `caplab-retrieval-plan/1`: normalized spec, pins, the full assignment roster, provenance |
| `attempts.jsonl` | one normalized attempt per line, exactly the attempt contract, fsynced as recorded |
| `evidence.jsonl` | hash-chained index: per attempt its raw artifact references, plus named artifacts |
| `report.json` | `caplab-retrieval-report/1`, written by `finish()` |
| `manifest.json` | `caplab-retrieval-manifest/1`: file hashes, chain head, ledger references; written last |
| `ledger/` | a `FilesystemQualificationLedger`: exact raw bytes, the plan and the report |

`manifest.json` is the commit point. After `finish()` the files are read-only.

Pins in the plan (`sha256:` digests of canonical JSON): `spec_sha256`,
`corpus_sha256`, `cases_sha256` (query ids, text and labels), `roster_sha256`,
one digest per arm, and the design (`cutoffs`, `seeds`, `timeout_seconds`).
Provenance is caller-supplied finite JSON (for example `file_identity(path)` for
a binary or a checkout file); it is sealed, not interpreted.

## Writing

- `register_bytes(name, payload, *, media_type=...)` registers a named artifact (a slug of
  at most 256 characters, such as `arm.<arm-id>.stdout`; raw roles are at most 128).
  Same name and bytes is idempotent; other bytes raise `ARTIFACT_NAME_CONFLICT`.
- `record_attempt(attempt, *, raw=None)` validates the attempt with
  `contracts.validate_attempt` (`ContractError` propagates and nothing is written),
  refuses a second attempt for an assignment (`DUPLICATE_ATTEMPT`), registers each
  raw role (`request`, `response`, `stdout`, `stderr`, `api_log`, any slug) as exact
  bytes, then appends the evidence entry and the attempt line, each fsynced. The
  evidence entry comes first, so a crash leaves orphan evidence (reported, and
  the assignment counts as missing), never an unexplained attempt.
- `pending_assignments()` lists roster rows without an attempt.
- `finish()` verifies everything it wrote, computes `metrics.summarize`, writes the
  report and the manifest, and returns `{status, complete, run, report,
  manifest_sha256, output, report_path}`. `status` is `complete` (every assignment
  ok), `completed_with_failures` (every assignment recorded, some not ok) or
  `incomplete` (some assignment never recorded). Only `complete` should exit zero.

Raw bytes are never re-encoded. JSON media is stored as opaque bytes because the
ledger canonicalizes JSON documents and refuses floats; the declared media type
is kept in the evidence index. Floats therefore survive in raw responses and in
`report.json`, and every comparison uses the integer numerator and denominator.

## Verification

`verify_run(output, *, allow_unfinished=False)` checks, in order: plan schema,
spec validity and normalization, pins and roster against the spec; the evidence
hash chain; every attempt line (valid, in normalized form, unique, bound to an
evidence entry by hash); every raw object through the ledger (hash and size); the
manifest against the current files; the registered plan and report bytes; and
the whole report, which must equal the report recomputed from the retained
attempts (float tolerance `1e-9` relative). Failures raise `ArtifactIntegrityError`
with `code`, `message` and `detail`:

`RUN_MISSING`, `FILE_MISSING`, `FILE_UNREADABLE`, `FILE_MALFORMED`, `PLAN_INVALID`,
`SPEC_INVALID`, `SPEC_NOT_NORMALIZED`, `PLAN_MISMATCH`, `EVIDENCE_CHAIN_BROKEN`,
`ATTEMPTS_TRUNCATED`, `ATTEMPT_INVALID`, `ATTEMPT_NOT_NORMALIZED`,
`ATTEMPT_DUPLICATE`, `ATTEMPT_WITHOUT_EVIDENCE`, `LEDGER_MISSING`,
`RAW_ARTIFACT_TAMPERED`, `MANIFEST_MISMATCH`, `REPORT_INVALID`, `REPORT_MISMATCH`,
`RUN_NOT_FINISHED`, `REPORT_WITHOUT_MANIFEST`.

A run without a manifest (interrupted) raises `RUN_NOT_FINISHED`. With
`allow_unfinished=True` it returns `finished: false` and a report computed in
memory (`run.finished` false) that lists every missing assignment. Unexpected
extra files are listed in `verification.unexpected_files` and do not fail.

These checks detect inconsistent edits, including a forger who also re-registers
the report and rewrites the manifest. They do not authenticate the author: someone
who rewrites every file consistently cannot be detected. Pin `manifest_sha256`
elsewhere to detect wholesale replacement.

## Report

`caplab-retrieval-report/1` keys, in order: `schema_version`, `reviewer_context`
(purpose, what was tested, labelled truth and pins, run status, how to read),
`run` (status, planned, recorded, ok, failed or not started, missing, by status,
failures, missing assignments), `denominators`, `limitations`, `provenance`,
`references` (file hashes and raw artifact list), then `summary` (exactly
`metrics.summarize`). `render_markdown(document)` renders a report or a
comparison with the same reviewer-context-first order and shows every rate as
numerator/denominator. Conditional metrics, coverage and all-assignment bounds
are never merged, and failures are never successful abstentions.

## Comparison

`compare_runs(left, right, *, left_arm=None, right_arm=None)` verifies both runs
first (both must be finished) and returns `caplab-retrieval-comparison/1`.
Deltas are right minus left.

Pins that must be equal, or `ArtifactError INCOMPATIBLE_RUNS` names the
mismatches and nothing is compared: spec schema, `corpus_sha256`, `cases_sha256`,
`seeds`, `cutoffs`, `timeout_seconds`. `experiment_id` and `spec_sha256` may differ.

Arm selection: both selectors, or neither. Neither is valid for two single-arm
runs (`single_arm_inputs`) or two runs with identical arm ids (`matching_arms`,
one comparison per arm). Otherwise `AMBIGUOUS_ARM`; `UNKNOWN_ARM` and `SAME_ARM`
(an arm against itself in one run) are refused. Passing the same run as left and
right with two arm ids compares arms inside the run.

Pairing is by identical `(query_id, seed)`. `pairing.counts` separates pairs
scorable in both arms from left only, right only and neither; every other pair is
listed with both states (`ok`, `missing` or a failure status) up to 200 rows.

Per cutoff, for answerable queries, over pairs scorable in both arms:
- metrics `recall`, `precision`, `reciprocal_rank`, `success` (exact rationals) and
  `ndcg` (float). Seeds are averaged inside each query first, so a case is a query.
  Each metric reports case count, left and right means, the delta, right wins,
  left wins, ties, an exact two-sided sign test over non-tied cases, and a 95% t
  interval over cases when there are at least three (above 30 degrees of freedom
  the critical value of the largest tabulated df at or below the actual one is used,
  which is slightly conservative). The sign test and interval are descriptive.
- `discordant_hits`: assignments where only one arm has a hit within k, listed,
  plus both-hit and both-miss counts (assignment level; seeds are not independent).
- `exposure_recall`: the same case-level statistics over pairs where both adapters
  observed delivery.
- `all_roster_sensitivity`: over every planned answerable assignment, each arm's
  mean recall is bounded by imputing 0 (lower) or 1 (upper) for its unscorable
  assignments. `delta_bounds` is `[right_lower - left_upper, right_upper - left_lower]`.
  `zero_imputed_scenario_delta` (`right_lower - left_lower`) is one scenario and is
  not a bound on the delta when the arms miss different assignments.

For control (empty-gold) queries and queries with forbidden labels, `controls`
counts pairs where neither, only the left, only the right or both arms returned a
false positive or a forbidden note.

## Limits

No significance rule or pass threshold is applied. Relevance, exposure and task
completion are separate; a better ranking does not show that an agent was helped.
A run has one writer in one process: there is no resume, and a second `RunArtifacts`
cannot reopen an existing directory. After an interruption, rerun into a new
directory; the interrupted one stays as evidence. Verification opens the ledger's
lock file, so the `ledger/` directory must remain writable for the verifying user.
`compare_runs` reads the retained `caplab-retrieval-summary/1` and refuses other
summary schemas (`SUMMARY_UNSUPPORTED`). The development dependency on
`contracts.py` and `metrics.py` is agent-235 commit `4b0ebfc`.
