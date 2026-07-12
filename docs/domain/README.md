# Repository domain model

This directory is the start-here surface for the repository's domain language
and candidate boundaries. It documents how the source library, generated
corpus, doctrine, evidence packets, and evaluation records relate without
inferring bounded contexts from directories.

## Authority and artifact map

| Artifact | Authority |
|---|---|
| [`../../ubiquitous_language.md`](../../ubiquitous_language.md) | Canonical meanings of repository terms |
| [`UBIQUITOUS_LANGUAGE.md`](UBIQUITOUS_LANGUAGE.md) | Uppercase DDD discovery entrypoint; no duplicate definitions |
| [`context-map.md`](context-map.md) | Candidate or decided context boundaries and relationships |
| [`../decisions/`](../decisions/README.md) | Selected architectural choices and their rationale |
| [`../product/`](../product/README.md) | Product specifications and implementation plans |
| [`../../doctrine/`](../../doctrine/README.md) | Evidence-governed engineering guidance below repository decisions |

Explicit owner instructions and accepted repository contracts precede these
artifacts. A context map entry becomes authoritative only when its status and
governing ADR say that a named owner selected it.

## Present capability inventory

The current repository exposes four capability clusters worth testing as
bounded-context candidates:

- corpus production;
- doctrine curation;
- judgment support;
- evaluation and adjudication.

They are candidates, not decided contexts. Their current responsibilities and
evidence are recorded in the [context map](context-map.md).

## Working rules

- Change a term when examples, code, tests, or reviewed usage show that its
  current meaning is wrong or ambiguous.
- Record a boundary or relationship selection in an ADR. Directory layout is
  not enough.
- Introduce aggregates, repositories, value objects, or domain events only
  after concrete invariants, identities, lifecycle rules, or past-tense domain
  facts are observed.
- Keep model screening and pre-review separate from human audits and
  dispositions.
- Do not let evaluation output rewrite doctrine or a decided context silently.

## Explicit unknowns

The scaffold does not yet decide:

- whether the four capability clusters are separate bounded contexts;
- which area, if any, is the Core Domain;
- context ownership or Customer/Supplier, Conformist, Published Language,
  Anticorruption Layer, or other relationship patterns;
- aggregates, aggregate roots, entities, value objects, repositories, or
  domain events;
- whether similarly named terms require translation between contexts;
- compatibility, service-level, retention, or release boundaries not already
  established elsewhere in the repository.

Those questions require scenarios and ownership evidence before an ADR can
select an answer.
