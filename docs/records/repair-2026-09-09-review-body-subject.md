# Attribute body verdicts to the exact reviewed subject

Baseline `44bb7bc`. Decision mechanism: primary agent under the continuing
CAPLAB improvement goal and [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Observations and decision

The body reader verifies object bytes but assigns a body verdict solely by
`produced_by_run`. The source admission funnel verifies the body's hash;
Striatum's fold uses the first `edges.evidences` subject, and strict review
bodies contain exactly one `subject_pins` entry matching the sealed subject.
Legacy review bodies need not contain that field. Availability of valid JSON
does not establish that the body reviews this run's artifact.

Require an admission after its producing review run, a nonempty artifact
identity, agreement between admitted content hash and verified body hash, and
an exact admitted subject matching the run's subject. If the body supplies
`subject_pins`, require exactly one matching complete pin; absent body pins
may use the admitted subject without claiming strict contract conformance.
Missing, malformed or contradictory supplied pins must not use that fallback.
Retain raw body verdicts and subject evidence, with explicit attribution
status. The latest unlinked admission cannot inherit an earlier body verdict.
An independently linked gate remains available as the labeled fallback.

Body and admitted claim verdicts may disagree; preserve the verified body's
verdict and existing same-admission gate discrepancy when subject/hash linkage
is valid. This does not adjudicate either claim. The change is a semantic
attribution repair, not full Striatum admission replay or qualification.

## Authorization before execution

Authorize changes to the criterion reader, canary, their existing tests,
`tests/test_review_body_subject.py`, and this record. Use constructed ledgers
and real private SOB1 objects. Update existing fixtures to supply the admitted
subject/hash fields required by the inspected producer. Keep their parser,
missingness, gate-disagreement and source-preservation assertions meaningful.
Version the prospective method/report and preserve all older baseline versions.

Retain source snapshots, failures, controls and verification under
`/tmp/caplab-review-body-subject-*`. Copy the current Striatum
`internal/store/admission.go`, `internal/store/admission_v2.go`,
`internal/reviewledger/contract.go`, `internal/driver/fold.go` and
`schema/review-ledger.schema.json`, with original paths, source commit and
SHA-256. These are external interface evidence only. Run focused/full checks
and commit this local scope. No live ledger or object-store reads, production
recomputation, historical research admission/rewrite, model/native calls,
credentials, spend, tracker writes, messages, push or Striatum mutations.
Preserve unrelated files, `docs/designs/`, worktrees and services. Stop for an
unexplained failure or contradictory contract, retaining failure custody.
Authorization expires at commit. No reviewer ranking or independent verdict
is conferred by this repair.

Before gate/body integration changes, extend this scope to reject gate fallback
when its exact referenced admission has a parsed body with conflicting
attribution. A missing/unparseable body may still use independently linked
gate metadata. This prevents fallback from bypassing a newly detected body
subject/hash conflict while preserving the existing missing-body behavior.

## Execution and verification

The source snapshots name Striatum commit
`5ea87ca65c1bd25f228c0447110d991a3f0de8c8` and CAPLAB baseline `44bb7bc`.
Original paths, copied bytes, commits and SHA-256 values are retained in
`/tmp/caplab-review-body-subject-sources.json`. `ValidateLegacy` accepts the
closed verdict vocabulary without subject pins; `ValidateStrict` requires
exactly the sealed subject. The admission writer verifies content hash against
body bytes and records evidence edges. The driver fold reads the first
evidence edge's subject. These source semantics govern the new predicates.

The first real-object regression assigned a refusal to a different admitted
subject. Three changes isolated identity, version and content hash. After
fixing that join, eighteen cases still assigned a verdict despite malformed
or contradictory body subject pins, missing/mismatched admitted identity or
hash, or admission before its purported producing run. Those cases then
passed after the remaining linkage checks. All raw parsed verdicts remain
available for inspection; failing attribution empties the selected body
verdict, findings and summary rather than silently retaining an older body.

The next test demonstrated that a gate could bypass the newly detected body
conflict. The gate reader now consults the observation for its exact evidence
admission. If that body parsed but attribution failed, the gate is marked
`evidence-body-attribution-conflict`; its raw outcome and references remain
visible. Removing the synthetic body object demonstrates the separate
missing-body case: exact gate metadata can still supply labeled fallback.

The body and gate predicates share only extraction of the first admitted
evidence claim, matching the source fold. Other joins remain in their existing
reader. Decoded inputs are borrowed without modification. The canary consumes
the recorded attribution, counts unverified body observations and renders
their reasons. It does not independently decide which body belongs to a run.

The prospective report is `caplab-review-canary/9`, with
`admitted-body-hash-and-exact-subject/1` and
`latest-body-if-linked-then-linked-review-gate/3`. Baseline versions 1–8 retain
their source/window checks and remain unmodified. Present but null, empty,
multiple or malformed body subject pins cannot use the absent-field fallback.
An absent field can use the admitted subject; the report explicitly denies
that this proves strict response conformance. A valid body can still disagree
with a gate's verdict for the same admission; that inspection signal remains.

The existing canary fixture writer now supplies admitted subject and content
hash defaults for constructed review outputs, like the inspected producer.
Explicitly provided malformed fields remain unchanged. The storage fixture
now supplies the admitted evidence edge; the same-admission discrepancy
fixture now uses matching artifact/body/evidence hash references. This repairs
the fixture contract rather than weakening the new checks. Parser and
missingness tests still exercise their original malformed response bytes.

Six new tests exercise real private SOB1/zstd objects and 65 focused tests
pass. They cover subject identity/version/hash collisions, 13 supplied-pin
forms, four admitted identity/hash failures, ledger ordering, positive legacy
and explicit subject linkage, latest-body selection, and gate fallback with
present conflicting versus missing bodies. Ruff F and diff checks passed.

The retained comparison under `/tmp/caplab-review-body-subject-fixture/`
contains four complete review bodies validated against the copied review
schema, their actual objects, source ledgers and canary reports. The baseline
reader assigns a refusal in all four cases. The repaired reader preserves
the matched refusal and leaves admitted-subject, body-subject and admitted-hash
mismatches unknown. Each remains a parsed body with raw verdict `reject`.
This distinguishes byte/schema validity from attribution. The verification
does not claim that the synthetic graph is valid for native execution.

No production incidence or reviewer correctness conclusion follows. The
reader still does not replay full native admission, posture, request,
independence or graph-integrity rules. Other downstream joins and object-store
resource limits remain separate surfaces. Historical evidence was not
recomputed, admitted or rewritten; the goal and roadmap remain incomplete.

## Doctrine and final checks

The release retrieval gate passed with fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`
and retriever `retriever-ec995ecdd083b2c8`. Initial packet
`pkt-817dcdbcd3f7d637` was reassembled once with four typed evidence records.
Final packet `pkt-912b5ba54ec7b9c5` has hash
`912b5ba54ec7b9c564f6254a6a766e7f81998a5a7359886e26ef6e5505de9e19`.
The activated concepts, conflicts, prohibitions and authority ceiling remained
unchanged after that pass.

Applied `universal-repository-contract-precedence`,
`universal-evidence-before-intervention`, `agent-conduct-authority-bounded-action`,
`python-mutable-ownership`, and `universal-preserve-behavior-by-default`.
The existing source contract defines exact pin comparison; this repair
introduces no entity class, identity lifecycle or new domain vocabulary.
The AI failure-mode review focused on schema-valid but misattributed data
and on gate fallback bypassing a body-level refusal to attribute.

Thirty-one residual obligations are nonmaterial: entity/modeling/expert-loop
requirements (14) concern a new domain-model investment rather than reuse of
the inspected immutable record contract; toolchain/configuration/version
inventories (6) concern no new language facility; resource and codec policies
(10) are unchanged by these in-memory attribution checks; expected future
change (1) is unnecessary for the demonstrated current defect. The exact
comparison semantics and positive/negative cases have source and executable
evidence above, independent of those modeling obligations.

`make check` exited zero: 1,326 tests in 164.602 seconds, four skips. The log
is `/tmp/caplab-review-body-subject-make-check.log`. No runtime or test edits
followed the run. Passing checks verify the scoped repair; they supply no
independent review judgment, production prevalence estimate or qualification.

Final private verification manifest:
`/tmp/caplab-review-body-subject-verification.json`, SHA-256
`1418b32ed3f98329cc0c46d998110e6f2fa3ec62536f83dacbc596fbb21e3614`.
It records 49 artifacts, including 15 retained synthetic fixture files, and
six runtime/test source hashes. Source snapshots matched their named commits;
the inspected Striatum files still matched those snapshots. All four typed
evidence records retained matching provenance hashes, and all five doctrine
citations classified as valid packet citations. Ten temporary packet,
evidence and citation files were embedded byte-for-byte, checked, then removed
by exact path. Source copies, regression logs, synthetic ledgers and reports,
full-suite output and verification scripts remain available.
