---
id: adr-0019
artifact_type: architecture-decision-record
title: Canonical CAPLAB repository and Ethogram history consolidation
status: decided
decision_owner: repository-owner
decision_authority: direct-owner-instruction-and-caplab-39
created: 2026-07-19
decided_at: 2026-07-19
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-runtime
  - historical-evaluation-custody
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# Canonical CAPLAB repository and Ethogram history consolidation

## Decision question and scope

How should the published Ethogram repository and the standalone CAPLAB runtime
repository become one canonical `halbritt/caplab` repository without losing
either Git history, unmerged branches, unrelated local work, or a rollback
path?

This decision governs repository identity, history topology, the active tree,
GitHub metadata, local checkout paths, compatibility redirects, and recovery
artifacts. It does not reinterpret historical studies, change CAPLAB runtime
behavior, authorize a new evidence admission, or promote historical Ethogram
code into active product authority.

## Observations and evidence

**Observation:** the standalone `/home/halbritt/git/caplab` repository owns the
active product, `src/caplab` package, decisions, runtime, and verification
records, but had no remote before this migration. **Evidence:** CAPLAB ADR 0008,
its repository instructions, and Git inventory at
`49aabe939270a29de3d98c731c4f37e72a512a7e`.

**Observation:** GitHub repository ID `1296585434` was named
`halbritt/ethogram`, retained the prior published history and one merged pull
request, and already accepted `halbritt/caplab` as a redirect to that same
object. **Evidence:** GitHub repository and REST API inventory on 2026-07-19.

**Observation:** the local histories had unrelated roots. Ethogram retained
seven local branches beyond `main`, all with commits not contained in its
`main`; it had no tags or releases. **Evidence:** `git rev-list`, `git cat-file`,
`git for-each-ref`, and GitHub inventory before mutation.

**Observation:** the Ethogram checkout contained 511 MiB of untracked book
conversion work and a 6.3 MiB untracked binary. No live process, unit,
container, cron entry, or symlink depended on the Ethogram path. **Evidence:**
Git porcelain status, filesystem inventory, process inspection, systemd,
Docker, cron, and symlink checks on 2026-07-19.

**Observation:** the former Ethogram ADR 0008 named owner selection of a new
identity, later CAPLAB evidence admission, and retirement of linked-worktree
constraints as reopening conditions. **Evidence:** the decided record at
Ethogram commit `16f9d7a0766281d1a0264ca5d335f3049fbf557b`.

## Inference, rivals, and recommendation

**Inference:** using the existing GitHub repository object for the canonical
remote preserves its pull-request metadata and redirects, while combining the
unrelated histories in Git preserves both provenance lines. Keeping the active
CAPLAB tree at the root avoids changing runtime behavior or host integration.

The principal rival was to make the former Ethogram tree the active root and
merge the standalone package into it. That would place two `caplab` Python
package layouts and two build contracts on one import path. Another rival was
an ancestry-only `ours` merge, which would retain commits but make the former
tracked tree needlessly difficult to inspect. Keeping two canonical
repositories would reject the owner's selected identity and preserve the
authority ambiguity.

**Recommendation:** retain CAPLAB as the first-parent active line; import the
complete former Ethogram tracked tree under `history/ethogram/` with its main
history as a merge parent; preserve every former branch; rename the existing
GitHub repository object back to `halbritt/caplab`; and keep both verified Git
bundles and the old dirty checkout as rollback material.

## Decision, owner, authority, and rationale

**Decision:** `halbritt/caplab` and `/home/halbritt/git/caplab` are the sole
canonical repository identities. The root tree remains CAPLAB's active
product and runtime authority. The former Ethogram `main` tree is retained at
`history/ethogram/`, and its ancestry is a parent of the consolidation commit.
Former Ethogram branches retain their names and commits. Historical uses of
“Ethogram” remain intact when they identify past artifacts or decisions.

The existing GitHub repository object is renamed from `ethogram` to `caplab`
so its metadata and the old URL redirect survive. The old local checkout is
retained under a dated recovery path with its untracked contents; the former
`/home/halbritt/git/ethogram` path becomes a compatibility redirect to the
canonical checkout only after recovery verification.

**Owner and authority:** the repository owner selected CAPLAB directly on
2026-07-19 and authorized planning and execution through CAPLAB-39. That scope
includes repository and remote mutations but requires exact target
verification and a retained recovery path before retiring the old identity.

**Rationale:** one canonical root preserves product authority, while a subtree
and merge parent preserve inspectable historical bytes without creating a
second active package or CI surface. Verified bundles and a retained dirty
checkout make the structural migration reversible.

## Verification and rollback

Verification requires:

- both pre-migration Git bundles verify as complete and retain their SHA-256;
- the consolidation commit has both histories as ancestors;
- every former Ethogram branch and its exact tip remains present remotely;
- CAPLAB's full repository gate passes from the canonical root;
- the former Ethogram hermetic suite still passes from the historical subtree;
- GitHub exposes `halbritt/caplab` as repository ID `1296585434` and the old
  `halbritt/ethogram` URL redirects to it;
- no active build, runtime, automation, agent, fleet, or Plane reference treats
  Ethogram as canonical; and
- the canonical branch is clean and pushed.

Rollback may reconstruct either pre-migration repository from
`/var/tmp/caplab-39-caplab-before-2026-07-19.bundle` or
`/var/tmp/caplab-39-ethogram-before-2026-07-19.bundle`. The dated recovery
checkout retains the two untracked Ethogram paths that Git bundles cannot
contain.

Passing these checks is verification, not owner acceptance.

## Reopening conditions

Reopen if the historical subtree becomes an active package dependency, GitHub
no longer maintains the old-name redirect, a preserved branch tip is missing,
or a consumer requires a separately released historical-evaluation product.

## Status history

- `2026-07-19` — `decided` — repository owner selected CAPLAB as the canonical
  identity and authorized the history-preserving consolidation in CAPLAB-39.
