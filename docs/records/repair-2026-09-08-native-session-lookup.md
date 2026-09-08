# Reject ambiguous native session discovery

Date: 2026-09-08. Baseline: `a0e9fdd`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Use new temporary synthetic session trees to reproduce the two `_find_rollout`
helpers' substring/glob matching and last-filename selection. Implement one
shared lookup in `src/caplab/artifact_rater.py` and use it from
`scripts/caplab-artifact-rater.py` and `scripts/caplab-ladder-subject.py`.
Add `tests/test_native_session_lookup.py`,
`docs/product/contracts/native-session-lookup-v1.md`, and this record.
Require a unique regular candidate with an exactly matching complete filename
ID; reject unsafe ID patterns, linked search paths, matching nonregular files,
ambiguous candidates and traversal failures. Preserve bounded waiting for a
new candidate, caller-specific error types, and all later byte/thread checks.

Only temporary synthetic directories may be enumerated or used for lookup
execution in this repair. Do not scan the actual home session tree, read native
captures, run a harness/authentication probe, copy or admit historical evidence,
change a frozen manifest, renew a campaign, spend model calls, score a reviewer,
change ranking/placement, or write to Plane or another external system.
The historical ladder's unconditional execution closure remains in place.
Preserve `docs/designs/`, sibling worktrees, services and timers.

Run regressions against the old helpers first, then the shared implementation,
existing custody/caller tests and `make check`. Retain execution receipts under
`/tmp`; remove only named doctrine scratch after recording its receipt.
Authorization expires at commit. Stop on unresolved lookup ambiguity; do not
resolve it by choosing a path, deleting a duplicate, or opening unrelated bodies.

## Observation and selected response

Both helpers currently expand `**/*{thread_id}*.jsonl`, sort matches, and return
the last one. A matching substring can name a different session. Glob syntax
in a supplied thread ID changes the search. More than one matching path is
silently reduced to one without establishing which capture belongs to the
attempt. CAPLAB-79 requires exact session linkage and stops on ambiguity.

Select a shared filename-discovery policy for timestamped rollout names:
`rollout-YYYY-MM-DDTHH-MM-SS-<thread-id>.jsonl`. Compare the whole extracted ID,
without case conversion or normalization. This is CAPLAB's discovery grammar,
not a complete or future-proof native-provider schema. The lookup is read-only;
it produces a candidate path, never a model attestation or custody admission.
Native metadata must still match the stdout thread ID after retention.

No change retains unsupported selection. Reading every session body would
expand evidence access; choosing newest, largest, or identical-looking files
would not establish unique linkage. Share this policy in the existing rater
module because both callers already use its preservation and identity contract.


## Execution and verification

Added `find_rollout` and its read-only candidate traversal beside the existing
rater preservation/attestation functions. Both script wrappers use it; the
ladder wrapper preserves its `NativeSubjectError` interface. Removed the
rater script's now-unused `time` import. No native command, prompt, parser,
preservation, judgment derivation, recovery receipt, or ladder closure changed.
This is an authorized semantic lookup repair with shared placement, not an
independent architecture refactor.

The old wrappers were exercised on new temporary trees. Three targeted tests
produced six failures: two wrappers each selected duplicate-ID candidates,
matched `thread-12?` to `thread-123`, and matched a longer ID containing the
requested substring. Receipt: `/tmp/caplab-session-lookup-callers-red.log`.
The earlier full new-test run also reported missing-helper errors because the
new API did not yet exist, and `*` triggered pathlib's invalid-glob exception;
those are not counted as demonstrated false path selections.

Twelve new tests cover both callers, exact whole-ID lookup without body reads,
source preservation, case differences, invalid IDs and deadlines before
traversal, symlink roots/directories/candidates, matching directories and FIFOs,
root-metadata/enumeration failures, and a candidate appearing during bounded
waiting. The wait fixture publishes a file at the sleep seam rather than using
a real sleep. Focused lookup, native custody and rater tests passed 48 tests
in 1.354 seconds: `/tmp/caplab-session-lookup-focused-final.log`.

