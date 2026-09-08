# Ground later-version observations in artifact admissions

Date: 2026-09-08. Baseline: `55e7f20`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Use newly authored temporary ledgers and patched object-store reads to compare
bare version references with actual `artifact_admitted` events. Repair
`scripts/review_criterion_ledger_pass.py` and `scripts/review_canary.py` so
later-version reporting and the criterion's refused-then-revised exclusion
require an admission of the same identity after review closure and after the
reviewed version. Retain admission metadata and locators in the canary; expose
the changed derivation in report metadata/version. Preserve other event joins,
verdict rules, source bytes and historical reports.

Update `tests/test_review_canary.py`, the production-review guide, and this
record. Correct existing synthetic revision fixtures to contain real admission
events; demonstrate the old reference-only behavior separately. Verify focused
regressions, a before/after valid-admission fixture, and `make check`. Producer
source reads are supporting evidence only. No live ledger export, body-store
inspection, historical result regeneration, model spend, evidence admission,
qualification, ranking, placement, tracker change or external message is
authorized. Preserve `docs/designs/` and unrelated state. Retain verification
receipts; remove only named task doctrine scratch after recording its receipt.
Authorization expires at commit.

## Observation and selected response

The current version inventory consists of review subject pins and head-movement
`to_version` fields. It does not require the referenced admission to exist or
match the identity. It also misses an admitted version that has not yet become
a head or received another review. The canary's numeric comparison with closure
does not repair that evidence gap.

Select actual admission events as the version source, matching Striatum's
`internal/derived/fold.go` (`VersionSeq: record.Seq` in `artifact_admitted`).
A later admission is an observation that a version was recorded; it does not
prove adoption, changed content, a correction caused by refusal, or correctness.
Keep these limits visible in the report. Reference-only mentions must not
substitute for the event, and newly admitted versions need no subsequent
head movement or review to be observable.


## Execution and verification

The shared criterion reader now indexes actual admission events. Both consumers
use the same sequence-based post-closure predicate; the canary also retains
admission sequence, timestamp, identity, and recorded content hash. Known
optional numeric references remain validated, but validation alone no longer
substitutes for an admission. The criterion summary and canary expose
`revision_evidence: artifact-admission-after-review-closure/1`.
New canary output is `caplab-review-canary/6`; versions 1–6 remain eligible
baseline formats subject to the existing decoding and prefix checks.

This is a semantic repair with no separate structural refactor. No change would
retain both false reference-only links and missed admissions. Requiring both a
head movement and an admission would still hide recorded versions; reading
artifact bodies would add access and interpretation beyond this event claim.
The shared reader owns the join so the canary and criterion exclusion cannot
silently use different version inventories. Other event joins, verdict
selection, strict decoding, numeric validation, and the legacy case-file field
boundary are preserved. Historical output can differ when regenerated under
this rule; no historical report was regenerated here.

`/tmp/caplab-review-revision-before.json` records the synthetic reproduction:
a head reference to 999 produced a later-version count of one, while an actual
admission without a head or later review produced zero. Store-object reads
were patched and asserted unused. Four new tests cover those cases, admissions
before closure, unknown/open reviews, missing reviewed versions, exact Unicode
identity, reversed timestamps, duplicate content across distinct admissions,
source-event retention, and one count per refused run. Two older synthetic
fixtures now contain actual admission events instead of only head references.
The red run had three failures among 39 tests; focused verification then passed
39 tests in 0.628 seconds. Receipts:
`/tmp/caplab-review-revision-red.log` and
`/tmp/caplab-review-revision-focused.log`.

The valid-admission comparison executes baseline scripts from commit `55e7f20`
and current scripts against the same synthetic four-run fixture, with a
matching original subject hash and version. Summary, strata, runs, and canary
output are byte-identical after excluding only the temporary source path,
report version, and newly added revision-rule/observation fields. Store reads
were patched and asserted unused. Retained probe and results:
`/tmp/caplab-review-revision-valid-probe.py`,
`/tmp/caplab-review-revision-valid-before.json`, and
`/tmp/caplab-review-revision-valid-after.json`. This is synthetic parity,
not live-data verification.

