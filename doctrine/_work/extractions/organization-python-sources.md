# Organization and Python Sources: Evidence Extraction

Status: complete source-lane extraction for synthesis. This is an evidence ledger, not a book summary, and neither source is normative by reputation alone.

## Scope, source IDs, and locator convention

The converted Markdown for both assigned sources was inspected across every chapter file, including front matter, dividers, appendices, indexes, and colophons. Reference-only and structural files remain in the coverage ledger but do not independently support actionable doctrine.

- `SEAG` — *Software Engineering at Google: Lessons Learned from Programming Over Time* (Titus Winters, Tom Manshreck, and Hyrum Wright, first edition).
  - `SEAG_ROOT = books/dokumen-pub-software-engineering-at-google-lessons-learned-from-programming-over-time-1nbsped-1492082791-9781492082798`
- `APWP` — *Architecture Patterns with Python: Enabling Test-Driven Development, Domain-Driven Design, and Event-Driven Microservices* (Harry Percival and Bob Gregory, first edition).
  - `APWP_ROOT = books/architecture-patterns-with-python`

Every citation uses `books/<slug>/chapters/<file>.md :: <Exact Heading>`. Each selected heading was verified verbatim and carries `role: section` in its tracked section map. Embedded headings are not used as locators; when an embedded subsection contributes, it remains inside the bounded cited section.

## Complete chapter coverage ledger

### SEAG coverage (38/38 files)

