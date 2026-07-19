# Architecture and Domain Sources: Evidence Extraction

Status: complete source-lane extraction for synthesis. This is not a book summary and does not treat any source as normative by prestige.

## Scope, source IDs, and locator convention

The complete converted Markdown chapter sets were inspected for the three assigned sources, including front matter, part dividers, appendices, self-assessment material, indexes, and references. Index and publication-only files are recorded in the coverage ledger but do not independently support actionable doctrine.

- `CA` — *Clean Architecture: A Craftsman's Guide to Software Structure and Design*.
  - `CA_ROOT = books/clean-architecture-a-craftsman-guide-to-software-structure-and-design`
- `FSA` — *Fundamentals of Software Architecture: An Engineering Approach*.
  - `FSA_ROOT = books/oreilly-fundamentals-of-software-architecture-2020-1`
- `DDD` — *Domain-Driven Design: Tackling Complexity in the Heart of Software*.
  - `DDD_ROOT = books/domain-driven-design-tackling-complexity-in-the-heart-of-software-eric-evans`

Every locator below is `SOURCE_ID: chapters/<file> :: <Markdown heading>`. It is therefore relative to the declared source root and resolves to an exact converted file and heading. Claims are paraphrases. Where a claim appears in only one source, it remains source advocacy unless independently supported or operationally bounded.

## Chapter coverage ledger

### CA coverage (48/48 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `CA_ROOT/chapters/001-clean-architecture.md` | Clean Architecture | Edition metadata; declared audience; no independent doctrine. |
| `CA_ROOT/chapters/002-contents.md` | Contents | Source navigation and heading cross-check. |
| `CA_ROOT/chapters/003-foreword.md` | Foreword | Architecture as costly-to-change decisions; architecture as hypothesis tested by implementation and measurement; incomplete knowledge. |
| `CA_ROOT/chapters/004-preface.md` | Preface | Author's claim of architecture-rule continuity; broad experiential basis; important universality caveat. |
| `CA_ROOT/chapters/005-acknowledgments.md` | Acknowledgments | Publication-only. |
| `CA_ROOT/chapters/006-about-the-author.md` | About the Author | Author background and source-bias context. |
| `CA_ROOT/chapters/007-i-introduction.md` | Part I: Introduction | Lifetime change cost, coupling, and maintainability motivation; largely rhetorical. |
| `CA_ROOT/chapters/008-chapter-1-what-is-design-and-architecture.md` | Chapter 1: What Is Design and Architecture? | Design/architecture continuum; lifetime human effort; productivity degradation; rewrite caution. |
| `CA_ROOT/chapters/009-chapter-2-a-tale-of-two-values.md` | Chapter 2: A Tale of Two Values | Behavior versus changeability; structural stewardship; urgency versus importance. |
| `CA_ROOT/chapters/010-ii-starting-with-the-bricks-programming-paradigms.md` | Part II: Programming Paradigms | Code-level disciplines as architecture substrate. |
| `CA_ROOT/chapters/011-chapter-3-paradigm-overview.md` | Chapter 3: Paradigm Overview | Structured, OO, functional disciplines; function, separation, and data management. |
| `CA_ROOT/chapters/012-chapter-4-structured-programming.md` | Chapter 4: Structured Programming | Decomposition; falsifiable testing rather than proof; functional decomposition. |
| `CA_ROOT/chapters/013-chapter-5-object-oriented-programming.md` | Chapter 5: Object-Oriented Programming | Polymorphism, plugin boundaries, source dependency inversion, independent deployment claims. |
| `CA_ROOT/chapters/014-chapter-6-functional-programming.md` | Chapter 6: Functional Programming | Mutability segregation, concurrency risk, event-sourcing advocacy and resource caveats. |
| `CA_ROOT/chapters/015-iii-design-principles.md` | Part III: Design Principles | SOLID scope and claimed goals; module-level context. |
| `CA_ROOT/chapters/016-chapter-7-srp-the-single-responsibility-principle.md` | Chapter 7: SRP | Actor-driven change axes, accidental coupling, merge pressure, facade trade-off. |
| `CA_ROOT/chapters/017-chapter-8-ocp-the-open-closed-principle.md` | Chapter 8: OCP | Extension pressure, change protection hierarchy, directional control, information hiding. |
| `CA_ROOT/chapters/018-chapter-9-lsp-the-liskov-substitution-principle.md` | Chapter 9: LSP | Behavioral substitutability as boundary contract, not inheritance aesthetics. |
| `CA_ROOT/chapters/019-chapter-10-isp-the-interface-segregation-principle.md` | Chapter 10: ISP | Avoiding dependencies on unused capabilities; language and architectural costs. |
| `CA_ROOT/chapters/020-chapter-11-dip-the-dependency-inversion-principle.md` | Chapter 11: DIP | Stable policy abstractions, factories, unavoidable concrete edges. |
| `CA_ROOT/chapters/021-iv-component-principles.md` | Part IV: Component Principles | Part divider. |
| `CA_ROOT/chapters/022-chapter-12-components.md` | Chapter 12: Components | Deployment units and historical linking context. |
| `CA_ROOT/chapters/023-chapter-13-component-cohesion.md` | Chapter 13: Component Cohesion | Release/reuse, common closure, common reuse, unavoidable cohesion tension. |
| `CA_ROOT/chapters/024-chapter-14-component-coupling.md` | Chapter 14: Component Coupling | Acyclic graph, stability, stable abstractions, metrics as indicators rather than gods. |
| `CA_ROOT/chapters/025-v-architecture.md` | Part V: Architecture | Part divider. |
| `CA_ROOT/chapters/026-chapter-15-what-is-architecture.md` | Chapter 15: What Is Architecture? | Development/deployment/operation/maintenance drivers; option preservation; policy/detail separation; team-size context. |
| `CA_ROOT/chapters/027-chapter-16-independence.md` | Chapter 16: Independence | Use-case separation; decoupling modes; deployment versus source boundaries; duplication nuance. |
| `CA_ROOT/chapters/028-chapter-17-boundaries-drawing-lines.md` | Chapter 17: Boundaries: Drawing Lines | Boundary timing, plugin direction, policy versus volatile detail, delayed commitment. |
| `CA_ROOT/chapters/029-chapter-18-boundary-anatomy.md` | Chapter 18: Boundary Anatomy | In-process, component, thread, process, and service boundary costs. |
| `CA_ROOT/chapters/030-chapter-19-policy-and-level.md` | Chapter 19: Policy and Level | Policy level as distance from inputs/outputs, not source placement. |
| `CA_ROOT/chapters/031-chapter-20-business-rules.md` | Chapter 20: Business Rules | Entity and use-case rules; request/response models; business-policy isolation. |
| `CA_ROOT/chapters/032-chapter-21-screaming-architecture.md` | Chapter 21: Screaming Architecture | Repository structure should reveal purpose; frameworks are tools; testability. |
| `CA_ROOT/chapters/033-chapter-22-the-clean-architecture.md` | Chapter 22: The Clean Architecture | Policy/detail layers, inward dependency rule, adapters, boundary data forms. |
| `CA_ROOT/chapters/034-chapter-23-presenters-and-humble-objects.md` | Chapter 23: Presenters and Humble Objects | Separate hard-to-test adapters from testable policy; gateways, mappers, listeners. |
| `CA_ROOT/chapters/035-chapter-24-partial-boundaries.md` | Chapter 24: Partial Boundaries | Full-boundary cost, partial placeholders, erosion risk, facade and one-way trade-offs. |
| `CA_ROOT/chapters/036-chapter-25-layers-and-boundaries.md` | Chapter 25: Layers and Boundaries | Multiple change axes, boundary inflection point, YAGNI tension, continuous watchfulness. |
| `CA_ROOT/chapters/037-chapter-26-the-main-component.md` | Chapter 26: The Main Component | Composition root; framework and configuration containment. |
| `CA_ROOT/chapters/038-chapter-27-services-great-and-small.md` | Chapter 27: Services: Great and Small | Service decoupling fallacies; cross-cutting change; component boundaries can remain in-process. |
| `CA_ROOT/chapters/039-chapter-28-the-test-boundary.md` | Chapter 28: The Test Boundary | Tests as clients/components; structural coupling; stable testing API and security concern. |
| `CA_ROOT/chapters/040-chapter-29-clean-embedded-architecture.md` | Chapter 29: Clean Embedded Architecture | Hardware/OS isolation, HAL, target-independent testability, conditional compilation control. |
| `CA_ROOT/chapters/041-vi-details.md` | Part VI: Details | Part divider. |
| `CA_ROOT/chapters/042-chapter-30-the-database-is-a-detail.md` | Chapter 30: The Database Is a Detail | Persistence technology versus data model; overbroad advocacy caveat; performance exceptions. |
| `CA_ROOT/chapters/043-chapter-31-the-web-is-a-detail.md` | Chapter 31: The Web Is a Detail | Delivery mechanism volatility; UI boundary. |
| `CA_ROOT/chapters/044-chapter-32-frameworks-are-details.md` | Chapter 32: Frameworks Are Details | Framework lock-in, asymmetric commitment, isolate and defer adoption. |
| `CA_ROOT/chapters/045-chapter-33-case-study-video-sales.md` | Chapter 33: Case Study: Video Sales | Use-case analysis, component grouping, dependency management example. |
| `CA_ROOT/chapters/046-chapter-34-the-missing-chapter.md` | Chapter 34: The Missing Chapter | Package by layer/feature/component; compile-time enforcement; access control; implementation must realize diagrams. |
| `CA_ROOT/chapters/047-vii-appendix.md` | Appendix A: Architecture Archaeology | Longitudinal anecdotes; overarchitecture failure; premature reusable framework failure; boundaries under old technologies. |
| `CA_ROOT/chapters/048-index.md` | Index | Retrieval aid only; no independent doctrine. |

### FSA coverage (35/35 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `FSA_ROOT/chapters/001-fundamentals-of-software-architecture.md` | Fundamentals of Software Architecture | Edition and positioning metadata; no independent doctrine. |
| `FSA_ROOT/chapters/002-table-of-contents.md` | Table of Contents | Source navigation and heading cross-check. |
| `FSA_ROOT/chapters/003-preface-invalidating-axioms.md` | Preface: Invalidating Axioms | Revalidate architectural axioms against ecosystem capability; engineering rigor and trade-offs. |
| `FSA_ROOT/chapters/004-acknowledgments.md` | Acknowledgments | Publication-only. |
| `FSA_ROOT/chapters/005-chapter-1-introduction.md` | Chapter 1: Introduction | Architecture dimensions, architect expectations, iterative delivery, DevOps/operations/data intersections, trade-off laws. |
| `FSA_ROOT/chapters/006-part-i-foundations.md` | Part I: Foundations | Part divider. |
| `FSA_ROOT/chapters/007-chapter-2-architectural-thinking.md` | Chapter 2: Architectural Thinking | Architect/developer feedback, breadth, stale expertise, business drivers, trade-off analysis, hands-on balance. |
| `FSA_ROOT/chapters/008-chapter-3-modularity.md` | Chapter 3: Modularity | Cohesion/coupling/connascence, static and dynamic coupling, metric limitations, component transition. |
| `FSA_ROOT/chapters/009-chapter-4-architecture-characteristics-defined.md` | Chapter 4: Architecture Characteristics Defined | Structural significance, operational/structural/cross-cutting qualities, ambiguity, least-worst trade-offs. |
| `FSA_ROOT/chapters/010-chapter-5-identifying-architectural-characteristics.md` | Chapter 5: Identifying Architecture Characteristics | Extract explicit/implicit drivers; avoid over-specification; prioritize minimal characteristic set. |
| `FSA_ROOT/chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md` | Chapter 6: Measuring and Governing Architecture Characteristics | Objective definitions, percentiles/budgets, process measures, automated fitness functions and caveats. |
| `FSA_ROOT/chapters/012-chapter-7-scope-of-architecture-characteristics.md` | Chapter 7: Scope of Architecture Characteristics | Architecture quantum, static/dynamic coupling, bounded-context comparison, characteristic scope. |
| `FSA_ROOT/chapters/013-chapter-8-component-based-thinking.md` | Chapter 8: Component-Based Thinking | Technical/domain partitioning, Conway effects, iterative component discovery, entity trap, granularity, monolith/distributed decision. |
| `FSA_ROOT/chapters/014-part-ii-architecture-styles.md` | Part II: Architecture Styles | Part divider. |
| `FSA_ROOT/chapters/015-chapter-9-foundations.md` | Chapter 9: Foundations | Architecture style vocabulary; Big Ball of Mud; monolith/distributed split; distributed fallacies, logs, transactions, contracts. |
| `FSA_ROOT/chapters/016-chapter-10-layered-architecture-style.md` | Chapter 10: Layered Architecture Style | Technical layers, closed/open layers, sinkhole risk, simplicity versus agility/testability. |
| `FSA_ROOT/chapters/017-chapter-11-pipeline-architecture-style.md` | Chapter 11: Pipeline Architecture Style | Pipes/filters, unidirectional transformation, modular processing, topology constraints. |
| `FSA_ROOT/chapters/018-chapter-12-microkernel-architecture-style.md` | Chapter 12: Microkernel Architecture Style | Core/plugin topology, registry/contracts, customization fit, plugin coupling and single-quantum limits. |
| `FSA_ROOT/chapters/019-chapter-13-service-based-architecture-style.md` | Chapter 13: Service-Based Architecture Style | Coarse domain services, shared/federated data, ACID benefits, moderate distribution, pragmatic trade-offs. |
| `FSA_ROOT/chapters/020-chapter-14-event-driven-architecture-style.md` | Chapter 14: Event-Driven Architecture Style | Broker versus mediator, async flow, error/recovery/data-loss controls, eventual consistency, test/debug costs. |
| `FSA_ROOT/chapters/021-chapter-15-space-based-architecture-style.md` | Chapter 15: Space-Based Architecture Style | Extreme scale/elasticity via in-memory grids, async persistence, collision/recovery complexity, operational prerequisites. |
| `FSA_ROOT/chapters/022-chapter-16-orchestration-driven-service-oriented-architecture.md` | Chapter 16: Orchestration-Driven SOA | Central orchestration, reuse-driven coupling, service taxonomy, governance and complexity costs. |
| `FSA_ROOT/chapters/023-chapter-17-microservices-architecture.md` | Chapter 17: Microservices Architecture | Bounded contexts, data isolation, granularity, operational reuse, choreography/orchestration, sagas and distributed costs. |
| `FSA_ROOT/chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md` | Chapter 18: Choosing the Appropriate Architecture Style | Contextual style selection, data and team/operations constraints, monolith/distributed, sync/async default, hybridization. |
| `FSA_ROOT/chapters/025-part-iii-techniques-and-soft-skills.md` | Part III: Techniques and Soft Skills | Part divider. |
| `FSA_ROOT/chapters/026-chapter-19-architecture-decisions.md` | Chapter 19: Architecture Decisions | Last responsible moment, architecturally significant decisions, ADRs, consequences/compliance, decision authority. |
| `FSA_ROOT/chapters/027-chapter-20-analyzing-architecture-risk.md` | Chapter 20: Analyzing Architecture Risk | Impact/likelihood matrix, collaborative risk storming, mitigation, repeated assessment. |
| `FSA_ROOT/chapters/028-chapter-21-diagramming-and-presenting-architecture.md` | Chapter 21: Diagramming and Presenting Architecture | Representational consistency, low-fidelity exploration, C4/UML limits, communication fidelity. |
| `FSA_ROOT/chapters/029-chapter-22-making-teams-effective.md` | Chapter 22: Making Teams Effective | Constraint calibration, control-freak/armchair failure modes, team-context control, checklists. |
| `FSA_ROOT/chapters/030-chapter-23-negotiation-and-leadership-skills.md` | Chapter 23: Negotiation and Leadership Skills | Stakeholder negotiation, business justification, pragmatic leadership, team proximity. |
| `FSA_ROOT/chapters/031-chapter-24-developing-a-career-path.md` | Chapter 24: Developing a Career Path | Keeping knowledge current, technology radar, learning and architecture practice. |
| `FSA_ROOT/chapters/032-self-assessment-questions.md` | Self-Assessment Questions | Retrieval/check coverage for chapters 1–24; no independent claims. |
| `FSA_ROOT/chapters/033-index.md` | Index | Retrieval aid only; no independent doctrine. |
| `FSA_ROOT/chapters/034-about-the-authors.md` | About the Authors | Author background and distributed-systems consulting context. |
| `FSA_ROOT/chapters/035-colophon.md` | Colophon | Publication-only. |

### DDD coverage (20/20 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `DDD_ROOT/chapters/001-domain-driven-dissign.md` | Domain-Driven DISSIGN | Cover/title conversion; no independent doctrine. |
| `DDD_ROOT/chapters/002-chapter-1-crunching-knowledge.md` | Chapter 1: Crunching Knowledge | Developer/expert learning loop, knowledge-rich models, prototype feedback, distillation. |
| `DDD_ROOT/chapters/003-chapter-2-communication-and-the-use-of-language.md` | Chapter 2: Communication and the Use of Language | Ubiquitous language, model-aligned conversation/code/tests, documentation roles, explanatory models. |
| `DDD_ROOT/chapters/004-chapter-3-binding-model-and-implementation.md` | Chapter 3: Binding Model and Implementation | Model-driven design, paradigm/tool fit, user-model alignment, hands-on modelers. |
| `DDD_ROOT/chapters/005-chapter-4-isolating-the-domain.md` | Chapter 4: Isolating the Domain | Domain-layer isolation, framework selectivity, Smart UI contraindication and simpler alternatives. |
| `DDD_ROOT/chapters/006-chapter-5-a-model-expressed-in-software.md` | Chapter 5: A Model Expressed in Software | Association constraints, entity/value/service/module decisions, technical packaging and paradigm mixing. |
| `DDD_ROOT/chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md` | Chapter 6: The Life Cycle of a Domain Object | Aggregate consistency boundaries, factories, repositories, transactions, relational compromise. |
| `DDD_ROOT/chapters/008-chapter-7-using-the-language-an-extended-example.md` | Chapter 7: Using the Language: An Extended Example | Integrated modeling choices, scenarios, aggregates/repositories, external integration, performance trade-offs. |
| `DDD_ROOT/chapters/009-chapter-8-breakthrough.md` | Chapter 8: Breakthrough | Deep-model discontinuities, risk/benefit decision, broad refactoring under deadline. |
| `DDD_ROOT/chapters/010-epilogue-a-cascade-of-new-insights.md` | Epilogue: A Cascade of New Insights | One model breakthrough exposing further implicit concepts. |
| `DDD_ROOT/chapters/011-chapter-9-making-implicit-concepts-explicit.md` | Chapter 9: Making Implicit Concepts Explicit | Language/design awkwardness as evidence, constraints/process/specification objects, working prototypes. |
| `DDD_ROOT/chapters/012-chapter-10-supple-design.md` | Chapter 10: Supple Design | Intention-revealing interfaces, side-effect-free functions, assertions, contours, declarative design, restraint. |
| `DDD_ROOT/chapters/013-chapter-11-applying-analysis-patterns.md` | Chapter 11: Applying Analysis Patterns | Prior models as starting evidence, not recipes; implementation feedback and compromise. |
| `DDD_ROOT/chapters/014-chapter-12-relating-design-patterns-to-the-model.md` | Chapter 12: Relating Design Patterns to the Model | Strategy/policy and composite only when they express domain concepts; reject pattern-for-pattern's-sake. |
| `DDD_ROOT/chapters/015-chapter-13-refactoring-toward-deeper-insight.md` | Chapter 13: Refactoring Toward Deeper Insight | Model-refactoring signals, exploration teams, domain validation, timing and release cautions. |
| `DDD_ROOT/chapters/016-chapter-14-maintaining-model-integrity.md` | Chapter 14: Maintaining Model Integrity | Bounded contexts, context maps, integration relationships, model-boundary tests, legacy migration. |
| `DDD_ROOT/chapters/017-chapter-15-distillation.md` | Chapter 15: Distillation | Core domain, generic subdomains, cohesive mechanisms, segregated/abstract core, refactoring priority. |
| `DDD_ROOT/chapters/018-chapter-16-large-scale-structure.md` | Chapter 16: Large-Scale Structure | Evolving order, minimal structures, metaphors/layers/knowledge level/plugins, fit and discard conditions. |
| `DDD_ROOT/chapters/019-chapter-17-bringing-the-strategy-together.md` | Chapter 17: Bringing the Strategy Together | Assessment-first strategy, feedback-driven architecture, minimalism/humility, avoid master plans. |
| `DDD_ROOT/chapters/020-references.md` | References | Bibliographic provenance; no independent doctrine. |

## Per-source corpus-map evidence

### CA — Clean Architecture

- **Primary domain:** dependency structure and boundary design for maintainable systems, with module/component principles and policy/detail separation.
- **Strongest contributions:** connects change protection to source-dependency direction; distinguishes source/component/process/service boundaries; exposes the cost gradient from facade to full boundary; argues that deployment, operation, development, and maintenance are separate architectural drivers; treats tests and composition roots as architectural clients/details; records failures from overarchitecture and premature framework reuse.
- **Contextual assumptions:** primarily OO and often statically typed enterprise or embedded systems; high-level policy is sufficiently identifiable; teams can enforce source boundaries; changeability is a dominant economic concern; much evidence is practitioner anecdote.
- **Limitations and dating:** publication-era Java/C#/C++ packaging, jar/DLL deployment, J2EE-era framework examples, and strong claims that database/web are merely details. Operational/data/security constraints can make those elements architectural drivers. Its component metrics are heuristics; the source itself says the metric is not a god. Some universal or absolute phrasing is advocacy rather than demonstrated cross-context fact.
- **Known tensions:** FSA gives operational characteristics and data topology more structural weight; DDD permits direct/domain-tailored models and multiple contexts rather than one uniform inward-layer scheme; CA itself contains an appendix showing overarchitecture and a guest chapter favoring package-by-component over diagrammatic layering.
- **Likely roles:** architecture agents, coding agents working at accepted boundaries, review agents, embedded-system agents, refactoring agents assessing dependency direction.
- **Concepts worth mining:** change amplification, dependency direction, policy/detail separation, boundary cost, partial boundaries, source versus deployment coupling, information hiding, composition root, test boundary, compiler-enforced architecture, option preservation.
- **Representative locators:** `CA: chapters/026-chapter-15-what-is-architecture.md :: ### KEEPING OPTIONS OPEN`; `CA: chapters/036-chapter-25-layers-and-boundaries.md :: ### CONCLUSION`; `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE DECOUPLING FALLACY`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### CONCLUSION: THE MISSING ADVICE`; `CA: chapters/047-vii-appendix.md :: #### ... BY ANY OTHER NAME`.

### FSA — Fundamentals of Software Architecture

- **Primary domain:** evidence-based selection and governance of architectural characteristics, styles, risks, and decisions in modern monolithic and distributed systems.
- **Strongest contributions:** makes trade-offs and business drivers explicit; distinguishes operational, structural, and cross-cutting characteristics; requires measurable definitions and fitness functions; catalogs distributed-system costs; gives decision/risk procedures; treats architecture as iterative and coupled to engineering and operational capability.
- **Contextual assumptions:** 2020-era commercial systems, often Java/.NET and cloud/DevOps capable; organizations have architect roles, teams, CI/CD, monitoring, and enough agency to select styles; style ratings are comparative teaching devices, not empirical guarantees.
- **Limitations and dating:** container/Kubernetes/cloud practices and product examples may drift; security and data architecture are acknowledged but not deeply developed; `architecture quantum` is a useful author-defined lens, not a universal industry standard; star ratings compress context and must never substitute for repository evidence.
- **Known tensions:** rejects fixed axioms and one-style answers, directly tempering CA's timeless/universal framing; tends to separate architecture and detailed design roles more than CA/DDD, while still insisting on feedback and hands-on practice; its default-to-synchronous advice conflicts with event-first or workload-specific designs.
- **Likely roles:** architecture agents, design-review agents, repository-assessment agents, performance/reliability agents, risk reviewers, decision-record authors.
- **Concepts worth mining:** architectural drivers, minimal characteristic set, fitness functions, evolutionary architecture, style selection, architecture quantum, distributed fallacies, ADRs, risk storming, constraint calibration, representational consistency.
- **Representative locators:** `FSA: chapters/003-preface-invalidating-axioms.md :: ## Axiom`; `FSA: chapters/005-chapter-1-introduction.md :: ## Laws of Software Architecture`; `FSA: chapters/010-chapter-5-identifying-architectural-characteristics.md :: ## Implicit Characteristics`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecture Decision Records`.

### DDD — Domain-Driven Design

- **Primary domain:** modeling complex business domains and maintaining model integrity across implementation, teams, and system boundaries.
- **Strongest contributions:** treats model and implementation as one feedback system; makes language an executable design instrument; provides explicit rules for entity/value/service, aggregate and repository boundaries; offers a rich context-relationship decision vocabulary; supplies strong contraindications for domain modeling; prioritizes the differentiating core domain; insists large-scale structure evolve from experience.
- **Contextual assumptions:** a sufficiently complex, knowledge-rich business domain; sustained access to domain experts; skilled developers capable of iterative modeling; an implementation paradigm that can express the model; usually object-oriented enterprise applications.
- **Limitations and dating:** Java/J2EE, entity-bean, XML/DTD, CORBA and relational-mapping examples reflect 2003 technology; terminology such as `Service` predates current microservice usage; some transaction/aggregate guidance needs reinterpretation under modern distributed consistency; the book explicitly says Smart UI/transaction-script approaches can be superior for simple CRUD and weakly skilled teams.
- **Known tensions:** domain purity is repeatedly subordinated to implementation performance, framework reality, and translation cost; bounded contexts are model-consistency boundaries, not automatic microservices; large unified models are sometimes valuable despite modern service fashion; reusable/plugin frameworks require maturity and multiple proven applications.
- **Likely roles:** domain/design agents, architecture agents, legacy integration agents, coding agents in domain-heavy repositories, review agents, refactoring agents pursuing deeper models.
- **Concepts worth mining:** ubiquitous language, knowledge crunching, model/implementation binding, aggregate invariants, bounded context, context map, anticorruption layer, core domain, generic subdomain, model breakthrough, evolving order, domain-specific contraindications.
- **Representative locators:** `DDD: chapters/002-chapter-1-crunching-knowledge.md :: ## Ingredients of Effective Modeling`; `DDD: chapters/003-chapter-2-communication-and-the-use-of-language.md :: ## Ubiquitous Language`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`; `DDD: chapters/017-chapter-15-distillation.md :: ## Core Domain`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Evolving Order`.

## Source-role classification

| Source | Source roles | Appropriate doctrinal weight |
|---|---|---|
| CA | Architectural reasoning; dependency and boundary design; implementation-to-architecture linkage; embedded design; historical practitioner evidence | Strong for questions of change protection and boundary mechanics; contextual for universal layering, DIP, and detail classification. |
| FSA | Architectural reasoning; operational architecture; style-selection catalog; governance/risk/decision technique; team practice | Strong for trade-off procedure, measurable characteristics, distributed preconditions, ADR/risk practice; contextual for style ratings and quanta terminology. |
| DDD | Domain modeling; implementation craft for rich domains; strategic boundary design; legacy/external integration; model-oriented refactoring | Strong for model-language/invariant/context decisions in complex domains; inapplicable by its own account to many simple CRUD or infrastructure-heavy systems. |

## Conversion and evidence caveats

- OCR/conversion artifacts include dropped ligatures (`software` rendered as `soware`), hyphenated words, malformed emphasis in DDD headings, merged or spurious headings, and the cover typo `DISSIGN`. Locators use actual converted filenames and headings so they remain resolvable.
- Some CA code listings are represented by image links plus partial text; diagrams carry meaning not fully recoverable from prose. FSA and DDD diagrams likewise encode topology and mappings. Claims here rely on accompanying prose, not inference from an unseen image alone.
- Index, contents, self-assessment, references, publication metadata, acknowledgments, and colophon were inspected and classified but do not add independent support.
- Page anchors are conversion artifacts and were not used as canonical locators. Heading locators are more stable in this corpus.
- The sources contain anecdotes and pedagogical examples, not controlled comparative studies. Confidence labels below distinguish cross-source operational principles from school-specific advocacy.
- Technology claims that can drift—framework capabilities, cloud operations, messaging semantics, database behavior—must be verified against the current repository and selected technology before execution.

## Candidate doctrine records

These are candidates for the synthesized ontology. IDs are stable within this extraction, not declarations that the final ontology must retain every record unchanged.

### AD-ARC-001 — Architecture is a response to demonstrated change and quality forces

- **Category:** architecture; universal.
- **Claim:** Architecture is the set of consequential structural decisions that shape lifecycle cost and system qualities. A diagram, named style, or large file is not by itself architecture evidence.
- **Decision rule:** Treat a decision as architectural when it materially affects structure, nonfunctional characteristics, dependencies, interfaces, construction/deployment technique, or the cost and risk of expected change. Describe the force before proposing a structure.
- **Required evidence:** accepted requirements; observed change paths; operational SLOs/constraints; incidents; deployment topology; dependency graph; data ownership; team/release boundaries; accepted decisions.
- **Insufficient evidence:** aesthetic discomfort; source prestige; diagram symmetry; file size alone; a style trend; hypothetical scale without a demand model.
- **Applicable when:** assessing architecture, recording a significant decision, or deciding whether implementation work may challenge accepted structure.
- **Not applicable when:** a local implementation decision does not alter architectural drivers or contracts.
- **Costs, reversal, scale, operations:** architectural decisions coordinate many consumers and are often costly to reverse; the cost increases across persistent data, public contracts, deployment units, and organizational ownership. Operational consequences must be explicit.
- **Preservation boundaries:** accepted behavior, public/partner contracts, data semantics, security/trust boundaries, SLOs, and owner authority.
- **Safe actions:** observe and map forces; quantify a characteristic; identify an unprotected expected change; write a proposal or ADR within authority.
- **Unsafe actions:** rename local taste as an architecture requirement; alter deployment/data boundaries while nominally doing code cleanup.
- **Failure modes:** architecture astronomy, under-specification, treating every defect as architecture, confusing topology with rationale.
- **Confidence:** strong, cross-source.
- **Roles/context:** architecture-agent, review-agent, repository-assessment-agent; all archetypes.
- **Source support:** `CA: chapters/003-foreword.md :: FOREWORD`; `CA: chapters/026-chapter-15-what-is-architecture.md :: ### MAINTENANCE`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecturally Significant`; `FSA: chapters/005-chapter-1-introduction.md :: ## Laws of Software Architecture`.

### AD-ARC-002 — Repository contracts and observed reality outrank architectural schools

