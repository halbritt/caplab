# Separate rater validation from judgment publication

## Decision and authorization

The primary agent, under ADR 0026 and the active CAPLAB improvement goal,
selects a prospective publication repair. New immutable attempt records use
`caplab-artifact-rater-attempt/2`: `validated` describes evidence validation,
not publication. A validated record retains the candidate judgment before
publication. `accepted.json` is the publication marker and names the record
hash supporting it. Publish that marker atomically without replacement.

A failed publication must be retried from preserved evidence without a new
native call. A failure to save the attempt record must leave no publication
marker. A partial attempt without its record requires disposition rather than
an automatic replacement call. Existing recovery receipts may support a retry
only when they agree with the current validated evidence; their mere presence
cannot mean publication completed. Publication I/O failure stops the call
rather than falling through to another native invocation.

Authorized effects are prospective source changes, newly authored disposable
fixtures, tests, and this record. No historical record, answer, judgment,
capture, registration, or admission may be rewritten or recovered under this
authorization. No model calls, spend, ranking, placement, or tracker writes
are authorized. Stop if verification requires those effects. Preserve the
closed public ladder boundary. The source commit is reversible; remove only
task-owned fixture and doctrine inputs. Verify publication and record-write
failures, retries, collisions, and normal operation, then run the full suite.

## Observation and selected repair

At parent `42e4e47`, the fresh rater path sets `accepted=True` before writing
the publication marker, then writes the attempt record afterward. Marker
failure leaves a false accepted flag; record failure can leave a marker with
no supporting attempt record. Recovery writes its receipt before publication
and skips any attempt whose receipt already exists. A marker-write failure
therefore causes the next call to skip preserved evidence and potentially
launch another model invocation. The retry loop also swallows I/O failures.

The repair records validation first and publishes a complete marker afterward.
It retains a candidate for retry, checks its identity and derivation against
preserved evidence, and uses the captured rollout rather than requiring the
live source session to remain available. The normal and resumed marker carry
the same record hash and candidate. Legacy recovery can resume matching
receipts without replacing them. All source records remain immutable.

Merely moving the accepted flag would leave marker/record ordering and retry
loss unresolved. Treating receipt existence as success would conceal failed
publication. This change separates the two observable states instead. It is
not a new guarantee of power-loss durability or a general native-launch
transaction; interrupted attempts without a record remain explicit stops.

## Verification

The pre-repair run failed four tests:
`/tmp/caplab-publication-red.log`. Disposable fixtures demonstrated a false
accepted flag after marker-write failure, a published marker after record-write
failure, a skipped legacy recovery after publication failed, and an unexpected
new native-call attempt after recovery I/O failure.

The final publication suite passes 13 tests:
`/tmp/caplab-publication-final-focused.log`. It covers all four failures plus
retry with the live source removed, unchanged supporting records, changed
candidate and stream refusal, missing/unreadable records, conflicting legacy
receipts, marker-to-record hash checks, complete JSON visibility, no-replacement
collisions, and cleanup after a flush failure. Fake native-call assertions
verify that these publication retries do not invoke a model. The existing
23-test capture/custody suite also passes under the new validation-record
semantics. Its new-record assertions now inspect `validated`; its legacy
fixtures retain their original `accepted` field and bytes.

Full `make check` passed: 808 tests, four existing skips, 150.284 seconds.
Log: `/tmp/caplab-publication-make-check.log`. `git diff --check` passed.
JSON is written to a private temporary file, flushed, and linked into place
without replacement; the temporary name is removed afterward. The record
precedes the marker. Parent-directory
power-loss durability and a complete native-launch transaction are outside
this repair's claim. No historical publication failure, independent review,
or study acceptance is inferred from local fixtures.

## Engineering guidance

Typed source, contract, and fixture evidence informed Pincite packet
`pkt-1f95bef2a8a4e90f`, content SHA-256
`1f95bef2a8a4e90f7ec2f2c37507a3a526ed52857b87ded75d98ad4132e2209c`,
doctrine `doctrine-f6bbb5196a3f8bf9`, retriever
`retriever-ec995ecdd083b2c8`. Applied concepts were
`implementation-placement-by-ownership` and
`implementation-risk-driven-tests`; both citations were validated and traced.

Material questions are authority, state meaning, effect ordering, retry
behavior, evidence identity, preservation, and regression evidence. The
decision, concrete failure traces, implementation, and tests above address
them. Generic obligations about bulk ingestion, database deduplication,
symbolic configuration references, top-N selection, operational paging, and
serving parity are nonmaterial to this file-publication repair. No live
incident, provider observation, complete crash-durability guarantee, or
measurement-validity conclusion is supplied by these fixtures. Task-owned
doctrine inputs are removed after tracing; test logs remain available.
