# Data Systems Sources: Evidence Extraction

Status: complete source-lane extraction for synthesis. This is not a book summary, and neither source is treated as normative by reputation alone. Observations remain source-attributed; the records below are recommendations for integration, not decisions or authorization.

## Scope, source IDs, and locator convention

The converted Markdown for both assigned sources was inspected in full, including front matter, substantive chapters, glossary, index, biographies, colophon, and the chapter-3 extract's publication matter.

- `DDIA` — *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*, Second Edition (Martin Kleppmann and Chris Riccomini, first released 2026-02-18).
  - `DDIA_ROOT = books/dokumen-pub-designing-data-intensive-applications-the-big-ideas-behind-reliable-scalable-and-maintainable-systems-2`
- `ADP` — *API Design Patterns*, Chapter 3 extract: “Naming” (JJ Geewax, 2021).
  - `ADP_ROOT = books/bookshelf-ch-three-api-design-patterns`

Every doctrine locator uses the full repository path `books/<slug>/chapters/<file>.md :: <Exact Heading>`. All 25 candidate locators were verified verbatim in Markdown and against the corresponding tracked section map with `role: section`. Conversion-flattened embedded headings are never used as locators; their material is attributed only to the enclosing citable section and each contribution is narrower than that section.

## Complete chapter coverage ledger

### DDIA coverage (22/22 files)

| Path | Converted title | Data-systems themes or disposition |
|---|---|---|
| `DDIA_ROOT/chapters/001-2nd-edition.md` | 2nd Edition | Structural — edition and title matter; praise and revision history. |
| `DDIA_ROOT/chapters/002-table-of-contents.md` | Table of Contents | Structural — book navigation; chapter and section inventory. |
| `DDIA_ROOT/chapters/003-preface.md` | Preface | Structural — intended audience; second-edition scope; conventions. |
| `DDIA_ROOT/chapters/004-acknowledgments.md` | Acknowledgments | Structural — acknowledgments. |
| `DDIA_ROOT/chapters/005-chapter-1-trade-offs-in-data-systems-architecture.md` | Chapter 1: Trade-Offs in Data Systems Architecture | Substantive — contextual architecture trade-offs; systems of record and derived data; distribution and cloud choices; data systems and society. |
| `DDIA_ROOT/chapters/006-chapter-2-defining-nonfunctional-requirements.md` | Chapter 2: Defining Nonfunctional Requirements | Substantive — measurable nonfunctional requirements; load and scalability; latency distributions; fault tolerance and maintainability. |
| `DDIA_ROOT/chapters/007-chapter-3-data-models-and-query-languages.md` | Chapter 3: Data Models and Query Languages | Substantive — data-model selection; normalization and denormalization; relational document and graph models; event sourcing and analytical models. |
| `DDIA_ROOT/chapters/008-chapter-4-storage-and-retrieval.md` | Chapter 4: Storage and Retrieval | Substantive — storage-engine trade-offs; indexes as derived structures; analytical storage; full-text and vector retrieval. |
| `DDIA_ROOT/chapters/009-chapter-5-encoding-and-evolution.md` | Chapter 5: Encoding and Evolution | Substantive — schema evolution and compatibility; serialization; remote dataflow; durable workflows and events. |
| `DDIA_ROOT/chapters/010-chapter-6-replication.md` | Chapter 6: Replication | Substantive — replication guarantees; replication lag; multi-leader and leaderless operation; causality and conflict resolution. |
| `DDIA_ROOT/chapters/011-chapter-7-sharding.md` | Chapter 7: Sharding | Substantive — sharding evidence and costs; partition-key selection; hot spots and rebalancing; secondary indexes. |
| `DDIA_ROOT/chapters/012-chapter-8-transactions.md` | Chapter 8: Transactions | Substantive — transaction semantics; isolation anomalies; invariant preservation; distributed transactions and message processing. |
| `DDIA_ROOT/chapters/013-chapter-9-the-trouble-with-distributed-systems.md` | Chapter 9: The Trouble with Distributed Systems | Substantive — partial failure; network and clock uncertainty; leases and fencing; system models and verification. |
| `DDIA_ROOT/chapters/014-chapter-10-consistency-and-consensus.md` | Chapter 10: Consistency and Consensus | Substantive — linearizability and serializability; logical clocks; consensus; coordination services. |
| `DDIA_ROOT/chapters/015-chapter-11-batch-processing.md` | Chapter 11: Batch Processing | Substantive — reproducible batch derivation; distributed orchestration; dataflow and shuffle; serving derived data. |
| `DDIA_ROOT/chapters/016-chapter-12-stream-processing.md` | Chapter 12: Stream Processing | Substantive — event transport and durable logs; change data capture; event-time semantics; stream joins and fault tolerance. |
| `DDIA_ROOT/chapters/017-chapter-13-a-philosophy-of-streaming-systems.md` | Chapter 13: A Philosophy of Streaming Systems | Substantive — data integration and derivation; end-to-end correctness; constraint enforcement; auditability and integrity. |
| `DDIA_ROOT/chapters/018-chapter-14-doing-the-right-thing.md` | Chapter 14: Doing the Right Thing | Substantive — ethical consequences; bias and accountability; privacy and consent; data minimization. |
| `DDIA_ROOT/chapters/019-glossary.md` | Glossary | Reference Only — data-systems terminology; cross-references to substantive chapters. |
| `DDIA_ROOT/chapters/020-index.md` | Index | Reference Only — alphabetical topic index; product and concept references. |
| `DDIA_ROOT/chapters/021-about-the-authors.md` | About the Authors | Structural — author biographies. |
| `DDIA_ROOT/chapters/022-colophon.md` | Colophon | Structural — cover and production credits; publisher promotion. |