- **Category:** universal; architecture; agent-conduct.
- **Claim:** A named school supplies hypotheses and techniques; the current repository, accepted decisions, runtime constraints, and owner instructions determine applicability.
- **Decision rule:** Before applying Clean Architecture, DDD, microservices, layering, or another style, identify the repository's current contracts and the force the technique would solve. If no force is demonstrated, leave the architecture unchanged.
- **Required evidence:** repository instructions; ADR/RFC status; build/deploy manifests; actual package/module visibility; runtime topology; ownership and data contracts; tests.
- **Insufficient evidence:** a source saying a technique is universal; folder names that resemble a pattern; a technology keyword in dependencies.
- **Applicable when:** all architecture recommendations and reviews.
- **Not applicable when:** none; this is a precedence rule.
- **Costs/reversal/operations:** prevents generic doctrine from erasing context; may retain imperfect local structures when changing them lacks business value.
- **Preservation boundaries:** explicit project and authority contracts.
- **Safe actions:** describe a source pattern as a candidate; test it against current forces; record conflicts.
- **Unsafe actions:** replace repository conventions solely because a book prefers another organization.
- **Failure modes:** cargo-cult architecture; decontextualized best practices; claiming consensus where sources conflict.
- **Confidence:** universal.
- **Roles/context:** all agents and repositories.
- **Source support:** `FSA: chapters/003-preface-invalidating-axioms.md :: ## Axiom`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### CONCLUSION: THE MISSING ADVICE`.

### AD-ARC-003 — Define a minimal measurable set of architecture characteristics

- **Category:** architecture; review.
- **Claim:** Quality attributes earn structural influence only when critical to success, structurally consequential, and defined precisely enough to evaluate.
- **Decision rule:** Translate business/domain concerns into candidate characteristics; operationalize each with a scenario, stimulus, response, measurement, and scope; rank them; remove those that do not affect structure or success. Prefer the smallest sufficient set because qualities trade off.
- **Required evidence:** user/business outcomes, load/latency/availability/recovery targets, compliance or safety obligations, operating environment, cost limits, historical incidents.
- **Insufficient evidence:** `fast`, `scalable`, `secure`, `agile`, or `high availability` without a scenario or threshold; treating every desirable quality as equally critical.
- **Applicable when:** architecture planning, risk review, style selection, performance/reliability work.
- **Not applicable when:** a characteristic is purely a local design concern with no structural consequence.
- **Costs/reversal/scale/operations:** every prioritized characteristic constrains design and adds verification cost; over-specification produces complexity and mutually defeating requirements.
- **Preservation boundaries:** currently accepted SLOs and user-visible behavior.
- **Safe actions:** distinguish average from tail latency; scalability from elasticity; availability from reliability/recoverability; define a budget or monitor.
- **Unsafe actions:** invent production targets; trade away a mandated quality without authority.
- **Failure modes:** `-ility` shopping lists, ambiguous measures, optimizing one characteristic while silently degrading another.
- **Confidence:** strong.
- **Roles/context:** architecture-agent, performance-agent, review-agent; services and distributed systems especially.
- **Source support:** `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Critical or important to application success`; `FSA: chapters/010-chapter-5-identifying-architectural-characteristics.md :: ## Implicit Characteristics`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Measuring Architecture Characteristics`.

### AD-ARC-004 — Architecture evolves through implementation and measurement

- **Category:** architecture; universal.
- **Claim:** Architecture is a tested hypothesis. Unknowns and implementation constraints require iterative refinement; upfront work should establish only decisions whose delay is riskier than their current uncertainty.
- **Decision rule:** Decide at the last responsible moment: late enough to possess material evidence, early enough not to block delivery or incur a known irreversible cost. Put reversible decisions behind small experiments; verify consequential assumptions through implementation, tests, benchmarks, or operational observation.
- **Required evidence:** uncertainty ledger, reversal cost, dependency lead time, experiment results, implementation feedback, decision deadline.
- **Insufficient evidence:** `we might need it`; `we can always change it later`; a complete speculative future roadmap.
- **Applicable when:** greenfield, modernization, style/boundary selection, uncertain technology.
- **Not applicable when:** a legal, physical, safety, or irreversible data constraint requires early commitment.
- **Costs/reversal/scale/operations:** experiments consume time but reduce decision uncertainty; delayed decisions can increase migration cost; premature structures add continuing coordination cost.
- **Preservation boundaries:** production behavior and agreed release scope; experiments must be isolated or reversible.
- **Safe actions:** spike; thin vertical slice; low-fidelity diagram; provisional decision with review trigger; fitness function.
- **Unsafe actions:** freeze a master plan; keep a blocking decision open past its responsible moment; infer that evolutionary means architecture-free.
- **Failure modes:** big design up front, analysis paralysis, architecture drift without recorded decisions, disposable prototype silently becoming production.
- **Confidence:** strong, cross-source.
- **Roles/context:** architecture-agent, coding-agent, review-agent; greenfield and converging products.
- **Source support:** `CA: chapters/003-foreword.md :: FOREWORD`; `CA: chapters/036-chapter-25-layers-and-boundaries.md :: ### CONCLUSION`; `FSA: chapters/005-chapter-1-introduction.md :: ## Engineering Practices`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Covering Your Assets Anti-Pattern`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Evolving Order`.

### AD-ARC-005 — Preserve options selectively, not universally

- **Category:** architecture.
- **Claim:** Delay volatile implementation-detail choices when the delay creates useful learning and policy can proceed independently; do not build indirection around every imaginable detail.
- **Decision rule:** Preserve an option only when (1) alternatives remain plausible, (2) later evidence can change the choice, (3) commitment has meaningful reversal cost, and (4) a low-cost seam exists. Otherwise choose directly and record the assumption.
- **Required evidence:** credible alternatives, volatility/history, experiment plan, reversal cost, seam cost, policy/detail distinction.
- **Insufficient evidence:** possibility alone; generic fear of vendor lock-in; a requirement to be `future-proof`.
- **Applicable when:** database/framework/protocol/vendor choices, replaceable adapters, staged migrations.
- **Not applicable when:** repository contract already commits the choice; the supposed detail shapes core semantics, SLOs, data ownership, or regulatory behavior.
- **Costs/reversal/scale/operations:** seams cost code, concepts, tests, and operations; unused options become accidental complexity. Full isolation across a process or database is far costlier than in-process substitution.
- **Preservation boundaries:** existing contracts and semantics; do not pretend a made external commitment does not exist operationally.
- **Safe actions:** isolate construction in composition root; keep framework types at boundary; run comparative proof.
- **Unsafe actions:** abstract every framework call; deny operational coupling; hide a required vendor feature behind a lossy lowest-common-denominator API.
- **Failure modes:** speculative generality, leaky abstraction, false portability.
- **Confidence:** strong but contextual.
- **Roles/context:** architecture-agent, coding-agent; volatile technical edges.
- **Source support:** `CA: chapters/026-chapter-15-what-is-architecture.md :: ### KEEPING OPTIONS OPEN`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### THE RISKS`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Covering Your Assets Anti-Pattern`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## The Pitfalls of Infrastructure-Driven Packaging`.

### AD-ARC-006 — Boundaries must be earned by a force and sized to that force

- **Category:** architecture.
- **Claim:** A boundary is justified by independently changing policy, model consistency, data/invariant ownership, quality-attribute scope, deployment/release need, trust boundary, or team coordination—not by symmetry or directory aesthetics.
- **Decision rule:** Name the force; identify two sides and the protected direction; show their independent change or operational requirements; choose the cheapest boundary mode that enforces the needed preservation. Reassess at an explicit trigger.
- **Required evidence:** co-change and change-history differences; distinct actors/domain languages; transaction/invariant scope; SLO or scaling differences; independent release need; trust/security segmentation; ownership boundaries.
- **Insufficient evidence:** a large module, many classes, service fashion, one possible future implementation, team count alone.
- **Applicable when:** module split/merge, service extraction, package/component boundaries, domain contexts.
- **Not applicable when:** the code changes together for the same reasons and shares one invariant/quality scope.
- **Costs/reversal/scale/operations:** boundaries add translation, contracts, versioning, latency, failure modes, deployment and cognitive overhead. Reversal from distributed boundaries may require data migration and contract retirement.
- **Preservation boundaries:** semantics across the proposed seam, transactional guarantees, compatibility, data ownership, observability.
- **Safe actions:** in-process module boundary; facade; one-way interface; characterization at boundary; partial boundary with erosion checks.
- **Unsafe actions:** split a transaction without a consistency design; publish internal entities; assume process separation creates decoupling.
- **Failure modes:** nano-services, distributed monolith, boundary-by-org-chart, translation swamp, facade with uncontrolled backchannels.
- **Confidence:** universal decision rule; implementation contextual.
- **Roles/context:** architecture-agent, domain-agent, refactoring-agent, review-agent.
- **Source support:** `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24: Partial Boundaries`; `CA: chapters/036-chapter-25-layers-and-boundaries.md :: ### CONCLUSION`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Analyze Architecture Characteristics`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`.

### AD-ARC-007 — Boundary strength has a cost gradient

- **Category:** architecture; implementation.
- **Claim:** A facade, consumer-owned interface, separately compiled component, local process, and remote service provide different enforcement and failure properties; they are not interchangeable labels.
- **Decision rule:** Select the weakest mechanism that reliably enforces the required change, authority, trust, deployment, and failure isolation. Escalate only when an observed or mandated force exceeds the current mechanism.
- **Required evidence:** required enforcement property; build/module visibility; release cadence; process isolation need; fault/latency budget; security boundary; versioning ownership.
- **Insufficient evidence:** `decoupling` without specifying source, runtime, deployment, temporal, or semantic coupling.
- **Applicable when:** choosing package/module/process/service boundary form.
- **Not applicable when:** discussing model boundaries without an implementation decision yet.
- **Costs/reversal/scale/operations:** stronger boundaries add admin, observability, serialization, latency, availability, compatibility, and incident surface. Partial boundaries risk erosion and need checks.
- **Preservation boundaries:** behavior and contract equivalence across escalation; rollback path.
- **Safe actions:** document boundary mode; use compiler visibility; add dependency checks; monitor erosion.
- **Unsafe actions:** call an interface an independent deployment; treat a network hop as a stronger semantic boundary.
- **Failure modes:** accidental distributed system, unenforced architectural diagram, premature binary/module split.
- **Confidence:** strong.
- **Roles/context:** architecture-agent, coding-agent, review-agent.
- **Source support:** `CA: chapters/029-chapter-18-boundary-anatomy.md :: ## BOUNDARY CROSSING`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### ONE-DIMENSIONAL BOUNDARIES`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### OTHER DECOUPLING MODES`; `FSA: chapters/015-chapter-9-foundations.md :: ## Monolithic Versus Distributed Architectures`.

### AD-ARC-008 — Direct dependencies are the default; inversion protects a demonstrated stable policy

- **Category:** architecture; implementation.
- **Claim:** Dependency inversion is valuable when it prevents a volatile or externally controlled detail from dictating a policy, but an interface at every call adds indirection without protection.
- **Decision rule:** Invert a dependency when the caller's policy must evolve independently of the callee's detail, when implementations genuinely vary, when substitution is needed at an owned boundary, or when deployment/trust ownership demands it. Define the interface from the consuming policy's needs. Otherwise depend directly.
- **Required evidence:** volatility difference; multiple or planned-and-funded implementation; testing substitution that cannot use ordinary seams; external ownership; policy/mechanism boundary; stable consumer contract.
- **Insufficient evidence:** `loose coupling`; mocking convenience alone; one implementation plus no change pressure; a rule that every class needs an interface.
- **Applicable when:** adapter boundaries, gateways, plugins, framework isolation, cross-component dependency direction.
- **Not applicable when:** simple cohesive local collaboration or where inversion misrepresents ownership.
- **Costs/reversal/scale/operations:** interfaces add concepts, factories/wiring, versioning, and may freeze a premature abstraction. In-process reversal is usually moderate; published interfaces are expensive.
- **Preservation boundaries:** substitutability contract, error and timing semantics, policy invariants.
- **Safe actions:** consumer-defined narrow port; contract tests; direct concrete code at composition edge.
- **Unsafe actions:** provider-wide generic interface; leaking framework/database types inward; claiming independent deployment from source inversion alone.
- **Failure modes:** interface explosion, mock-shaped production design, unstable abstraction, dependency direction that contradicts actual authority.
- **Confidence:** strong/contextual; CA advocacy bounded by FSA/DDD trade-off rules.
- **Roles/context:** coding-agent, architecture-agent, review-agent.
- **Source support:** `CA: chapters/013-chapter-5-object-oriented-programming.md :: #### DEPENDENCY INVERSION`; `CA: chapters/020-chapter-11-dip-the-dependency-inversion-principle.md :: ## STABLE ABSTRACTIONS`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES`; `DDD: chapters/012-chapter-10-supple-design.md :: # Chapter 10: Supple Design`.

### AD-ARC-009 — Protect policy from details only to the extent policy is actually independent

- **Category:** architecture; domain.
- **Claim:** Separating business/domain policy from UI, persistence, frameworks, or devices improves change locality and testability when the policy has coherent semantics independent of those mechanisms. Some data, operational, safety, and performance choices are not mere details.
- **Decision rule:** Identify a policy whose invariants and use cases can be expressed without the mechanism. Isolate conversion and side effects at the edge. If removing the mechanism changes policy semantics or required qualities, model that influence explicitly rather than pretending independence.
- **Required evidence:** stable domain/use-case rules, alternate delivery/storage mechanism or observed mechanism volatility, testable boundary contract, explicit mapping.
- **Insufficient evidence:** labeling all database/web/framework code `detail`; moving types to an `inner` directory while data semantics still leak.
- **Applicable when:** domain-heavy systems, embedded hardware isolation, multi-adapter applications, volatile delivery mechanisms.
- **Not applicable when:** simple data-entry system; database constraints are the core correctness mechanism; query/data topology defines behavior; framework is accepted architecture.
- **Costs/reversal/scale/operations:** adapters and mappings cost effort and can duplicate types; excessive isolation harms performance and clarity. Operational topology remains real even if policy source is isolated.
- **Preservation boundaries:** domain invariants, transaction semantics, data fidelity, error semantics.
- **Safe actions:** humble adapter; plain boundary data; HAL; explicit repository contract.
- **Unsafe actions:** duplicate canonical data models without a translation need; ignore database consistency or hardware timing.
- **Failure modes:** anemic domain behind ceremonial layers, mapping explosion, policy that cannot exploit required platform capability.
- **Confidence:** strong when preconditions hold; contested as universal framing.
- **Roles/context:** architecture-agent, coding-agent, domain-agent, embedded-agent.
- **Source support:** `CA: chapters/033-chapter-22-the-clean-architecture.md :: ## THE DEPENDENCY RULE`; `CA: chapters/040-chapter-29-clean-embedded-architecture.md :: #### The Hardware Is a Detail`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ### Data architecture`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Domain Layer Is Where the Model Lives`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"`.

### AD-ARC-010 — Component cohesion follows change, reuse, release, and semantic forces

- **Category:** architecture; implementation.
- **Claim:** Components should group elements that change for the same actors/reasons, are released together, and are reused together, while presenting a coherent concept. These forces can conflict.
- **Decision rule:** Examine co-change, ownership actors, release/version unit, consumers, and domain responsibility. Group only where the dominant forces align; record the trade-off when common closure conflicts with common reuse.
- **Required evidence:** version/release history; co-change history; consumer dependency graph; actor/ownership; semantic responsibility.
- **Insufficient evidence:** proximity, file count, `one class per component`, team structure alone.
- **Applicable when:** package/module/component reorganization, shared library extraction, API surface review.
- **Not applicable when:** generated/vendored code or fixed external packaging.
- **Costs/reversal/scale/operations:** too coarse increases internal coupling and blast radius; too fine increases communication, version coordination, deployment and cognitive cost.
- **Preservation boundaries:** public surface, release compatibility, ownership and behavior.
- **Safe actions:** reduce public types; compiler-enforce entry point; co-locate cohesive implementation.
- **Unsafe actions:** shared `common` bucket; split because of size; force reuse on consumers that need different subsets.
- **Failure modes:** dependency magnet, change shotgun, release lockstep, duplicated policy hidden behind `common`.
- **Confidence:** strong.
- **Roles/context:** architecture-agent, refactoring-agent, coding-agent.
- **Source support:** `CA: chapters/023-chapter-13-component-cohesion.md :: ## THE REUSE/RELEASE EQUIVALENCE PRINCIPLE`; `CA: chapters/023-chapter-13-component-cohesion.md :: ### THE COMMON CLOSURE PRINCIPLE`; `CA: chapters/023-chapter-13-component-cohesion.md :: ### THE COMMON REUSE PRINCIPLE`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Component Granularity`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Modules (a.k.a. Packages)`.

### AD-ARC-011 — Component granularity is an iterative empirical decision

- **Category:** architecture.
- **Claim:** Initial component boundaries are candidates. Implementation, workflow, quality-scope, and change evidence refine them.
- **Decision rule:** Generate an initial decomposition from workflows/actors/domain concepts; map requirements; compare architecture-characteristic scope; implement a thin slice; then split, merge, or redraw only where evidence shows communication overload, internal coupling, inconsistent qualities, or unclear responsibility.
- **Required evidence:** mapped use cases, collaboration graph, quality-scope differences, code/change feedback, test/deploy consequences.
- **Insufficient evidence:** entity list, database tables, one workshop diagram, one developer preference.
- **Applicable when:** greenfield component design and evolving modularity.
- **Not applicable when:** externally fixed protocol or vendor component.
- **Costs/reversal/scale/operations:** too-fine components amplify calls/contracts; too-coarse components amplify test/release/change blast radius.
- **Preservation boundaries:** use-case behavior and public contracts during redrawing.
- **Safe actions:** keep first design provisional; use in-process modules; collect change evidence.
- **Unsafe actions:** turn every entity into a manager/service; treat architect draft as final.
- **Failure modes:** entity trap, nano-components, god component, premature service extraction.
- **Confidence:** strong.
- **Roles/context:** architecture-agent, coding-agent, review-agent; greenfield and converging products.
- **Source support:** `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Component Identification Flow`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Entity trap`; `CA: chapters/036-chapter-25-layers-and-boundaries.md :: ### CONCLUSION`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Refactoring Toward a Fitting Structure`.

### AD-ARC-012 — Domain partitioning and technical partitioning solve different problems

- **Category:** architecture; domain.
- **Claim:** Domain partitioning localizes workflow/business change and can ease later distribution; technical partitioning centralizes technical consistency and may be simpler for uniform CRUD or strongly shared mechanisms. Neither is automatically superior.
- **Decision rule:** Prefer domain partitioning when business capabilities change independently, have meaningful language/ownership, or need differing characteristics. Prefer technical partitioning when workflows are simple/uniform, shared technical behavior dominates, or team capability and cost favor it. Enforce whichever partition is chosen.
- **Required evidence:** workflows and change axes; cross-domain technical customization; data coupling; team skill; architectural characteristics; public surface.
- **Insufficient evidence:** `DDD means folders by feature`; `layers are always bad`; directory names alone.
- **Applicable when:** module/package topology and style selection.
- **Not applicable when:** tiny code base where either structure adds more ceremony than signal.
- **Costs/reversal/scale/operations:** domain partitioning may duplicate technical customization; technical layering may create global coupling and domain scattering. Migration is easier if data and public surfaces respect eventual ownership.
- **Preservation boundaries:** business rules, security/authorization paths, shared data invariants.
- **Safe actions:** package by component/feature with hidden internals; architecture checks.
- **Unsafe actions:** allow web/controller to bypass policy to persistence because arrows still point down.
- **Failure modes:** relaxed-layer bypass, duplicated domain model across layers, infrastructure-driven packaging.
- **Confidence:** strong/contextual.
- **Roles/context:** architecture-agent, coding-agent, review-agent.
- **Source support:** `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Architecture Partitioning`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY COMPONENT`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## The Pitfalls of Infrastructure-Driven Packaging`.

### AD-ARC-013 — Use compiler/build enforcement for accepted structural constraints

- **Category:** architecture; review.
- **Claim:** An architectural rule that matters should be enforced as close to the change as practical, preferably by language visibility, module/build boundaries, tests, or static analysis.
- **Decision rule:** For each accepted constraint, select the cheapest objective check. Prefer construction that makes violation impossible; otherwise run a fitness function in the normal verification path.
- **Required evidence:** accepted decision and exact forbidden/required dependency or measurable quality; tool support; false-positive review.
- **Insufficient evidence:** diagram, team memory, style guide alone, a metric with no decision consequence.
- **Applicable when:** dependency direction, cycles, public surface, performance budgets, contract boundaries.
- **Not applicable when:** a constraint is exploratory, qualitative, or cannot yet be measured reliably; record/manual review may be appropriate.
- **Costs/reversal/scale/operations:** checks add maintenance and can ossify stale decisions; every check needs an owner and retirement/update condition.
- **Preservation boundaries:** build reliability and developer feedback time; checks must not encode preferences as blockers.
- **Safe actions:** package-private implementation; module exports; dependency test; SLO monitor; cycle check.
- **Unsafe actions:** rigid metric gate detached from domain complexity; hidden bypasses via reflection; governance with no revision path.
- **Failure modes:** architecture drift, brittle fitness tests, false authority, lagging post-build review.
- **Confidence:** strong.
- **Roles/context:** architecture-agent, review-agent, coding-agent.
- **Source support:** `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### ORGANIZATION VERSUS`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Continuous Integration`.

### AD-ARC-014 — Metrics detect questions; they do not decide architecture

- **Category:** architecture; review.
- **Claim:** Coupling, instability, abstractness, complexity, coverage, and distance metrics are narrow indicators. Outliers earn investigation, not automatic restructuring.
- **Decision rule:** Establish a repository-relative baseline and trend; investigate deviations with semantic, history, runtime, and domain evidence; act only if the metric corresponds to a demonstrated risk or accepted characteristic.
- **Required evidence:** definition, baseline, trend, distribution, known confounders, relation to a quality or incident.
- **Insufficient evidence:** universal threshold; single snapshot; rank ordering without context.
- **Applicable when:** fitness functions, risk discovery, hotspot triage.
- **Not applicable when:** generated/vendor code or inherently complex algorithms unless separately scoped.
- **Costs/reversal/scale/operations:** metric gaming can worsen design; broad gates create churn. Metrics are cheap to reverse but the changes they provoke may not be.
- **Preservation boundaries:** domain correctness and understandable structure outrank metric optimization.
- **Safe actions:** flag cyclic dependency or rising tail latency; inspect why.
- **Unsafe actions:** split a function/component solely to lower a number; call coverage proof of correctness.
- **Failure modes:** Goodhart's law, threshold cargo cult, aesthetic refactoring disguised as governance.
- **Confidence:** universal.
- **Roles/context:** review-agent, architecture-agent, refactoring-agent, performance-agent.
- **Source support:** `CA: chapters/024-chapter-14-component-coupling.md :: ### CONCLUSION`; `FSA: chapters/008-chapter-3-modularity.md :: ## Limitations of Metrics`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## What's a Good Value for Cyclomatic Complexity?`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Client Code Ignores R***EPOSITORY* **Implementation; Developers Do Not`.

### AD-ARC-015 — Architect and implementer must share a closed feedback loop

- **Category:** architecture; agent-conduct.
- **Claim:** Architecture separated from implementation loses feasibility feedback; implementation without architectural context erodes constraints. The roles may differ, but the loop must remain direct and frequent.
- **Decision rule:** Require architectural proposals to be exercised by an implementation slice and reviewed with implementers. Require implementation discoveries that alter a driver or contract to return to the decision owner. Keep architects hands-on enough to observe consequences without taking over all detailed design.
- **Required evidence:** implementation feedback path; joint review; decision owner; representative slice; team skill and project complexity.
- **Insufficient evidence:** architect-generated diagram handed off once; developer claim that architecture is irrelevant; title-based authority.
- **Applicable when:** all nontrivial projects and agent handoffs.
- **Not applicable when:** trivial local implementation with no architectural effect, though repository constraints still apply.
- **Costs/reversal/scale/operations:** collaboration consumes time but prevents expensive divergence; too much architectural control removes developer agency and slows flow; too little creates inconsistent implementation.
- **Preservation boundaries:** decision authority: an implementation agent reports pressure but does not silently redefine architecture.
- **Safe actions:** prototype; pairing; design review; feedback ADR update; architect writes representative code.
- **Unsafe actions:** ivory-tower mandate; control-freak pseudocode; armchair topology with no implementation consequences.
- **Failure modes:** model handoff loss, architecture drift, unimplementable standards, architect bottleneck.
- **Confidence:** strong, cross-source.
- **Roles/context:** architecture-agent, coding-agent, review-agent, agent-conduct.
- **Source support:** `CA: chapters/026-chapter-15-what-is-architecture.md :: # Chapter 15: What Is Architecture?`; `FSA: chapters/007-chapter-2-architectural-thinking.md :: ## Architecture Versus Design`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: ## Architect Personalities`; `DDD: chapters/004-chapter-3-binding-model-and-implementation.md :: ## Hands-On Modelers`.

### AD-DOM-016 — Invest in domain modeling only where complexity and value earn it

- **Category:** domain; architecture.
- **Claim:** Domain-driven design is an investment for complex, differentiating domains; simple CRUD/data-entry work may be clearer, faster, and safer with transaction scripts, generated UI, or direct layering.
- **Decision rule:** Use rich domain modeling when business rules, language, identity, invariants, policy variation, or conceptual change create persistent complexity and the team has expert access and modeling skill. Otherwise choose a simpler design and state its growth limit.
- **Required evidence:** rule complexity; recurring ambiguity; domain-expert involvement; business differentiation; expected change; team capability; failed simpler design.
- **Insufficient evidence:** business nouns; desire for `clean code`; DDD package names; database size.
- **Applicable when:** domain-heavy products, complex policy, regulated business rules, long-lived systems.
- **Not applicable when:** simple CRUD, short-lived tool, infrastructure-heavy service, weak expert access, low-skill/short-timeline team where ceremony would dominate.
- **Costs/reversal/scale/operations:** modeling requires skilled collaboration, extra types, refactoring, and sustained language discipline. A Smart UI can be replaced only in coarse units; a rich model can be needless overhead.
- **Preservation boundaries:** business behavior and delivery constraints; do not rewrite a successful simple system for doctrinal purity.
- **Safe actions:** prototype a rule-rich slice; compare direct transaction script; identify core versus generic needs.
- **Unsafe actions:** declare every repository a domain; force entities/value objects/aggregates onto data plumbing.
- **Failure modes:** anemic ceremonial model, jargon without behavior, sophisticated layers around simple tables, inaccessible model.
- **Confidence:** strong/contextual, explicitly self-limited by DDD.
- **Roles/context:** domain-agent, architecture-agent, coding-agent, review-agent.
- **Source support:** `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## Advantages`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Naked Objects and Similar Frameworks`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ### The domain`.

### AD-DOM-017 — A domain model is a tested working language, not a noun inventory

- **Category:** domain; implementation.
- **Claim:** A useful model captures rules, identity, processes, constraints, and relationships in language shared by experts, code, tests, and documentation. Nouns and data schemas are only leads.
- **Decision rule:** Exercise candidate concepts through concrete domain scenarios with experts; retain a concept only if it makes explanations more precise and implementation/test behavior clearer. Refactor names and relationships when language changes.
- **Required evidence:** expert corrections; scenarios; code/test correspondence; resolved ambiguity; explicit rule or decision enabled by the concept.
- **Insufficient evidence:** repeated noun, table/entity name, directory name, glossary entry without behavior.
- **Applicable when:** complex domain discovery, API semantics, model review.
- **Not applicable when:** no domain complexity or experts; use simpler technical vocabulary.
- **Costs/reversal/scale/operations:** language changes propagate through code/docs/tests and require coordination; the cost is justified when it reduces translation and wrong behavior.
- **Preservation boundaries:** externally accepted terminology/contracts and current semantics; renaming must not silently change behavior.
- **Safe actions:** model aloud; scenario walk-through; rename after agreement; capture explicit concept.
- **Unsafe actions:** infer a boundary from terminology alone; let developers and experts maintain separate translations indefinitely.
- **Failure modes:** false cognates, duplicate concepts, technical jargon masquerading as domain language, model divorced from code.
- **Confidence:** strong.
- **Roles/context:** domain-agent, coding-agent, architecture-agent, review-agent.
- **Source support:** `DDD: chapters/002-chapter-1-crunching-knowledge.md :: ## Ingredients of Effective Modeling`; `DDD: chapters/003-chapter-2-communication-and-the-use-of-language.md :: ## Ubiquitous Language`; `DDD: chapters/011-chapter-9-making-implicit-concepts-explicit.md :: ## Listen to Language`; `CA: chapters/032-chapter-21-screaming-architecture.md :: ## THE THEME OF AN ARCHITECTURE`.

### AD-DOM-018 — Model and implementation must coevolve

- **Category:** domain; implementation.
- **Claim:** A model that cannot be expressed effectively in the implementation is not an operational model; implementation friction, performance, and awkward code are evidence for revising either the model or its mapping.
- **Decision rule:** Bind every material model concept to an observable code/test construct. When the mapping is indirect or costly, determine whether the tool/paradigm is wrong, the model is wrong, or a documented compromise is warranted. Feed results back to experts.
- **Required evidence:** prototype or production code; tests; persistence/serialization mapping; performance profile; expert validation.
- **Insufficient evidence:** UML alone, analyst document handed to programmers, implementation that uses model names only in comments.
- **Applicable when:** model-driven design, domain refactoring, ORM/framework selection.
- **Not applicable when:** explanatory models deliberately outside implementation; label them as such.
- **Costs/reversal/scale/operations:** tight correspondence improves clarity but may constrain persistence or tool choices; deliberate mapping layers add cost and must preserve semantics.
- **Preservation boundaries:** domain semantics, stored-data compatibility, performance and transaction guarantees.
- **Safe actions:** behavior-only prototype without infrastructure; refactor model and code together; use a translator for distinct models.
- **Unsafe actions:** preserve a beautiful model that fails operational constraints; let framework classes become the accidental domain vocabulary.
- **Failure modes:** analysis/design split, anemic data model, framework-driven concepts, hidden mapping semantics.
- **Confidence:** strong.
- **Roles/context:** coding-agent, domain-agent, architecture-agent.
- **Source support:** `DDD: chapters/002-chapter-1-crunching-knowledge.md :: ## Ingredients of Effective Modeling`; `DDD: chapters/004-chapter-3-binding-model-and-implementation.md :: ## Model-Driven Design`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Designing Objects for Relational Databases`; `FSA: chapters/007-chapter-2-architectural-thinking.md :: ## Architecture Versus Design`.

### AD-DOM-019 — Make identity, value, and stateless domain service semantics explicit

- **Category:** domain; implementation.
- **Claim:** Model an element as an entity only when continuity and identity matter to the domain; as a value when interchangeable attributes define it; and as a domain service when a meaningful stateless operation fits no entity or value without distortion.
- **Decision rule:** Ask what makes two instances the same, whether history matters, whether replacement is equivalent, and who owns the operation. Make the minimum identity and lifecycle explicit; prefer immutable values; reject service objects that merely collect displaced behavior.
- **Required evidence:** domain matching rules; lifecycle; identity source; mutation/ownership; scenario showing operation does not belong naturally elsewhere.
- **Insufficient evidence:** database primary key; class/object identity; operation suffix `Service`; persistence table.
- **Applicable when:** rich domain implementation and API modeling.
- **Not applicable when:** data transfer representations or infrastructure service nomenclature; do not confuse them with domain services.
- **Costs/reversal/scale/operations:** entity identity creates tracking and consistency cost; value immutability may allocate/copy; services can create an anemic model if overused.
- **Preservation boundaries:** identity continuity, equality semantics, invariants, serialization compatibility.
- **Safe actions:** domain-specific identifier; immutable whole value; narrow intention-revealing operation.
- **Unsafe actions:** assign identity to everything; mutate shared value; move all business behavior to `*Service`.
- **Failure modes:** mistaken identity, temporal bugs, aliasing, anemic entities, procedural service layer.
- **Confidence:** strong in domain-heavy contexts.
- **Roles/context:** coding-agent, domain-agent, review-agent.
- **Source support:** `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Entities (a.k.a. Reference Objects)`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Value Objects`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Services`; `CA: chapters/031-chapter-20-business-rules.md :: ## ENTITIES`.

