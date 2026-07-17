---
id: adr-0015
artifact_type: architecture-decision-record
title: CAPLAB P5 frozen executor source worktree correction
status: decided
decision_owner: caplab-execution-delegate
decision_authority: direct-repository-owner-delegation
created: 2026-07-17
decided_at: 2026-07-17
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-custody
  - proximal-caplab-p5
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# CAPLAB P5 frozen executor source worktree correction

Status interpretation: ADR 0014 authorized the exact remaining P5 purge and
required a clean installed-source preflight. The first preflight returned
status 2 before mutation because the P5 controller requires the shared CAPLAB
checkout's current `HEAD` to equal the older executor commit frozen in
`/etc/caplab-p5/SOURCE_COMMIT`. ADR 0014's own required commit necessarily
advanced that shared checkout. No credential, byte, database, role, service,
or backup effect occurred.

## Decision and authorization

**Decision:** bind the P5 controller to a dedicated clean linked worktree at
the already-frozen executor commit
`e86ed0ecd734b902be2afcd0d20d5a07225c2579` instead of the advancing shared
CAPLAB checkout.

**Owner and authority:** the `caplab-execution-delegate` acts under the
repository owner's delegated CAPLAB decision authority and the explicit ADR
0014 execution authorization. This correction changes only how the existing
source identity is located and verified. It does not change that identity,
the installed P5 package, registration runtime commit, request, content,
manifest, authorization hash, expiry, namespaces, roles, or allowed effects.

The executor may:

1. create linked worktree
   `/home/halbritt/git/caplab.worktrees/p5-executor-e86ed0e` at detached commit
   `e86ed0ecd734b902be2afcd0d20d5a07225c2579`;
2. update only the Proximal `caplab-p5` controller, tests, and documentation to
   name that exact path;
3. require exact `HEAD`, clean status, real-directory, and no-symlink checks;
4. commit and push the Proximal correction, run its full P5 host-surface gate,
   install only the corrected controller and otherwise byte-identical desired
   state; and
5. retry ADR 0014's read-only P5 preflight.

The linked worktree is active execution state through final P5 verification.
After P5 PASS and credential disablement, it must be removed with ordinary
`git worktree remove` and pruned. It is not historical evidence.

## Rationale and alternatives

The shared checkout must advance to record decisions and execution evidence.
Rewinding it would hide current authority from the executor and disturb other
work. Weakening the commit equality to an ancestor check would permit
unreviewed source changes. Temporarily bind-mounting or replacing the shared
path would create a dangerous alias. A dedicated exact-commit worktree keeps
the original equality and cleanliness guards while separating immutable
executor source from the repository's moving decision head.

## Verification and preservation

Repository tests must fail if the controller names the shared checkout, trusts
all Git directories, accepts a symlinked source, a different commit, or a dirty
worktree. Before installation, the full Proximal P5 gate and `git diff --check`
must pass. After installation, the helper and committed file hashes must
match. The retried preflight must still prove P4, P5, service, expiry, role,
credential, and backup state.

The shared CAPLAB checkout, live PostgreSQL cluster, P4, P5 data, Garage,
`/nvr`, backup services, and isolated-restore paths remain unchanged by this
correction.

## Doctrine provenance and stop conditions

This correction applies the local-contract precedence, explicit-invariant,
evidence-before-intervention, authority-boundary, and preservation guidance in
ADR 0014's evidenced doctrine packet `pkt-2ef8ec66cc51515b`. The new runtime
observation is the direct status-2 preflight refusal above.

Stop on any worktree path, commit, status, ownership, symlink, Proximal source,
installed-file, P4, P5, service, expiry, or credential mismatch. Stop rather
than loosen the exact commit or cleanliness predicates. Reopen if a linked
worktree cannot be safely verified or if any additional P5 behavior must
change.
