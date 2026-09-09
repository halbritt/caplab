# Keep downstream acceptance separate from review correctness

## Decision and authorization

At baseline `5da1868`, `scripts/review_criterion_ledger_pass.py` can emit
`gold-defect` or `gold-clear` when a Principal acceptance gate shares a reviewed
content hash and has a timestamp after review opening. It does not require
matching artifact identity/version, closure before the gate, or a ruling on
that review. The canary already says review-specific gold outcomes are
unavailable. The confirmed September 7 disposition and its signed-request draft
require independent review adjudication; an artifact acceptance is insufficient.

Under ADR 0026 and the continuing improvement request, authorize a prospective
repair of the criterion reader and CLI, focused tests, and this record. Do not
create gold labels until a separately selected reader and adjudication contract
can establish them. Preserve Principal acceptance events as explicitly
non-adjudicated observations, linked only by complete recorded artifact
identity, version sequence and content hash, after review closure in ledger
order. Incomplete pins do not match. Preserve event locators and expose these
observations in a separate CLI output so removing labels does not hide them.

Keep anchored population, selected reviewer verdicts, existing silver/bronze
candidate rules apart from their acceptance-event linkage, lifecycle/canary
semantics, source bytes and historical reports unchanged. Add explicit report
method and gold-unavailability fields. This changes prospective criterion
semantics to follow the governing disposition; it is not a characterization
refactor, a new adjudication policy, or a claim of zero real-world gold events.

Use newly constructed local ledger fixtures only, including both verdict
directions, shared hashes across identities/versions, missing pins, clock/order
disagreement, open and unknown-verdict runs, and the CLI's retained outputs.
Retain red/green/full logs and advisory/source provenance under
`/tmp/caplab-gold-eligibility-*`; run focused/full checks and commit this scope.
No production ledger export, evidence import/admission/relabeling/purge, model
call, spend, native launch, Striatum modification, tracker write, message,
human judgment or independent acceptance. Preserve unrelated files, worktrees
and services. Stop on unexplained regressions; do not loosen the adjudication
requirement to retain an old label. Authorization expires at the verified
local commit.

## Alternatives

Keeping hash-only gold labels conflicts with the confirmed disposition.
Requiring an exact pin alone would still confuse artifact acceptance with a
judgment about a review. Inventing a new external re-ruling schema would claim
authority over Striatum and still supply no independent outcomes. Select
explicit gold unavailability with retained exact-pin observations instead.
Historical exports remain as records of the method used when they were made;
this repair authorizes no recomputation or replacement of them.

The CLI currently opens its output files for replacement inside an existing
directory. Before changing that behavior, authorize requiring a fresh output
directory for prospective exports. This prevents the repaired method from
silently replacing historical files, including the old default destination.
An existing directory must fail before any output file is opened. Verify that
refusal with retained synthetic output bytes; no existing production export is
opened for writing or migrated.

## Execution and observed regressions

The first constructed ledger made the old reader assign `gold-defect` and
`gold-clear` from ordinary artifact acceptance gates, without an adjudication
of either review. The repaired reader emits neither gold stratum and explicitly
reports that gold outcomes are unavailable. This is a method limitation, not
an observation that production contains zero qualifying incidents.

The next regressions showed acceptance gates crossing artifact identities and
versions through shared hashes, and acceptance ordering following timestamps
after opening rather than ledger sequence after closure. The reader now keys
observations by `(identity, version_seq, content_hash)` and links only after
the selected review closure. Missing identity/version/hash prevents a match;
version zero remains valid, while booleans, text and negative version references
are refused rather than coerced. No content-hash authenticity is inferred from
matching the recorded strings.

`post_close_acceptance_observations` remains available for unknown-verdict
reviews; open reviews have no post-closure observation. Unsupported acceptance
outcomes remain recorded observations without a correctness label. Existing
Principal acceptance totals still count recorded gates, including those whose
incomplete pins cannot be linked. Multiple reviews of one pin may reference
the same gate; those links are not independent adjudication incidents.

