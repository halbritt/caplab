# Attribute review-gate fallback through exact admitted evidence

Baseline: `41a3247`. Decision mechanism: primary agent under the continuing
CAPLAB goal and [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Source observation and decision

Striatum `session_progress.go` selects one admitted review ledger and derives
the gate outcome from that ledger's recorded verdict. `gate_context.go`
resolves its exact evidence pin, producing run and reviewed subject.
`fold.go` derives the review subject and verdict from the first
`edges.evidences` entry. CAPLAB instead copies each review gate's outcome to
every referenced run without checking these links.

Require one distinct evidence entry, an exact subject matching the review run,
and a preceding admitted review-ledger artifact matching the evidence pin and
producing run. Its recorded subject and verdict must agree with the gate's
subject, verdict and pass/fail outcome. Keep raw gate observations and specific
reasons for unverified attribution. An unverified latest gate cannot inherit
an older gate's verdict. Retained body verdicts keep precedence; compare body
and gate disagreement only when the gate refers to that admitted body.
This is an inspection linkage rule, not full Striatum contextual validation,
independence proof or correctness adjudication. Multiple evidence items are
not assigned a common verdict without a separately specified aggregation rule.

## Authorization before execution

Authorize changing the criterion reader, canary renderer, their tests and this
record. Add focused synthetic tests in `tests/test_review_gate_attribution.py`;
update existing criterion/canary fixtures to reflect the inspected producer
contract and version the prospective canary/selection method. Retain all
previous baseline versions and historical exports without rewriting them.

Copy current Striatum `internal/driver/session_progress.go`, `gate_context.go`,
`fold.go` and `schema/ledger-records/gate_result.schema.json` plus
`schema/pin.schema.json` into private `/tmp/caplab-review-gate-link-*` custody,
with source commit/path/hash. These copies are interface evidence only, not
historical research admission. Retain constructed ledgers, before sources,
test logs, controls and verification artifacts under the same private prefix.
Run focused/full repository checks and commit the exact local scope.

No live ledger export/recompute, provider/model/native calls, credentials,
tracker writes, messages, push, Striatum changes or historical evidence edits.
Preserve unrelated files, `docs/designs/`, worktrees and services. Stop for
unexplained verification failures or a contradictory producer contract;
preserve failure custody. Authorization expires at commit. No ranking,
qualification or independent acceptance is delegated by this repair record.

## Execution and bounded verification

Source custody names Striatum commit
`5ea87ca65c1bd25f228c0447110d991a3f0de8c8` and CAPLAB baseline `41a3247`.
The copied files matched their committed bytes before intervention. The exact
paths and SHA-256 values are in `/tmp/caplab-review-gate-link-sources.json`.
No external event producer or historical export was changed.

The first regression showed an unrelated subject's gate clearing the review.
After subject linkage was repaired, eleven evidence mutations still cleared
it: missing/wrong pins, wrong producer/kind, missing or contradictory admitted
claims, contradictory gate verdict, and multiple evidence entries. The next
repair rejects those associations. Subsequent tests exposed missing report
diagnostics and cross-admission body/gate disagreement, then passed after
the canary changes. Red and green logs are retained separately.

`review_gate_attribution` owns the join in the existing criterion reader;
the canary consumes its result instead of independently recomputing it.
The gate's subject must exactly equal the run manifest's subject. Its evidence
pin must identify a review-ledger admission strictly after run opening and
before the gate event, with matching identity, content hash and producing run.
The first admitted `edges.evidences` entry must name that same subject and the
same verdict as the gate; the verdict must map to the recorded pass/fail
outcome. Duplicate identical evidence entries are tolerated, while distinct
entries remain unverified because the inspected normal producer selects one.

The reader validates supplied evidence version references without coercing
booleans, floats, strings, containers or negative numbers. Malformed reference
containers fail before body access. Complete admitted-artifact keys use the
event sequence as the version, as Striatum's fold does. Missing keys never
match each other. These are read-only comparisons; the decoded records are
not modified, and all original linked gate evidence is retained in the new
observation fields. No additional object-store lookup was introduced.

The most recent gate observation controls fallback eligibility. If it is
unverified, the selected gate outcome and evidence sequence are empty; an
earlier gate cannot silently survive under the latest gate's locator. Body
verdict precedence is preserved. Body/gate discrepancy flags require the same
admission sequence, so two different admitted review artifacts are not falsely
reported as one contradictory source pair.

Canary reports now identify `caplab-review-canary/7` and both readers identify
`latest-admitted-body-then-linked-review-gate/2`. Old baseline versions 1–6
still preserve their source hash and population cutoff without rewriting
their report bytes or claiming identical calculations. The rendered report
names unverified attribution reasons and states the limits of fallback.

The existing fixtures previously had only producing run references. They now
include a constructed admitted review artifact, subject pin and recorded
verdict. The added admission is itself a missing-body observation; old body
tests now include it in their expected sequence lists and continue to test
the specific later bodies. The changed disagreement assertion follows the
new same-admission contract, with a separate positive test proving that an
actual same-admission discrepancy is still flagged. Two pre-existing unused
test bindings were removed to pass the focused F lint check.

All 54 focused tests passed, including seven malformed reference forms,
future-admission rejection, repeated evidence, latest unverified gate
selection, same-admission disagreement and legacy baseline preservation.
Ruff F checks and `git diff --check` passed.

The private schema verifier validates complete constructed gate payloads
against the copied v2 schema with an explicit local registry, excluding the
permissive v1 union branch. Four gate payloads remain schema-valid: one matched
case and three with cross-record subject, evidence-hash or admitted-verdict
disagreement. The old reader clears all four; the new reader clears the
matched case and leaves the three mismatches unknown. This distinguishes
payload shape validation from actual record linkage. The verifier, source
ledgers and results remain under `/tmp/caplab-review-gate-link-*`.

No live production incidence is established. The reader does not replay
request equivalence, semantic environments, producing-run manifest hashes,
placement independence or native harness identity. It does not claim that
the constructed graph references form a valid executable Striatum graph.
`linked` means only that the inspected artifact, subject, verdict and ordering
references agree. Retained body attribution and other downstream joins remain
separate potential failure surfaces; gold correctness evidence is still
unavailable. Passing checks do not accept or qualify a reviewer.

## Doctrine disposition

The release retrieval gate passed with fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Initial packet
`pkt-f2533d6b0785fa02` was reassembled once with four typed evidence records.
Final packet `pkt-6e2fe9103f0ab3af` has hash
`6e2fe9103f0ab3afc2d6844ab299e16a65884b1728bd8552642d8ad78a442458`.

Applied `universal-repository-contract-precedence`,
`universal-evidence-before-intervention`, `agent-conduct-authority-bounded-action`,
`implementation-placement-by-ownership`, `python-runtime-static-boundary`,
and `universal-preserve-behavior-by-default`. The source producer and repository
contracts govern field semantics; tests exercise joins beyond schema shape.
The existing reader owns attribution, with no new orchestration layer.
Leaving the implementation unchanged would preserve the reproduced false
clearances. Removing every gate fallback would also discard the matched
case's usable recorded verdict; this repair distinguishes the two.

Twenty generic obligations remain nonmaterial: recurring-change evidence (1)
and expected future change (1) are unnecessary for the current reproduction;
toolchain/version/configuration inventories (6) and annotation/checker costs
(2) concern no introduced language facility or typing claim; structured
cleanup (5) concerns no new resource acquisition; codec/normalization/round-trip
obligations (5) concern unchanged byte/text handling. No material obligation
is treated as discharged solely by a type annotation or passing fixture.

## Final verification

`make check` exited zero: 1,315 tests in 203.515 seconds, four skips. The log
is `/tmp/caplab-review-gate-link-make-check.log`. No runtime or test edits
followed that run. The completed work improves attribution in prospective
reports; it supplies no new reviewer measurement or production prevalence
estimate and does not complete the roadmap.

The private verification manifest is
`/tmp/caplab-review-gate-link-verification.json`, SHA-256
`bd587ee6890b7617f042869ee51f6cb213b3dd19a5a6781bf4a1223de3bb1d6b`.
It covers 39 artifacts, committed source custody, five current runtime/test
hashes, the four schema-valid linkage controls and six valid doctrine citation
classifications. Ten temporary packet/evidence/citation files were embedded
byte-for-byte, verified, then removed by exact path. Source snapshots, failure
logs, synthetic ledgers, full-suite log and verification scripts remain.
The Doctrine release commit remains
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
