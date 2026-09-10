---
id: adr-0066
artifact_type: architecture-decision-record
title: Rank native reviewers on verified code-review outcomes
status: decided
decision_owner: primary-agent
decision_authority: adr-0026 and owner thread goal
created: 2026-09-10
---

# Rank native reviewers on verified code-review outcomes

## Owner requirement and decision

The owner activated this goal in thread
`01a08054-82f9-7a32-b0c1-a62c395cd320`:

> Develop and validate a defensible ranking of native agent reviewers for
> explicitly defined code-review tasks, without routine human participation,
> using independently verifiable defect and clean-control evidence.

The owner then required: "Please don't repeat the mistakes earlier agents
made by creating instruments that didn't measure the desired outcome."

Select `reviewer-ranking-001`: measure whether a native reviewer identifies
real, actionable defects and avoids false blockers in actual code changes.
The initial target is first-pass review of changes to the owner's software
repositories. This is a new empirical question. Completing ADR 0065's
advisory-response study does not complete it. Do not resume that study merely
because its infrastructure is reusable.

The primary agent exercises the existing ADR 0026 delegation for routine
study decisions. No routine human coding or adjudication is planned. That
delegation cannot turn an agent's opinion into independent ground truth.

## Validity before measurement

The September 7 operator audit found that the old ordering came from
perturbations without production analogs; eight of nine bindings caught all
13 scorable analog defects. Preserve the prohibition on ranking from that
instrument. This decision does not reopen its sweeps, re-score its history,
adopt its thresholds, or change operational placement.

The initial population reconnaissance is a census of mainline code changes
in `caplab`, `striatum-next`, `council`, and `ai-newsroom`, with exact source
tips and a fixed committer-time window. These repositories are a starting
frame, not an assertion that they represent all owner work. Quantify their
languages, change sizes, and exclusions before selecting a study population.
Commit messages, later fix labels, reviewer results, and ease of scoring must
not determine membership in that frame. Related changes and repeated runs
must not become independent incidents by renaming them.

Use real changes with their original base, surrounding implementation,
requirements, and available tests. Defect witnesses must demonstrate the
claimed behavior and its contractual violation. Clean evidence must state
which properties it establishes; a passing regression suite does not prove
an entire patch defect-free. Author-written toy implementations, reversed
fixes, injected mutations, and canned reviews can test the apparatus but
cannot silently become the ranking population.

Before a ranking campaign, the instrument must satisfy the outcome and
validity gates in the [study development contract](../product/studies/reviewer-ranking-001/README.md).
An unmeasurable outcome stays unresolved and contributes to uncertainty. It
must not be relabeled a false positive, omitted from the denominator, or
replaced with a conveniently measurable proxy. Broad claims remain blocked
if the unresolved portion could reverse the ordering.

## Alternatives

| Option | Decision and reason |
|---|---|
| Resume synthetic injection ordering | Rejected: observed separation lacked production validity. |
| Finish the advisory-response roadmap first | Rejected as the goal path: behavior change does not measure review correctness. Reuse components when needed. |
| Adopt a public leaderboard or LLM judge labels | Rejected as a truth basis. External cases and methods may inform investigation; independent verification is still required. |
| Require owner adjudication for every case | Not selected: the owner requires autonomous work. Mechanically justified outcomes and explicit unresolved cases are the selected route. |
| Start with actual-workload census and outcome validation | Selected: exposes coverage and scoring gaps before committing to reviewer measurements. |

## Bounded development authorization

Under the active goal and ADR 0026, authorize changes to CAPLAB's new study
documents, population-census implementation and tests, plus local execution
of that census. Authorize read-only Git metadata inspection of these exact
source tips and their ancestry:

| Repository under `/home/halbritt/git` | Source tip |
|---|---|
| caplab | `152b9f197f8d37fc02f09e696653921b498c14da` |
| striatum-next | `5ea87ca65c1bd25f228c0447110d991a3f0de8c8` |
| council | `1144389665a3cbc89413e6aba6af2f3781d11e6f` |
| ai-newsroom | `544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f` |

Retain derived commit/parent/tree/blob identifiers, paths, times, counts,
selection reasons, and hashes locally and in CAPLAB's study records. This
names the historical metadata effect only: no source-content import,
experimental admission, original-history mutation, ledger relabeling, or
external transmission of source content is authorized by this record.
Preserve existing untracked `docs/designs/` and the detached worktree.

This development step spends zero model calls. Later bounded authorizations
can be recorded by the delegated mechanism after inspecting exact targets,
validity requirements, data exposure, budgets, and cleanup. Do not ask the
owner to approve routine decisions already delegated. Stop the relevant
effect on source mismatch, unavailable provenance, or an unverified outcome;
continue independent work. The development authorization expires when this
step is verified or the owner cancels the goal.

## Doctrine receipt and limits

Validated release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`. Evidence-backed packet
`pkt-609fb73005dbb3eb`, content hash
`609fb73005dbb3eb145f196ca0c41367b07bea3f9be63643e64bc7191c713373`,
is retained under `/tmp/caplab-review-ranking-doctrine-evidenced.json`.
The evidence-obligation disposition is retained with the development
verification record. Applied evidence-before-intervention, repository
precedence, explicit invariants, and authority-bounded action.

The doctrine packet does not establish population validity, independent
truth, or comparative performance. Those material obligations remain open;
the selected action is an investigation, not an accepted instrument.
Generic datastore, architecture restructuring, caching, and transaction
obligations are nonmaterial to the metadata census, which executes no target
repository code and changes no target runtime.

Reopen the instrument design if its case coverage misses substantial real
work, clean-control evidence is inadequate, scoring can be gamed, observed
performance is at ceiling, or adjudication uncertainty can change the result.
Do not lower validity requirements to finish a campaign.