### AD-DOM-020 — Aggregate boundaries are transactional invariant boundaries, not object graphs

- **Category:** domain; architecture.
- **Claim:** An aggregate groups the minimum state that must be consistent at one transaction boundary. External access is through a root; cross-aggregate rules require an explicit consistency timescale rather than an ever-growing lock scope.
- **Decision rule:** Enumerate invariants and concurrent updates; group only objects that must change atomically to preserve them; choose a root that mediates mutation; reference other aggregates by identity/root; define eventual checks for cross-boundary rules.
- **Required evidence:** invariant statements; transaction semantics; concurrent write scenarios; contention/load; lifecycle/delete semantics; query needs.
- **Insufficient evidence:** composition in UML; `has-many` relation; object graph reachability; desire to avoid joins.
- **Applicable when:** domain state with nontrivial consistency and concurrency.
- **Not applicable when:** immutable data, read models, simple records with no multi-object invariant.
- **Costs/reversal/scale/operations:** large aggregates serialize work and increase contention; small aggregates move correctness into async coordination and failure recovery. Changing boundaries may require data/API migration.
- **Preservation boundaries:** invariants, identity, transaction atomicity, message ordering and retry semantics.
- **Safe actions:** lock/version root; transient internal references; explicit event/outbox for cross-boundary update.
- **Unsafe actions:** direct mutation of internals; split atomic invariant across services; assume eventual consistency is automatically acceptable.
- **Failure modes:** giant aggregate, invariant violation under concurrency, aggregate-per-entity cargo cult, hidden distributed transaction.
- **Confidence:** strong/contextual.
- **Roles/context:** domain-agent, architecture-agent, coding-agent, review-agent; durability-sensitive systems.
- **Source support:** `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Purchase Order Integrity`; `FSA: chapters/019-chapter-13-service-based-architecture-style.md :: ## Service Design and Granularity`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Transactions and Sagas`.

### AD-DOM-021 — Repository and factory boundaries express lifecycle semantics

- **Category:** domain; implementation.
- **Claim:** Repositories provide collection-like access only to aggregate roots that need global retrieval; factories encapsulate creation when valid construction is complex. They are semantic boundaries, not mandatory wrappers over every table or constructor.
- **Decision rule:** Add a repository only for a root reached independently by a use case. Add a factory only when construction/reconstitution must enforce invariants, choose a concrete type, or hide a complex assembly. Keep transaction authority with the caller unless the repository contract explicitly owns it.
- **Required evidence:** use-case lookup; aggregate root; construction invariant/complexity; persistence substitution need; transaction owner.
- **Insufficient evidence:** one database table/class; testing fashion; desire for uniformity.
- **Applicable when:** rich domain lifecycle and persistence boundaries.
- **Not applicable when:** simple record access, read projection, framework repository already matches needs.
- **Costs/reversal/scale/operations:** generic repositories obscure query/performance and data capabilities; factories add indirection. Query implementation must be profiled at realistic scale.
- **Preservation boundaries:** aggregate invariants, identity continuity, transaction scope, query semantics.
- **Safe actions:** explicit intent-revealing query; in-memory test implementation; optimized internal query hidden behind stable semantics.
- **Unsafe actions:** `all()` over production-scale set; repository per class; `find-or-create` that hides domain-significant novelty.
- **Failure modes:** persistence abstraction leak, N+1/load explosion, generic CRUD domain, transaction surprise.
- **Confidence:** strong/contextual.
- **Roles/context:** coding-agent, domain-agent, performance-agent, review-agent.
- **Source support:** `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Repositories`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Client Code Ignores R***EPOSITORY* **Implementation; Developers Do Not`; `CA: chapters/034-chapter-23-presenters-and-humble-objects.md :: ### DATABASE GATEWAYS`.

### AD-DOM-022 — Constrain associations to reduce semantic and implementation coupling

- **Category:** domain; implementation.
- **Claim:** Bidirectional and many-to-many associations should remain only when domain semantics and required traversal demand them. Direction, qualification, or deletion can encode knowledge and reduce coupling.
- **Decision rule:** For each association, identify required traversal, multiplicity, ownership, update synchronization, and query frequency. Remove unused traversal, qualify multiplicity with a domain rule, or replace navigation with a repository/query when that produces clearer and safer behavior.
- **Required evidence:** use-case traversal; domain constraint; query/update profile; lifecycle ownership.
- **Insufficient evidence:** real-world relationship exists; ORM can map it; diagram looks complete.
- **Applicable when:** domain models, object graphs, API schemas.
- **Not applicable when:** graph-centric domains where bidirectionality is the core model; still characterize operations and scale.
- **Costs/reversal/scale/operations:** retaining associations increases synchronization and loading cost; removing them may add queries and latency. Profile actual access patterns.
- **Preservation boundaries:** relationship meaning and consistency.
- **Safe actions:** unidirectional reference; identity reference; explicit lookup; qualified key.
- **Unsafe actions:** expose entire connected graph; duplicate both directions without a synchronization owner.
- **Failure modes:** object graph explosion, cascading loads, stale mirror collections, accidental aggregate expansion.
- **Confidence:** strong/contextual.
- **Roles/context:** coding-agent, domain-agent, performance-agent.
- **Source support:** `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Associations`; `DDD: chapters/008-chapter-7-using-the-language-an-extended-example.md :: ## Designing Associations in the Shipping Domain`; `FSA: chapters/015-chapter-9-foundations.md :: ## Fallacy #3: Bandwidth Is Infinite`.

### AD-DOM-023 — Bounded context is a model-consistency and ownership boundary

- **Category:** domain; architecture.
- **Claim:** A bounded context delimits where terms, rules, and model semantics are unified. It is not synonymous with a module, package, service, team, or subdomain, though those may realize or influence it.
- **Decision rule:** Map the models actually in use; locate conflicting meanings, independent expert communities, code/data ownership, and team communication. Draw the smallest contexts within which one model can be kept consistent and name every translation point. Map current reality before proposing a target.
- **Required evidence:** vocabulary contradictions/false cognates; distinct rules for similar concepts; team/code/schema ownership; integration points; model-specific tests.
- **Insufficient evidence:** folder names; organization chart alone; one entity per service; desire for microservices.
- **Applicable when:** large domains, multiple teams/systems, legacy integration, domain partitioning.
- **Not applicable when:** one small coherent model/team; adding contexts would introduce translation without benefit.
- **Costs/reversal/scale/operations:** each context creates translation, duplicated concepts, deployment coordination, and communication cost; one huge context creates coordination and conceptual compromise. Merging is harder than splitting.
- **Preservation boundaries:** meaning, rules, data ownership, interface translations, team authority.
- **Safe actions:** current-state context map; boundary contract tests; explicit translator.
- **Unsafe actions:** share model code casually across contexts; infer a service boundary automatically; claim contexts are clean when language is still contradictory.
- **Failure modes:** false cognates, accidental shared kernel, distributed shared database with contradictory semantics, context-per-entity.
- **Confidence:** strong.
- **Roles/context:** domain-agent, architecture-agent, legacy-agent, repository-assessment-agent.
- **Source support:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## B***OUNDED* **C***ONTEXTS* **Are Not M***ODULES`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Domain-Driven Design's Bounded Context`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Bounded Context`.

### AD-DOM-024 — Choose context relationships by cooperation, control, and integration value

- **Category:** domain; architecture; legacy.
- **Claim:** Cross-context integration requires an explicit relationship strategy. Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Separate Ways, Open Host Service, and Published Language optimize different conditions.
- **Decision rule:** Determine integration necessity, model quality, ownership/control, team cooperation, number of consumers, and translation cost; select the relationship that matches current reality. Do not choose the most prestigious or independent-looking option.
- **Required evidence:** control over each side; consumer count; interface breadth; model compatibility; release coordination; translation/duplication cost; business value of integration.
- **Insufficient evidence:** two systems exchange data; same noun appears on both sides; API already exists.
- **Applicable when:** legacy/external integration, multiple teams, platform services, mergers.
- **Not applicable when:** no meaningful integration need—choose Separate Ways deliberately.
- **Costs/reversal/scale/operations:** Shared Kernel has high coordination; Conformist deepens dependency; ACL has translation and maintenance cost; Open Host freezes a public protocol; Separate Ways duplicates and forecloses easy future merge.
- **Preservation boundaries:** each context's semantics, compatibility, deployment coordination, translation tests.
- **Safe actions:** table in techniques ledger below; choose consciously; boundary acceptance tests.
- **Unsafe actions:** informal code sharing; one universal enterprise model; ACL without semantic translation; public protocol for one consumer.
- **Failure modes:** corruption by foreign model, translation explosion, frozen host model, unsupported downstream promises.
- **Confidence:** strong/contextual.
- **Roles/context:** architecture-agent, domain-agent, legacy-agent, review-agent.
- **Source support:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Relationships Between B***OUNDED* **C***ONTEXTS`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## A Cautionary Tale`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## The Trade-off`.

### AD-DOM-025 — Protect a local model with an anticorruption layer only when translation earns its cost

- **Category:** legacy; domain; architecture.
- **Claim:** An anticorruption layer protects a valuable local model from a necessary, materially different external/legacy model. It is semantic translation, not merely transport wrapping.
- **Decision rule:** Use an ACL when integration is required, models conflict, the local model is valuable, and conforming would impose unacceptable semantic/coupling cost. Define local services, external facade if needed, adapters, and explicit translators; test both directions. Prefer conforming or direct integration when the foreign model is good enough and interface is broad.
- **Required evidence:** semantic mapping; model conflicts; ownership limits; interface breadth; local-model value; translation/test/operation budget.
- **Insufficient evidence:** external API exists; dislike of legacy naming; generic desire to isolate vendors.
- **Applicable when:** legacy replacement, third-party integration, mergers, distinct internal contexts.
- **Not applicable when:** small clean interface; upstream model is acceptable and indispensable; integration value is low.
- **Costs/reversal/scale/operations:** ACL can become a substantial subsystem, duplicate data, add latency/failures, and require versioned mappings. It can enable incremental legacy retirement.
- **Preservation boundaries:** semantic fidelity, identity mapping, ordering, error/retry behavior, auditability.
- **Safe actions:** facade in foreign context; adapter per local service; stateless translator; contract tests; phased deletion.
- **Unsafe actions:** mix foreign primitives throughout local domain; call a transport client an ACL; duplicate business rules ambiguously.
- **Failure modes:** translation swamp, third accidental model, stale mappings, unbounded bidirectional coupling.
- **Confidence:** strong/contextual.
- **Roles/context:** legacy-agent, architecture-agent, domain-agent, coding-agent.
- **Source support:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Anticorruption Layer`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Implementing the A***NTICORRUPTION* **L***AYER`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Phasing Out a Legacy System`; `CA: chapters/034-chapter-23-presenters-and-humble-objects.md :: ### SERVICE LISTENERS`.

### AD-DOM-026 — Distill effort toward the differentiating core domain

- **Category:** domain; architecture; refactoring.
- **Claim:** Not all domain code deserves equal modeling and refactoring investment. The differentiating core should receive the strongest talent and deepest design; generic/supporting work should be simplified, bought, published, outsourced, or isolated when safe.
- **Decision rule:** Identify the capabilities that directly create distinctive user/business value; validate with stakeholders; mark supporting/generic subdomains; rank design/refactoring work by effect on the core and its relationship to support code.
- **Required evidence:** domain vision/business strategy; user outcomes; change and pain in core workflows; ownership; cost/benefit of generic solutions.
- **Insufficient evidence:** most complex code; most technically interesting subsystem; highest line count; executive label alone.
- **Applicable when:** prioritizing modeling, refactoring, staffing, build-vs-buy, modernization.
- **Not applicable when:** commodity/infrastructure product where the technical mechanism itself is the differentiator—then it may be core.
- **Costs/reversal/scale/operations:** distillation can break convenient cohesion and requires team agreement; outsourcing/buying adds vendor/integration risk.
- **Preservation boundaries:** domain behavior, core ownership/knowledge, support contracts.
- **Safe actions:** brief domain vision; highlighted core; segregated core after evidence; generic subdomain evaluation.
- **Unsafe actions:** outsource the core knowledge; call infrastructure core because engineers prefer it; refactor whole codebase uniformly.
- **Failure modes:** gold-plated periphery, neglected core, false build-vs-buy economy, key knowledge leakage.
- **Confidence:** strong/contextual.
- **Roles/context:** architecture-agent, domain-agent, refactoring-agent, planning/review agent.
- **Source support:** `DDD: chapters/017-chapter-15-distillation.md :: ## Core Domain`; `DDD: chapters/017-chapter-15-distillation.md :: ## Generic Subdomains`; `DDD: chapters/017-chapter-15-distillation.md :: ## Choosing Refactoring Targets`; `CA: chapters/030-chapter-19-policy-and-level.md :: ## LEVEL`.

### AD-DOM-027 — Make implicit domain concepts explicit only when they simplify decisions or behavior

- **Category:** domain; refactoring.
- **Claim:** Repeated language, awkward procedures, contradictions, duplicated calculations, or unexplained policy may reveal a missing concept. Creating a type is warranted only when it clarifies scenarios, removes duplication/coupling, or makes a rule executable.
- **Decision rule:** Locate awkwardness; propose a concept; test it aloud with experts and in code/tests; compare complexity before/after; retain it only if it improves the model and implementation together.
- **Required evidence:** repeated unexplained term; awkward behavior; recurring rule; contradictory expert statements; concrete prototype/refactoring improvement.
- **Insufficient evidence:** noun frequency; desire for more domain classes; isolated elegance.
- **Applicable when:** domain-heavy design/refactoring.
- **Not applicable when:** concept is incidental, used once, or better expressed as data/operation.
- **Costs/reversal/scale/operations:** new concepts add vocabulary and migration cost; a wrong concept can distort the model.
- **Preservation boundaries:** existing behavior and expert meaning; model refactoring may be semantic and requires authority if behavior changes.
- **Safe actions:** small exploration team; test-first interface; working prototype.
- **Unsafe actions:** call behavior-changing model redesign `refactoring`; force experts to accept technical vocabulary.
- **Failure modes:** abstraction fever, elegant but false concept, stale language/code mismatch.
- **Confidence:** strong/contextual.
- **Roles/context:** domain-agent, refactoring-agent, coding-agent, review-agent.
- **Source support:** `DDD: chapters/011-chapter-9-making-implicit-concepts-explicit.md :: ## Digging Out Concepts`; `DDD: chapters/011-chapter-9-making-implicit-concepts-explicit.md :: ## Scrutinize Awkwardness`; `DDD: chapters/015-chapter-13-refactoring-toward-deeper-insight.md :: ## Initiation`.

### AD-DOM-028 — Large-scale domain structure must earn and retain fit

- **Category:** architecture; domain.
- **Claim:** A large-scale structure is optional. Use the smallest shared organizing rule that makes a complex model intelligible; evolve or discard it when exceptions and workarounds outnumber guidance.
- **Decision rule:** Introduce structure only after module/context complexity obstructs comprehension or consistent decisions and a domain-grounded pattern has emerged. Define its scope, exceptions, and falsification/retirement trigger.
- **Required evidence:** recurring navigation/placement confusion; inconsistent independent decisions; shared domain pattern; successful application to representative areas.
- **Insufficient evidence:** desire for an enterprise blueprint; a compelling metaphor; architecture team authority.
- **Applicable when:** large models, multi-team domains, strategic design.
- **Not applicable when:** modules/context map already make system understandable; no fitting structure is evident.
- **Costs/reversal/scale/operations:** global rules reduce local optimization and can become straitjackets; plugin frameworks freeze core protocols and require mature repeated applications.
- **Preservation boundaries:** local context autonomy, core semantics, explicit exceptions.
- **Safe actions:** loose metaphor/responsibility layers; minimal structure; iterative refactor.
- **Unsafe actions:** master plan, framework for imagined reusers, comprehensive global rules before domain learning.
- **Failure modes:** totalitarian architecture, bypassed framework, cargo-cult metaphor, frozen abstract core.
- **Confidence:** strong/contextual.
- **Roles/context:** architecture-agent, domain-agent, review-agent.
- **Source support:** `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Evolving Order`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Pluggable Component Framework`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## How Restrictive Should a Structure Be?`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Beware the Master Plan`.

### AD-ARC-029 — Prefer a modular monolith when one operational/consistency envelope suffices

- **Category:** architecture.
- **Claim:** A monolith is not the absence of boundaries. When one deployable/quality/consistency envelope suffices, a modular monolith avoids network and distributed-data costs while retaining internal domain/component boundaries.
- **Decision rule:** Start with one deployment when components can share acceptable characteristics, release cadence, trust zone, and transaction model. Enforce internal modules and data ownership. Distribute only components with demonstrated incompatible envelopes or independent operational/ownership needs.
- **Required evidence:** characteristic scope; scaling/load profile; release/ownership; data/transaction boundary; fault-isolation need; operational maturity.
- **Insufficient evidence:** team count; microservices fashion; repository size; future scale with no model.
- **Applicable when:** greenfield business systems, small/medium teams, converging products, cost-sensitive systems.
- **Not applicable when:** mandatory isolation, independently scaled workloads, hard trust/legal boundaries, genuinely independent release/availability requirements.
- **Costs/reversal/scale/operations:** monolith simplifies calls, transactions, debugging, and deployment but may enlarge blast radius and scaling unit. Module/data discipline preserves extraction options.
- **Preservation boundaries:** module public surfaces, data ownership, one-step deploy/rollback, transactional semantics.
- **Safe actions:** package by component; hidden internals; schema/domain partitions; dependency fitness tests.
- **Unsafe actions:** global mutable shared state; controllers bypassing components; claim modularity based on folders only.
- **Failure modes:** distributed envy, modular-monolith label on Big Ball of Mud, premature split, shared database as unowned commons.
- **Confidence:** strong/contextual.
- **Roles/context:** architecture-agent, coding-agent, review-agent.
- **Source support:** `CA: chapters/026-chapter-15-what-is-architecture.md :: ## DEVELOPMENT`; `CA: chapters/038-chapter-27-services-great-and-small.md :: ## SERVICE BENEFITS?`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Architecture Quantum Redux: Choosing Between Monolithic Versus Distributed Architectures`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Modular Monolith`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY COMPONENT`.

### AD-ARC-030 — Distribution must be purchased with demonstrated operational need and capability

- **Category:** architecture; performance; durability.
- **Claim:** Service/process separation provides independent deployment, scaling, isolation, or ownership only when contracts, data, operations, and teams support it; otherwise it adds unreliable networks, latency, security surface, versioning, logging, and consistency failures.
- **Decision rule:** Require at least one hard distribution driver and readiness evidence for observability, automation, failure handling, data ownership, contract evolution, and incident response. Compare against an in-process/module alternative.
- **Required evidence:** load and scaling asymmetry; fault/trust boundary; release independence; team ownership; network latency percentiles; retry/idempotency; tracing/logging; deployment automation; data consistency design.
- **Insufficient evidence:** `decoupling`, `independent teams`, containers, REST, or separate repositories alone.
- **Applicable when:** service-based, event-driven, space-based, SOA, microservices, remote plugins.
- **Not applicable when:** one quality/transaction envelope suffices or operations are manual/immature.
- **Costs/reversal/scale/operations:** introduces every distributed-computing fallacy, security endpoints, transport cost, contract/version burden, and cross-service diagnosis. Reversal can require data consolidation and client migration.
- **Preservation boundaries:** business transaction semantics, failure outcomes, ordering, SLOs, security, compatibility.
- **Safe actions:** latency/failure proof; coarse service first; outbox/idempotency; observability before split.
- **Unsafe actions:** split database transaction with no saga/compensation; synchronous call chain assuming local semantics; shared mutable database with supposed service independence.
- **Failure modes:** distributed monolith, retry storm, partial failure corruption, untraceable request, version lockstep.
- **Confidence:** universal precondition; style contextual.
- **Roles/context:** architecture-agent, performance-agent, debugging/repair-agent, review-agent.
- **Source support:** `FSA: chapters/015-chapter-9-foundations.md :: ## Monolithic Versus Distributed Architectures`; `FSA: chapters/015-chapter-9-foundations.md :: ## Fallacy #1: The Network Is Reliable`; `FSA: chapters/015-chapter-9-foundations.md :: ## Other Distributed Considerations`; `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE DECOUPLING FALLACY`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Deployment`.

### AD-ARC-031 — Select architecture style from drivers, not fashion

- **Category:** architecture.
- **Claim:** Layered, pipeline, microkernel, service-based, event-driven, space-based, SOA, and microservices styles each optimize a different force bundle and impose characteristic costs. Hybridization is normal when forces differ by area.
- **Decision rule:** Rank architecture characteristics and domain topology; assess data, team, process, operational maturity, cost, and reversal; eliminate contraindicated styles; compare at least one simpler alternative; record the least-worst choice and mitigation for weak characteristics.
- **Required evidence:** AD-ARC-003 inputs, domain workflows, deployment/data topology, capability/readiness, cost/time limits.
- **Insufficient evidence:** trend reports; framework availability; star-rating table alone; one favored quality.
- **Applicable when:** greenfield or authorized restructuring.
- **Not applicable when:** accepted architecture already meets needs and no pressure warrants change.
- **Costs/reversal/scale/operations:** see techniques ledger; style names do not implement constraints.
- **Preservation boundaries:** current behavior and data; organizational authority; migration path.
- **Safe actions:** style scorecard tied to repository evidence; hybrid in bounded scope; ADR with rejected alternatives.
- **Unsafe actions:** wholesale style migration for modernity; assume a named style guarantees qualities.
- **Failure modes:** architecture fashion, technique/goal confusion, one-size-fits-all enterprise platform.
- **Confidence:** strong.
- **Roles/context:** architecture-agent, review-agent, repository-assessment-agent.
- **Source support:** `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Shifting "Fashion" in Architecture`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Trade-Offs and Least Worst Architecture`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Strategic design requires minimalism and humility`.

### AD-ARC-032 — Event-driven architecture requires explicit temporal and failure semantics

- **Category:** architecture; durability; performance.
- **Claim:** Asynchrony can improve responsiveness, buffering, scalability, and extensibility, but sacrifices immediate certainty and creates ordering, duplication, loss, recovery, observability, and testability obligations.
- **Decision rule:** Use events for action-based reactions, burst absorption, independent consumers, or required temporal decoupling. Define event ownership, delivery guarantee, idempotency, ordering scope, completion/failure detection, replay, data consistency, and workflow control before implementation. Prefer request/response for simple deterministic queries and workflows requiring immediate certainty.
- **Required evidence:** burst/load model; consumer independence; acceptable staleness; workflow topology; broker guarantees; error/recovery design; observability and test plan.
- **Insufficient evidence:** need for `loose coupling`; existing message broker; future consumers; performance claim without benchmark.
- **Applicable when:** event-driven or hybrid systems, async integration, durable workflows.
- **Not applicable when:** atomic immediate response is required and no compensation/reconciliation is acceptable.
- **Costs/reversal/scale/operations:** broker topology favors decoupling/scale but weakens workflow control/recovery; mediator improves control but centralizes complexity. Persistent queues, acknowledgments, and transaction/outbox patterns add cost.
- **Preservation boundaries:** causal ordering, at-least/at-most/exactly-once claims, business completion, audit trail, failure visibility.
- **Safe actions:** persistent send; client acknowledge; dead-letter/retry policy; correlation; event schema/version; chaos/failure tests.
- **Unsafe actions:** fire-and-forget business critical events; advertise exactly-once without end-to-end proof; use async to hide slow synchronous dependency.
- **Failure modes:** lost/duplicate messages, poisoned queue, invisible stuck workflow, out-of-order repair, event tree explosion.
- **Confidence:** strong/contextual.
- **Roles/context:** architecture-agent, durability-agent, performance-agent, debugging-agent.
- **Source support:** `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Broker Topology`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Error Handling`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Preventing Data Loss`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Choosing Between Request-Based and Event-Based`; `CA: chapters/014-chapter-6-functional-programming.md :: ### EVENT SOURCING`.

### AD-ARC-033 — Prefer synchronous collaboration by default only when its coupling is acceptable

- **Category:** architecture; performance.
- **Claim:** Synchronous calls are simpler to design, test, and debug, but propagate latency and availability coupling. Asynchronous communication is justified when buffering, independent progress, or differing capacity/failure envelopes outweigh its semantic cost.
- **Decision rule:** For each interaction, ask whether the caller requires the result now, whether combined availability/latency meets the budget, and whether stale/eventual completion is acceptable. Choose synchronous if yes and affordable; asynchronous when independent progress is a requirement, not a fashion.
- **Required evidence:** response dependency; latency percentiles; availability composition; backlog behavior; consistency tolerance; debugging/operations capability.
- **Insufficient evidence:** universal `sync first` or `events decouple`; protocol preference.
- **Applicable when:** service and component communication design.
- **Not applicable when:** in-process pure function call with no material temporal concern.
- **Costs/reversal/scale/operations:** sync creates call-chain fragility; async creates queues/state machines/reconciliation. Protocol migration changes contracts and often behavior.
- **Preservation boundaries:** timeouts, cancellation, retries, ordering, user-visible completion.
- **Safe actions:** bounded timeout; circuit breaker where evidence supports; queue with explicit completion state.
- **Unsafe actions:** unbounded synchronous chain; blocking request-reply over messaging marketed as async.
- **Failure modes:** cascading outage, hidden latency multiplication, eventual-consistency surprise.
- **Confidence:** strong/contextual; FSA default is bounded by workload evidence.
- **Roles/context:** architecture-agent, performance-agent, review-agent.
- **Source support:** `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## What communication styles between services—synchronous or asynchronous?`; `FSA: chapters/015-chapter-9-foundations.md :: ## Fallacy #2: Latency Is Zero`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Choosing Between Request-Based and Event-Based`.

### AD-ARC-034 — Make architectural decisions explicit, scoped, justified, and revisable

- **Category:** architecture; agent-conduct; review.
- **Claim:** Architecturally significant decisions need a single durable record containing force, decision, status/authority, consequences, compliance, and replacement history.
- **Decision rule:** Create an ADR only for a structurally significant choice. Record context and alternatives, affirmative decision, technical and business rationale, positive/negative consequences, verification, owner/authority, and revisit trigger. Use `proposed` when authority is insufficient; never silently self-approve cross-team, cost, security, or semantic scope beyond mandate.
- **Required evidence:** decision force; alternatives; trade-off analysis; authority threshold; affected parties; verification plan.
- **Insufficient evidence:** email thread; topology without why; decision with benefits but no costs; author title.
- **Applicable when:** architecture selection/change, public interface, data boundary, quality mechanism, construction technique.
- **Not applicable when:** reversible local implementation detail, unless repository policy requires a record.
- **Costs/reversal/scale/operations:** records cost maintenance but prevent repeated debate and preserve rationale; stale ADRs mislead unless superseded.
- **Preservation boundaries:** decision authority and acceptance; history must not be rewritten.
- **Safe actions:** RFC deadline; proposed status; supersede link; notify only affected consumers with canonical link.
- **Unsafe actions:** architecture by email; claim acceptance without approver; delete old rationale.
- **Failure modes:** Groundhog Day, Covering Your Assets, Email-Driven Architecture, decision graveyard.
- **Confidence:** strong.
- **Roles/context:** architecture-agent, review-agent, agent-conduct; all significant decisions.
- **Source support:** `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecture Decision Records`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## ADRs and Request for Comments (RFC)`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ### Context`; `CA: chapters/009-chapter-2-a-tale-of-two-values.md :: ### FIGHT FOR THE ARCHITECTURE`.

### AD-ARC-035 — Rank architecture risk collaboratively and continuously

- **Category:** architecture; review; debugging/repair.
- **Claim:** Architecture risk is the conjunction of impact and likelihood under a particular quality/behavior scenario. Individual identification followed by collaborative consensus exposes blind spots without prematurely anchoring the group.
- **Decision rule:** Choose a risk dimension; participants independently mark concrete hotspots; discuss disagreements; score likelihood and impact; identify mitigation/proof; rank by exposure and uncertainty; repeat after material change or incident.
- **Required evidence:** topology/current design; quality scenarios; incidents; unknown technologies; owner input; mitigation cost.
- **Insufficient evidence:** generic concern with no scenario; consensus reached before independent identification; severity without likelihood.
- **Applicable when:** architecture review, migration, major feature, incident follow-up, unfamiliar technology.
- **Not applicable when:** simple local implementation risk; use normal code review.
- **Costs/reversal/scale/operations:** workshop time; rankings can be subjective, so preserve dissent and evidence. Unknown/unproven components should carry explicit uncertainty.
- **Preservation boundaries:** distinguish risk identification from authorization to change.
- **Safe actions:** prototype high-uncertainty item; add fitness function; contingency/rollback plan.
- **Unsafe actions:** use risk score as proof of defect; hide minority high-impact concern; declare mitigation complete without verification.
- **Failure modes:** groupthink, stale risk register, risk theater, prioritization by loudness.
- **Confidence:** strong procedure; scoring contextual.
- **Roles/context:** architecture-agent, review-agent, performance/durability agent, repository-assessment agent.
- **Source support:** `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Risk Matrix`; `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Risk Storming`; `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Agile Story Risk Analysis`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Assessment First`.

### AD-ARC-036 — Verify architecture at the preservation boundary

- **Category:** architecture; review; testing.
- **Claim:** Architectural claims need tests or observations at the boundary they protect: dependency checks for source structure, contract tests for context/API translation, SLO monitors for operations, and failure exercises for recovery.
- **Decision rule:** For each decision, state the failure it prevents and place a check at the narrowest surface that would detect that failure before unacceptable harm. Combine structural and runtime evidence where the claim spans both.
- **Required evidence:** accepted decision, boundary contract, representative failure, executable or observable check, owner and response.
- **Insufficient evidence:** unit tests deep inside one side; high aggregate coverage; one happy-path integration test; diagram review.
- **Applicable when:** module/service/context boundaries, migrations, architecture fitness.
- **Not applicable when:** decision cannot yet be operationalized; require manual evidence and a plan rather than fake automation.
- **Costs/reversal/scale/operations:** boundary tests can be slower and brittle; keep them contract-focused. Runtime checks need alert/response ownership.
- **Preservation boundaries:** test interfaces must not expose sensitive internals or freeze implementation unnecessarily.
- **Safe actions:** context translation examples; consumer contract; dependency cycle test; chaos/failover test.
- **Unsafe actions:** public test-only API exposing implementation details; tests structurally coupled to every class.
- **Failure modes:** green tests with broken integration, test boundary becoming privileged backdoor, brittle snapshot governance.
- **Confidence:** strong.
- **Roles/context:** review-agent, architecture-agent, coding-agent, legacy-agent.
- **Source support:** `CA: chapters/039-chapter-28-the-test-boundary.md :: ## TESTS AS SYSTEM COMPONENTS`; `CA: chapters/034-chapter-23-presenters-and-humble-objects.md :: ### TESTING AND ARCHITECTURE`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Testing at the C***ONTEXT* **Boundaries`.

