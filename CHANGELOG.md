# Changelog

This project does not yet publish numbered releases. Dated entries record
notable repository changes; completed work not yet assigned to a dated release
remains under `Unreleased`, whether or not it has been committed.

## Unreleased

### Added

- Added the BOOKS-1 compiled doctrine retrieval path: a deterministic Python
  compiler projects authoritative YAML into a checked-in, checksummed SQLite
  read model; a CGO-free Go executable assembles version 2 evidence packets;
  and Python-oracle parity, static-build, stale-index, corruption, Unicode,
  CLI-failure, and latency gates cover the cutover. The retained Python
  assembler remains the one-release fallback.
- Added a repository DDD documentation spine: expanded canonical domain
  vocabulary, an uppercase discovery entrypoint, a candidate context map, an
  ADR index and template, and `adr-0001` governing the authority boundaries
  among domain docs, decisions, specifications, plans, and receipts.
- Registered *100 Go Mistakes and How to Avoid Them* (SRC-100GO) and
  *Concurrency in Go* (SRC-CIG) with exact source metadata, contextual
  limitations, a complete 31-chapter extraction ledger, 11 canonical concepts,
  36 provenance-preserving support records (14 on new concepts and 22 refining
  existing concepts), and Go-specific evidence on four preserved conflicts;
  exact doctrine coverage grows from 378 to 409 chapters and the concept
  catalog from 182 to 193 records.
- Registered *Designing Data-Intensive Applications*, Second Edition
  (SRC-DDIA2), and the explicitly scoped *API Design Patterns* chapter-3
  Naming extract (SRC-ADPCH3) as doctrine sources, with complete 24-file
  coverage in a data-systems extraction ledger and edition, time, OCR, and
  excerpt limitations carried into the corpus map.
- Added the data-systems concept catalog with 15 canonical `data-*` records
  carrying 16 source supports after folding denormalization into
  source/derived authority; the catalog covers indexes, schema evolution,
  replication, sharding, partition keys, transactions and consistency,
  fencing, reproducible batch and stream derivation, CDC, event time,
  end-to-end idempotence and integrity auditing, and data minimization.
- Added nine narrowly scoped citations to existing architecture, performance,
  operations, universal, refactoring, and implementation concepts, including
  load-model evidence on `performance-measurable-objective` and
  relational/document-model evidence on `implementation-representation-fit`;
  chapter coverage grows 409 -> 433, registered sources 15 -> 17, and canonical
  concepts 193 -> 208 with no new conflict record.
- Registered *Software Engineering at Google* (SRC-SEAG) and
  *Architecture Patterns with Python* (SRC-APWP) with a complete
  67-chapter extraction ledger, six canonical concepts, and 33
  provenance-preserving support records (six on new concepts and 27
  extending existing concepts); exact doctrine coverage grows from 433
  to 500 chapters, registered sources from 17 to 19, and canonical
  concepts from 208 to 214 while preserved conflicts remain at 29.
- Added eight PDF sources and their chaptered Markdown corpora: *100 Go
  Mistakes and How to Avoid Them*, *API Design Patterns* chapter 3 (an
  explicitly labeled extract), *Architecture Patterns with Python*,
  *Concurrency in Go*, *Designing Data-Intensive Applications* second edition,
  *Release It!* second edition, *Software Engineering at Google*, and *Unit
  Testing: Principles, Practices, and Patterns*.
- Added a mandatory PDF airlock and sandboxed raster CDR path. Every PDF is
  statically classified before Marker; non-clean originals remain unchanged
  while a separately hashed, post-gated pixel-only derivative crosses the
  converter boundary. Provenance records the x-ray, CDR, execution target,
  commands, hashes, and selected input.
- Added an explicit policy-compatible raw-cache migration for already validated
  peecee conversions. It accepts only fallback-free CLEAN or networkless
  CDR-CLEAN inputs, rejects SUSPECT original bytes, and records the bounded
  compatibility decision in per-book provenance.
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
- Added frontier-model second-opinion reviews of the 31 pending screening flags
  (`doctrine/evaluations/entailment/frontier-review.jsonl`, reviewer kind
  `model`), displayed in the adjudication bench beside the local screening
  verdict; 17 of 31 local flags were judged artifacts of section extraction
  truncated by conversion-flattened subsection and callout headings.
