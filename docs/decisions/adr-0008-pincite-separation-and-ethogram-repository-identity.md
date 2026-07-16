---
id: adr-0008
artifact_type: architecture-decision-record
title: Pincite separation and Ethogram repository identity
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership-and-direct-instruction
created: 2026-07-16
decided_at: 2026-07-16
supersedes: []
superseded_by: null
affected_contexts:
  - pincite
  - ethogram
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# Pincite separation and Ethogram repository identity

Status interpretation: the repository owner directed continuation of the
Pincite separation and a subsequent repository rename on 2026-07-16. This
record selects the Pincite ownership boundary and records the owner's later
selection of Ethogram as the repository identity. It does not accept the
implementation or authorize changes to either separate repository.

## Decision question and scope

Which responsibilities remain here after Pincite becomes an independent corpus
and retrieval product, and what repository identity should describe the
remaining and intended work?

This decision governs tracked repository contents, the study-to-Pincite
integration contract, the GitHub repository identity, and live documentation.
It does not rewrite sealed experiment inputs, re-pin historical studies, alter
Pincite or standalone CAPLAB contents, or move the shared local Git common
directory while linked worktrees depend on it.

## Observations and evidence

**Observation:** Pincite is already a separate private repository with an
authoritative corpus, doctrine library, retrieval index, and executable release
at tag `pincite-release-20260716T023801Z`. **Evidence:** the dependency recorded
in [`../../pincite-dependency.json`](../../pincite-dependency.json) and its
fail-closed verification command.

**Observation:** ADR 0002 selected Agent Capability Lab as a product boundary
while CAPLAB work was still conducted here. **Evidence:**
[`adr-0002`](adr-0002-agent-capability-lab-v0.md).

**Observation:** `/home/halbritt/git/caplab` is now a separate Git repository.
Its ADR 0008 assigns current CAPLAB product and runtime authority there while
leaving source-study evidence in this repository before a later evidence
admission decision. **Evidence:** the standalone repository's README and
`docs/decisions/adr-0008-standalone-repository.md` at execution time.

**Observation:** checked-in Harbor tasks and reports contain content-addressed
Pincite projections and old `/home/halbritt/git/books` mount paths. Changing
those bytes would change historical experiment evidence. **Evidence:**
`doctrine/evaluations/robustness/harbor/tasks/`.

**Observation:** the local Git common directory serves multiple linked
worktrees. Moving it during this migration would invalidate their administrative
paths. **Evidence:** `git worktree list --porcelain` at execution time.

## Inferences, rivals, assumptions, and uncertainty

**Inference:** keeping a second live corpus, doctrine graph, retrieval runtime,
or conversion pipeline here would create two authorities and make release
identity ambiguous.

**Inference:** using `caplab` for this repository would create ambiguous product
authority and occupy the natural remote name for the existing standalone
CAPLAB repository.

**Observation:** the repository owner states that the repository will evaluate
skills, measure agent judgment, and support model fine-tuning, then selected
`ethogram` after a divergent naming review. **Evidence:** owner instructions on
2026-07-16.

## Recommendation and alternatives

**Recommendation:** retain historical evaluation, adjudication, dashboard, and
study-custody surfaces; consume an exact Pincite release through a checked
dependency manifest; use Ethogram as the identity for behavioral evaluation,
judgment measurement, and governed fine-tuning evidence; and defer moving the
local common directory until linked worktrees are retired.

Alternatives were to retain duplicate Pincite implementation, use an unpinned
neighbor checkout, rewrite historical experiment bytes, or move the local
common directory immediately. Those options respectively create split
authority, non-reproducible inputs, invalidated provenance, or broken
worktrees.

## Decision, owner, authority, and rationale

**Decision:** separate all live Pincite-owned corpus, conversion, doctrine,
retrieval, and generated-book implementation from this repository. The
historical study and evaluation surfaces retained here consume Pincite through
the exact dependency contract. The repository identity is Ethogram, with
GitHub slug `ethogram`. Ethogram covers agent-skill evaluation, agent-judgment
measurement, and provenance-preserving selection of evidence for model
fine-tuning. It does not silently turn evaluation output into authorized
training data.

**Owner and authority:** repository owner under repository ownership, through
the direct 2026-07-16 instruction to continue the separation and then rename
the repository and the subsequent direct selection of `ethogram`.

**Rationale:** one authority per product makes provenance, release identity,
and failure ownership inspectable. A pinned external seam preserves
reproducibility without duplicating Pincite implementation.

## Authorization and execution scope

Authorized execution includes:

- removal of Pincite-owned tracked content from this repository;
- CAPLAB tool and test changes needed to read the pinned Pincite release;
- documentation and CI changes for the Pincite boundary;
- regeneration of deterministic evaluation metadata retained here;
- commits and pushes for this migration; and
- renaming the GitHub repository and its configured remote to `ethogram`.

The separate Pincite repository, historical sealed experiment bytes, raw
Harbor jobs, standalone CAPLAB repository, model calls, paid services, and
acceptance decisions are outside this authorization. Moving the local Git
common directory is deferred.

## Consequences and preservation boundaries

- Repository checks fail closed when the Pincite commit, release tag, corpus
  ID, or doctrine ID differs from the manifest.
- GitHub Actions runs the hermetic suite; private Pincite integration is
  verified by the full local gate.
- Historical `books` paths remain where changing them would alter sealed
  experiment evidence or stable schema identifiers.
- The GitHub repository is named `ethogram`. The local checkout remains at
  `/home/halbritt/git/books` until its linked worktrees can be retired safely.
- Pincite upgrades require an explicit manifest change and integration check.

## Verification and fitness criteria

- no live source corpus, generated books, conversion pipeline, doctrine graph,
  or Pincite retrieval implementation remains tracked;
- `make test` passes without reading a local Pincite release;
- `make check` passes against the exact pinned Pincite release;
- deterministic generated files are current;
- repository documentation distinguishes this evidence-custody repository
  from standalone CAPLAB;
- historical sealed artifacts are byte-preserved;
- the GitHub repository is private, named `ethogram`, and retains `main`; and
- unrelated linked worktrees remain intact.

These checks verify conformance. They do not constitute owner acceptance.

## Acceptance owner and outcome

The repository owner is the acceptance owner. Outcome pending.

## Reopening and supersession conditions

Reopen if Pincite must own study custody, the private dependency cannot be
verified in the required environments, a shared contract repository becomes
necessary, standalone CAPLAB admits the historical evidence, the owner selects
a new repository identity, or the linked-worktree constraint ends and the
local common directory should be moved.

## Related artifacts

- [`pincite-dependency.json`](../../pincite-dependency.json)
- [`context-map.md`](../domain/context-map.md)
- [`README.md`](../../README.md)
- Pincite ADRs 0004 and 0005

## Status history

- `2026-07-16` — `decided` — repository owner directed the continued
  separation and repository rename; implementation and verification followed
  under the bounded scope above. An initial `caplab` slug assumption was
  reverted after discovery of the existing standalone CAPLAB repository.
- `2026-07-16` — `decided` — repository owner selected `ethogram` for a
  repository intended to evaluate skills, measure agent judgment, and support
  governed model fine-tuning.
