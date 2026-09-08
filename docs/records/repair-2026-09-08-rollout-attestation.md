# Whole-capture Codex tuple attestation

## Decision and authorization

The primary agent, exercising ADR 0026 delegation under the active CAPLAB
improvement goal, selects a prospective repair to `read_rollout_attestation`.
The destination study's per-episode attestation requirement and CAPLAB-79's
per-turn capture requirement govern this repair. The reader must reject a
captured model or effort change even if a later record restores the original
tuple. Configuration events alone do not establish observed turn identity.

Authorized effects are source, local fixture tests, and this record. Preserve
the successful return fields for a consistent, complete captured tuple; reject
malformed records, incomplete turn tuples, conflicting session metadata, and
settings that contradict the observed tuple. Hash the same bytes that were
parsed. Require at least one complete turn context. This verifies consistency
within supplied bytes, not that every provider request was captured or that a
provider served the requested model. Completion remains a separate check.

No historical capture, judgment, registration, or score may be rewritten or
recovered under this authorization. No model calls, spend, ranking, placement,
or tracker writes are authorized here. Stop if verification requires those
effects. Source changes are reversible with a commit revert; temporary local
fixtures are disposable. Verification must reproduce the old false attestation,
exercise rejection and valid-capture boundaries, and pass the repository suite.

## Observation and causal explanation

At parent `7fb86d2`, the reader overwrites model, effort, session, and CLI
metadata as it reads. A middle model/effort change disappears if a later turn
returns to the first tuple. Missing turn fields inherit preceding values, and
malformed JSON is skipped. The returned hash is obtained from a second file
read. Both ladder subject execution and artifact rating consume this reader;
they already treat `CalibrationError` as failure rather than an attested pin.

Leaving the reader unchanged would allow mixed native subjects to appear pinned.
The selected repair belongs in the existing reader, preserving caller APIs and
avoiding a second attestation policy. It does not establish that any historical
run actually drifted.

## Verification and disposition

The pre-repair fixture run reported 12 failed assertions and seven errors
across 12 tests: `/tmp/caplab-attestation-red.log`. These include transient
model/effort/session/CLI changes, missing turn fields, settings-only capture,
conflicting settings, malformed JSON, non-object records, and invalid UTF-8.
The first repaired focused run passed all 12 tests:
`/tmp/caplab-attestation-green.log`. Further empty-capture, missing-session,
and missing-event-type boundaries were added before the full suite.

Full `make check` passed: 761 tests, four existing skips, 112.965 seconds.
Log: `/tmp/caplab-attestation-make-check.log`. `git diff --check` passed.
This record makes no independent review claim or roadmap acceptance claim.
The destination study remains unpreregistered. This reader repair does not
complete CAPLAB-79's broader capture, cost, redaction, and custody design
requirements.

## Engineering guidance

Pincite packet `pkt-4c4926a1aa94cd53`, content SHA-256
`4c4926a1aa94cd53f534827846b28ee3adc60462f9e1f35e101932f68cf13413`,
used typed source, contract, and fixture evidence. Applied concepts were
`implementation-risk-driven-tests` and
`universal-repository-contract-precedence`; structured citation checking
classified both as valid packet citations and wrote the local trace.
Doctrine version: `doctrine-f6bbb5196a3f8bf9`.

The material evidence is the recorded authority and preservation boundary,
the reader and its callers, the per-turn requirement, and executable
counterexamples. Generic packet obligations about database deduplication,
population discovery, top-N selection, operational paging, and serving parity
do not govern this local capture parser repair. No production incident or
live-provider verification is claimed. Broader capture completeness and
provider identity remain explicit limits, not obligations satisfied by these
fixtures. Temporary packet, evidence, and citation inputs are removed after
tracing; test logs remain for inspection.