### AD-DOM-037 — Domain-facing interfaces must reveal intention and consequences

- **Category:** domain; implementation; review.
- **Claim:** A domain API should state the effect, policy, and invariants in the ubiquitous language while hiding mechanism. Queries/calculations should be side-effect-free where practical; commands should expose their postconditions and keep mutation narrow.
- **Decision rule:** Review each public domain operation from the client perspective: can an informed reader predict purpose, result, state change, failure, and invariant without reading internals? If not, rename, split command/query, introduce a value/specification, or document an assertion.
- **Required evidence:** representative client code/tests; domain language; pre/postcondition; mutation scope.
- **Insufficient evidence:** short method, generic verb, fluent API aesthetics.
- **Applicable when:** rich domain APIs and core modules.
- **Not applicable when:** low-level internal mechanism not exposed as domain vocabulary.
- **Costs/reversal/scale/operations:** richer types can add allocations and concepts; side-effect-free values may have performance costs that must be measured.
- **Preservation boundaries:** behavior, atomicity, equality, error/failure semantics.
- **Safe actions:** test from client view; immutable value; explicit specification; simple command.
- **Unsafe actions:** conceal side effects behind query name; return mutable internals; create DSL without demonstrated domain fit.
- **Failure modes:** leaky encapsulation, temporal coupling, opaque behavior, decorative fluent interface.
- **Confidence:** strong/contextual.
- **Roles/context:** coding-agent, domain-agent, review-agent.
- **Source support:** `DDD: chapters/012-chapter-10-supple-design.md :: ## Intention-Revealing Interfaces`; `DDD: chapters/012-chapter-10-supple-design.md :: ## Side -Effect-Free Functions`; `DDD: chapters/012-chapter-10-supple-design.md :: ## Assertions`; `CA: chapters/031-chapter-20-business-rules.md :: ### REQUEST AND RESPONSE MODELS`.

### AD-ARC-038 — Reuse and framework extraction require multiple proven consumers

- **Category:** architecture; implementation.
- **Claim:** A reusable framework or plugin core cannot be inferred reliably from one application. Usability in multiple concrete consumers must precede generalized reuse.
- **Decision rule:** Keep local code local until at least two or preferably several real consumers expose stable common semantics and variation. Extract the narrow shared kernel/protocol; keep consumer-specific behavior outside. Treat framework evolution and compatibility as a product obligation.
- **Required evidence:** multiple implemented consumers; repeated code/contract; stable variation points; maintenance owner; compatibility tests.
- **Insufficient evidence:** one future consumer; visually similar classes; desire to avoid duplication; framework expertise.
- **Applicable when:** shared libraries, plugin frameworks, platform APIs, generalized domain components.
- **Not applicable when:** one-off local code or rapidly changing core semantics.
- **Costs/reversal/scale/operations:** published framework creates versioning, support, documentation, governance, and lowest-common-denominator pressure; reversal is high once external consumers exist.
- **Preservation boundaries:** consumer behavior and compatibility; core-domain evolution must not be frozen without accepted value.
- **Safe actions:** duplicate locally while learning; extract after co-evolution; version protocol; test multiple consumers.
- **Unsafe actions:** 45k-line framework for first 6k-line app; freeze abstract core from one use case; share code casually across contexts.
- **Failure modes:** speculative generality, unusable framework, shared-kernel coordination tax, core stagnation.
- **Confidence:** strong, cross-source.
- **Roles/context:** architecture-agent, coding-agent, review-agent.
- **Source support:** `CA: chapters/047-vii-appendix.md :: ### ARCHITECTS REGISTRY EXAM`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Pluggable Component Framework`; `CA: chapters/023-chapter-13-component-cohesion.md :: ## THE REUSE/RELEASE EQUIVALENCE PRINCIPLE`.

### AD-ARC-039 — Framework adoption is an asymmetric architectural commitment

- **Category:** architecture; implementation.
- **Claim:** A framework can solve expensive infrastructure problems, but application code typically commits more deeply to the framework than the framework commits to the application. Adopt only the capabilities that earn their coupling.
- **Decision rule:** Identify the exact problem and alternatives; inspect inheritance/hooks/generated types, lifecycle control, testability, upgrade path, operational footprint, and exit cost; isolate at a composition/adapter edge where feasible; decline unused features.
- **Required evidence:** problem benchmark/prototype; dependency surface; version/support policy; upgrade/exit proof; repository convention.
- **Insufficient evidence:** popularity, vendor prestige, included feature count, `standard stack` without local contract.
- **Applicable when:** web/ORM/DI/workflow/rules/platform framework selection.
- **Not applicable when:** framework is an accepted immutable repository contract; still contain unnecessary spread.
- **Costs/reversal/scale/operations:** lock-in, forced design shape, startup/runtime footprint, upgrade/security workload, generated-code coupling.
- **Preservation boundaries:** framework-specific behavior, data mapping, lifecycle and transaction semantics.
- **Safe actions:** selective capability; wrapper at volatile edge; proof upgrade; composition-root injection.
- **Unsafe actions:** extend framework base type through core domain; use every feature; generic wrapper that hides required semantics.
- **Failure modes:** framework as architecture, untestable callbacks, frozen version, abstraction leak.
- **Confidence:** strong/contextual.
- **Roles/context:** architecture-agent, coding-agent, dependency/review agent.
- **Source support:** `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### ASYMMETRIC MARRIAGE`; `CA: chapters/037-chapter-26-the-main-component.md :: ## THE ULTIMATE DETAIL`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## Architectural Frameworks`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Knowledge of process, teams, and operational concerns`.

### AD-ARC-040 — Team structure is an architectural force, not an automatic boundary map

- **Category:** architecture; agent-conduct.
- **Claim:** Communication topology influences system structure, but component/service boundaries should not merely mirror current teams unless domain, change, and operational forces align.
- **Decision rule:** Treat team ownership and communication as evidence alongside semantic cohesion, data/invariant ownership, release and quality needs. If team and system boundaries conflict, either adjust ownership or explicitly budget coordination; do not canonize an accidental org chart.
- **Required evidence:** team communication/ownership; change paths; release coordination; domain boundaries; skill distribution.
- **Insufficient evidence:** `one service per team`; Conway's law quoted without repository analysis.
- **Applicable when:** multi-team architecture, ownership design, component splitting.
- **Not applicable when:** small single team, though future ownership may be a contextual consideration.
- **Costs/reversal/scale/operations:** team-aligned boundaries reduce coordination but can fragment invariants and duplicate infrastructure; changing either organization or system is expensive.
- **Preservation boundaries:** ownership authority, on-call responsibility, domain semantics, release contracts.
- **Safe actions:** jointly map team and technical dependencies; assign clear owner; keep shared kernel small.
- **Unsafe actions:** create services solely to give each team one; central architecture team siphoning domain expertise.
- **Failure modes:** org-chart architecture, orphaned shared service, coordination bottleneck, uneven team capability.
- **Confidence:** strong/contextual.
- **Roles/context:** architecture-agent, planning agent, review-agent.
- **Source support:** `CA: chapters/026-chapter-15-what-is-architecture.md :: ## DEVELOPMENT`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Conway's Law`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Context Map`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Architecture teams must not siphon off all the best and brightest`.

## Negative doctrine candidates

Each prohibition is intentionally conditional. The evidence threshold identifies when it is strong enough to operate as a guard rather than a preference.

| ID | Prohibition | Evidence threshold / scope | Source support |
|---|---|---|---|
| ND-ARC-001 | Never invent an architectural boundary solely for diagram symmetry, file size, or style conformance. | No independent change, invariant, quality, trust, release, or ownership force has been demonstrated. | `CA: chapters/036-chapter-25-layers-and-boundaries.md :: ### CONCLUSION`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Component Granularity` |
| ND-ARC-002 | Never equate an interface, package, process, or service with decoupling without naming the coupling dimension. | Recommendation uses `decouple` but provides no source/runtime/deployment/temporal/semantic/data analysis. | `CA: chapters/029-chapter-18-boundary-anatomy.md :: ## BOUNDARY CROSSING`; `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE DECOUPLING FALLACY` |
| ND-ARC-003 | Never introduce dependency inversion merely because a concrete class exists. | There is one stable implementation and no policy-protection, substitution, ownership, or volatility pressure. | `CA: chapters/020-chapter-11-dip-the-dependency-inversion-principle.md :: ### CONCRETE COMPONENTS`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES` |
| ND-ARC-004 | Never call a database, web layer, framework, or device a `detail` when it determines required semantics or qualities. | Data consistency, latency, topology, safety, regulation, or runtime behavior depends on it. | `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ### Data architecture`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Designing Objects for Relational Databases`; tension with `CA: chapters/042-chapter-30-the-database-is-a-detail.md :: # Chapter 30` |
| ND-ARC-005 | Never adopt an architecture style because it is current fashion or source-preferred. | No repository-specific driver/contraindication comparison and no simpler alternative evaluated. | `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Shifting "Fashion" in Architecture`; `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Trade-Offs and Least Worst Architecture` |
| ND-ARC-006 | Never distribute a cohesive transaction or model merely to create independent services. | Atomic invariant, synchronous completion, or shared data remains; no saga/compensation and no hard distribution driver exists. | `FSA: chapters/019-chapter-13-service-based-architecture-style.md :: ## Service Design and Granularity`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Transactions and Sagas`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates` |
| ND-ARC-007 | Never claim service/process separation guarantees independent development or deployment. | Shared database, release, contract, synchronous call chain, or cross-cutting changes still couple the units. | `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE FALLACY OF INDEPENDENT DEVELOPMENT AND DEPLOYMENT`; `FSA: chapters/015-chapter-9-foundations.md :: ## Contract maintenance and versioning` |
| ND-ARC-008 | Never optimize for a quality attribute that has no operational definition or priority. | Characteristic is stated only as an adjective or universal desire, with no scenario/measure/scope. | `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Measuring Architecture Characteristics`; `FSA: chapters/010-chapter-5-identifying-architectural-characteristics.md :: ## Implicit Characteristics` |
| ND-ARC-009 | Never let a metric automatically trigger restructuring. | Metric has no repository baseline/trend, semantic explanation, or demonstrated risk. | `CA: chapters/024-chapter-14-component-coupling.md :: ### CONCLUSION`; `FSA: chapters/008-chapter-3-modularity.md :: ## Limitations of Metrics` |
| ND-ARC-010 | Never treat test coverage, dependency arrows, or a passing fitness function as proof of complete correctness. | Claim exceeds the narrow behavior/structure the check actually observes. | `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Process Measures`; `CA: chapters/039-chapter-28-the-test-boundary.md :: ## TESTS AS SYSTEM COMPONENTS` |
| ND-ARC-011 | Never expose implementation detail publicly merely to make it testable. | Proposed test API increases supported surface or bypasses security without a stable client contract. | `CA: chapters/039-chapter-28-the-test-boundary.md :: ### THE TESTING API`; `CA: chapters/034-chapter-23-presenters-and-humble-objects.md :: ## THE HUMBLE OBJECT PATTERN` |
| ND-ARC-012 | Never freeze an architectural master plan against implementation feedback. | New evidence invalidates a force or reveals repeated workarounds/exceptions, but change is rejected due to prior authority or artifact investment. | `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Evolving Order`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Beware the Master Plan`; `FSA: chapters/028-chapter-21-diagramming-and-presenting-architecture.md :: ## Irrational Artifact Attachment` |
| ND-ARC-013 | Never delay a blocking architecture decision beyond its last responsible moment. | The missing decision now blocks delivery, procurement, safety proof, data design, or an irreversible dependency path. | `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Covering Your Assets Anti-Pattern` |
| ND-ARC-014 | Never record an architecture decision without its negative consequences and authority/status. | Decision affects structure, contracts, data, cost, security, or another team. | `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Basic Structure`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## ADRs and Request for Comments (RFC)` |
| ND-ARC-015 | Never communicate the canonical architecture decision only in email/chat. | Decision must guide future or cross-team implementation and has no durable single system of record. | `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Email-Driven Architecture Anti-Pattern` |
| ND-ARC-016 | Never infer a domain boundary from directory names, database tables, or entity nouns alone. | No distinct language/rules, workflow, ownership, invariant, or characteristic scope is shown. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## B***OUNDED* **C***ONTEXTS* **Are Not M***ODULES`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Entity trap` |
| ND-DOM-017 | Never share model code casually across bounded contexts. | Terms/rules or ownership differ and no explicit Shared Kernel governance/test process exists. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Context Map`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel` |
| ND-DOM-018 | Never force one enterprise-wide domain model merely to eliminate translation. | Distinct user communities, rules, terminology, or team capability make full unification costly or compromising. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: # Chapter 14: Maintaining Model Integrity`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Catering to Special Needs with Distinct Models` |
| ND-DOM-019 | Never treat every object with a primary key as a domain entity. | Domain does not care about continuity/identity independent of attributes. | `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Entities (a.k.a. Reference Objects)` |
| ND-DOM-020 | Never draw an aggregate boundary from composition or object reachability alone. | No transaction-level invariant/concurrent-update evidence supports the grouping. | `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates` |
| ND-DOM-021 | Never allow external code to retain or mutate aggregate internals if the root owns the invariant. | Mutation can bypass root invariant checks or widen transaction uncertainty. | `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates` |
| ND-DOM-022 | Never create a repository per class or table as a uniform rule. | Object is not a globally retrieved aggregate root or use case has no independent lookup. | `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ### Therefore:` under Repositories |
| ND-DOM-023 | Never hide a domain-significant distinction between new and existing behind `find or create`. | Creation, identity, audit, authorization, or lifecycle differs. | `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## The Relationship with F***ACTORIES` |
| ND-DOM-024 | Never introduce a domain service just to relocate behavior from an entity/value object. | Operation naturally belongs to an existing concept and service would make it anemic. | `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Services` |
| ND-DOM-025 | Never adopt DDD ceremony for a simple CRUD/data-entry system without demonstrated domain complexity. | Rules, identity, policy, language, and differentiation are weak; team/timeline cannot sustain modeling. | `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Naked Objects and Similar Frameworks` |
| ND-DOM-026 | Never call a new abstraction a deeper model unless domain experts can use and validate it. | Concept is technically elegant but does not improve domain scenarios/language. | `DDD: chapters/015-chapter-13-refactoring-toward-deeper-insight.md :: ## Timing`; `DDD: chapters/009-chapter-8-breakthrough.md :: ## A Deeper Model` |
| ND-DOM-027 | Never treat an analysis/design pattern as an out-of-the-box domain solution. | Local model, implementation, and expert scenarios have not validated fit. | `DDD: chapters/013-chapter-11-applying-analysis-patterns.md :: # Chapter 11`; `DDD: chapters/014-chapter-12-relating-design-patterns-to-the-model.md :: ## Why Not F***LYWEIGHT?` |
| ND-DOM-028 | Never build a reusable domain/plugin framework from a single consumer. | Variation has not been demonstrated by multiple implemented applications. | `CA: chapters/047-vii-appendix.md :: ### ARCHITECTS REGISTRY EXAM`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Pluggable Component Framework` |
| ND-DOM-029 | Never let a framework's packaging or inheritance scatter one conceptual object without an immediate technical need. | Distribution is hypothetical and the scattering obscures model/change cohesion. | `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## The Pitfalls of Infrastructure-Driven Packaging`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### THE RISKS` |
| ND-ARC-030 | Never assume asynchronous messaging prevents data loss or provides exactly-once outcomes. | End-to-end persistence, acknowledgment, transaction/idempotency, retry, and recovery are not proven. | `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Preventing Data Loss`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Error Handling` |
| ND-ARC-031 | Never use a network call as if it had local call latency and failure semantics. | Remote dependency lacks measured tail latency, timeout, retry/idempotency, and partial-failure handling. | `FSA: chapters/015-chapter-9-foundations.md :: ## Fallacy #1: The Network Is Reliable`; `FSA: chapters/015-chapter-9-foundations.md :: ## Fallacy #2: Latency Is Zero` |
| ND-ARC-032 | Never declare a public interchange language identical to the host's internal model by default. | External stability and internal evolution have different needs. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Published Language`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Open Host Service Published Language` |
| ND-ARC-033 | Never let the architecture team remove all strong designers and domain knowledge from implementation teams. | Application teams cannot interpret/evolve strategic decisions or feed back constraints. | `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Architecture teams must not siphon off all the best and brightest`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: ## Armchair Architect` |
| ND-ARC-034 | Never confuse risk identification, recommendation, or proposal with authority to execute. | Agent/architect lacks accepted decision status or explicit change authority, especially for cross-team/data/security effects. | `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## ADRs and Request for Comments (RFC)`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Who Sets the Strategy?` |

## Conflict registry

### CONFLICT-ARC-001 — Up-front architecture versus evolutionary architecture

- **Positions:**
  - A: Decide important boundaries and policy/detail direction early because adding them after extensive coupling can be expensive (`CA`).
  - B: Unknown unknowns and implementation learning make comprehensive up-front architecture unreliable; evolve structure and decide at the last responsible moment (`FSA`, `DDD`, and CA's foreword/chapter 25 caveat).
- **Hidden assumptions:** A assumes identifiable axes of change and high future extraction cost; B assumes rapid feedback, reversible experiments, and no physical/regulatory decision forcing early commitment.
- **Evidence favoring A:** irreversible data/public contract; known trust boundary; hardware/safety constraint; multiple teams need stable interface; prior similar system shows repeated force; migration lead time is long.
- **Evidence favoring B:** uncertain domain/product; small team; cheap in-process refactor; unproven technology; requirements still converging; prior upfront abstractions became waste.
- **Decision rule:** make only decisions whose delay creates more expected cost/risk than current uncertainty. For the rest, preserve a low-cost option and define the evidence/trigger that will force a decision.
- **Unresolved questions:** exact inflection point is project-specific and cannot be derived from source authority; estimate ranges and revisit.
- **Roles affected:** architecture-agent, coding-agent, planning/review-agent.
- **Source support:** `CA: chapters/028-chapter-17-boundaries-drawing-lines.md :: ## WHICH LINES DO YOU DRAW, AND WHEN DO YOU DRAW THEM?`; `CA: chapters/036-chapter-25-layers-and-boundaries.md :: ### CONCLUSION`; `FSA: chapters/005-chapter-1-introduction.md :: ## Engineering Practices`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Evolving Order`.

### CONFLICT-ARC-002 — Dependency inversion versus direct coupling

- **Positions:**
  - A: invert dependencies so volatile details depend on stable policy; plugins preserve policy and options (`CA`).
  - B: direct collaboration is simpler and more transparent; every interface adds a concept and can freeze a guessed variation (`CA` partial-boundary costs, FSA trade-off doctrine, DDD simplicity).
- **Hidden assumptions:** A assumes stable policy, volatile/replaceable detail, and a meaningful consumer contract; B assumes local ownership, one implementation, cohesive evolution, and cheap future refactor.
- **Evidence favoring A:** external system/framework, multiple implementations, independently evolving policy, consumer-owned contract, trust/deployment edge, difficult-to-test hard boundary.
- **Evidence favoring B:** one implementation, same owner/change cadence, no stable abstraction, local in-process call, indirection would only serve mocks.
- **Decision rule:** invert only at demonstrated policy/detail or ownership boundaries; define interfaces in the consuming policy's language and keep concrete wiring at the edge. Otherwise use direct dependencies.
- **Unresolved questions:** an anticipated but not-yet-observed implementation can justify a partial seam only when reversal cost and likelihood are both material.
- **Roles affected:** coding-agent, architecture-agent, review-agent.
- **Source support:** `CA: chapters/020-chapter-11-dip-the-dependency-inversion-principle.md :: ## STABLE ABSTRACTIONS`; `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24`; `FSA: chapters/005-chapter-1-introduction.md :: ## Laws of Software Architecture`; `DDD: chapters/012-chapter-10-supple-design.md :: # Chapter 10`.

### CONFLICT-DOM-003 — Domain purity versus implementation simplicity

- **Positions:**
  - A: isolate a domain layer and keep infrastructure/framework concepts from corrupting the model (`DDD`, `CA`).
  - B: simple Smart UI/transaction scripts/framework-native models may be faster and clearer for simple domains; mapping and purity can be waste (`DDD` explicitly; FSA entity-framework caveat).
- **Hidden assumptions:** A assumes complex enduring domain behavior and skilled expert collaboration; B assumes simple data-centric behavior, modest lifespan/ambition, or team/tool constraints.
- **Evidence favoring A:** rules duplicated across workflows; rich invariants/identity; expert language not represented; mechanism volatility; model changes drive value.
- **Evidence favoring B:** CRUD/data-entry predominates; little differentiated policy; short timeline; model ceremony already exceeds behavior; framework supplies adequate semantics.
- **Decision rule:** choose the simplest design that can express current and evidenced near-term domain complexity without duplication/corruption. State the growth ceiling. Escalate to a domain layer when repeated rules and language pressure cross it.
- **Unresolved questions:** future ambition is uncertain; preserve observations and choose a reversible packaging boundary when cheap.
- **Roles affected:** domain-agent, architecture-agent, coding-agent, review-agent.
- **Source support:** `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Domain Layer Is Where the Model Lives`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"`; `CA: chapters/033-chapter-22-the-clean-architecture.md :: ### ENTITIES`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Naked Objects and Similar Frameworks`.

### CONFLICT-ARC-004 — Uniformity versus context-sensitive design

- **Positions:**
  - A: uniform dependency direction, layering, protocols, and large-scale structure improve comprehension and enforcement (`CA`; DDD large-scale structure).
  - B: local domains and quality needs differ; forcing one model/style creates compromises and workarounds (`FSA`; DDD bounded contexts/evolving order).
- **Hidden assumptions:** A assumes repeated forces and enough semantic similarity; B assumes meaningful local variation and affordable translation/learning.
- **Evidence favoring A:** repeated same problem; cross-team maintenance; shared operational platform; uniform rule can be compiler-tested; exceptions are rare.
- **Evidence favoring B:** distinct models, quality envelopes, legacy constraints, technologies, or user communities; exceptions proliferate; uniform rule obscures domain.
- **Decision rule:** standardize only the minimum that reduces net coordination cost. Permit explicit exceptions/contexts. When exceptions become common, revise or retire the standard rather than accumulating waivers.
- **Unresolved questions:** organization-level coordination costs are hard to quantify; preserve dissent and review after actual use.
- **Roles affected:** architecture-agent, review-agent, platform/coding agents.
- **Source support:** `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## How Restrictive Should a Structure Be?`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Catering to Special Needs with Distinct Models`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `CA: chapters/033-chapter-22-the-clean-architecture.md :: #### ONLY FOUR CIRCLES?`.

### CONFLICT-ARC-005 — Services versus monolith

- **Positions:**
  - A: separate services enable independent qualities, deployment, scaling, fault/trust boundaries, and ownership (`FSA`).
  - B: in-process modules avoid network, version, observability, distributed transaction, and operational costs; services do not guarantee decoupling (`CA`, FSA).
- **Hidden assumptions:** A assumes distinct architecture quanta, operational automation, observable contracts, data ownership, and enough scale/organizational need; B assumes one deployment/quality/consistency envelope and manageable blast radius.
- **Evidence favoring A:** independent scaling/fault/security requirement; divergent availability/latency; legally separated data; release independence with owned data/contracts; operational readiness.
- **Evidence favoring B:** shared transaction/data; one team/release; modest load; manual operations; synchronous call graph; services would deploy in lockstep.
- **Decision rule:** choose monolith/module by default when one envelope suffices; distribute only the portions with demonstrated incompatible envelopes and readiness. Prefer coarse services before fine ones.
- **Unresolved questions:** future scale and organization are uncertain; preserve internal module/data boundaries to keep extraction possible without paying network cost now.
- **Roles affected:** architecture-agent, performance/durability agent, review-agent.
- **Source support:** `CA: chapters/038-chapter-27-services-great-and-small.md :: # Chapter 27`; `FSA: chapters/015-chapter-9-foundations.md :: ## Monolithic Versus Distributed Architectures`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Architecture Quantum Redux`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Monolith versus distributed`.

### CONFLICT-ARC-006 — Full boundary now versus YAGNI/partial boundary

- **Positions:**
  - A: implement a full boundary before coupling makes it prohibitively expensive (`CA`).
  - B: abstractions without actual need are costlier than underengineering; use direct design or a partial placeholder (`CA` acknowledges both; DDD minimalism).
- **Hidden assumptions:** A assumes high likelihood/late extraction cost; B assumes low likelihood/cheap refactor and discipline to watch pressure.
- **Evidence favoring A:** external ownership/trust; mandated independent deployment; already diverging changes; expensive persistent contract; high-frequency conflicting changes.
- **Evidence favoring B:** one owner and implementation; speculative alternative; small code; no independent release/quality force; full boundary types duplicate simple data.
- **Decision rule:** compare expected cost `likelihood × delayed extraction cost` against initial plus ongoing boundary cost. Use a partial boundary only with an explicit trigger and erosion check; otherwise choose direct code.
- **Unresolved questions:** probabilities are uncertain; record assumptions rather than fabricate precision.
- **Roles affected:** architecture-agent, coding-agent, review-agent.
- **Source support:** `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24`; `CA: chapters/036-chapter-25-layers-and-boundaries.md :: ### CONCLUSION`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Strategic design requires minimalism and humility`.

### CONFLICT-ARC-007 — Domain partitioning versus technical layering

- **Positions:**
  - A: domain components localize workflows and align language/change; may ease modular monolith/service evolution (`FSA`, DDD, CA package-by-component).
  - B: technical layers centralize technical policy/customization, are familiar, and can be simpler for uniform systems (`FSA`).
- **Hidden assumptions:** A assumes business capabilities evolve independently; B assumes shared technical operations dominate and cross-domain workflows are simple.
- **Evidence favoring A:** domain-specific change/co-change; independent quality scope; authorization/business rules bypass layers; data ownership can align.
- **Evidence favoring B:** simple CRUD; highly uniform transformations; one database and workflow; technical customization changes globally.
- **Decision rule:** map actual change and workflow paths. Choose the partition that minimizes cross-boundary change amplification while preserving necessary technical consistency; use nested layering inside domain components when useful.
- **Unresolved questions:** hybrid structures are often best but need clear primary ownership and enforcement.
- **Roles affected:** architecture-agent, coding-agent, review-agent.
- **Source support:** `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Architecture Partitioning`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY COMPONENT`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## The Pitfalls of Infrastructure-Driven Packaging`.

### CONFLICT-DOM-008 — One unified model versus multiple bounded contexts

- **Positions:**
  - A: one model eliminates translation, duplication, and language fragmentation; continuous integration preserves coherence.
  - B: multiple models preserve specialized meaning and team autonomy; global unification is often infeasible or harmful.
- **Hidden assumptions:** A assumes high integration value, compatible needs, and strong coordination; B assumes meaningful semantic differences and bounded integration needs.
- **Evidence favoring A:** constant cross-context operations, extensive translation, duplicated core rules, same experts/users, teams can integrate continuously.
- **Evidence favoring B:** different user communities/rules, low integration, independent ownership/technology, unification produces option-heavy compromise.
- **Decision rule:** unify only the concepts whose shared semantics and integration value exceed coordination cost. Otherwise bound contexts explicitly and select a relationship pattern. Merge first through a small tested Shared Kernel.
- **Unresolved questions:** a deeper model may later unify contexts; do not assume it will emerge.
- **Roles affected:** domain-agent, architecture-agent, legacy-agent.
- **Source support:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: # Chapter 14`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Unifying an Elephant`.

### CONFLICT-ARC-009 — Synchronous requests versus asynchronous events

- **Positions:**
  - A: synchronous calls provide determinism, immediate outcome, simpler tests/debugging and transactions.
  - B: asynchronous events provide buffering, responsiveness, extensibility, scale, and independent progress.
- **Hidden assumptions:** A assumes combined latency/availability are affordable; B assumes staleness, duplicate/reordered processing, and reconciliation are acceptable and operable.
- **Evidence favoring A:** caller needs answer now; short bounded chain; atomic failure semantics; low scale; no acceptable eventual state.
- **Evidence favoring B:** burst absorption; independent consumers; long-running work; differing capacity; user need not wait; durable retry/replay available.
- **Decision rule:** choose based on required temporal semantics. Default to the simpler synchronous interaction only while latency/availability coupling stays within budget; choose async only with complete failure/ordering/idempotency design.
- **Unresolved questions:** hybrid request acceptance plus async completion often fits, but changes user-visible semantics and requires authorization.
- **Roles affected:** architecture-agent, durability/performance agent, review-agent.
- **Source support:** `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Choosing Between Request-Based and Event-Based`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## What communication styles between services—synchronous or asynchronous?`.

### CONFLICT-ARC-010 — Choreography/broker versus orchestration/mediator

- **Positions:**
  - A: choreography/broker maximizes local autonomy, extensibility, throughput, and decoupling.
  - B: orchestration/mediator centralizes workflow visibility, error handling, recovery, and deterministic control.
- **Hidden assumptions:** A assumes simple/observable workflows and acceptable emergent completion; B assumes workflow is a coherent policy and central mediator capacity/availability are manageable.
- **Evidence favoring A:** short event chain; independent reactions; no single completion owner; frequent new consumers; high scale.
- **Evidence favoring B:** regulated/long-running transaction; compensation; human steps; explicit completion; complex conditional path; recovery/restart required.
- **Decision rule:** model business completion and error ownership first. If no component can answer whether the workflow completed correctly, use an orchestrator or add explicit process state. If the reactions are genuinely independent, choreography is simpler.
- **Unresolved questions:** distributed process managers blur the binary; evaluate actual failure and evolution cost.
- **Roles affected:** architecture-agent, durability/debugging agent.
- **Source support:** `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Broker Topology`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Mediator Topology`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Choreography and Orchestration`.

### CONFLICT-DOM-011 — Shared Kernel versus Anticorruption Layer versus Conformist

- **Positions:**
  - A: Shared Kernel minimizes translation but requires close bilateral coordination.
  - B: ACL preserves local meaning but costs translation and maintenance.
  - C: Conformist eliminates translation by accepting upstream meaning but sacrifices local freedom.
- **Hidden assumptions:** A assumes mutual control/trust; B assumes local model value exceeds translation cost; C assumes upstream is stable/good enough and downstream lacks leverage.
- **Evidence favoring each:** A—small stable overlap, frequent cooperation, integrated tests; B—model conflict, necessary integration, valuable local core, poor/uncontrolled upstream; C—broad upstream interface, acceptable semantics, no supplier cooperation, prohibitive translator.
- **Decision rule:** choose based on actual control and economics, not emotional preference for independence. Reassess if cooperation, interface breadth, or model quality changes.
- **Unresolved questions:** relationship can differ by subdomain; do not force one choice across the entire integration.
- **Roles affected:** domain-agent, legacy-agent, architecture-agent.
- **Source support:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Conformist`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Anticorruption Layer`.

