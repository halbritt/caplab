# Keep ledger references distinct from Boolean and floating values

Date: 2026-09-08. Baseline: `21692ae`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Use newly constructed temporary ledgers and patched store-object reads to
reproduce numeric reference aliasing. Repair the shared criterion reader and
canary baseline reader so ledger sequence values and the numeric reference
paths consumed by the report cannot treat Boolean, floating, negative, or
other non-integer values as integer identities. Preserve zero as an integer
sequence and absent/null optional references as absent. Validate these paths
before body-store access. Do not silently coerce or discard invalid references.

Permitted edits: `scripts/review_criterion_ledger_pass.py`,
`scripts/review_canary.py`, `tests/test_review_canary.py`,
`docs/product/advisory/production-review-report.md`, and this record. Expose
the new reference policy in report metadata and version new output. Preserve
valid-input report semantics, baseline continuity, original source bytes,
and all historical reports. Verify focused regression tests, a synthetic
before/after comparison, and `make check` before commit.

Read-only producer source inspection in Striatum is supporting evidence; it
does not confer ownership or authorize changes there. No live ledger export,
store inspection, historical body processing, model spend, scoring, admission,
ranking, placement, tracker edit, or external message is authorized. Preserve
`docs/designs/`, sibling worktrees and unrelated state. Retain verification
receipts; remove only named task doctrine scratch after recording its receipt.
Authorization expires at commit.

## Observation and selected response

The reader indexes runs by integer ledger sequence and uses unvalidated
`run_ref`, `produced_by_run`, request, and version fields in joins and ordering.
Python equality and dictionary lookup can match `true` or `1.0` to integer 1.
The contiguous-sequence check also compares values without requiring integer
type. A matching hash and unique JSON keys do not establish reference type.

Select explicit nonnegative-integer validation at the consumed reference
paths. Missing optional paths remain missing, rather than becoming zero.
Keep this as a reader contract, not a claim of full producer-schema conformance,
referential existence, correct target kind, causal ordering, or truth of the
joined event. No change leaves false joins possible; coercion masks corrupted
identity; a wholesale producer-schema mirror would exceed this defect's scope.

## Execution and verification

Added a read-only validator over the consumed numeric reference paths,
including gate evidence's producing-run reference. It runs during export
parsing before any review-body lookup. Invalid values and containers raise
errors with the event/field locator; missing or null optional paths are not
coerced to zero. Every event sequence requires exact integer type and the
existing contiguous ordering. The baseline's final event cannot use Boolean
or floating equality to match integer snapshot metadata.

New reports use `caplab-review-canary/5` with
`reference_validation: nonnegative-integer-sequence-paths/1`. Versions 1–5
can supply a baseline subject to current decoding and prefix validation;
the complete new export uses the new reference checks. The JSON policy,
latest-body/gate precedence, downstream ordering, and report-only boundary
remain unchanged. No source evidence or historical report was rewritten.

`/tmp/caplab-review-ref-before.json` records both synthetic reproductions:
`produced_by_run: true` and `produced_by_run: 1.0` each attached a new acceptance
body to integer run 1. Store-object reads were patched to new synthetic bytes.
The initial test run exposed default-MagicMock decoding errors; the test
fixtures were corrected before implementation to supply valid synthetic body
bytes. The final pre-repair run then recorded 21 failures and two errors
(unhashable invalid references) in `/tmp/caplab-review-ref-red-final.log`.
Those failures are not a claim about any historical ledger.

Seven new tests cover the numeric paths and nested containers, Boolean and
floating sequence aliases, no body-store read before all reference checks,
CLI failure without output or source mutation, terminal baseline type checks
even with a matching hash, and zero/null/missing/large-integer distinctions.
Focused verification passed 35 tests in 0.624 seconds:
`/tmp/caplab-review-ref-focused-final.log`.

The retained synthetic four-run comparison is byte-identical before/after,
excluding only the temporary source path and declared report-version/policy
metadata: `/tmp/caplab-review-ref-valid-before.json` and
`/tmp/caplab-review-ref-valid-after.json`. It covers criterion summary, strata,
per-run observations, and canary output for valid closed/open, known/unknown,
body/gate disagreement, Unicode, and downstream-event cases. Reproduction
script: `/tmp/caplab-review-ref-valid-probe.py`. No live-data parity is claimed.
Both changed scripts pass AST parsing and direct-import-use inspection.

