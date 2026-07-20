---
id: adr-0025
artifact_type: architecture-decision-record
title: CAPLAB P13 independent verification authorization
status: authorized
decision_owner: repository-owner
decision_authority: repository-ownership-and-explicit-delegation
authorization_delegate: primary-agent
executor: /root/p13_independent_verifier
created: 2026-07-20
decided_at: 2026-07-20
expires_at: 2026-07-21T23:59:59Z
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-study-001
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts:
  - caplab-p13-independent-verification-proposal-2026-07-20
---

# CAPLAB P13 independent verification authorization

## Owner delegation

After receiving the exact CAPLAB-33 proposal and a request to authorize its
delegation to a fresh independent sub-agent, the repository owner instructed:

> I delegate authorization to you

The primary agent accepts that bounded delegation only to select the exact P13
executor, verification access, expiry, cleanup, and stop conditions below. It
does not receive verification or acceptance authority. The primary agent
implemented or executed parts of P7 through P11 and cannot issue P13's verdict.

## Decision and authorization

Authorize fresh team task `/root/p13_independent_verifier` to execute
CAPLAB-33 under the procedure in
[`caplab-p13-independent-verification-proposal-2026-07-20`](../records/caplab-p13-independent-verification-proposal-2026-07-20.md).
The executor works only in branch `verify/caplab-33-independent` at sibling
worktree `/home/halbritt/git/caplab-wt/verify-caplab-33-independent`.

The campaign identity is
`caplab-p13-independent-verification-2026-07-20`. Its root-owned mode-0700
evidence directory is
`/var/tmp/caplab-p13-verification-2026-07-20`. Authorization expires at
`2026-07-21T23:59:59Z`; access must be disabled earlier when verification
stops.

The product-and-decision baseline is clean CAPLAB commit
`cc6044fb8418d7ddafa1005e0e941616bd8cdc1f`. The verifier also records and
checks the clean authorization commit containing this ADR before beginning.
Proximal desired state remains
`1b79aa07cc4e44e8fc828449f882c6b62008edb6`.

## Authorized effects

The independent executor may:

1. create files only inside its isolated worktree, temporary directories, and
   the named verification evidence directory;
2. read the CAPLAB and Proximal repositories, installed CAPLAB configuration
   and runtime, CAPLAB-controlled database and object inventories, and retained
   P4 through P10 execution and verification evidence;
3. use `sudo` for those bounded read-only observations without printing or
   retaining credentials;
4. copy only the exact inputs and outputs needed for independent comparison
   from sealed CAPLAB evidence into the new verification directory, preserving
   source locator, source manifest, byte hash, and custody provenance;
5. run the repository gate, hermetic fixture checks, canonical profile and
   candidate replays, checksum verification, and read-only store queries;
6. run one live P7 read-access lifecycle through the installed controller:
   install a cleanup trap, `enable`, `verify --phase ready`, run the frozen
   model-free recomputation twice as `caplab_reader`, `disable`, and
   `verify --phase disabled`; and
7. write and commit one independent P13 verification record, with its criterion
   ledger, separate technical and v0-criteria conclusions, residual failures,
   cleanup observation, and sealed evidence-manifest identity.

The existing P7 reader role and controller are reused for the one authorized
read-only lifecycle. No new persistent database role, OS account, Garage key
alias, runtime, service, or host file is authorized. The controller-created
temporary key, credential, login, state, session, and access window must all be
removed through aggregate disablement.

## Excluded effects

This authorization does not permit:

- evidence admission, registration, historical rewriting, or mutation of P4
  through P10 evidence;
- database, Garage, or independent-copy repair, restore, purge, deletion, or
  write;
- runtime, controller, service, configuration, migration, repository product
  code, or accepted-criteria changes;
- P12 export, any other copy outside the named verification root, model calls,
  training, publication, routing, deployment, or preference work;
- synthesis or revision of P9 or P11 human judgments; or
- CAPLAB-34 acceptance, conditional acceptance, revision, or rejection.

Recovery verification is limited to the sealed P5 records and evidence plus
isolated synthetic tests. A need for fresh live recovery, restore, repair, or
purge must be reported as `NOT VERIFIED` and separately authorized.

## Stop and cleanup conditions

The executor stops without repair when independence, source custody, a bound
identity, a replay, an expected refusal, an observable oracle, or the authority
boundary cannot be established. It also stops if any command would exceed the
named effects, expose a credential, or mutate protected state.

Aggregate disablement runs on every exit after access enablement. A cleanup
failure is retained as a failed criterion and escalated; it is not hidden by a
technical pass. The verifier records `PASS`, `FAIL`, `NOT VERIFIED`, or
`UNMET BY DECISION` for every frozen criterion and cannot change the criteria.

The primary agent may merge the independently committed record and reconcile
Plane after checking branch provenance and repository gates. That merge is
record custody, not a second verification verdict or acceptance.

## Status history

- `2026-07-20` — `authorized` — the repository owner delegated authorization;
  the primary agent bound the exact independent executor and P13 effects.
