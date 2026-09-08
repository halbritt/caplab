# Preserve native timeout output and attempt records

## Decision and authorization

The primary agent selects a prospective timeout-capture repair under ADR 0026
and the active CAPLAB improvement goal. Native stdout and stderr are captured
and retained as bytes. A timeout's partial output must not prevent recording
the failed attempt. Timeout facts belong in attempt metadata, not text appended
to native stderr. Missing or undecodable event evidence cannot establish a
successful attempt.

Authorized effects are source changes, newly authored local subprocess
fixtures, tests, and this record. Preserve historical captures, judgments,
and registrations. The public ladder boundary remains closed; no native model
call, recovery of historical attempts, model spend, ranking, placement, or
tracker write is authorized. Stop if verification requires any such effect.
The change is reversible by commit revert; dispose only of task-owned fixture
and doctrine inputs. Require a local subprocess counterexample and caller
failure records, then the full repository suite.

## Observation and causal explanation

At parent `ab8990f`, the artifact-rater and retained ladder mechanics use
`subprocess.run(text=True)` and then assume timeout stdout/stderr are strings.
They concatenate stderr with a timeout message and encode stdout afterward.
Partial `TimeoutExpired` output is bytes: either operation can raise before
the output files and attempt record are written. A timed-out attempt can thus
leave only a partial directory, losing failure evidence and denominator state.

The repair uses binary subprocess capture, preserves raw streams unchanged,
and records `timed_out` and `timeout_seconds` separately. Decoding occurs only
at event interpretation and rejects invalid UTF-8 as unavailable evidence.
Normal text callers of the existing event helpers remain supported. No
benchmark population or missingness policy is changed; the failed native
attempt becomes inspectable under the existing failure disposition.

Leaving these paths unchanged loses precisely the evidence needed to inspect
failures. Decoding partial output with replacement before saving would corrupt
raw custody; appending local diagnostic prose would invent native stderr.
The selected repair retains the bytes and keeps diagnostic facts separate.

## Verification

The local subprocess fixture writes known stdout and stderr bytes, including
an incomplete UTF-8 sequence and an invalid stderr byte, then sleeps. Its
`subprocess.run(text=True)` timeout returns those exact bytes. Before repair,
the two caller tests raised `TypeError: can't concat str to bytes`; an empty
output fixture also exposed the invented timeout text in native stderr.
Log: `/tmp/caplab-timeout-red.log` (one failure and two errors).

The final focused capture suite passes 15 tests:
`/tmp/caplab-timeout-final-focused.log`. It covers preserved partial/empty
streams, failure records and hashes, no accepted judgment on timeout, a
normal exit 124 distinct from timeout, unmodified CRLF/non-ASCII output, and
invalid UTF-8 refused both during initial interpretation and recovery. Existing
custody-conflict and write-failure counterexamples remain protected. Separate
event-helper tests cover valid binary input, undecodable bytes, and non-object
records without an unhandled exception.

Final `make check` passed: 778 tests, four existing skips, 120.423 seconds.
Log: `/tmp/caplab-timeout-final-make-check.log`. An earlier full run passed 777
tests before the final recovery boundary and its regression were included.
`git diff --check` passed. No historical timeout is claimed to have occurred,
and no study acceptance or independent review is claimed from this repair.
The eight original capture/custody tests remain local fixtures; none of these
checks launched a native agent or revived a campaign.

## Engineering guidance

Pincite packet `pkt-fbb6a971f86f0418`, content SHA-256
`fbb6a971f86f0418ca2fedd37f99712d275784c215289bb9d1f72c7ede67cf78`,
used typed source, contract, and local subprocess evidence. Doctrine version:
`doctrine-f6bbb5196a3f8bf9`; retriever:
`retriever-ec995ecdd083b2c8`. Applied concepts were
`python-text-bytes-boundary` and
`universal-repository-contract-precedence`. Both structured citations were
validated and traced. The release was validated in the preceding custody
repair at `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.

Material questions are the subprocess byte contract, preservation of raw
output, failure-record disposition, invalid-text behavior, authority, and
regression evidence. The recorded decision, actual local timeout, source,
and tests address them. Generic obligations concerning bulk ingestion,
database deduplication, symbolic configuration references, top-N selection,
operational paging, and eval-versus-serving parity are nonmaterial to these
two capture paths. No production incidence, provider behavior, system-wide
capture completeness, or study validity is inferred from local fixtures.
Temporary packet, evidence, and citation inputs are deleted after tracing;
test logs remain available for inspection.
