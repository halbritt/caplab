---
id: adr-0008
artifact_type: architecture-decision-record
title: Standalone CAPLAB repository
status: decided
decision_owner: caplab-execution-delegate
decision_authority: direct-repository-owner-delegation
created: 2026-07-15
decided_at: 2026-07-15
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-runtime
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# Standalone CAPLAB repository

## Decision question and scope

Should CAPLAB runtime and product authority remain in the `books` repository,
or should CAPLAB own a standalone repository while retaining content-identified
source provenance for the records first authored there?

This decision governs repository placement, package paths, imported governing
records, and the boundary between CAPLAB and its source studies. It does not
change Study 001, its capability card, evidence custody, or ADR 0007's storage
and P4 behavior contracts.

## Observations and evidence

**Observation:** ADR 0007 was proposed and selected at `halbritt/books` commit
`cdbb5120d1d450763fca2a8aca172f6308413440`. Its repository-effect section
still named `books` paths. **Evidence:** the selected commit and source SHA-256
recorded in [`source-provenance`](../source-provenance.md).

**Observation:** the repository owner then stated that CAPLAB had been
divorced from that repository and delegated CAPLAB decision authority to the
active agent. **Evidence:** the owner instruction on 2026-07-15.

**Observation:** no standalone `/home/halbritt/git/caplab` Git repository or
GitHub remote existed when execution began. The live read-only dashboard was a
release copied from the selected books branch. **Evidence:** filesystem, Git
worktree, and GitHub-repository inspection on 2026-07-15.

## Inferences, rivals, and uncertainty

Keeping CAPLAB code in `books` would preserve source-history convenience but
would make a research and model-development product depend on an engineering
corpus repository's lifecycle. A standalone repository gives CAPLAB one place
for its decisions, runtime, tests, dashboard, and verification records.

Copying historical Study 001 inputs into the new repository would simplify the
old dashboard projector, but it would move evidence under a P4 authorization
that explicitly excludes evidence admission. Keeping only the already
sanitized projection preserves the current review surface without performing
P6.

## Decision, owner, authority, and rationale

**Decision:** CAPLAB owns `/home/halbritt/git/caplab` as its standalone source
repository. Python packages use the `src/caplab/**` layout. ADR 0007's runtime,
test, fixture, and integration-test paths are normalized here as
`src/caplab/runtime/**`, `tests/test_runtime.py`, `tests/fixtures/runtime/**`,
and `tests/integration/test_runtime_local.py`. Its former `books` branch and
path clause is replaced by this decision. Proximal may own host integration
code, but it does not own CAPLAB product or research state.

The standalone import contains the governing CAPLAB records, capability card,
dashboard server, static assets, and sanitized Study 001 projection identified
in [`source-provenance`](../source-provenance.md). It does not import the
historical projector because that projector requires the unadmitted source
study's Git objects. A later P6 decision may provide a CAPLAB-native
recomputation path after evidence admission.

**Owner and authority:** `caplab-execution-delegate`, under the repository
owner's direct instruction that CAPLAB is separate and delegation of decision
authority on 2026-07-15. That role is bound to the primary agent in this
owner-authorized thread and campaign; it survives a handoff only when the
handoff preserves the direct instruction and campaign identity. It is not a
standing authority for unrelated agents. This delegation permits autonomous
CAPLAB design decisions. It does not silently expand an active execution
authorization.

**Rationale:** repository ownership should follow the product's lifecycle and
authority. Source provenance is sufficient to preserve the imported decisions'
origin; source-study evidence remains under its existing custody until P6.

## Authorization and execution scope

The owner's correction authorizes the structural import and adaptation needed
to continue the already-authorized CAPLAB-22/P4 campaign in the standalone
repository. The active P4 scope remains the one selected in ADR 0007, expiring
at `2026-07-22T23:59:59Z`.

No historical evidence copy, fetch, registration, retention change, model
call, P5 operation, historical-evidence disclosure, publication beyond the
authorized sanitized Plane projection, training action, or acceptance is
authorized by this decision.

## Verification and acceptance

Repository separation is verified when the imported source hashes are
recorded, CAPLAB has no runtime import from `books` or Pincite, the dashboard
loads the sanitized projection from the standalone package, and internal links
and tests pass. No source-study evidence is admitted or registered; the
identified sanitized projection is the sole imported derived view.

These checks do not verify P4 and do not accept CAPLAB. The repository owner
has delegated CAPLAB decision authority, not acceptance of an unverified
outcome.

## Reopening conditions

Reopen if CAPLAB must share a release cycle with another product, source-study
evidence cannot remain externally referenced before P6, or the standalone
split prevents exact provenance verification.

## Status history

- `2026-07-15` — `decided` — the delegated CAPLAB agent recorded the owner's
  repository-separation instruction and moved P4 implementation ownership to
  the standalone repository.