### ADP coverage (2/2 files)

| Path | Converted title | API-naming themes or disposition |
|---|---|---|
| `ADP_ROOT/chapters/001-api-design-patterns.md` | API Design Patterns | Structural — title and author matter; copyright and publication metadata. |
| `ADP_ROOT/chapters/002-chapter-3-naming.md` | Chapter 3: Naming | Substantive — durable public names; expressive simple predictable naming; context and conventions; units and rich data types. |

## Per-theme evidence notes

### Authority, representation, and workload fit

DDIA2 distinguishes authoritative systems of record from reproducible derived data, then applies that distinction to denormalized state, indexes, CDC, batch outputs, and stream-maintained views. Its model, index, scaling, sharding, and partition-key recommendations are conditional on measured relationships, access paths, load dimensions, skew, locality, and failure consequences rather than product categories or fashion.

### Compatibility, consistency, and distributed failure

Schema records enable predeployment forward- and backward-compatibility checks and minimize concurrently supported formats; replication records separate durability, latency, and availability; transaction and consistency records reject overloaded product labels in favor of operation-scoped guarantees. Causality, process pauses, leases, and unknown outcomes ground the refinements to event semantics, integration-point distrust, and explicit invariants. Fencing and end-to-end request identity are retained as concepts rather than unvalidated technique records.

### Reproducible derivation, temporal semantics, and auditability

Batch processing contributes immutable-input, side-effect-bounded recomputation. CDC contributes one ordering authority for downstream state. Stream processing contributes event-time, lateness, window, state, and replay semantics. The end-to-end argument contributes durable request identity and full-path integrity checks that component guarantees cannot supply alone.

### Responsible data lifecycle

Chapter 14's ethical discussion is retained as normative practitioner argument, not as a repository decision. The extracted lifecycle rule is deliberately narrow: declare the purpose for sensitive-data collection, minimize collection to what that purpose needs, bound retention, and purge data when it is no longer needed for that declared purpose. Current legal applicability must be verified independently.

### API naming excerpt

ADPCH3 is explicitly limited to chapter 3. Section 3.1 refines compatibility migration by showing why public names cannot be changed atomically across unknown private consumers. Section 3.5 refines semantic naming by requiring units or richer types where a primitive field name would collapse incompatible quantities.

### Deliberately not extracted

DDIA2 product catalogs, current service comparisons, hardware capacities, pricing, framework APIs, algorithm implementation details, chapter summaries, glossary definitions, and index entries remain source context rather than timeless doctrine. ADPCH3 language choice, American-English preference, casing syntax, grammar catalog, exercises, and case-study particulars remain contextual implementation guidance rather than separate records.

### Source limitations carried into the corpus map

DDIA2 is edition- and time-bounded to its second-edition 2025-2026 context; current product, cloud, hardware, price, legal, regulatory, and security claims require primary-source verification. Its chapter 13 philosophy is deliberately opinionated and chapter 14 is normative. Marker used Surya OCR on all 673 pages, and visible conversion artifacts make the glossary and index reference-only.

ADPCH3 is a 17-page chapter-3 extract, not the complete 2021 book. No inference may be drawn from absent chapters. Marker used Surya OCR on all pages and some code-listing layout is damaged. Single-source support from either source is capped at strong or contextual confidence.
