# Keep invalid responses out of review measurements

Date: 2026-09-08. Observation, execution, and verification under the repository
owner's active CAPLAB improvement goal. The preceding goal turn made verified
progress in commits `6a2be3a` and `f3413dd`; both were present at the start of
this continuation. The untracked `docs/designs/` directory was preserved.

## Reproduction and cause

At `f3413dd`, `pool_runner.measure_case` treated every non-null verdict as a
vote and every parsed object as a usable representative. Constructed
responses with verdict `maybe` were treated as clearances; array or object
verdicts could raise exceptions. Valid-looking JSON from an unsuccessful
process could also supply a vote. A missing replicate could disappear from
the majority denominator.

The pre-repair regression run produced eleven failures and five errors across
five test methods. This establishes defects in the measurement software,
not the frequency of those defects in production or a model capability.

## Repair

`caplab.advisory.review_response` owns a shared structural and execution
validator used by the pool and the admission gate. It requires a supported
verdict and a findings array of objects; supplied anchor, text, and rationale
fields must be strings. A valid observation requires a successful process
exit, explicit non-timeout status, and no transport error. Tree-mode pool
attempts also require their manifest verification. The gate additionally
requires bwrap.

The pool retains each parsed response with its `review_error`, the declared
replication, and valid-attempt counts. Invalid attempts contribute `null` to
the verdict list. A partial set of replicates cannot supply a complete-pair
score. Complete valid pairs keep the existing majority and tie behavior.
Process-launch errors now produce unavailable-attempt telemetry instead of
escaping before the row can be written.

Prospective rows and summaries name `response_validation: review-response/1`.
The summary reports missing and incomplete pairs separately from actual
operator inapplicability. Consecutive incomplete review cases trip the
existing abort limit. `scoring.completed`, which the claim exporter uses,
refuses prospective runs with missing or incomplete pairs. Reporting a rate
over only the surviving pairs therefore cannot produce a new advisory claim.

Resumption rejects a different validation version, duplicate retained cases,
or cases outside the requested plan before invoking an adapter. A matching
complete local fixture can resume without repeating its attempts. No
historical rows or summaries were rewritten, and no historical claim was
rescored or superseded. The
[gate report guide](../product/advisory/review-gate-report.md) describes the
new validity and missingness rules.

## Verification and limits

The focused pool, tree-v1, gate, scoring, and executor suites passed 125 tests.
Tests cover malformed types, unknown verdicts, failed process exits, launch
errors, partial replication, abort and persisted rows from a real local
subprocess, incomplete-run eligibility, and resumption without duplicate
calls. Existing positive majority, tie, profile, and finding-selection tests
remain in place. Two older subprocess mocks were corrected to provide the
non-timeout field that the real invocation function already records.

Full `make check` passed: **704 tests, four existing skips, no failures or
errors**, in 143.203 seconds. The skipped P4 campaign and PostgreSQL
integration checks remain outside this verification. The local log is
`/tmp/caplab-response-make-check.log`. `git diff --check` passed.

No model calls were made. The repair validates response structure and
execution; it cannot establish finding correctness or real-world reviewer
value. Lexical discipline and anchor-text matching still require semantic
validation. The confirmed review disposition still retires ranking and keeps
live injection sweeps parked. The production gold-outcome population was not
refreshed in this continuation. The wider goal remains active.

## Engineering evidence

The validated Pincite release supplied packet `pkt-e38098dfa5cc7a2e`, content
SHA-256 `e38098dfa5cc7a2eed95bcb6e019b2a8c133fee12f14ffdbd58da41ad76d896c`,
doctrine `doctrine-f6bbb5196a3f8bf9`, retriever
`retriever-ec995ecdd083b2c8`. Source inspection and the regression executions
support `python-runtime-static-boundary`,
`operations-gate-authoritative-signal`, and
`universal-repository-contract-precedence`. The selected repair validates
untrusted values and preserves attempt evidence under the local authority
boundary. Leaving the code unchanged or merely documenting the error would
continue to invent votes; filtering individual failures without an explicit
completeness rule would conceal missing replication.

Material obligations for the software claim are the emitted response
contract, execution telemetry, declared population, and regression outcomes
above. Live harness parity and production incident frequency remain
unverified and exclude claims about deployment readiness or effect size.
Generic packet obligations about top-N ranking, ingest traversal, paging,
annotation maintenance cost, or architecture alternatives are nonmaterial
to this bounded runtime-validation repair. Doctrine supplied guidance, not
CAPLAB product authority or acceptance.
