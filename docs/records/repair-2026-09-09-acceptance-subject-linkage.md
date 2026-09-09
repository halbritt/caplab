# Link acceptance observations through the gate subject

Baseline: `3024a6f`. Decision owner: primary agent under the continuing
CAPLAB improvement goal and [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Observation and decision

The previous gold-eligibility repair correctly removed unsupported gold labels,
but selected the artifact pin from `applicability.materialization`. Current
Striatum source puts the exact pin in `subject`; materialization has no version
and can contain a derived product-tree hash. The previous synthetic fixture
put a version in a field whose current schema prohibits it. Passing that
fixture did not establish compatibility with the producer.

Select the complete top-level subject pin for prospective acceptance linkage.
Keep the after-review-closure ledger ordering and gold-unavailability rule.
Do not fall back to materialization when a subject is absent or incomplete.
Count unlinked Principal acceptance gates in aggregate totals. Version the
reported linkage method so new reports identify the changed derivation.

No change would continue to drop schema-conforming observations. Falling back
to materialization would restore ambiguous attribution. This is a semantic
repair, not a refactor or an adjudication policy.

## Authorization before execution

Authorize changes to `scripts/review_criterion_ledger_pass.py`,
`tests/test_review_gold_eligibility.py`, and this record. Construct synthetic
ledger cases and validate their relevant payloads against the inspected
Striatum schema; retain private source snapshots, hashes, test logs and
verification scripts under `/tmp/caplab-acceptance-subject-*`. Copy only the
current producer source and its gate/pin schemas into that private verification
custody, with source commit, original path and content hash. This is source
contract verification, not CAPLAB admission of historical research evidence.

Run focused tests and required repository checks, then commit this exact local
scope. Preserve historical records/exports, `docs/designs/`, other worktrees,
services and Striatum files. No live ledger export or recomputation, object
store reads beyond constructed tests, model/native calls, credential access,
provider spend, tracker writes, outbound messages, push, ranking or independent
acceptance. Preserve failed test evidence; stop on a source-contract conflict
or an unexplained check failure. This execution authorization expires at commit.

Review-gate attribution is a separate unresolved question. This repair does
not validate that join or create new gold evidence.

## Execution and verification

Inspected Striatum commit `5ea87ca65c1bd25f228c0447110d991a3f0de8c8`:
`internal/driver/gate_context.go` constructs the subject with candidate sequence
and content hash, and separately constructs materialization without a sequence.
`schema/ledger-records/gate_result.schema.json` requires a subject pin for v2
and prohibits extra materialization fields. `schema/pin.schema.json` defines
the exact pin. The source manifest at
`/tmp/caplab-acceptance-subject-sources.json` retains original paths, copied
snapshot paths, source commits and SHA-256 values; the inspected files were
clean in that checkout. These are external interface evidence, not CAPLAB
product decisions.

After correcting the acceptance helper's field placement, the existing
identity/version regression failed against the old reader: expected gate 10
was missing. The repaired reader passes all seven prior gold-eligibility
tests. Two additional tests distinguish subject bytes from materialized tree
bytes and reject fallback to a fabricated materialization pin when subject is
absent. The combined criterion/canary selection passed 48 tests. Ruff's F
checks and `git diff --check` passed.

The complete synthetic product gate was validated against the copied v2 schema
using the installed JSON Schema validator with an explicit local registry.
The permissive v1 union branch was excluded from validation. A negative
control adding `version_seq` to materialization was rejected. Running the
same constructed ledger through the retained old reader and current reader
gave zero and one linked observations respectively; the review of tree bytes
remained unlinked. The script and result are
`/tmp/caplab-acceptance-subject-verify-schema.py` and
`/tmp/caplab-acceptance-subject-schema-check.json`.

This validates the complete fixture's payload schema and the reader join. It
does not execute the producer or resolve every synthetic reference against a
real graph. The other fixtures deliberately remain partial payloads for
missingness and malformed-input tests. The CAPLAB reader remains a tolerant
inspection projection, not a full Striatum v2 validator or authority engine.
It validates the subject sequence as a nonnegative integer when supplied;
subject shape errors are rejected before attribution. Missing/incomplete pins
remain unlinked. A complete pin can be inspected in a legacy payload without
promoting that record to current Striatum authority.

The new reported method is `gate-subject-pin-after-review-closure/2`.
Aggregate class counts now follow the subject identity and report unknown
when it is absent. Gold labels, review verdict selection, review-gate joining,
and other downstream candidate predicates are unchanged. Historical exports
and the previous repair record remain intact; no production prevalence or
reviewer capability conclusion follows from these synthetic checks.

## Doctrine and closeout

The release retrieval gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` and retriever
`retriever-ec995ecdd083b2c8`. Initial packet `pkt-efcbc3b55dd772de` was followed
by two typed-evidence passes. The final packet is `pkt-5d0a34f4f330e3dd`, hash
`5d0a34f4f330e3ddb928c7a6fb4de524aad22622c91185143da6cbed1fc5cf32`.

Applied `universal-repository-contract-precedence`,
`universal-evidence-before-intervention`, `agent-conduct-authority-bounded-action`,
`universal-preserve-behavior-by-default`,
`universal-separate-semantic-structural-change`, and
`data-dedup-key-identity-completeness`. The grouping key contains identity,
version sequence and content hash. Lists retain multiple gate observations
without deduplication or overwrite; the key does not establish event identity.
The schema disagreement justified correcting the old test fixture rather than
preserving its invented contract. The AI failure-mode review focused on this
plausible-but-wrong field interpretation and on avoiding fabricated success.

All 32 remaining retrieval obligations are nonmaterial to this repair:

| Concept | Count | Scope reason |
| --- | ---: | --- |
| `data-ingest-population-scoping` | 4 | No traversal, backfill or input-population change; tests name each constructed ledger. |
| `domain-authorization-embodied-in-action` | 4 | No authorization UI or gate discharge is implemented; the separate execution scope above governs this edit. |
| `implementation-async-ui-state-design` | 4 | No asynchronous UI changes. |
| `implementation-attention-budget-presentation` | 5 | No presentation budget or prioritization change. |
| `implementation-config-reference-validation` | 3 | No configuration identifier inventory changes; full graph reference resolution is explicitly unclaimed. |
| `implementation-rank-before-truncate` | 4 | No relevance ranking or truncation changes. |
| `operations-gate-authoritative-signal` | 4 | No serving/readiness gate implementation or production parity claim; payload linkage has separate source/schema evidence above. |
| `operations-symptom-cause-monitoring` | 3 | No paging or service monitoring changes. |
| `universal-no-change-option` | 1 | Expected future change is unnecessary to justify the reproduced current defect. |

Final `make check` exited zero: 1,309 tests in 164.177 seconds, four skips.
The private log is `/tmp/caplab-acceptance-subject-make-check.log`. No source or
test changes followed that run. These checks provide verification, not an
independent verdict, deployment acceptance, new gold outcome or roadmap closure.

Private verification manifest:
`/tmp/caplab-acceptance-subject-verification.json`, SHA-256
`6acc8f517224db79cf2e94cc5b4e9d9e3b18f9077fe20cfb4278d4e23834b59d`.
It records 29 artifacts, source snapshots checked against their named commits,
current runtime/test hashes, and six valid doctrine citation classifications.
Thirteen temporary packet/evidence/citation files were embedded byte-for-byte,
verified and removed by exact path. Source snapshots, synthetic ledger, failed
regression log, schema negative control, full-suite log and verification scripts
remain available. Historical evidence was neither recomputed nor rewritten.
