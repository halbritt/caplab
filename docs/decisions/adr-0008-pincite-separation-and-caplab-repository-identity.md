---
id: adr-0008
artifact_type: architecture-decision-record
title: Pincite separation and CAPLAB repository identity
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership-and-direct-instruction
created: 2026-07-16
decided_at: 2026-07-16
supersedes: []
superseded_by: null
affected_contexts:
  - pincite
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# Pincite separation and CAPLAB repository identity

Status interpretation: the repository owner directed continuation of the
Pincite separation and the subsequent repository rename on 2026-07-16. This
record selects the ownership boundary and repository identity. It does not
accept the implementation or authorize changes to the separate Pincite
repository.

## Decision question and scope

Which responsibilities remain in this repository after Pincite becomes an
independent corpus and retrieval product, and what identity should this
repository use?

This decision governs tracked repository contents, the CAPLAB-to-Pincite
integration contract, the GitHub repository name, and live documentation. It
does not rewrite sealed experiment inputs, re-pin historical studies, alter
Pincite contents, or move the shared local Git common directory while linked
worktrees depend on it.

## Observations and evidence

**Observation:** Pincite is already a separate private repository with an
authoritative corpus, doctrine library, retrieval index, and executable release
at tag `pincite-release-20260716T023801Z`. **Evidence:** the dependency recorded
in [`../../pincite-dependency.json`](../../pincite-dependency.json) and its
fail-closed verification command.

**Observation:** ADR 0002 selected Agent Capability Lab as this repository's
product boundary. CAPLAB owns behavioral capability measurement, study
identity, experiment custody, adjudication, and reviewer-facing capability
claims. **Evidence:** [`adr-0002`](adr-0002-agent-capability-lab-v0.md).

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

**Inference:** `caplab` is the least-surprising repository slug because the
accepted product name is Agent Capability Lab and the owner requested a rename
after separation. A longer `agent-capability-lab` slug is a credible
alternative; the shorter slug is used as an explicit execution assumption and
can be changed through GitHub's redirect-preserving rename if the owner later
selects another spelling.

## Recommendation and alternatives

**Recommendation:** retain only CAPLAB product, evaluation, adjudication,
dashboard, and study-custody surfaces; consume an exact Pincite release through
a checked dependency manifest; rename the GitHub repository to `caplab`; and
defer moving the local common directory until linked worktrees are retired.

Alternatives were to retain duplicate Pincite implementation, use an unpinned
neighbor checkout, rewrite historical experiment bytes, or move the local
common directory immediately. Those options respectively create split
authority, non-reproducible inputs, invalidated provenance, or broken
worktrees.

## Decision, owner, authority, and rationale

**Decision:** separate all live Pincite-owned corpus, conversion, doctrine,
retrieval, and generated-book implementation from this repository. CAPLAB
keeps evaluation and adjudication custody and consumes Pincite through the
exact dependency contract. The repository identity is Agent Capability Lab,
with GitHub slug `caplab`.

**Owner and authority:** repository owner under repository ownership, through
the direct 2026-07-16 instruction to continue the separation and then rename
the repository. The `caplab` slug follows the already decided product name.

**Rationale:** one authority per product makes provenance, release identity,
and failure ownership inspectable. A pinned external seam preserves
reproducibility without duplicating Pincite implementation.

## Authorization and execution scope

Authorized execution includes:

- removal of Pincite-owned tracked content from this repository;
- CAPLAB tool and test changes needed to read the pinned Pincite release;
- documentation and CI changes for the CAPLAB boundary;
- regeneration of CAPLAB-owned deterministic evaluation metadata;
- commits and pushes for this migration; and
- renaming the GitHub repository and its configured remote to `caplab`.

The separate Pincite repository, historical sealed experiment bytes, raw
Harbor jobs, model calls, paid services, and acceptance decisions are outside
this authorization. Moving the local Git common directory is deferred.

## Consequences and preservation boundaries

- CAPLAB checks fail closed when the Pincite commit, release tag, corpus ID, or
  doctrine ID differs from the manifest.
- GitHub Actions runs the hermetic CAPLAB suite; private Pincite integration is
  verified by the full local gate.
- Historical `books` paths remain where changing them would alter sealed
  experiment evidence or stable schema identifiers.
- The local checkout may remain at `/home/halbritt/git/books` temporarily even
  though the repository identity and remote are `caplab`.
- Pincite upgrades require an explicit manifest change and integration check.

## Verification and fitness criteria

- no live source corpus, generated books, conversion pipeline, doctrine graph,
  or Pincite retrieval implementation remains tracked;
- `make test` passes without reading a local Pincite release;
- `make check` passes against the exact pinned Pincite release;
- deterministic CAPLAB-generated files are current;
- repository documentation and live configuration use the CAPLAB identity;
- historical sealed artifacts are byte-preserved;
- the GitHub repository is private, named `caplab`, and retains `main`; and
- unrelated linked worktrees remain intact.

These checks verify conformance. They do not constitute owner acceptance.

## Acceptance owner and outcome

The repository owner is the acceptance owner. Outcome pending.

## Reopening and supersession conditions

Reopen if CAPLAB must author doctrine, Pincite must own study custody, the
private dependency cannot be verified in the required environments, a shared
contract repository becomes necessary, the owner selects a different
repository slug, or the linked-worktree constraint ends and the local common
directory should be moved.

## Related artifacts

- [`pincite-dependency.json`](../../pincite-dependency.json)
- [`context-map.md`](../domain/context-map.md)
- [`README.md`](../../README.md)
- Pincite ADRs 0004 and 0005

## Status history

- `2026-07-16` — `decided` — repository owner directed the continued
  separation and repository rename; implementation and verification followed
  under the bounded scope above.
