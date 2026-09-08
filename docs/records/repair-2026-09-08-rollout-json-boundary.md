# Reject ambiguous rollout JSON before rater attestation

## Decision and authorization

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
authorizes a prospective repair to the artifact-rater rollout reader. Parse
each LF-delimited native record with the existing strict native JSON parser,
reject duplicate keys and non-JSON constants, and require a final record
delimiter. Blank records are malformed. Preserve valid Unicode within JSON
strings and hash the original bytes without normalization.

Authorized effects are source changes, newly authored local fixtures and
tests, and this record. Do not read, repair, rewrite, evaluate, recover,
admit, or rescore historical captures. No model calls, spend, ranking,
placement, tracker updates, or messages. Preserve the September 7 instrument
disposition, frozen numerical calibration gates, configured subjects, source
custody, and unrelated untracked designs. Stop if an excluded effect is
required. Revert this commit to reverse prospective behavior and remove only
task-owned temporary fixtures and advisory inputs.

## Observation and preservation boundary

At parent 6305896, read_rollout_attestation uses json.loads and splitlines,
while native event parsing rejects duplicate keys and non-JSON constants.
Duplicate model, effort, payload, or session fields can therefore be silently
resolved by retaining the last value before attestation. A missing final LF
is accepted, and valid Unicode line separators inside JSON strings can be
mistaken for record boundaries. These are parsing inconsistencies, not
evidence that an archived capture was manipulated.

The selected repair reuses parse_native_json at this existing ingress.
Attestation still requires consistent session/CLI identity and complete
model/effort turn contexts. It does not authenticate the provider, establish
whole-session completeness, verify blinding, change calibration thresholds,
or turn agreement into accuracy. A final LF establishes a complete record
boundary, not proof that every record was captured.

Retain invalid bytes in failed attempt custody as before, without publishing
a judgment. Read-only verification of a published judgment must reject
ambiguous supporting rollout bytes even if its hashes were recomputed.
No implementation is replaced by a generic capture framework.

## Verification plan

Use raw JSON fixtures with duplicate identity and nested keys, non-JSON
constants, blank or unterminated records, valid CRLF, and Unicode line
separators inside text. Verify direct attestation, failed-attempt retention,
and publication/evaluation refusal at the existing consumers. Then run the
repository checks. This is a semantic integrity repair, not refactoring or
independent instrument acceptance.


## Execution and verification

The reader now decodes UTF-8, requires a terminal LF, splits only at LF, and
passes every record through parse_native_json. Its existing object, event-type,
session, CLI-version, turn-context, and tuple-consistency checks remain.
CRLF is accepted as JSON whitespace at the end of each record; the source
hash includes the original CRLF bytes. Unicode line and paragraph separators
inside strings stay inside those strings.

Before repair, the new boundary tests plus calibration-reader tests ran 21
tests and produced 16 assertion failures and two errors; see
`/tmp/caplab-rollout-json-red.log`. Ambiguous captures could be attested and
used for calibration, while the Unicode fixtures failed to parse.

The focused run passed 70 tests in 1.854 seconds; see
`/tmp/caplab-rollout-json-focused.log`. Six new regressions cover duplicate
identity and nested keys, non-JSON constants, record boundaries, valid Unicode
and CRLF, failed-attempt retention without publication, and calibration refusal
after supporting hashes are recomputed. The last test also verifies that the
read does not change evidence or write a calibration result. It establishes
semantic validation beyond matching hashes without claiming authenticated
custody.

One old handmade valid-rollout fixture omitted its final record delimiter.
It now includes LF under the explicitly selected prospective framing contract.
The separate regression verifies refusal when LF is absent. No historical
fixture, native capture, or frozen numerical criterion was modified.

Final `make check` passed 859 tests with 4 skips in 155.242 seconds;
see `/tmp/caplab-rollout-json-make-check.log`. No source or test edits
followed that run. `git diff --check` passed. No historical capture was
read or changed, and no model calls or tracker updates occurred.

This repair changes eligibility at the shared reader, including prospective
reads of existing publications, but it does not rewrite or revoke a retained
publication as a side effect. No historical compatibility rate was measured.
Provider identity, capture completeness, blinding, full Binding attestation,
and independent instrument acceptance remain outside this verification.


## Advisory receipt

Packet `pkt-00203e06873e4aaf`, content SHA-256
`00203e06873e4aaf467abae8a093d385edbfd0b0f2e9df7e35cc201e9c52cb3f`, uses release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. The release retrieval gate was
rechecked and passed. Applied concepts are
`implementation-placement-by-ownership`, `operations-gate-authoritative-signal`,
`universal-evidence-before-intervention`, and
`agent-conduct-authority-bounded-action`. The existing rollout ingress owns
the parse contract; publication and evaluation must inspect that evidence
instead of accepting matching hashes as sufficient. Citation consumption is
recorded locally.

Remaining advisory obligations are nonmaterial to the bounded parser repair:

| Concept | Missing requirements | Scope reason |
| --- | --- | --- |
| data-dedup-key-identity-completeness | an explicit enumeration of the record's identity dimensions matched against the key's columns; logical-identity definition of the affected record; the conflict-handling semantics at that key - abort update or silent drop | No database key, uniqueness policy, or duplicate-record disposition is introduced. Duplicate JSON keys are rejected by the existing native parser. |
| data-ingest-population-scoping | a dry-run enumeration with counts compared against expectation; the discovery pattern shown to match the specification's depth and class constraints; the input population specification; the specified input population stated precisely | No archive discovery, bulk ingest, or backfill ran; callers still name one retained rollout file. |
| implementation-config-reference-validation | a load-time or gate check resolving every reference against them; a named-identifier failure on mismatch; the consumer's defined identifier and enum sets | No configuration identifiers or enums change. Existing session and tuple checks remain; this repair changes decoding and record framing. |
| implementation-placement-by-ownership | recurring change evidence when available | A reproduced defect at one existing ingress justifies the repair without a history of recurring coordinated changes. |
| implementation-rank-before-truncate | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No search, relevance ordering, top-N selection, or truncation is performed. |
| operations-external-capability-verification | access to the real device or endpoint; an end-to-end verification artifact against the actual device or endpoint; or an explicit record that verification is provisional; the real system's own statement of its capability - device configuration output wire capture or endpoint self-description | No live compatibility or readiness claim is made. The native process is replaced only inside new local tests; no provider or model was invoked. |
| operations-gate-authoritative-signal | eval-versus-serving configuration parity | Serving parity is unverified and unnecessary for the demonstrated parsing counterexamples; the gate reads the preserved rollout bytes. |
| operations-symptom-cause-monitoring | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No service monitoring, alert, or page changes. |
| task:defect-repair | evidence-incidents | The source defect is established by new failing and passing fixtures, not a claim of an observed production incident. |