- Expanded root documentation for corpus conversion, doctrine contracts, evaluation fixtures, assertion discipline, and integrity boundaries.
- Added author attribution to the root source-book catalog.
- Added a tailnet-local web adjudication bench
  (`doctrine/tools/adjudication_server.py` + `adjudication_ui.html`, systemd
  user unit `doctrine-adjudication`, http://100.85.100.81:8788/): one-item-at-a-time
  human review of the entailment screening flags (evidence quote highlighted
  in the resolved cited section, audits appended to
  `doctrine/evaluations/entailment/human-audit.jsonl`) and the gold queue
  candidates (every reference resolved best-effort with explicit unresolved
  markers, machine screening joined for source-support candidates, dispositions
  appended atomically to `human-dispositions.json` with whole-document schema
  validation followed by builder `--write`/`--check`). Access is limited to
  loopback and the Tailscale CGNAT range by socket peer address; dispositions
  and audits record the human's dictated judgment verbatim.
- Added a repository-native product-document scaffold under `docs/product/`
  with explicit specification and implementation-plan lifecycles, reusable
  templates, and a stable index that keeps proposal, decision, authorization,
  execution, verification, and acceptance distinct.
- Added the selected Doctrine Robustness Laboratory specification, authorized
  pilot plan, versioned offline contracts, strict loader, and deterministic
  `authority-withdrawal` pair. The P2 runner changes one declared authority
  selector and invokes the existing scenario runner for clean and mutant
  branches; later grading and human-adjudication checkpoints remain deferred.
- Added tracked per-book section maps (`doctrine/section-maps/*.yaml`, schema
  `section-map/1`) classifying every chapter heading as a genuine section
  boundary or conversion-flattened embedded content (callouts, captions,
  definition-list items, flattened subsection children), built by
  `doctrine/tools/build_section_map.py --write | --check | --stats`. A
  deterministic rule ladder (chapter title, callout, caption, numbered-book,
  printed-TOC, doctrine-cited) records provenance per heading; the local model
  classifies the remainder as screening evidence; human entries are
  authoritative and preserved verbatim. `--check` enforces book/chapter/heading
  coverage, current chapter hashes, and that every doctrine-cited heading is a
  section.
- Section extraction is now map-aware: embedded headings no longer terminate
  cited sections, and an optional per-heading `depth` expresses genuine nested
  subsections flattened to their parent's markdown level (two such subsections
  are themselves doctrine-cited). Evidence-quote verification normalizes
  conversion artifacts (PDF line-break hyphenation, markdown emphasis and
  escapes, span anchors, curly quotes) and treats ellipses as elisions
  (`entailment-prompt/4`); the judged-section budget rose from 24000 to 60000
  characters. A release-gate oracle requires all 19 artifact-flag evidence
  quotes to be recoverable from the re-bounded sections.
- Registered Release It! (2nd ed., SRC-RI) and Unit Testing: Principles,
  Practices, and Patterns (SRC-UT) as doctrine sources via a five-reader,
  two-integrator extraction campaign: 41 new concepts (25 operations-*, 16
  testing-*), 25 new citations on 16 existing concepts, 12 costed stability
  techniques, 4 new preserved conflicts (fault-tolerance-vs-let-it-crash,
  live-control-vs-immutable-replacement, efficiency-vs-resilience-margin,
  classical-vs-london-test-isolation), and the prohibit-coverage-number-target
  prohibition. Chapter coverage grows 331 -> 378 with two complete extraction
  ledgers; the graph grows to 182 concepts; the gold queue to 101 candidates.
  New-citation entailment screening is recorded separately.
- Added this changelog.

### Changed

- Chapter-boundary recovery now uses noisy printed-contents sequences and
  repeated numbered body-section patterns to recover logical chapters whose
  OCR headings omit the word or number `Chapter`.
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
