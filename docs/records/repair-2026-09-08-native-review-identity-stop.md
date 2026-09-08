# Stop native review continuation when model identity is unavailable

## Decision and authorization

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
authorizes a prospective repair to native review observation, custody loading,
attempt accounting, and preparation. Reuse the captured-model assessment from
ac04ad3. Record it alongside execution status, recompute it from retained
stdout when reading custody, and stop continuation when any prior attempt
has missing or mismatched model evidence. Preparation must reload custody
instead of trusting the caller's prior-attempt list.

Authorized effects are source changes, tests using newly authored local
fixtures, documentation, and this record. No model calls, spend, historical
inspection or rewriting, evidence admission, rescoring, ranking, placement,
tracker changes, or messages. The September 7 instrument disposition remains
in force. Stop if the repair requires an excluded effect. Revert this commit
to reverse prospective behavior; clean up only task-owned temporary artifacts.

Identity failure does not become a reviewer failure or authorize replacement.
Even an infrastructure attempt cannot proceed to its otherwise available
replacement while model evidence is unavailable. Preserve its execution
status and infrastructure accounting separately. Read-only identity accounting must
retain recorded attempts that pass the existing order and infrastructure
checks, report the first identity stop and subsequent
recorded attempt count, and keep unattempted primary slots explicit. It does
not retroactively authorize the recorded attempts or erase them.

New observations use version 2. Original version 1 records remain immutable;
their model evidence can be derived read-only from raw bytes for the current
continuation check. A stored version 2 assessment must agree with the same
raw-byte derivation. Neither a missing field nor a resealed false positive
may bypass the gate. Known malformed streams must still yield a retained
unverified observation, rather than leaving the attempt without a disposition.

## Observation and alternatives

At ac04ad3, record_native_review_observation stores status and usage without
the captured-model assessment. load_native_review_attempts verifies some
custody seals and returns four accounting fields. prepare_native_review_trial
uses only caller-supplied prior_attempts, so it can miss a completed failed
identity check or operate on a stale list. Model identity is checked only
later by normalization. Filtering the eventual score cannot prevent further
exposure or spend during an invalid campaign.

The selected repair puts the stop at preparation, before rendering or launch,
and preserves read-only accounting. Leaving continuation unchanged preserves
the exposure gap. Reclassifying identity failure as retryable infrastructure
would create a new attempt policy. Rejecting all read-only accounting after
the first failure would conceal already recorded exposure. No change to
reference truth, numerical grading, model roster, or model evidence criteria
is selected. This is a semantic repair, not a refactoring campaign.

Verify the record/load/prepare path with local sealed fixtures: matching,
missing and substituted model evidence; malformed JSON; false stored model
claims; stale caller state; explicit unattempted counts; no additional
rendering or model invocation after a stop; and retained read-only accounting
after an already recorded identity failure. Run the repository checks.
This repair does not establish full Binding attestation, capture completeness,
provider identity, live readiness, or independent instrument acceptance.


## Execution and compatibility

`assess_native_review_model` is shared by capture, observation, and custody
loading. Its malformed-stream result is unverified with reason
`native-trace-invalid`. Capture still rejects malformed JSON before grading;
observation can retain the failed execution and identity disposition.
Version 2 observations include the raw-linked assessment without changing
execution status or usage.

The loader validates the assignment against the instrument slot, checks
launch/completion/observation links, requires the attempt's own stdout path,
checks those stdout bytes against the observation hash, and derives identity
from the configured subject and those bytes. A version 2 recorded assessment
must equal that derivation. Version 1 remains readable without modification;
a missing old assessment cannot create a positive model claim.

Preparation reloads this accounting before any task rendering and compares it
to the supplied prior list. A difference raises `native_review_prior_attempts_changed`.
The first identity exclusion supplies `identity_stop`; the overall stop reason
prevents another primary or replacement. Infrastructure accounting can still
show `pending_replacement_for`, but a non-null stop reason withholds permission
to prepare it. `attempts_after_identity_stop` reports subsequent recorded
exposure without erasing or authorizing it. `unattempted_primary_slots`
counts slots with no primary attempt; a failed primary awaiting replacement
has already been attempted and does not inflate that count.

