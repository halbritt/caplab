# Require complete native event evidence before attempt credit

## Decision and authorization

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
selects a prospective repair to artifact rating, its recovery path, and ladder
disposition. A successful process exit and valid answer file do not establish
successful native execution. Require one unambiguous thread start, one turn
start, and one final turn completion, with no failure, rejected rate limit,
malformed JSON, duplicate object keys, or trailing incomplete activity.

This adopts for these callers the structural completion contract already
enforced by `revbench.codex.derive_codex_response`. Revbench's implementation
and response-schema derivation remain unchanged. A small shared event owner
will expose thread identity extraction and completed-turn validation; the
existing artifact-rater helper will preserve its error API.

Authorized effects are code, new local fixture tests, and this record.
Historical evidence and accepted judgments must not be rewritten, recovered,
or revoked under this authorization. The public ladder remains closed. No
native model execution, spend, ranking, placement, or tracker write is
authorized. Stop if verification requires those effects. The source repair
is reversible by commit revert; dispose only of task-owned fixture and
doctrine inputs. Verify original acceptance counterexamples, valid execution,
and caller failure records, then the full repository suite.

## Observation and causal explanation

At parent `e54cb79`, artifact rating and recovery check exit status, answer
shape, and rollout tuple but never require a completed native turn. Ladder
classification remembers any `turn.completed`, skips malformed JSON, and does
not reject a later started but unfinished turn. Thread extraction returns the
first identifier without checking subsequent identity conflicts. These paths
can grant usable-attempt credit to contradictory or incomplete evidence.

The selected repair centralizes the shared stream contract while retaining
separate caller decisions: the rater withholds accepted judgment; the ladder
records infrastructure with unknown behavioural attempt status. Failure facts
remain failure facts even if later events include a completion. Thread-only
extraction does not require completion, so partial but well-formed streams can
still identify preserved failure evidence. No historical drift or historical
false acceptance is inferred from prospective code counterexamples.

## Verification

The pre-repair caller suite failed nine assertions:
`/tmp/caplab-completion-red.log`. Newly authored streams demonstrated initial
rater acceptance without completion, after failure, with trailing incomplete
activity, without a turn start, with a second thread, with duplicate JSON
keys, and with a rejected rate limit. A separate recovery fixture accepted a
failed turn despite a valid-looking answer file.

The repaired caller suite passes all 17 tests:
`/tmp/caplab-completion-green.log`. Six additional event-contract tests pass:
`/tmp/caplab-completion-events.log`. These cover exact lifecycle boundaries,
thread-only evidence, whole-stream identity, failure persistence, duplicate
keys at nested levels, non-object records, valid Unicode line separators
inside JSON strings, and CRLF. Ladder tests preserve both behavioural attempt
and non-attempt classification for complete evidence, and reject trailing or
malformed activity. The old positive caller fixtures were completed with an
explicit `turn.started` event under the adopted contract; no historical stream
was edited to meet it.

Full `make check` passed: 787 tests, four existing skips, 119.632 seconds.
Log: `/tmp/caplab-completion-make-check.log`. `git diff --check` passed.
This repair does not prove provider identity, complete capture of provider
requests, answer correctness, or that an answer file was derived from a
particular native message. Those claims remain separate from structural native
completion. No independent review or study acceptance is claimed.

## Engineering guidance

Typed source, contract, and fixture evidence informed Pincite packet
`pkt-97716e39b3f7b9ba`, content SHA-256
`97716e39b3f7b9ba4a7524ddce6742e4872786545af8a0621d345a7a99226765`,
doctrine `doctrine-f6bbb5196a3f8bf9`, retriever
`retriever-ec995ecdd083b2c8`. Applied concepts were
`implementation-placement-by-ownership` and
`implementation-risk-driven-tests`; both citations were validated and traced.

Material obligations concern authority, the accepted completion contract,
caller credit, preservation boundaries, causal reproduction, and regression
evidence. The decision, source pointers, and tests above address them. Leaving
the callers unchanged permits contradictory evidence to support measurement;
requiring only a completion substring would preserve the same ambiguity.
Generic obligations concerning database identity, bulk ingestion, symbolic
configuration references, top-N selection, operational paging, and serving
parity are nonmaterial to this structural parser repair. No live incident,
provider verification, or complete measurement-validity claim is supplied by
these local fixtures. Task-owned doctrine inputs are removed after tracing;
verification logs remain available.