| Path | Disposition | Themes |
|---|---|---|
| `SEAG_ROOT/chapters/001-o-reilly.md` | reference-only | Title, publication data, curator attribution, and catalog description. |
| `SEAG_ROOT/chapters/002-table-of-contents.md` | reference-only | Navigation and printed chapter and section inventory. |
| `SEAG_ROOT/chapters/003-foreword.md` | reference-only | External framing of Google practices and their limits outside Google. |
| `SEAG_ROOT/chapters/004-preface.md` | reference-only | Source thesis, time-scale-tradeoff framing, scope, and explicit limitations. |
| `SEAG_ROOT/chapters/005-acknowledgments.md` | reference-only | Contributors, reviewers, and acknowledgments. |
| `SEAG_ROOT/chapters/006-part-i-thesis.md` | structural | Part I divider. |
| `SEAG_ROOT/chapters/007-chapter-1-what-is-software-engineering.md` | substantive | Software over time; scale; Hyrum law; scalable policy; tradeoffs; decision inputs. |
| `SEAG_ROOT/chapters/008-part-ii.md` | structural | Part II culture divider. |
| `SEAG_ROOT/chapters/009-chapter-2-how-to-work-well-on-teams.md` | substantive | Collaborative visibility, team trust, early feedback, bus factor, and blameless learning. |
| `SEAG_ROOT/chapters/010-chapter-3-knowledge-sharing.md` | substantive | Psychological safety, mentorship, canonical information, documentation, code, and organizational learning. |
| `SEAG_ROOT/chapters/011-chapter-4-engineering-for-equity.md` | substantive | Bias, diversity, inclusive product outcomes, process challenges, and responsible release choices. |
| `SEAG_ROOT/chapters/012-chapter-5-how-to-lead-a-team.md` | substantive | Engineering leadership roles, servant leadership, management antipatterns, delegation, and goals. |
| `SEAG_ROOT/chapters/013-chapter-6-leading-at-scale.md` | substantive | Decision tradeoffs, delegation, self-sustaining teams, scaling work, and leadership attention. |
| `SEAG_ROOT/chapters/014-chapter-7-measuring-engineering-productivity.md` | substantive | Measurement triage, goals-signals-metrics, mixed methods, metric validation, decision ownership, and action. |
| `SEAG_ROOT/chapters/015-part-iii.md` | structural | Part III processes divider. |
| `SEAG_ROOT/chapters/016-chapter-8-style-guides-and-rules.md` | substantive | Earned rules, readability, consistency hierarchy, ecosystem conventions, automation, and exceptions. |
| `SEAG_ROOT/chapters/017-chapter-9-code-review.md` | substantive | Review flow, code liability, correctness, comprehension, small changes, review types, and automation. |
| `SEAG_ROOT/chapters/018-chapter-10-documentation.md` | substantive | Documentation audiences and forms, ownership, canonical sources, review, freshness, and deprecation. |
| `SEAG_ROOT/chapters/019-chapter-11-testing-overview.md` | substantive | Test purpose, sizes and scopes, failure testing, coverage limits, flaky-test cost, and test culture. |
| `SEAG_ROOT/chapters/020-chapter-12-unit-testing.md` | substantive | Maintainable tests, public APIs, state versus interaction, behavior focus, clarity, and DAMP sharing. |
| `SEAG_ROOT/chapters/021-chapter-13-test-doubles.md` | substantive | Double fidelity, seams, fakes, stubs, interaction tests, realism, state testing, and overspecification. |
| `SEAG_ROOT/chapters/022-chapter-14-larger-testing.md` | substantive | Unit-test gaps, fidelity, hermeticity, test data, load and configuration, ownership, and workflow. |
| `SEAG_ROOT/chapters/023-chapter-15-deprecation.md` | substantive | Deprecation motives, advisory and compulsory forms, warnings, ownership, milestones, and tooling. |
| `SEAG_ROOT/chapters/024-part-iv.md` | structural | Part IV tools divider. |
| `SEAG_ROOT/chapters/025-chapter-16-version-control-and-branch-management.md` | substantive | Version-control authority, source of truth, branch models, one-version practice, and monorepos. |
| `SEAG_ROOT/chapters/026-chapter-17-code-search.md` | substantive | Repository-scale code search, browsing workflows, indexing, ranking, latency, completeness, and trust. |
| `SEAG_ROOT/chapters/027-chapter-18-build-systems-and-build-philosophy.md` | substantive | Dependency graphs, declarative artifacts, hermetic builds, reproducibility, distribution, and module visibility. |
| `SEAG_ROOT/chapters/028-chapter-19-critique-google-s-code-review-tool.md` | substantive | Review-tool workflow, communication, approvals, history, trust, and integration with analysis. |
| `SEAG_ROOT/chapters/029-chapter-20-static-analysis.md` | substantive | Static-analysis scalability, developer usability, workflow integration, feedback, and suggested fixes. |
| `SEAG_ROOT/chapters/030-chapter-21-dependency-management.md` | substantive | Import costs, compatibility promises, upgrade ownership, semantic versioning, and provider-consumer obligations. |
| `SEAG_ROOT/chapters/031-chapter-22-large-scale-changes.md` | substantive | Large-scale migration authorization, generation, sharding, testing, review, submission, and cleanup. |
| `SEAG_ROOT/chapters/032-chapter-23-continuous-integration.md` | substantive | Fast feedback, continuous build and testing, hermeticity, configuration, flakiness, and failure management. |
| `SEAG_ROOT/chapters/033-chapter-24-continuous-delivery.md` | substantive | Release trains, feature flags, incremental deployment, evidence, discipline, and team-scale release pressure. |
| `SEAG_ROOT/chapters/034-chapter-25-compute-as-a-service.md` | substantive | Compute automation, containers, multitenancy, state, failure, service connection, and abstraction tradeoffs. |
| `SEAG_ROOT/chapters/035-part-v-conclusion.md` | structural | Part V conclusion divider. |
| `SEAG_ROOT/chapters/036-afterword.md` | reference-only | Closing social-responsibility and future-looking framing. |
| `SEAG_ROOT/chapters/037-index.md` | reference-only | Back-of-book index and author biographies. |
| `SEAG_ROOT/chapters/038-colophon.md` | reference-only | Colophon and publisher material. |

### APWP coverage (29/29 files)

