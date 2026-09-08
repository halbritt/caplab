# Review gate: preserve incomplete observations

Date: 2026-09-08. Assertion types: observation, execution, verification, and
bounded inference. This record makes no admission or placement decision.

The repository owner's active goal authorizes continued CAPLAB improvements
to measurement rigor and trustworthiness. This repair changes local code and
constructed tests. The confirmed
[review-instrument disposition](report-2026-09-07-review-instrument-disposition.md)
still governs live calls and ranking. No model call was made; no historical
row, adjudication, claim, or governing record was rewritten.

## Observed defects at 30382fe

`scripts/review_gate.py` classified every discarded row as not applicable,
including transport failure, missing bases, and unparseable output. Missing
planned cells had no counter. Its control counts used the pair's majority
verdict, so one refusal among three attempts disappeared. It called every
control without a defective adjudication sound, including unadjudicated
controls. Filtering for a parseable mutant also removed valid control
observations when the mutant arm failed.

Natural-case counters credited refusals and conformance without requiring a
successful process exit or verified base manifest. The conformance function
discarded non-object findings before checking them; malformed values could
either pass or raise an exception. The gate reused output directories and
ran natural cases after an aborted pool.

Before repair, constructed natural-case tests reproduced credited failed
executions and accepted or crashing malformed findings. The initial test
run recorded five failures and nineteen errors, including missing accounting
function errors. These are software reproductions, not observations of a
binding's review capability.

## Executed repair

Pool rows now retain every parsed attempt and its execution telemetry, with
the manifest verification specific to that attempt. Existing pair-summary
semantics remain unchanged. The gate reads the attempt evidence and emits
`caplab-review-admission-gate-result/2`:

- Every specified cell is scorable, not applicable, incomplete, or missing.
  Duplicate or unexpected cells and excess attempts are rejected.
- Control observations are counted per attempt and grouped by recorded
  disposition. Missing attempts stay visible; an unavailable mutant does not
  erase an observed control refusal.
- An observed verdict requires a valid value, successful execution, bwrap,
  and verified materialization. Analog rows must name tree-v1. Missing old
  telemetry supplies no observation.
- Natural-case responses are retained in full as parsed objects. Failed
  executions contribute neither a hit nor conformance credit. Malformed
  findings fail the structural check.
- Existing output directories are refused. Pool abortion suppresses the
  natural-case calls and reports those attempts as unavailable.

The [report guide](../product/advisory/review-gate-report.md) defines the
denominators and limitations. The gate specification and proposed floors
were preserved. No pass/fail policy was adopted.

## Verification

The focused command is:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest \
  tests.test_review_gate tests.test_advisory_pool_runner \
  tests.test_advisory_tree_v1 -q
```

It passed 82 tests. Coverage includes individual refusals hidden by a
majority, failed mutant attempts, missing rows, actual operator
inapplicability, unadjudicated controls, malformed verdicts and findings,
failed containment/integrity evidence, absent legacy telemetry, duplicate
cells, excess attempts, and the CLI's aborted-pool report and overwrite
refusal. Pool tests verify preservation of per-attempt execution and manifest
results. These are offline tests; they do not validate a live native harness.

The initial full `make check` ran 695 tests with four skips and two errors.
Both errors came from unchanged tests: `test_repository_contract` requires
the GitHub workflow deliberately removed by Principal decision in commit
`63e9beb`; `test_revbench_codex` expects acceptance of the installed Codex
executable even though it does not match the frozen bundle pin. The runtime
correctly rejects that executable. These baseline test-contract mismatches
require a separate repair; the full suite is not recorded as passing here.

## Remaining work and interpretation

The repair prevents specified accounting failures from making the report
look more complete or favorable. It does not establish benchmark validity.
The following work remains material to the owner's goal:

1. Verify the production outcome event surface and independently grounded
   incident population before interpreting reviewer accuracy. The last
   committed criterion pass found no gold incidents; this turn did not
   refresh that population.
2. Check the applicability of control adjudications to tree-v1 before using
   the sound-label group for a gate decision. Current labels include
   judgments made under iso-v1; the report explicitly preserves that limit.
3. Audit the pool's representative-verdict path on malformed model outputs.
   This repair adds attempt evidence and fixes gate accounting; it does not
   redefine the historical pair scorer's validity rules.
4. Validate semantic finding quality. The current discipline check is lexical
   and the natural-case anchor check matches text. Neither demonstrates that
   a reviewer has established the defect or supplied an actionable finding.

The tree-v1 sweep plan remains parked under the confirmed disposition. ADR
0028 preserves the wider roadmap; the older advisory plan's completed
matched-custody comparison is not evidence that this active goal is complete.
The untracked system-design document was left untouched. Goal status remains
active. The latest inspectable prior work, commit 30382fe, added the tested
production report and is classified as progress; no live job was resumed.

## Advisory engineering guidance

Pincite's release gate verified corpus `corpus-2026-07-12-a11702cc9217`,
doctrine `doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`,
at release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
Evidence packet `pkt-32cffe7e51d5bc39`, content SHA-256
`32cffe7e51d5bc39066e5eb28eee9d2e753ad158fb9eaec3d66aa8f8cc71485e`,
used the gate specification, source inspection, and failing tests.

The applied concepts were `implementation-risk-driven-tests`,
`operations-gate-authoritative-signal`, and
`universal-repository-contract-precedence`: test observable counters, read
per-attempt evidence, and keep technical observations below decision
authority. Leaving the counters unchanged or merely adding a caveat would
preserve demonstrated evidence loss. A new scoring policy was unnecessary.

The material obligations for this bounded repair are the specified
population, execution signals, preservation boundary, and regression
evidence, documented above. Live configuration parity, incident frequency,
and semantic reviewer accuracy remain unverified and bar broader claims.
Generic packet routes about top-N ranking, ingestion traversal, monitoring
pages, recurring ownership changes, and architecture alternatives are
nonmaterial to this local accounting change. Guidance supplied no CAPLAB
product authority or human acceptance.
