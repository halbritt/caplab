# Native review scores require captured model evidence

## Decision and authorization

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
authorizes a prospective repair to native review capture and normalization,
implementing the identity separation selected in the CAPLAB-78 inspection
record. Authorized effects are source, regression tests with newly authored
local fixtures, and this record. No historical normalization, evidence
copying, admission, rewriting, rescoring, model calls, spend, ranking,
placement, tracker changes, or messages are authorized. The September 7
instrument disposition remains in force. Stop if these effects are required.

Keep the configured subject seal and original execution status. Add a
raw-byte-linked assessment of native-reported model evidence. An explicit
fallback, any mismatching initialization or response model, or missing
required model evidence prevents a configured-subject score, including refusal
credit. Identity exclusions retain their assigned slots and do not authorize
replacement attempts. Additional usage-model names alone do not establish
which model authored the principal response.

The current Claude stream can establish agreement among its initialization
and assistant model fields. Require a structurally bounded stream, one initialization at the start, one successful terminal result, and a model on every captured
assistant message. Codex stdout lacks the required model evidence; it stays
unverified until a separate rollout capture integration is implemented and
authorized. Do not infer its model from invocation arguments or Claude-shaped
fields. Matching native-reported model fields do not verify effort, full
Binding identity, provider authentication, or capture completeness.

New captures and results use version 2. Existing immutable version 1 files
are unchanged. The campaign summary must reject non-null scores without a
passing model assessment and expose identity exclusion counts. Existing
review schema, task preservation, required reads, numerical grading, trial
accounting, and launch authority remain unchanged.

## Observation, alternatives, and verification plan

At parent bff1693, build_native_review_capture derives subject_seal solely
from configured fields and can award 1.0 to a matching review even when the
native stream names another model. The summary trusts any non-null score.
The CAPLAB-78 annotation already documents an explicit historical fallback;
this repair uses only new fixtures to reproduce the attribution defect.

Leaving the implementation unchanged preserves the known attribution gap.
Renaming the planned subject to the observed model would alter the assignment.
Treating identity failure as ordinary reviewer error or retryable
infrastructure would respectively misstate capability or alter exposure.
The selected change withholds attribution separately at the existing capture
owner and preserves the denominator. It is a semantic repair, not refactoring.

Verify missing and mismatched model evidence, transient fallback, auxiliary
usage, malformed streams, refusals, supported matching streams, unchanged
configured seals, and summary propagation with local fixtures, then run the
repository checks. Revert this commit to reverse prospective behavior.
Independent instrument acceptance and future campaign readiness remain open.


## Execution and limits

Captures now use `caplab.review-dissent.native-capture/v2` and carry
`model_identity`, including the exact stdout SHA-256 and one-based source
lines for initialization, response-model, fallback, and usage observations.
`native-model-match` is a necessary model-evidence condition. The alternative
statuses are `model-mismatch` and `model-unverified`; their mechanical fields
remain unavailable, including refusal credit. Infrastructure outcome retains
its existing precedence; other excluded outcomes are `identity-unavailable`.
Neither the configured subject seal nor execution status is rewritten.

The result and capture-manifest schemas advance to version 2. Rows expose
identity status, reason, and stdout hash; aggregate and grouped counts retain
all assigned slots. A non-null score without `native-model-match` raises a
contract error. This aggregation guard consumes capture-derived rows; it does
not independently authenticate a manually constructed row. The normalizer
also checks the very stdout bytes it passes to capture against the sealed
observation hash, so an intervening file change cannot silently change the
model assessment.

Malformed or ambiguous JSON, including duplicate keys and non-JSON numeric
constants, raises a capture contract error before grading. UTF-8 decoding is
strict and record separation uses LF, preserving Unicode characters that
Python's broader splitlines would misinterpret as record boundaries. Empty
stdout is unverified; an unterminated or structurally incomplete Claude
stream cannot pass. Explicit fallback remains disqualifying even when later
model fields return to the configured name. Usage-model names alone supply
no positive or negative primary-model attestation.

The normalizer no longer copies the historical severity-enum explanation into
every prospective result. `failure_explanation` is unavailable and human
qualitative disposition is explicitly absent; the historical version 1
explanation is preserved in its original artifact. This removes an unsupported
inference from the new result path without replacing it with a causal claim.