| Path | Disposition | Themes |
|---|---|---|
| `APWP_ROOT/chapters/001-o-reilly.md` | reference-only | Title, table of contents, publication data, and revision history. |
| `APWP_ROOT/chapters/002-preface.md` | reference-only | Audience, source scope, TDD-DDD-event framing, examples, and conventions. |
| `APWP_ROOT/chapters/003-acknowledgments.md` | reference-only | Reviewers and acknowledgments. |
| `APWP_ROOT/chapters/004-introduction.md` | substantive | Encapsulation, abstractions, layering, dependency inversion, and a domain-model center. |
| `APWP_ROOT/chapters/005-part-i-building-an-architecture-to-support-domain-modeling.md` | structural | Part I divider and roadmap. |
| `APWP_ROOT/chapters/006-chapter-1-domain-modeling.md` | substantive | Domain language, executable examples, entities, value objects, domain services, idiomatic Python, and domain failures. |
| `APWP_ROOT/chapters/007-chapter-2-repository-pattern.md` | substantive | Persistence isolation, dependency inversion, repository semantics, ports and adapters, fakes, and abstraction cost. |
| `APWP_ROOT/chapters/008-chapter-3-a-brief-interlude-on-coupling-and-abstractions.md` | substantive | Coupling, responsibility discovery, policy-mechanism separation, dependency injection, fakes, and classical versus London testing. |
| `APWP_ROOT/chapters/009-chapter-4-our-first-use-case-flask-api-and-service-layer.md` | substantive | Entrypoints, orchestration versus domain policy, service layer, end-to-end and service tests, and placement. |
| `APWP_ROOT/chapters/010-chapter-5-tdd-in-high-gear-and-low-gear.md` | substantive | Test pyramid, design-feedback versus coupling, service and domain test levels, and end-to-end coverage. |
| `APWP_ROOT/chapters/011-chapter-6-unit-of-work-pattern.md` | substantive | Transaction ownership, context-managed cleanup, explicit commit, default rollback, repositories, and atomic operations. |
| `APWP_ROOT/chapters/012-chapter-7-aggregates-and-consistency-boundaries.md` | substantive | Invariants, concurrency, consistency boundaries, aggregate choice, optimistic locking, isolation, and performance. |
| `APWP_ROOT/chapters/013-part-i-recap.md` | reference-only | Part I pattern recap and summary tables. |
| `APWP_ROOT/chapters/014-part-ii-event-driven-architecture.md` | structural | Part II event-driven architecture divider. |
| `APWP_ROOT/chapters/015-chapter-8-events-and-the-message-bus.md` | substantive | Domain events, event recording, message-bus dispatch, handlers, and responsibility separation. |
| `APWP_ROOT/chapters/016-chapter-9-going-to-town-on-the-message-bus.md` | substantive | Message-handler architecture, event interfaces, unit-of-work event collection, and handler testing. |
| `APWP_ROOT/chapters/017-chapter-10-commands-and-command-handler.md` | substantive | Commands versus events, intent versus fact, recipients, and distinct failure behavior. |
| `APWP_ROOT/chapters/018-chapter-11-event-driven-architecture-using-events-to-integrate-microservices.md` | substantive | Distributed coupling, partial failure, temporal decoupling, asynchronous integration, adapters, and end-to-end tests. |
| `APWP_ROOT/chapters/019-chapter-12-command-query-responsibility-segregation-cqrs.md` | substantive | Write-side domain rules, read models, consistency, query representations, rebuilds, and performance. |
| `APWP_ROOT/chapters/020-chapter-13-dependency-injection-and-bootstrapping.md` | substantive | Explicit dependencies, manual injection, composition roots, entrypoint bootstrapping, adapters, and tests. |
| `APWP_ROOT/chapters/021-epilogue.md` | substantive | Incremental legacy separation, aggregate and context discovery, event interception, strangler migration, and reliability warnings. |
| `APWP_ROOT/chapters/022-appendix-a-summary-diagram-and-table.md` | reference-only | Architecture diagram and component responsibility table. |
| `APWP_ROOT/chapters/023-appendix-b-a-template-project-structure.md` | substantive | Project layout, environment configuration, containers, packaging, commands, and test structure. |
| `APWP_ROOT/chapters/024-appendix-c-swapping-out-the-infrastructure-do-everything-with-csvs.md` | substantive | Infrastructure substitution proof using CSV repository and unit-of-work adapters. |
| `APWP_ROOT/chapters/025-appendix-d-repository-and-unit-of-work-patterns-with-django.md` | substantive | Django repository and unit-of-work adaptation, framework coupling, views as adapters, and incremental options. |
| `APWP_ROOT/chapters/026-appendix-e-validation.md` | substantive | Syntax, semantics, pragmatics, tolerant readers, edge validation, preconditions, and idempotence. |
| `APWP_ROOT/chapters/027-index.md` | reference-only | Back-of-book subject index. |
| `APWP_ROOT/chapters/028-about-the-authors.md` | reference-only | Author biographies. |
| `APWP_ROOT/chapters/029-colophon.md` | reference-only | Colophon and cover information. |

