# Preserve and compare whole review anchors

Date: 2026-09-08. Observation, execution, and verification under the repository
owner's active CAPLAB improvement goal. The preceding goal turn produced
verified progress in `7738ed1`. This repair makes no model calls and grants no
qualification or placement authority.

## Reproduction

At `7738ed1`, the advisory pool credited an anchor when either normalized
string contained the other. A finding naming `m`, `motivation-extra`, or
`some-motivation` could therefore receive credit for `motivation`. The runner
also compared every emitted anchor but retained only eight, allowing a later
rescore to lose a match that appeared ninth.

The constructed regression run failed eleven assertions across six test
methods before the repair. The failures cover substring credit, truncated
evidence, missing version boundaries, and pooling incompatible anchor rules.
This is evidence about measurement software, not observed reviewer behavior.
The local reproduction log is `/tmp/caplab-anchor-red.log`.

## Prospective behavior

New pool rows and summaries declare
`anchor_matching: normalized-anchor-exact/1`. The shared review-response
module compares whole normalized identities. The existing normalization of
wrappers and letter case is preserved; this is not byte-exact matching.
The full representative mutant anchor list is retained. The existing
per-attempt records continue to retain all parsed responses.

The scorer reports `exact_anchor_mention` with its numerator and denominator.
Historical runs keep their frozen substring matcher and
`anchored_detection` denominator. A backend with both kinds of run receives
separate location metrics. Verdict metrics retain their existing behavior.
Unknown matching versions or inconsistent row/summary markers refuse
scoring, and resumption refuses incompatible rows before invoking an adapter.

The historical vendored matcher, existing rows, summaries, claims, and
exports were not rewritten or reissued. The export generator's catalog and
the advisory guides explain the new metric for future use.

## Interpretation and remaining work

An exact location mention does not establish that the finding correctly
explains a defect. It can accompany an accepting verdict; listing every real
anchor can still satisfy it. This repair removes substring gaming and lost
evidence, but does not validate semantic finding quality, alter the gate's
lexical conformance check, admit a new benchmark, or support reviewer ranking.
The confirmed disposition keeps injection sweeps parked.

A read-only Plane enumeration returned all 86 CAPLAB work items: 60 Done,
five Cancelled, eleven Ready, nine Backlog, and one In Progress. The snapshot
is `/tmp/caplab-roadmap-20260908.json`. These are planning states, not an
acceptance audit; no tracker state was changed. The code-review construct
remains a design scaffold in
`docs/product/advisory/code-review-construct-design.md`. Semantic finding
validation and independently grounded production outcomes remain material
to the active goal. The untracked `docs/designs/` work was preserved.

## Verification

Full `make check` passed **717 tests with four existing skips** in 160.251
seconds. The log is `/tmp/caplab-anchor-make-check.log`. Tests cover whole-name
matching, empty names, wrapper normalization, finding-text extraction,
retention beyond the eighth finding, accepting verdicts with exact mentions,
historical behavior, separate denominators, incompatible resumption, and
persistence through a real local subprocess fixture. `git diff --check`
passed. The skipped campaign and PostgreSQL integration checks remain outside
this verification.

## Engineering guidance and limits

The validated Pincite release supplied packet `pkt-ed98285672385a3c`, content
SHA-256 `ed98285672385a3c378312685a20b16aa29d0dbdff6bacc54fdbe3c1f89afbfe`,
doctrine `doctrine-f6bbb5196a3f8bf9`, retriever
`retriever-ec995ecdd083b2c8`. The applied guidance was
`implementation-risk-driven-tests`,
`universal-preserve-behavior-by-default`, and
`universal-repository-contract-precedence`.

Material authority, contract, and preservation questions are answered by the
owner's active goal, AGENTS.md, ubiquitous language, confirmed disposition,
and the prospective scope above. The inspected source and failing regression
establish the causal defect; the completed suite establishes the bounded
repair. These observations discharge the material questions even where the
packet retains generic authority and contract checklist entries. This is a
semantic software repair, not a refactoring or historical reanalysis.

The no-change alternative leaves trivial substring credit and unreproducible
anchor scores. Changing the vendored matcher in place risks silently changing
historical interpretation. Keeping full evidence and separating prospective
matching adds one declared contract without migrating retained data. No
schema, database, deployment, or external service changed.

Remaining packet obligations concerning ingest population, deduplication
keys, relevance-ranked top-N selection, operational pages, recurring-change
statistics, and an entire gate inventory are nonmaterial to this bounded
repair. Actual production incident frequency and eval-versus-serving parity
remain unverified and exclude claims about reviewer performance or deployment
readiness. Doctrine is advisory; it supplies no CAPLAB acceptance authority.
