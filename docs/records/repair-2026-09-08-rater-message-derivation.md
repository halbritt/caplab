# Bind artifact judgments to the captured native message

## Decision and authorization

The primary agent selects a prospective judgment-derivation repair under
ADR 0026 and the active CAPLAB improvement goal. Artifact rating and recovery
must derive their exact Boolean judgment from the last completed native
agent-message item inside the completed turn. The separate last-message file
must parse to the same exact Boolean mapping. Formatting differences may be
accepted; missing, ambiguous, malformed, or contradictory evidence must not.

Record the captured event-stream hash, selected event index and item ID,
extracted-text hash, last-message-file hash, and comparison rule with the
admitted judgment. Preserve raw bytes and the current capture/completion gates.
This follows the source-derived response pattern already used by Revbench,
without changing Revbench's response schema or implementation.

Authorized effects are source, new disposable fixtures, tests, and this
record. No historical answer, capture, admission, registration, or judgment
may be changed or recovered under this authorization. No model execution,
spend, reviewer ranking, placement, or tracker write is authorized. Stop if
verification requires those effects. The public ladder boundary stays closed.
Revert the source commit to undo the repair; remove only task-owned temporary
fixtures and doctrine inputs. Verify original false-admission counterexamples,
matching answers, message selection and provenance, then the full suite.

## Observation and selected repair

At parent `b4ebaba`, rating and recovery read Boolean judgments from
`last-message.txt`. They separately validate stream completion and rollout
identity but never require a captured agent message or compare its answer.
The admitted judgment can therefore disagree with the response that the native
stream records. Reading the sidecar again for its hash also leaves the hash
separate from the parsed bytes.

The shared Codex event owner will select the final completed agent-message
item, reject malformed candidates rather than falling back to an earlier one,
and keep item location within the completed turn. The artifact-rater owner
will enforce strict JSON and the exact Boolean-code contract on both answers,
compare them, and derive the judgment from the stream. Each hash will describe
the same bytes used for its derivation.

Leaving the paths unchanged does not bind a score to the measured subject's
response. Comparing only schema or tuple identity cannot resolve that gap.
The selected comparison permits JSON whitespace and key-order differences,
while refusing any changed Boolean or ambiguous duplicate key. It establishes
response provenance, not answer correctness or reviewer capability.

## Verification

The pre-repair caller run failed six assertions:
`/tmp/caplab-derivation-red.log`. New fixtures exposed admission with a changed
native Boolean, no captured agent message, tool output substituted for an
agent message, a contradictory later message, missing message text, and a
recovery-sidecar mismatch. All fixtures use local files and a fake native
process; no historical capture was changed or admitted.

The final caller suite passes 23 tests:
`/tmp/caplab-derivation-final-focused.log`. Matching JSON with different
whitespace and key order is admitted with `caplab-artifact-rater-derivation/1`
provenance. Tests inspect source hashes, selected event/item, and equality of
the derivation in the attempt and admitted judgment. Matching fixture recovery
also records derivation without rewriting the original attempt record.
Duplicate keys in either answer and invalid UTF-8 in the sidecar fail without
admission. Eight event-owner tests pass, including malformed later candidates,
duplicate item identities, messages outside the turn, and tool output after
the final agent message.

Full `make check` passed: 795 tests, four existing skips, 123.894 seconds.
Log: `/tmp/caplab-derivation-make-check.log`. `git diff --check` passed.
No historical mismatch, independent review, or study acceptance is claimed.
Existing admitted records are not revoked or reinterpreted by this repair;
the new derivation applies to new admissions through the repaired paths.

## Engineering guidance

Pincite packet `pkt-0014ede88753f7ae`, content SHA-256
`0014ede88753f7aee3c976d0861028bd75aea71046620e4654a987ce68707c18`,
used typed source, contract, and fixture evidence. Doctrine:
`doctrine-f6bbb5196a3f8bf9`; retriever:
`retriever-ec995ecdd083b2c8`. Applied concepts were
`implementation-placement-by-ownership` and
`implementation-risk-driven-tests`; both citations were validated and traced.

The material questions concern authority, source-message selection, Boolean
comparison, byte provenance, failure behavior, preservation, and regression
evidence. The recorded decision, source paths, and tests above address them.
Generic obligations about bulk ingest, database deduplication, symbolic
configuration references, top-N selection, operational paging, and serving
parity are nonmaterial to this derivation repair. No provider observation,
production-incidence estimate, independent correctness label, or study-validity
claim is inferred from local fixtures. Task-owned doctrine inputs are removed
after tracing; the test logs remain for inspection.
