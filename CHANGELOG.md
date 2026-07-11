# Changelog

This project does not yet publish numbered releases. Dated entries record notable repository changes; work not yet committed remains under `Unreleased`.

## Unreleased

### Added

- Added the deterministic evidence-packet assembler (`doctrine/tools/assemble_packet.py`): applies the routing-index retrieval contract for a role, task, question, and optional repository signals, languages, and risk class, and emits packets validated against `doctrine/runtime/evidence-packet.schema.json`.
- Added the claim-to-source entailment screening harness (`doctrine/tools/entailment_eval.py`) with a 12-judgment pilot recorded under `doctrine/evaluations/entailment/`; verdicts are model-judged screening evidence for human audit, not verification.
- Expanded root documentation for corpus conversion, doctrine contracts, evaluation fixtures, assertion discipline, and integrity boundaries.
- Added author attribution to the root source-book catalog.
- Added this changelog.

### Changed

- Moved the original PDF and EPUB inputs from the repository root into `sources/` and updated conversion discovery accordingly.
- Added repository-relative input paths and source SHA-256 values to provenance records without reconverting chapter content.

## 2026-07-10

### Added

- Added portable assertion, evidence-packet, decision-receipt, dependency-manifest, scenario, and scenario-result contracts, with replayable authority and dependency-impact fixtures (`ac0f977`).
- Added repository agent instructions that require the canonical ubiquitous language (`39928de`).
- Defined observation, inference, recommendation, decision, authorization, execution, verification, and acceptance as distinct repository terms (`51d2b23`).
- Preserved the converged doctrine recommendation and documented the operationalization sequence from source spans through evaluated outcomes (`32968fe`, `f893a41`).
- Documented the root-level source book catalog (`f647db3`).
- Added the initial raw Markdown conversion of *Refactoring: Improving the Design of Existing Code* (`36b7735`).