## Supporting producer source and limits

Read-only Striatum inspection found uint64 run references and version pins.
The two cited files were clean at observed source commit
`a6b1ae71d95cdf99200c10d8c6ce855d9da70a69`:

| Source path under Striatum | SHA-256 |
|---|---|
| `internal/scheduler/evaluation.go` | `6046dc3bd9567c71e48bdcda28a38585aee64b3f971a8f1e951f9cbf85cf755f` |
| `internal/derived/fold.go` | `982c29046c35124664327f1559bda598b0536bfd94fa1a07110c14082952a80e` |

These locators support the distinction between numeric identities and Boolean
or floating fields; they do not establish complete conformance with every
producer schema version. CAPLAB owns this reader policy. Integer width,
reference existence, target kind, temporal validity, content-hash format,
and event truth remain outside this repair's verification. No actual incident
rate, reviewer accuracy, qualification, or independent acceptance is claimed.

## Doctrine receipt

The release retrieval-state gate passed. Release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`.

Final packet `pkt-56dcf8fcf4e3b900`, SHA-256
`56dcf8fcf4e3b900193e4c0765727d6595e7f0f49d9a8c3e16bb0fc240f14c86`.
One evidence-gathering pass supplied five typed records: authority, repository
contracts, current source, synthetic reproduction/parity, and tests.

Applied `universal-repository-contract-precedence` to preserve report-only
and source-custody limits; `universal-evidence-before-intervention` to scope
the repair to observed aliasing; `python-mutable-ownership` to validate borrowed
input without filling or rewriting fields; and
`agent-conduct-authority-bounded-action` to keep producer-source reads separate
from any authority to alter Striatum or judge reviewers.

All remaining obligations are nonmaterial to this reference-type repair:

| Group | Exact unmet requirements | Classification and reason |
|---|---|---|
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI, formatter, or static-checker guarantee is claimed; the local Makefile and executable tests are the verification surface. |
| `performance-measurable-objective` | accepted workload and operation boundary; authority to inspect the target and identify the objective owner; environment, input distribution and scale, concurrency, and success/failure population; latency percentile, throughput, CPU, memory, I/O, network, cost, or other metric with a target; owner for the objective and any quality tradeoff | Nonmaterial: no performance, resource-use, or bottleneck improvement is selected or claimed; this is reference correctness. |
| `performance-memory-lifecycle` | allocation and in-use/retention evidence; owner/reference/lifetime path; precise memory metric and interval; representative macro memory behavior | Nonmaterial: no performance, resource-use, or bottleneck improvement is selected or claimed; this is reference correctness. |
| `performance-metric-semantics` | access to instrumentation definition or benchmark harness; instrumentation definition and configuration; instrumentation overhead and data-loss limits; sanity check against actual runtime behavior; unit, aggregation window, population, and sampling behavior | Nonmaterial: no performance, resource-use, or bottleneck improvement is selected or claimed; this is reference correctness. |
| `performance-profile-causal-bottleneck` | direct versus cumulative contribution and concurrency boundary analysis; profile type and sampling/granularity semantics; representative workload, version, and profile interval; reproducibility or independent corroboration | Nonmaterial: no performance, resource-use, or bottleneck improvement is selected or claimed; this is reference correctness. |
| `python-mutable-ownership` | concurrency; lifetime and size | Nonmaterial: no new concurrency, retained data structure, or lifetime policy; existing ownership and input bytes are preserved. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no CI, formatter, or static-checker guarantee is claimed; the local Makefile and executable tests are the verification surface. |

## Completion checks

`make check` passed 909 tests with four skips in 120.348 seconds; receipt:
`/tmp/caplab-review-ref-make-check.log`. No production or test source changed
after that check began. Four doctrine citations classified as
`valid-packet-citation`; their receipt is retained here before removal of the
eleven named task doctrine scratch files. Verification logs and synthetic
comparison artifacts remain. No tracker field or external message was changed.

Final link, diff, and parity checks are recorded in
`/tmp/caplab-review-ref-verification.json`. Commit closes this bounded repair,
not the broader measurement goal.
