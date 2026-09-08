# Anchor drift: retain both outcomes and comparison coverage

Date: 2026-09-08. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `6a95d0e`.

## Authority and preservation boundary

The active CAPLAB objective authorizes a bounded reporting repair in
`src/caplab/advisory/anchor.py`, new local tests in
`tests/test_advisory_anchor_drift.py`, the advisory README, and this record.
Before changing production code, reproduce the report errors with new synthetic
rows. Verify the public result, relevant existing tests, and `make check`.
Commit only these changes. This authorization expires at that commit.

No historical campaign or result reads, regeneration, rewriting, admission,
rescoring, model calls, reviewer rankings, placement changes, Plane updates,
service changes, or modifications to `docs/designs/` are authorized. Source
reads of existing report callers and tests are allowed. Preserve the current
reliability calculation, anchor selection, score metrics, qualification gates,
and numerical thresholds. Remove only this task's temporary doctrine working
files after recording receipts; retain test logs.

## Observation and selected repair

`drift` currently uses only catch agreement to select “anchor stable”. The
false-alarm agreement it computes cannot change that reading. Its dictionaries
silently overwrite duplicate dispatch IDs and exclude unusable anchors before
reporting the overlap, so missing or failed cases disappear from the comparison
boundary. Equality also treats unknown outcomes or numeric Boolean lookalikes
as agreement. The existing regression covers a changed catch result only.

The callers in `scripts/seed_20260819_report.py` and
`scripts/replay_20260820_report.py` embed this dictionary in their report; they
do not establish a cause for an observed change. The pool runner constructs
dispatch IDs from substrate ID, operator and seed. Matching that label alone
does not verify input bytes, condition parity, a native Binding, or the planned
population. Those checks remain separate from this descriptive function.

Select a versioned result that reports changes in either outcome and retains
recorded population coverage. Compare only shared usable rows with actual
Boolean catch and false-alarm outcomes. Retain unavailable rows and their
reasons in the coverage report. Reject missing or duplicate anchor identities
instead of selecting a row by input order. Report observed agreement on the
available comparison, never whole-instrument stability or a demonstrated cause.

Changing the catch-only conditional alone would leave attrition and ambiguous
identities hidden. Adding a statistical drift alarm or a full experiment
comparability gate here would require a different input contract and evidence;
neither is selected. No change would preserve a demonstrated misleading report.

## Verification

The nine new tests failed before production changes (7 failures, 14 errors):
`/tmp/caplab-anchor-drift-red.log`. After repair, all 84 tests in
`test_advisory_anchor_drift` and `test_advisory_pool_runner` passed in 5.255
seconds: `/tmp/caplab-anchor-drift-focused.log`. Existing catch-change behavior
and both agreement fractions on valid pairs remain covered.

Direct execution of the shared function on new synthetic rows produced:

| Input condition | Observed status | Comparable cases |
|---|---|---|
| Catch agrees, false alarm changes | `observed-change` | 1 |
| Surviving case agrees, previous case disappears | `agreement-on-subset` | 1 |
| Shared case is now unusable | `unavailable` | 0 |

Receipt: `/tmp/caplab-anchor-drift-probe.json`. The no-comparison result carries
null agreement, not a zero disagreement rate. Tests also verify unknown and
numeric outcomes remain unavailable, duplicate identities fail regardless of
input order or usability, missing identities fail, breadth rows are ignored,
and input objects are preserved.

The report schema is `caplab-anchor-drift/2`. `shared_anchor_cases` now counts
only pairs with usable rows and complete Boolean catch/false-alarm outcomes.
`coverage.shared_recorded_cases` separately counts ID overlap before that
filter. Status `observed-change` can coexist with incomplete coverage; it
reports the change actually seen without implying that unseen cases agree.
Status `observed-agreement` covers only the recorded anchor population, which
may itself omit planned cases. New output is not byte-compatible with the old
unversioned dictionary; source-inspected callers simply embed it as JSON.

`make check` passed: 868 tests in 113.136 seconds, four skips, exit 0;
`/tmp/caplab-anchor-drift-make-check.log`. No source or test changes followed
that run. `git diff --check` passed. All five used doctrine concepts were
classified as valid packet citations and consumption recorded locally.

No historical reports have been regenerated, and no live compatibility or
independent instrument acceptance is claimed. No roadmap state changed; the
broader measurement goal remains open.

## Advisory receipt

The retrieval gate passed at release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-6cdcbd2abd2278e0`, content SHA-256
`6cdcbd2abd2278e0770bc4b15d71bfa9aa3365be9dfd912a688690087c0bfeea`, uses corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts are
`implementation-placement-by-ownership`, `universal-evidence-before-intervention`,
`agent-conduct-authority-bounded-action`, `data-ingest-population-scoping`, and
`data-dedup-key-identity-completeness`. The existing report owns the join, both
outcomes and its stated population boundary; an ambiguous key is rejected.

Two evidence-gathering passes established the material source, authorization,
reproduction and report-population obligations. Remaining obligations are
nonmaterial to this repair for the reasons below. They do not become verified
by this classification.

| Concept | Missing requirements | Scope reason |
|---|---|---|
| implementation-config-reference-validation | a load-time or gate check resolving every reference against them; a named-identifier failure on mismatch; the consumer's defined identifier and enum sets | No named configuration references or enum registry change; anchor row identity validation is exercised directly. |
| implementation-placement-by-ownership | recurring change evidence when available | A reproduced shared reporting defect justifies the repair without recurring-change history. |
| implementation-rank-before-truncate | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No ranking, top-N selection or truncation occurs; all supplied anchor IDs remain represented. |
| operations-external-capability-verification | access to the real device or endpoint; an end-to-end verification artifact against the actual device or endpoint; or an explicit record that verification is provisional; the real system's own statement of its capability - device configuration output wire capture or endpoint self-description | No external capability or native harness is invoked or certified; all evidence is local function behavior. |
| operations-gate-authoritative-signal | eval-versus-serving configuration parity; inventory of gates and the signals they observe; proof the check reads that signal rather than a derived view; the authoritative signal named for each gate | This descriptive report explicitly does not verify native or experiment evidence and does not gate execution or qualification. |
| operations-symptom-cause-monitoring | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No service monitoring or alert policy changes; the report removes causal attribution. |
| task:defect-repair | evidence-incidents | No historical incident rate is claimed; the defect is demonstrated by new synthetic inputs and current source. |
| universal-no-change-option | actual current cost/risk or absence within a stated interval; expected future change from accepted plans; intervention cost and uncertainty; latent security, safety, data, durability, and compatibility check; proc-decide-leave-code-alone | The demonstrated misleading outcome motivates this bounded repair; no system-wide cost or latent-risk audit is claimed. |
| universal-repository-contract-precedence | accepted ADR, RFC, API, compatibility, generation, build, and test contracts | Relevant instructions, authority, source, tests and reporting contracts were inspected; unrelated API and generation contracts are outside this repair. |