### CONFLICT-ARC-012 — Abstraction/reuse versus duplication/local clarity

- **Positions:**
  - A: shared abstractions reduce duplicated behavior and coordinate consistency.
  - B: local duplication preserves independent change and avoids premature common contracts.
- **Hidden assumptions:** A assumes same semantics and coordinated evolution; B assumes coincidental similarity or divergent actors/contexts.
- **Evidence favoring A:** repeated defect/rule in several consumers; changes always co-occur; stable shared semantics; multiple proven reusers.
- **Evidence favoring B:** different actors/rules; similarity is syntactic; shared change has already caused accidental coupling; abstraction would expose unused operations.
- **Decision rule:** tolerate duplication until semantic commonality and variation are demonstrated. Share policy, not merely code shape; do not share across contexts without explicit governance.
- **Unresolved questions:** duplication can be a discovery mechanism; set a revisit trigger rather than a universal count.
- **Roles affected:** coding-agent, architecture-agent, refactoring-agent, domain-agent.
- **Source support:** `CA: chapters/016-chapter-7-srp-the-single-responsibility-principle.md :: ## SYMPTOM 1: ACCIDENTAL DUPLICATION`; `CA: chapters/027-chapter-16-independence.md :: ### DUPLICATION`; `CA: chapters/023-chapter-13-component-cohesion.md :: ### THE COMMON REUSE PRINCIPLE`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`.

### CONFLICT-DOM-013 — Model fidelity versus performance/data constraints

- **Positions:**
  - A: keep model, code, and persistence mapping transparent to preserve meaning and refactorability.
  - B: optimized data shapes, caching, denormalization, service boundaries, or alternate computational models may be necessary for throughput/latency/scale.
- **Hidden assumptions:** A assumes simple mappings meet performance; B assumes measured bottleneck and semantic-preserving translation.
- **Evidence favoring A:** no measured issue; model churn high; mapping complexity creates defects; direct implementation meets budgets.
- **Evidence favoring B:** realistic profile/benchmark shows budget violation; known algorithm/data-layout advantage; translation can be characterized/tested.
- **Decision rule:** begin with direct model-aligned implementation; optimize only measured bottlenecks behind a semantic boundary, retaining a clear translation and baseline/regression test.
- **Unresolved questions:** sometimes the optimized representation reveals a better domain model; validate with experts rather than treating all divergence as technical.
- **Roles affected:** domain-agent, performance-agent, architecture-agent, coding-agent.
- **Source support:** `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Designing Objects for Relational Databases`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Two C***ONTEXTS* **in a Shipping Application`; `DDD: chapters/008-chapter-7-using-the-language-an-extended-example.md :: ## Performance Tuning`; `FSA: chapters/021-chapter-15-space-based-architecture-style.md :: # Chapter 15`.

### CONFLICT-ARC-014 — Architectural constraint versus team autonomy

- **Positions:**
  - A: explicit constraints and governance prevent drift and unsafe local optimization.
  - B: excessive control prevents implementers from adapting details and destroys feedback/productivity.
- **Hidden assumptions:** A assumes inexperienced/large team, high complexity, or high-risk invariant; B assumes experienced cohesive team and clear outcome contracts.
- **Evidence favoring A:** repeated violations; junior/large/new team; safety/security risk; complex project; long duration.
- **Evidence favoring B:** small experienced familiar team; simple/short project; strong tests/feedback; constraints specify implementation rather than outcomes.
- **Decision rule:** constrain architecturally significant outcomes and forbidden dependencies, not every method/class. Calibrate guidance to team familiarity, size, experience, project complexity/duration, and risk; revisit.
- **Unresolved questions:** FSA's numeric personality scale is pedagogical and should not become an automated authority score.
- **Roles affected:** architecture-agent, coding-agent, agent-conduct/review.
- **Source support:** `FSA: chapters/029-chapter-22-making-teams-effective.md :: ## Team Boundaries`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: ## How Much Control?`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The decision process must absorb feedback`.

## Decision-procedure candidates

These are deterministic candidates for the architecture and domain-design lanes. A procedure may return **leave unchanged**; generating a structural proposal is not a success criterion.

### PROC-ARC-001 — Assess architectural pressure

- **Inputs:** requested outcome; repository contracts and accepted decisions; current structural/deployment/data boundaries; change history; tests; incidents and runtime measurements; team and operational constraints; agent authority.
- **Evidence required:** at least one named architectural driver or recurring system-level failure whose effect crosses a local implementation seam. A quality-attribute claim needs a concrete stimulus, environment, response, and measurable response threshold.
- **Decision steps:**
  1. Classify the requested work (feature, repair, refactoring, migration, optimization, or architectural restructuring) and its permitted semantics.
  2. Separate observations from inferred causes. Record the current behavior and preservation boundary.
  3. Name each alleged driver: change amplification, deployment coupling, invariant ownership, latency, throughput, availability, security, durability, organizational coordination, or domain-language conflict.
  4. Scope each driver to the smallest affected component or architectural quantum; do not assume it is system-wide.
  5. Seek corroboration from a second evidence class when the proposed response is expensive or hard to reverse.
  6. Compare four candidates: no change, local implementation change, modular/boundary change, and style/deployment change.
  7. Estimate introduced coordination, runtime, migration, testing, and operational costs plus reversal path.
  8. Select the least costly candidate that satisfies the measured driver and repository contracts.
- **Outputs:** evidence ledger; scoped drivers and thresholds; preservation boundary; selected/no-change outcome; rejected alternatives; risks; verification and reversal plan; confidence.
- **Stop conditions:** no driver beyond taste; pressure is local; repository contract forbids the change; baseline is missing; or the agent has assessment-only authority.
- **Escalation conditions:** behavior or data semantics would change; ownership/deployment topology changes; accepted decisions must be superseded; regulated qualities are implicated; evidence remains contested.
- **Common false positives:** file size, directory shape, fashionable style mismatch, churn without cause analysis, a single difficult test, diagram asymmetry, and a quality adjective without a scenario.
- **Source support:** `FSA: chapters/010-chapter-5-identifying-architectural-characteristics.md :: ## Extracting Architecture Characteristics from Domain Concerns`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `CA: chapters/008-chapter-1-what-is-design-and-architecture.md :: ## THE GOAL?`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The decision process must absorb feedback`.

### PROC-ARC-002 — Select an architectural boundary and its strength

- **Inputs:** independently changing policies; consumers/providers; domain invariants; data and authority ownership; release/deployment needs; runtime communication budget; current dependency graph; candidate seam.
- **Evidence required:** demonstrated independent evolution, asymmetric volatility, ownership/authority separation, incompatible models, required substitution, or deployment/runtime isolation. A test double alone earns at most a local seam unless production forces corroborate it.
- **Decision steps:**
  1. State what must vary independently and who causes each variation.
  2. Identify data and behavior that must remain cohesive to preserve invariants.
  3. Draw the narrowest semantic contract, including failure and temporal semantics.
  4. Compare direct call, facade/module seam, dependency-inverted in-process interface, deployable component, local process, and remote service.
  5. Price each crossing: translation, versioning, latency, partial failure, observability, testing, release coordination, and team ownership.
  6. Choose the cheapest strength that absorbs the demonstrated pressure; keep a route to strengthen later if the trigger is plausible.
  7. Define forbidden dependencies and automated checks only for invariants whose violation would matter.
- **Outputs:** boundary decision; contract owner; allowed dependency direction; crossing data; chosen strength; rejected strengths; migration/reversal triggers; verification.
- **Stop conditions:** responsibilities change together; no stable semantic contract exists; separation weakens an invariant; or direct coupling fits the volatility and ownership.
- **Escalation conditions:** remote distribution, public API, database ownership transfer, cross-team authority, or irreversible schema/protocol commitment is required.
- **Common false positives:** interface-per-class, service-per-entity, testability treated as deployability, package names treated as contexts, and independence claimed without separate changes or owners.
- **Source support:** `CA: chapters/028-chapter-17-boundaries-drawing-lines.md :: ## WHICH LINES DO YOU DRAW, AND WHEN DO YOU DRAW THEM?`; `CA: chapters/029-chapter-18-boundary-anatomy.md :: ## BOUNDARY CROSSING`; `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`.

### PROC-ARC-003 — Determine whether dependency inversion or an interface is earned

- **Inputs:** concrete dependency; volatility and ownership on each side; consumers; implementation count; substitution need; test strategy; deployment boundary; language conventions.
- **Evidence required:** one or more of: multiple real implementations, consumer-defined stable need narrower than provider, high-level policy threatened by volatile detail, independent release/deployment, explicit policy/mechanism split, or a necessary legacy interception seam.
- **Decision steps:**
  1. Write the direct dependency and the concrete harm it causes now.
  2. Check whether moving behavior/data ownership removes the harm without indirection.
  3. Define the smallest consumer-needed contract and its semantic obligations.
  4. Verify that the contract is more stable than the implementation and does not expose implementation detail.
  5. Compare direct dependency, local adapter/function, facade, and polymorphic interface.
  6. Introduce indirection only if the expected independent changes exceed naming, navigation, mocking, compatibility, and lifecycle cost.
  7. Set deletion/review triggers for single-use or temporary seams.
- **Outputs:** direct-coupling decision or minimal contract; contract owner; evidence; costs; tests; removal/review trigger.
- **Stop conditions:** only aesthetic decoupling is claimed; variation is hypothetical; repository idiom favors concrete/function injection; or inversion merely relocates a cycle.
- **Escalation conditions:** public contract or cross-team protocol; framework replacement; behavior-visible error/latency change.
- **Common false positives:** every dependency is a boundary; mocking proves design value; an interface makes a network call local; and a provider-owned broad interface counts as dependency inversion.
- **Source support:** `CA: chapters/017-chapter-8-ocp-the-open-closed-principle.md :: ## DIRECTIONAL CONTROL`; `CA: chapters/020-chapter-11-dip-the-dependency-inversion-principle.md :: ## STABLE ABSTRACTIONS`; `CA: chapters/028-chapter-17-boundaries-drawing-lines.md :: ### PLUGIN ARCHITECTURE`; `FSA: chapters/008-chapter-3-modularity.md :: ## From Modules to Components`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Services`.

### PROC-ARC-004 — Define and scope architecture characteristics

- **Inputs:** explicit requirements; domain concerns; stakeholder priorities; operational SLOs; regulatory constraints; component/data topology; known trade-offs.
- **Evidence required:** each characteristic must be explicit or traceable to a domain/operational concern, influence structural design, and be important to system success. A measurable scenario or test proxy must exist or be proposed.
- **Decision steps:**
  1. Extract candidate characteristics from explicit statements and domain verbs/risks; mark inference as inference.
  2. Remove qualities that do not affect structure or are already universal project expectations.
  3. Define stimulus, operating environment, affected scope, desired response, and threshold.
  4. Scope globally only if every quantum must satisfy it; otherwise attach it to the relevant component/flow.
  5. Limit the set to the smallest differentiating drivers and expose conflicts (for example security versus usability, consistency versus availability).
  6. Select measurement/fitness functions and baseline them before changing structure.
  7. Obtain stakeholder acceptance for priorities and thresholds.
- **Outputs:** prioritized/scoped characteristic scenarios; evidence and owner; measurement method; trade-off ledger; acceptance status.
- **Stop conditions:** only adjectives exist; no structural consequence; threshold cannot yet be defined; stakeholder priority is unknown.
- **Escalation conditions:** conflicting stakeholders, regulated thresholds, or a characteristic requires a different deployment/data topology.
- **Common false positives:** maximizing every quality, treating maintainability as unbounded, system-wide scope by default, and confusing feature requirements with architecture drivers.
- **Source support:** `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Architectural Characteristics (Partially) Listed`; `FSA: chapters/010-chapter-5-identifying-architectural-characteristics.md :: ## Extracting Architecture Characteristics from Requirements`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Governing Architecture Characteristics`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`.

### PROC-ARC-005 — Choose monolith, modular monolith, or distributed deployment

- **Inputs:** domain and change partitions; data consistency needs; scale/elasticity profile; availability/isolation needs; geographic constraints; team ownership; deployment cadence; operational maturity; latency budget; security/regulatory boundary.
- **Evidence required:** distribution requires a driver that cannot be met economically in-process plus readiness for networking, observability, versioning, independent data, automation, and partial failure. Modularization requires independent change semantics, not separate deployment.
- **Decision steps:**
  1. Establish the simplest deployable topology meeting current thresholds.
  2. Model transactions, joins, failure propagation, latency, and coordination in the hottest cross-boundary workflows.
  3. Check whether modular in-process boundaries meet change/team needs without network cost.
  4. For proposed services, assign data ownership and prove the absence or explicit handling of distributed transactions.
  5. Assess deployment automation, tracing/metrics/logging, on-call skill, capacity planning, compatibility, and incident recovery.
  6. Compare total cost and reversal path for monolith, modular monolith, coarse services, and fine-grained services.
  7. Distribute only the quanta whose drivers earn it; avoid system-wide style purity.
- **Outputs:** chosen topology per quantum; readiness gaps; workflow/failure model; data ownership; migration/reversal plan; verification thresholds.
- **Stop conditions:** the only rationale is fashion, team-size folklore, directory modularity, or hoped-for future scale; transaction/data ownership is unresolved.
- **Escalation conditions:** public deployment changes, data migration, new operational ownership, consistency semantics, or cost envelope changes.
- **Common false positives:** services imply decoupling, multiple repositories imply independent release, asynchronous messaging eliminates coupling, and deployment scalability fixes inefficient algorithms.
- **Source support:** `CA: chapters/029-chapter-18-boundary-anatomy.md :: ### SERVICES`; `CA: chapters/038-chapter-27-services-great-and-small.md :: ### SERVICE BENEFITS?`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Monolith versus distributed`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Transactions and Sagas`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`.

### PROC-ARC-006 — Select an architecture style or hybrid

- **Inputs:** scoped architecture characteristics; domain topology; data and transaction needs; workflow temporal semantics; team/operational constraints; existing style; migration budget.
- **Evidence required:** ranked drivers and realistic workflow examples. Every candidate must be evaluated for its introduced costs and not just its favorable characteristic ratings.
- **Decision steps:**
  1. Treat the existing style and no structural change as candidates.
  2. Eliminate styles whose core topology conflicts with hard constraints.
  3. Compare layered, pipeline, microkernel, service-based, event-driven, space-based, orchestration-driven, and microservices only where their solved problem matches a driver.
  4. Walk at least one normal, failure, recovery, deployment, and evolution scenario through each finalist.
  5. Account for data, communication, observability, testing, versioning, staffing, and migration.
  6. Select per architectural quantum; document intentional hybrid seams and their semantics.
  7. Define fitness functions and reversal signals.
- **Outputs:** selected style per scope; rationale and trade-offs; rejected alternatives; hybrid interfaces; operational and migration plan; ADR candidate.
- **Stop conditions:** drivers are not ranked; evidence is purely trend/preference; operational consequences are unknown; a local module solves the issue.
- **Escalation conditions:** the style changes external contracts, deployment model, persistence/consistency, or staffing/operations.
- **Common false positives:** one style for the whole enterprise, numeric ratings treated as proof, copying a reference diagram, and selecting microservices merely because bounded contexts exist.
- **Source support:** `FSA: chapters/015-chapter-9-foundations.md :: ## Fundamental Patterns`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `CA: chapters/027-chapter-16-independence.md :: ### DECOUPLING MODES (AGAIN)`.

### PROC-DOM-007 — Decide whether strategic/tactical domain modeling is earned

- **Inputs:** business differentiation; rule/invariant complexity; language ambiguity; domain-expert access; expected product life and change; implementation team capability; integration landscape.
- **Evidence required:** strategic DDD requires business-critical complexity and a sustainable expert/developer learning loop. Tactical patterns require a specific identity, invariant, lifecycle, or boundary problem.
- **Decision steps:**
  1. Classify the area as differentiating core, supporting, generic, or simple data workflow.
  2. Identify actual ambiguity, contradiction, recurring rule defects, and change cost.
  3. Confirm access to experts and a cadence for model experimentation and correction.
  4. Compare direct transaction script/Smart UI, modest domain module, and deep model.
  5. Add only tactical constructs whose semantics are present; do not adopt the pattern vocabulary as a package template.
  6. Concentrate modeling effort on the core and integrate/buy generic capabilities where economics favor it.
  7. Set learning checkpoints and stop if the model ceases to improve communication or code.
- **Outputs:** investment decision by subdomain; expected learning loop; selected tactical constructs; exclusions; revisit trigger.
- **Stop conditions:** simple CRUD/reporting; no expert access; short-lived utility; model work has no decision or code consequence; ceremony exceeds domain complexity.
- **Escalation conditions:** model changes public language/behavior, creates team or data boundaries, or contradicts accepted domain contracts.
- **Common false positives:** many database tables, industry jargon, rich object graphs, entity suffixes, and the presence of microservices.
- **Source support:** `DDD: chapters/002-chapter-1-crunching-knowledge.md :: ## Knowledge Crunching`; `DDD: chapters/003-chapter-2-communication-and-the-use-of-language.md :: ## Ubiquitous Language`; `DDD: chapters/011-chapter-9-making-implicit-concepts-explicit.md :: # Chapter 9`; `DDD: chapters/017-chapter-15-distillation.md :: ## Core Domain`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Strategic design requires minimalism and humility`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"`.

### PROC-DOM-008 — Identify a bounded context or domain boundary

- **Inputs:** domain language from experts/artifacts; workflows; invariants; policies; identity definitions; data/authority ownership; team/change history; integrations; existing models.
- **Evidence required:** a boundary candidate needs a coherent model internally and a demonstrable discontinuity externally: term meaning, rule, identity, lifecycle, ownership, cadence, or authority. Directory names alone are insufficient.
- **Decision steps:**
  1. Build a glossary with examples and record terms whose meaning changes by speaker/workflow.
  2. Trace critical decisions and invariants to the people/systems authorized to define them.
  3. Map workflows and data, distinguishing shared facts from shared representation.
  4. Identify clusters in which one model is consistent and useful.
  5. Test candidate boundaries against real changes and scenarios; merge if translation adds no value, split if one term/rule cannot remain coherent.
  6. Name each context in business language and state its model, owner, inputs/outputs, and non-goals.
  7. Choose an explicit relationship for every necessary crossing.
- **Outputs:** context map candidate; glossary and semantic conflicts; owners; invariants; translations; confidence and unresolved questions.
- **Stop conditions:** only structural/code evidence exists; expert usage is unobserved; boundary is inferred from database/schema alone; proposed split has no semantic or ownership discontinuity.
- **Escalation conditions:** ownership reorganization, public vocabulary change, database split, or cross-team contract is proposed.
- **Common false positives:** one context per service/team/table/entity, identical names imply identical concepts, and all enterprise data should share one canonical model.
- **Source support:** `DDD: chapters/003-chapter-2-communication-and-the-use-of-language.md :: ## Ubiquitous Language`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Context Map`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Discovering Components`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Bounded Context`.

### PROC-DOM-009 — Select a context relationship and integration pattern

- **Inputs:** two contexts; upstream/downstream direction; control and negotiation power; semantic distance; integration breadth/frequency; local model value; reliability/performance needs; ownership.
- **Evidence required:** observed model mismatch, coordination reality, and interface economics. Pattern selection must correspond to the actual organizational relationship.
- **Decision steps:**
  1. Establish upstream/downstream and who can change which contract.
  2. Enumerate semantic mismatches and the local rules that would be polluted or lost.
  3. Assess cooperation, trust, release coordination, interface breadth, and translator cost.
  4. Choose among Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Separate Ways, or Open Host Service/Published Language.
  5. Define translation ownership, versioning, failure handling, and conformance tests.
  6. Limit the relationship to the relevant subdomains; different crossings may use different patterns.
  7. Set reassessment triggers when control, quality, or integration breadth changes.
- **Outputs:** relationship decision; contract/translation; ownership; accepted semantic loss; operational behavior; tests; revisit trigger.
- **Stop conditions:** no necessary integration; same model and coordinated ownership make translation redundant; organizational relationship is unknown.
- **Escalation conditions:** public protocol, shared ownership agreement, accepted semantic loss, or supplier negotiation is required.
- **Common false positives:** ACL as mandatory cleanliness, Shared Kernel as a common utility library, Conformist as negligence, and a published schema as automatically a Published Language.
- **Source support:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Customer/Supplier Development Teams`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Conformist`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Anticorruption Layer`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Separate Ways`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Open Host Service`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Published Language`.

### PROC-DOM-010 — Establish aggregate and transaction preservation boundaries

- **Inputs:** business invariants; commands and concurrency; identity/lifecycle; transaction capabilities; consistency tolerance; access paths; performance and contention measurements.
- **Evidence required:** an aggregate groups only state that must be kept consistent by one authorized operation/transaction. Convenience navigation or object containment is insufficient.
- **Decision steps:**
  1. Express each invariant in domain language and identify the commands that can violate it.
  2. Determine what must be atomically observed/changed and what may be eventually reconciled.
  3. Choose the smallest root that can enforce the atomic invariants.
  4. Make external references use identity unless direct containment is necessary for the invariant.
  5. Define creation/reconstitution through factory/repository only where lifecycle complexity earns them.
  6. Test concurrent, failure, retry, and partial-update scenarios.
  7. Measure contention and load; split only if semantics permit and measured pressure earns weaker consistency.
- **Outputs:** aggregate root/boundary; invariant list; transaction and consistency semantics; allowed references; repository/factory decision; tests and performance risks.
- **Stop conditions:** invariant is not known; boundary is only an ORM graph; proposal broadens transaction without semantic need.
- **Escalation conditions:** consistency weakens, data migration occurs, external behavior changes, or distributed transaction/saga is introduced.
- **Common false positives:** aggregate per entity, aggregate as collection, repository per table, persistence cascade as domain invariance, and eventual consistency chosen only for scale folklore.
- **Source support:** `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Factories`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Repositories`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Transactions and Sagas`.

### PROC-ARC-011 — Choose synchronous, asynchronous, brokered, or mediated interaction

- **Inputs:** required response timing; completion owner; ordering and delivery semantics; transaction scope; load shape; consumer independence; retry/idempotency; observability/recovery; latency/availability budgets.
- **Evidence required:** temporal and failure semantics for the workflow, not merely a desire to “decouple.” Async requires explicit loss, duplicate, ordering, poison-message, replay, and reconciliation handling.
- **Decision steps:**
  1. State when the initiator needs a result and what “complete” means.
  2. Trace normal, timeout, duplicate, reordered, partial, and recovery paths.
  3. Use synchronous calls for bounded immediate answers when combined latency/availability fit budgets.
  4. Use async for independent progress, burst absorption, or long work only with durable handling and user-visible state semantics.
  5. If reactions are independent and no global completion policy exists, consider broker/choreography.
  6. If completion, compensation, conditional routing, or audit requires an owner, use mediator/orchestrator/process state.
  7. Baseline end-to-end latency, loss/retry, queue age, and recovery; test failure modes.
- **Outputs:** interaction decision; temporal/failure contract; workflow owner; delivery/order/idempotency rules; observability and recovery plan.
- **Stop conditions:** semantics are unspecified; event is merely a remote command disguised as notification; no recovery owner; synchronous path already meets needs.
- **Escalation conditions:** user-visible completion semantics change; consistency weakens; new infrastructure/on-call obligations; cross-team protocol.
- **Common false positives:** async equals faster, events eliminate coupling, exactly-once is assumed, brokers guarantee business completion, and orchestration is always a bottleneck.
- **Source support:** `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Asynchronous Capabilities`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Error Handling`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Preventing Data Loss`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Choosing Between Request-Based and Event-Based`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Choreography and Orchestration`.

### PROC-ARC-012 — Record, authorize, verify, and revisit an architecture decision

- **Inputs:** decision scope; observations/inferences; alternatives; drivers; repository contracts; authority matrix; stakeholders; verification and reversal options.
- **Evidence required:** an ADR-worthy decision is structurally significant, cross-cutting, expensive to reverse, or constraining to future agents/teams. The selected option needs evidence tied to ranked drivers.
- **Decision steps:**
  1. State status, context, decision, scope, owner, and date; distinguish proposal, authorization, and execution.
  2. Record all viable alternatives, why each was rejected now, and assumptions.
  3. Describe positive and negative consequences, migration, operations, security/durability, and reversal cost.
  4. Define measurable verification and review triggers.
  5. Obtain authorization at the level required by repository governance; an assessment agent stops at proposal.
  6. After implementation, verify thresholds and preservation boundaries independently of design intent.
  7. Supersede rather than silently rewrite accepted history when assumptions change.
- **Outputs:** proposed/accepted/superseded ADR; evidence links; authority record; implementation and verification gates; revisit triggers.
- **Stop conditions:** issue is local/reversible and does not constrain others; authority absent; evidence does not distinguish alternatives.
- **Escalation conditions:** accepted contract changes, semantic behavior/data ownership shifts, irreversible commitment, or stakeholders disagree.
- **Common false positives:** an email/diagram as durable decision, decision title without context, “best practice” as rationale, implementation treated as authorization, and tests treated as acceptance.
- **Source support:** `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecture Decision Records`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Storing ADRs`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Decisions must reach the entire team`.

### PROC-ARC-013 — Risk-storm a proposed architecture proportionately

- **Inputs:** architecture/components; critical user journeys; scoped characteristics; participants from architecture, implementation, operations, security/domain; existing controls and incidents.
- **Evidence required:** architecture diagram and characteristic scenarios detailed enough to locate risk; participants must include people with implementation/operational knowledge.
- **Decision steps:**
  1. Select only the characteristics and flows whose failure matters for the decision.
  2. Have participants independently identify component/interaction risks to avoid premature consensus.
  3. Discuss, merge, and score likelihood/impact with explicit uncertainty.
  4. Trace highest risks through dependencies and operational controls.
  5. Choose mitigation, experiment, acceptance, transfer, or avoidance with owner and deadline.
  6. Convert mitigations into verification gates; rescore after evidence.
- **Outputs:** risk matrix and rationale; disputed scores; mitigations/owners; experiments; residual-risk acceptance authority.
- **Stop conditions:** no concrete architecture/flow; exercise becomes generic brainstorming; mitigation authority/owner absent.
- **Escalation conditions:** high residual safety/security/durability risk; acceptance exceeds agent authority; participants disagree on critical assumptions.
- **Common false positives:** averaging scores into false certainty, treating risk as a defect, scoring every component equally, and mitigation without verification.
- **Source support:** `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Risk Matrix`; `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Risk Storming`; `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Agile Story Risk Analysis`.

### PROC-ARC-014 — Define architecture fitness and leave-code-alone criteria

- **Inputs:** accepted decision and drivers; measurable characteristic scenarios; preservation boundary; current baseline; change frequency/risk; test and telemetry capabilities.
- **Evidence required:** a fitness function must protect a named accepted outcome and have a signal sufficiently related to that outcome. Proxy metrics need documented limits.
- **Decision steps:**
  1. For each accepted decision, identify observable behavior or structural rule whose drift would matter.
  2. Prefer end-to-end outcome measures; add structural checks only for enforceable dependency/contract rules.
  3. Establish baseline, tolerance, noise, execution cadence, owner, and response.
  4. Include normal/failure/recovery behavior and domain invariant tests where relevant.
  5. Verify after implementation and during operation; distinguish passing checks from stakeholder acceptance.
  6. If current thresholds pass, no recurring change pressure exists, and intervention adds risk without authorized benefit, return leave unchanged with revisit triggers.
  7. Delete or revise stale checks when the decision is superseded.
- **Outputs:** fitness suite/telemetry plan; baseline and thresholds; ownership; no-change decision or detected drift; revisit trigger.
- **Stop conditions:** proxy cannot establish the claim; no accepted outcome; check would freeze implementation detail; baseline absent.
- **Escalation conditions:** threshold/priorities need stakeholder approval; verification reveals semantic regression; monitoring introduces sensitive-data or operational cost.
- **Common false positives:** coverage or coupling metric as architecture proof, tests as proof of independent deployability, passing benchmark as user acceptance, and unattractive code as sufficient pressure.
- **Source support:** `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`; `FSA: chapters/008-chapter-3-modularity.md :: ## Measuring Modularity`; `CA: chapters/008-chapter-1-what-is-design-and-architecture.md :: ## CASE STUDY`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The decision process must absorb feedback`.

## Architectural-technique evidence ledger

Ratings and pattern names are candidate vocabulary, never default selections. “Reversal” describes the likely exit path, not a promise that reversal is cheap.

