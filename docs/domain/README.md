# CAPLAB domain model

This directory describes the repository's domain language and its integration
boundary with Pincite.

## Authority and artifact map

| Artifact | Authority |
|---|---|
| [`../../ubiquitous_language.md`](../../ubiquitous_language.md) | Canonical assertion, evaluation, and decision meanings |
| [`UBIQUITOUS_LANGUAGE.md`](UBIQUITOUS_LANGUAGE.md) | Uppercase discovery entrypoint; no duplicate definitions |
| [`context-map.md`](context-map.md) | Decided CAPLAB/Pincite boundary and relationship |
| [`../decisions/`](../decisions/README.md) | Selected architectural choices and rationale |
| [`../product/`](../product/README.md) | Product specifications and implementation plans |
| [`../../pincite-dependency.json`](../../pincite-dependency.json) | Exact external Pincite release contract |

Explicit owner instructions and accepted repository contracts precede these
artifacts. Evaluation findings do not rewrite a context boundary or Pincite
dependency without a separately authorized decision.

## Working rules

- Keep Pincite corpus and doctrine provenance intact when CAPLAB records an
  observation about them.
- Record boundary changes in an ADR; directory layout alone is not authority.
- Keep model screening and mechanical grading separate from human adjudication.
- Do not promote study-local evidence into a broader capability claim without
  its declared promotion gate.
- Do not let CAPLAB evaluation output rewrite Pincite doctrine silently.
