# Preserve shared custody inspection with explicit startup selection anchors

Baseline `3f60ca3`. Primary agent under ADR 0026 and the continuing CAPLAB goal.
The preceding turn was progress, but inspection of the next native-binary
integration revealed a compatibility regression that must be repaired first.

## Observation and decision

The original close-observation auditor calls inspect_custody on its retained
safe capture. That root has selection.json for its private diagnostic, not the
public startup's selections.json. Its report intentionally supplies task,
collection and handoff anchors without an exec anchor; separate native checks
own execution linkage. The latest extraction unconditionally reads plural
selections.json and therefore rejects this valid shared-custody caller. The
previous refinement's premise that every valid caller has public startup
selections is contradicted by the actual retained auditor.

Introduce an optional independent expected_selections_sha256 keyword on
inspect_custody and its execution inspector. With no selection anchor and no
exec trace anchor, preserve the original empty execution report without reading
startup-specific files. With an explicit selection anchor, validate it and read
the sealed selections even if the report lacks an exec anchor; a true
entrypoint-termination requirement must still reject that missing trace. For
legacy traced callers without the new keyword, keep the existing selection-to-
intent check and exec-only/required-result interpretation. An explicit anchor
must agree with both selection bytes and intent. Malformed or wrong hashes
must fail without falling back to the legacy path.

New traced startup calls pass their independently retained selection hash both
inside the supervisor and during post-exit inspection. This separates whether
the caller requires startup selection custody from whether a report happens to
contain a trace anchor. No field in the untrusted report may select that caller
requirement. Default shared custody supplies no startup-execution claim.

## Prospective authorization

Authorize changes to the startup probe, its execution tests, the native launch
contract and this record. Retain private source, regression, compatibility,
advisory, test and live Plane evidence under /tmp/caplab-selection-anchor-*.
Reconstruct the original close diagnostic's in-memory custody input from its
retained handoff/resource/inventory records, verify its original manifest and
all listed hashes, reproduce current failure, then compare repaired custody
output with the original audit's custody_consistency. This read-only application
is a new inspection, not rerunning or editing the frozen original auditor.
Preserve original source commits, paths, hashes and attempt dispositions.

Use TDD for the legacy untraced caller, independently anchored missing-trace
refusal, wrong/malformed selection anchors, selection/intent tampering and
normal new traced behavior. Update the preceding missing-trace regression to
supply the explicit caller anchor; retain its rejection expectation. Run
focused and full checks. No new native attempt, provider/model call, real
credentials, tracker write, historical evidence rewrite/admission, push,
message, deployment or independent acceptance. Preserve unrelated designs,
worktrees and services. Stop on unexplained regressions or source drift;
temporary fixtures and read descriptors close on failure. Authorization expires
at the local commit. Native-child linkage and the wider roadmap remain open.

Leaving the regression in place breaks a demonstrated caller. Inferring the
need for selection custody from file existence would let omission choose a
weaker path. The explicit caller anchor preserves the shared interface while
making the new startup requirement independent of report omissions.

## Reproduction and implementation

The private compatibility probe verified the original close-observation
manifest and all its artifact hashes, reconstructed the original custody input
in memory and reproduced FileNotFoundError for safe's absent selections.json.
It did not launch a process or rerun the original frozen auditor. The first
test draft lacked handoff context and failed before the intended regression;
the corrected fixture retained that context and reproduced the missing file.
Both logs remain available. The restored no-anchor/no-exec branch passed the
corrected test and performs no startup-specific reads.

The next regression supplied eight wrong or malformed independent anchors;
the initial new keyword ignored them, so all eight failed the refusal test.
Explicit lowercase SHA-256 validation and equality against selected bytes now
reject them. The original missing-trace regression still requires refusal,
with its caller hash supplied independently. A separately re-sealed weaker
selection and matching intent also fail against the original caller hash.
No field in the report can remove that argument. New traced supervisor and
post-exit callers pass the hash; untraced shared callers keep the old default.

All 35 focused startup, launch, termination and tracer tests pass. Three new
test methods protect the observed compatibility defect, ignored hashes and
joint selection/intent replacement. Updated existing tests exercise the new
explicit caller argument while preserving missing-trace and normal-result
assertions. Test Guard found no mocks or internal-call assertions. Failures
continue through existing RuntimeError guards, capture/ValueError checks and
filesystem exceptions, with no alternate-source or weaker-report fallback.

After repair, the unchanged compatibility probe verifies that inspect_custody's
complete output equals the original audit's custody_consistency exactly.
Original task, collection, handoff and retained-mount anchors agree, and study
eligibility stays false with capture completeness null. This is a new read-only
compatibility observation; original source pins and failed-attempt disposition
remain historical and unchanged. It does not assert that the old auditor could
run unchanged against today's source pins or that a new native attempt passed.

The source check retains 12 baseline/current identities and verifies unchanged
non-execution custody-check ASTs, startup constants and four unrelated startup
functions. Native launch, exec, termination, tracer and resource implementations
are unchanged. Current Plane still reports 86 items, 12 open, CAPLAB-84 In
Progress. Ruff F and diff checks pass. The contract now states exactly when
selection custody is required and why shared callers can omit it without
claiming startup execution. Native-child linkage remains the next integration
gap after this prerequisite repair.

The full make check passes 1,393 tests with four skips. No runtime or test
source changed after it began. Documentation symbols, argument flow and
relative links match current source; the contract explicitly replaces the
previous unconditional-read behavior. Private probe scripts also pass Ruff F.

## Advisory review

The retrieval-state gate passes for release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-f9079bc8e26fe649` and final packet
`pkt-c7d685aa0fc92dda` were read. Final content SHA-256 is
`c7d685aa0fc92dda8e187ea1731eb76be8fe83046022963cf72dc9b4aedca7ae`.
Five typed records retain authority, incidents, source, tests and runtime
observations with exact source locators and hashes.

Applied guidance is repository-contract precedence, evidence before
intervention, authority-bounded action, behavior preservation and separation
of semantic from structural work. Actual caller evidence overrides the prior
assumption about startup file topology. The repair changes only the explicit
selection requirement and its callers; it does not expand into native-binary,
resource or capture refactoring. Keeping the failure or inferring requirements
from file existence would leave either compatibility or omission safety broken.

Of 28 unmet obligations, 18 concerning deduplication, bulk discovery,
asynchronous UI, symbolic configuration references and top-N ranking are
nonmaterial: none of those mechanisms changes here. Three monitoring
obligations are nonmaterial because no service or paging policy changes.
Three external-capability and four authoritative-gate obligations remain
material to full native startup/serving-parity conclusions, which are withheld.
The supported claim is repaired shared custody compatibility and explicit
caller-anchored startup refusal behavior. Neither the passing suite nor the
matching historical custody result establishes complete capture, independent
acceptance or reviewer capability.

Private manifest `/tmp/caplab-selection-anchor-verification.json`, SHA-256
`876e1da355c85d948507099476057eacfa6a2c36db1438192c089f97e6509ef6`,
seals 20 artifacts, 12 baseline/current source records and three current
implementation/test/contract files. Eleven advisory scratch files were
embedded, hash-verified and removed. All five cited concepts classified as valid
packet citations. Original diagnostic artifact hashes remain unchanged.

This local commit closes the scoped compatibility repair and expires its
authorization. No native attempt, tracker write, push or independent acceptance
occurred. The broader goal remains active, with native-child identity,
parentage and outcome integration still next.