| ID / technique | Problem it can solve | Evidence that earns it | Introduced costs | Contraindications | Reversal / appropriate scale / operational consequences | Source support |
|---|---|---|---|---|---|---|
| TECH-ARC-001 — Direct in-process dependency | Local collaboration with shared lifecycle and no meaningful volatility/ownership split. | Same owner, release, failure domain, and change cadence; concrete semantics stable; latency and atomicity valuable. | Compile-time/change coupling; future extraction may need adapter. | Volatile provider controls stable policy; public/cross-team contract; independent deployment or substitution is required. | Easiest initial form; later extract behind measured seam. Suitable from function through modular monolith. Minimal network/operations cost. | `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES`; `FSA: chapters/015-chapter-9-foundations.md :: ### Monolithic` |
| TECH-ARC-002 — Layered architecture | Organize technically similar concerns and constrain calls through a familiar monolith. | Simple/standard business workflow; technically partitioned team/repository; low deployment and domain partition pressure. | Change can traverse layers; sinkhole pass-through; domain behavior can become anemic; shared deployment/database. | Independent domain change/deployability is primary; high scale/availability isolation; layers have no distinct responsibility. | Easy to start, moderate to repartition because features are scattered. Small-to-medium monolith; simple operations, limited fault isolation. | `FSA: chapters/016-chapter-10-layered-architecture-style.md :: ## Topology`; `FSA: chapters/016-chapter-10-layered-architecture-style.md :: ## Why Use This Architecture Style`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ## PACKAGE BY LAYER` |
| TECH-ARC-003 — Package/component by domain feature | Keep a use case/domain capability locally understandable and restrict accidental cross-feature access. | Feature changes traverse technical layers; recognizable cohesive capability; package/module encapsulation can be enforced. | Some technical duplication; boundary naming/ownership; shared infrastructure adapters still need placement. | Feature has no coherent semantics; language/runtime cannot enforce access and project will not add checks; tiny utility. | Usually reversible module moves; feature/module-to-modular-monolith scale. No inherent deployment cost. | `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY FEATURE`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY COMPONENT`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ### Domain partitioning` |
| TECH-ARC-004 — Ports and adapters / policy-detail boundary | Protect stable application/domain policy from volatile delivery, storage, framework, or device mechanisms. | Policy has independent tests/evolution; multiple/adaptable mechanisms; volatile framework/device; explicit inward contract can be smaller and stable. | Mapping, indirection, extra types, composition wiring, possible duplicated representations. | CRUD/trivial workflow; mechanism semantics dominate; hypothetical portability; public exposure of internal test seams. | Reversible by collapsing adapters, though representations may have spread. Module to system scale. Operational topology unchanged unless adapters are remote. | `CA: chapters/033-chapter-22-the-clean-architecture.md :: ## THE DEPENDENCY RULE`; `CA: chapters/034-chapter-23-presenters-and-humble-objects.md :: ## THE HUMBLE OBJECT PATTERN`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ## PORTS AND ADAPTERS` |
| TECH-ARC-005 — Partial boundary / facade | Reserve a likely seam or control dependency at less cost than a fully deployable boundary. | Pressure is plausible and localized, but independent deployment/dual implementation is not yet earned; delaying every structure would make later separation materially harder. | Some indirection without full independence; false sense of protection; future completion still costs work. | No concrete likely variation; facade hides no meaningful complexity; boundary needs actual runtime isolation now. | Delete or complete; local/module scale. Little operational cost, but one-dimensional seams can permit reverse coupling. | `CA: chapters/035-chapter-24-partial-boundaries.md :: ## SKIP THE LAST STEP`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### ONE-DIMENSIONAL BOUNDARIES`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES` |
| TECH-ARC-006 — Dependency inversion / consumer-owned port | Reverse source dependency so stable policy is not forced to depend on volatile mechanism. | Asymmetric volatility; consumer need is narrower/more stable; multiple implementation/substitution/deployment; necessary test/legacy seam. | Interface ownership/versioning, navigation, adapters, mocks, lifecycle complexity. | Single stable dependency; interface mirrors provider; no independent variation; repository idiom uses functions/concrete injection more clearly. | Collapse to direct adapter if pressure disappears. Function/module/component scale. Remote use adds protocol/operations not supplied by DIP itself. | `CA: chapters/020-chapter-11-dip-the-dependency-inversion-principle.md :: ## STABLE ABSTRACTIONS`; `CA: chapters/017-chapter-8-ocp-the-open-closed-principle.md :: ## DIRECTIONAL CONTROL` |
| TECH-ARC-007 — Plugin / microkernel | Stable core must support independently varying, optional, or customer-specific capabilities. | Multiple real plugins; stable core contract; runtime/configurable extension; product variants or tools need isolation. | Registry/discovery, compatibility/security, versioned contracts, weaker cross-plugin transactions, debugging. | One implementation; core cannot be kept small/stable; plugins require pervasive internal access; strong atomic workflow. | Plugins can be folded into core; contract consumers raise reversal cost. Product/tool or bounded system scale. Requires plugin lifecycle, compatibility, isolation, and observability. | `CA: chapters/028-chapter-17-boundaries-drawing-lines.md :: ### PLUGIN ARCHITECTURE`; `FSA: chapters/018-chapter-12-microkernel-architecture-style.md :: ## Topology`; `FSA: chapters/018-chapter-12-microkernel-architecture-style.md :: ## Contracts` |
| TECH-ARC-008 — Pipeline | Transform/test a stream through ordered, largely independent stages. | Processing is naturally sequential; stages have narrow data contracts; reuse/reordering/parallelization matters; stage side effects are controlled. | Intermediate representations; ordering/error semantics; backpressure; cross-stage debugging and observability. | Rich shared transactional state; interactive branching workflow; transformations cannot be isolated. | Compose/collapse stages; application/subsystem scale. Streaming pipelines need buffering, retry, checkpoint, ordering, and backpressure operations. | `FSA: chapters/017-chapter-11-pipeline-architecture-style.md :: ## Pipes`; `FSA: chapters/017-chapter-11-pipeline-architecture-style.md :: ## Filters` |
| TECH-ARC-009 — Modular monolith | Domain/change modules need strong source boundaries without distributed-system costs. | Cohesive modules; shared deployment/transactions acceptable; teams can coordinate releases; operations simplicity is valuable. | Shared process/database failure and deployment; boundaries require discipline/tooling; scale often coarse. | Independent availability/geography/security/deployability is mandatory; one module dominates incompatible resource needs. | Extract selected modules later through explicit ports/data ownership. Product/system scale. Single deployment/observability domain, simpler transactions. | `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Modular Monolith`; `CA: chapters/029-chapter-18-boundary-anatomy.md :: ### THE DREADED MONOLITH`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY COMPONENT` |
| TECH-ARC-010 — Service-based architecture | Coarse domain areas need some independent deployment/scale while preserving simpler shared-database/operations. | A few coarse domains; moderate elasticity/agility; team owns whole service; shared data trade-off accepted. | Network latency/failure; contract versioning; shared DB coordination; service orchestration; distributed logging. | Strong data isolation; fine-grained independent scaling; unresolved cross-service transactions; no operational maturity. | Merge services or split further; system scale. Requires service deployment, monitoring, security, API compatibility, and failure handling. | `FSA: chapters/019-chapter-13-service-based-architecture-style.md :: ## Topology`; `FSA: chapters/019-chapter-13-service-based-architecture-style.md :: ## When to Use This Architecture Style` |
| TECH-ARC-011 — Event broker / choreography | Independent reactions and high-throughput event flow need extensibility and loose temporal coupling. | No single workflow owner; simple independent reactions; consumer addition is frequent; durable messaging/replay and idempotency available. | Emergent flow, difficult completion/error visibility, duplicates/order, eventual consistency, tracing and schema evolution. | Regulated/deterministic long workflow; compensation/explicit completion required; weak observability; events are commands in disguise. | Add process manager/mediator or return to direct request; subsystem/system scale. Requires broker availability, DLQ/replay, schema governance, lag and trace operations. | `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Broker Topology`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Error Handling`; `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Preventing Data Loss` |
| TECH-ARC-012 — Event mediator / orchestration | Multi-step workflow needs explicit completion, conditional routing, compensation, audit, and recovery ownership. | Long-running/regulated transaction; branches/human steps; recovery/restart; one business process owns completion. | Mediator availability/scale; central coupling; workflow versioning; process-state persistence; bottleneck risk. | Reactions genuinely independent; workflow is short/direct; mediator would merely relay every message. | Decentralize stable independent reactions; process/system scale. Requires durable process state, idempotency, compensation, observability, and upgrade strategy. | `FSA: chapters/020-chapter-14-event-driven-architecture-style.md :: ## Mediator Topology`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Choreography and Orchestration` |
| TECH-ARC-013 — Space-based architecture | Extreme concurrent load and database bottleneck need elastic in-memory processing with distributed data. | Measured variable load; database contention; partitionable data; eventual synchronization/collision policies acceptable; sophisticated operations available. | Data-grid complexity, replication/collision/loss risk, memory cost, cache coherence, specialized skills. | Strong centralized transactions; dataset cannot partition; ordinary scale; weak operational maturity; cost ceiling. | High reversal/migration because storage/processing model changes. Specialized high-scale system. Requires grid health, data pumps/writers/readers, replication, recovery, capacity and collision monitoring. | `FSA: chapters/021-chapter-15-space-based-architecture-style.md :: ## General Topology`; `FSA: chapters/021-chapter-15-space-based-architecture-style.md :: ## Data Collisions`; `FSA: chapters/021-chapter-15-space-based-architecture-style.md :: ## Architecture Characteristics Ratings` |
| TECH-ARC-014 — Orchestration-driven SOA | Enterprise processes must coordinate heterogeneous services and centralized integration/policy. | Existing heterogeneous systems; enterprise workflow/reuse mandate; central governance and orchestration budget; stable shared services. | Enterprise-service coupling, orchestration bottleneck, governance overhead, reuse-induced change amplification, vendor/infrastructure complexity. | Product autonomy/rapid local change; central team cannot govern responsively; reuse is only syntactic; latency/availability budget is tight. | High reversal when shared enterprise services are pervasive. Enterprise scale. Requires orchestration engine, service registry/governance, monitoring, compatibility, and recovery. | `FSA: chapters/022-chapter-16-orchestration-driven-service-oriented-architecture.md :: ## Orchestration Engine`; `FSA: chapters/022-chapter-16-orchestration-driven-service-oriented-architecture.md :: ## Reuse…and Coupling` |
| TECH-ARC-015 — Microservices | Independently deployable bounded capabilities need differing scale, technology, availability, and team ownership. | Mature bounded contexts/data ownership; high deployment agility; independent scale/isolation; automated delivery/observability; sagas/consistency accepted. | Network/contract/data duplication; partial failure; distributed transactions; operational and cognitive overhead; eventual consistency; testing/debugging. | Small/simple/early product; shared transactions/joins; boundaries unknown; weak platform/on-call; uniform scaling; cost sensitive. | High reversal due to data/protocol/team topology; system/enterprise scale, selectively. Requires per-service CI/CD, telemetry, security, compatibility, discovery, capacity, incident and data recovery. | `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Granularity`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Data Isolation`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Transactions and Sagas`; `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE DECOUPLING FALLACY` |
| TECH-ARC-016 — Architectural quantum | Scope qualities and independent deployment to the smallest strongly connected functional unit. | Different parts need different qualities; synchronous connascence/cohesion and deployment boundaries can be identified. | Analysis and instrumentation; can be mistaken for a mandated service boundary. | Uniform small system; deployability is not a driver; quanta are guessed from organization rather than dependencies. | Analytical model, not necessarily a structural change. Component-to-system scale. Makes per-quantum SLO, deployment, and failure implications explicit. | `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Architecture Quantum Redux: Choosing Between Monolithic Versus Distributed Architectures` |
| TECH-ARC-017 — Fitness function | Detect drift in a named architecture characteristic or dependency rule continuously. | Accepted measurable outcome; reliable proxy/observable; meaningful threshold and response owner. | Test/monitor maintenance, false positives, metric gaming, runtime cost. | Unmeasurable adjective; check freezes detail; proxy weakly related; no owner/action. | Delete with superseded decision. Any scale; build-time checks or operational telemetry/chaos impose distinct cost and risk. | `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## The Origin of the Simian Army` |
| TECH-ARC-018 — ADR/RFC | Preserve context, authority, consequences, compliance, and revisitability of significant decisions. | Decision constrains future work, crosses boundaries, or is expensive to reverse/forget. | Writing/review upkeep; stale decisions; bureaucracy if applied to local choices. | Trivial/reversible implementation detail; no selection authority; rationale is absent. | Supersede explicitly. Team/system/enterprise decision scale. Operational consequences and compliance need linked verification. | `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecturally Significant`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecture Decision Records`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## ADRs and Request for Comments (RFC)` |
| TECH-ARC-019 — Risk storming | Surface and prioritize architecture risk across multiple perspectives before or during change. | Concrete flow/architecture and characteristic; uncertainty/high consequence; knowledgeable cross-role participants. | Workshop time, subjective scoring, consensus pressure, mitigation backlog. | Generic brainstorming without decision; low-risk local change; absent operators/implementers. | Repeat after mitigation; proposal/iteration scale. Converts high risks into experiments, tests, telemetry, recovery, and acceptance decisions. | `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Risk Storming`; `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Consensus`; `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ### Mitigation` |
| TECH-ARC-020 — Framework isolation | Limit asymmetric commitment and preserve application policy from framework lifecycle/API churn. | Framework is volatile, invasive, replaceable, or controls lifecycle; policy can be expressed behind a narrow adapter. | Adapter/wrapper effort; lost framework convenience; translation; possible lowest-common-denominator API. | Framework is the product/runtime semantics; wrapper merely mirrors it; replacement is implausible and adapter costs exceed risk. | Replace adapter or deliberately accept commitment. Module/system scale. Upgrades, security, startup/lifecycle, and observability remain operational concerns. | `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### ASYMMETRIC MARRIAGE`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### THE RISKS`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### THE SOLUTION` |

## Domain-technique evidence ledger

| ID / technique | Problem it can solve | Evidence that earns it | Introduced costs | Contraindications | Reversal / appropriate scale / operational consequences | Source support |
|---|---|---|---|---|---|---|
| TECH-DOM-001 — Ubiquitous Language | Experts, requirements, code, and tests use ambiguous or divergent terms. | Recurring translation/defects; accessible experts; terms affect rules/decisions; examples can validate meanings. | Continuous collaboration and renaming; disagreement is exposed rather than hidden. | Generic infrastructure; no expert access; vocabulary has no model/code consequence. | Evolve through explicit model changes; context/team scale. Logs, APIs, events, docs, and runbooks may need coordinated language/versioning. | `DDD: chapters/003-chapter-2-communication-and-the-use-of-language.md :: ## Ubiquitous Language`; `DDD: chapters/004-chapter-3-binding-model-and-implementation.md :: ## Model-Driven Design` |
| TECH-DOM-002 — Entity | Domain meaning depends on continuity/identity despite attribute change. | Experts distinguish “same thing”; lifecycle/history/reference requires stable identity; identity source/rules known. | Identity generation/comparison, mutable lifecycle, persistence/concurrency complexity. | Meaning is entirely attributes; identity is database convenience; immutable value is clearer. | Convert with data migration/reference changes. Local/context scale. Operational duplication/idempotency and identity authority matter. | `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Entities (a.k.a. Reference Objects)` |
| TECH-DOM-003 — Value Object | A descriptive concept is defined by attributes and benefits from immutability/whole-value semantics. | No independent identity; equality by value; replacement is valid; constraints belong to the concept. | Creation/copying/mapping; careless large values may affect performance. | Lifecycle/identity matters; mutation is semantically meaningful; object is only a DTO with no concept. | Usually easy to inline/replace; local/context scale. Serialization, units, precision and compatibility must preserve representation semantics. | `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Value Objects` |
| TECH-DOM-004 — Domain Service | An important domain operation does not naturally belong to one entity/value and is stateless in domain terms. | Experts name a process/policy; inputs/outputs are domain concepts; assigning to an entity would distort responsibility. | Procedural/anemic-model drift; broad dependency hub; hidden side effects. | Operation belongs to an entity/value; technical orchestration; service exists only as a layer convention. | Move behavior to concepts or split service. Local/context scale. Side effects/failure/transactions require explicit orchestration. | `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Services`; `DDD: chapters/011-chapter-9-making-implicit-concepts-explicit.md :: ## Processes as Domain Objects` |
| TECH-DOM-005 — Aggregate | Enforce a cluster of invariants under one consistency and lifecycle boundary. | Named invariants require atomic coordination; root can authorize changes; external references need not traverse internals. | Contention, loading/mapping, command routing; too-large boundary limits scale; too-small weakens invariants. | Object graph containment only; no shared invariant; persistence cascade defines boundary. | Split/merge requires semantic and data migration. Context scale. Transactions, concurrency, retries, and consistency are operational consequences. | `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates` |
| TECH-DOM-006 — Factory | Complex creation must establish an invariant whole while hiding construction detail. | Many coordinated parts/invariants; valid creation cannot be expressed by simple constructor; lifecycle transition creates another aggregate/value. | Extra abstraction; construction can become detached from domain; dependency setup. | Simple construction; framework factory cargo cult; object is invalid for unrelated post-creation reasons. | Inline when creation simplifies. Aggregate/context scale. Failure, idempotency, generated identity, and dependency availability must be defined. | `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Factories` |
| TECH-DOM-007 — Repository | Domain code needs collection-like access to aggregate roots while persistence/query mechanisms remain separate. | Aggregate lifecycle and reconstitution; meaningful domain retrieval; multiple persistence concerns would pollute model. | Query abstraction mismatch, N+1/hidden I/O, transaction/session complexity, generic CRUD APIs. | Per-table DAO renamed repository; non-root internals exposed; trivial data script; queries do not return domain aggregates. | Collapse to direct gateway or specialize queries. Aggregate/context scale. Latency, consistency, pagination, transaction and cache semantics must be visible. | `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Repositories`; `CA: chapters/034-chapter-23-presenters-and-humble-objects.md :: ### DATABASE GATEWAYS` |
| TECH-DOM-008 — Specification | Complex predicate/selection/creation rule is a domain concept needing composition and reuse. | Experts name the criterion; rule recurs; logic is awkward/duplicated; validation/query/build share semantics. | Object/DSL proliferation; translation to persistence; hidden expensive evaluation. | One simple conditional; no domain name; generic predicate library; performance semantics unknown. | Inline or specialize. Local/context scale. Query translation, evaluation cost, versioning, and explanation/audit may matter. | `DDD: chapters/011-chapter-9-making-implicit-concepts-explicit.md :: ## Specification`; `DDD: chapters/011-chapter-9-making-implicit-concepts-explicit.md :: ## Applying and Implementing S***PECIFICATION` |
| TECH-DOM-009 — Bounded Context + Context Map | One model/language cannot remain coherent across differing meanings, authorities, or systems. | Semantic contradiction; distinct owners/cadences/invariants; unavoidable integration; boundary verified through examples/change. | Translation, duplicated concepts/data, contract/versioning, organizational coordination. | One small coherent team/model; split only mirrors directories/services; translation adds no semantic value. | Merge/split via explicit mapping and migration; subsystem/team/enterprise scale. Integration reliability, data synchronization, monitoring and ownership become operational. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Context Map`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Domain-Driven Design's Bounded Context` |
| TECH-DOM-010 — Shared Kernel | Two contexts gain more from a small shared model/code subset than from translation. | Close trust/coordination; stable tiny overlap; mutual change process and integrated tests. | Release coordination, mutual veto, shared failure/change amplification, blurred ownership. | Low trust, different cadence, broad overlap, semantic divergence, uncoordinated teams. | Extract copies/translators or merge contexts; two-team/context scale. Shared release compatibility and joint regression tests are required. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel` |
| TECH-DOM-011 — Customer/Supplier | Downstream needs influence over upstream interface while upstream remains authoritative. | Clear direction; real dependency; negotiation channel; supplier can prioritize downstream needs; joint acceptance tests possible. | Planning/priority coordination; downstream remains coupled to supplier schedule/quality. | No leverage/cooperation; symmetrical joint ownership; semantics unacceptable without translation. | Move to Conformist or ACL if relationship changes. Cross-team scale. Contract testing, release communication, SLO and escalation path required. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Customer/Supplier Development Teams` |
| TECH-DOM-012 — Conformist | Downstream lacks influence and translation value does not justify its cost. | Upstream model is stable/adequate; interface broad; local differentiation low; negotiation impossible. | Local model constrained/polluted; upstream changes propagate; autonomy lost. | Local core value would be harmed; semantics unsafe; translation is affordable; upstream is unstable. | Add ACL or separate when economics change. Downstream-context scale. Must monitor upstream compatibility and accepted semantic loss. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Conformist` |
| TECH-DOM-013 — Anticorruption Layer | Necessary integration with an uncontrolled/legacy model would corrupt a valuable local model. | Concrete semantic mismatch; local core model has value; integration cannot be avoided; translation contract can be tested. | Translators/facades, duplicated models, latency/error mapping, maintenance and team ownership. | Same semantics; tiny stable interface; local model has little value; translator cost exceeds protection. | Remove if contexts converge or choose Conformist. Boundary/context scale. Needs mapping tests, error/identity/transaction semantics, metrics, compatibility and fallback. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Anticorruption Layer`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES` |
| TECH-DOM-014 — Separate Ways | Integration cost exceeds its business value. | Workflow can tolerate independence/manual transfer/duplication; no hard invariant; maintenance/reliability benefit exceeds shared capability. | Duplicate capabilities/data; user reconciliation; loss of enterprise uniformity. | Legal/financial invariant; essential end-to-end workflow; inconsistent results unacceptable. | Integrate later through explicit relationship. Context/system scale. Manual operations, reconciliation, ownership and user communication must be explicit. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Separate Ways` |
| TECH-DOM-015 — Open Host Service + Published Language | Many consumers need a stable, generalized integration surface without bespoke translators for each. | Multiple independent consumers; recurring common exchange; stable semantics; provider can govern/version public protocol. | Public compatibility, governance, security, lowest-common-denominator pressure, documentation/support. | One consumer; rapidly changing/unclear semantics; exposing internal model; consumers need incompatible views. | Version/deprecate or return to bilateral adapters. Multi-context/ecosystem scale. Requires auth, SLO, schema/versioning, monitoring, support and deprecation policy. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Open Host Service`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Published Language` |
| TECH-DOM-016 — Core Domain + Generic Subdomain distillation | Scarce modeling talent and architectural protection need focus on business differentiation. | Explicit business strategy; differentiating capability; generic/supporting functions identified; investment can improve competitive outcome. | Classification disputes; neglect of necessary supporting reliability; buy/build/vendor risk. | All domains equally generic/regulated; strategy unknown; “core” used as prestige label. | Reclassify as strategy evolves. Product/portfolio scale. Core receives stronger talent/tests/observability; generic sourcing introduces vendor/integration operations. | `DDD: chapters/017-chapter-15-distillation.md :: ## Core Domain`; `DDD: chapters/017-chapter-15-distillation.md :: ## Generic Subdomains`; `DDD: chapters/017-chapter-15-distillation.md :: ## Domain Vision Statement` |
| TECH-DOM-017 — Minimal evolving large-scale structure | Large model/team needs a shared organizing concept without freezing local evolution. | Coordination/cognitive pressure across multiple parts; a simple conceptual rule fits current model and clarifies placement. | Constraint can become ceremonial or suppress discovery; maintenance/governance. | Small coherent model; structure does not fit; imposed master plan; local variation is valuable. | Simplify/replace when fit deteriorates. Multi-module/context scale. Constraints may be enforced in build/review; ownership and evolution must be explicit. | `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Evolving Order`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## System Metaphor`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Responsibility Layers`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Strategic design requires minimalism and humility` |
| TECH-DOM-018 — Smart UI / transaction script | Simple data-centric workflow needs rapid delivery by a less specialized team. | Low domain complexity; short-lived/simple product; validations/workflows straightforward; UI-centric change; deep model offers no strategic payoff. | Domain logic can duplicate and become hard to extract as complexity grows; UI/framework coupling. | Differentiating complex rules; multiple channels; long-lived evolving domain; invariants span workflows. | Refactor behind characterization when complexity trigger appears. Small/simple application scale. Operations are conventional; business rules may be harder to observe independently. | `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"` |

## Evaluation-rubric candidates

Use 0 = absent/unsupported, 1 = partial/assumed, 2 = explicit and evidenced. A numeric total never overrides a hard gate or repository contract.

### RUBRIC-ARC-001 — Architectural assessment quality (maximum 20)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Authority and change type | Role/semantic authority assumed | Role named but transition unclear | Observation, proposal, authorization, execution and acceptance are explicitly separated |
| Repository contracts | Ignored | Listed without reconciliation | Accepted decisions/conventions are traced and conflicts escalated |
| Driver evidence | Taste/style adjective | One weak evidence class | Named system-level force with threshold and corroboration proportional to reversal cost |
| Scope | Whole system by default | Rough component scope | Smallest affected quantum/flow and unaffected areas are explicit |
| Preservation | Not stated | Generic “tests pass” | Behavior, data, protocol, quality and operational boundaries are explicit |
| Alternatives | Preferred pattern only | One alternative | No-change, local, modular and topology alternatives compared |
| Cost/trade-offs | Benefits only | Generic cost list | Migration, coordination, runtime, data, security, operations and opportunity costs estimated |
| Reversibility | Claimed reversible | Exit idea | Reversal mechanics, trigger, irreversible commitments and option cost specified |
| Verification | Review/tests generically | One metric | Baseline, scenario, threshold, fitness/telemetry, owner and acceptance are specified |
| Uncertainty | Certainty theater | Caveats listed | Observation/inference confidence and unresolved questions drive experiments/escalation |

- **Pass guidance:** 16/20 for a selection-ready assessment; 12–15 remains a proposal requiring evidence; below 12 is orientation only.
- **Hard gates:** zero in authority, repository contracts, driver evidence, or preservation prevents execution. Distribution also requires RUBRIC-ARC-004 to pass.

### RUBRIC-ARC-002 — Boundary proposal quality (maximum 16)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Independent force | No change/ownership evidence | Plausible variation | Actual independent policy, volatility, owner, release, model or quality force |
| Semantic cohesion | Directory/classes only | Responsibility narrative | Invariants, decisions, data and behavior that must stay together are demonstrated |
| Contract | Types/endpoints only | Happy path | Meaning, authority, error, temporal, identity and version semantics are explicit |
| Strength selection | Interface/service assumed | Two forms considered | Direct, facade, inverted, component, process and service costs compared |
| Information hiding | Internals exposed | Some translation | Consumer sees the minimum stable semantic surface |
| Operations/data | Omitted | Generic concerns | Data ownership, transactions, latency, failure, observability and recovery modeled |
| Migration/reversal | Big-bang or absent | Stages named | Characterized slices, compatibility, rollback and completion/deletion triggers specified |
| Enforcement | Diagram only | Review convention | Necessary forbidden dependencies/contracts have proportional automated checks |

- **Pass guidance:** 13/16 and no hard-gate failure.
- **Hard gates:** independent force, semantic cohesion, and contract must each score 2 before a deployable boundary is authorized.

### RUBRIC-DOM-003 — Domain/context proposal quality (maximum 18)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Domain investment | Pattern enthusiasm | Complexity asserted | Core/support/generic/simple classification tied to business value and lifespan |
| Expert evidence | Code/schema only | Documents/one interview | Examples and language validated repeatedly with authoritative experts |
| Language/model | Nouns only | Glossary | Decisions, policies, identity and invariants form an executable/tested model |
| Boundary evidence | Team/directory/service | One semantic difference | Internal coherence plus external language/rule/authority/cadence discontinuity |
| Ownership | Unspecified | Team label | Decision/data authority and upstream/downstream power are explicit |
| Relationship | “API” only | Translator named | Shared Kernel/Customer-Supplier/Conformist/ACL/Separate/Open Host chosen by economics |
| Tactical patterns | Template cargo cult | Some semantic fit | Entity/value/service/aggregate/repository/factory each justified by its own force |
| Preservation/integration | Happy path | Mapping tests | Semantic loss, identity, failure, transaction, version and reconciliation are explicit |
| Learning loop | Final model claimed | Future review | Experiments, expert feedback, triggers to merge/split/simplify and confidence recorded |

- **Pass guidance:** 14/18 for a strategic proposal; tactical implementation can pass with 12 if no context/team/data topology changes.
- **Hard gates:** expert evidence, language/model, boundary evidence, and preservation/integration cannot be zero for a context restructuring.

### RUBRIC-ARC-004 — Distributed-topology readiness (maximum 18)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Irreducible driver | Fashion/scale guess | Plausible future need | Current measurable isolation, scale, geography, security or deployment driver |
| Boundary maturity | Entities/directories | Candidate module | Stable coherent capability/context tested in-process |
| Data ownership | Shared DB assumed | Tables assigned | Authority, transactions, joins, migration, consistency and reconciliation designed |
| Failure semantics | Network treated local | Retries/timeouts | Partial failure, idempotency, ordering, duplicate, fallback and recovery tested |
| Compatibility | Unversioned calls/events | Version idea | Contract/schema evolution, rollout order, deprecation and consumer tests |
| Delivery/platform | Manual | Some automation | Repeatable independent CI/CD, config/secrets, discovery and rollback |
| Observability/operations | Logs only | Per-service metrics | End-to-end tracing, SLOs, ownership, alerts, capacity, incident and disaster recovery |
| Security/durability | Assumed | Controls named | Threat/trust boundary, auth, encryption, audit, backup/restore verified |
| Cost/reversal | Benefits only | Budget noted | Infrastructure/team cost, migration stages, merge-back route and stop triggers |

- **Pass guidance:** 15/18; any lower result defaults to monolith/modular monolith or a bounded experiment.
- **Hard gates:** data ownership, failure semantics, delivery/platform, and observability/operations must score 2 before production distribution.

### RUBRIC-DOM-005 — Aggregate/invariant proposal quality (maximum 14)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Invariants | Object graph | Rule named | Expert-validated rule with violating commands/examples |
| Atomic need | ORM cascade | Transaction assumed | Exact state requiring atomic consistency and allowed eventual state |
| Root authority | Arbitrary container | Entry point named | Root exclusively enforces mutations and lifecycle |
| Identity/reference | Internal object exposure | IDs used inconsistently | Identity authority and cross-aggregate reference policy explicit |
| Concurrency/failure | Happy path | Lock/retry named | Concurrent, retry, partial, duplicate and recovery behavior tested |
| Persistence access | Repository per table | Aggregate repository | Query/load/transaction/latency semantics support domain use without hidden surprises |
| Scale/evolution | “Small aggregates” maxim | Performance guess | Measured contention/load and semantic split/merge triggers |

- **Pass guidance:** 11/14. Invariants and atomic need must score 2; otherwise no aggregate boundary is established.

### RUBRIC-ARC-006 — ADR and authority discipline (maximum 16)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Status/authority | Decision implied | Proposer named | Proposed/accepted/superseded plus selector, authorizer, executor, verifier, accepter |
| Context/evidence | Pattern claim | Drivers listed | Observations, thresholds, constraints, assumptions and evidence links |
| Scope | Global ambiguity | Components named | Included/excluded quanta, behaviors, data, teams and operations |
| Alternatives | None | One rejected | No-change/local/structural candidates and why each loses under current evidence |
| Consequences | Benefits | Generic cons | Positive/negative, migration, operations, security/durability and opportunity cost |
| Compliance/verification | “Follow architecture” | Review gate | Executable fitness/telemetry, baseline, owner and response |
| Reversal/evolution | Permanent or “reversible” | Review date | Irreversible commitments, exit mechanics and evidence-based supersession trigger |
| Communication | Private note | Repository file | Discoverable durable record reaches affected implementers/operators |

- **Pass guidance:** 13/16. A zero in status/authority, context/evidence, scope, or consequences leaves the ADR unselectable.

## Architecture/domain checklists

### CHECK-ARC-001 — Architectural-evidence checklist

- [ ] Change type and allowed semantic change are named.
- [ ] Repository contracts and accepted decisions were read before generic doctrine.
- [ ] Observation, inference, recommendation, selection, authorization, execution, verification, and acceptance are distinguished.
- [ ] At least one structural driver has a concrete scenario and threshold.
- [ ] Expensive/irreversible action has corroboration from another evidence class.
- [ ] Driver is scoped to the smallest affected flow/quantum.
- [ ] Current baseline and preservation boundaries exist.
- [ ] No-change and local implementation alternatives were considered.
- [ ] Coordination, migration, runtime, data, operational, security/durability, and opportunity costs are explicit.
- [ ] Reversal mechanics and stop/revisit triggers are explicit.
- [ ] Agent has authority for the next transition; otherwise output is a proposal.

### CHECK-ARC-002 — Boundary-evidence checklist

- [ ] What changes independently, who changes it, and how often are evidenced.
- [ ] Invariants/data/behavior that must stay cohesive are named.
- [ ] Contract meaning includes errors, timing, identity, version, and authority—not only types.
- [ ] Direct call, local seam, inverted interface, deployable component, process, and service were compared where relevant.
- [ ] Boundary strength is the cheapest that satisfies current force.
- [ ] Translation and information-hiding value exceed navigation/mapping/versioning cost.
- [ ] Data ownership and transactions remain valid.
- [ ] Runtime crossings account for latency, partial failure, observability, security, and recovery.
- [ ] Testability did not become permission to expose internals publicly.
- [ ] There is a merge/delete/strengthen trigger.

### CHECK-DOM-003 — Domain/context checklist

