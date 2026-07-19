---
id: adr-0001
artifact_type: architecture-decision-record
title: Domain documentation authority
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership
created: 2026-07-12
decided_at: 2026-07-12
supersedes: []
superseded_by: null
affected_contexts: [repository-wide]
related_specs: []
related_plans: []
related_receipts: []
---

# Domain documentation authority

Status interpretation: the repository owner selected this documentation spine
and authorized its repository-local implementation. The decision does not
select runtime architecture or accept future domain-boundary proposals.

## Decision question and scope

Where should repository-wide vocabulary, domain-boundary proposals,
architectural selections, product contracts, and implementation sequencing be
recorded so agents and maintainers do not conflate them?

This ADR governs documentation authority and navigation. It does not select
bounded contexts, aggregates, repositories, domain events, service boundaries,
or implementation architecture.

## Observations and evidence

- `ubiquitous_language.md` already defines repository-wide assertion and
  authority terms and is mandatory under `AGENTS.md`.
- Doctrine tooling and pinned evaluation surfaces consume the lowercase root
  path `ubiquitous_language.md`.
- The repository had product specifications and implementation plans but no
  ADR index, ADR template, domain index, or context map before this decision.
- The then-repository-local Pincite operationalization document said a decision
  receipt may feed an ADR, but no repository-native ADR contract existed.
- The repository owner requested a DDD scaffold with an uppercase
  `UBIQUITOUS_LANGUAGE.md` entrypoint and ADRs on 2026-07-12.

## Inferences, rivals, assumptions, and uncertainty

A domain index and ADR contract give terms, proposed boundaries, selected
architecture, product behavior, and execution plans separate homes. The main
rival is to keep the existing glossary and product documents alone; that
leaves architectural selections without a durable identity or supersession
path.

A case-only root rename would provide the requested uppercase spelling, but it
would also change hardcoded and manifest-pinned paths. An uppercase discovery
entrypoint under `docs/domain/` supplies the conventional filename without
creating two root files that collide on case-insensitive systems.

The candidate capability clusters in the context map may not be bounded
contexts. Their status remains proposed until scenarios, language differences,
ownership, and integration evidence support a separate decision.

## Recommendation and alternatives

Select a small documentation spine:

- keep `ubiquitous_language.md` as the single canonical glossary;
- add `docs/domain/UBIQUITOUS_LANGUAGE.md` as the uppercase discovery
  entrypoint;
- record candidate boundaries in `docs/domain/context-map.md`;
- record architectural selections under `docs/decisions/`;
- keep specifications, plans, receipts, verification, and acceptance in their
  existing distinct roles.

Alternatives considered:

- **No change:** lowest immediate cost, but preserves the missing ADR and
  context-map surfaces.
- **Rename the root glossary:** clearer casing in isolation, but breaks pinned
  paths and expands the change into experiment migration.
- **Add tactical DDD catalogs now:** more familiar ceremony, but no current
  evidence establishes aggregates, repositories, or domain events.

## Decision, owner, authority, and rationale

The repository owner selected the recommended documentation spine through the
2026-07-12 request to add DDD scaffolding, ubiquitous language, and ADRs. The
selection applies to repository documentation and does not decide the candidate
bounded contexts in the initial map.

The selected split preserves one vocabulary source, makes architectural
selection durable, and prevents product readiness or model pre-review from
being mistaken for decision or acceptance.

## Authorization and execution scope

The same owner request authorizes documentation-only changes to:

- the canonical glossary;
- `docs/domain/` and `docs/decisions/`;
- repository navigation, product templates, doctrine navigation, and the
  changelog.

It does not authorize runtime behavior changes, generated corpus changes,
human audit or disposition changes, or re-pinning existing evaluation
surfaces.

## Consequences and preservation boundaries

- New architectural selections need stable ADR IDs and explicit owners.
- Candidate context boundaries remain visibly non-authoritative.
- The lowercase root glossary path remains stable for existing tools and
  manifests.
- ADR authors must keep authorization, execution, verification, and acceptance
  separate from selection.
- The additional documents require link maintenance when paths or authority
  rules change.

## Verification and fitness criteria

- Every new repository-relative Markdown link resolves.
- The canonical glossary has one normative definition for each added term.
- The ADR index, template, and this record agree on IDs and lifecycle states.
- `make check` passes without modifying generated or human-owned artifacts.
- A clean second link check produces the same result.

## Acceptance owner and outcome

The repository owner is the acceptance owner. Acceptance remains unrecorded
until the owner reviews the verified scaffold.

## Reopening and supersession conditions

Reopen this decision if tooling can migrate the canonical glossary safely, an
ADR tool imposes a different stable contract, the context map becomes
machine-validated, or a selected bounded context needs its own scoped
ubiquitous language.

Supersede this record with a reciprocally linked ADR rather than rewriting this
decision in place.

## Related artifacts

- [`../domain/README.md`](../domain/README.md)
- [`../domain/context-map.md`](../domain/context-map.md)
- [`README.md`](README.md)
- [`adr-template.md`](adr-template.md)
- [`../../ubiquitous_language.md`](../../ubiquitous_language.md)
- [`../../pincite-dependency.json`](../../pincite-dependency.json), which now
  identifies the external Pincite decision-receipt contract

## Status history

- `2026-07-12` — `decided` — repository owner selected and authorized the
  documentation spine.