The prospective CLI writes `caplab-review-criterion-candidates/2` summaries
with the source snapshot and explicit method/unavailability fields. It emits
only silver/bronze inspection candidates in `review-criterion-cases.jsonl` and
keeps downstream gates separately in `review-acceptance-observations.jsonl`.
Each observation row carries the ledger digest, review-run sequence, exact
subject pin and gate sequence. The existing 600-character detail prefix remains
a bounded display field; the original ledger is the source for complete text.
The new file does not assert that the gate overruled the linked review.

The CLI now refuses an existing output directory, including an existing default
destination, before opening any output file. A regression observed the old
writer replace an existing synthetic report; the repaired writer preserves its
exact bytes and creates no additional file there. Callers must choose a fresh
`--out` path. A failed write into a new root can leave partial new output; this
change does not introduce transactional multi-file publication or retry.

Seven new reader/CLI tests passed with the existing canary and admission-gate
tests: 62 tests in 1.309 seconds. Sequential red/green logs under
`/tmp/caplab-gold-eligibility-*` preserve the unsupported gold, pin collision,
closure-order, observation-export and overwrite regressions. No production
ledger or historical report was recomputed, and no model/native execution,
spend, external-system change, reviewer ranking or independent acceptance
occurred. The canonical study and roadmap remain incomplete.

## Advisory and review

The retrieval gate verified fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, and release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. The question nominated no precise
doctrine concepts; the packet supplied baseline/routed guidance. Repository
domain rules, the confirmed disposition and the reproduced failures establish
the methodological defect. Doctrine does not define review truth.

Initial packet `pkt-ad8fbb410c9c1a4d` was followed by two typed evidence passes.
Final packet `pkt-f1253c3899af2b9b`, retriever `retriever-ec995ecdd083b2c8`, has
content hash `f1253c3899af2b9b595ab9202114f3674c55a56e149b813cdbbad9e88690e916`.
Evidence retains authority, contracts, current source and executed tests.

Nine unmet obligations remain nonmaterial: recurring-change evidence (the
reproduced semantic defect already warrants repair); CI/build matrix,
formatter/static configuration, Python/dependency matrix,
formatter/linter/type-checker configuration and complete toolchain inspection
(no platform or toolchain change/qualification); annotation maintenance cost
and configured checker/Python matrix (no annotation migration); representative
non-ASCII data (no decoding or normalization change, and no new text-coverage
claim). Local interpreter/source checks and exercised fixtures bound the result.

The applied concepts are repository-contract precedence, evidence before
intervention, authority-bounded action, runtime/static validation boundaries,
placement by ownership and preservation by default. The existing reader owns
the criterion policy and linkage, so the repair remains there. The review
checked missing-pin joins, temporal ordering, unknown/open denominators,
unsupported gold promotion, preservation of source locators and historical
outputs, and the distinction between link counts and independent incidents.

After the first full suite passed, the direct gold regression was strengthened
to use one unambiguous acceptance gate per reviewed version. The 62 focused
checks still passed. A separate in-memory promotion control restores only the
weak gold-classification branches while preserving the repaired pin/order
rules; the strengthened regression fails as expected. Repository source remains
unchanged. This shows that the direct test detects unsupported gold promotion
even without conflicting gates or a hash collision. The earlier fixture source,
both focused runs and the intentional control failure remain retained.

## Final verification and custody

The final `make check` passed: 1,307 tests in 206.998 seconds, with four skips.
The final focused run passed 62 tests in 1.513 seconds. The earlier full run
also passed, before the direct fixture was strengthened; its separate log and
test-source snapshot remain retained. Runtime source was unchanged between
those runs. Ruff and diff checks passed for the final source and test files.

The private verification manifest is
`/tmp/caplab-gold-eligibility-verification.json`, SHA-256
`7f97cc7308fd7d727e8d358e7a09a94a8171200eefb19596b6165b02aab44671`.
It retains 33 artifact entries, final source hashes, test results and advisory
identities. Thirteen advisory scratch files were embedded byte-for-byte and
verified before removing those exact temporary paths. The original scoped
authorization, red/green/full/control logs and verification script remain
private. Governing disposition/request records and the canary source matched
their recorded hashes throughout; no historical report was replaced.

Commit only the criterion reader, its seven tests and this record. The repair
prevents unsupported promotion into gold evidence; it supplies no independent
gold outcomes, eligibility for replay, reviewer ranking or roadmap completion.