- [ ] Business differentiation and domain complexity justify the investment.
- [ ] Domain experts and operational examples—not only schema/code—support the model.
- [ ] Ubiquitous Language includes verbs, policies, identities, invariants, and examples.
- [ ] Each context is internally coherent and externally discontinuous for a demonstrated reason.
- [ ] Contexts are not inferred from services, folders, teams, tables, or entity nouns alone.
- [ ] Upstream/downstream, control, trust, and negotiation capacity are explicit.
- [ ] Relationship pattern is chosen by actual economics and semantic distance.
- [ ] Entities, values, services, aggregates, repositories, factories, and specifications are introduced only when their semantics exist.
- [ ] Semantic loss, translation, versioning, identity, consistency, failure, and reconciliation are tested.
- [ ] The model/context has an experiment and evolution/simplification trigger.

### CHECK-ARC-004 — Distribution and eventing checklist

- [ ] A current driver cannot be met economically in-process.
- [ ] Capability/context boundary is mature before deployment split.
- [ ] Each service owns authoritative data or explicitly accepts shared-data coupling.
- [ ] Cross-service transactions/joins have authorized consistency and reconciliation semantics.
- [ ] Network fallacies, end-to-end latency, capacity, and cost are modeled.
- [ ] Retry, timeout, duplicate, ordering, idempotency, poison messages, replay, and recovery are designed.
- [ ] Completion owner and orchestration/choreography choice are explicit.
- [ ] Independent CI/CD, rollback, contract versioning, and consumer compatibility exist.
- [ ] Tracing, metrics, logs, SLOs, on-call, incident and disaster recovery exist.
- [ ] Security/trust boundary and data durability are verified.
- [ ] Merge-back or bounded-trial stop condition exists.

### CHECK-ARC-005 — Architecture stop-and-escalate checklist

- [ ] Stop if evidence demonstrates taste, symmetry, or fashion rather than a force.
- [ ] Stop if a local implementation change meets the accepted thresholds.
- [ ] Stop if baseline/preservation behavior is unknown and first characterize it.
- [ ] Stop if proposed boundary weakens a known invariant or hides unresolved semantics.
- [ ] Stop if distribution lacks data, failure, delivery, or operational readiness.
- [ ] Escalate any unauthorized behavior, consistency, API, data ownership, deployment, security/durability, or cost change.
- [ ] Escalate a proposal that supersedes an accepted repository decision.
- [ ] Escalate disputed expert language or risk rather than manufacturing consensus.
- [ ] Report uncertainty and alternatives when evidence cannot reliably select.

## Retrieval/routing candidates

| Route | Activate for roles | Tasks and repository signals | Risk / prerequisites | Exclude when | Priority / budget hint | Candidate concepts |
|---|---|---|---|---|---|---|
| ROUTE-ARC-CORE | architecture-agent, review-agent, repository-assessment-agent | architecture assessment, boundary/style proposal, accepted-decision review; cross-module change, quality constraint, ownership/deployment question | Any risk; repository contracts and authority required | Purely local implementation with accepted architecture | core / 2–4 records plus procedure | AD-ARC-001–008, AD-ARC-034–036; PROC-ARC-001, 012, 014 |
| ROUTE-ARC-BOUNDARY | architecture-agent, coding-agent, refactoring-agent, legacy-agent | interface/module/service question; dependency cycles; change amplification; independent ownership/release; legacy seam | High for public/remote/data boundary; preservation model required | Variation/pressure is hypothetical | high / 3–6 records + TECH comparison | AD-ARC-006–013, 029, 038–040; PROC-ARC-002–003 |
| ROUTE-ARC-CHARACTERISTIC | architecture-agent, performance-agent, review-agent | SLO, availability, security, scalability, architecture fitness, metric/governance | Threshold/owner required; regulated claims need authority | Quality adjective lacks structural consequence | high / 2–5 records | AD-ARC-003–005, 014, 035–036; PROC-ARC-004, 013–014 |
| ROUTE-ARC-STYLE | architecture-agent, operational/review-agent | monolith/distributed/style selection; service decomposition; topology migration | High; ranked characteristics, data and operations required | Local module solves driver | specialist / finalist technique rows only | AD-ARC-029–033; PROC-ARC-005–006, 011; TECH-ARC-002, 007–015 |
| ROUTE-DOM-CORE | domain-agent, coding-agent, architecture-agent, review-agent | domain concept placement/model review; ambiguous language; complex rules/invariants | Expert examples and accepted business semantics required | Generic infrastructure or simple data flow | high / 3–6 records | AD-DOM-016–022, 027, 037; PROC-DOM-007, 010 |
| ROUTE-DOM-CONTEXT | domain-agent, architecture-agent, legacy/integration-agent | bounded context/context map, legacy integration, model conflict, team/data ownership | High for org/data/API change; language and relationship evidence required | Boundary inferred only from directory/service/schema | specialist / 4–8 records | AD-DOM-023–026, 028; PROC-DOM-008–009; TECH-DOM-009–017 |
| ROUTE-ARC-DISTRIBUTED | architecture-agent, durability/performance/debugging agent | remote services, events, queues, sagas, independent deployment; latency/failure/incidents | High; RUBRIC-ARC-004 prerequisites | Weak operational maturity or no irreducible driver | specialist / 4–10 records | AD-ARC-029–033, 035–036; PROC-ARC-005, 011, 013–014 |
| ROUTE-ARC-FRAMEWORK | coding-agent, architecture-agent, review-agent | framework/library adoption or replacement; generated/vendor boundary | Commitment/lifecycle evidence required | Wrapper mirrors framework or framework semantics are the product | normal / 2–3 records | AD-ARC-038–039; TECH-ARC-006, 020 |

## Graph candidates

### Graph conventions

- A **canonical node** is a synthesis candidate, not a claim that every source uses the same term or scope.
- **direct_support** means the source explicitly advances substantially the node's proposition.
- **corroboration** means the source independently advances a materially similar proposition in its own vocabulary.
- **refinement** means the source narrows, conditions, decomposes, or adds consequences to the proposition.
- **derived_inference** means the formulation is a defensible synthesis but is not stated as such by that source; it must never be presented as a quotation or source consensus.
- An absent equivalent is stated explicitly rather than filled by analogy. Exact locators use the source IDs defined at the top of this artifact.

### Canonical candidate nodes and source formulations

#### GRAPH-ARC-001 — Evidence-governed architectural intervention

- **Kind:** universal principle / decision rule.
- **CA — direct_support:** Judge architecture by whether it minimizes the human effort needed to build and maintain the system over its lifetime; a deteriorating cost-of-change curve is design evidence, not merely aesthetics. Locator: `CA: chapters/008-chapter-1-what-is-design-and-architecture.md :: ## THE GOAL?`; `CA: chapters/008-chapter-1-what-is-design-and-architecture.md :: ## CASE STUDY`.
- **FSA — direct_support:** Architecture is contextual trade-off analysis: no characteristic or style is globally best, so selection follows business drivers and the “least worst” set of compromises. Locator: `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Trade-Offs and Least Worst Architecture`; `FSA: chapters/007-chapter-2-architectural-thinking.md :: ## Understanding Business Drivers`.
- **DDD — refinement:** Strategic design begins with assessment and must absorb feedback from implementation and domain learning; a preconceived ideal model is not sufficient evidence. Locator: `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Assessment First`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The decision process must absorb feedback`.
- **Convergence/tension:** All reject architecture by appearance alone. The canonical “evidence before intervention” rule is a derived synthesis: CA emphasizes lifetime effort, FSA quality/business trade-offs, and DDD domain-learning feedback, so the evidence class depends on the claimed force.

#### GRAPH-ARC-002 — Scoped and measurable architecture characteristics

- **Kind:** evidence model / architecture concept.
- **CA — refinement:** Architecture must support operation, development, deployment, and maintenance, but operational efficiency alone may be achieved without a well-structured system; the relevant concern must be tied to lifecycle consequences. Locator: `CA: chapters/026-chapter-15-what-is-architecture.md :: ## DEVELOPMENT`; `CA: chapters/026-chapter-15-what-is-architecture.md :: ### DEPLOYMENT`; `CA: chapters/026-chapter-15-what-is-architecture.md :: ### OPERATION`; `CA: chapters/026-chapter-15-what-is-architecture.md :: ### MAINTENANCE`.
- **FSA — direct_support:** A characteristic is architecturally relevant when it affects structure and is critical to success; it should be identified from domain/requirements, scoped to the affected quantum, and governed with measures or fitness functions. Locator: `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Influences some structural aspect of the design`; `FSA: chapters/010-chapter-5-identifying-architectural-characteristics.md :: ## Extracting Architecture Characteristics from Domain Concerns`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`.
- **DDD — refinement:** Performance and persistence constraints can justify a separate representation/context, but such tuning should preserve a transparent relationship to domain meaning instead of silently corrupting the model. Locator: `DDD: chapters/008-chapter-7-using-the-language-an-extended-example.md :: ## Performance Tuning`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Designing Objects for Relational Databases`.
- **Convergence/tension:** FSA supplies the general taxonomy; CA supplies lifecycle dimensions; DDD supplies a domain-integrity constraint. DDD does not directly endorse FSA's characteristic vocabulary, so that correspondence is contextual, not terminological consensus.

#### GRAPH-ARC-003 — Boundary earned by an independent force

- **Kind:** architecture decision rule / boundary principle.
- **CA — direct_support:** Draw a boundary where high-level policy needs protection from a volatile detail, while considering when the cost of a full boundary is justified. Locator: `CA: chapters/028-chapter-17-boundaries-drawing-lines.md :: ## WHICH LINES DO YOU DRAW, AND WHEN DO YOU DRAW THEM?`; `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24: Partial Boundaries`.
- **FSA — corroboration:** Component granularity and architectural quanta should follow cohesion, synchronous coupling, deployability, architecture characteristics, and change pressure—not an arbitrary component count. Locator: `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Component Granularity`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`.
- **DDD — refinement:** A Bounded Context earns a boundary where one model/language can be kept internally consistent and its relationship to other models is made explicit; it is not just a module. Locator: `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## B***OUNDED* **C***ONTEXTS* **Are Not M***ODULES`.
- **Convergence/tension:** The sources converge on non-arbitrary boundaries but privilege different forces: policy volatility (CA), deployability/quality/coupling (FSA), and semantic consistency (DDD). None of those forces automatically proves the others.

#### GRAPH-ARC-004 — Boundary strength is a costed continuum

- **Kind:** architecture model / decision rule.
- **CA — direct_support:** A boundary may be an in-memory source dependency, deployable component, local process, or service; partial boundaries deliberately buy less protection at less initial cost. Locator: `CA: chapters/029-chapter-18-boundary-anatomy.md :: ## BOUNDARY CROSSING`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ## SKIP THE LAST STEP`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### ONE-DIMENSIONAL BOUNDARIES`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES`.
- **FSA — direct_support:** Monolithic and distributed topologies impose different coupling, latency, transaction, deployment, and operational trade-offs; choose topology from drivers rather than treating distribution as advanced modularity. Locator: `FSA: chapters/015-chapter-9-foundations.md :: ## Monolithic Versus Distributed Architectures`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Monolith versus distributed`.
- **DDD — refinement:** Context relationships and deployment are separate strategic choices; model boundaries can transform, merge, or remain integrated, and each relationship has a trade-off. Locator: `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Transforming Boundaries`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Deployment`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## The Trade-off`.
- **Convergence/tension:** Semantic, source, release, process, and network boundaries must be represented as distinct graph nodes/edges. “Boundary” without a type is too ambiguous for routing.

#### GRAPH-ARC-005 — Protect semantic policy from contingent mechanism

- **Kind:** architecture principle / dependency rule.
- **CA — direct_support:** Source dependencies at an architectural boundary should point toward higher-level policy; boundary data should avoid dragging framework/database representations inward. Locator: `CA: chapters/030-chapter-19-policy-and-level.md :: ## LEVEL`; `CA: chapters/033-chapter-22-the-clean-architecture.md :: ## THE DEPENDENCY RULE`; `CA: chapters/033-chapter-22-the-clean-architecture.md :: #### WHICH DATA CROSSES THE BOUNDARIES`.
- **FSA — corroboration:** Domain partitioning organizes behavior by business capability and can reduce technical-layer change amplification, though it introduces duplication and does not dominate every context. Locator: `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Architecture Partitioning`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ### Domain partitioning`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ### Technical partitioning`.
- **DDD — direct_support:** Isolate the domain layer so the model and business rules are not submerged in UI, application, or infrastructure concerns. Locator: `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## Layered Architecture`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Domain Layer Is Where the Model Lives`.
- **Convergence/tension:** This is strong convergence at the level of protecting business meaning. CA's dependency direction, FSA's partition choice, and DDD's domain layer are not structurally identical; a graph should connect them by `may_realize`, not `same_as`.

#### GRAPH-ARC-006 — Semantic cohesion and change locality determine grouping

- **Kind:** universal architecture principle / evidence rule.
- **CA — direct_support:** Group classes/components that close against the same changes and are reused/released together; cohesion principles conflict, so grouping changes with lifecycle phase and consumers. Locator: `CA: chapters/023-chapter-13-component-cohesion.md :: ### THE COMMON CLOSURE PRINCIPLE`; `CA: chapters/023-chapter-13-component-cohesion.md :: ### THE COMMON REUSE PRINCIPLE`; `CA: chapters/023-chapter-13-component-cohesion.md :: ## THE TENSION DIAGRAM FOR COMPONENT COHESION`.
- **FSA — direct_support:** Cohesion ranges from functional to coincidental; component discovery and granularity iterate over responsibility, architecture characteristics, roles, and change. Locator: `FSA: chapters/008-chapter-3-modularity.md :: ## Cohesion`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Analyze Roles and Responsibilities`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Component Granularity`.
- **DDD — refinement:** Modules and conceptual contours should reflect a meaningful model and keep a conceptual object together unless distribution is intentional. Locator: `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Modules (a.k.a. Packages)`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Unless there is a real intention to distribute code on different servers, keep all the code that implements a single conceptual object in the same MODULE, if not the same object`; `DDD: chapters/012-chapter-10-supple-design.md :: ## Conceptual Contours`.
- **Convergence/tension:** Change closure, functional cohesion, and conceptual contour often reinforce each other but can disagree. The graph must preserve separate evidence predicates and represent grouping as a selection among competing forces.

#### GRAPH-ARC-007 — Architecture evolves while preserving valuable options

- **Kind:** universal principle / lifecycle rule.
- **CA — direct_support:** Good architecture postpones irrelevant detail commitments and keeps options open, but each reserved option costs structure and should serve plausible change. Locator: `CA: chapters/026-chapter-15-what-is-architecture.md :: ### KEEPING OPTIONS OPEN`; `CA: chapters/027-chapter-16-independence.md :: ### LEAVING OPTIONS OPEN`; `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24: Partial Boundaries`.
- **FSA — corroboration:** Architecture knowledge and ecosystem assumptions become obsolete, and decisions are trade-offs whose consequences and compliance should be recorded so they can be revisited. Locator: `FSA: chapters/003-preface-invalidating-axioms.md :: ## Axiom`; `FSA: chapters/007-chapter-2-architectural-thinking.md :: ## Frozen Caveman Anti-Pattern`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecture Decision Records`.
- **DDD — direct_support:** Large-scale structure should be evolved to fit, strategic plans must absorb feedback and allow evolution, and teams should beware master plans. Locator: `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Evolving Order`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The plan must allow for evolution`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Beware the Master Plan`.
- **Convergence/tension:** CA can sound more proactive about preserving choices; DDD warns that advance structures can constrain discovery; FSA foregrounds changing ecosystem knowledge. The decision rule is selective option preservation based on probability, impact, delay value, and carrying cost—not maximum flexibility.

#### GRAPH-ARC-008 — Architecture style and structure are contextual selections

- **Kind:** architecture decision rule / conflict node.
- **CA — refinement:** Decoupling mode should track development, deployment, and operational needs; layers/use cases need not all be separated by the same mechanism. Locator: `CA: chapters/027-chapter-16-independence.md :: ### DECOUPLING MODE`; `CA: chapters/027-chapter-16-independence.md :: ### DECOUPLING MODES (AGAIN)`; `CA: chapters/036-chapter-25-layers-and-boundaries.md :: ### CROSSING THE STREAMS`.
- **FSA — direct_support:** Styles carry different characteristic trade-offs and must be selected from domain, data, organizational, process, team, and operational criteria rather than fashion. Locator: `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Shifting "Fashion" in Architecture`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`.
- **DDD — corroboration:** Large-scale structures and strategic patterns should be minimal, fitting, and evolved; patterns are a language for recurrent forces, not a master plan. Locator: `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## How Restrictive Should a Structure Be?`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Minimalism`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The Use of Patterns in This Book`.
- **Convergence/tension:** Strong convergence against uniformity. FSA catalogs styles, CA offers a normative dependency center, and DDD organizes domain meaning; the graph should encode each as candidate technique under conditions rather than a universal architecture root.

#### GRAPH-ARC-009 — Distribution adds coupling and failure; it does not prove decoupling

- **Kind:** negative doctrine / risk principle.
- **CA — direct_support:** Services are not automatically architecturally significant or independently deployable; cross-cutting changes and shared data/protocols can couple them. Locator: `CA: chapters/038-chapter-27-services-great-and-small.md :: ## SERVICE ARCHITECTURE?`; `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE DECOUPLING FALLACY`; `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE FALLACY OF INDEPENDENT DEVELOPMENT AND DEPLOYMENT`.
- **FSA — direct_support:** Distributed systems incur unreliable networks, latency, finite bandwidth, security/topology/administration/transport/heterogeneity concerns plus logging, transaction, contract, and versioning complexity. Locator: `FSA: chapters/015-chapter-9-foundations.md :: ## Fallacy #1: The Network Is Reliable`; `FSA: chapters/015-chapter-9-foundations.md :: ## Other Distributed Considerations`; `FSA: chapters/015-chapter-9-foundations.md :: ## Contract maintenance and versioning`.
- **DDD — refinement:** Bounded Contexts are model boundaries, not modules or mandatory deployment units; deployment choices and integrations have separate trade-offs. Locator: `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## B***OUNDED* **C***ONTEXTS* **Are Not M***ODULES`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Deployment`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## The Trade-off`.
- **Convergence/tension:** Strong convergence that semantic or source modularity does not entail network distribution. FSA provides the fullest operational evidence; DDD's contribution prevents the historically common “bounded context equals microservice” collapse.

#### GRAPH-ARC-010 — Modular monolith is a first-class topology

- **Kind:** architecture technique / topology.
- **CA — corroboration:** A monolith can cross strong source boundaries and contain independently testable components; deployability is only one boundary dimension. Locator: `CA: chapters/029-chapter-18-boundary-anatomy.md :: ### THE DREADED MONOLITH`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY COMPONENT`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### OTHER DECOUPLING MODES`.
- **FSA — direct_support:** A modular monolith can preserve domain partitioning and code modularity while avoiding distributed latency, transaction, and operational costs. Locator: `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Modular Monolith`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Monolith Case Study: Silicon Sandwiches`.
- **DDD — corroboration:** Keep code for a single conceptual object/module together unless actual distribution is intended; Bounded Context and deployment are separate choices. Locator: `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Unless there is a real intention to distribute code on different servers, keep all the code that implements a single conceptual object in the same MODULE, if not the same object`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Deployment`.
- **Convergence/tension:** The term “modular monolith” is FSA's, not shared vocabulary. The underlying proposition is corroborated across sources and should be linked via `realizes_source_boundary_without` rather than asserting identical terminology.

#### GRAPH-ARC-011 — Reuse and abstraction trade duplication for coordination

- **Kind:** conflict node / decision rule.
- **CA — direct_support:** Components should not force consumers to depend on unused things; reuse/release and common-reuse pressures conflict with common-closure pressure, while premature framework commitment is asymmetric. Locator: `CA: chapters/023-chapter-13-component-cohesion.md :: ## THE REUSE/RELEASE EQUIVALENCE PRINCIPLE`; `CA: chapters/023-chapter-13-component-cohesion.md :: ### THE COMMON REUSE PRINCIPLE`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### ASYMMETRIC MARRIAGE`.
- **FSA — direct_support:** Reused enterprise services increase coupling, and general-purpose/framework choices require more abstraction and governance than special-purpose code. Locator: `FSA: chapters/022-chapter-16-orchestration-driven-service-oriented-architecture.md :: ## Reuse…and Coupling`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: ### Special purpose`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: #### General purpose`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: #### Framework`.
- **DDD — refinement:** A Shared Kernel is intentionally small and jointly coordinated; generic does not mean reusable, and generic subdomain sourcing depends on economics rather than purity. Locator: `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`; `DDD: chapters/017-chapter-15-distillation.md :: ## Generic Doesn't Mean Reusable`; `DDD: chapters/017-chapter-15-distillation.md :: ## Generic Subdomains`.
- **Convergence/tension:** Strong convergence that reuse is organizational and release coupling, not only code deletion. The sources differ in unit (component, enterprise service/framework, domain model); graph edges must carry unit/scope.

#### GRAPH-DOM-012 — Domain model, language, implementation, and learning form one loop

- **Kind:** domain principle / learning process.
- **CA — corroboration:** Architecture and package structure should reveal application use cases/business rules rather than frameworks, keeping policy independently testable. Locator: `CA: chapters/032-chapter-21-screaming-architecture.md :: ## THE THEME OF AN ARCHITECTURE`; `CA: chapters/031-chapter-20-business-rules.md :: ## ENTITIES`; `CA: chapters/031-chapter-20-business-rules.md :: ### USE CASES`.
- **FSA — refinement:** Component discovery can use actors/actions, workflows, and event storming; domain partitioning makes business capabilities visible, but FSA does not prescribe a single executable domain language. Locator: `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Discovering Components`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Actor/Actions approach`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ### Event storming`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: #### Workow approach`.
- **DDD — direct_support:** Developers and experts continuously crunch knowledge in a Ubiquitous Language; a Model-Driven Design binds that language/model to code, and hands-on modelers use implementation feedback to change the model. Locator: `DDD: chapters/002-chapter-1-crunching-knowledge.md :: ## Knowledge Crunching`; `DDD: chapters/002-chapter-1-crunching-knowledge.md :: ## Continuous Learning`; `DDD: chapters/003-chapter-2-communication-and-the-use-of-language.md :: ## Ubiquitous Language`; `DDD: chapters/004-chapter-3-binding-model-and-implementation.md :: ## Model-Driven Design`; `DDD: chapters/004-chapter-3-binding-model-and-implementation.md :: ## Hands-On Modelers`.
- **Convergence/tension:** DDD is the direct foundation. CA corroborates visible policy and FSA offers discovery heuristics; neither independently supports every claim in the DDD learning loop.

#### GRAPH-DOM-013 — Aggregate is an invariant and consistency boundary

- **Kind:** domain technique / preservation boundary.
- **CA — refinement:** Enterprise business rules and use cases should be explicit and boundary data should not carry framework details, but CA's “Entity” is a policy layer—not DDD's identity-bearing Entity or Aggregate. Locator: `CA: chapters/031-chapter-20-business-rules.md :: ## ENTITIES`; `CA: chapters/031-chapter-20-business-rules.md :: ### USE CASES`; `CA: chapters/033-chapter-22-the-clean-architecture.md :: #### WHICH DATA CROSSES THE BOUNDARIES`.
- **FSA — refinement:** Service granularity and data isolation are constrained by transactions; distributed workflows may require sagas and changed consistency semantics. Locator: `FSA: chapters/023-chapter-17-microservices-architecture.md :: #### Transactions`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Data Isolation`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Transactions and Sagas`.
- **DDD — direct_support:** An Aggregate defines a cluster and root whose boundary protects invariants; factories and repositories manage creation and reconstitution without exposing internals. Locator: `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Factories`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Repositories`.
- **Convergence/tension:** Only DDD directly defines Aggregate. FSA supplies distribution consequences and CA supplies policy/boundary constraints. The graph must not alias CA Entity, DDD Entity, database entity, and Aggregate.

#### GRAPH-DOM-014 — Bounded Context protects model integrity

- **Kind:** domain boundary / semantic ownership concept.
- **CA — refinement:** Policy/detail and use-case boundaries protect different rules from volatile mechanisms and cross-cutting changes, but CA does not define a context through language/model consistency. Locator: `CA: chapters/027-chapter-16-independence.md :: ### DECOUPLING USE CASES`; `CA: chapters/033-chapter-22-the-clean-architecture.md :: ## THE DEPENDENCY RULE`.
- **FSA — refinement:** A bounded context can inform an architectural quantum or microservice boundary, but deployment, synchronous coupling, and architecture characteristics also determine the quantum. Locator: `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Domain-Driven Design's Bounded Context`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Bounded Context`.
- **DDD — direct_support:** Explicitly delimit the conditions under which one model applies, continuously integrate it internally, map it to other contexts, and test boundaries. Locator: `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Continuous Integration`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Context Map`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Testing at the C***ONTEXT* **Boundaries`.
- **Convergence/tension:** FSA historically adapts DDD vocabulary into deployment reasoning. This is a legitimate refinement but creates a known risk of equating semantic context with microservice; keep `may_inform` rather than `maps_one_to_one_to`.

#### GRAPH-DOM-015 — Context relationship follows control, semantic distance, and economics

- **Kind:** domain decision rule / relationship taxonomy.
- **CA — derived_inference:** A facade/adapter can protect policy from an external detail, but CA provides no organizational relationship taxonomy equivalent to DDD's Shared Kernel, Conformist, or Customer/Supplier. Locator: `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### THE SOLUTION`.
- **FSA — refinement:** Data location, communication style, organizational factors, and operational concerns constrain inter-component/service relationships, but FSA does not model upstream/downstream power as a named taxonomy. Locator: `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: #### Data architecture`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: #### Organizational factors`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## What communication styles between services—synchronous or asynchronous?`.
- **DDD — direct_support:** Choose Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Separate Ways, or Open Host/Published Language according to cooperation, control, model conflict, interface breadth, and integration value. Locator: `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Relationships Between B***OUNDED* **C***ONTEXTS`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Customer/Supplier Development Teams`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Conformist`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Anticorruption Layer`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Separate Ways`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Open Host Service`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Published Language`.
- **Convergence/tension:** The canonical relationship decision rule is DDD-led. CA/FSA corroborate adapter and operational forces but must not be cited as direct support for DDD's organizational semantics.

#### GRAPH-ARC-016 — Architecture requires executable feedback and independent verification

- **Kind:** universal principle / verification rule.
- **CA — direct_support:** Architecture should make business rules independently testable; tests are system components crossing a boundary, though a testing API can create coupling/security risk. Locator: `CA: chapters/032-chapter-21-screaming-architecture.md :: ### TESTABLE ARCHITECTURES`; `CA: chapters/039-chapter-28-the-test-boundary.md :: ## TESTS AS SYSTEM COMPONENTS`; `CA: chapters/039-chapter-28-the-test-boundary.md :: ### THE TESTING API`.
- **FSA — direct_support:** Fitness functions govern architecture characteristics continuously, while risk assessment/storming supplies collaborative evidence and mitigations. Locator: `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Governance and Fitness Functions`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`; `FSA: chapters/027-chapter-20-analyzing-architecture-risk.md :: ## Risk Storming`.
- **DDD — corroboration:** Models improve through working code, continuous integration within a context, boundary tests, prototypes, and strategic feedback. Locator: `DDD: chapters/004-chapter-3-binding-model-and-implementation.md :: ## Hands-On Modelers`; `DDD: chapters/011-chapter-9-making-implicit-concepts-explicit.md :: ## Clearing Development Logjams with Working Prototypes`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Continuous Integration`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The decision process must absorb feedback`.
- **Convergence/tension:** All require feedback, but they verify different things: behavior/policy isolation, quality/structural fitness, and semantic model fit. Passing one does not establish the others or constitute stakeholder acceptance.

#### GRAPH-ARC-017 — Significant decisions need explicit context, authority, and supersession

- **Kind:** agent-conduct principle / decision record.
- **CA — derived_inference:** Architecture protects stakeholders from premature implementation commitments, but CA gives no ADR/status/authorization schema. Locator: `CA: chapters/026-chapter-15-what-is-architecture.md :: ### KEEPING OPTIONS OPEN`; `CA: chapters/028-chapter-17-boundaries-drawing-lines.md :: ## WHICH LINES DO YOU DRAW, AND WHEN DO YOU DRAW THEM?`.
- **FSA — direct_support:** Architecturally significant decisions should be captured in ADRs with status, context, decision, consequences, compliance, notes, durable storage, and RFC interaction; anti-patterns include CYA, repeated forgotten decisions, and email-only architecture. Locator: `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecture Decision Anti-Patterns`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecturally Significant`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecture Decision Records`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## ADRs and Request for Comments (RFC)`.
- **DDD — refinement:** Strategic choices may be team-level or higher, must reach the entire team, absorb feedback, and allow evolution; strategy setters should not monopolize implementation insight. Locator: `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Team Decision or Higher`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Who Sets the Strategy?`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Decisions must reach the entire team`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The plan must allow for evolution`.
- **Convergence/tension:** FSA directly supplies the record mechanics; DDD supplies decision legitimacy/communication/feedback; CA supplies commitment cost. The explicit agent transition model remains a derived doctrine extension, not direct book consensus.

#### GRAPH-ARC-018 — Framework adoption is an asymmetric, scope-dependent commitment

- **Kind:** risk principle / technique-selection rule.
- **CA — direct_support:** Framework authors optimize adoption into their framework, while the application bears lifecycle coupling; isolate the framework and avoid inheriting from it throughout core policy when commitment is not justified. Locator: `CA: chapters/044-chapter-32-frameworks-are-details.md :: ## FRAMEWORK AUTHORS`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### ASYMMETRIC MARRIAGE`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### THE RISKS`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### THE SOLUTION`.
- **FSA — refinement:** Special-purpose code, general-purpose code, and frameworks require increasing generality and control; architects should justify that abstraction level to teams rather than equating framework construction with quality. Locator: `FSA: chapters/029-chapter-22-making-teams-effective.md :: ### Special purpose`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: #### General purpose`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: #### Framework`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: ## The Impact of Business Justifications`.
- **DDD — corroboration:** Technical frameworks should emerge from demonstrated application needs, and pluggable component frameworks are ambitious structures whose restrictiveness must fit the model/team. Locator: `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Pluggable Component Framework`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## How Restrictive Should a Structure Be?`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The Same Goes for the Technical Frameworks`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ### Don't write frameworks for dummies`.
- **Convergence/tension:** Strong convergence against premature framework generalization. CA is most categorical; DDD allows an earned pluggable framework in mature domains; FSA frames an abstraction/business-justification continuum. Preserve that contextual disagreement.

#### GRAPH-DOM-019 — Concentrate scarce design effort on the Core Domain

