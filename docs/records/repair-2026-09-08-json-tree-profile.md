# Preserve tree review routing for structured artifacts

## Decision and authorization

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
selects a prospective correction to `calibrate.profile_for_artifact`:
non-change-set artifacts use `v1-tree` when tree mode is selected, whether
or not their body parses as JSON. Change sets retain `v3-changeset` in tree
mode and `v2-changeset` otherwise. Non-tree document routing stays `v1`.
The existing definition of a change-set-shaped body is unchanged.

Authorized effects are this source correction, regression tests using newly
authored disposable artifacts and local echo processes, and this record.
No historical case or campaign is evaluated, rewritten, admitted, or
rescored. No model calls, sweeps, new qualification, ranking, placement,
tracker writes, or changes to the parked study are authorized. The
2026-09-07 instrument disposition remains binding. Stop if verification
requires such effects. Revert the source commit to undo this repair; clean
up only its disposable fixture and advisory retrieval inputs.

## Observation and inference

At parent `341e3d5`, non-JSON document bodies correctly take the
`v1-tree` branch. Parsed JSON bodies without the top-level `files`, `base`,
or `base_composition` markers fall through to `v1`, even with `tree=True`.
`pool_runner.measure_case` then indexes `TREE_PROFILE_BODIES`, which has
only `v1-tree` and `v3-changeset`. After passing the mechanical pair gate
and materializing the workspace, the case raises `KeyError` before either
arm reaches a reviewer. This is an apparatus failure, not subject behavior.

The accepted tree environment uses the artifact's shape and the selected
environment to route its contract. Successful JSON parsing does not remove
the environment. The repair changes that single fallback; it adds no new
prompt text, classifier, operator, case population, or scoring rule. Leaving
the defect intact loses eligible structured artifacts; catching the error
and scoring an empty answer would misattribute it to the reviewer.

`run_spec.instrument_sources` already hashes `calibrate.py`, so this source
change produces a different prospective run specification and cannot
silently resume old pool evidence under the same source identity.

## Verification

The two new tests failed before the repair: nine JSON-shape routing
assertions and a `KeyError: 'v1'` from the actual tree-runner lookup. See
`/tmp/caplab-json-tree-red.log`. The paired fixture uses a newly authored JSON
summary that cites a file in a disposable git tree, the existing
`dangling_reference` operator and pair gate, and a local echo process.
After the correction, 25 focused checks pass in 0.234 seconds; see
`/tmp/caplab-json-tree-focused.log`. Both arms retain the rendered tree
contract and actual base location, the original control body reaches the
adapter, and the base manifest still verifies. The routing matrix includes
objects, arrays, strings, numbers, Booleans, and null; existing tests protect
change-set routing and missing-base behavior.

The fixture disables bubblewrap for its local echo process to inspect the
received prompts. It makes no new containment or native-harness claim. Its
mechanical contrast tests routing and capture only, not independent
production truth or reviewer discrimination. `dangling_reference` remains
sentinel-only under the standing disposition. No case is admitted by this
repair. Full `make check` passed 825 tests with 4 skips in 125.995 seconds;
see `/tmp/caplab-json-tree-make-check.log`. `git diff --check` passed.


## Advisory doctrine receipt

Packet `pkt-b8adfe2e470595c7`, content SHA-256
`b8adfe2e470595c7363abaec764652b62fe5e9032f5a6bebf5dbc1ad00e2d8be`, was assembled from
source, repository contract, and local test evidence using release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. The applicable guidance is
`implementation-placement-by-ownership`,
`universal-repository-contract-precedence`,
`universal-evidence-before-intervention`, and
`agent-conduct-authority-bounded-action`. The existing router owns the
correction; the caller should not invent a replacement contract or an empty
review. The packet's execute ceiling is advisory and does not supply the
CAPLAB authorization above. Citation consumption is recorded locally.

The remaining obligations are nonmaterial to this bounded source correction;
no broader operational, population, or ranking claim is made.

| Concept | Missing requirements | Reason |
| --- | --- | --- |
| `data-dedup-key-identity-completeness` | an explicit enumeration of the record's identity dimensions matched against the key's columns; logical-identity definition of the affected record; the conflict-handling semantics at that key - abort update or silent drop | No database key or deduplication behavior changes. |
| `data-ingest-population-scoping` | a dry-run enumeration with counts compared against expectation; the discovery pattern shown to match the specification's depth and class constraints; the input population specification; the specified input population stated precisely | No input discovery, admission, or backfill is performed; the new artifact is disposable test data. |
| `implementation-placement-by-ownership` | recurring change evidence when available | The current router and consuming lookup establish ownership without a longitudinal co-change claim. |
| `implementation-rank-before-truncate` | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No top-N or ranking operation is involved. |
| `operations-gate-authoritative-signal` | eval-versus-serving configuration parity; inventory of gates and the signals they observe; proof the check reads that signal rather than a derived view; the authoritative signal named for each gate | No operational gate, provider identity, or serving-parity claim is made. Existing pair and measurement gates are unchanged. |
| `operations-symptom-cause-monitoring` | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No service monitor or paging policy changes. |
| `task:defect-repair` | evidence-incidents; evidence-runtime-observation | The failure is established by local executable counterexamples; no historical production incidence is claimed. |