Only local fixtures were normalized. No historical data was read or changed
by the new implementation and no native model ran. CAPLAB-79 remains open:
Codex rollout integration, effort and harness-version evidence, full capture
configuration, and live-attempt stopping on identity failure still need
separate work. These tests establish mechanical exclusion under the stated
stream contract, not capture completeness or independent provider identity.


## Verification

Before implementation, the focused file ran 11 tests and reported 22 failing
subtests and two missing-field errors; see
`/tmp/caplab-native-model-red.log`. The prior implementation awarded scores
without model evidence and accepted ambiguous native JSON.

After implementation, all 34 review-dissent tests passed in 7.108 seconds;
see `/tmp/caplab-native-model-focused.log`. Eight new tests cover mismatch
and transient fallback, incomplete or missing model evidence, auxiliary usage,
Codex non-attestation, refusal and infrastructure handling, ambiguous JSON,
summary exclusion, and end-to-end local fixture normalization. The existing
positive capture fixture now supplies explicit matching native model fields
and still earns its frozen 1.0 oracle score. This fixture revision implements
the selected eligibility requirement; it does not reinterpret prior evidence.

The end-to-end test writes 16 new local attempt fixtures, uses the real sealed
attempt reader and normalizer, verifies all source bytes stay unchanged,
checks capture-to-row hashes and identity counts, and confirms that existing
normalization cannot be overwritten. It also injects a stdout change after
initial validation and confirms rejection before capture publication.

Final `make check` passed 841 tests with 4 skips in 133.827 seconds;
see `/tmp/caplab-native-model-make-check.log`. No source or test changes
followed this run. `git diff --check` passed. These checks verify the stated
mechanical contract; they do not supply independent instrument acceptance.


## Advisory doctrine receipt

The evidence-backed packet is `pkt-db31041e3272861d`, content SHA-256
`db31041e3272861d7941e4bf86ec2904780e65422c87670873c9f11a98d2705a`. The retrieval gate verified release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts are
`python-text-bytes-boundary`, `universal-evidence-before-intervention`,
`operations-gate-authoritative-signal`,
`universal-repository-contract-precedence`, and
`agent-conduct-authority-bounded-action`. The raw stream supplies the observed
model fields; configuration supplies the planned assignment. Repository
contracts and delegated authority govern this repair. Citation consumption
is recorded locally.

Remaining advisory obligations are nonmaterial to this bounded fixture-verified
normalization repair for the reasons below. No live-readiness conclusion is
made.

| Concept | Remaining requirements | Scope reason |
| --- | --- | --- |
| data-dedup-key-identity-completeness | an explicit enumeration of the record's identity dimensions matched against the key's columns; logical-identity definition of the affected record; the conflict-handling semantics at that key - abort update or silent drop | No uniqueness key or conflict-handling policy changes; configured seals and exclusive file writes remain. |
| data-ingest-population-scoping | a dry-run enumeration with counts compared against expectation; the discovery pattern shown to match the specification's depth and class constraints; the input population specification; the specified input population stated precisely | No archive traversal or backfill is executed. The new fixture enumerates the existing 16-slot order; production population validation is unchanged. |
| implementation-config-reference-validation | a load-time or gate check resolving every reference against them; a named-identifier failure on mismatch; the consumer's defined identifier and enum sets | No new user-configurable identifier is introduced. Existing instrument validation supplies model and harness identifiers; new assessment statuses are derived internally and tested through the consumer. |
| implementation-rank-before-truncate | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No ranking, search, truncation, or top-N selection occurs. |
| operations-external-capability-verification | access to the real device or endpoint; an end-to-end verification artifact against the actual device or endpoint; or an explicit record that verification is provisional; the real system's own statement of its capability - device configuration output wire capture or endpoint self-description | Live model execution is outside authority. Verification is limited to newly authored native-format fixtures; provider identity and live readiness are unverified. |
| operations-gate-authoritative-signal | eval-versus-serving configuration parity | No evaluation-versus-serving parity claim is made. The source repair checks retained native fields and explicitly leaves full Binding attestation open. |
| operations-symptom-cause-monitoring | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No service, page, or monitoring contract changes. |
| task:defect-repair | evidence-incidents | The prior CAPLAB-78 record supplies the incident observation. This turn reproduces the source defect using new fixtures and does not reopen that archive inspection. |