AST and direct-import-use checks passed for the three changed Python files and
the new test module. Source hashes and those checks are retained in
`/tmp/caplab-session-lookup-source-check.json`. The exact existing caller paths
were inspected: live scoring and first recovery preserve and attest the chosen
path; already-preserved recovery verifies its own retained hash and metadata.
Lookup failures reach their existing failure paths. No past receipt was
reprocessed to test these claims.

## Limits and next boundary

The [lookup contract](../product/contracts/native-session-lookup-v1.md) defines
this filename grammar and its limits. It is not an observed guarantee about
every installed or future Codex version. Only synthetic trees were enumerated;
actual home sessions and native bodies were not read. A returned filename still
needs byte custody and thread/model/effort attestation. Traversal is not atomic
and cannot prevent a later path replacement, byte change or new duplicate.
Stable source sealing remains an unimplemented requirement of the prospective
CAPLAB-79 recorder.

Existing wrappers still supply their home session root. This repair does not
establish isolated runtime capture, complete child-session linkage, native
compatibility, full bounded capture integration, redaction, or CAPLAB-84
completion. It makes no claim about historical defect frequency, reviewer
accuracy, capability, ranking, placement, or independent acceptance. Reopen the
lookup grammar if a selected native version demonstrably changes its filenames;
do not restore substring matching as an automatic compatibility fallback.

## Doctrine receipt

The release retrieval-state gate passed. Release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`.

Final packet `pkt-6ab82d469c861654`, SHA-256
`6ab82d469c8616541e0988d06324abd779e9fbec86a27e9ce0909b8aa8da1abd`.
One evidence-gathering pass supplied five typed records: authority, repository
contracts, source structure, tests and the old-caller reproduction. Retrieval
matched no precisely nominated concept; the packet supplies baseline, routed,
prerequisite and kernel guidance.

Applied `universal-evidence-before-intervention` to require old-caller failures;
`universal-repository-contract-precedence` to preserve evidence/authority
boundaries; `implementation-placement-by-ownership` to share the actual two
callers' lookup policy; and `agent-conduct-authority-bounded-action` to keep
synthetic discovery verification separate from real-session access or launch.

All 14 remaining obligations are nonmaterial to this lookup repair:

| Group | Exact unmet requirements | Classification and reason |
|---|---|---|
| `implementation-placement-by-ownership` | recurring change evidence when available | Nonmaterial: two current callers demonstrably share the lookup policy; no claim of recurring churn or architecture-cost reduction is made. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI, formatter or static-tool conformance is claimed. Verification uses the existing Makefile, local interpreter and executable tests. |
| `python-mutable-ownership` | concurrency; lifetime and size | Nonmaterial: no concurrent worker, retained cache or input mutation is added; the candidate list is local to a lookup. No memory-scaling or atomic-directory claim is made. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no formatter, linter or type-checker policy changes or conformance claims. |
| `python-runtime-static-boundary` | annotation maintenance cost; checker and trust-boundary evidence; configured checker and Python version | Nonmaterial: no annotation or checker policy changes; executable validation and filename/caller tests establish the bounded lookup claim. |
| `python-structured-cleanup` | acquisition and release paths; exception and cancellation behavior; nesting order; owner and lifetime; resource ownership and failure policy | Nonmaterial: no manual file descriptor, native process or custody resource is acquired. Standard library traversal and temporary test owners are used; no broader cancellation or resource-lifecycle guarantee is claimed. |


## Completion checks

`make check` passed 941 tests with four skips in 120.964 seconds:
`/tmp/caplab-session-lookup-make-check.log`. No source or test file changed
after that check began. Final file/link, source-preservation and ladder-closure
checks are retained in `/tmp/caplab-session-lookup-verification.json`.

Four doctrine citations classified as `valid-packet-citation`; the packet
identity, applied concepts and obligation table above retain the receipt.
The eleven named task doctrine scratch files were removed after recording it;
regression, focused/full test, and source-check receipts remain. No tracker
field or external message was changed. Commit closes this lookup repair,
not the broader measurement goal or native capture integration.
