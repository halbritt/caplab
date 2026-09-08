# Stop a review case when its retained tree loses integrity

## Decision and authorization

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
authorizes a prospective repair to the advisory pool and natural-case gate.
Each tree-bound invocation must verify the digest captured at materialization
and the files it names before invoking the reviewer. A failed pre-check
prevents that invocation. A failed post-check retains the returned capture
as unusable. Either failure stops the remaining invocations for that case,
including the other arm. Assignments that did not run remain explicit and
must not become invented failed reviewer responses or shrink denominators.

The shared invocation boundary owns the check against the pinned manifest;
the two callers own their assignment counts and case-level stop. Ordinary
transport failures retain their existing treatment. Other cases, services,
worktrees, and timers are outside this stop scope.

Authorized effects: source and regression-test changes, newly authored local
fixtures, and this record. No model calls, historical recovery, evidence
admission or rewriting, rescoring, ranking, placement, sweeps, or tracker
changes. The 2026-09-07 instrument disposition stays in force. Stop if such
effects are required. Revert the commit to reverse the repair and remove
only task-owned temporary fixtures and advisory inputs. This is not a new
study authorization or independent acceptance of the instrument.

## Observation and rationale

At parent `7bd506c`, `pool_runner.measure_case` and
`review_gate.run_natural_case` call the reviewer after a false pre-check,
then keep running later replicates after a false post-check. Their final
records exclude affected responses but do not prevent additional exposure
or spend in the failed environment. `materialize.verify_manifest` validates
the on-disk manifest against itself without comparing it to the digest
captured by the caller. A replacement manifest can therefore validate a
different tree while the row still names the earlier digest.

The retained tree plan requires per-attempt manifest verification and a
digest on each row. A check against a moving reference does not establish
that identity. Continuing after a known failure cannot restore the original
measurement condition; rejecting only the final score is insufficient.
No change to prompt text, mechanical pair validity, operator eligibility,
reference truth, or numerical scoring is selected. Source hashing in pool
run specifications keeps prospective execution distinct from old sources.

## Verification

Before repair, six new tests produced six assertion failures and two
missing-field errors (`/tmp/caplab-tree-stop-red.log`). They observed actual
calls to a local fake reviewer after corrupting the newly materialized tree,
including a self-consistent replacement manifest.

The final focused run passed 50 tests in 0.242 seconds; see
`/tmp/caplab-tree-stop-focused.log`. Eight new regressions cover pre-call
refusal, post-call stopping and capture retention, cross-arm stopping,
replacement and non-object manifests, a file read error after invocation,
unchanged valid execution, and expected/unattempted counts through the gate
consumer. The pool-aborted natural-case path uses the same explicit counts.

Two old tests combined ordinary execution failure with post-check corruption
and expected later calls to continue. They now isolate execution failure in
an intact tree, preserving that existing policy. The new integrity tests
establish the separately authorized case stop. No numerical threshold or
reviewer judgment oracle was changed to make a test pass.

Final `make check` passed 833 tests with 4 skips in 109.181 seconds after
the report assertions were added; see `/tmp/caplab-tree-stop-make-check.log`.
The earlier full run also passed but is not the final-source verification.
`git diff --check` passed. Existing source-package hashes make future pool
run specifications differ from the pre-repair implementation.

## Result contract and limits

An `integrity_failure` identifies the phase, assigned replicate, and (for
pool cases) arm. Completed captures retain `manifest_before`,
`manifest_after`, and `manifest_verified`. Failed pre-checks create no
review response. A pool case still records its assigned `replicates` and
`mutant_replicates`, alongside each arm's `unattempted_replicates` count.
Natural cases record `expected_replicates` and `unattempted_replicates`;
`unavailable` is expected minus observed, including assignments stopped
before invocation. Earlier valid observations stay visible. A post-check
failure makes that response unavailable even when its parsed verdict clears.

The optional unpinned verifier remains available for inspecting a
materialization; execution uses the captured digest. This establishes
consistency with the materialization selected by the caller, not independent
admission of that initial tree, uninterrupted custody, or immunity to changes
that occur and are restored between checks. The existing mount supplies the
read-only boundary. This repair adds no crash-recovery protocol and makes no
claim that bounded capture prefixes are complete native transcripts.
No live model behavior, gold criterion, qualification, or independent
acceptance was established.


## Advisory doctrine receipt

The evidence-backed packet is `pkt-99f586ebb17384d3`, content SHA-256
`99f586ebb17384d3944baf463a1c76e530c8d519d8f583e7b7f77d639ebef281`. It uses release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Typed source, contract, and test
observations discharge the material obligations for this repair. The
execute ceiling is advisory; ADR 0026 and the scoped decision above provide
authority. Citation consumption is recorded in the local Pincite trace.

Applied concepts are `implementation-placement-by-ownership`,
`implementation-risk-driven-tests`, `agent-conduct-authority-bounded-action`,
and `universal-repository-contract-precedence`. One invocation helper owns
pinned-tree verification; callers retain responsibility for their assignments
and reports. A generic workflow engine or a change to unrelated failure
policies would exceed the demonstrated defect.

The remaining obligations are nonmaterial to this bounded repair:

| Concept | Missing requirements | Reason |
| --- | --- | --- |
| `data-dedup-key-identity-completeness` | an explicit enumeration of the record's identity dimensions matched against the key's columns; logical-identity definition of the affected record; the conflict-handling semantics at that key - abort update or silent drop | No database key or deduplication policy changes. |
| `data-ingest-population-scoping` | a dry-run enumeration with counts compared against expectation; the discovery pattern shown to match the specification's depth and class constraints; the input population specification; the specified input population stated precisely | No traversal-based import, population change, or backfill is performed. |
| `implementation-config-reference-validation` | a load-time or gate check resolving every reference against them; a named-identifier failure on mismatch; the consumer's defined identifier and enum sets | No declarative registry or symbolic enum configuration changes; the captured digest is compared directly. |
| `implementation-placement-by-ownership` | recurring change evidence when available | Both current callers establish the common invocation invariant without requiring longitudinal co-change evidence. |
| `implementation-rank-before-truncate` | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No search ranking, truncation, or top-N selection is involved. |
| `operations-gate-authoritative-signal` | eval-versus-serving configuration parity; inventory of gates and the signals they observe; proof the check reads that signal rather than a derived view; the authoritative signal named for each gate | No general operational gate inventory or live-serving parity is claimed. The two local manifest-check paths were directly inspected and exercised. |
| `operations-symptom-cause-monitoring` | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No paging policy, service monitor, or operational-health claim changes. |
| `task:defect-repair` | evidence-incidents; evidence-runtime-observation | Local counterexamples establish the defect. No production incident or live reviewer observation is claimed. |
