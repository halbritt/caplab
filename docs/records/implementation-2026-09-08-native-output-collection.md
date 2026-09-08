# Collect bounded native episode outputs

Date: 2026-09-08. Baseline: `e4075c3`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Implement `src/caplab/native_collection.py`, `tests/test_native_collection.py`,
a versioned collection contract and this record; link the runtime preparation
contract. Read only current source/contracts and newly generated synthetic
prepared runtimes. Create bounded synthetic nested sessions, diagnostics, binary
and non-ASCII files, missing paths, symlinks and special files; inject read/write
and publication failures. Run focused/full tests and a bounded local Python
producer through existing task capture, followed by collection. No native
inference, authentication, credentials, historical sessions/tasks, evidence
registration, tracker writes or messages. Preserve all existing source, policies,
profiles, launchers, frozen manifests, `docs/designs/`, worktrees and services.
Permit a local commit; authorization expires at commit. Retain probes and logs;
remove only enumerated doctrine scratch after receipt consolidation. Stop if
collection requires broader home access or mutation of the frozen launch path.

## Decision and preservation boundary

Select an episode collector whose source selection comes from an independently
anchored preparation receipt and a rebuilt canonical invocation. It copies only
that plan's declared session tree, diagnostics and final output, after the caller
has stopped writers. Retain exact preparation/invocation receipt bytes, and
capture native output bytes without JSON interpretation or newline conversion.
Share the existing task inventory engine for bounded descriptor-relative
no-follow copying, source change checks and explicit partial-failure behavior.
Use one total byte/entry allowance across all selected outputs. Preserve missing
paths in the final receipt; their absence is not an empty successful transcript.
Never follow a symlink at a selected root or parent; nested symlink targets are
retained literally. Unexpected object kinds fail without a collection receipt.

The collector has no launch, parsing, identity, eligibility, admission or scoring
authority. An isolated prepared root does not prove its actual contents came from
the configured native process. Child linkage, actual native emission, executable
and account binding, containment and study gates remain unresolved. Recording
all files under a selected session tree does not prove exhaustive native capture.
No-change leaves native outputs mutable and outside retained custody; whole-home
copying broadens access to credential/configuration surfaces. A new generic
filesystem copier would duplicate the established task capture owner. Reopen
this selection for a changed profile or measured collection requirement.

## Execution and verification evidence

The collector reuses the existing bounded receipt reader and task inventory
owner. It validates an independent preparation anchor, linked invocation bytes,
canonical plan and selected host paths before creating output. A single inventory
owns all selected locations and one shared quota. Opened descriptors have
structured lifetimes; filesystem and source-change errors propagate. The code
has no worker, cache, mutable retained caller input, native parser or fallback.
Explicit keyword limits follow the adjacent capture APIs; no new configurable
collector framework or change to shared filesystem code was needed.

Eleven focused tests passed in 1.119 seconds. Log:
`/tmp/caplab-native-collection-focused.log`. The first ten-test run had one
new-test fixture error: `claude-fable5-max` instead of the actual canonical
`claude-fable-5-max`; the builder rejected it. That log remains at
`/tmp/caplab-native-collection-initial-tests.log`. This is a new feature, not
an old-defect regression claim. Final tests cover both harness layouts, nested
child candidate files, invalid UTF-8/NUL/CRLF and non-ASCII path bytes, exact
receipt copies, home exclusion, missing files and empty directories, combined
receipt/artifact/entry limits, no-follow boundaries, FIFO rejection, changed
sources, final publication failure and refusal to reuse partial output.

The real subprocess test runs a local Python producer through bounded task
capture, verifies that task bundle and then collects the generated runtime.
Retained output still matches its hashes after selected sources are changed
or deleted. This tests custody mechanics, with no inference or native-format
claim. The separate retained probe exercises the same production APIs:
`/tmp/caplab-native-collection-probe.py` and
`/tmp/caplab-native-collection-probe.json`. Root:
`/tmp/caplab-native-collection-probe-04witxak`.
It preserves four synthetic output files, 86 artifact bytes and seven entries;
the task inspection verifies 22 task bytes, three entries, zero stream bytes,
4,427 receipt bytes and exit zero. Collection SHA-256:
`a8816e69883a0b42a28a46763b882a9f7c2c18bf38bf09d2617a468515fdef11`.
The probe separately checks each retained file's size and digest. Those checks
are not a general anchored native-collection reader or eligibility verifier.

Source/test hashes and direct-import checks are retained in
`/tmp/caplab-native-collection-source-check.json`. No unused direct imports were
found. Nine protected sources remain byte-identical to baseline `e4075c3`,
including native preparation, invocation, task/process capture and verification,
subject policy/validation and both legacy launchers. Python is 3.12.3. No
dependency, interpreter, CI, formatter or checker configuration changed.
The contract was checked against the implementation and exercised API, including
partial failure, source quiescence, missingness and non-eligibility claims.

Full `make check` passed: 1,032 tests in 173.616 seconds, four skips, exit zero.
Log: `/tmp/caplab-native-collection-make-check.log`. Afterward, source/test hashes
still matched and all nine protected sources were checked again against baseline.
No source or test changed during that full run. Documentation links resolve.
The prose review found no generic sentence requiring removal; contract caveats
name specific unverified behavior rather than claiming study readiness.

## Advisory doctrine and completion

Retrieval passed the release gate at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-053228b9d62f8319`, content SHA-256
`053228b9d62f8319f6262c23639638d7b1248a294ceb787966cc2be04dfb1848`,
uses `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9` and
`retriever-ec995ecdd083b2c8`. One evidence-gathering pass supplied five typed
records. Four citations classify as valid: `python-structured-cleanup` for
scoped descriptors, `python-text-bytes-boundary` for raw receipt/payload custody,
`implementation-placement-by-ownership` for shared inventory reuse, and
`agent-conduct-authority-bounded-action` for collection without inference or
admission. Repository authority and contracts govern all effects.

Six unmet obligations are nonmaterial to this bounded implementation:

- `implementation-placement-by-ownership`: `recurring change evidence when available`;
  the accepted missing collection requirement motivates this feature, with no
  historical churn or maintainability-improvement claim.
- `implementation-repository-language-conformance`: `CI and build matrix` and
  `formatter and static-tool configuration`; neither changes here, and no new
  cross-platform or tooling qualification is claimed.
- `python-repository-shaped-idiom`: `formatter linter and type-checker configuration`;
  this follows the existing capture owners, with no checker/formatter claim.
- `python-runtime-static-boundary`: `annotation maintenance cost` and
  `configured checker and Python version`; no static proof or annotation-cost
  claim is made. Actual local Python is recorded separately above.

`/tmp/caplab-native-collection-verification.json` consolidates packet identity,
citations, unmet obligations, source/probe checks and full-test results. It also
records hashes and paths of exactly eleven removed doctrine scratch files.
All test logs, probes, source checks and retained synthetic custody remain.

The collector is implemented and technically verified within its stated scope.
It supplies raw evidence preservation needed by CAPLAB-84; that item and the
CAPLAB-85 containment work remain incomplete. The next consumer needs an
anchored collection reader and session/attempt linkage before interpretation.
Native adapter integration, actual emission verification and the study gates
remain required. No ranking, placement, native qualification, roadmap completion
or independent acceptance is asserted.