`make check` passed 913 tests with four skips in 132.736 seconds:
`/tmp/caplab-review-revision-make-check.log`. No production or test source
changed after that check began. Both changed scripts pass AST parsing and
direct-import-use inspection. The local toolchain is Python 3.12.3; the
Makefile invokes unittest discovery with `PYTHONPATH=src`.

## Supporting source and limits

Striatum source `internal/derived/fold.go` was clean at observed commit
`a6b1ae71d95cdf99200c10d8c6ce855d9da70a69`, SHA-256
`982c29046c35124664327f1559bda598b0536bfd94fa1a07110c14082952a80e`.
Its artifact-admission branch creates a version with `VersionSeq: record.Seq`;
head movement updates a pointer. This supports the event distinction, not
complete producer-schema conformance or authority over Striatum.

No live ledger or artifact body was read for this repair. No claim is made
about historical incidence, accepted revisions, changed content, causal repair,
reviewer accuracy, qualification, or independent acceptance. The broader
measurement goal remains open. Reopen this reader policy if the producer's
version identity changes or a demonstrated admission case violates this join.

## Doctrine receipt

The release retrieval-state gate passed. Release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`.

Final packet `pkt-f6502b619becb813`, SHA-256
`f6502b619becb8135bb4d599633d66e3429e045ec4c26b5faa5d5b880b155bc9`.
One evidence-gathering pass supplied five typed records: authority, repository
contracts, source structure, synthetic probes/parity, and tests.

Applied `universal-evidence-before-intervention` to require reproduced false
and missing links; `universal-repository-contract-precedence` to preserve the
report-only contract; `implementation-placement-by-ownership` to place the
shared join in its existing reader; and
`agent-conduct-authority-bounded-action` to preserve historical evidence and
keep producer source separate from CAPLAB authority. No new abstraction or
adjacent refactor was selected.

All remaining obligations are nonmaterial to this event-join repair:

| Group | Exact unmet requirements | Classification and reason |
|---|---|---|
| `implementation-placement-by-ownership` | recurring change evidence when available | Nonmaterial: the demonstrated event-join defect warrants correction without a recurring-change or architectural-cost claim. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI, formatter, or static-checker conformance is claimed; verification uses the inspected local Makefile and interpreter. |
| `python-mutable-ownership` | concurrency; lifetime and size | Nonmaterial: the index and added metadata remain local to one synchronous report read; no concurrency, memory bound, or retention-performance claim is made. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no formatter, linter, or type-checker policy is changed or claimed verified. |
| `python-runtime-static-boundary` | annotation maintenance cost; checker and trust-boundary evidence; configured checker and Python version | Nonmaterial: no annotations or checker configuration change; executable event predicates and tests establish the bounded runtime behavior. |
| `python-structured-cleanup` | acquisition and release paths; exception and cancellation behavior; nesting order; owner and lifetime; resource ownership and failure policy | Nonmaterial: the production repair adds no file, process, lock, transaction, or other acquired resource and changes no acquisition or release path. |
| `universal-no-change-option` | expected future change from accepted plans | Nonmaterial: repair is justified by reproduced current false and missing links, without forecasting roadmap demand. |


## Completion checks

Four doctrine citations classified as `valid-packet-citation`; the packet
identity, hash, applied concepts and obligation dispositions above retain the
receipt before removal of the eleven named task doctrine scratch files.
Synthetic probes, comparison artifacts and test logs remain in `/tmp`.
Final file/link, diff, source-hash, and parity checks are recorded in
`/tmp/caplab-review-revision-verification.json`.

No tracker field or external message was changed. Commit closes this bounded
repair, not the broader measurement goal; technical verification is not an
independent acceptance verdict.