Existing limits, order checks, review schema, numerical scoring, and other
stop rules remain. `complete` still means all primary assignments have been
accounted for; it does not override an identity stop or establish calibration.
Normalization remains able to describe a completed fixture with excluded
identity rows, using the scoring exclusion from ac04ad3.

Changing the runner invalidates the old frozen manifest's runner-source hash.
The manifest was not updated. Four prior live-contract tests initially failed
at that binding check. They now create a separate temporary manifest with a
new local fixture campaign ID and the current runner hash. A new negative test
proves mismatching source bytes are rejected. The fixture does not authorize
an actual live campaign or renew the historical manifest's expiry.

This check operates before preparation. Native runtime preflight still occurs
before preparation in the execution entry point; the reviewer invocation
occurs only after the stop check passes. The execution regression patches
preflight to avoid external calls and verifies the reviewer is never invoked.
No continuous-custody or concurrent-writer safety claim is added. Full Binding
attestation, Codex rollout integration, and capture configuration remain open
under CAPLAB-79. No historical attempt was inspected or changed this turn.


## Verification

Before repair, eight new tests produced three assertion failures and four
missing-field errors (`/tmp/caplab-native-stop-red.log`). They observed missing
identity disposition and preparation accepting stale or failed-identity
accounting. No native model was invoked during reproduction.

The final focused run passed 46 review-dissent tests in 8.175 seconds;
see `/tmp/caplab-native-stop-focused.log`. Eleven new identity-stop tests
exercise observation, custody loading, accounting, preparation, and execution.
The additional manifest-binding regression verifies that changing the runner
requires a correspondingly authorized source binding. Positive tests preserve
matching-model preparation and infrastructure replacement behavior.

Final `make check` passed 853 tests with 4 skips in 160.568 seconds;
see `/tmp/caplab-native-stop-make-check.log`. No source or test edits followed
that run. `git diff --check` passed. Existing untracked `docs/designs/` content
was preserved. The tests establish the stated mechanical continuation gate;
independent acceptance and future campaign readiness remain unestablished.


## Advisory doctrine receipt

Packet `pkt-2d77621d49dbf995`, content SHA-256
`2d77621d49dbf995bbbc128be72c3c279093549a25ea9488eb6c514782401e7b`, uses release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts are
`operations-gate-authoritative-signal`,
`universal-repository-contract-precedence`, and
`agent-conduct-authority-bounded-action`. Preparation owns advancement;
raw captured model fields govern this necessary identity condition. Repository
authority governs the repair; no doctrine packet authorizes execution.
Citation consumption is recorded locally.

Remaining obligations are nonmaterial to the bounded local-fixture claim:

| Concept | Missing requirements | Scope reason |
| --- | --- | --- |
| data-dedup-key-identity-completeness | an explicit enumeration of the record's identity dimensions matched against the key's columns; logical-identity definition of the affected record; the conflict-handling semantics at that key - abort update or silent drop | No deduplication key or conflict policy changes; existing exclusive attempt files and configured identities remain. |
| data-ingest-population-scoping | a dry-run enumeration with counts compared against expectation; the discovery pattern shown to match the specification's depth and class constraints; the input population specification; the specified input population stated precisely | No archive ingest or backfill ran. Tests use newly authored immediate-child attempt directories; discovery scope is unchanged. |
| implementation-rank-before-truncate | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No ranking, relevance selection, truncation, or top-N operation occurs. |
| operations-external-capability-verification | access to the real device or endpoint; an end-to-end verification artifact against the actual device or endpoint; or an explicit record that verification is provisional; the real system's own statement of its capability - device configuration output wire capture or endpoint self-description | Verification is limited to local fixtures. No real endpoint was invoked; no live-readiness or provider-capability claim is made. |
| operations-gate-authoritative-signal | eval-versus-serving configuration parity | Serving parity and complete capture remain unverified; this tests a retained-model-field stop only. |
| operations-symptom-cause-monitoring | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No monitoring service, page, or operational alert policy changes. |
| python-mutable-ownership | concurrency; lifetime and size | The serial preparation check adds no concurrency protocol or memory/performance claim. The source continues to read each retained stdout in full. |
| task:defect-repair | evidence-incidents | The defect is established by inspected source and failing local fixtures; no new production incident or historical audit is claimed. |