## Evidence synthesis

### SEAG: compatibility, evidence, review, and durable process

SEAG contributes most usefully where its Google-specific experience sharpens existing technical doctrine: observable behavior becomes compatibility pressure over time; measurement is worthwhile only when both outcomes can change an owned decision; behavioral metrics need validation against the experience they claim to measure; small review slices improve comprehension and failure localization; coverage is not adequacy; and larger tests cover risks isolated unit tests cannot see. Its documentation, dependency-adoption, deprecation, hermetic-build, and large-scale-change sections support durable lifecycle records. Organization and leadership chapters were read and covered but were not converted into generic agent-management doctrine.

The chapter-24 claim that microservices or a rewrite are the best-return answer to costly team-scale monolith releases is retained only as a tension against the existing distribution gate and monolith-versus-services conflict. It is not an endorsed decision rule.

### APWP: domain, architecture, and testing evidence

APWP supplies executable examples for domain language, value and entity identity, domain services, repositories, aggregate consistency, bounded contexts, service-layer orchestration, and validation placement. Its architecture material makes indirection costs explicit: repository and unit-of-work patterns are earned by policy isolation, substitution, test, or migration value, while the Django appendix directly supports retaining framework coupling when those benefits do not repay the cost.

Its testing evidence is explicitly classical: state-oriented fakes and high-level behavior checks are preferred over interaction-heavy mocks. That evidence corroborates one side of `conflict-classical-vs-london-test-isolation`; it does not erase the London or legacy-seam position. Event, command, asynchronous integration, and CQRS material remains conditional on existing synchrony, distribution, and representation conflicts.

## Deliberately not extracted

- SEAG leadership, motivation, office practice, equity-process, code-search UI, and Google-tool implementation details were covered but not promoted into generic agent doctrine without a tighter engineering decision rule.
- Numerical thresholds, Google fleet sizes, review latency targets, and productivity figures remain illustrations rather than portable gates.
- APWP framework syntax, ORM mappings, broker code, project trees, and OCR-reconstructed examples remain implementation illustrations; prose sections support the doctrine candidates.
- No technique files are proposed. Mechanism material is folded into concept records or existing conflicts.

## Conversion and source limitations

Both PDFs were airlock-DANGEROUS and were converted only from CDR-CLEAN 150-DPI raster derivatives by Marker 1.10.2 on peecee, with Surya OCR on every page and no LLM or fallback. SEAG retains 9 damaged-code, 125 unresolved-table, 9 duplicate-heading, and one low-confidence-boundary finding. APWP retains 20 damaged-code, 32 unresolved-table, 20 duplicate-heading, and one low-confidence-boundary finding. Exact prose locators and section roles were verified; code, tables, and numerical details require comparison with source images before fidelity-sensitive use.
