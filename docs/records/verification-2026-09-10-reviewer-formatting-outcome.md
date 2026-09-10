# Formatting repair preserves the original compiled tests

Selected Striatum change `98759de9d5f1bfa855cc8d7ff43456be243db7db`
changes only whitespace in `internal/scheduler/glm_activation_test.go`.
The complete Git diff, identical formatter output, identical compiled test
binaries and repeated original test results support preservation for this
edit. It adds a bounded clean-control candidate in the previously uncovered
Striatum 0–20-line stratum.

## Evidence

The original parent is `03f0cc39b02c7882674ca2706398560e986b1032`.
The original Makefile requires formatting checks. Only the named test file
differs across the complete commit; its original bytes are retained.

| Check | Observation |
| --- | --- |
| Go 1.23.4 formatter | Base and change normalize to identical bytes. |
| Conformance | The changed file already equals that output; the base does not. |
| Original scheduler test-package builds | Both compile with locked dependencies and produce the same binary hash. |
| `TestRepositoryGLMReviewDeactivationContract` | Runs and passes on both trees in both repetitions. |
| `TestClaudeHarmFamilyTracksExactAvailabilityPosture` | Runs and passes on both trees in both repetitions. |

The compiled test binary SHA-256 is
`eee51da8399331af1602726a17d8f5ef4e69e8402077264f9c288d5b29943dc8`.
Canonical source SHA-256 is
`6eb9a1afe9ce944e3f50cc654f04e60c63b1410c601644d2d6f4945a77a64541`.
Both original package builds, two formatter executions and four test
executions completed within 7.73 seconds. The original package is compiled;
only the two affected tests execute. No tests or source functions are added
or replaced inside the historical trees.

These tests read historical backend declarations and scheduler policy. Their
passing assertions are not independent evidence of model capability or
current availability. The inference concerns the edit: with the pinned
compiler and inputs, formatting changed while the compiled test program and
observed outcomes remained unchanged. Passing tests alone would be weaker
evidence; here the formatter and binary identities corroborate preservation.

## Custody and verification

The [authorization](authorization-2026-09-10-reviewer-formatting-witness.md)
names the exact source and historical policy imports. Private custody is
`~/.local/share/caplab/reviewer-ranking-001/development/formatting-witness-1`.
It preserves 534 original files per revision with commit, tree, Git blob,
path, mode and content hashes. Toolchain and locked cached dependencies are
pinned; source is read-only and execution has no external network. No real
backend, provider, service, graph or original checkout is executed or changed.

The [receipt](../product/studies/reviewer-ranking-001/formatting-development-receipt.json)
identifies 44 process, binary and assessment files plus the original source
snapshots. Frozen plan SHA-256 is
`ea3151ddf4a90961af9bc7e1a52b66a4b861e944d909f67055c0c1ad453438a1`;
verification SHA-256 is
`87136366db3d7ef732bf7693524285d4fd2f75d00fa33cb7dc4c476e3c816348`;
assessment SHA-256 is
`3a673a1ddf6e025ca198d3b52b674a80d6de89bcc6829b2f5552371786f274a6`.

Three focused verifier tests pass. They distinguish a formatted semantic
change from equivalent formatting, distinguish canonical equivalence from
conformance, and reject a pass banner with missing, skipped, duplicate or
wrong test names. The full repository check passed: 1,557 tests in 207.067
seconds, seven skipped. Its output is retained as `repository-check.log` in
the custody root, separately from the execution receipt. Verification
reproduces, and all 44 receipt files and 1,068 original source files match
their hashes.

## Ranking scope

This supports a clean-control candidate for runtime-regression allegations
about the whitespace edit under the tested configuration. It does not
independently validate every assumption in the historical tests, execute the
full original suite or admit a case. No reviewer result is scored here.

Fixed-sample coverage is now nine bounded change investigations, three
base-tree-only investigations and twenty pending, with zero admitted cases.
The sample is unchanged. Four test executions are one investigated change,
not four independent cases. Broader coverage, prospective scorer validation
and held-out comparisons remain required; the reviewer-ranking goal is active.
