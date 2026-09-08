# Repeated runtime diagnostics behind missing review outputs

Date: 2026-09-08. Report-only finding under the continued CAPLAB improvement
request and confirmed review-instrument disposition. No reviewer ranking,
model call, credential change, placement change, or evidence admission.

## Question and source

What do retained diagnostics actually say about the 2,880 unknown-verdict
reviews in the production canary? The prior lifecycle report identified
missing output admissions and scheduling outcomes; those labels alone did
not explain why the expected review body was absent.

Source report: `/tmp/caplab-lifecycle-production/report.json`, SHA-256
`6632a86fbc8943deedd822255f25955c07131c19d9d824f22184a4725c1387bd`.
Its retained ledger export is
`/tmp/caplab-production-20260908-9e8Est/ledger.jsonl`, SHA-256
`ba8754dd853fc51442904fb2b7502fa253b164cff31c8205d3f4e4c37d18d3bf`,
through sequence 406970 at `2026-09-08T09:53:36.328Z`. This is a bounded
inspection of an older snapshot, not a current authentication or quota check.

The inspection selected the first eight unique objects labeled `transcript-*`
by distinct linked unknown-verdict run count, descending, with hash order as
the tie-breaker. Every selected object was read locally through the existing
object-store reader and its decoded bytes were independently SHA-256 checked.
No prompt objects were inspected. The selection prioritizes repeated exact
messages; it is not a representative sample of failures.

## Observations

| Diagnostic reported by the retained transcript | Hash prefix | Distinct linked runs | Run-opening dates (UTC, 2026) |
|---|---|---:|---|
| OAuth session expired and could not be refreshed | `8cc9b1270cb5` | 826 | August 11–12 |
| Usage credits exhausted for Fable 5 | `ad39127499b0` | 175 | August 10–11 |
| Timeout waiting for response | `60aa3a5934a4` | 100 | July 28–August 8 |
| Weekly usage limit reached | `fc59ae506253` | 73 | August 21–22 |
| Session usage limit reached | `8ce7a423a837` | 37 | August 16 |
| Agent execution terminated due to error | `e8ee408e7e64` | 22 | August 4 |
| Fable 5 usage limit reached | `1799631b4a8e` | 18 | August 16 |
| Unrecognized `glm-5.3[1m]` model during session-title generation | `d8254390d48f` | 16 | August 28–29 |

The source report contains 1,373 unique transcript-object references linked
to 1,985 unknown-verdict runs. These eight objects cover 1,264 distinct runs.
Their row counts sum to 1,267 because some runs reference more than one
selected diagnostic. Repeated attempts also reuse the same object. These
counts are neither independent failure incidents nor reviewer-error counts.

Full hashes, all linked run and lifecycle-event sequences, labels, decoded
diagnostic text, and first/last run-opening times are retained in
`/tmp/caplab-review-diagnostic-inspection.json`, SHA-256
`13c938cf50f752535f51793534007fd46318d7f5eb3faadea5a3f6b78b8ad147`.
The reference index is `/tmp/caplab-review-diagnostic-index.json`. Hash prefixes above are
display abbreviations; the inspection uses complete content hashes.

## Inference and next action

The repeated authentication and usage messages make runtime access and
availability concrete investigation targets. They provide stronger evidence
than the generic `schema_invalid` admission code paired with an absent output.
They do not establish a reviewer's ability to find defects. The session-title
message also cannot establish that the main review model was unrecognized.
A diagnostic is a recorded message; this inspection does not independently
verify every claimed cause or identify whether the account, provider,
wrapper, host, or scheduling policy was responsible.

The concentration of 826 matching authentication messages within August
11–12 further argues against treating them as independent capability
observations. It does not prove that all came from one independently
identified outage, nor that the authentication problem persists today.

Before spending on a future named-binding admission gate, inspect the current
native-client authentication and availability state and the capture path for
that binding. Use these exact run and diagnostic references to distinguish
historical incidents from current faults. Do not infer that old credentials
are still expired, silently switch the subject to another model or harness,
or interpret a usage limit as a capability failure. Any live gate still
requires the Principal's named-binding authorization, and production reviewer
ranking still requires independently grounded outcome evidence.

No runtime change is selected by this finding. Automatically classifying all
diagnostics by regex would add unvalidated semantics, while repeatedly
launching reviewers would spend without resolving the observation gap.
Leaving the missingness as an undifferentiated count would hide the evidence
already available. The next action is source-grounded runtime investigation
within its authority, not another accuracy estimate from this corpus.

## Verification and limits

The inspection verified eight complete hashes and retained every reference
used for their run counts. Set union verified the distinct-run coverage and
exposed the overlapping memberships. The original report and object-store
contents were not changed. No historical record was registered, superseded,
or purged. The user-owned `docs/designs/` draft remains untouched.

This turn changes documentation only, so no code test suite was rerun. The
previous implementation verification remains 756 tests with four existing
skips at commit `e64f374`; it does not validate this finding's causal claims.
The checks here verify source hashes, locators, and counting. Current runtime
health, full diagnostic coverage, independent incidents, native Binding
identity, and reviewer correctness remain unverified. The wider goal remains
open.

## Engineering guidance

Repository requirements govern this finding. Retrieved guidance supplied
`universal-evidence-before-intervention`,
`agent-conduct-authority-bounded-action`, and `universal-no-change-option`.
Packet `pkt-c1729521e0bbb0f6` has SHA-256
`c1729521e0bbb0f6f625b088b1a316d07a8505688dab979a357608c1babd9813`,
from release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. The authority ceiling is the
report-only investigation performed here; it grants no runtime intervention.
Source locators are the retained report, reference index, inspection record,
and hash-verifying object reader named above.

Material population and presentation obligations are covered by the complete
transcript-reference enumeration, sorting before selecting eight objects,
and retained run/event references. The selection key is distinct-run count,
not inferred severity, reviewer value, or text relevance. Hash checks,
reference counting, and set union verify the bounded observations. The reader
receives eight diagnostic groups with dates and coverage, while the full
index and source report remain unchanged.

The packet's remaining traversal-depth, asynchronous UI, placement/refactoring,
paging, code-test, and build-matrix obligations are nonmaterial to this
documentation-only finding. No runtime behavior, dependency, gate, or service
is changed. Existing code tests do not establish this finding's causal
interpretation. Production incident independence and present operational cost
or future frequency remain unknown; the retained counts establish neither.

Current endpoint access, native serving parity, complete gate inventories,
and independently confirmed root cause remain unverified and material to
any proposed operational repair. This finding therefore selects none. The
unverified current-state obligations limit the recommendation to inspecting
the affected native path before a separately authorized live measurement.
They cannot justify renewing credentials, switching models, claiming recovery,
or evaluating reviewer capability from these historical failures.
