# Changelog

This project does not yet publish numbered releases. Dated entries record
notable repository changes; completed work not yet assigned to a dated release
remains under `Unreleased`, whether or not it has been committed.

## Unreleased

### Added

- Added a repository-native remediation plan covering runtime authority,
  routing, graph semantics, exact provenance, conversion reproducibility,
  evaluation identity, corpus quality, and calibration gates.
- Added exact source and chapter release gates: all source binaries,
  `source.json` records, extraction ledgers, 331 chapter files, hashes, titles,
  and source locators are now validated as part of `make check`.
- Added a generated chapter-coverage manifest and separated non-semantic routing
  adjacency from the provenance-bearing canonical doctrine graph.
- Added canonical bibliographic metadata for all 11 sources, including creator
  roles, edition evidence, and direct-versus-derived provenance.
- Added typed evidence records and version 2 assertion, receipt, scenario, and
  evidence-packet contracts.
- Added continuous-integration coverage for the complete conversion and doctrine
  release gate, with pinned major-version ranges for its Python dependencies.
- Added a deterministic 99-candidate human calibration queue spanning sources,
  graph and support relationships, roles, contextual risks, authority
  transitions, abstention, insufficient evidence, and no-change outcomes. All
  candidates remain explicitly pending human adjudication.
- Added the deterministic evidence-packet assembler (`doctrine/tools/assemble_packet.py`): applies the routing-index retrieval contract for a role, task, question, and optional repository signals, languages, and risk class, and emits packets validated against `doctrine/runtime/evidence-packet.schema.json`.
- Added the claim-to-source entailment screening harness (`doctrine/tools/entailment_eval.py`) with a 12-judgment pilot recorded under `doctrine/evaluations/entailment/`; verdicts are model-judged screening evidence for human audit, not verification.
- Added a `--model` flag to the entailment harness so multi-model OpenAI-compatible servers (ollama) route to the requested judge model; recorded model provenance now prefers the requested model when the server lists it.
- Expanded root documentation for corpus conversion, doctrine contracts, evaluation fixtures, assertion discipline, and integrity boundaries.
- Added author attribution to the root source-book catalog.
- Added this changelog.

### Changed

- Evidence packets now use canonical role and task vocabularies, keep activation
  signals separate from typed evidence, preserve claim-level provenance, close
  prerequisite chains, record explainable question-sensitive selection, enforce
  a retrieval budget, and content-address the doctrine, retriever, and packet.
- The default evidence packet is compact and bounded; full derived audit views
  are available explicitly rather than repeated in every agent-facing packet.
- Assertion and receipt validation now enforces legal authority lineage,
  evidence resolution, scope containment, ownership, verification criteria,
  acceptance ownership and verified lineage, and lifecycle reopening
  conditions.
- Every material conflict now carries position-specific support and provenance;
  all conflicts and source formulations project into the canonical graph while
  preserving derived inference and local-policy distinctions.
- Converter cache reuse now depends on converter, helper, option, environment,
  platform, and pipeline-stage identity; legacy cache records are treated as
  unverified until reconverted, and `--fresh-converter` bypasses reuse.
- Entailment judgments now bind the complete claim, locator, section content,
  prompt, model, endpoint, and sampler configuration; ambiguous headings and
  truncated sections become explicit insufficient-context results.
- Corroboration now distinguishes additional within-source support from
  independent cross-source support; `entailment-prompt/3` prevents judgments
  using the earlier relationship wording from being silently reused.
- Generated catalogs now distinguish conversion, integrity, content quality,
  and human-review status and expose complete severity and citation-impact
  counts at the finest available warning locator (currently chapter-level).
  `--catalog-only` regenerates them without invoking document converters.
- Numeric rubric thresholds are explicitly provisional until calibrated against
  human-adjudicated examples.
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