- **Kind:** domain strategy / prioritization rule.
- **CA — refinement:** High-level business rules and use cases should be independent of delivery/storage details, focusing architecture on policy rather than framework mechanics. Locator: `CA: chapters/030-chapter-19-policy-and-level.md :: ## LEVEL`; `CA: chapters/031-chapter-20-business-rules.md :: ## ENTITIES`; `CA: chapters/031-chapter-20-business-rules.md :: ### USE CASES`.
- **FSA — refinement:** Business drivers and domain concerns identify the few architecture characteristics and partitions that deserve structural attention; not every concern is architecturally significant. Locator: `FSA: chapters/010-chapter-5-identifying-architectural-characteristics.md :: ## Extracting Architecture Characteristics from Domain Concerns`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: ## Architecturally Significant`.
- **DDD — direct_support:** Distill the differentiating Core Domain, separate Generic Subdomains and cohesive mechanisms, assign strong people to the core, and use strategic value/risk to choose sourcing and refactoring targets. Locator: `DDD: chapters/017-chapter-15-distillation.md :: ## Core Domain`; `DDD: chapters/017-chapter-15-distillation.md :: ## Generic Subdomains`; `DDD: chapters/017-chapter-15-distillation.md :: ## Who Does the Work?`; `DDD: chapters/017-chapter-15-distillation.md :: ## Project Risk Management`; `DDD: chapters/017-chapter-15-distillation.md :: ## Choosing Refactoring Targets`.
- **Convergence/tension:** DDD uniquely supplies the portfolio strategy. CA's “business rules” and FSA's “business drivers” support focus but do not establish that a capability is a Core Domain; that classification needs product/domain evidence.

#### GRAPH-ARC-020 — Team topology is an architectural force, not an automatic boundary

- **Kind:** socio-technical principle / contextual lens.
- **CA — refinement:** Development and deployment independence can motivate separation, but services do not guarantee independent teams when changes cross them. Locator: `CA: chapters/027-chapter-16-independence.md :: ## INDEPENDENT DEVELOP-ABILITY`; `CA: chapters/027-chapter-16-independence.md :: ### INDEPENDENT DEPLOYABILITY`; `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE FALLACY OF INDEPENDENT DEVELOPMENT AND DEPLOYMENT`.
- **FSA — direct_support:** Conway's Law, team boundaries, familiarity, size, experience, project complexity, and duration shape partitioning and the appropriate degree of architectural control. Locator: `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Conway's Law`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: ## Team Boundaries`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: ## How Much Control?`.
- **DDD — refinement:** Model/context strategy depends on team decision rights and communication; architecture teams must not siphon modelers away from implementation feedback. Locator: `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Team Decision or Higher`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Who Sets the Strategy?`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Architecture teams must not siphon off all the best and brightest`.
- **Convergence/tension:** All recognize socio-technical coupling. None justifies “one team equals one service/context” as a universal rule; ownership is evidence for a boundary only when semantic/change/quality forces align.

#### GRAPH-ARC-021 — Leave structure unchanged when intervention is not earned

- **Kind:** negative doctrine / terminal decision.
- **CA — refinement:** Full and partial boundaries have ongoing costs, and retrospective examples show grand redesign or premature architecture can fail; unattractive directness may be cheaper until a real policy/detail pressure appears. Locator: `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24: Partial Boundaries`; `CA: chapters/047-vii-appendix.md :: #### THE GRAND REDESIGN IN THE SKY`; `CA: chapters/047-vii-appendix.md :: #### THE SCHEDULE TRAP`.
- **FSA — direct_support:** Architecture is the least-worst trade-off under current drivers, and style selection begins with domain/data/organization/operations rather than a target fashion; no candidate is universally superior. Locator: `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Trade-Offs and Least Worst Architecture`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Shifting "Fashion" in Architecture`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`.
- **DDD — direct_support:** Use Smart UI for genuinely simple domains, keep strategic structure minimalist and humble, and reject a master plan that exceeds current insight. Locator: `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Minimalism`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Strategic design requires minimalism and humility`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Beware the Master Plan`.
- **Convergence/tension:** This node is a high-confidence derived operational rule. The sources do not celebrate inaction; they condition intervention on forces, value, and learning. “Leave unchanged” must therefore include preservation rationale and a revisit trigger, not indifference.

### Candidate typed edges with provenance

Edge predicates are intentionally specific. `may_inform_but_not_entail` and `not_equivalent_to` are first-class so retrieval cannot silently turn correlation into architectural obligation.

| Edge ID | From | Typed relation | To | Selection condition / meaning | Provenance |
|---|---|---|---|---|---|
| GEDGE-001 | GRAPH-ARC-001 | governs_selection_of | GRAPH-ARC-003 | A boundary is selectable only after its claimed force and current harm are evidenced. | **derived_inference:** CA boundary timing plus lifetime-effort goal (`CA: chapters/028-chapter-17-boundaries-drawing-lines.md :: ## WHICH LINES DO YOU DRAW, AND WHEN DO YOU DRAW THEM?`; `CA: chapters/008-chapter-1-what-is-design-and-architecture.md :: ## THE GOAL?`); corroborated by `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria` and `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Assessment First`. |
| GEDGE-002 | GRAPH-ARC-002 | provides_driver_for | GRAPH-ARC-003 | A scoped characteristic can earn a structural boundary when the boundary is necessary to meet its threshold. | **direct_support/refinement:** `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Analyze Architecture Characteristics`. |
| GEDGE-003 | GRAPH-ARC-006 | provides_change_evidence_for | GRAPH-ARC-003 | Recurring independent closure/cohesion may earn a module/component boundary, but similarity alone does not. | **direct_support/corroboration:** `CA: chapters/023-chapter-13-component-cohesion.md :: ### THE COMMON CLOSURE PRINCIPLE`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Component Granularity`; `DDD: chapters/012-chapter-10-supple-design.md :: ## Conceptual Contours`. |
| GEDGE-004 | GRAPH-DOM-014 | provides_semantic_evidence_for | GRAPH-ARC-003 | Model-language discontinuity can earn a semantic boundary; it does not alone earn process/network separation. | **direct_support + derived restriction:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Deployment`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Domain-Driven Design's Bounded Context`. |
| GEDGE-005 | GRAPH-ARC-003 | instantiated_at_strength | GRAPH-ARC-004 | An earned boundary must separately select source, release, process, network, or relationship strength. | **direct_support:** `CA: chapters/029-chapter-18-boundary-anatomy.md :: ## BOUNDARY CROSSING`; refinement by `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Deployment`. |
| GEDGE-006 | GRAPH-ARC-003 | may_protect | GRAPH-ARC-005 | Boundary direction can protect stable policy/domain semantics from a volatile mechanism. | **direct_support:** `CA: chapters/033-chapter-22-the-clean-architecture.md :: ## THE DEPENDENCY RULE`; corroborated by `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Domain Layer Is Where the Model Lives`. |
| GEDGE-007 | GRAPH-ARC-005 | may_be_realized_by | GRAPH-ARC-010 | A modular monolith can enforce policy/domain source boundaries without network distribution. | **derived_inference:** `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY COMPONENT`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Modular Monolith`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Modules (a.k.a. Packages)`. |
| GEDGE-008 | GRAPH-ARC-007 | favors_reversible_strength_in | GRAPH-ARC-004 | When evidence is incomplete and change plausible, prefer a lower-cost seam that can be strengthened; do not reserve every option. | **refinement/derived_inference:** `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24: Partial Boundaries`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The plan must allow for evolution`; constrained by `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Trade-Offs and Least Worst Architecture`. |
| GEDGE-009 | GRAPH-ARC-021 | constrains_option_carrying_by | GRAPH-ARC-007 | Option preservation is rejected when carrying cost exceeds plausible delay value or no trigger exists. | **derived_inference:** CA's partial-boundary cost (`CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24: Partial Boundaries`) plus DDD minimalism (`DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Minimalism`). |
| GEDGE-010 | GRAPH-ARC-002 | constrains_selection_of | GRAPH-ARC-008 | Ranked/scoped characteristics eliminate styles and define the least-worst finalist set. | **direct_support:** `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Trade-Offs and Least Worst Architecture`. |
| GEDGE-011 | GRAPH-ARC-009 | imposes_cost_on | GRAPH-ARC-004 | Crossing a network boundary adds failure, latency, security, versioning, transaction and operational costs absent from source-only seams. | **direct_support:** `FSA: chapters/015-chapter-9-foundations.md :: ## Fallacy #1: The Network Is Reliable`; `FSA: chapters/015-chapter-9-foundations.md :: ## Other Distributed Considerations`; `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE DECOUPLING FALLACY`. |
| GEDGE-012 | GRAPH-ARC-009 | increases_prior_probability_of | GRAPH-ARC-010 | When no irreducible distribution driver exists, a modular monolith is the lower-operational-cost candidate. | **derived_inference:** `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Modular Monolith`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Monolith versus distributed`; corroborated by `CA: chapters/029-chapter-18-boundary-anatomy.md :: ### THE DREADED MONOLITH`. |
| GEDGE-013 | GRAPH-DOM-014 | may_inform_but_not_entail | GRAPH-ARC-010 | A Bounded Context may be one in-process module; it is not defined by being a module. | **direct_support/refinement:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## B***OUNDED* **C***ONTEXTS* **Are Not M***ODULES`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Modular Monolith`. |
| GEDGE-014 | GRAPH-DOM-014 | may_inform_but_not_entail | GRAPH-ARC-004 | A semantic context may motivate a deployable boundary, but architecture characteristics and operations must separately earn boundary strength. | **refinement:** `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Domain-Driven Design's Bounded Context`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Architectural Quanta and Granularity`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Deployment`. |
| GEDGE-015 | GRAPH-ARC-011 | may_conflict_with | GRAPH-ARC-006 | Reuse grouping can increase change coupling when consumers do not close against the same changes; change locality can justify duplication. | **direct_support:** tension within `CA: chapters/023-chapter-13-component-cohesion.md :: ## THE TENSION DIAGRAM FOR COMPONENT COHESION`; corroborated by `FSA: chapters/022-chapter-16-orchestration-driven-service-oriented-architecture.md :: ## Reuse…and Coupling` and `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`. |
| GEDGE-016 | GRAPH-ARC-018 | specializes | GRAPH-ARC-011 | Framework generalization/reuse is a particularly asymmetric and high-commitment abstraction decision. | **direct_support/refinement:** `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### ASYMMETRIC MARRIAGE`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: #### Framework`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The Same Goes for the Technical Frameworks`. |
| GEDGE-017 | GRAPH-DOM-012 | supplies_language_evidence_for | GRAPH-DOM-014 | Contradictory meanings and model assumptions reveal candidate context boundaries. | **direct_support:** `DDD: chapters/003-chapter-2-communication-and-the-use-of-language.md :: ## Ubiquitous Language`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Recognizing Splinters Within a B***OUNDED* **C***ONTEXT`. |
| GEDGE-018 | GRAPH-DOM-012 | supplies_model_evidence_for | GRAPH-DOM-013 | Explicit invariants, identity, lifecycle and commands justify an Aggregate; nouns/object graphs do not. | **derived_inference from direct DDD concepts:** `DDD: chapters/002-chapter-1-crunching-knowledge.md :: ## Knowledge-Rich Design`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates`. |
| GEDGE-019 | GRAPH-DOM-013 | defines_preservation_boundary_within | GRAPH-DOM-014 | Aggregate invariants are enforced inside a model context; identical terms in another context need not share that aggregate. | **refinement/derived_inference:** `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`. |
| GEDGE-020 | GRAPH-DOM-013 | constrains_strength_of | GRAPH-ARC-004 | Required atomicity can contraindicate a remote boundary or require authorized weaker consistency/saga semantics. | **corroboration/refinement:** `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Aggregates`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: #### Transactions`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Transactions and Sagas`. |
| GEDGE-021 | GRAPH-DOM-015 | connects_instances_of | GRAPH-DOM-014 | Context relationships make integration, control, translation and accepted semantic loss explicit. | **direct_support:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Relationships Between B***OUNDED* **C***ONTEXTS`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Choosing Your Model Context Strategy`. |
| GEDGE-022 | GRAPH-DOM-015 | may_realize_policy_protection_of | GRAPH-ARC-005 | An Anticorruption Layer may protect a valuable local model from an external mechanism/model. | **direct_support/corroboration:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Anticorruption Layer`; CA adapter/facade corroboration at `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES`. |
| GEDGE-023 | GRAPH-ARC-011 | conditions_shared_kernel_in | GRAPH-DOM-015 | Shared Kernel is selected only when shared semantics and joint coordination outperform translation/autonomy. | **direct_support:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`; corroborated by component-reuse tension at `CA: chapters/023-chapter-13-component-cohesion.md :: ## THE TENSION DIAGRAM FOR COMPONENT COHESION`. |
| GEDGE-024 | GRAPH-DOM-019 | prioritizes_investment_in | GRAPH-DOM-012 | The model-language-code learning loop receives greatest sustained effort in the differentiating Core Domain. | **direct_support:** `DDD: chapters/017-chapter-15-distillation.md :: ## Core Domain`; `DDD: chapters/017-chapter-15-distillation.md :: ## Who Does the Work?`; `DDD: chapters/017-chapter-15-distillation.md :: ## Choosing Refactoring Targets`. |
| GEDGE-025 | GRAPH-DOM-019 | prioritizes_protection_by | GRAPH-ARC-005 | High-value core policy is the strongest candidate for isolation from volatile detail, subject to repository evidence. | **derived_inference:** DDD Core Domain (`DDD: chapters/017-chapter-15-distillation.md :: ## Core Domain`) plus CA policy level (`CA: chapters/030-chapter-19-policy-and-level.md :: ## LEVEL`) and FSA business drivers (`FSA: chapters/007-chapter-2-architectural-thinking.md :: ## Understanding Business Drivers`). |
| GEDGE-026 | GRAPH-ARC-016 | feeds_evidence_back_to | GRAPH-ARC-001 | Tests, fitness functions, risk exercises, runtime measures and model experiments turn architectural intent into action evidence. | **corroboration:** `CA: chapters/039-chapter-28-the-test-boundary.md :: ## TESTS AS SYSTEM COMPONENTS`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## Fitness Functions`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The decision process must absorb feedback`. |
| GEDGE-027 | GRAPH-ARC-016 | may_invalidate_and_reopen | GRAPH-ARC-017 | Failed thresholds or model feedback can supersede an accepted decision but do not themselves grant authority to change it. | **derived_inference:** ADR compliance at `FSA: chapters/026-chapter-19-architecture-decisions.md :: #### COMPLIANCE`; feedback/evolution at `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The plan must allow for evolution`. |
| GEDGE-028 | GRAPH-ARC-017 | authorizes_transition_from | GRAPH-ARC-001 | Evidence can support a recommendation; an explicit decision/status is still required before architecture-changing execution. | **derived_inference:** FSA decision status (`FSA: chapters/026-chapter-19-architecture-decisions.md :: ### Title`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: #### Status`) and DDD decision level (`DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Team Decision or Higher`). |
| GEDGE-029 | GRAPH-ARC-020 | provides_contextual_force_for | GRAPH-ARC-003 | Team ownership/coordination may strengthen boundary evidence only when aligned with semantic/change/quality forces. | **refinement:** `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Conway's Law`; constrained by service-independence critique at `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE FALLACY OF INDEPENDENT DEVELOPMENT AND DEPLOYMENT`. |
| GEDGE-030 | GRAPH-ARC-020 | provides_contextual_force_for | GRAPH-DOM-015 | Cooperation, trust and decision rights influence Shared Kernel, Customer/Supplier, Conformist and ACL economics. | **direct_support/refinement:** `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Team Decision or Higher`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Customer/Supplier Development Teams`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: ## Team Boundaries`. |
| GEDGE-031 | GRAPH-ARC-020 | does_not_entail | GRAPH-ARC-004 | Separate teams alone do not prove separate processes/services. | **derived restriction:** `CA: chapters/038-chapter-27-services-great-and-small.md :: #### THE FALLACY OF INDEPENDENT DEVELOPMENT AND DEPLOYMENT`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ### Domain/architecture isomorphism`. |
| GEDGE-032 | GRAPH-ARC-021 | terminal_alternative_to | GRAPH-ARC-003 | If no independent force clears its evidence/cost threshold, return no boundary change with revisit conditions. | **derived_inference:** `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24: Partial Boundaries`; `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Trade-Offs and Least Worst Architecture`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Strategic design requires minimalism and humility`. |
| GEDGE-033 | GRAPH-ARC-021 | terminal_alternative_to | GRAPH-ARC-008 | If current style meets accepted characteristics and migration adds unearned cost, style remains unchanged. | **derived_inference:** `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Refactoring Toward a Fitting Structure`. |
| GEDGE-034 | GRAPH-ARC-016 | verifies_but_does_not_accept | GRAPH-ARC-017 | Technical verification establishes selected claims; acceptance remains with the authorized stakeholder/governance process. | **derived_inference:** FSA separates ADR decision/compliance (`FSA: chapters/026-chapter-19-architecture-decisions.md :: #### DECISION`; `FSA: chapters/026-chapter-19-architecture-decisions.md :: #### COMPLIANCE`); DDD locates strategy authority (`DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Who Sets the Strategy?`). |
| GEDGE-035 | GRAPH-DOM-012 | refines_semantics_of | GRAPH-ARC-005 | Domain modeling specifies what “policy” means locally; architecture cannot infer domain policy from a generic layer diagram. | **derived_inference:** `DDD: chapters/004-chapter-3-binding-model-and-implementation.md :: ## Model-Driven Design`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Domain Layer Is Where the Model Lives`; `CA: chapters/030-chapter-19-policy-and-level.md :: ## LEVEL`. |
| GEDGE-036 | GRAPH-ARC-002 | may_conflict_with | GRAPH-DOM-013 | Performance/availability/distribution goals may pressure an aggregate's consistency/representation; semantic weakening requires explicit authorization and evidence. | **refinement:** `DDD: chapters/008-chapter-7-using-the-language-an-extended-example.md :: ## Performance Tuning`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Transactions and Sagas`; `FSA: chapters/021-chapter-15-space-based-architecture-style.md :: ## Data Collisions`. |

### Convergence, disagreement, context, history, and terminology annotations

| Annotation ID | Topic | Competing source formulations | Cause classification | Graph handling / decision rule | Provenance |
|---|---|---|---|---|---|
| GANN-001 | Up-front boundaries versus evolutionary architecture | CA urges early protection of high-level policy and option preservation; DDD warns against master plans and insists on evolving order; FSA treats architecture as changing trade-offs. | **context_conditional + emphasis_difference**, not a simple contradiction. | Preserve GRAPH-ARC-007 ↔ GRAPH-ARC-021 tension. Make early structure proportional to reversal cost and credible pressure; use partial/reversible experiments when uncertainty and future cost are both material. | `CA: chapters/026-chapter-15-what-is-architecture.md :: ### KEEPING OPTIONS OPEN`; `CA: chapters/035-chapter-24-partial-boundaries.md :: # Chapter 24`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Evolving Order`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## Beware the Master Plan`; `FSA: chapters/003-preface-invalidating-axioms.md :: ## Axiom`. |
| GANN-002 | Dependency inversion versus direct dependency | CA strongly favors inward dependencies at policy/detail boundaries; DDD favors domain isolation but also simple constructors/direct modules when sufficient; FSA treats coupling/partition as trade-offs rather than universal interface insertion. | **scope_difference + context_conditional**. | Model “protect policy” separately from “introduce interface.” Direct coupling wins absent asymmetric volatility, substitution, ownership or deployment pressure; inversion wins when a stable consumer contract is evidenced. | `CA: chapters/020-chapter-11-dip-the-dependency-inversion-principle.md :: ## STABLE ABSTRACTIONS`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## When a Constructor Is All You Need`; `FSA: chapters/008-chapter-3-modularity.md :: ## Coupling`. |
| GANN-003 | Domain purity versus implementation simplicity | DDD values a model isolated from technical concerns but explicitly permits Smart UI for simple work; CA favors policy isolation; FSA accepts technically partitioned layered architecture where its trade-offs fit. | **genuine_contextual_alternatives**. | Do not merge into “always isolate domain.” Activate deep domain/policy isolation only with strategic rule complexity, longevity and expert feedback; use direct/layered transaction scripts for genuinely simple contexts with a growth trigger. | `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Domain Layer Is Where the Model Lives`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## The Smart UI "Anti-Pattern"`; `CA: chapters/033-chapter-22-the-clean-architecture.md :: ## THE DEPENDENCY RULE`; `FSA: chapters/016-chapter-10-layered-architecture-style.md :: ## Why Use This Architecture Style`. |
| GANN-004 | Uniform structure versus contextual structure | CA presents a strongly directional architecture family; FSA explicitly chooses styles per drivers; DDD requires fitting, minimal large-scale structures and permits multiple contexts. | **genuine_emphasis_difference + granularity_difference**. | Store CA's dependency rule as one technique/principle node, not the graph root. Route it only where protected policy exists; allow per-quantum/context styles with explicit crossings. | `CA: chapters/033-chapter-22-the-clean-architecture.md :: ## THE DEPENDENCY RULE`; `CA: chapters/033-chapter-22-the-clean-architecture.md :: #### ONLY FOUR CIRCLES?`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Decision Criteria`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## How Restrictive Should a Structure Be?`. |
| GANN-005 | Services versus modular monolith | CA rejects “services imply architecture/decoupling”; FSA describes service styles and microservices as valid under strong drivers while preserving modular monolith as a candidate; DDD separates model context from deployment. | **context_conditional + historical_misapplication**. | Maintain service and context/module nodes separately. Require irreducible deployment/scale/isolation force plus distributed readiness; otherwise favor in-process modularity. | `CA: chapters/038-chapter-27-services-great-and-small.md :: ## SERVICE ARCHITECTURE?`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ## Modular Monolith`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Data Isolation`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Deployment`. |
| GANN-006 | Full boundary versus partial/no boundary | CA itself preserves the disagreement: full boundary maximizes independence but costs interfaces/types/maintenance; partial boundaries reserve some option but may fail to protect; DDD minimalism and FSA trade-offs reinforce restraint. | **cost_threshold_conflict**. | Graph `full`, `partial`, `direct` as alternatives with distinct protection/cost, not maturity stages. Select cheapest sufficient current protection and give partial seams completion/deletion triggers. | `CA: chapters/035-chapter-24-partial-boundaries.md :: ## SKIP THE LAST STEP`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### ONE-DIMENSIONAL BOUNDARIES`; `CA: chapters/035-chapter-24-partial-boundaries.md :: ### FACADES`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Minimalism`; `FSA: chapters/009-chapter-4-architecture-characteristics-defined.md :: ## Trade-Offs and Least Worst Architecture`. |
| GANN-007 | Technical layers versus domain partition | CA's missing-chapter discussion favors package-by-component for enforceable use cases but describes multiple package strategies; FSA lists advantages/disadvantages of both; DDD uses a technical layered isolation plus domain modules/contexts. | **orthogonal_axes often falsely treated as exclusive**. | Represent technical concern, domain ownership, source visibility, and deployment as separate partition dimensions. A system may use technical layers inside domain modules; choose based on change locality and enforcement. | `CA: chapters/046-chapter-34-the-missing-chapter.md :: ## PACKAGE BY LAYER`; `CA: chapters/046-chapter-34-the-missing-chapter.md :: ### PACKAGE BY COMPONENT`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Architecture Partitioning`; `DDD: chapters/005-chapter-4-isolating-the-domain.md :: ## Layered Architecture`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Modules (a.k.a. Packages)`. |
| GANN-008 | One unified model versus multiple contexts | DDD directly rejects a single unbounded enterprise model where meanings conflict, yet supports Shared Kernel/merging under close integration; FSA borrows bounded context for quanta; CA's policy hierarchy can be misread as one global model. | **genuine_contextual_alternatives + terminology_transfer**. | Keep unify/split/translate as candidates. Unify when meanings/authority/change are coherent and translation has no value; split when contradictions/ownership require integrity; never infer from directory or service count. | `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Bounded Context`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Unifying an Elephant`; `FSA: chapters/012-chapter-7-scope-of-architecture-characteristics.md :: ## Domain-Driven Design's Bounded Context`. |
| GANN-009 | Reuse versus local duplication | CA's cohesion principles explicitly pull in different directions; FSA warns reuse creates coupling; DDD permits small Shared Kernels but says generic is not automatically reusable. | **genuine_tradeoff**. | Do not average into “balanced reuse.” Share only stable semantics with real coordinated consumers/governance; duplicate when similarity is syntactic or change/authority diverges; set a revisit trigger. | `CA: chapters/023-chapter-13-component-cohesion.md :: ## THE TENSION DIAGRAM FOR COMPONENT COHESION`; `FSA: chapters/022-chapter-16-orchestration-driven-service-oriented-architecture.md :: ## Reuse…and Coupling`; `DDD: chapters/017-chapter-15-distillation.md :: ## Generic Doesn't Mean Reusable`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## Shared Kernel`. |
| GANN-010 | Entity terminology | CA “Entity” means enterprise-wide high-level business rules; DDD Entity means an object defined by identity and lifecycle; FSA's “entity trap” means deriving components from data entities. | **terminology_collision**. | Create distinct nodes: `enterprise-policy`, `identity-entity`, and `data-record`. Add `not_equivalent_to` edges; never route a rule about one from the word “entity” alone. | `CA: chapters/031-chapter-20-business-rules.md :: ## ENTITIES`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Entities (a.k.a. Reference Objects)`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Entity trap`. |
| GANN-011 | Service terminology | CA mostly discusses deployable services; FSA uses service-based/SOA/microservice topologies; DDD Domain Service is a stateless domain operation that may be in-process. | **terminology_collision + scale_difference**. | Type every service node (`domain-operation`, `application-service`, `deployable-service`, `microservice`, `enterprise-service`). Disallow untyped `service` edges in machine-readable doctrine. | `CA: chapters/038-chapter-27-services-great-and-small.md :: # Chapter 27: Services: Great and Small`; `FSA: chapters/019-chapter-13-service-based-architecture-style.md :: ## Topology`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## Topology`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Services`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## S***ERVICES* **and the Isolated Domain Layer`. |
| GANN-012 | Component/module terminology | CA component is a deployable/release unit and also discusses source components; FSA defines component as architecture building block with language/platform-dependent scope; DDD Module is a conceptual package and explicitly distinguishes it from Bounded Context. | **terminology_collision + technology_context**. | Store artifact type and scale on every node: source module/package, release component, deployable unit, quantum, context. No `same_as` edge based only on “component/module.” | `CA: chapters/022-chapter-12-components.md :: # Chapter 12: Components`; `FSA: chapters/013-chapter-8-component-based-thinking.md :: ## Component Scope`; `DDD: chapters/006-chapter-5-a-model-expressed-in-software.md :: ## Modules (a.k.a. Packages)`; `DDD: chapters/016-chapter-14-maintaining-model-integrity.md :: ## B***OUNDED* **C***ONTEXTS* **Are Not M***ODULES`. |
| GANN-013 | Policy terminology | CA policy is a statement/calculation whose “level” relates to distance from input/output; DDD Strategy/Policy is often an explicit domain object/algorithm; FSA uses business drivers and architecture decisions. | **terminology_overlap without identity**. | Connect DDD policy to domain semantic nodes and CA policy to dependency-level nodes by `may_instantiate`; do not infer architectural level solely from a class named Policy. | `CA: chapters/030-chapter-19-policy-and-level.md :: # Chapter 19: Policy and Level`; `DDD: chapters/014-chapter-12-relating-design-patterns-to-the-model.md :: ## Strategy (A.K.A.Policy)`; `FSA: chapters/007-chapter-2-architectural-thinking.md :: ## Understanding Business Drivers`. |
| GANN-014 | Architecture metrics versus outcomes | CA uses component metrics/“main sequence”; FSA catalogs complexity/coupling/fitness while warning definitions are not physics; DDD relies more on model fit/feedback than numeric structure metrics. | **epistemic_difference**. | Treat metrics as evidence signals/proxies with scope and limits, never automated verdicts. Require a causal link to an accepted outcome and corroborate expensive changes. | `CA: chapters/024-chapter-14-component-coupling.md :: #### STABILITY METRICS`; `CA: chapters/024-chapter-14-component-coupling.md :: #### THE MAIN SEQUENCE`; `FSA: chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: ## They aren't physics`; `FSA: chapters/008-chapter-3-modularity.md :: ## Limitations of Metrics`; `DDD: chapters/019-chapter-17-bringing-the-strategy-together.md :: ## The decision process must absorb feedback`. |
| GANN-015 | Framework restraint versus framework as architecture | CA characterizes frameworks as volatile details and asymmetric commitments; DDD presents an earned Pluggable Component Framework for mature structure; FSA treats microkernel/framework generality as a valid style/continuum. | **genuine_contextual_alternatives + maturity_difference**. | Framework is earned by multiple demonstrated consumers, stable contracts, extension economics and lifecycle budget. Isolate it when commitment is asymmetric; do not generalize one application speculatively. | `CA: chapters/044-chapter-32-frameworks-are-details.md :: ### ASYMMETRIC MARRIAGE`; `FSA: chapters/018-chapter-12-microkernel-architecture-style.md :: ## Plug-In Components`; `FSA: chapters/029-chapter-22-making-teams-effective.md :: #### Framework`; `DDD: chapters/018-chapter-16-large-scale-structure.md :: ## Pluggable Component Framework`. |
| GANN-016 | Historical operating context | DDD (2003) reasons heavily through OO/Java, relational persistence, EJB-era frameworks and pre-microservice contexts; CA (2017) reacts to web/framework/database coupling and service hype; FSA (2020) assumes cloud, DevOps, microservices, eventing and modern operational platforms. | **historical_shift** affecting examples, costs and available mechanisms. | Preserve timeless force separately from historical mechanism. Revalidate operational cost, language/platform idiom, deployment tooling, security and data assumptions in the target repository before recommendation. | `DDD: chapters/004-chapter-3-binding-model-and-implementation.md :: ## Modeling Paradigms and Tool Support`; `DDD: chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: ## Working Within Your Frameworks`; `CA: chapters/043-chapter-31-the-web-is-a-detail.md :: # Chapter 31: The Web Is a Detail`; `CA: chapters/044-chapter-32-frameworks-are-details.md :: # Chapter 32`; `FSA: chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: ### Technology changes`; `FSA: chapters/023-chapter-17-microservices-architecture.md :: ## History`. |

### Graph-ingestion safeguards

- Preserve source-formulation nodes or provenance properties beneath every canonical node; do not replace three contextual claims with one unattributed maxim.
- Never create `same_as` from lexical matches alone. The known collision terms are **entity**, **service**, **component**, **module**, **policy**, **layer**, **boundary**, and **model**.
- Encode source date/role and formulation relation on every provenance edge. A `derived_inference` cannot be upgraded to `direct_support` through repeated retrieval.
- Encode applicability and contraindication as graph predicates, not prose-only metadata; otherwise retrieval will surface techniques without their evidence gates.
- Preserve negative and `not_equivalent_to` edges. They prevent bounded-context→microservice, interface→decoupling, service→independent deployment, tests→acceptance, and metric→verdict inference errors.
- A graph traversal must stop at repository contracts and authority boundaries. Doctrine can propose supersession; it cannot silently outrank or rewrite an accepted project decision.
- Retrieval should rank direct support before corroboration, corroboration before refinement for the same claim, and derived inference last; conflict nodes must be co-retrieved with either competing position.
- Conversion caveats remain provenance metadata: malformed OCR headings, missing image semantics, and anecdotal examples lower locator precision/confidence even when the chapter was read completely.
