# Implementation-Craft Sources: Evidence Extraction

Status: complete source-lane extraction for synthesis. This is not a book summary, and none of the three sources is treated as normative by reputation alone.

## Scope, source IDs, and locator convention

The converted Markdown sets for all three assigned sources were inspected, including front matter, part dividers, appendices, exercise answers, summaries, indexes, and bibliographies. Reference-only and publication-only files appear in the coverage ledger but do not independently support actionable doctrine.

- `CC` — *Code Complete, Second Edition*.
  - `CC_ROOT = books/code-complete-2nd-edition-v413hav`
- `PP` — *The Pragmatic Programmer: From Journeyman to Master*.
  - `PP_ROOT = books/the-pragmatic-programmer`
- `APOSD` — *A Philosophy of Software Design, Second Edition*.
  - `APOSD_ROOT = books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217`

Every locator below has the form `SOURCE_ID: chapters/<file> :: <Markdown heading>`. It is relative to the declared source root and resolves to an exact converted file and heading. APOSD conversion retained only chapter-level Markdown headings, so its locators are necessarily chapter-granular. Claims are paraphrases; numerical claims and prescriptions remain contextual unless the repository supplies corroborating evidence.

## Complete chapter coverage ledger

### CC coverage (48/48 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `CC_ROOT/chapters/001-complete.md` | Complete | Cover, edition, copyright, endorsements, and high-level contents; publication context only. |
| `CC_ROOT/chapters/002-table-of-contents.md` | Table of Contents | Navigation and chapter/heading cross-check; no independent doctrine. |
| `CC_ROOT/chapters/003-preface.md` | Preface | Construction scope, audience, evidence/experience basis, balanced-practice intent, and limits of a construction-focused source. |
| `CC_ROOT/chapters/004-acknowledgments.md` | Acknowledgments | Reviewer and practitioner provenance; no independent doctrine. |
| `CC_ROOT/chapters/005-part-i-laying-the-foundation.md` | Part I: Laying the Foundation | Part divider and navigation only. |
| `CC_ROOT/chapters/006-chapter-1-welcome-to-software-construction.md` | Chapter 1: Welcome to Software Construction | Construction as detailed design, coding, debugging, developer testing, review, and integration; source code as an important operational description. |
| `CC_ROOT/chapters/007-chapter-2-metaphors-for-a-richer-understanding-of-software-development.md` | Chapter 2: Metaphors for a Richer Understanding of Software Development | Models as fallible heuristics; construction, growth, and accretion metaphors; select and combine models without overextending them. |
| `CC_ROOT/chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md` | Chapter 3: Measure Twice, Cut Once: Upstream Prerequisites | Problem/requirement/architecture readiness, iterative versus sequential context, risks, error/security/performance/scalability policies, feasibility, buy/build/reuse, and change strategy. |
| `CC_ROOT/chapters/009-chapter-4-key-construction-decisions.md` | Chapter 4: Key Construction Decisions | Language strengths/limits, repository conventions, technology maturity, programming into a language, construction-practice selection, tooling and integration policy. |
| `CC_ROOT/chapters/010-part-ii-creating-high-quality-code.md` | Part II: Creating High-Quality Code | Part divider and navigation only. |
| `CC_ROOT/chapters/011-chapter-5-design-in-construction.md` | Chapter 5: Design in Construction | Complexity management, heuristic/iterative design, information hiding, coupling/cohesion, change isolation, contracts, testability, alternatives, prototyping, and proportionate design records. |
| `CC_ROOT/chapters/012-chapter-6-working-classes.md` | Chapter 6: Working Classes | ADTs, class abstraction and encapsulation, containment versus inheritance, constructor validity, class creation/avoidance, packages, and interface quality. |
| `CC_ROOT/chapters/013-chapter-7-high-quality-routines.md` | Chapter 7: High-Quality Routines | Reasons to extract, functional cohesion, naming and side effects, routine length evidence, parameter contracts, functions/procedures, macro and inline hazards. |
| `CC_ROOT/chapters/014-chapter-8-defensive-programming.md` | Chapter 8: Defensive Programming | Invalid-input containment, assertions, error policy, robustness/correctness trade-off, exceptions, trust boundaries, debug aids, and production hardening. |
| `CC_ROOT/chapters/015-chapter-9-the-pseudocode-programming-process.md` | Chapter 9: The Pseudocode Programming Process | Intent-first routine design, iterative code translation, review, testing, cleanup, and alternatives; pseudocode as a design probe rather than required notation. |
| `CC_ROOT/chapters/016-part-iii-variables.md` | Part III: Variables | Part divider and navigation only. |
| `CC_ROOT/chapters/017-chapter-10-general-issues-in-using-variables.md` | Chapter 10: General Issues in Using Variables | Data literacy, initialization, minimal scope/live time, persistence, binding time, data/control alignment, and one-purpose variables. |
| `CC_ROOT/chapters/018-chapter-11-the-power-of-variable-names.md` | Chapter 11: The Power of Variable Names | Problem-oriented naming, scope-sensitive length, semantic qualifiers/opposites, booleans/enums/constants, naming conventions, abbreviations, and reader cost. |
| `CC_ROOT/chapters/019-chapter-12-fundamental-data-types.md` | Chapter 12: Fundamental Data Types | Numeric bounds/precision, strings, booleans, enumerations, constants, arrays, and domain-specific types; examples strongly language/era dependent. |
| `CC_ROOT/chapters/020-chapter-13-unusual-data-types.md` | Chapter 13: Unusual Data Types | Structures, pointer representation/ownership hazards, global-data costs, access mediation, and containment of unavoidable globals. |
| `CC_ROOT/chapters/021-part-iv-statements.md` | Part IV: Statements | Part divider and navigation only. |
| `CC_ROOT/chapters/022-chapter-14-organizing-straight-line-code.md` | Chapter 14: Organizing Straight-Line Code | Make ordering dependencies explicit; top-to-bottom flow; group semantically related statements. |
| `CC_ROOT/chapters/023-chapter-15-using-conditionals.md` | Chapter 15: Using Conditionals | Nominal-path clarity, positive conditions, branch ordering, exhaustive/default handling, and choosing conditional forms. |
| `CC_ROOT/chapters/024-chapter-16-controlling-loops.md` | Chapter 16: Controlling Loops | Loop-form selection, entry/exit invariants, early exits, endpoint correctness, one-purpose indexes, nesting, and inside-out construction. |
| `CC_ROOT/chapters/025-chapter-17-unusual-control-structures.md` | Chapter 17: Unusual Control Structures | Multiple returns, recursion constraints, rare `goto` cases, cleanup/error-flow trade-offs, and control-flow reviewability. |
| `CC_ROOT/chapters/026-chapter-18-table-driven-methods.md` | Chapter 18: Table-Driven Methods | Replacing complicated logic with direct/indexed/stair-step tables, lookup-key design, configuration/data trade-offs, and readability/performance conditions. |
| `CC_ROOT/chapters/027-chapter-19-general-control-issues.md` | Chapter 19: General Control Issues | Boolean clarity, block/null-statement hazards, taming nesting, structured flow, decision complexity, and measurement as a warning signal. |
| `CC_ROOT/chapters/028-part-v-code-improvements.md` | Part V: Code Improvements | Part divider and navigation only. |
| `CC_ROOT/chapters/029-chapter-20-the-software-quality-landscape.md` | Chapter 20: The Software-Quality Landscape | Quality attributes and trade-offs, explicit objectives, complementary prevention/detection methods, timing, and cost-of-defect evidence. |
| `CC_ROOT/chapters/030-chapter-21-collaborative-construction.md` | Chapter 21: Collaborative Construction | Pairing, inspections, walkthroughs, code reading, role/checklist discipline, complementary defect detection, and non-personal review. |
| `CC_ROOT/chapters/031-chapter-22-developer-testing.md` | Chapter 22: Developer Testing | Test-first/last trade-off, basis/data-flow/boundary/equivalence testing, good/bad data, error clustering, scaffolding, automation, coverage, and records. |
| `CC_ROOT/chapters/032-chapter-23-debugging.md` | Chapter 23: Debugging | Scientific hypothesis loop, stabilization, localization, root-cause repair, sibling search, psychological traps, warnings, tools, and regression protection. |
| `CC_ROOT/chapters/033-chapter-24-refactoring.md` | Chapter 24: Refactoring | Evolution pressures, smells as candidate signals, behavior preservation, reasons not to refactor, transformation catalog, small verified steps, and bad timing. |
| `CC_ROOT/chapters/034-chapter-25-code-tuning-strategies.md` | Chapter 25: Code-Tuning Strategies | Performance requirements, architecture/algorithm primacy, profiling, hotspots, baseline/measurement precision, iteration, and clean-code preservation. |
| `CC_ROOT/chapters/035-chapter-26-code-tuning-techniques.md` | Chapter 26: Code-Tuning Techniques | Logic/loop/data/expression/routine/low-level transformations; every result is environment-specific and requires measurement and semantic safeguards. |
| `CC_ROOT/chapters/036-part-vi-system-considerations.md` | Part VI: System Considerations | Part divider and navigation only. |
| `CC_ROOT/chapters/037-chapter-27-how-program-size-affects-construction.md` | Chapter 27: How Program Size Affects Construction | Communication paths, defect/productivity effects, activity mix, and process formality scaled to project size. |
| `CC_ROOT/chapters/038-chapter-28-managing-construction.md` | Chapter 28: Managing Construction | Standards calibration, configuration/change control, version/environment records, estimates, measurement, human variation, and authority/management context. |
| `CC_ROOT/chapters/039-chapter-29-integration.md` | Chapter 29: Integration | Incremental versus big-bang integration, risk/feature/top-down/bottom-up strategies, daily build/smoke test, and continuous integration. |
| `CC_ROOT/chapters/040-chapter-30-programming-tools.md` | Chapter 30: Programming Tools | Search/diff/analysis/refactoring/VCS/build/debug/test/profile/automation tools; tools amplify reasoning but do not replace it. |
| `CC_ROOT/chapters/041-part-vii-software-craftsmanship.md` | Part VII: Software Craftsmanship | Part divider and navigation only. |
| `CC_ROOT/chapters/042-chapter-31-layout-and-style.md` | Chapter 31: Layout and Style | Logical/consistent formatting, whitespace and block visibility, statement/comment/class/file organization, convention over aesthetic argument. |
| `CC_ROOT/chapters/043-chapter-32-self-documenting-code.md` | Chapter 32: Self-Documenting Code | Code structure as documentation, when comments add non-code information, intent/rationale/contract comments, maintenance proximity, and external documents. |
| `CC_ROOT/chapters/044-chapter-33-personal-character.md` | Chapter 33: Personal Character | Intellectual humility/honesty, curiosity, cooperation, discipline, habits, and willingness to seek evidence; conduct evidence is practitioner-oriented. |
| `CC_ROOT/chapters/045-chapter-34-themes-in-software-craftsmanship.md` | Chapter 34: Themes in Software Craftsmanship | Complexity, process selection, human readers, programming into languages, conventions, domain-level expression, warning signs, iteration, experimentation, and anti-dogmatism. |
| `CC_ROOT/chapters/046-chapter-35-where-to-find-more-information.md` | Chapter 35: Where to Find More Information | Reading plan, source categories, periodicals, and professional learning; dated bibliography routes, no independent implementation rule. |
| `CC_ROOT/chapters/047-bibliography.md` | Bibliography | Citation provenance and historical evidence routes; no independent doctrine. |
| `CC_ROOT/chapters/048-index.md` | Index | Retrieval aid and topic cross-check; no independent doctrine. |

### PP coverage (17/17 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `PP_ROOT/chapters/001-what-others-in-the-trenches-say-about-the-pragmatic-programmer.md` | Endorsements/title/copyright | Publication and first-edition/printing context; endorsements are not evidence. |
| `PP_ROOT/chapters/002-contents.md` | Contents | Navigation and topic cross-check; no independent doctrine. |
| `PP_ROOT/chapters/003-foreword.md` | Foreword | Practitioner framing and adaptability; largely rhetorical. |
| `PP_ROOT/chapters/004-preface.md` | Preface | Pattern-language format, context dependence, no universal best solution, intended audience and source limitations. |
| `PP_ROOT/chapters/005-acknowledgments.md` | Acknowledgments | Publication-only. |
| `PP_ROOT/chapters/006-chapter-1-a-pragmatic-philosophy.md` | Chapter 1: A Pragmatic Philosophy | Responsibility/authority, entropy, good-enough quality, stopping, learning, critical thinking, and audience-aware communication. |
| `PP_ROOT/chapters/007-chapter-2-a-pragmatic-approach.md` | Chapter 2: A Pragmatic Approach | DRY as knowledge authority, orthogonality, reversibility, tracer bullets, disposable prototypes, domain languages, and evidence-refined estimation. |
| `PP_ROOT/chapters/008-chapter-3-the-basic-tools.md` | Chapter 3: The Basic Tools | Plain-text longevity, shell/editor fluency, VCS, systematic debugging, text transformation, and active/passive generation. Tool specifics are dated. |
| `PP_ROOT/chapters/009-chapter-4-pragmatic-paranoia.md` | Chapter 4: Pragmatic Paranoia | Contracts, pre/postconditions/invariants, crash/fail early, assertions, exceptions versus normal flow, and resource ownership/balance. |
| `PP_ROOT/chapters/010-chapter-5-bend-or-break.md` | Chapter 5: Bend, or Break | Law of Demeter, coupling, metadata/configuration, temporal coupling/concurrency, pub-sub/MVC, blackboards, and costs of indirect control. |
| `PP_ROOT/chapters/011-chapter-6-while-you-are-coding.md` | Chapter 6: While You Are Coding | Deliberate programming, assumptions, algorithmic complexity, refactoring boundaries, contract tests, harnesses, observability, and tool-generated code caution. |
| `PP_ROOT/chapters/012-chapter-7-before-the-project.md` | Chapter 7: Before the Project | Discovering needs, policy versus implementation, glossary, scope control, readiness, specifications as abstractions, and formal-method limits. |
| `PP_ROOT/chapters/013-chapter-8-pragmatic-projects.md` | Chapter 8: Pragmatic Projects | Team conventions, automation, regression, multi-level/risk testing, test data and tests-of-tests, documentation authority, expectations, and shared ownership. |
| `PP_ROOT/chapters/014-appendix-a.md` | Appendix A | Resources, organizations, tools, periodicals, and reading routes; largely historically dated and not independent doctrine. |
| `PP_ROOT/chapters/015-bibliography.md` | Bibliography | Citation provenance; no independent doctrine. |
| `PP_ROOT/chapters/016-appendix-b.md` | Appendix B | Exercise answers and worked examples reinforcing DRY, orthogonality, contracts, algorithms, refactoring, testing, and design trade-offs. |
| `PP_ROOT/chapters/017-index.md` | Index and quick-reference tips | Retrieval aid and compact claim cross-check; repeated tips do not add independent support. |

### APOSD coverage (32/32 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `APOSD_ROOT/chapters/001-cover-page.md` | Cover Page | Publication-only. |
| `APOSD_ROOT/chapters/002-title-page.md` | Title Page | Edition/title metadata; publication-only. |
| `APOSD_ROOT/chapters/003-copyright.md` | Copyright | Second-edition date and publication context; no doctrine. |
| `APOSD_ROOT/chapters/004-contents.md` | Contents | Navigation and chapter cross-check. |
| `APOSD_ROOT/chapters/005-preface.md` | Preface | Design philosophy scope, teaching/practitioner basis, and explicit non-exhaustiveness. |
| `APOSD_ROOT/chapters/006-1-introduction.md` | 1: Introduction | Complexity as central design problem, strategic investment, and iterative design framing. |
| `APOSD_ROOT/chapters/007-2-the-nature-of-complexity.md` | 2: The Nature of Complexity | Change amplification, cognitive load, unknown unknowns, dependency/obscurity causes, reader frequency weighting. |
| `APOSD_ROOT/chapters/008-3-working-code-isnt-enough.md` | 3: Working Code Isn’t Enough | Strategic versus tactical implementation, continuous design investment, and explicitly opinion-based payback estimates. |
| `APOSD_ROOT/chapters/009-4-modules-should-be-deep.md` | 4: Modules Should Be Deep | Interface cost versus hidden functionality, common-case simplicity, shallow-module warning, and examples/counterexamples. |
| `APOSD_ROOT/chapters/010-5-information-hiding-and-leakage.md` | 5: Information Hiding (and Leakage) | Hide design decisions, detect duplicated knowledge, avoid temporal decomposition, expose user-needed facts, and distinguish privacy from hiding. |
| `APOSD_ROOT/chapters/011-6-general-purpose-modules-are-deeper.md` | 6: General-Purpose Modules are Deeper | Current-needs generality, clean mechanisms, specialized layers, simpler APIs, and overgeneralization constraints. |
| `APOSD_ROOT/chapters/012-7-different-layer-different-abstraction.md` | 7: Different Layer, Different Abstraction | Pass-through warning, dispatcher/implementation/adapter exceptions, decorator and configuration costs, context-object trade-offs. |
| `APOSD_ROOT/chapters/013-8-pull-complexity-downwards.md` | 8: Pull Complexity Downwards | Let modules absorb related complexity to simplify callers; avoid pulling unrelated policy into a module. |
| `APOSD_ROOT/chapters/014-9-better-together-or-better-apart.md` | 9: Better Together Or Better Apart? | Shared knowledge/use/concept criteria, interface and duplication costs, clean subtask extraction, method-length disagreement. |
| `APOSD_ROOT/chapters/015-10-define-errors-out-of-existence.md` | 10: Define Errors Out Of Existence | Reduce exception sites by semantics, masking, aggregation, or crash in bounded contexts; preserve meaningful environmental/durability failures. |
| `APOSD_ROOT/chapters/016-11-design-it-twice.md` | 11: Design it Twice | Generate substantially different designs; compare caller ease, interface, generality, performance, and implementation cost. |
| `APOSD_ROOT/chapters/017-12-why-write-comments-the-four-excuses.md` | 12: Why Write Comments? The Four Excuses | Comments as design/abstraction information, critique of comments-as-failure, and rebuttals to common objections. |
| `APOSD_ROOT/chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md` | 13: Comments Should Describe Things that Aren’t Obvious from the Code | Informal contracts, rationale, invariants, ownership, units, side effects, higher/lower-level commentary, and cross-module design records. |
| `APOSD_ROOT/chapters/019-14-choosing-names.md` | 14: Choosing Names | Precise mental images, semantic consistency, scope, typed/domain distinctions, hard-to-name design signal, and Go-style naming tension. |
| `APOSD_ROOT/chapters/020-15-write-the-comments-first.md` | 15: Write The Comments First | Interface/implementation comments as a pre-code design probe; contextual practice, not an invariant workflow. |
| `APOSD_ROOT/chapters/021-16-modifying-existing-code.md` | 16: Modifying Existing Code | Strategic improvement while changing, preserving design quality, resisting tactical patches, and bounding cleanups. |
| `APOSD_ROOT/chapters/022-17-consistency.md` | 17: Consistency | Cognitive leverage from conventions, documentation/automation/review, repository conformity, and thresholds for changing convention. |
| `APOSD_ROOT/chapters/023-18-code-should-be-obvious.md` | 18: Code Should be Obvious | Reader-tested obviousness, event invocation context, semantic containers, whitespace/comments/names, and reading-over-writing priority. |
| `APOSD_ROOT/chapters/024-19-software-trends.md` | 19: Software Trends | Interface versus implementation inheritance, composition, agile/TDD tensions, pattern restraint, and accessor skepticism. |
| `APOSD_ROOT/chapters/025-20-designing-for-performance.md` | 20: Designing for Performance | Naturally efficient design, baseline/profiling/microbenchmarks, algorithm/architecture first, critical-path isolation, and remove unproven optimizations. |
| `APOSD_ROOT/chapters/026-21-decide-what-matters.md` | 21: Decide What Matters | Identify externally important constraints, minimize important concepts/locations, expose what matters and hide the rest. |
| `APOSD_ROOT/chapters/027-22-conclusion.md` | 22: Conclusion | Consolidated design principles and red flags; summary does not add independent support. |
| `APOSD_ROOT/chapters/028-index.md` | Index | Retrieval aid only. |
| `APOSD_ROOT/chapters/029-summary-of-design-principles.md` | Summary of Design Principles | Canonical author summary and cross-check; repetitions do not add independent evidence. |
| `APOSD_ROOT/chapters/030-summary-of-red-flags.md` | Summary of Red Flags | Author's diagnostic signals; signals are hypotheses, not automatic verdicts. |
| `APOSD_ROOT/chapters/031-about-the-author.md` | About the Author | Author/research/teaching context and potential source bias. |
| `APOSD_ROOT/chapters/032-back-cover.md` | Back Cover | Promotional synopsis and endorsements; not evidence. |

## Per-source corpus map

### CC — Code Complete, Second Edition

- **Primary domain:** construction craft: detailed design, implementation, developer testing, debugging, refactoring, tuning, integration, and the management practices immediately surrounding them.
- **Strongest contributions:** a broad operational inventory of construction decisions; complexity and human comprehension as unifying concerns; explicit upstream readiness checks; class/routine/data/control-flow techniques; defensive-programming and testing checklists; systematic debugging; measurement-before-tuning; proportionate process and convention selection; repeated anti-dogmatism.
- **Contextual assumptions:** mostly imperative and object-oriented commercial software; many examples in C++, Java, Visual Basic, Ada, and C; a team can establish project conventions; source is often statically typed; construction has recognizable requirements and architectural inputs. It acknowledges iterative, small-project, early-wave, and safety-critical differences.
- **Limitations and dating:** published in 2004. Language popularity, numeric operation costs, compiler behavior, tool capability, hardware, framework names, code layout practice, and some empirical studies are dated. Several numerical thresholds—seven parameters, 100–200-line routines, defect percentages, cost multipliers—are useful prompts but not repository-independent limits. Examples sometimes overfavor class/inheritance refactorings by modern standards. Construction focus does not establish product, security, operations, or architecture authority.
- **Known tensions:** CC strongly encourages extracting even very small operations when they create an understandable abstraction, but also rejects smallness as a goal and rejects fixed routine-length limits. Its broad “duplicate code implies decomposition error” phrasing conflicts with APOSD's interface-cost warning and must be narrowed to duplicated knowledge/change coupling. Its guidance to anticipate likely change is more speculative than APOSD's current-needs generality. Its “code is always current” observation conflicts with runtime behavior, generated sources, data, and external contracts as possible authorities.
- **Likely agent roles:** coding agents, implementation planners, debugging/repair agents, review agents, refactoring agents, performance agents, test agents, repository-assessment agents.
- **Concepts worth mining:** implementation readiness, complexity budget, local reasoning, information hiding, routine/class cohesion, explicit contracts, defensive boundary, naming as design, data lifetime, control-flow obviousness, complementary defect detection, scientific debugging, incremental integration, measured tuning, proportionate process.
- **Representative locators:** `CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### cc2e.com/0386 Checklist: Upstream Prerequisites`; `CC: chapters/011-chapter-5-design-in-construction.md :: #### Software's Primary Technical Imperative: Managing Complexity`; `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.4 How Long Can a Routine Be?`; `CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.3 Error-Handling Techniques`; `CC: chapters/031-chapter-22-developer-testing.md :: #### 22.3 Bag of Testing Tricks`; `CC: chapters/032-chapter-23-debugging.md :: #### The Scientific Method of Debugging`; `CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.4 Measurement`; `CC: chapters/045-chapter-34-themes-in-software-craftsmanship.md :: #### 34.9 Thou Shalt Rend Software and Religion Asunder`.

### PP — The Pragmatic Programmer

- **Primary domain:** adaptable practitioner conduct and cross-cutting implementation practices, spanning knowledge ownership, coupling, tools, contracts, debugging, testing, requirements, automation, and team delivery.
- **Strongest contributions:** DRY as a rule about authoritative knowledge rather than visual repetition; orthogonality as change locality; explicit responsibility and communication; prototype versus retained tracer-code distinction; contract/invariant thinking; resource ownership; systematic debugging; deliberate programming; testability/observability; automation; requirements as discovered needs rather than dictated implementation.
- **Contextual assumptions:** capable developers have substantial latitude over tools, practices, and design; many examples assume late-1990s C/C++/Java, Unix, client-server, CORBA, and enterprise systems; principles are intentionally presented as context-sensitive tips rather than a closed method.
- **Limitations and dating:** original first edition, copyright 1999/2000 with a 2010 printing in this corpus. Tool commands, VCS products, CORBA/EJB examples, GUI/MVC specifics, language exception behavior, code-generation technology, and concurrency deployment examples are dated. “Always design for concurrency,” dynamic-agent contracts, “broken windows,” and aggressive metadata claims are advocacy, not universal evidence. Strong refactor-sooner rhetoric needs repository pressure, protection, scope, and authority gates.
- **Known tensions:** Law of Demeter can create pass-through wrappers that APOSD identifies as shallow-module costs. PP's configurable metadata emphasis conflicts with pulling complexity into modules and treating configuration as a public interface. Its exceptions-for-unexpected-events distinction differs from APOSD's reduce/define-away error strategy. DRY is often misread more broadly than PP states. PP supports tests as design feedback, while APOSD warns that feature-by-feature TDD can lock in tactical structure.
- **Likely agent roles:** coding agents, repair/debugging agents, test agents, review agents, implementation planners, legacy agents, delivery/automation agents, and agents assessing authority or uncertainty.
- **Concepts worth mining:** knowledge authority, change locality, reversible choices, tracer bullet, disposable prototype, explicit contract, invariant, resource ownership, deliberate implementation, scientific debugging, test surface, automation, good-enough stopping rule, expectation management.
- **Representative locators:** `PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Take Responsibility`; `PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Know When to Stop`; `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication`; `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Tracer Bullets Don't Always Hit Their Target`; `PP: chapters/008-chapter-3-the-basic-tools.md :: ### Debugging Strategies`; `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>21</sup>** Design by Contract`; `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>25</sup>** How to Balance Resources`; `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### How to Program Deliberately`; `PP: chapters/013-chapter-8-pragmatic-projects.md :: ## **<sup>43</sup>** Ruthless Testing`.

### APOSD — A Philosophy of Software Design, Second Edition

- **Primary domain:** reducing software complexity through deep modules, information hiding, strategic design, simple interfaces, explicit non-obvious knowledge, and reader-centered implementation.
- **Strongest contributions:** an operational complexity model—change amplification, cognitive load, and unknown unknowns caused by dependencies and obscurity; module depth as interface cost versus hidden benefit; information leakage diagnostics; current-needs generality; different-layer/different-abstraction tests; explicit criteria for keeping code together or apart; error-site reduction; design-alternative comparison; comments as informal contracts; repository consistency; reader feedback; performance design grounded in measurement.
- **Contextual assumptions:** modular systems where interface and implementation can be distinguished; long-lived code and changeability matter; teams can review designs and comments; examples are mainly Java/C++/Tcl and systems/infrastructure code, with some Go discussion. Much support comes from teaching and projects rather than comparative experiments.
- **Limitations and dating:** second edition dated 2021, but examples span earlier projects. The suggested strategic-investment percentage/payback period is expressly opinion without empirical support. “Deepness” has no universal scalar and can conceal cohesion, operational visibility, security, or policy if applied mechanically. Defining errors away is unsafe when callers need failure information. Comments-first is an optional design technique, not a universal workflow. Hardware-operation cost examples drift.
- **Known tensions:** directly challenges rigid “small methods/classes” doctrine and comments-as-failure doctrine. It is less aggressive than PP/CC about extracting repeated short code and more skeptical of decorators/pass-through layers, configuration, TDD-led design, and implementation inheritance. Its “somewhat general-purpose” recommendation can sound like speculative generality, but the source bounds it to current requirements and simpler interfaces. Pulling complexity downward conflicts with separation when complexity belongs to caller policy or operational authority.
- **Likely agent roles:** coding agents, API/design-review agents, architecture agents at module scale, refactoring agents, performance agents, maintainability assessors, and reviewers of comments/names/interfaces.
- **Concepts worth mining:** change amplification, cognitive load, unknown unknowns, deep module, interface burden, information leakage, semantic cohesion, caller simplification, representational integrity, obviousness, design twice, strategic programming, error-surface reduction, consistency leverage, measured critical path.
- **Representative locators:** `APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity`; `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`; `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`; `APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?`; `APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence`; `APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code`; `APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance`.

## Source-role classification

| Source | Source roles | Appropriate doctrinal weight |
|---|---|---|
| CC | Implementation craft; construction planning; detailed design; defensive coding; developer testing; debugging; refactoring mechanics; performance tactics; integration and team construction | Strong for decision inventories, local implementation procedure, testing/debugging flow, and measurement gates; contextual for numerical thresholds, language-era technique, class/inheritance preferences, and management statistics. |
| PP | Universal engineering foundation; implementation craft; safe change; debugging; testability; requirements interpretation; automation/team conduct | Strong for responsibility, knowledge authority, explicit contracts, resource ownership, hypothesis-driven debugging, automation, and prototype/tracer distinctions; contextual for Law of Demeter, metadata, concurrency universality, exception doctrine, and broken-window rhetoric. |
| APOSD | Universal complexity foundation; module/API design; implementation craft; maintainability review; performance design; strategic refactoring | Strong for complexity symptoms/causes, interface-cost reasoning, information hiding/leakage, reader-centered obviousness, and design alternatives; contextual for deepness, comments-first, error elimination, TDD criticism, and claimed investment payback. |

## Conversion and evidence caveats

- CC and PP were converted from PDFs by Marker. CC preserves 467 probable unresolved tables and 11 duplicate-heading patterns; PP preserves 117 unresolved tables and 27 duplicate-heading patterns. Both have one conservatively inferred chapter boundary and no reliable fenced-code language identifiers. Table-aligned numbers and code formatting must be checked against source context before reuse.
- APOSD was converted from EPUB by Pandoc. It has two unresolved tables, one unrestored navigation anchor, and 65 internal links redirected to chapter anchors. Its section headings were flattened; precise locators therefore stop at the chapter H1.
- OCR artifacts include split words, malformed emphasis, merged headings, and code listings rendered partly as prose. Claims here rely on surrounding prose and author summaries, not on silently reconstructed code.
- Indexes, contents, endorsements, acknowledgments, bibliographies, exercise answers, summary lists, and publication files were inspected and classified. Repetition in an index or summary is not counted as independent source support.
- CC cites empirical studies, but many are decades old and tied to languages, processes, and definitions that do not map cleanly to a current repository. Their direction can generate a hypothesis; their exact values cannot establish a current threshold.
- All three books blend evidence, practitioner experience, anecdote, and advocacy. Cross-source recurrence raises confidence only where operational decision rules also align. Repository tests, accepted decisions, runtime evidence, language behavior, user requirements, and granted authority remain superior evidence.
- No source independently authorizes an agent to change behavior, architecture, public APIs, dependencies, deployment, or project conventions. Source advice can support observation, diagnosis, recommendation, or an in-scope implementation choice only after repository evidence and authority gates are satisfied.

### Claims deliberately not promoted as universal doctrine

| Source claim | Why it remains weak, dated, or contested | Safe doctrinal use |
|---|---|---|
| APOSD's suggested continuous design-investment percentage and six-to-eighteen-month payback | The source labels these figures as opinion and supplies no empirical basis. | Require sustained strategic investment proportional to current change pressure; do not prescribe a percentage or payback horizon. |
| PP's “always design for concurrency” rhetoric | Concurrency adds ordering, ownership, lifecycle, resource, and debugging costs; no universal workload driver is established. | Remove accidental temporal coupling where cheap, but require an actual concurrency driver before concurrent execution. |
| PP's broken-window causal metaphor | The cultural effect is plausible but not a reliable authorization or severity test for a particular code change. | Treat visible disorder as a smell that triggers investigation, then require concrete pressure, protection, and scope. |
| PP's broad metadata/configuration preference | Configuration can move complexity to every operator/caller and create an enduring public interface. | Externalize genuine policy/environment variation; derive or hide stable mechanism choices. |
| CC's exact defect, productivity, parameter-count, routine-length, and late-fix cost numbers | Studies use old languages, processes, definitions, and populations; conversion also preserves unresolved tables. | Use the direction as a hypothesis and the values as historical context, never as a current repository threshold. |
| CC's dated language, framework, compiler, hardware, and tool comparisons | The examples describe the 2004 technology wave and can be wrong for current runtimes. | Retain the meta-rule: verify language/runtime/tool behavior and adapt construction practice to current maturity. |
| APOSD's broad criticism of TDD | Outcomes depend on test level, design practice, and team skill; CC and PP present contextual benefits. | Require a failing regression before repair; for new shared abstractions, compare designs before allowing individual tests to dictate structure. |
| APOSD's preference for defining errors away | Total/idempotent semantics can simplify APIs, but failure information is necessary for many user, network, security, and durability decisions. | Define away only when semantics are natural, recovery is reliable, and no caller-relevant information is lost. |


## Candidate canonical doctrine records

These are synthesis candidates organized by engineering decision, not by source. IDs are stable within this extraction. `source_support` lists exact source locators, not merely book names. Routing fields are included where this lane provides useful selectivity.

### U-IMPL-001 — Establish evidence and authority before intervention

```yaml
id: U-IMPL-001
title: Establish evidence and authority before intervention
category: universal
claim: An implementation choice is justified only by the accepted requirement, repository and runtime evidence, language behavior, risk constraints, and granted authority that bear on that choice; generic craft advice cannot create a requirement.
decision_rule: Separate observed facts, inferred causes, candidate recommendations, authorized decisions, and executed changes. Act only when the requested task grants the relevant decision level and the evidence resolves preservation and risk questions; otherwise report or propose.
why_it_matters: Responsibility includes declining or renegotiating unsupported work, and construction readiness depends on knowing the problem, constraints, quality goals, and architecture that implementation must honor.
applicable_when: [all engineering-agent work]
not_applicable_when: []
required_evidence: [user request or accepted work item, repository contracts and conventions, relevant source and tests, applicable runtime or operational constraints, explicit authority for semantic or structural scope]
insufficient_evidence: [a book's preference, aesthetic discomfort, a directory name, an isolated code smell, an unverified assumption about language or runtime behavior]
required_inputs: [task purpose, authority boundary, repository state, preservation boundary, unresolved uncertainties]
expected_outputs: [fact/inference/recommendation/decision labels, in-scope action or escalation, cited repository evidence]
preservation_boundaries: [accepted behavior, public and operational contracts, data and resource integrity, repository conventions unless migration is authorized]
safe_actions: [read, search, reproduce, inspect history and tests, make reversible in-scope changes, state uncertainty]
unsafe_actions: [silently redefine architecture, expand a repair into cleanup, convert preference into acceptance criterion, claim authorization not granted]
common_failure_modes: [solution-first coding, treating generic doctrine as repository law, silent scope expansion, hiding uncertainty]
counterexamples: [a user explicitly authorizes a bounded exploratory prototype; it may trade production constraints for learning if clearly disposable]
interactions: [U-IMPL-002, IMPL-003, IMPL-014, REPAIR-001]
conflicts: []
source_support:
  - "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Take Responsibility"
  - "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Involve Your Users in the Trade-Off"
  - "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### cc2e.com/0386 Checklist: Upstream Prerequisites"
  - "CC: chapters/009-chapter-4-key-construction-decisions.md :: #### cc2e.com/0496 Checklist: Major Construction Practices Coding"
confidence: strong
roles: [coding-agent, architecture-agent, refactoring-agent, legacy-agent, repair-agent, review-agent, performance-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [authority, evidence, prerequisites, scope, uncertainty, repository contract]
activate_for_roles: [all-engineering-agents]
activate_for_tasks: [planning, implementation, diagnosis, review, change]
activate_for_repository_signals: [missing requirement, unclear ownership, accepted ADR, project convention, high-risk boundary]
activate_for_risk_classes: [all]
exclude_when: []
prerequisites: []
retrieval_priority: core
retrieval_budget_hint: small
related_concepts: [U-IMPL-002, AGENT-IMPL-001]
```

### U-IMPL-002 — Minimize simultaneous uncertainty

```yaml
id: U-IMPL-002
title: Minimize simultaneous uncertainty
category: universal
claim: Organize work so that one uncertain behavior, dependency, design choice, or performance hypothesis is tested at a time, and preserve a fast feedback path.
decision_rule: Identify the highest-consequence unresolved assumption; obtain the cheapest discriminating evidence by a search, experiment, prototype, characterization test, trace, benchmark, or review; update the plan before broad implementation.
why_it_matters: Design is heuristic and incomplete, defects are easier to locate in small increments, and uncertainty compounds when requirements, architecture, semantics, and optimization change together.
applicable_when: [unfamiliar code, novel dependencies, poorly characterized behavior, algorithm or performance uncertainty, integration work]
not_applicable_when: [fully mechanical changes whose behavior and verification are established]
required_evidence: [enumerated assumptions, consequence/likelihood, discriminating check, baseline or observation]
insufficient_evidence: [confidence, precedent from another repository, a large implementation that happens to compile]
required_inputs: [unknowns, risk ranking, available probes, stop conditions]
expected_outputs: [resolved or narrowed assumption, retained/discarded prototype, updated implementation plan]
preservation_boundaries: [do not let experiments alter production data or accepted behavior unless authorized]
safe_actions: [throwaway prototype, tracer slice with production quality, targeted logging, one-change-at-a-time debugging]
unsafe_actions: [retain prototype code without review, batch unrelated hypotheses, infer causation from a coincident change]
common_failure_modes: [prototype laundering, broad speculative edits, changing test and implementation until both pass, premature architecture]
counterexamples: [a tracer bullet is deliberately retained, but unlike a prototype it must meet production quality and evolve through feedback]
interactions: [IMPL-014, REPAIR-001, PERF-IMPL-001]
conflicts: []
source_support:
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Design Is a Heuristic Process"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Experimental Prototyping"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Tracer Bullets Don't Always Hit Their Target"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### How Not to Use Prototypes"
  - "CC: chapters/032-chapter-23-debugging.md :: #### The Scientific Method of Debugging"
confidence: strong
roles: [coding-agent, repair-agent, legacy-agent, architecture-agent, performance-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [uncertainty, prototype, tracer bullet, experiment, hypothesis, incremental]
activate_for_tasks: [planning, unfamiliar implementation, debugging, integration, performance]
activate_for_risk_classes: [medium, high]
retrieval_priority: core
retrieval_budget_hint: small
related_concepts: [IMPL-014, REPAIR-001]
```

### IMPL-001 — Require construction readiness proportional to risk

```yaml
id: IMPL-001
title: Require construction readiness proportional to risk
category: implementation
claim: Before coding, establish enough problem, contract, architectural, test, error, security, resource, and integration context to avoid guessing; the required formality increases with consequence, novelty, scale, lifetime, and team coordination.
decision_rule: If the agent cannot state the intended observable outcome, affected contract, placement constraints, error/resource policy, verification method, and integration path, pause implementation and obtain the missing evidence. Do not demand exhaustive up-front design where a reversible low-risk slice can answer the question.
why_it_matters: Missing prerequisites turn design uncertainty into costly code and hide unauthorized behavior choices.
applicable_when: [feature implementation, behavior change, new dependency, public API work, durable or safety-sensitive code]
not_applicable_when: [bounded investigation or explicitly disposable prototype]
required_evidence: [problem statement, functional and quality requirements, accepted architecture or local placement conventions, relevant existing behavior, test strategy, risk class]
insufficient_evidence: [ticket title alone, similar code in another product, presumed user intent]
required_inputs: [task, repository signals, risk, language/runtime, authority]
expected_outputs: [readiness decision, explicit gaps, bounded plan, verification gates]
preservation_boundaries: [existing behavior not authorized to change, public/API/data/operational compatibility]
safe_actions: [clarify requirements, inspect analogous paths, choose a thin end-to-end slice, document assumptions]
unsafe_actions: [invent business rules, select architecture by habit, begin a broad implementation with no verification route]
common_failure_modes: [analysis paralysis, no design at all, polishing documents instead of exploring alternatives, treating an iterative process as no-prerequisites]
counterexamples: [short-lived internal script with obvious inputs/outputs can use a lightweight readiness check]
interactions: [IMPL-002, IMPL-003, IMPL-009, IMPL-014]
conflicts: [CONFLICT-007]
source_support:
  - "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### 3.1 Importance of Prerequisites"
  - "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Iterative Approaches' Effect on Prerequisites"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### How Much Design Is Enough?"
  - "PP: chapters/012-chapter-7-before-the-project.md :: ## **<sup>36</sup>** The Requirements Pit"
confidence: strong
roles: [coding-agent, implementation-agent, review-agent]
languages: [language-independent]
repository_archetypes: [library, service, cli, embedded, monolith, distributed-system]
retrieval_terms: [implementation readiness, prerequisites, requirements, plan, risk, test strategy]
activate_for_tasks: [feature implementation, public API, behavior change, dependency introduction]
activate_for_repository_signals: [missing tests, unclear architecture, cross-module change, high consequence]
activate_for_risk_classes: [all]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [U-IMPL-001, IMPL-002, IMPL-014]
```

### IMPL-002 — Place behavior with the knowledge and invariants it needs

```yaml
id: IMPL-002
title: Place behavior with the knowledge and invariants it needs
category: implementation
claim: New behavior belongs in the smallest existing module that owns the relevant state, policy, invariant, or hidden design decision and can expose it through a coherent interface without importing unrelated concerns.
decision_rule: Trace the behavior's inputs, owned data, invariants, side effects, error policy, and likely callers. Prefer the owner that can implement it without duplicating knowledge or exposing representation. Create a new owner only when no existing module has semantic ownership and the candidate forms a coherent, useful abstraction.
why_it_matters: Placement determines change locality, knowledge duplication, caller complexity, and whether future readers can reason locally.
applicable_when: [new behavior, bug repair placement, helper extraction, module/class selection]
not_applicable_when: [generated or vendored code, unless changing its generator or adapter is in scope]
required_evidence: [data/authority ownership, existing interfaces and call graph, invariants, co-change or repeated caller needs, repository architecture]
insufficient_evidence: [directory names alone, file size, desire for diagram symmetry, a generic layered-architecture preference]
required_inputs: [behavior contract, dependencies, owners, callers, repository conventions]
expected_outputs: [placement decision and rationale, interface impact, preservation boundary]
preservation_boundaries: [ownership, transaction/resource lifetime, public contract, dependency direction accepted by repository]
safe_actions: [extend a coherent owner, add a private helper, introduce a bounded adapter at an external boundary]
unsafe_actions: [put policy in a utility grab-bag, copy knowledge across modules, move behavior solely to make a file smaller]
common_failure_modes: [temporal decomposition, feature envy without ownership analysis, context-object grab-bag, technical-layer placement of domain policy]
counterexamples: [a dispatcher may legitimately route behavior while owning no domain state; an adapter may translate an external interface]
interactions: [IMPL-004, IMPL-005, IMPL-006, IMPL-008]
conflicts: [CONFLICT-003, CONFLICT-006]
source_support:
  - "APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)"
  - "APOSD: chapters/013-8-pull-complexity-downwards.md :: # 8: Pull Complexity Downwards"
  - "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Assign Responsibilities"
  - "CC: chapters/012-chapter-6-working-classes.md :: #### Good Abstraction"
confidence: strong
roles: [coding-agent, architecture-agent, review-agent, refactoring-agent]
languages: [language-independent]
repository_archetypes: [all-non-generated]
retrieval_terms: [placement, ownership, responsibility, behavior location, invariants, data owner]
activate_for_tasks: [implement behavior, move code, design module, review placement]
activate_for_repository_signals: [duplicated rule, cross-module state access, utility module, pass-through layer]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-004, IMPL-005]
```

### IMPL-003 — Design alternatives before committing an expensive interface

```yaml
id: IMPL-003
title: Design alternatives before committing an expensive interface
category: implementation
claim: For consequential or hard-to-reverse implementation choices, compare at least two materially different designs before selecting one; trivial local choices do not require ceremony.
decision_rule: Sketch alternative interfaces and responsibility allocations, not cosmetic variations. Compare caller burden, hidden complexity, information leakage, error/resource semantics, change amplification, testability, performance constraints, and reversal cost. Select the least complex option that satisfies current evidence and record rejected trade-offs proportionally.
why_it_matters: First ideas anchor thinking; interface and ownership mistakes propagate to many callers and are expensive to reverse.
applicable_when: [public API, shared module, persistence format, concurrency model, new abstraction, high-risk algorithm]
not_applicable_when: [mechanical private edit with an obvious repository precedent]
required_evidence: [current requirements, likely callers, constraints, alternative sketches, comparison criteria]
insufficient_evidence: [one completed design plus a token rename, source prestige, hypothetical future requirements]
required_inputs: [drivers, repository constraints, risk/reversibility, candidate designs]
expected_outputs: [selected alternative, trade-off note, validation plan]
preservation_boundaries: [accepted architecture and behavior; design exploration itself grants no authority to change them]
safe_actions: [pseudocode, interface sketches, throwaway experiment, review with maintainers]
unsafe_actions: [build all alternatives fully, overdesign low-risk code, choose by aesthetic symmetry]
common_failure_modes: [cosmetic alternatives, analysis paralysis, ignoring callers, documenting only the winner]
counterexamples: [a one-line fix following a well-established local pattern normally needs no alternative design exercise]
interactions: [IMPL-001, IMPL-004, IMPL-009, PERF-IMPL-001]
conflicts: [CONFLICT-007]
source_support:
  - "APOSD: chapters/016-11-design-it-twice.md :: # 11: Design it Twice"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Iterate"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Top-Down and Bottom-Up Design Approaches"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Reversibility"
confidence: strong
roles: [coding-agent, architecture-agent, review-agent]
languages: [language-independent]
repository_archetypes: [library, service, embedded, distributed-system, long-lived-product]
retrieval_terms: [design twice, alternatives, interface, reversibility, tradeoff]
activate_for_tasks: [API design, shared abstraction, irreversible choice, high-risk feature]
activate_for_risk_classes: [medium, high]
retrieval_priority: high
retrieval_budget_hint: medium
related_concepts: [IMPL-004, IMPL-009]
```

### IMPL-004 — Earn an abstraction by reducing total cognitive and change cost

```yaml
id: IMPL-004
title: Earn an abstraction by reducing total cognitive and change cost
category: implementation
claim: Introduce or retain an abstraction only when it hides nontrivial knowledge or mechanism behind a coherent interface and reduces total caller complexity, coordinated change, or substitution cost more than the interface and indirection add.
decision_rule: Identify the knowledge hidden, current consumers, independent variation, and predicted coordinated changes. Compare direct code against the abstraction including interface concepts, navigation, error semantics, testing, and operational visibility. Reject abstractions justified only by line count, symmetry, a single hypothetical variation, or superficial similarity.
why_it_matters: Abstraction can create local reasoning and single knowledge authority, but shallow abstractions add interfaces without hiding complexity.
applicable_when: [helper/module/interface/base-class/design-pattern proposal, duplicated knowledge, multiple implementations]
not_applicable_when: [generated repetition managed by one generator; deliberately duplicated stable code with different semantic ownership]
required_evidence: [coherent concept, hidden decision/mechanism, current callers or demonstrated variation, change/reader cost comparison, simple contract]
insufficient_evidence: [two similar snippets, large file, mocking convenience alone when repository uses concrete fakes, desire for extensibility with no variation]
required_inputs: [candidate occurrences, semantic ownership, change history if available, interface sketch]
expected_outputs: [extract/retain-duplication decision, abstraction boundary, contract and migration scope]
preservation_boundaries: [behavior and error/resource semantics; do not combine extraction with behavior repair]
safe_actions: [private function with intention-revealing name, consumer-owned narrow interface, module hiding a volatile representation]
unsafe_actions: [generic framework before demonstrated use, type hierarchy to remove cosmetic duplication, pass-through wrapper with no policy or hiding]
common_failure_modes: [speculative generality, wrong commonality, abstraction inversion, parameter explosion, leaky interface, mock-driven public API]
counterexamples: [a dispatcher, external adapter, or multiple implementation boundary may be shallow in code size yet carry a distinct abstraction and dependency role]
interactions: [IMPL-005, IMPL-006, IMPL-007, IMPL-008]
conflicts: [CONFLICT-001, CONFLICT-002, CONFLICT-003, CONFLICT-004]
source_support:
  - "APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep"
  - "APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)"
  - "APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication"
confidence: strong
roles: [coding-agent, architecture-agent, refactoring-agent, review-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [earned abstraction, interface, helper, indirection, deep module, speculative generality]
activate_for_tasks: [extract abstraction, add interface, design module, remove duplication, review design]
activate_for_repository_signals: [pass-through method, shallow wrapper, duplicated rule, multiple implementations, parameter explosion]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-005, IMPL-007]
```

### IMPL-005 — Prefer deep modules, but measure depth by leverage rather than size

```yaml
id: IMPL-005
title: Prefer interface leverage over arbitrary module size
category: implementation
claim: A useful module exposes a small, comprehensible common-case contract while hiding substantial coherent complexity; neither short code nor long code is inherently deep, cohesive, or maintainable.
decision_rule: Evaluate the number and difficulty of interface concepts against useful behavior hidden, caller simplification, cohesion, variable/decision burden, error/resource semantics, and independent understandability. Split when a clean independent abstraction lowers total cognitive load; merge conjoined or pass-through fragments when doing so removes interfaces without mixing unrelated knowledge.
why_it_matters: Every routine/class/module interface is a cognitive and defect surface. Arbitrary size limits can multiply shallow interfaces or leave truly incohesive routines intact.
applicable_when: [large method/class/file review, helper proliferation, facade/decorator layers, module redesign]
not_applicable_when: [generated code; externally imposed interfaces that cannot be changed in scope]
required_evidence: [cohesion, callers, interface concepts, nesting/decision/data burden, independent change and comprehension, review feedback]
insufficient_evidence: [line count alone, method count, one-screen rule, “one thing” without defining the abstraction]
required_inputs: [module contract and implementation, call sites, change evidence, reader/reviewer feedback]
expected_outputs: [leave/split/merge/deepen decision with seam and contract]
preservation_boundaries: [behavior, API compatibility, error/resource order, performance if relevant]
safe_actions: [extract a named independent subtask, merge pass-through helpers, simplify common-case API, hide configuration defaults]
unsafe_actions: [split at arbitrary line intervals, conceal unrelated responsibilities behind a small facade, add wrappers solely to satisfy traversal rules]
common_failure_modes: [interface proliferation, god module, false depth through opacity, parameter/context grab-bags, aesthetic size enforcement]
counterexamples: [a tiny parsing or conversion function can be deep if its simple contract hides a tricky representation; a long linear algorithm can be cohesive and locally comprehensible]
interactions: [IMPL-002, IMPL-004, IMPL-006, IMPL-011]
conflicts: [CONFLICT-001, CONFLICT-003]
source_support:
  - "APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep"
  - "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.4 How Long Can a Routine Be?"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.2 Design at the Routine Level"
confidence: strong
roles: [coding-agent, refactoring-agent, review-agent, architecture-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [deep module, routine length, large method, small function, shallow class, split, merge]
activate_for_tasks: [review module, split file, extract method, merge helpers, API design]
activate_for_repository_signals: [large file, many tiny wrappers, pass-through methods, high interface count]
retrieval_priority: high
retrieval_budget_hint: medium
related_concepts: [IMPL-004, IMPL-006]
```

### IMPL-006 — Hide decisions, not merely fields

```yaml
id: IMPL-006
title: Hide decisions, not merely fields
category: implementation
claim: Information hiding succeeds when one module owns a design decision or representation and callers depend on its stable meaning rather than its mechanics; access modifiers alone do not establish hiding.
decision_rule: List facts a caller must know to use the module. Move internal representation, order, policy defaults, and mechanism knowledge behind the owner unless the caller genuinely needs them for correctness, durability, performance, security, or operation. Treat duplicated knowledge across modules as leakage.
why_it_matters: Leaked decisions amplify changes, expand the knowledge required for local work, and create unknown dependencies.
applicable_when: [module/API design, data representation, sequencing, configuration, refactoring]
not_applicable_when: [information is an explicit public/operational contract or must be exposed for caller policy]
required_evidence: [decision owner, caller needs, change coupling, interface semantics, operational requirements]
insufficient_evidence: [private fields, getters/setters, facade existence, directory boundary]
required_inputs: [call graph, representation, contracts, operational constraints]
expected_outputs: [hidden/exposed knowledge inventory, owner, interface change proposal]
preservation_boundaries: [facts users/operators need; observability; compatibility; data format]
safe_actions: [centralize format/order logic, expose semantic operation, derive defaults internally, document necessary external facts]
unsafe_actions: [hide meaningful failure or durability semantics, duplicate policy in callers, expose raw state through routine getters]
common_failure_modes: [privacy mistaken for hiding, temporal decomposition, configuration leakage, representation getters, false abstraction]
counterexamples: [a caller deciding a business policy must receive the relevant fact; a performance-sensitive API may expose layout deliberately with an explicit contract]
interactions: [IMPL-002, IMPL-004, IMPL-009, IMPL-011]
conflicts: [CONFLICT-005, CONFLICT-006]
source_support:
  - "APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Hide Secrets (Information Hiding)"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Living with Orthogonality"
confidence: strong
roles: [coding-agent, architecture-agent, review-agent, refactoring-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [information hiding, leakage, encapsulation, representation, change amplification]
activate_for_tasks: [API design, placement, refactoring, configuration, review]
activate_for_repository_signals: [duplicated knowledge, raw getters, caller sequencing, public fields]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-004, IMPL-009]
```

### IMPL-007 — Treat duplication as evidence about knowledge, not syntax

```yaml
id: IMPL-007
title: Treat duplication as evidence about knowledge, not syntax
category: implementation
claim: Duplication is harmful when multiple representations encode one authoritative rule or must change together; similar-looking code with independent ownership may be safer than a premature common abstraction.
decision_rule: Ask whether occurrences represent the same knowledge, have the same reasons to change, and have historically or logically required coordinated edits. Extract only when the shared concept has a coherent contract and the resulting interface does not add more coupling or caller complexity. If deliberately duplicated, record ownership and divergence expectations where non-obvious.
why_it_matters: Blind deduplication creates wrong commonality, while true duplicated knowledge causes inconsistent repairs and change amplification.
applicable_when: [duplicate-code finding, base-class/helper proposal, generated representations, caches]
not_applicable_when: [generated outputs whose single generator is authoritative; independent algorithms coincidentally alike]
required_evidence: [semantic equivalence, authority source, change reasons, co-change/history where available, abstraction contract]
insufficient_evidence: [token similarity, two occurrences, clone metric alone]
required_inputs: [occurrences, owners, requirements, change history, generator/cache semantics]
expected_outputs: [single-authority/extract/retain decision, consistency mechanism]
preservation_boundaries: [independent evolution, performance semantics, generated-file workflow, behavior]
safe_actions: [central rule, active generation, bounded shared helper, explicit cache invalidation]
unsafe_actions: [inheritance solely for reuse, generic abstraction before variation stabilizes, editing generated copies independently]
common_failure_modes: [wrong abstraction, coupled independent domains, scattered cache synchronization, copy-paste repair drift]
counterexamples: [a performance cache deliberately duplicates state but has one explicit update/invalidation authority; adapter code for distinct external contracts may remain duplicated]
interactions: [IMPL-004, IMPL-006, IMPL-008]
conflicts: [CONFLICT-002]
source_support:
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication"
  - "PP: chapters/008-chapter-3-the-basic-tools.md :: ### Active Code Generators"
  - "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine"
confidence: strong
roles: [coding-agent, refactoring-agent, review-agent, performance-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [duplication, DRY, clone, knowledge, generator, cache, premature abstraction]
activate_for_tasks: [evaluate duplication, extract helper, generate code, cache design]
activate_for_repository_signals: [similar snippets, duplicated rules, generated files, coordinated edits]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-004, IMPL-006]
```

### IMPL-008 — Generalize only across current, demonstrated needs

```yaml
id: IMPL-008
title: Generalize only across current demonstrated needs
category: implementation
claim: Prefer the simplest interface that handles current known uses without embedding one caller's incidental details; do not add hypothetical options, types, layers, or configuration merely to appear reusable.
decision_rule: Separate a stable mechanism from caller-specific policy only when at least one current caller boundary, repeated use, independently changing policy, or repository commitment demonstrates the distinction. Generalize the interface enough to make common current cases simple; defer imagined variation behind reversible implementation choices.
why_it_matters: Caller-bound modules leak details and duplicate mechanisms, but speculative generality burdens every caller and freezes false assumptions.
applicable_when: [shared helper, library API, reusable component, configuration or framework proposal]
not_applicable_when: [one-off local implementation with no reusable semantic concept]
required_evidence: [current use cases, common mechanism, caller-specific policy, likely change supported by repository evidence]
insufficient_evidence: [“might need later,” desire to publish a framework, parameterizing every constant]
required_inputs: [current callers, requirements, change evidence, API alternatives]
expected_outputs: [bounded general interface, specialization location, deferred choices]
preservation_boundaries: [common-case simplicity, no unsupported semantics, repository conventions]
safe_actions: [neutral representation, separate policy layer, internal default, minimal option set]
unsafe_actions: [generic framework from one example, force callers to reconstruct a simple operation, expose internal tuning knobs]
common_failure_modes: [speculative generality, lowest-common-denominator API, parameter soup, configuration sprawl, one-caller abstraction]
counterexamples: [an external library with an accepted compatibility mission may need deliberate extension points even before multiple in-repo callers; authority and published requirements must establish them]
interactions: [IMPL-004, IMPL-006, IMPL-009]
conflicts: [CONFLICT-004, CONFLICT-005]
source_support:
  - "APOSD: chapters/011-6-general-purpose-modules-are-deeper.md :: # 6: General-Purpose Modules are Deeper"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Reversibility"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Identify Areas Likely to Change"
confidence: contextual
roles: [coding-agent, architecture-agent, review-agent]
languages: [language-independent]
repository_archetypes: [library, service, long-lived-product]
retrieval_terms: [generality, reuse, YAGNI, extension point, mechanism policy, configuration]
activate_for_tasks: [design reusable API, add option, extract library, add configuration]
activate_for_repository_signals: [single-use generic type, option proliferation, repeated mechanism]
retrieval_priority: high
retrieval_budget_hint: medium
related_concepts: [IMPL-004, IMPL-009]
```

### IMPL-009 — Make APIs explicit about meaning, effects, and failure

```yaml
id: IMPL-009
title: Make APIs explicit about meaning, effects, and failure
category: implementation
claim: An API should present a coherent abstraction with intention-revealing names and the minimum concepts callers need, while making inputs, outputs, units, mutability, ownership, side effects, ordering, errors, and invariants discoverable and enforceable where possible.
decision_rule: Review the API from a caller's perspective. For every parameter/return/callback, identify semantic role, valid range/state, mutation, ownership/lifetime, failure modes, blocking/concurrency behavior, and compatibility promise. Remove unused/pass-through concepts, prefer types and language enforcement to prose, and document the informal contract that code cannot express.
why_it_matters: Interfaces are high-frequency cognitive and defect surfaces; ambiguity forces every caller to inspect implementation or guess.
applicable_when: [new or changed public/internal shared API, routine/class interface, callback, data structure]
not_applicable_when: [purely local expression with no stable caller boundary]
required_evidence: [callers and use cases, existing conventions, error/resource semantics, language capabilities, compatibility constraints]
insufficient_evidence: [implementation compiles, happy-path example only, familiar method name whose effects differ]
required_inputs: [interface, callers, contract, language/runtime, compatibility policy]
expected_outputs: [API assessment, explicit contract, tests/examples, blocker/suggestion classification]
preservation_boundaries: [behavior, binary/source/data compatibility as applicable, failure and ownership semantics]
safe_actions: [semantic types, precise names, immutable inputs, explicit result/error, consumer-defined small interface]
unsafe_actions: [boolean/control flags for unrelated operations, hidden side effects, expose representation for test convenience, swallow meaningful failure]
common_failure_modes: [wide interface, false abstraction, ambiguous null/zero, undocumented units, getter/setter leakage, accidental blocking]
counterexamples: [a language's idiomatic convention may encode an API property tersely; repository convention outranks a generic preference if the meaning remains clear]
interactions: [IMPL-006, IMPL-010, IMPL-011, IMPL-012, IMPL-013]
conflicts: [CONFLICT-008]
source_support:
  - "CC: chapters/012-chapter-6-working-classes.md :: ### 6.2 Good Class Interfaces"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.5 How to Use Routine Parameters"
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>21</sup>** Design by Contract"
  - "APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep"
  - "APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code"
confidence: strong
roles: [coding-agent, review-agent, architecture-agent]
languages: [language-independent]
repository_archetypes: [library, service, cli, embedded, monolith]
retrieval_terms: [API review, interface, parameters, side effects, ownership, errors, invariants]
activate_for_tasks: [design API, review interface, change public method, add callback]
activate_for_risk_classes: [all]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-011, IMPL-012, IMPL-013]
```

### IMPL-010 — Use names to expose semantic distinctions

```yaml
id: IMPL-010
title: Use names to expose semantic distinctions
category: implementation
claim: Names should let a repository reader distinguish the domain concept, role, unit, state, and effect relevant at that scope; naming difficulty is evidence to inspect the underlying design, not proof that a rename alone will fix it.
decision_rule: Start from repository and language conventions. Choose a precise domain image, consistent opposite/predicate vocabulary, and enough context for the name's scope. If a routine name must enumerate unrelated effects or a variable cannot be named without generic terms, re-examine cohesion and representation. Validate disputed names with maintainers/readers.
why_it_matters: Naming carries the abstraction into every use and can either remove or introduce obscurity.
applicable_when: [all handwritten identifiers, APIs, domain types, booleans, units]
not_applicable_when: [generated/vendored identifiers, protocol-mandated names, language idioms where context makes short names clear]
required_evidence: [repository convention, domain language, scope, reader feedback, actual role/effects]
insufficient_evidence: [personal style, character-count target, book-specific language convention]
required_inputs: [concept, scope, adjacent vocabulary, language norms]
expected_outputs: [name or design issue, consistency rationale]
preservation_boundaries: [public compatibility, serialization/reflection names, protocol contracts]
safe_actions: [precise predicate, semantic type, unit qualifier where type cannot encode it, consistent term]
unsafe_actions: [mass rename without authority, ambiguous abbreviations, type-only names, misleading effect name]
common_failure_modes: [synonyms for one concept, same word for distinct concepts, vague verbs, misleading temporary names, redundant type words]
counterexamples: [short Go receiver/loop names may be idiomatic and clear in tiny scopes; APOSD's preference for longer names does not override repository reader evidence]
interactions: [IMPL-002, IMPL-005, IMPL-009, IMPL-015]
conflicts: [CONFLICT-008]
source_support:
  - "APOSD: chapters/019-14-choosing-names.md :: # 14: Choosing Names"
  - "CC: chapters/018-chapter-11-the-power-of-variable-names.md :: #### The Most Important Naming Consideration"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.3 Good Routine Names"
  - "PP: chapters/012-chapter-7-before-the-project.md :: ### Maintain a Glossary"
confidence: strong
roles: [coding-agent, review-agent, refactoring-agent]
languages: [language-independent, Go-contextual]
repository_archetypes: [all]
retrieval_terms: [naming, vocabulary, boolean, domain language, hard to name, abbreviation]
activate_for_tasks: [implementation, API design, review, rename]
activate_for_repository_signals: [vague names, synonym drift, long effect name, unit confusion]
retrieval_priority: high
retrieval_budget_hint: small
related_concepts: [IMPL-009, IMPL-015]
```

### IMPL-011 — Make invariants and invalid states explicit

```yaml
id: IMPL-011
title: Make invariants and invalid states explicit
category: implementation
claim: Represent and enforce the conditions that must remain true across an operation or object lifecycle, using types, construction, contracts, assertions, validation, and tests at the boundary best able to own them.
decision_rule: Classify each condition as external input validity, public pre/postcondition, persistent/domain invariant, or internal programmer assumption. Validate external input with defined errors; make public contracts discoverable; establish valid objects at construction; assert impossible internal states without side effects; test boundary and transition cases.
why_it_matters: Implicit assumptions produce action at a distance and delayed corruption; explicit invariants constrain valid states and focus debugging and review.
applicable_when: [stateful object, domain rule, parser, resource lifecycle, concurrency, repair]
not_applicable_when: [a condition is merely a current implementation detail with no correctness consequence]
required_evidence: [accepted behavior/domain rule, valid/invalid states, transition points, caller responsibility, failure policy]
insufficient_evidence: [an assertion added because a value looked surprising, a comment without enforcement where enforcement is feasible]
required_inputs: [state model, boundaries, constructors/transitions, error policy]
expected_outputs: [invariant inventory, enforcement location, tests and failure behavior]
preservation_boundaries: [do not strengthen a public precondition or weaken a postcondition without semantic-change authority]
safe_actions: [validated constructor, semantic type, pre/postcondition test, side-effect-free assertion]
unsafe_actions: [assert normal user errors, rely on disabled assertions for safety, mutate inside an assertion, expose invalid intermediate state]
common_failure_modes: [two-phase initialization, ambiguous sentinel, contract weaker in substitute, validation duplicated inconsistently]
counterexamples: [at a trust boundary, redundant validation may be warranted even when an upstream contract exists]
interactions: [IMPL-009, IMPL-012, IMPL-013, IMPL-014]
conflicts: []
source_support:
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>21</sup>** Design by Contract"
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Other Uses of Invariants"
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>23</sup>** Assertive Programming"
  - "CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.2 Assertions"
  - "CC: chapters/012-chapter-6-working-classes.md :: #### Constructors"
confidence: strong
roles: [coding-agent, review-agent, repair-agent, legacy-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [invariant, contract, assertion, invalid state, precondition, postcondition]
activate_for_tasks: [implement state, API review, defect repair, characterization]
activate_for_repository_signals: [two-phase init, sentinel state, repeated validation, corruption]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-012, IMPL-014]
```

### IMPL-012 — Design error semantics as part of the interface

```yaml
id: IMPL-012
title: Design error semantics as part of the interface
category: implementation
claim: Errors should communicate caller-relevant failure without multiplying handling sites; define away, mask, aggregate, return, throw, retry, or terminate only according to the operation's semantics, recoverability, information needs, and consequence of continuation.
decision_rule: For each failure, ask whether the operation can have useful total/idempotent semantics, whether the module can recover reliably, whether the caller can make a meaningful decision, and whether continuation risks corruption or safety. Hide low-level failures only when recovery is reliable and preserves required information; expose meaningful user/environment/durability outcomes; fail fast on violated internal invariants when safe containment is possible.
why_it_matters: Both excessive exceptions and swallowed failures burden callers or destroy information. Error behavior is part of the API and system safety model.
applicable_when: [I/O, parsing, boundary validation, APIs, retries, background work, durable writes]
not_applicable_when: [no plausible failure beyond process termination, and repository contract explicitly treats it as fatal]
required_evidence: [failure modes, caller capabilities, recovery semantics, retry/idempotence, safety/durability requirements, repository error convention]
insufficient_evidence: [“exceptions are exceptional,” “crash early,” or “define errors away” as slogans]
required_inputs: [operation semantics, callers, trust boundary, consequence, language/runtime]
expected_outputs: [error taxonomy, propagation/recovery rule, logging/observability, tests]
preservation_boundaries: [diagnostic information, partial effects, durability guarantees, cleanup, compatibility]
safe_actions: [total semantics when natural, bounded retry, typed/sentinel result per repository idiom, aggregate high-level report, invariant crash in contained process]
unsafe_actions: [swallow data-loss or network failure, use exceptions as ordinary branching without repository convention, continue after possible corruption, leak low-level mechanism errors as public contract accidentally]
common_failure_modes: [handler proliferation, catch-all success, double reporting, partial commit, retry storm, ambiguous zero/null]
counterexamples: [deleting an absent item may naturally be idempotent; failing to persist acknowledged data cannot be defined away]
interactions: [IMPL-009, IMPL-011, IMPL-013, REPAIR-001]
conflicts: [CONFLICT-009]
source_support:
  - "APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence"
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>22</sup>** Dead Programs Tell No Lies"
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>24</sup>** When to Use Exceptions"
  - "CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.3 Error-Handling Techniques"
  - "CC: chapters/014-chapter-8-defensive-programming.md :: #### Robustness vs. Correctness"
confidence: strong
roles: [coding-agent, review-agent, repair-agent, architecture-agent]
languages: [language-independent]
repository_archetypes: [library, service, cli, embedded, distributed-system]
retrieval_terms: [error handling, exception, fail fast, define away, recovery, retry, durability]
activate_for_tasks: [API design, I/O, defect repair, resilience, review]
activate_for_risk_classes: [all]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-011, IMPL-013]
```

### IMPL-013 — Give every resource an explicit owner and release path

```yaml
id: IMPL-013
title: Give every resource an explicit owner and release path
category: implementation
claim: Every acquired resource and mutable shared asset needs an unambiguous owner responsible for release, balance, ordering, transfer, and failure cleanup.
decision_rule: At acquisition, identify owner, lifetime, transfer rules, release action, exceptional/early-return paths, and multi-resource ordering. Prefer language/runtime constructs that enforce lexical or object lifetime. Acquire shared resources in a consistent order where contention can deadlock; verify balance under failures.
why_it_matters: Leaks, double release, deadlock, and half-initialized state often arise when ownership is implicit across routines.
applicable_when: [files, locks, memory, transactions, sockets, goroutines/tasks, subscriptions, temporary files]
not_applicable_when: [immutable values with runtime-managed lifetime and no external resource]
required_evidence: [acquisition/release sites, lifecycle and transfer, failure paths, concurrency semantics]
insufficient_evidence: [garbage collection alone for external resources, happy-path close, comment saying caller owns without consistent API]
required_inputs: [resource graph, control flow, language features, failure policy]
expected_outputs: [ownership map, enforced cleanup, failure tests]
preservation_boundaries: [release ordering, transaction semantics, cancellation, error propagation]
safe_actions: [RAII/context manager/defer/finally according to language, reverse-order release, explicit transfer]
unsafe_actions: [hidden ownership transfer, release only on success, mixed lock ordering, finalizer-dependent correctness]
common_failure_modes: [leak, double close, deadlock, orphan task, transaction left open, cleanup masks primary error]
counterexamples: [process-lifetime singleton resources may intentionally have no routine-level release, but ownership and shutdown semantics still need an explicit decision]
interactions: [IMPL-009, IMPL-011, IMPL-012, IMPL-018]
conflicts: []
source_support:
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>25</sup>** How to Balance Resources"
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Nest Allocations"
  - "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Resource Management"
  - "CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.4 Exceptions"
confidence: strong
roles: [coding-agent, review-agent, repair-agent, performance-agent]
languages: [language-independent]
repository_archetypes: [service, cli, embedded, distributed-system, library]
retrieval_terms: [resource ownership, cleanup, lock order, lifetime, RAII, context manager, defer]
activate_for_tasks: [I/O, concurrency, transactions, lifecycle review, repair leak]
activate_for_repository_signals: [manual close, multiple returns, locks, goroutine/task, transaction]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-012, IMPL-018]
```

### IMPL-014 — Build protection from contract, boundaries, risks, and observed defects

```yaml
id: IMPL-014
title: Build protection from contract boundaries risks and observed defects
category: implementation
claim: Tests and characterization should protect observable contracts, invariants, boundary values, failure/resource paths, state combinations, and repaired regressions; line coverage alone cannot establish adequacy.
decision_rule: Derive tests from accepted behavior and risk. Cover nominal and invalid classes, equivalence partitions and boundaries, state transitions/data flow, failure cleanup, and each reproduced defect. Use the smallest test level that observes the contract without binding to irrelevant internals; add integration/system/performance checks where the contract crosses boundaries. Test the test when consequence warrants it.
why_it_matters: Different defect classes escape different methods; behavior-preserving work needs an executable preservation surface.
applicable_when: [new behavior, repair, refactoring, legacy change, optimization, integration]
not_applicable_when: [generated/vendored code protected at generator or adapter level, unless directly maintained]
required_evidence: [contract, risk and boundary inventory, current suite, defect/reproduction, observability]
insufficient_evidence: [coverage percentage, happy path, snapshot with no semantic oracle, mocks of implementation details]
required_inputs: [behavior, risks, seams, test infrastructure, authority]
expected_outputs: [test/characterization matrix, required level, oracle, gaps/uncertainty]
preservation_boundaries: [tests must not silently ratify known incorrect behavior as desired semantics; label characterization versus requirement tests]
safe_actions: [regression test before repair, boundary table, contract fake, deterministic generator, mutation check]
unsafe_actions: [change tests merely to accept implementation, expose internals publicly for testability, rely on manual ad-hoc test without recording]
common_failure_modes: [implementation-coupled test, flaky time/concurrency test, asserted mock choreography, untested cleanup, false confidence from coverage]
counterexamples: [a characterization test may intentionally record undocumented behavior without asserting it is correct; its purpose and uncertainty must be explicit]
interactions: [IMPL-001, IMPL-011, IMPL-012, REPAIR-001, PERF-IMPL-001]
conflicts: [CONFLICT-010]
source_support:
  - "CC: chapters/031-chapter-22-developer-testing.md :: #### 22.3 Bag of Testing Tricks"
  - "CC: chapters/031-chapter-22-developer-testing.md :: #### Boundary Analysis"
  - "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Testing Against Contract"
  - "PP: chapters/013-chapter-8-pragmatic-projects.md :: ### What to Test"
  - "PP: chapters/013-chapter-8-pragmatic-projects.md :: #### Testing the Tests"
  - "APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends"
confidence: strong
roles: [coding-agent, repair-agent, refactoring-agent, legacy-agent, review-agent, performance-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [tests, characterization, boundary, contract, regression, coverage, test the test]
activate_for_tasks: [implementation, repair, refactoring, legacy change, optimization]
activate_for_repository_signals: [weak tests, bug report, boundary behavior, flaky test]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [REPAIR-001, PERF-IMPL-001]
```

### IMPL-015 — Use comments for non-obvious contract and rationale

```yaml
id: IMPL-015
title: Use comments for non-obvious contract and rationale
category: implementation
claim: Code should express structure and mechanics, while comments and nearby design records preserve caller obligations, rationale, invariants, units, ownership, side effects, unusual constraints, and cross-module decisions that code cannot make obvious.
decision_rule: First improve misleading names, structure, types, and control flow. Then document information a reader needs but cannot reliably derive: interface semantics, why a non-obvious choice exists, what must remain true, what is intentionally not handled, and where a broader decision is recorded. Keep one authoritative explanation close to the governed code and update it with changes.
why_it_matters: Self-documenting structure cannot encode all informal contracts or reasons; redundant narration drifts and obscures important knowledge.
applicable_when: [public/shared interface, non-obvious algorithm, workaround, concurrency/resource contract, domain invariant, generated boundary]
not_applicable_when: [comment merely restates an obvious statement or stale history available in VCS]
required_evidence: [reader need, information not encoded by code/type/test, decision/invariant source]
insufficient_evidence: [comment quota, complex code left unimproved, prose paraphrase of each line]
required_inputs: [code, interface, rationale, readers, repository documentation convention]
expected_outputs: [code improvement and/or precise maintained comment/design record]
preservation_boundaries: [do not alter behavior merely to make prose cleaner; avoid duplicating authoritative contracts]
safe_actions: [interface contract, reason for workaround, units/ownership, cross-link to central ADR]
unsafe_actions: [comment false guarantee, commented-out code, vague TODO without owner/condition, duplicate long explanation]
common_failure_modes: [narration, stale comment, missing side effects, hidden rationale, documentation in unreachable location]
counterexamples: [an obvious private local helper may need no comment beyond a good name; a complex public interface still requires a contract even if implementation is readable]
interactions: [IMPL-006, IMPL-009, IMPL-010, IMPL-016]
conflicts: [CONFLICT-011]
source_support:
  - "APOSD: chapters/017-12-why-write-comments-the-four-excuses.md :: # 12: Why Write Comments? The Four Excuses"
  - "APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code"
  - "CC: chapters/043-chapter-32-self-documenting-code.md :: #### 32.4 Keys to Effective Comments"
  - "CC: chapters/043-chapter-32-self-documenting-code.md :: #### Information That Cannot Possibly Be Expressed by the Code Itself"
  - "PP: chapters/013-chapter-8-pragmatic-projects.md :: ### Comments in Code"
confidence: strong
roles: [coding-agent, review-agent, legacy-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [comments, self documenting, rationale, intent, invariant, ownership, contract]
activate_for_tasks: [implementation, API design, review, repair, workaround]
activate_for_repository_signals: [non-obvious decision, workaround, complex API, stale comment]
retrieval_priority: high
retrieval_budget_hint: small
related_concepts: [IMPL-009, IMPL-016]
```

### IMPL-016 — Conform to repository convention unless a migration is earned

```yaml
id: IMPL-016
title: Conform to repository convention unless a migration is earned
category: implementation
claim: Consistency reduces arbitrary cognitive load; an agent should follow established repository and language conventions unless a demonstrated defect, measurable cost, or accepted migration authorizes changing them.
decision_rule: Discover enforced and de facto conventions from project instructions, formatters/linters, nearby maintained code, tests, and review history. Follow them for scoped work. Propose a convention change only with evidence of harm, migration scope, compatibility and tooling plan, owner approval, and a way to avoid a mixed state.
why_it_matters: Local “improvements” can impose repository-wide variation and review noise without improving behavior or comprehension.
applicable_when: [naming, layout, error idiom, package structure, testing style, documentation]
not_applicable_when: [convention conflicts with explicit requirement, security/safety constraint, or current language correctness]
required_evidence: [repository instruction and tooling, dominant local practice, harm/benefit of change, migration authority]
insufficient_evidence: [book style, agent preference, isolated old file, “modern best practice” without repository fit]
required_inputs: [repository contracts, language standard, local examples, scope]
expected_outputs: [conforming implementation or separate migration proposal]
preservation_boundaries: [minimize diff noise; preserve compatibility and generated/vendored boundaries]
safe_actions: [run formatter, match error idiom, document an exception]
unsafe_actions: [drive-by reformat, mixed naming scheme, replace idiom across unrelated files, modify vendored code]
common_failure_modes: [aesthetic churn, blind majority rule over explicit contract, inconsistent partial migration, applying one language's style to another]
counterexamples: [a localized security flaw or language-version break can justify divergence, but the reason and follow-up must be explicit]
interactions: [IMPL-009, IMPL-010, IMPL-015, AGENT-IMPL-001]
conflicts: [CONFLICT-012]
source_support:
  - "APOSD: chapters/022-17-consistency.md :: # 17: Consistency"
  - "CC: chapters/009-chapter-4-key-construction-decisions.md :: #### 4.2 Programming Conventions"
  - "CC: chapters/042-chapter-31-layout-and-style.md :: #### Layout as Religion"
  - "CC: chapters/045-chapter-34-themes-in-software-craftsmanship.md :: ### 34.5 Focus Your Attention with the Help of Conventions"
confidence: strong
roles: [coding-agent, review-agent, refactoring-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [convention, consistency, style, formatting, repository idiom, migration]
activate_for_tasks: [all code changes, review, migration]
activate_for_repository_signals: [formatter, linter, style guide, mixed idiom]
retrieval_priority: core
retrieval_budget_hint: small
related_concepts: [IMPL-010, AGENT-IMPL-001]
```

### IMPL-017 — Optimize control flow and data for local reasoning

```yaml
id: IMPL-017
title: Optimize control flow and data for local reasoning
category: implementation
claim: Organize control flow and data so a reader can follow the nominal path, see ordering and termination, distinguish states and units, and reason about each variable within a short scope without hidden global effects.
decision_rule: Choose the simplest repository-idiomatic construct that matches the data and operation. Make required order explicit, keep the common path visible, bound nesting, use one-purpose variables with short live ranges, encode distinct states/types, handle exhaustive/default cases deliberately, and isolate unusual exits or recursion when they obscure reasoning.
why_it_matters: Deep nesting, long-lived mutable state, hidden sequencing, ambiguous sentinels, and globals increase cognitive load and defect probability.
applicable_when: [routine implementation, state machine, loops, conditionals, data transformation]
not_applicable_when: [generated code or performance-specialized code whose different structure is measured and documented]
required_evidence: [actual data/state model, language semantics, nominal/error paths, variable and decision burden, reader review]
insufficient_evidence: [cyclomatic number alone, blanket ban on early returns, blanket preference for polymorphism or tables]
required_inputs: [control/data flow, invariants, language idiom, performance constraints]
expected_outputs: [obvious routine structure, explicit states/order/termination, review rationale]
preservation_boundaries: [evaluation order, side effects, exception/cleanup behavior, numeric precision, performance contract]
safe_actions: [guard clause, named predicate, enum/sum type, table lookup when data is clearer than logic, local immutable variable]
unsafe_actions: [clever boolean expression, reuse variable for multiple meanings, hidden global dependency, default branch that masks new states]
common_failure_modes: [temporal coupling, sentinel ambiguity, off-by-one, accidental fallthrough, state/action flags, premature table/config indirection]
counterexamples: [multiple early returns can improve the nominal flow when cleanup is structurally guaranteed; a single exit is not a universal requirement]
interactions: [IMPL-010, IMPL-011, IMPL-013, PERF-IMPL-001]
conflicts: []
source_support:
  - "CC: chapters/017-chapter-10-general-issues-in-using-variables.md :: #### 10.4 Scope"
  - "CC: chapters/017-chapter-10-general-issues-in-using-variables.md :: #### 10.8 Using Each Variable for Exactly One Purpose"
  - "CC: chapters/022-chapter-14-organizing-straight-line-code.md :: #### 14.1 Statements That Must Be in a Specific Order"
  - "CC: chapters/024-chapter-16-controlling-loops.md :: #### 16.2 Controlling the Loop"
  - "CC: chapters/027-chapter-19-general-control-issues.md :: #### 19.4 Taming Dangerously Deep Nesting"
  - "APOSD: chapters/023-18-code-should-be-obvious.md :: # 18: Code Should be Obvious"
confidence: strong
roles: [coding-agent, review-agent, repair-agent, performance-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [control flow, local reasoning, nesting, loop, variable scope, state, ordering]
activate_for_tasks: [routine implementation, review, repair, algorithm]
activate_for_repository_signals: [deep nesting, globals, long live range, state flags, ambiguous branch]
retrieval_priority: high
retrieval_budget_hint: medium
related_concepts: [IMPL-011, IMPL-013]
```

### IMPL-018 — Treat concurrency as ordering, ownership, and lifecycle design

```yaml
id: IMPL-018
title: Treat concurrency as ordering ownership and lifecycle design
category: implementation
claim: Introduce concurrency only for a demonstrated responsiveness, throughput, isolation, or scheduling need, and make shared-state ownership, valid states, causal ordering, cancellation, backpressure, error propagation, and shutdown explicit.
decision_rule: First identify which operations are truly independent and which orderings are semantic. Compare a sequential design with concurrent alternatives. Prefer message/ownership boundaries or constrained synchronization; define task lifecycle and resource ownership; test deterministic invariants and use stress/race tooling appropriate to the language. Do not infer safety from absence of reproduced races.
why_it_matters: Concurrency can remove unnecessary temporal coupling but creates nondeterminism, resource cost, and failure/lifecycle complexity.
applicable_when: [parallel work, asynchronous I/O, event delivery, background task, shared mutable state]
not_applicable_when: [no measured/user-visible concurrency need; generated framework callback already dictates concurrency]
required_evidence: [required latency/throughput/responsiveness, dependency/order graph, shared state, runtime costs, lifecycle and failure model]
insufficient_evidence: [“design everything for concurrency,” available threads/goroutines, speculative scalability]
required_inputs: [workload, ordering, ownership, cancellation, resource limits, language runtime]
expected_outputs: [concurrency decision, state/ownership model, lifecycle, tests/observability]
preservation_boundaries: [ordering, exactly/at-least-once semantics, resource caps, durability, deterministic results where promised]
safe_actions: [bounded queue, immutable message, structured task group, consistent lock order, sequential fallback]
unsafe_actions: [unbounded fanout, global mutable state, orphan task, implicit retry, two-phase initialization visible concurrently]
common_failure_modes: [race, deadlock, leak, reorder, duplicate side effect, overload, lost error, shutdown hang]
counterexamples: [a UI/event loop or runtime may impose asynchronous callbacks; the agent still must establish state and lifecycle semantics within that model]
interactions: [IMPL-011, IMPL-012, IMPL-013, PERF-IMPL-001]
conflicts: [CONFLICT-013]
source_support:
  - "PP: chapters/010-chapter-5-bend-or-break.md :: ## **<sup>28</sup>** Temporal Coupling"
  - "PP: chapters/010-chapter-5-bend-or-break.md :: ### Design for Concurrency"
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Nest Allocations"
  - "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Resource Management"
confidence: contextual
roles: [coding-agent, architecture-agent, review-agent, performance-agent, repair-agent]
languages: [language-independent]
repository_archetypes: [service, embedded, distributed-system, GUI, concurrent-library]
retrieval_terms: [concurrency, temporal coupling, ordering, task lifecycle, backpressure, cancellation, race]
activate_for_tasks: [add concurrency, review async code, repair race, performance]
activate_for_repository_signals: [goroutine, thread, async, queue, lock, callback, event]
activate_for_risk_classes: [medium, high]
retrieval_priority: specialist
retrieval_budget_hint: large
related_concepts: [IMPL-013, PERF-IMPL-001]
```

### REPAIR-001 — Diagnose defects with a reproducible hypothesis loop

```yaml
id: REPAIR-001
title: Diagnose defects with a reproducible hypothesis loop
category: agent-conduct
claim: A repair should follow a stabilized reproduction, competing causal hypotheses, discriminating observations, localization of the first incorrect state or event, a root-cause explanation, and regression verification.
decision_rule: Reproduce with one controlled command/input and record expected versus actual. Narrow environmental and input variation. Form multiple hypotheses and choose the cheapest check that distinguishes them; trace backward from symptom to first divergence. Patch the cause, rerun reproduction and broader relevant tests, search for sibling instances, and remove temporary instrumentation unless retained deliberately.
why_it_matters: Symptoms can be distant from causes, and coincident edits or debugger experiments easily create false causal stories.
applicable_when: [bug report, flaky failure, data corruption, performance regression with correctness symptom]
not_applicable_when: [purely specified feature with no defect claim]
required_evidence: [reproduction or explicit inability, expected contract, observations, hypothesis ledger, first divergence, verification]
insufficient_evidence: [stack trace alone, suspicious code, changing code until test passes, blaming platform/library without isolation]
required_inputs: [report, environment, logs/data, source/history, tests]
expected_outputs: [reproduction, diagnosis with confidence, minimal repair, regression test, residual uncertainty]
preservation_boundaries: [unrelated behavior and structure; diagnostic instrumentation; production data/privacy]
safe_actions: [trace/log locally, binary search, data visualization, rubber-duck explanation, diff known-good, inspect warnings]
unsafe_actions: [bundle cleanup, suppress failing test, catch and ignore, alter production state without authority, leave secret-bearing logs]
common_failure_modes: [confirmation bias, non-reproducible patch, symptom fix, multiple simultaneous changes, environmental assumption]
counterexamples: [an urgent containment may precede full diagnosis when explicitly authorized and failure consequence requires it; mark it containment, not root-cause repair]
interactions: [U-IMPL-002, IMPL-011, IMPL-014, CHANGE-IMPL-001]
conflicts: []
source_support:
  - "CC: chapters/032-chapter-23-debugging.md :: #### The Scientific Method of Debugging"
  - "CC: chapters/032-chapter-23-debugging.md :: #### Stabilize the Error"
  - "CC: chapters/032-chapter-23-debugging.md :: #### 23.3 Fixing a Defect"
  - "PP: chapters/008-chapter-3-the-basic-tools.md :: ### Debugging Strategies"
  - "PP: chapters/008-chapter-3-the-basic-tools.md :: ### The Element of Surprise"
confidence: strong
roles: [repair-agent, debugging-agent, coding-agent, review-agent, legacy-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [debugging, reproduce, hypothesis, root cause, regression, first divergence]
activate_for_tasks: [diagnose bug, repair defect, investigate flake]
activate_for_repository_signals: [failing test, incident, stack trace, corrupted state, flaky behavior]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [IMPL-014, CHANGE-IMPL-001]
```

### CHANGE-IMPL-001 — Separate semantic repair from structural improvement

```yaml
id: CHANGE-IMPL-001
title: Separate semantic repair from structural improvement
category: refactoring
claim: Feature work and defect repair intentionally change behavior; refactoring preserves behavior. Do not obscure that distinction by bundling semantic and structural changes in one unreviewable step.
decision_rule: Label each intended edit by purpose and allowable semantic delta. Establish a preservation test before structural work. For a defect, first capture the failing behavior, make the smallest causal semantic repair, and verify it; perform optional structural cleanup in a separate, behavior-preserving slice only if authorized and earned. For a refactoring prerequisite that is necessary to reach the repair, keep it minimal and verify before the semantic step.
why_it_matters: Mixed changes destroy causal attribution, make review and rollback hard, and let unapproved behavior changes masquerade as cleanup.
applicable_when: [repair, feature plus cleanup, refactoring, optimization, migration]
not_applicable_when: [atomic transformation whose semantic and structural aspects cannot be separated without greater risk; the combined scope must then be explicit]
required_evidence: [change-type classification, behavior baseline, test/characterization, authority, diff sequence]
insufficient_evidence: [“while here,” prettier design, passing final suite with no intermediate proof]
required_inputs: [purpose, allowable behavior change, structural pressure, tests, scope]
expected_outputs: [separate commits/slices or explicit inseparability rationale, verification per slice]
preservation_boundaries: [all behavior outside authorized delta, public/data/operational contracts]
safe_actions: [preparatory rename/extract with tests, minimal repair, follow-up refactor proposal]
unsafe_actions: [repair and broad redesign together, call behavior change refactoring, update golden test to hide delta]
common_failure_modes: [scope creep, causal ambiguity, accidental semantic change, reviewer overload]
counterexamples: [changing a representation may require migration and behavior adapters together; classify it as migration, not refactoring]
interactions: [REPAIR-001, IMPL-014, CHANGE-IMPL-002, PERF-IMPL-001]
conflicts: []
source_support:
  - "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### How Do You Refactor?"
  - "CC: chapters/033-chapter-24-refactoring.md :: #### 24.4 Refactoring Safely"
  - "CC: chapters/033-chapter-24-refactoring.md :: #### Bad Times to Refactor"
confidence: strong
roles: [coding-agent, repair-agent, refactoring-agent, review-agent, legacy-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [repair versus refactoring, semantic change, structural change, scope, behavior preserving]
activate_for_tasks: [repair, refactoring, feature cleanup, review mixed diff]
activate_for_repository_signals: [large bugfix diff, rename plus logic, test expectation changes]
retrieval_priority: core
retrieval_budget_hint: small
related_concepts: [REPAIR-001, CHANGE-IMPL-002]
```

### CHANGE-IMPL-002 — Refactor only against demonstrated structural pressure

```yaml
id: CHANGE-IMPL-002
title: Refactor only against demonstrated structural pressure
category: refactoring
claim: A smell is a hypothesis. Structural change is earned when current or recurring work shows change amplification, duplicated knowledge, obscured invariants, unsafe coupling, test blockage, defect concentration, or reader burden, and a bounded transformation improves the pressure without weakening the design.
decision_rule: Record the pressure and evidence, behavior to preserve, candidate seam, expected improvement, campaign boundary, and rollback/stop condition. Prefer the smallest high-leverage campaign. Leave unattractive stable code alone when no current pressure, protection, or authority supports intervention.
why_it_matters: Continuous design investment is valuable, but aesthetic refactoring consumes risk and attention and can introduce shallow abstractions.
applicable_when: [refactoring assessment, repeated change hotspot, legacy seam, blocked feature/repair]
not_applicable_when: [vendored/generated code, stable low-touch code with no demonstrated harm, semantic repair]
required_evidence: [current task friction or history/co-change/defect/test evidence, preservation surface, seam, expected improvement]
insufficient_evidence: [file size, age, dislike, generic smell name, one difficult reading without corroboration]
required_inputs: [pressure ledger, behavior, history/tests, candidate transformations, authority]
expected_outputs: [leave-alone or one bounded campaign, verification and stop conditions]
preservation_boundaries: [observable behavior, performance/error/resource/API/data contracts]
safe_actions: [small rename/extract/move behind characterization, delete proven dead code, introduce temporary seam]
unsafe_actions: [rewrite, opportunistic redesign, many smells in one campaign, semantic fix hidden within move]
common_failure_modes: [aesthetic cleanup, abstraction proliferation, lost undocumented behavior, no stopping rule]
counterexamples: [a severe latent safety/security risk can justify preventive structural work even without frequent churn, if evidence and authority establish the risk]
interactions: [IMPL-004, IMPL-005, IMPL-014, CHANGE-IMPL-001]
conflicts: [CONFLICT-014]
source_support:
  - "CC: chapters/033-chapter-24-refactoring.md :: #### Reasons to Refactor"
  - "CC: chapters/033-chapter-24-refactoring.md :: #### Reasons Not to Refactor"
  - "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### When Should You Refactor?"
  - "APOSD: chapters/021-16-modifying-existing-code.md :: # 16: Modifying Existing Code"
  - "APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity"
confidence: contextual
roles: [refactoring-agent, legacy-agent, coding-agent, review-agent]
languages: [language-independent]
repository_archetypes: [legacy, long-lived-product, weakly-tested]
retrieval_terms: [refactoring pressure, smell hypothesis, leave code alone, hotspot, preservation]
activate_for_tasks: [assess refactoring, select campaign, enable change]
activate_for_repository_signals: [co-change, repeated repair, test blockage, duplicated rule, unknown behavior]
retrieval_priority: core
retrieval_budget_hint: medium
related_concepts: [CHANGE-IMPL-001, IMPL-014]
```

### PERF-IMPL-001 — Require measured performance pressure and a preserved baseline

```yaml
id: PERF-IMPL-001
title: Require measured performance pressure and a preserved baseline
category: performance
claim: Performance work is justified by an explicit quality requirement or measured bottleneck on representative workload; algorithm, architecture, I/O, allocation, and data layout should be considered before localized micro-optimization, and every change must preserve semantics and show repeatable improvement.
decision_rule: State metric, target, workload, environment, variability, and semantic boundary. Establish a correctness and performance baseline; profile to locate the critical path; choose the highest-level feasible intervention; change one factor; rerun correctness and statistically appropriate performance checks; keep the change only if the gain is material relative to noise and complexity cost, unless it also simplifies code.
why_it_matters: Intuition about hotspots and low-level costs is often wrong and drifts across runtimes/hardware; optimization can obscure code or change semantics.
applicable_when: [latency/throughput/memory/allocation/startup/energy requirement or regression]
not_applicable_when: [no performance requirement or evidence; microbenchmark disconnected from product workload]
required_evidence: [target/SLO or user impact, representative benchmark/profile, baseline variance, critical path, correctness oracle]
insufficient_evidence: [operation-cost folklore, one timing, synthetic microbenchmark alone, “faster” code shape, available concurrency]
required_inputs: [metric, workload, environment, profile, semantics, rollback]
expected_outputs: [measurement record, bottleneck explanation, ranked interventions, verified delta and regression guard]
preservation_boundaries: [results, precision/ordering, errors, resource ownership, durability, compatibility, readability budget]
safe_actions: [algorithm/data structure change, remove avoidable work, cache with explicit invalidation, isolate critical path, revert non-gain]
unsafe_actions: [optimize cold code, remove checks without authority, add concurrency without lifecycle model, retain opaque code with no measurable gain]
common_failure_modes: [benchmark bias, warmup/cache artifact, shifted bottleneck, semantic drift, memory-for-speed cost ignored, environment-specific result generalized]
counterexamples: [choosing a naturally efficient standard representation or algorithm during design need not await a production incident, but must not add speculative complexity]
interactions: [IMPL-003, IMPL-013, IMPL-014, IMPL-018]
conflicts: [CONFLICT-015]
source_support:
  - "CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.4 Measurement"
  - "CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.6 Summary of the Approach to Code Tuning"
  - "CC: chapters/035-chapter-26-code-tuning-techniques.md :: #### 26.7 The More Things Change, the More They Stay the Same"
  - "APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance"
  - "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Algorithm Speed in Practice"
confidence: strong
roles: [performance-agent, coding-agent, review-agent, architecture-agent]
languages: [language-independent]
repository_archetypes: [performance-sensitive, service, embedded, data-processing, library]
retrieval_terms: [performance, profile, benchmark, bottleneck, critical path, optimize, baseline]
activate_for_tasks: [performance assessment, optimization, regression]
activate_for_repository_signals: [SLO, profile, benchmark, incident, high allocation]
activate_for_risk_classes: [medium, high]
retrieval_priority: core
retrieval_budget_hint: large
related_concepts: [IMPL-014, IMPL-018]
```

### IMPL-019 — Integrate in small risk-revealing increments

```yaml
id: IMPL-019
title: Integrate in small risk-revealing increments
category: implementation
claim: Sequence implementation so working slices are integrated and tested frequently, with early proof of the riskiest boundaries and a buildable mainline.
decision_rule: Identify dependency and risk order; choose a thin end-to-end tracer or incremental component sequence; define per-slice smoke/regression gates; integrate at a cadence that keeps failures attributable. Avoid big-bang merge unless external constraints make incremental integration impossible and a specific mitigation exists.
why_it_matters: Integration order affects observability, defect localization, feedback, and the amount of unverified divergence.
applicable_when: [multi-file/module feature, dependency integration, team work, migration]
not_applicable_when: [single atomic local edit]
required_evidence: [dependency graph, risky interfaces, build/test gates, integration authority]
insufficient_evidence: [large branch compiles at end, unit tests with no boundary test]
required_inputs: [plan, dependencies, risk, CI, owners]
expected_outputs: [ordered slices, gates, mainline/integration strategy]
preservation_boundaries: [buildability, compatibility during transition, data migration safety]
safe_actions: [feature flag when justified, adapter, vertical tracer, daily smoke, incremental migration]
unsafe_actions: [long-lived unintegrated branch, all-at-once dependency switch, hidden partial state]
common_failure_modes: [big bang, fake vertical slice with stubs that hide risk, CI-only confidence, incompatible intermediate state]
counterexamples: [an indivisible protocol cutover may require coordinated release; classify it and rehearse rollback rather than calling it ordinary incremental integration]
interactions: [U-IMPL-002, IMPL-001, IMPL-014, CHANGE-IMPL-001]
conflicts: []
source_support:
  - "CC: chapters/039-chapter-29-integration.md :: #### 29.2 Integration Frequency—Phased or Incremental?"
  - "CC: chapters/039-chapter-29-integration.md :: #### Risk-Oriented Integration"
  - "CC: chapters/039-chapter-29-integration.md :: #### 29.4 Daily Build and Smoke Test"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>10</sup>** Tracer Bullets"
  - "PP: chapters/013-chapter-8-pragmatic-projects.md :: ### Regression Tests"
confidence: strong
roles: [coding-agent, implementation-agent, review-agent, migration-agent]
languages: [language-independent]
repository_archetypes: [all-multi-component]
retrieval_terms: [integration, tracer bullet, incremental, smoke test, risk order, mainline]
activate_for_tasks: [plan implementation, migration, integrate dependency]
activate_for_repository_signals: [cross-module change, long branch, new boundary]
retrieval_priority: high
retrieval_budget_hint: medium
related_concepts: [U-IMPL-002, IMPL-014]
```

### REVIEW-IMPL-001 — Classify review findings by contract and consequence

```yaml
id: REVIEW-IMPL-001
title: Classify review findings by contract and consequence
category: review
claim: A review finding should distinguish demonstrated defect or contract violation from risk, maintainability concern, suggestion, and personal preference, with severity proportional to consequence and confidence.
decision_rule: Tie a blocker to an accepted requirement, correctness/security/durability failure, incompatible API/architecture contract, or evidence-backed high-consequence risk. State reproduction or causal path. Mark maintainability hypotheses and alternatives separately. Respect repository convention and scope; do not demand source-school purity.
why_it_matters: Collaborative review detects different defects than testing, but vague preference and ego reduce signal and can silently expand authority.
applicable_when: [code review, implementation assessment, plan review]
not_applicable_when: []
required_evidence: [diff/context, contract, consequence, test/runtime/static evidence, confidence]
insufficient_evidence: [“cleaner,” book citation alone, unfamiliar style, unsupported future concern]
required_inputs: [scope, repository contract, change type, risk, evidence]
expected_outputs: [blocker/defect/risk/suggestion/preference, locator, rationale, verification]
preservation_boundaries: [review authority, task scope, author intent, unrelated code]
safe_actions: [ask focused question, cite concrete path, propose bounded alternative, acknowledge uncertainty]
unsafe_actions: [rewrite by preference, block on aesthetics, demand unrelated cleanup, equate no test with proven bug]
common_failure_modes: [severity inflation, drive-by architecture, vague style comments, missing consequence, duplicate findings]
counterexamples: [a project may designate style/lint violations as blockers; the repository contract then supplies the authority]
interactions: [U-IMPL-001, IMPL-009, IMPL-014, IMPL-016]
conflicts: []
source_support:
  - "CC: chapters/030-chapter-21-collaborative-construction.md :: #### Collaborative Construction Complements Other Quality-Assurance Techniques"
  - "CC: chapters/030-chapter-21-collaborative-construction.md :: #### Egos in Inspections"
  - "CC: chapters/029-chapter-20-the-software-quality-landscape.md :: #### 20.1 Characteristics of Software Quality"
  - "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Know Your Audience"
  - "APOSD: chapters/023-18-code-should-be-obvious.md :: # 18: Code Should be Obvious"
confidence: strong
roles: [review-agent, coding-agent, architecture-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [review, blocker, defect, suggestion, preference, severity, confidence]
activate_for_tasks: [code review, plan review, implementation assessment]
retrieval_priority: core
retrieval_budget_hint: small
related_concepts: [U-IMPL-001, IMPL-016]
```

### AGENT-IMPL-001 — Stop when authority, preservation, or evidence is insufficient

```yaml
id: AGENT-IMPL-001
title: Stop when authority preservation or evidence is insufficient
category: agent-conduct
claim: An autonomous agent must stop or escalate when completing the next step requires choosing unauthorized product semantics, changing architecture or public contracts outside scope, risking irrecoverable state, or proceeding without a credible preservation and verification path.
decision_rule: Before each material transition, ask whether the action is reversible, in scope, evidence-supported, and verifiable. Continue with safe observation or a smaller reversible slice when possible. Escalate with the decision required, alternatives, evidence, and consequence; do not merely report vague uncertainty.
why_it_matters: Technical ability and generic doctrine do not confer acceptance or execution authority.
applicable_when: [all autonomous work]
not_applicable_when: []
required_evidence: [authority, affected contracts, reversibility, verification, risk]
insufficient_evidence: [assumed maintainer preference, urgency alone, source recommendation]
required_inputs: [current action, scope, decision owner, risk, fallback]
expected_outputs: [continue/propose/stop decision, precise escalation packet]
preservation_boundaries: [behavior, data, architecture, external effects, human acceptance]
safe_actions: [read-only investigation, local reversible experiment, draft proposal, checkpoint]
unsafe_actions: [production mutation without authority, accept own work, silently widen scope, invent domain semantics]
common_failure_modes: [false completion, endless low-value analysis instead of focused escalation, authority laundering through tests, irreversible migration]
counterexamples: [normal implementation decisions within an explicitly authorized feature and accepted architecture do not require repeated human approval]
interactions: [U-IMPL-001, IMPL-001, CHANGE-IMPL-001, PERF-IMPL-001]
conflicts: []
source_support:
  - "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Take Responsibility"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### What to Say When Asked for an Estimate"
  - "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Boss-Readiness Test"
  - "CC: chapters/038-chapter-28-managing-construction.md :: #### Requirements and Design Changes"
confidence: strong
roles: [all-engineering-agents]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [stop, escalate, authority, irreversible, acceptance, uncertainty]
activate_for_tasks: [all autonomous changes]
activate_for_risk_classes: [all]
retrieval_priority: core
retrieval_budget_hint: small
related_concepts: [U-IMPL-001]
```

## High-confidence negative doctrine

These prohibitions are operational only with their stated scope and evidence threshold. They do not grant authority to modify code merely because a violation is observed.

| ID | Prohibition | Evidence threshold / exceptions | Source support |
|---|---|---|---|
| `NEG-IMPL-001` | Never begin consequential implementation while the intended behavior, affected contract, verification route, or authority remains unknowable. | A low-risk reversible experiment is allowed when explicitly framed as evidence collection; formality scales with risk. | `CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### cc2e.com/0386 Checklist: Upstream Prerequisites`; `PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Take Responsibility`. |
| `NEG-IMPL-002` | Never treat a generic practice or book preference as stronger than an accepted repository contract, current language semantics, or measured runtime evidence. | A source can identify a hypothesis or alternative; overriding the repository needs explicit evidence and authority. | `CC: chapters/045-chapter-34-themes-in-software-craftsmanship.md :: #### 34.9 Thou Shalt Rend Software and Religion Asunder`; `PP: chapters/004-preface.md :: # Preface`; `APOSD: chapters/022-17-consistency.md :: # 17: Consistency`. |
| `NEG-IMPL-003` | Never split a routine, class, or file solely because it exceeds a line or method-count threshold. | Split when a coherent independent responsibility/seam reduces total cognitive or change cost; extremely large code is a review signal, not a verdict. | `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.4 How Long Can a Routine Be?`; `APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?`. |
| `NEG-IMPL-004` | Never create routines merely to make every routine small. | Tiny routines are warranted when they introduce a meaningful abstraction, hide knowledge, centralize an operation, or improve testing/variation. | `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine`; `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`. |
| `NEG-IMPL-005` | Never introduce a shared abstraction from syntactic similarity alone. | Require shared knowledge/authority, common reasons to change, a coherent contract, and lower total cost; generated or independently owned duplication can remain. | `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication`; `APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?`. |
| `NEG-IMPL-006` | Never add an interface, wrapper, decorator, base class, or configuration knob solely to claim decoupling, testability, extensibility, or Law-of-Demeter compliance. | Require a real hidden decision, multiple implementations/consumers, ownership boundary, caller simplification, or independently changing policy. | `APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction`; `CC: chapters/012-chapter-6-working-classes.md :: #### Classes to Avoid`; `PP: chapters/010-chapter-5-bend-or-break.md :: ### Does It Really Make a Difference?`. |
| `NEG-IMPL-007` | Never infer placement or ownership from directory names or layer labels alone. | Trace state, policy, invariants, callers, accepted architecture, and change coupling. | `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`; `CC: chapters/011-chapter-5-design-in-construction.md :: #### Assign Responsibilities`. |
| `NEG-IMPL-008` | Never hide caller-relevant failure, durability, precision, ordering, or resource semantics merely to make an interface look simple. | A module may mask only failures it can reliably recover from while preserving required information and externally promised semantics. | `APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence`; `CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.3 Error-Handling Techniques`. |
| `NEG-IMPL-009` | Never use assertions as normal external-input validation or depend on disabled assertions for required safety. | Assertions express programmer assumptions/invariants; user and environment failures need defined runtime handling. | `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>23</sup>** Assertive Programming`; `CC: chapters/014-chapter-8-defensive-programming.md :: #### Guidelines for Using Assertions`. |
| `NEG-IMPL-010` | Never leave resource ownership, cleanup, cancellation, or lock acquisition order implicit across failure paths. | Process-lifetime resources may intentionally lack ordinary release, but ownership/shutdown must still be explicit. | `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>25</sup>** How to Balance Resources`; `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Nest Allocations`. |
| `NEG-IMPL-011` | Never combine a semantic repair with an unrelated “behavior-preserving” cleanup and call the whole change refactoring. | A minimal prerequisite refactor may precede a repair if separately verified and necessary; inseparable migrations must be labeled honestly. | `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### How Do You Refactor?`; `CC: chapters/033-chapter-24-refactoring.md :: #### 24.4 Refactoring Safely`. |
| `NEG-IMPL-012` | Never change a test merely to make a new implementation pass without reconciling the accepted contract. | A test can be corrected when evidence shows the test is wrong; record the authority and semantic decision. | `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Testing Against Contract`; `CC: chapters/031-chapter-22-developer-testing.md :: #### 22.1 Role of Developer Testing in Software Quality`. |
| `NEG-IMPL-013` | Never claim test adequacy from line coverage alone. | Coverage can reveal unexecuted code; adequacy requires contract, boundary, state, failure, data-flow, and risk analysis. | `CC: chapters/031-chapter-22-developer-testing.md :: #### Coverage Monitors`; `PP: chapters/013-chapter-8-pragmatic-projects.md :: ### Testing Thoroughly`. |
| `NEG-IMPL-014` | Never repair a defect without attempting a stable reproduction and root-cause explanation, unless an explicitly authorized emergency containment is required. | When reproduction is impossible, report that limitation, use available incident evidence, and reduce confidence. | `CC: chapters/032-chapter-23-debugging.md :: #### The Scientific Method of Debugging`; `PP: chapters/008-chapter-3-the-basic-tools.md :: #### Bug Reproduction`. |
| `NEG-IMPL-015` | Never optimize a suspected hotspot without a representative baseline, profile or equivalent localization, semantic oracle, and after-measurement. | Naturally efficient standard choices need not await an incident but must not add speculative complexity. | `CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.4 Measurement`; `APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance`. |
| `NEG-IMPL-016` | Never retain an opaque optimization that produces no material measured gain, unless it independently simplifies the code. | Measurement uncertainty and target workload must be considered before removal. | `APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance`; `CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.5 Iteration`. |
| `NEG-IMPL-017` | Never introduce concurrency merely because the runtime makes it easy or because future scale is imagined. | Require a demonstrated scheduling, throughput, latency, responsiveness, or isolation driver and an explicit ownership/lifecycle model. | `PP: chapters/010-chapter-5-bend-or-break.md :: ## **<sup>28</sup>** Temporal Coupling`; bounded by `CC: chapters/011-chapter-5-design-in-construction.md :: #### Design Is About Tradeoffs and Priorities`. |
| `NEG-IMPL-018` | Never narrate obvious code in comments or preserve a known-bad structure solely by explaining it. | Improve code first where safely possible; comment non-obvious contract, reason, invariant, ownership, unit, or constraint. | `CC: chapters/043-chapter-32-self-documenting-code.md :: #### Repeat of the Code`; `APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code`. |
| `NEG-IMPL-019` | Never change repository naming, layout, error, or test conventions as drive-by cleanup. | A separate accepted migration with demonstrated benefit and tooling can change them; correctness/safety can require a documented exception. | `APOSD: chapters/022-17-consistency.md :: # 17: Consistency`; `CC: chapters/042-chapter-31-layout-and-style.md :: #### Layout as Religion`. |
| `NEG-IMPL-020` | Never expose implementation detail publicly solely to make testing easier. | Introduce a test seam at the narrowest appropriate boundary, or use an existing contract; a stable test API is justified only as an intentional client contract. | `CC: chapters/011-chapter-5-design-in-construction.md :: #### Design for Test`; `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Build a Test Window`; refined by `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`. |
| `NEG-IMPL-021` | Never let a disposable prototype silently become production code. | Retained tracer code is different: it is production-quality from the start and grows through feedback. | `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Tracer Code versus Prototyping`; `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### How Not to Use Prototypes`. |
| `NEG-IMPL-022` | Never continue after a violated internal invariant when continuation can corrupt data or compound unsafe effects. | High-availability or embedded contexts may require containment/recovery instead of process death; the response must be an explicit high-level policy. | `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Crash, Don't Trash`; `CC: chapters/014-chapter-8-defensive-programming.md :: #### Robustness vs. Correctness`. |
| `NEG-IMPL-023` | Never treat source code as the sole authority for behavior when tests, generated artifacts, persisted data, protocols, runtime observations, or accepted decisions define additional contracts. | CC's “code is current” claim is useful only as a warning that stale prose cannot override execution; repository evidence classes must be reconciled. | `CC: chapters/006-chapter-1-welcome-to-software-construction.md :: ### 1.2 Why Is Software Construction Important?`; bounded by `PP: chapters/012-chapter-7-before-the-project.md :: ### Digging for Requirements`. |
| `NEG-IMPL-024` | Never turn a review preference into a blocking defect without a repository contract or evidence-backed consequence. | Project-enforced style and process rules can be blockers because the repository supplies the contract. | `CC: chapters/030-chapter-21-collaborative-construction.md :: #### Egos in Inspections`; `CC: chapters/045-chapter-34-themes-in-software-craftsmanship.md :: #### 34.9 Thou Shalt Rend Software and Religion Asunder`. |

## Conflict registry

### CONFLICT-001 — Deep modules versus small routines/classes

```yaml
conflict_id: CONFLICT-001
positions:
  - APOSD: Prefer deep modules; splitting is harmful when it multiplies shallow interfaces, separates conjoined knowledge, or forces readers to jump among fragments.
  - CC: Small routines can introduce intermediate abstractions, hide nested complexity, and centralize operations; however, smallness alone is explicitly not a reason to extract, and fixed length limits are rejected.
hidden_assumptions:
  - "Small-routine advocacy assumes the extracted block has a nameable, independently understandable purpose and that call navigation is cheap."
  - "Deep-module advocacy assumes the larger body remains cohesive and that hiding detail behind the interface does not obscure unrelated policy or operational behavior."
evidence_favoring_each_position:
  APOSD: [many pass-through helpers, repeated navigation needed to understand one operation, helpers share internal knowledge and never change independently, interface concepts rival hidden logic]
  CC: [deep nesting, reusable semantic operation, independently testable or changing subtask, repeated knowledge, well-named call replaces low-level mechanics]
decision_rule: Ignore line count as a verdict. Extract only a coherent independent abstraction that lowers total reader/change burden; otherwise keep the cohesive logic together. Merge fragments whose only purpose is forwarding or artificial sequencing. Review very large routines for decision/data burden, but do not split mechanically.
unresolved_questions: [No universal metric compares interface burden and hidden complexity; reader review and repository change evidence remain necessary.]
roles_affected: [coding-agent, refactoring-agent, review-agent, architecture-agent]
source_support:
  - "APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep"
  - "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.4 How Long Can a Routine Be?"
```

### CONFLICT-002 — Abstraction versus duplication

```yaml
conflict_id: CONFLICT-002
positions:
  - PP: Keep one authoritative representation of each piece of knowledge; duplication causes inconsistent change.
  - CC: Similar code commonly signals a decomposition problem and a shared routine/class may centralize maintenance.
  - APOSD: Extracting small repeated code can add a shallow interface and couple occurrences that are only superficially similar.
hidden_assumptions:
  - "Deduplication assumes occurrences encode the same knowledge and have the same reasons to change."
  - "Retaining duplication assumes independent semantic ownership or that the common interface would be more complex than coordinated maintenance."
evidence_favoring_each_position:
  abstraction: [same business rule or representation, repeated coordinated changes, shared bug fixes, one authoritative generator, coherent simple contract]
  duplication: [different domain owners, likely independent divergence, only syntax is shared, abstraction requires flags/type tests/parameters, generated outputs]
decision_rule: Apply DRY to knowledge authority, not tokens. Extract when shared semantics and change coupling are demonstrated and a coherent contract lowers total cost. Retain and, if needed, explain deliberate duplication when ownership differs or the abstraction is premature.
unresolved_questions: [Future divergence and future co-change cannot be known perfectly; choose the more reversible option and revisit with evidence.]
roles_affected: [coding-agent, refactoring-agent, review-agent]
source_support:
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication"
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine"
  - "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
```

### CONFLICT-003 — Law of Demeter wrappers versus direct coupling and deep interfaces

```yaml
conflict_id: CONFLICT-003
positions:
  - PP: Minimize traversal through collaborators so a routine knows only close collaborators; this limits structural coupling.
  - APOSD: Pass-through methods and decorators often create shallow modules and repeated interfaces without hiding a distinct abstraction.
hidden_assumptions:
  - "Demeter wrappers assume the intermediary owns the relationship and protects callers from an unstable object graph."
  - "Direct coupling assumes the downstream interface is a legitimate caller dependency and another wrapper would add no policy, translation, or hiding."
evidence_favoring_each_position:
  wrapper: [intermediary owns lifecycle/authority, downstream structure is volatile, wrapper presents a semantic operation, policy or translation is centralized]
  direct: [wrapper merely repeats signature, downstream is already accepted contract, no ownership hiding, wrapper multiplies navigation/tests]
decision_rule: Add forwarding only when it hides ownership/structure, centralizes policy, translates an external contract, or creates a stable semantic operation. Otherwise prefer the simplest direct dependency allowed by accepted architecture. Do not enforce traversal shape mechanically.
unresolved_questions: [Some repositories intentionally use facades for dependency governance even when locally shallow; accepted architecture may settle the trade-off.]
roles_affected: [coding-agent, architecture-agent, review-agent, refactoring-agent]
source_support:
  - "PP: chapters/010-chapter-5-bend-or-break.md :: ## **<sup>26</sup>** Decoupling and the Law of Demeter"
  - "PP: chapters/010-chapter-5-bend-or-break.md :: ### Does It Really Make a Difference?"
  - "APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction"
```

### CONFLICT-004 — Generalized reuse versus local clarity

```yaml
conflict_id: CONFLICT-004
positions:
  - APOSD: A somewhat general-purpose module can be deeper and simpler than a special-purpose one if it serves current needs through a clean mechanism.
  - PP: Reversibility and orthogonality favor abstraction from volatile technology or policy.
  - CC: Anticipating likely change and reusable components can reduce future modification.
  - Counter-pressure in all three: speculative features, overengineering, and abstraction can make present code harder.
hidden_assumptions:
  - "Generality assumes current examples reveal a stable common mechanism and likely variations are evidence-backed."
  - "Local specificity assumes deferring abstraction remains cheap and does not duplicate authoritative knowledge."
evidence_favoring_each_position:
  generality: [multiple current consumers, independent policy/mechanism, accepted library mission, repeated variation, simpler common-case API]
  local_clarity: [single use, unstable requirements, hypothetical options, generic contract more complex than implementation, low reversal cost]
decision_rule: Generalize across current demonstrated needs and accepted mission, not imagined features. Hide reversible implementation choices, keep the common case simple, and defer extension points until variation or compatibility commitments earn them.
unresolved_questions: [A public library may require anticipatory compatibility design whose evidence comes from product strategy rather than in-repository uses.]
roles_affected: [coding-agent, architecture-agent, review-agent]
source_support:
  - "APOSD: chapters/011-6-general-purpose-modules-are-deeper.md :: # 6: General-Purpose Modules are Deeper"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Reversibility"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Identify Areas Likely to Change"
  - "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Overengineering"
```

### CONFLICT-005 — Metadata/configuration versus pulling complexity downward

```yaml
conflict_id: CONFLICT-005
positions:
  - PP: Put abstractions in code and volatile details/policy in metadata; configuration can make behavior flexible without recompilation.
  - APOSD: Configuration is an interface and cognitive burden; modules should often choose sensible defaults and absorb complexity rather than make every caller/operator configure it.
hidden_assumptions:
  - "Metadata advocacy assumes the value is legitimately user/operator policy, changes independently, and can be validated/observed."
  - "Internalization assumes the module has enough information and authority to choose, and the choice is technical mechanism rather than external policy."
evidence_favoring_each_position:
  metadata: [operator/customer choice, deployment-specific credential/endpoint/resource limit, independently changing business rules, runtime reload requirement]
  internal: [stable implementation detail, derivable value, tuning knob users cannot choose safely, one valid default, configuration causes invalid combinations]
decision_rule: Expose configuration only for genuine external policy or independently varying environment. Internalize or derive mechanism choices and defaults. Treat every setting as a versioned public operational interface with validation, observability, ownership, and deprecation cost.
unresolved_questions: [Who owns a choice can vary by deployment model; repository and operational contracts decide.]
roles_affected: [coding-agent, architecture-agent, review-agent, operations-aware agent]
source_support:
  - "PP: chapters/010-chapter-5-bend-or-break.md :: ## **<sup>27</sup>** Metaprogramming"
  - "PP: chapters/010-chapter-5-bend-or-break.md :: ### When to Configure"
  - "APOSD: chapters/013-8-pull-complexity-downwards.md :: # 8: Pull Complexity Downwards"
  - "APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction"
```

### CONFLICT-006 — Keep behavior together versus separate responsibilities

```yaml
conflict_id: CONFLICT-006
positions:
  - CC: Favor functionally cohesive routines/classes and separate unrelated operations.
  - APOSD: Keep code together when it shares knowledge, is commonly used together, or cannot be understood independently; separation itself creates interfaces and duplication.
hidden_assumptions:
  - "Separation assumes responsibilities can be named and changed independently through simple contracts."
  - "Togetherness assumes shared knowledge is truly one abstraction, not accidental temporal sequence or a god object."
evidence_favoring_each_position:
  separate: [independent change/use, unrelated policy, distinct ownership/lifecycle, clean interface, tests isolate meaningful contract]
  together: [shared hidden decision/invariant, bidirectional calls, always-used-together concept, separation duplicates knowledge or adds pass-through]
decision_rule: Analyze shared knowledge, ownership, common use, independent change, and interface burden. Separate only along a coherent semantic seam; keep one module when separation leaks or duplicates the very knowledge it should hide.
unresolved_questions: [Organizational ownership can force boundaries despite local code cohesion; accepted architecture then dominates.]
roles_affected: [coding-agent, refactoring-agent, architecture-agent, review-agent]
source_support:
  - "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.2 Design at the Routine Level"
  - "CC: chapters/012-chapter-6-working-classes.md :: #### Good Abstraction"
  - "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
```

### CONFLICT-007 — Up-front design versus evolutionary design

```yaml
conflict_id: CONFLICT-007
positions:
  - CC: Upstream problem, requirements, and architecture work reduce downstream risk; design should proceed far enough that implementation is understood.
  - PP: Tracer bullets, prototypes, reversibility, and requirements discovery favor feedback and learning through working slices.
  - APOSD: Strategic design matters, but good design evolves continuously; design alternatives should precede consequential choices.
hidden_assumptions:
  - "Up-front design assumes key risks and constraints are discoverable before implementation and reversal is expensive."
  - "Evolutionary design assumes fast feedback, cheap reversible increments, and protection against tactical accretion."
evidence_favoring_each_position:
  upfront: [safety/durability, public contract, costly migration, many teams, known quality constraints, irreversible technology]
  evolutionary: [uncertain requirements, novel integration, small reversible slice, strong automated feedback, rapidly converging product]
decision_rule: Do the minimum design needed to resolve high-consequence and hard-to-reverse questions before coding; use prototypes or tracer slices to resolve empirical uncertainty; then invest continuously in coherent abstractions. Neither exhaustive detail nor zero design is acceptable by default.
unresolved_questions: [The exact threshold is contextual and cannot be reduced to a universal percentage or phase.]
roles_affected: [coding-agent, architecture-agent, implementation-agent, review-agent]
source_support:
  - "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Iterative Approaches' Effect on Prerequisites"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: ### 5.5 Comments on Popular Methodologies"
  - "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>10</sup>** Tracer Bullets"
  - "APOSD: chapters/008-3-working-code-isnt-enough.md :: # 3: Working Code Isn’t Enough"
  - "APOSD: chapters/016-11-design-it-twice.md :: # 11: Design it Twice"
```

### CONFLICT-008 — Descriptive names versus language/repository brevity

```yaml
conflict_id: CONFLICT-008
positions:
  - APOSD and CC: Names should form precise mental images and may need length to distinguish concepts, especially at broad scope.
  - Go-oriented convention discussed by APOSD and many repository idioms: short names can be clearer in tiny, conventional scopes and avoid stutter.
hidden_assumptions:
  - "Longer-name advocacy assumes the extra words carry semantic distinctions rather than repetition."
  - "Brevity assumes context is adjacent, scope is tiny, and readers share the idiom."
evidence_favoring_each_position:
  descriptive: [public API, wide scope, multiple similar concepts/units, effectful routine, domain distinction]
  brief: [loop/index/receiver in tiny scope, standard language idiom, surrounding type supplies context, repository reader feedback]
decision_rule: Follow repository/language convention, then choose the shortest name that preserves the necessary semantic distinction at its scope. Resolve disputes with real reader comprehension, not universal character counts.
unresolved_questions: [Reader populations differ; public libraries may need more context than internal packages.]
roles_affected: [coding-agent, review-agent]
source_support:
  - "APOSD: chapters/019-14-choosing-names.md :: # 14: Choosing Names"
  - "CC: chapters/018-chapter-11-the-power-of-variable-names.md :: #### The Effect of Scope on Variable Names"
  - "CC: chapters/018-chapter-11-the-power-of-variable-names.md :: #### Guidelines for Language-Specific Conventions"
```

### CONFLICT-009 — Exceptions for exceptional conditions versus reducing error surfaces

```yaml
conflict_id: CONFLICT-009
positions:
  - PP: Exceptions should represent genuinely unexpected conditions; ordinary outcomes often belong in normal return/control flow.
  - APOSD: Redesign semantics to eliminate, mask, or aggregate errors and reduce the number of handlers.
  - CC: Select among return/status, neutral value, retry, logging, shutdown, or exceptions based on robustness/correctness policy and language context.
hidden_assumptions:
  - "Exceptional-condition framing assumes a stable distinction between expected and unexpected for each caller."
  - "Error elimination assumes information is not needed by callers and the new semantics remain intuitive and safe."
evidence_favoring_each_position:
  explicit_normal_result: [common absence/conflict, caller routinely branches, language idiom uses result/error]
  exception: [cannot fulfill contract, propagation is needed across layers, language/repository idiom supports it]
  define_or_mask: [idempotent/total semantics natural, module can recover reliably, caller has no useful decision]
  crash: [internal invariant violated, continuation risks corruption, containment/restart policy exists]
decision_rule: Classify semantic normality per operation and caller, not globally. Preserve meaningful failure information. Reduce handlers only via natural semantics or reliable recovery; select the repository/language mechanism after deciding the contract.
unresolved_questions: [Checked/unchecked exception mechanics and idioms are language-specific and must be routed separately.]
roles_affected: [coding-agent, review-agent, repair-agent, architecture-agent]
source_support:
  - "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>24</sup>** When to Use Exceptions"
  - "APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence"
  - "CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.3 Error-Handling Techniques"
```

### CONFLICT-010 — Test-first development versus design-first abstraction

```yaml
conflict_id: CONFLICT-010
positions:
  - PP and CC: Writing tests first can shorten feedback, clarify contracts, and ensure testability; both also accept tests written after.
  - APOSD: Feature-by-feature TDD can encourage tactical design and prevent considering broader module interfaces; it explicitly endorses a failing test before a defect fix.
hidden_assumptions:
  - "Test-first advocacy assumes the next test expresses a stable external contract and developers still consider architectural alternatives."
  - "Design-first advocacy assumes designers can anticipate caller needs and will validate abstractions with executable feedback soon."
evidence_favoring_each_position:
  test_first: [defect regression, clear boundary contract, pure algorithm, behavior uncertainty resolved by examples]
  design_first: [new shared module/API, responsibility allocation, broad compatibility surface, risk of mock-driven internals]
decision_rule: Always establish a failing regression for a reproducible defect when feasible. For new module/API work, sketch and compare the abstraction and contracts first, then use tests to drive/verify behavior in small slices. Do not let test order substitute for design reasoning.
unresolved_questions: [Team skill and test style materially affect outcomes; corpus supplies no controlled resolution.]
roles_affected: [coding-agent, test-agent, review-agent, repair-agent]
source_support:
  - "CC: chapters/031-chapter-22-developer-testing.md :: #### Test First or Test Last?"
  - "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Unit Testing"
  - "APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends"
```

### CONFLICT-011 — Comments as essential design information versus self-documenting code

```yaml
conflict_id: CONFLICT-011
positions:
  - APOSD: Comments are essential for informal interfaces, abstractions, rationale, and non-obvious information; comments-first can improve design.
  - CC and PP: Prefer code whose names, types, organization, and control express mechanics; comments that repeat code are liabilities and complex code should be improved first.
hidden_assumptions:
  - "Comment advocacy assumes maintainers keep comments close and current and that the knowledge cannot be encoded."
  - "Self-documenting advocacy assumes code/type systems can express enough of the contract and rationale, which they often cannot."
evidence_favoring_each_position:
  comment: [public contract, invariant, unit/ownership, rationale, workaround, nonlocal relation, event invocation context]
  code_change: [comment narrates mechanics, name/control is misleading, type can prevent invalid state, comment drifts]
decision_rule: Improve code to express what it can; comment the remaining contract, intent, reason, invariant, and constraint. Comments-first is an optional design probe for consequential interfaces, not a mandatory workflow.
unresolved_questions: [Repository documentation tooling and language conventions determine the best location/form.]
roles_affected: [coding-agent, review-agent, legacy-agent]
source_support:
  - "APOSD: chapters/017-12-why-write-comments-the-four-excuses.md :: # 12: Why Write Comments? The Four Excuses"
  - "APOSD: chapters/020-15-write-the-comments-first.md :: # 15: Write The Comments First"
  - "CC: chapters/043-chapter-32-self-documenting-code.md :: ### 32.2 Programming Style as Documentation"
  - "CC: chapters/043-chapter-32-self-documenting-code.md :: #### 32.4 Keys to Effective Comments"
  - "PP: chapters/013-chapter-8-pragmatic-projects.md :: ### Comments in Code"
```

### CONFLICT-012 — Repository uniformity versus local improvement

```yaml
conflict_id: CONFLICT-012
positions:
  - APOSD and CC: Consistency frees attention for meaningful differences; follow established convention.
  - PP and CC: Do not let historical accidents or broken design accumulate; deliberately improve what is harmful.
hidden_assumptions:
  - "Uniformity assumes the convention is harmless and variation cost exceeds local benefit."
  - "Improvement assumes the agent has evidence, authority, and a migration path that avoids a worse mixed state."
evidence_favoring_each_position:
  uniformity: [aesthetic difference, no defect, enforced formatter/linter, broad migration outside scope]
  improvement: [correctness/security issue, recurring reader errors, measurable maintenance cost, language upgrade requirement, accepted migration]
decision_rule: Conform in ordinary scoped work. Treat a convention change as a separate migration with evidence, owner approval, tooling, compatibility plan, and completion boundary. Make documented local exceptions only for stronger correctness or safety constraints.
unresolved_questions: [A legacy repository may have no dominant convention; choose the nearest maintained subsystem and avoid claiming global standard.]
roles_affected: [coding-agent, review-agent, refactoring-agent]
source_support:
  - "APOSD: chapters/022-17-consistency.md :: # 17: Consistency"
  - "CC: chapters/009-chapter-4-key-construction-decisions.md :: #### 4.2 Programming Conventions"
  - "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ## **<sup>2</sup>** Software Entropy"
```

### CONFLICT-013 — Design for concurrency versus concurrency only under pressure

```yaml
conflict_id: CONFLICT-013
positions:
  - PP: Challenge unnecessary temporal coupling and design objects/workflow so operations can proceed concurrently.
  - Evidence-governed constraint from CC/APOSD: design trade-offs and complexity costs must follow actual quality drivers; concurrency adds state, ordering, resource, and debugging burdens.
hidden_assumptions:
  - "Concurrency-first assumes independence will be valuable and state can be made safe cheaply."
  - "Sequential-first assumes future concurrency can be introduced without prohibitive redesign."
evidence_favoring_each_position:
  concurrency: [measured latency/throughput, required responsiveness, independent I/O, failure isolation, existing async runtime contract]
  sequential: [no driver, low load, shared invariants dominate, deterministic simplicity, constrained resources]
decision_rule: Remove accidental ordering in interfaces when it does not add complexity, but execute concurrently only for demonstrated drivers and with explicit ownership, lifecycle, backpressure, cancellation, and ordering semantics.
unresolved_questions: [Some platform APIs impose concurrency regardless of need; doctrine must then focus on containment rather than selection.]
roles_affected: [coding-agent, performance-agent, architecture-agent, review-agent]
source_support:
  - "PP: chapters/010-chapter-5-bend-or-break.md :: ## **<sup>28</sup>** Temporal Coupling"
  - "PP: chapters/010-chapter-5-bend-or-break.md :: ### Design for Concurrency"
  - "CC: chapters/011-chapter-5-design-in-construction.md :: #### Design Is About Tradeoffs and Priorities"
  - "APOSD: chapters/026-21-decide-what-matters.md :: # 21: Decide What Matters"
```

### CONFLICT-014 — Continuous refactoring/broken windows versus leaving code alone

```yaml
conflict_id: CONFLICT-014
positions:
  - PP: Repair broken windows and refactor early/often before entropy normalizes poor structure.
  - APOSD: Invest strategically while modifying code, but avoid tactical patching; design quality compounds.
  - CC: Refactoring has explicit reasons not to do it and bad times; risk and verification matter.
hidden_assumptions:
  - "Immediate cleanup assumes the defect is real, local, protected, and within authority."
  - "Leave-alone assumes unattractive code is stable and the next change does not depend on it."
evidence_favoring_each_position:
  refactor_now: [current task blocked, recurring co-change/defects, duplicated rule, small protected transformation, imminent spread]
  leave_alone: [no current change pressure, weak characterization, high consequence, generated/vendor code, broad redesign, no authority]
decision_rule: Convert “broken window” or smell into a specific pressure and consequence. Perform a bounded verified change only if pressure, seam, protection, and authority exist; otherwise record the observation without drive-by cleanup.
unresolved_questions: [Cultural signaling effects of visible poor code are hard to measure and should not override concrete risk.]
roles_affected: [refactoring-agent, coding-agent, legacy-agent, review-agent]
source_support:
  - "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ## **<sup>2</sup>** Software Entropy"
  - "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### When Should You Refactor?"
  - "APOSD: chapters/021-16-modifying-existing-code.md :: # 16: Modifying Existing Code"
  - "CC: chapters/033-chapter-24-refactoring.md :: #### Reasons Not to Refactor"
  - "CC: chapters/033-chapter-24-refactoring.md :: #### Bad Times to Refactor"
```

### CONFLICT-015 — Performance specialization versus abstraction and clarity

```yaml
conflict_id: CONFLICT-015
positions:
  - CC and APOSD: Critical paths may justify specialized data layout, caching, inlining, reduced allocation, or low-level code after measurement.
  - PP/APOSD/CC: Orthogonality, deep interfaces, and clean code preserve changeability and make profiling/local optimization possible.
hidden_assumptions:
  - "Specialization assumes the measured gain is material and stable enough to repay semantic and maintenance cost."
  - "Abstraction-first assumes overhead is outside the critical path or can be optimized behind the interface."
evidence_favoring_each_position:
  specialization: [representative profile, hard target, material repeated gain, isolated critical path, regression benchmark]
  abstraction: [no hotspot evidence, negligible gain, broad readability loss, changing runtime, optimization can stay internal]
decision_rule: Preserve a simple semantic interface where possible and specialize behind it. If the interface itself must expose representation/performance, make that an explicit contract. Measure before/after, protect semantics, document the reason, and remove specialization when it no longer pays.
unresolved_questions: [Hardware/runtime drift can invalidate a previously earned optimization; periodic remeasurement may be warranted but cadence is contextual.]
roles_affected: [performance-agent, coding-agent, architecture-agent, review-agent]
source_support:
  - "CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.4 Measurement"
  - "CC: chapters/035-chapter-26-code-tuning-techniques.md :: #### 26.7 The More Things Change, the More They Stay the Same"
  - "APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance"
  - "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Algorithm Speed in Practice"
```

### CONFLICT-016 — Implementation inheritance versus composition

```yaml
conflict_id: CONFLICT-016
positions:
  - CC: Containment is usually preferable; inheritance is appropriate for a genuine substitutable is-a relation that simplifies design, but its rules and coupling costs are substantial.
  - APOSD: Interface inheritance can deepen a module through multiple implementations; implementation inheritance leaks state and coupling, so composition is usually safer.
  - PP/CC reuse pressure: inheritance can appear to remove duplication but may conflate reuse with substitutability.
hidden_assumptions:
  - "Inheritance assumes stable behavioral substitutability, controlled base evolution, and useful shared abstraction."
  - "Composition assumes delegation/interface overhead is lower and required variation can be expressed without privileged base access."
evidence_favoring_each_position:
  inheritance: [accepted framework contract, true substitution, multiple implementations, stable small base contract]
  composition: [reuse-only motive, independent lifecycles, base-state access, optional capability, likely independent change]
decision_rule: Require behavioral substitutability for inheritance. Prefer composition for implementation reuse and independent change. Never create a hierarchy solely to eliminate similar code.
unresolved_questions: [Some language/framework ecosystems mandate inheritance; contain it at the adapter boundary.]
roles_affected: [coding-agent, architecture-agent, refactoring-agent, review-agent]
source_support:
  - "CC: chapters/012-chapter-6-working-classes.md :: #### Containment (\"has a\" Relationships)"
  - "CC: chapters/012-chapter-6-working-classes.md :: #### Inheritance (\"is a\" Relationships)"
  - "APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends"
```

## Deterministic procedure and rubric contributions

### PROC-IMPL-001 — Plan an implementation

- **Inputs:** authorized outcome; repository instructions; accepted requirements/decisions; relevant source, tests, history, runtime signals; risk and language/runtime context.
- **Evidence required:** observable acceptance behavior; current path through the system; ownership and integration point; affected contracts; error/resource policy; verification route; explicit unknowns.
- **Decision steps:**
  1. State the requested outcome and classify the change type.
  2. Record authority and behavior that must not change.
  3. Trace an existing analogous path from entry to effect; identify data/policy owners and integration boundary.
  4. Enumerate functional, quality, error, resource, security, compatibility, and operational constraints that actually apply.
  5. Rank unresolved assumptions by consequence and reversal cost; run the cheapest discriminating probe for the top item.
  6. For consequential interfaces or placement, compare at least two materially different designs.
  7. Choose the smallest end-to-end or dependency-ordered slices; assign a verification gate and rollback/stop condition to each.
  8. Confirm conventions, generated/vendored boundaries, and files in scope before editing.
- **Outputs:** evidence ledger; selected design/placement; ordered slices; preservation matrix; test/verification plan; escalation questions.
- **Stop conditions:** required semantics cannot be inferred safely; no credible preservation test; next action is outside authority; irreversible/high-consequence change lacks owner approval.
- **Escalation conditions:** competing product semantics, public/API/data migration, architectural redefinition, production/external effect, unbounded risk.
- **Common false positives:** demanding full architecture for a tiny reversible edit; treating every unknown as blocking; copying an analogous path that is itself deprecated.
- **Source support:** `CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### cc2e.com/0386 Checklist: Upstream Prerequisites`; `CC: chapters/011-chapter-5-design-in-construction.md :: #### cc2e.com/0527 CHECKLIST: Design in Construction`; `APOSD: chapters/016-11-design-it-twice.md :: # 11: Design it Twice`; `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>10</sup>** Tracer Bullets`.

### PROC-IMPL-002 — Decide where new behavior belongs

- **Inputs:** behavior contract, state/data touched, invariants, side effects, callers, accepted architecture, repository package/module conventions.
- **Evidence required:** actual ownership and call paths, not filenames; current interfaces; knowledge that would otherwise be duplicated; lifecycle and policy boundaries.
- **Decision steps:**
  1. Name the behavior in domain/repository terms and list the facts it needs.
  2. Identify which module owns each fact, invariant, resource, and policy.
  3. Test each candidate owner: can it implement the behavior without exposing representation, importing unrelated policy, or creating a pass-through interface?
  4. Prefer the narrowest existing coherent owner.
  5. If no owner fits, define a new module only if its contract is coherent, useful to current callers, and hides nontrivial knowledge.
  6. Check dependency direction, error/resource semantics, test seam, and operational visibility.
  7. Validate against reader/change locality: how many modules must change and be understood?
- **Outputs:** owner and rationale; interface; dependencies; rejected placements; preservation boundary.
- **Stop conditions:** ownership depends on unauthorized architecture/product decisions; required state has no known authority; placement would cross a forbidden boundary.
- **Escalation conditions:** domain ownership disputed; new public boundary or dependency required; data authority moves.
- **Common false positives:** feature-folder placement by name; service/utility grab-bag; moving behavior to the caller because it is easier to test; interpreting “pull complexity down” as absorbing unrelated policy.
- **Source support:** `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`; `APOSD: chapters/013-8-pull-complexity-downwards.md :: # 8: Pull Complexity Downwards`; `CC: chapters/011-chapter-5-design-in-construction.md :: #### Assign Responsibilities`.

### PROC-IMPL-003 — Determine whether an abstraction is earned

- **Inputs:** candidate occurrences/callers, proposed contract, ownership, change history or current pressure, direct-code alternative.
- **Evidence required:** shared knowledge or independent variation; current use; interface and navigation cost; behavior/error/resource semantics; repository architecture.
- **Decision steps:**
  1. State the exact knowledge or mechanism the abstraction would hide.
  2. Identify current consumers and whether they share reasons to change.
  3. Sketch the direct implementation and abstraction interface.
  4. Count concepts callers must learn, parameters/flags, forwarding layers, and failure/ownership rules in each.
  5. Check whether the candidate supports a real boundary: multiple implementations, consumer substitution, external translation, policy/mechanism, or centralized authority.
  6. Reject if justified only by token similarity, line count, mocking convenience, or hypothetical use.
  7. Select the abstraction only if total cognitive/change cost falls; otherwise retain local code and revisit on evidence.
- **Outputs:** introduce/retain/defer decision; contract; evidence; revisit trigger.
- **Stop conditions:** behavior would change during extraction without authorization; no preservation surface; ownership is unresolved.
- **Escalation conditions:** public extension point, framework/library mission, dependency direction change.
- **Common false positives:** two copies imply shared concept; an interface automatically decouples; one implementation plus mock counts as variation; tiny wrapper counts as depth.
- **Source support:** `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`; `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication`; `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine`.

### PROC-IMPL-004 — Review an API

- **Inputs:** API declaration and implementation; callers/use cases; repository/language conventions; compatibility, error, resource, concurrency, and performance contracts.
- **Evidence required:** at least one real caller flow; valid/invalid states; effects; failure and ownership behavior; versioning/public status.
- **Decision steps:**
  1. State the abstraction in one sentence from the caller's perspective.
  2. List every concept a caller must understand; flag those that are representation or unrelated policy.
  3. For each operation/parameter/result, record meaning, units, validity, mutability, ownership, side effects, blocking, ordering, and failures.
  4. Check common-case simplicity and whether error/resource cleanup is possible.
  5. Check substitutability if interface/inheritance is involved; reject unused capabilities and control flags for unrelated operations.
  6. Check compatibility and evolution/reversal cost.
  7. Require tests/examples for important contracts and comments for non-obvious informal obligations.
  8. Classify findings as defect, risk, suggestion, or preference.
- **Outputs:** API scorecard; blockers and nonblockers; revised contract or acceptance rationale.
- **Stop conditions:** caller semantics or compatibility authority missing; failure/durability contract unknown.
- **Escalation conditions:** breaking change, public contract, data/protocol change, new operator burden.
- **Common false positives:** fewer methods means deeper API; getters equal encapsulation; a generic `context/options` object is simpler; testability warrants public internals.
- **Source support:** `CC: chapters/012-chapter-6-working-classes.md :: ### 6.2 Good Class Interfaces`; `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.5 How to Use Routine Parameters`; `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`; `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>21</sup>** Design by Contract`.

### PROC-IMPL-005 — Evaluate duplication

- **Inputs:** occurrences, semantic owners, requirements, history/co-change if available, generator/cache context.
- **Evidence required:** whether the same knowledge is represented; reasons to change; coordination burden; candidate contract.
- **Decision steps:**
  1. Normalize syntax mentally and name the rule each occurrence implements.
  2. Determine whether the rules share one authority or merely look alike.
  3. Inspect change history and defect fixes for coordinated edits; if unavailable, reason from explicit contracts and mark uncertainty.
  4. Check whether generation, configuration, or a cache deliberately duplicates from one authority.
  5. Sketch an abstraction and test whether it needs branching/flags/parameters for each owner.
  6. Extract only if shared authority and a coherent simpler contract exist; otherwise retain and, if surprising, document independence.
- **Outputs:** true-knowledge duplication, deliberate duplication, or coincidental similarity; action and consistency mechanism.
- **Stop conditions:** semantic ownership unknown; extraction would mix domains or behavior change.
- **Escalation conditions:** shared public API, generator ownership, cross-team/domain authority.
- **Common false positives:** clone detector result; same algorithm in independent domains; generated output; performance cache.
- **Source support:** `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication`; `APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?`.

### PROC-IMPL-006 — Evaluate module depth and a split/merge proposal

- **Inputs:** module/routine contract, implementation, callers, change/read history, proposed seam.
- **Evidence required:** interface concepts, hidden complexity, cohesion, dependency/knowledge sharing, decision/data burden, reader feedback.
- **Decision steps:**
  1. Describe useful functionality hidden and interface concepts exposed.
  2. Assess common-case caller steps and whether callers inspect implementation.
  3. Identify unrelated knowledge/owners versus shared decisions/invariants.
  4. Assess decision count, nesting, live data, side effects, and independent test/change.
  5. Simulate the split/merge: new interfaces, parameters, navigation, duplicated knowledge, dependency direction.
  6. Split if a coherent independent subtask lowers total burden; merge if fragments are pass-through/conjoined; otherwise leave unchanged.
- **Outputs:** leave/split/merge/deepen decision; seam; tests and migration scope.
- **Stop conditions:** behavior not characterized; public compatibility unresolved.
- **Escalation conditions:** architectural boundary or public API changes.
- **Common false positives:** long file, method count, one-screen rule, “single responsibility” without actor/knowledge evidence, tiny method assumed good.
- **Source support:** `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`; `APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?`; `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.4 How Long Can a Routine Be?`.

### PROC-IMPL-007 — Establish preservation boundaries and required protection

- **Inputs:** change type, authorized semantic delta, current behavior/contracts, users/callers, data/resource/operational constraints, tests/runtime observations.
- **Evidence required:** accepted requirements and decisions; public/internal contracts; relevant test and runtime evidence; known incidents and undocumented behavior for legacy work.
- **Decision steps:**
  1. Classify change as feature, repair, refactor, migration, optimization, cleanup, deletion, dependency upgrade, hardening, or documentation.
  2. State allowed semantic change and all behavior outside it.
  3. Inventory API/protocol/data, error, timing/order, precision, resource, durability, security, observability, and operational boundaries.
  4. Mark each as preserve, intentionally change, unknown, or not applicable; attach authority/evidence.
  5. Select the smallest observing test/check for each preserved boundary; label characterization separately from desired-behavior tests.
  6. Define rollback and stop triggers.
- **Outputs:** preservation matrix and verification plan.
- **Stop conditions:** important boundary remains unknown with no safe characterization; authority for intended delta is missing.
- **Escalation conditions:** incompatible behavior/data/protocol, irreversible state, safety/durability uncertainty.
- **Common false positives:** “all tests pass” means all behavior preserved; source code is sole contract; refactoring label guarantees no semantics changed.
- **Source support:** `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>21</sup>** Design by Contract`; `CC: chapters/033-chapter-24-refactoring.md :: #### 24.4 Refactoring Safely`; `CC: chapters/031-chapter-22-developer-testing.md :: #### 22.3 Bag of Testing Tricks`.

### PROC-IMPL-008 — Determine tests or characterization needed

- **Inputs:** preservation matrix, change/defect, current suite, seams/observability, risk.
- **Evidence required:** contract/state/error/boundary inventory; current protection and gaps; reproducible defect if repair.
- **Decision steps:**
  1. Separate desired behavior, current observed behavior, and unknown behavior.
  2. Derive equivalence classes, boundaries, state transitions, data-flow definitions/uses, invalid inputs, and resource/failure paths.
  3. Map each to the lowest stable test level; add integration/system tests where the contract crosses process/component/external boundaries.
  4. Add a failing regression before repair when feasible.
  5. For legacy unknowns, characterize only behavior touched or endangered; label surprising behavior and do not declare it desired.
  6. Validate oracle quality, determinism, and whether tests are coupled to irrelevant implementation.
  7. Use coverage/mutation/test-the-test evidence to find holes, not to replace risk reasoning.
- **Outputs:** test matrix, characterization labels, gaps, confidence.
- **Stop conditions:** no safe seam/oracle for high-risk change; test requires production mutation without authority.
- **Escalation conditions:** conflicting expected behavior; expensive external environment; safety-critical oracle unavailable.
- **Common false positives:** line coverage target; snapshot everything; mock choreography; characterization mistaken for acceptance.
- **Source support:** `CC: chapters/031-chapter-22-developer-testing.md :: #### 22.3 Bag of Testing Tricks`; `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Testing Against Contract`; `PP: chapters/013-chapter-8-pragmatic-projects.md :: #### Testing the Tests`.

### PROC-IMPL-009 — Diagnose and repair a defect

- **Inputs:** report, expected contract, environment/data, logs, source/history/tests.
- **Evidence required:** stable reproduction or explicit non-reproduction evidence; hypotheses; first incorrect state/event; root-cause chain; regression oracle.
- **Decision steps:**
  1. Reproduce with one controlled command and record expected/actual.
  2. Minimize input/environment and stabilize frequency.
  3. Generate competing hypotheses across input, state, code, dependency, and environment.
  4. Choose discriminating instrumentation/checks; avoid editing multiple causes at once.
  5. Trace backward to the earliest divergence and explain how it causes the symptom.
  6. Add a failing regression at the affected contract.
  7. Apply the smallest causal semantic fix, preserving unrelated structure.
  8. Rerun reproduction, relevant suite, and sibling search; remove temporary instrumentation.
- **Outputs:** diagnosis, repair, regression, sibling results, residual uncertainty.
- **Stop conditions:** next diagnostic step risks sensitive/production state; expected behavior disputed; only containment is authorized.
- **Escalation conditions:** dependency/platform defect, data migration, broad architectural cause, safety incident.
- **Common false positives:** suspicious line equals root cause; post-fix pass proves causality; platform blame; symptom suppression.
- **Source support:** `CC: chapters/032-chapter-23-debugging.md :: #### The Scientific Method of Debugging`; `PP: chapters/008-chapter-3-the-basic-tools.md :: ### Debugging Strategies`.

### PROC-IMPL-010 — Decide whether performance work is justified

- **Inputs:** requirement/SLO or complaint, representative workload, environment, correctness oracle, existing benchmark/profile.
- **Evidence required:** metric/target; baseline distribution; bottleneck location; business/operational consequence; semantic constraints.
- **Decision steps:**
  1. Define metric, target, workload, environment, and acceptable variance.
  2. Verify the workload represents the relevant user/operation and the correctness oracle holds.
  3. Establish repeatable baseline; profile/end-to-end measure to locate critical path.
  4. Rank architecture/algorithm/I/O/data-layout/allocation/concurrency/micro-level candidates by expected gain, cost, and reversal.
  5. Change one factor and measure correctness plus performance.
  6. Keep only a material repeatable gain; document trade-off and add regression guard; otherwise revert unless simpler.
- **Outputs:** no-action or optimization recommendation; baseline/profile; verified delta; guard.
- **Stop conditions:** no representative benchmark, no semantic oracle, noise exceeds claimed gain, performance target absent and work would add complexity.
- **Escalation conditions:** quality-attribute trade-off, infrastructure spend, public representation/API, concurrency or data model change.
- **Common false positives:** microbenchmark hotspot, one fast run, folklore about operation cost, compiler/hardware assumption, concurrency equals speed.
- **Source support:** `CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.4 Measurement`; `APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance`; `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Algorithm Speed in Practice`.

### PROC-IMPL-011 — Decide when to leave code alone

- **Inputs:** proposed cleanup/refactor, current task, change/defect/test/history evidence, ownership and authority.
- **Evidence required:** demonstrated pressure and expected improvement; preservation surface; scope/reversal cost.
- **Decision steps:**
  1. State the concrete harm: change amplification, defect, duplicated knowledge, obscured invariant, test blockage, or reader cost.
  2. Determine whether the current authorized task touches that harm and whether it is recurring or consequential.
  3. Check generated/vendored status, churn/history, characterization, operational consequence, and owner.
  4. Sketch the smallest improvement and its new interfaces/risks.
  5. Leave code alone when harm is aesthetic/unsupported, code is stable, protection is weak relative to consequence, or scope/authority is absent.
  6. Record a proposal only if evidence is useful; avoid backlog noise from mere taste.
- **Outputs:** leave/propose/refactor decision and evidence/revisit trigger.
- **Stop conditions:** semantic behavior unknown and change is not required; no authority.
- **Escalation conditions:** latent safety/security risk, unavoidable blocker to authorized work.
- **Common false positives:** file age/size, unfamiliar style, high churn caused by active product evolution rather than poor design, broken-window rhetoric.
- **Source support:** `CC: chapters/033-chapter-24-refactoring.md :: #### Reasons Not to Refactor`; `CC: chapters/033-chapter-24-refactoring.md :: #### Bad Times to Refactor`; `APOSD: chapters/021-16-modifying-existing-code.md :: # 16: Modifying Existing Code`; tension with `PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ## **<sup>2</sup>** Software Entropy`.

### PROC-IMPL-012 — Decide whether to stop and escalate

- **Inputs:** next action, authority, evidence, preservation matrix, reversibility, risk owner.
- **Evidence required:** explicit task scope; affected contracts/state; verification and rollback; missing decision owner.
- **Decision steps:**
  1. Classify the next action as observation, diagnosis, recommendation, selection, execution, verification, or acceptance.
  2. Confirm the task grants that level and affected scope.
  3. Check whether action is reversible, evidence-backed, and verifiable.
  4. Seek a smaller safe observation/experiment if it can resolve uncertainty without new authority.
  5. Stop when action requires unauthorized semantics/architecture/external effects, risks irrecoverable state, or lacks credible preservation.
  6. Escalate with the exact decision, alternatives, evidence, recommendation, consequence, and safe default.
- **Outputs:** proceed/propose/stop; precise escalation packet.
- **Stop conditions:** as above; stop is the output, not failure.
- **Escalation conditions:** human/product/architecture/operations acceptance or new authority is required.
- **Common false positives:** asking approval for every local implementation detail; vague “need clarification” without evidence; continuing because tests pass despite authority gap.
- **Source support:** `PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Take Responsibility`; `CC: chapters/038-chapter-28-managing-construction.md :: #### Requirements and Design Changes`.

### PROC-IMPL-013 — Review comments and names

- **Inputs:** changed names/comments and governed code/API; repository and language conventions; intended readers.
- **Evidence required:** actual semantics/effects; scope; domain vocabulary; information code cannot express; compatibility constraints.
- **Decision steps:**
  1. Verify name matches all outputs/side effects and distinguishes relevant domain concepts/units.
  2. Check repository/language convention and scope-appropriate brevity.
  3. If naming is awkward, inspect cohesion and representation before merely lengthening the name.
  4. Classify each comment as contract, intent/rationale, invariant/ownership/unit, summary, marker, narration, or stale.
  5. Improve code for narration/obscurity; retain or add only non-obvious authoritative information close to its subject.
  6. Check compatibility for public/reflected/serialized names and one-authority documentation.
- **Outputs:** accepted names/comments; design issues; migration/escalation if compatibility affected.
- **Stop conditions:** intended semantics or rationale unknown; do not invent documentation.
- **Escalation conditions:** public rename, protocol/schema key, repository-wide vocabulary change.
- **Common false positives:** long always clearer; comment always a failure; every routine needs prose; repository idiom is universally obvious.
- **Source support:** `APOSD: chapters/019-14-choosing-names.md :: # 14: Choosing Names`; `APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code`; `CC: chapters/043-chapter-32-self-documenting-code.md :: #### 32.4 Keys to Effective Comments`.

### PROC-IMPL-014 — Decide whether concurrency is justified

- **Inputs:** workload and target, sequential dependency graph, state/resources, runtime/platform, failure/lifecycle requirements.
- **Evidence required:** actual latency/throughput/responsiveness/isolation driver; operations that are semantically independent; resource budget; verification tools.
- **Decision steps:**
  1. Separate required causal order from accidental implementation order.
  2. Measure or establish the user/quality need the sequential design misses.
  3. Compare sequential, asynchronous, parallel, and batched alternatives including overhead and failure complexity.
  4. Define ownership of shared state, task/resource lifecycle, cancellation, backpressure, retry, errors, and shutdown.
  5. Bound concurrency and choose language-idiomatic enforcement.
  6. Test invariants deterministically; use race/stress/load evidence; observe resource caps and failure.
  7. Reject if benefit is speculative or lifecycle cannot be made explicit.
- **Outputs:** sequential/concurrent decision, model, bounds, tests/observability.
- **Stop conditions:** ordering/durability semantics unknown; resource budget absent; platform concurrency behavior unverified.
- **Escalation conditions:** distributed consistency, public ordering guarantee, capacity/SLO trade-off.
- **Common false positives:** tasks look independent but share invariant; async hides blocking; more workers always faster; no reproduced race means safe.
- **Source support:** `PP: chapters/010-chapter-5-bend-or-break.md :: ## **<sup>28</sup>** Temporal Coupling`; `PP: chapters/010-chapter-5-bend-or-break.md :: ### Design for Concurrency`; bounded by `APOSD: chapters/026-21-decide-what-matters.md :: # 21: Decide What Matters`.

## Evaluation-rubric contributions

Score each dimension `0 = absent/unsafe`, `1 = asserted but weakly evidenced`, `2 = adequate and evidenced`, `3 = unusually strong and proportionate`. A blocker exists independently of total score when authority, preservation, or correctness is violated.

### Coding-agent plan rubric

| Dimension | A score of 2 requires |
|---|---|
| Outcome and authority | Observable outcome, change type, granted scope, and explicit non-goals. |
| Repository grounding | Relevant instructions, analogous paths, conventions, owners, and accepted architecture cited. |
| Uncertainty control | Unknowns ranked; high-risk assumption has a discriminating probe or escalation. |
| Placement/design | Ownership/invariants/callers support placement; consequential alternatives compared. |
| Preservation | Behavior/API/data/error/resource/operational boundaries inventoried. |
| Slicing | Small dependency- or risk-ordered increments, each buildable/testable/reversible. |
| Verification | Contract/boundary/failure tests and repository gates mapped to slices. |
| Stop discipline | Concrete stop, rollback, and escalation conditions. |

### Implementation rubric

| Dimension | A score of 2 requires |
|---|---|
| Correctness | Meets authorized contract including invalid/boundary states. |
| Cohesion and placement | Behavior lives with owned knowledge/invariants and avoids unrelated policy. |
| Interface quality | Simple common case; explicit meaning/effects/errors/ownership; no accidental leakage. |
| Local reasoning | Obvious control/data flow, bounded state, precise names, minimal hidden sequencing. |
| Abstraction discipline | Every new indirection hides demonstrated complexity; deliberate duplication is justified. |
| Failure/resource safety | Defined failure semantics and cleanup/lifecycle across every exit. |
| Repository fit | Language/repository idiom, generated/vendor boundaries, and architecture honored. |
| Protection | Tests cover contract, boundaries, failures, and regression; comments preserve non-obvious knowledge. |
| Scope/reviewability | Diff contains one coherent authorized purpose and avoids drive-by churn. |

### Repair-plan rubric

| Dimension | A score of 2 requires |
|---|---|
| Reproduction | Stable command/input/environment or explicit non-reproduction evidence. |
| Hypotheses | Competing causal explanations and discriminating checks. |
| Localization | First incorrect state/event, not just final symptom. |
| Root cause | Causal explanation connecting defect to observed behavior. |
| Repair boundary | Smallest semantic change; structural work separated. |
| Regression | Failing-before/passing-after contract test where feasible. |
| Sibling and residual risk | Related instances searched; uncertainty and containment stated. |

### Performance-recommendation rubric

| Dimension | A score of 2 requires |
|---|---|
| Driver | Explicit metric/target and consequence. |
| Benchmark validity | Representative workload/environment, warmup/variance controls, correctness oracle. |
| Bottleneck evidence | Profile or equivalent localization identifies critical path. |
| Intervention level | Algorithm/architecture/data/I/O considered before micro-tuning. |
| Semantic preservation | Precision/order/errors/resources/durability checked. |
| Result | Repeatable material before/after gain and cost trade-off. |
| Regression/retirement | Guard exists; opaque optimization can be removed if benefit disappears. |

### Review and authority-discipline rubric

| Dimension | A score of 2 requires |
|---|---|
| Finding evidence | Concrete locator, contract, causal path or reproducible consequence. |
| Classification | Blocker/defect/risk/suggestion/preference separated. |
| Proportionality | Severity reflects likelihood, consequence, confidence, and task risk. |
| Repository fit | Accepted conventions and architecture outrank reviewer taste. |
| Scope | No unrelated cleanup or silent architecture/product redefinition. |
| Authority | Observation, recommendation, execution, verification, and acceptance are not conflated. |
| Uncertainty | Unknowns and needed decisions are explicit; recommendations do not masquerade as facts. |

## Graph candidates

This section is an additive canonical-graph extraction. It does not replace the concept records, conflict registry, or complete coverage ledger. Node kinds use the requested controlled vocabulary. `provenance_relation` describes how a source formulation relates to the candidate canonical node: `direct_support`, `corroboration`, `refinement`, or `derived_inference`. Derived inference is used sparingly and never presented as an author's direct claim.

### Candidate nodes

#### NODE-IMPL-001

```yaml
id: NODE-IMPL-001
label: Evidence before intervention
kind: principle
source_formulations:
  - source: CC
    formulation: Construction should not proceed blindly when the problem, requirements, architecture, quality goals, and major construction practices needed to manage risk are unresolved.
    locator: "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### cc2e.com/0386 Checklist: Upstream Prerequisites"
    provenance_relation: direct_support
  - source: PP
    formulation: Responsible practitioners accept, decline, or renegotiate work based on what they know, explain risks and alternatives, and do not excuse unsupported outcomes.
    locator: "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Take Responsibility"
    provenance_relation: refinement
  - source: APOSD
    formulation: Important design choices should be compared and judged by their consequences for callers and complexity rather than accepted as the first idea.
    locator: "APOSD: chapters/016-11-design-it-twice.md :: # 11: Design it Twice"
    provenance_relation: corroboration
```

#### NODE-IMPL-002

```yaml
id: NODE-IMPL-002
label: Repository contract supremacy
kind: constraint
source_formulations:
  - source: CC
    formulation: Construction practices and conventions must be chosen for the project, language, architecture, technology maturity, and quality goals; no one practice set fits every project.
    locator: "CC: chapters/009-chapter-4-key-construction-decisions.md :: #### 4.4 Selection of Major Construction Practices"
    provenance_relation: direct_support
  - source: PP
    formulation: The tips form a contextual repertoire and the practitioner must adapt them rather than assume one universal best solution.
    locator: "PP: chapters/004-preface.md :: # Preface"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Existing consistency has cognitive value; change a convention only when the improvement is significant enough to justify migration cost.
    locator: "APOSD: chapters/022-17-consistency.md :: # 17: Consistency"
    provenance_relation: refinement
```

#### NODE-IMPL-003

```yaml
id: NODE-IMPL-003
label: Complexity minimization
kind: principle
source_formulations:
  - source: CC
    formulation: The primary technical imperative is managing complexity by limiting essential complexity in view and preventing accidental complexity from proliferating.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Software's Primary Technical Imperative: Managing Complexity"
    provenance_relation: direct_support
  - source: APOSD
    formulation: Complexity is whatever makes a system hard to understand or modify and is created by dependencies and obscurity.
    locator: "APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity"
    provenance_relation: refinement
  - source: PP
    formulation: Orthogonality and DRY reduce the amount of coupled knowledge and coordinated change a developer must manage.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>8</sup>** Orthogonality"
    provenance_relation: corroboration
```

#### NODE-IMPL-004

```yaml
id: NODE-IMPL-004
label: Change amplification
kind: smell
source_formulations:
  - source: APOSD
    formulation: A seemingly simple change requiring edits in many places is a primary symptom of complexity.
    locator: "APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity"
    provenance_relation: direct_support
  - source: PP
    formulation: Nonorthogonal design and duplicated knowledge cause one conceptual change to ripple through multiple components or representations.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Living with Orthogonality"
    provenance_relation: corroboration
  - source: CC
    formulation: Information hiding, central points of control, and anticipated change isolation aim to keep modifications localized.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Identify Areas Likely to Change"
    provenance_relation: corroboration
```

#### NODE-IMPL-005

```yaml
id: NODE-IMPL-005
label: Cognitive load
kind: smell
source_formulations:
  - source: APOSD
    formulation: The amount of knowledge a developer must hold to complete a task is a primary complexity symptom, weighted by how often the code is touched.
    locator: "APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity"
    provenance_relation: direct_support
  - source: CC
    formulation: Design should let a developer safely focus on one piece without mentally juggling the whole program.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Importance of Managing Complexity"
    provenance_relation: corroboration
  - source: PP
    formulation: Orthogonal components and deliberate code reduce the unrelated facts and assumptions required for a local change.
    locator: "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### How to Program Deliberately"
    provenance_relation: refinement
```

#### NODE-IMPL-006

```yaml
id: NODE-IMPL-006
label: Unknown unknowns
kind: smell
source_formulations:
  - source: APOSD
    formulation: The worst complexity appears when needed knowledge or dependencies are not obvious enough for a developer to know what to inspect.
    locator: "APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity"
    provenance_relation: direct_support
  - source: CC
    formulation: Hidden ordering, global data, unexpected coupling, and unrecorded interface assumptions create defects because required dependencies are not locally visible.
    locator: "CC: chapters/020-chapter-13-unusual-data-types.md :: #### Common Problems with Global Data"
    provenance_relation: corroboration
  - source: PP
    formulation: Programming by coincidence fails when code depends on undocumented accidents of implementation or context.
    locator: "PP: chapters/011-chapter-6-while-you-are-coding.md :: ## **<sup>31</sup>** Programming by Coincidence"
    provenance_relation: refinement
```

#### NODE-IMPL-007

```yaml
id: NODE-IMPL-007
label: Local reasoning
kind: principle
source_formulations:
  - source: CC
    formulation: Organize subsystems, classes, routines, variables, and control flow so a developer can understand one piece with minimal knowledge of the rest.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### How to Attack Complexity"
    provenance_relation: direct_support
  - source: PP
    formulation: Orthogonal components can be changed, tested, and reused with limited effect on others.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Benefits of Orthogonality"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Deep modules and information hiding reduce the knowledge callers need and concentrate complexity behind a simple interface.
    locator: "APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep"
    provenance_relation: refinement
```

#### NODE-IMPL-008

```yaml
id: NODE-IMPL-008
label: Information hiding
kind: principle
source_formulations:
  - source: APOSD
    formulation: A module should conceal design decisions and representations so callers do not depend on them; private declarations alone do not establish hiding.
    locator: "APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)"
    provenance_relation: direct_support
  - source: CC
    formulation: Ask what secrets a module can hide and centralize likely-to-change decisions behind stable abstractions.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Hide Secrets (Information Hiding)"
    provenance_relation: corroboration
  - source: PP
    formulation: Encapsulate knowledge and isolate third-party or volatile details so changes do not propagate.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Design"
    provenance_relation: corroboration
```

#### NODE-IMPL-009

```yaml
id: NODE-IMPL-009
label: Information leakage
kind: smell
source_formulations:
  - source: APOSD
    formulation: The same design knowledge appearing in multiple modules, including temporal decomposition that exposes operation order, signals leakage.
    locator: "APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)"
    provenance_relation: direct_support
  - source: PP
    formulation: Multiple representations of one rule or assumption violate DRY even when their syntax differs.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication"
    provenance_relation: corroboration
  - source: CC
    formulation: Globals, exposed implementation, repeated sequences, and scattered control points make changes depend on nonlocal knowledge.
    locator: "CC: chapters/020-chapter-13-unusual-data-types.md :: #### Common Problems with Global Data"
    provenance_relation: corroboration
```

#### NODE-IMPL-010

```yaml
id: NODE-IMPL-010
label: Deep module
kind: heuristic
source_formulations:
  - source: APOSD
    formulation: Prefer modules whose simple common-case interface hides substantial coherent functionality and difficult decisions.
    locator: "APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep"
    provenance_relation: direct_support
  - source: CC
    formulation: A routine or class should create an understandable abstraction, hide details, and reduce complexity; its value is not determined by line count.
    locator: "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine"
    provenance_relation: refinement
  - source: PP
    formulation: A well-encapsulated orthogonal component provides useful service while limiting how much callers know about its implementation.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Design"
    provenance_relation: corroboration
```

#### NODE-IMPL-011

```yaml
id: NODE-IMPL-011
label: Shallow module
kind: smell
source_formulations:
  - source: APOSD
    formulation: A module whose interface is nearly as complex as the functionality it provides adds little leverage; pass-through methods and decorators are common forms.
    locator: "APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction"
    provenance_relation: direct_support
  - source: CC
    formulation: Interfaces are defect-prone, so routine extraction should have a valid abstractive purpose rather than merely making routines small.
    locator: "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.4 How Long Can a Routine Be?"
    provenance_relation: corroboration
  - source: PP
    formulation: Law-of-Demeter wrappers can impose runtime and interface overhead, a cost the source explicitly acknowledges.
    locator: "PP: chapters/010-chapter-5-bend-or-break.md :: ### Does It Really Make a Difference?"
    provenance_relation: refinement
```

#### NODE-IMPL-012

```yaml
id: NODE-IMPL-012
label: Earned abstraction
kind: proof-obligation
source_formulations:
  - source: CC
    formulation: A routine/class is warranted when it reduces complexity, introduces an abstraction, hides knowledge/sequencing, centralizes control, or serves another concrete design purpose.
    locator: "CC: chapters/013-chapter-7-high-quality-routines.md :: #### Summary of Reasons to Create a Routine"
    provenance_relation: direct_support
  - source: APOSD
    formulation: The new interface must hide enough coherent complexity to be deeper than the direct implementation and must not merely forward calls.
    locator: "APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep"
    provenance_relation: refinement
  - source: PP
    formulation: Decoupling or reuse should isolate actual knowledge/variation, not create an abstraction for its own sake.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Design"
    provenance_relation: corroboration
```

#### NODE-IMPL-013

```yaml
id: NODE-IMPL-013
label: Knowledge duplication
kind: smell
source_formulations:
  - source: PP
    formulation: Two or more authoritative representations of the same knowledge create maintenance inconsistency; generated derivations and deliberate caches must preserve one authority.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication"
    provenance_relation: direct_support
  - source: APOSD
    formulation: Repeated nontrivial knowledge can justify consolidation, but repeated short mechanics do not automatically justify another interface.
    locator: "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
    provenance_relation: refinement
  - source: CC
    formulation: Shared code can reduce inconsistent fixes and provide one control point, although its general “duplication implies decomposition error” wording needs the semantic qualification above.
    locator: "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine"
    provenance_relation: corroboration
```

#### NODE-IMPL-014

```yaml
id: NODE-IMPL-014
label: Speculative generality
kind: anti-pattern
source_formulations:
  - source: APOSD
    formulation: Make the module general enough for current needs and a simpler interface, but do not add features or mechanisms for hypothetical futures.
    locator: "APOSD: chapters/011-6-general-purpose-modules-are-deeper.md :: # 6: General-Purpose Modules are Deeper"
    provenance_relation: direct_support
  - source: CC
    formulation: Anticipating change and reuse can help, but overengineering and premature features must be checked explicitly.
    locator: "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Overengineering"
    provenance_relation: refinement
  - source: PP
    formulation: Preserve reversibility around volatile choices, but this does not require implementing every possible option now.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Reversibility"
    provenance_relation: corroboration
```

#### NODE-IMPL-015

```yaml
id: NODE-IMPL-015
label: Design alternatives
kind: transformation
source_formulations:
  - source: APOSD
    formulation: Sketch substantially different interfaces or implementations and compare caller ease, simplicity, generality, performance, and implementation cost before selecting.
    locator: "APOSD: chapters/016-11-design-it-twice.md :: # 11: Design it Twice"
    provenance_relation: direct_support
  - source: CC
    formulation: Good design is iterative and improves by exploring multiple decompositions, top-down and bottom-up views, prototypes, and peer review.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Iterate"
    provenance_relation: corroboration
  - source: PP
    formulation: Prototypes and tracer bullets can test alternative assumptions and integrations before a large commitment.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>11</sup>** Prototypes and Post-it Notes"
    provenance_relation: refinement
```

#### NODE-IMPL-016

```yaml
id: NODE-IMPL-016
label: Interface contract
kind: proof-obligation
source_formulations:
  - source: PP
    formulation: Preconditions, postconditions, and invariants define what callers and implementations owe each other without prescribing implementation.
    locator: "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>21</sup>** Design by Contract"
    provenance_relation: direct_support
  - source: CC
    formulation: Document and preferably enforce parameter direction, units, ranges, invalid values, effects, and class/routine abstraction assumptions.
    locator: "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.5 How to Use Routine Parameters"
    provenance_relation: corroboration
  - source: APOSD
    formulation: A module's informal interface includes every fact callers must know, so comments must capture non-obvious semantics beyond the signature.
    locator: "APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code"
    provenance_relation: refinement
```

#### NODE-IMPL-017

```yaml
id: NODE-IMPL-017
label: Explicit invariant
kind: proof-obligation
source_formulations:
  - source: PP
    formulation: State the semantic and loop conditions that must remain true; use contracts and assertions to detect programmer violations near their cause.
    locator: "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Other Uses of Invariants"
    provenance_relation: direct_support
  - source: CC
    formulation: Assertions should document and check conditions believed impossible, while ordinary bad input follows the defined error policy.
    locator: "CC: chapters/014-chapter-8-defensive-programming.md :: #### Guidelines for Using Assertions"
    provenance_relation: refinement
  - source: APOSD
    formulation: Non-obvious invariants and cross-module constraints are important design information that must be explicit and discoverable.
    locator: "APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code"
    provenance_relation: corroboration
```

#### NODE-IMPL-018

```yaml
id: NODE-IMPL-018
label: Error-surface reduction
kind: pattern
source_formulations:
  - source: APOSD
    formulation: Reduce the number of places that handle errors by defining natural total semantics, masking recoverable low-level failures, or aggregating failures at a useful level.
    locator: "APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence"
    provenance_relation: direct_support
  - source: CC
    formulation: Choose a consistent high-level error policy among neutral values, substitution, retry, propagation, logging, shutdown, or other techniques based on robustness/correctness needs.
    locator: "CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.3 Error-Handling Techniques"
    provenance_relation: refinement
  - source: PP
    formulation: Reserve exception mechanisms for failures outside the operation's normal semantic flow and use ordinary results when callers routinely decide on the outcome.
    locator: "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>24</sup>** When to Use Exceptions"
    provenance_relation: refinement
```

#### NODE-IMPL-019

```yaml
id: NODE-IMPL-019
label: Fail fast versus recover
kind: tradeoff
source_formulations:
  - source: PP
    formulation: When an impossible state makes continued execution untrustworthy, stop before corruption compounds; a dead program is preferable to damaged data.
    locator: "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Crash, Don't Trash"
    provenance_relation: direct_support
  - source: CC
    formulation: Robustness may require continued service while correctness may require refusing uncertain results; the choice is a high-level design policy shaped by product context.
    locator: "CC: chapters/014-chapter-8-defensive-programming.md :: #### Robustness vs. Correctness"
    provenance_relation: refinement
  - source: APOSD
    formulation: Crashing is one way to reduce propagated error complexity, but it is appropriate only when errors are rare and the deployment context can tolerate termination.
    locator: "APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence"
    provenance_relation: refinement
```

#### NODE-IMPL-020

```yaml
id: NODE-IMPL-020
label: Resource ownership
kind: proof-obligation
source_formulations:
  - source: PP
    formulation: The party that acquires a resource should normally own balancing it; nested acquisition releases in reverse order, and shared resources need consistent acquisition order.
    locator: "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>25</sup>** How to Balance Resources"
    provenance_relation: direct_support
  - source: CC
    formulation: Resource management and cleanup behavior must be designed at architecture and routine/error boundaries rather than left to happy-path code.
    locator: "CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Resource Management"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Ownership and side effects are part of non-obvious interface information callers must understand.
    locator: "APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code"
    provenance_relation: refinement
```

#### NODE-IMPL-021

```yaml
id: NODE-IMPL-021
label: Reader-oriented obviousness
kind: principle
source_formulations:
  - source: APOSD
    formulation: Code is obvious when a reader can quickly infer its behavior and context without surprises; reader review, not writer familiarity, is the test.
    locator: "APOSD: chapters/023-18-code-should-be-obvious.md :: # 18: Code Should be Obvious"
    provenance_relation: direct_support
  - source: CC
    formulation: Programs are written for people first and computers second, so names, control, layout, data, and abstraction should optimize human understanding.
    locator: "CC: chapters/045-chapter-34-themes-in-software-craftsmanship.md :: #### 34.3 Write Programs for People First, Computers Second"
    provenance_relation: corroboration
  - source: PP
    formulation: Communication must be audience-aware, and code/documentation should make intent and expectations clear to their consumers.
    locator: "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Know Your Audience"
    provenance_relation: corroboration
```

#### NODE-IMPL-022

```yaml
id: NODE-IMPL-022
label: Semantic naming
kind: heuristic
source_formulations:
  - source: APOSD
    formulation: Choose names that create precise mental images, distinguish types/domains, and use consistent vocabulary; hard-to-name code may reveal weak design.
    locator: "APOSD: chapters/019-14-choosing-names.md :: # 14: Choosing Names"
    provenance_relation: direct_support
  - source: CC
    formulation: Names should express the problem-domain meaning and all routine effects, with length and detail calibrated to scope and repository convention.
    locator: "CC: chapters/018-chapter-11-the-power-of-variable-names.md :: #### The Most Important Naming Consideration"
    provenance_relation: corroboration
  - source: PP
    formulation: Maintain a shared glossary so requirements, code, tests, and conversation use one domain vocabulary.
    locator: "PP: chapters/012-chapter-7-before-the-project.md :: ### Maintain a Glossary"
    provenance_relation: refinement
```

#### NODE-IMPL-023

```yaml
id: NODE-IMPL-023
label: Non-obvious commentary
kind: heuristic
source_formulations:
  - source: APOSD
    formulation: Comments should preserve abstraction, interface obligations, rationale, invariants, units, ownership, side effects, and other information not obvious from code.
    locator: "APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code"
    provenance_relation: direct_support
  - source: CC
    formulation: Improve code before explaining poor mechanics, then comment intent, summaries, markers, and information code cannot express; avoid repeating statements.
    locator: "CC: chapters/043-chapter-32-self-documenting-code.md :: #### 32.4 Keys to Effective Comments"
    provenance_relation: refinement
  - source: PP
    formulation: Comments should explain why, purpose, and trade-offs and should derive documents from authoritative sources where possible.
    locator: "PP: chapters/013-chapter-8-pragmatic-projects.md :: ### Comments in Code"
    provenance_relation: corroboration
```

#### NODE-IMPL-024

```yaml
id: NODE-IMPL-024
label: Repository consistency
kind: constraint
source_formulations:
  - source: APOSD
    formulation: Consistent naming, style, patterns, and interfaces let readers reuse prior knowledge; document, automate, and review conventions before changing them.
    locator: "APOSD: chapters/022-17-consistency.md :: # 17: Consistency"
    provenance_relation: direct_support
  - source: CC
    formulation: Project conventions remove arbitrary variation and align low-level implementation with architecture; formatting debates should not become religion.
    locator: "CC: chapters/009-chapter-4-key-construction-decisions.md :: #### 4.2 Programming Conventions"
    provenance_relation: corroboration
  - source: PP
    formulation: Teams should maintain shared practice and vocabulary, while deliberate improvement prevents harmful drift from becoming normal.
    locator: "PP: chapters/013-chapter-8-pragmatic-projects.md :: ## **<sup>41</sup>** Pragmatic Teams"
    provenance_relation: refinement
```

#### NODE-IMPL-025

```yaml
id: NODE-IMPL-025
label: Disposable prototype
kind: pattern
source_formulations:
  - source: PP
    formulation: Build the minimum throwaway artifact needed to answer a targeted question about architecture, tool, data, performance, or interface, and communicate that it will be discarded.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### How Not to Use Prototypes"
    provenance_relation: direct_support
  - source: CC
    formulation: Experimental prototypes should target risky or unfamiliar design questions and use only enough code to resolve them.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Experimental Prototyping"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Exploring multiple designs cheaply before commitment serves the same uncertainty-reduction purpose, though the source does not define prototype disposal as a named pattern.
    locator: "APOSD: chapters/016-11-design-it-twice.md :: # 11: Design it Twice"
    provenance_relation: derived_inference
```

#### NODE-IMPL-026

```yaml
id: NODE-IMPL-026
label: Tracer bullet
kind: pattern
source_formulations:
  - source: PP
    formulation: Build a lean production-quality end-to-end path that exercises major boundaries, retain it, and adjust aim through feedback.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>10</sup>** Tracer Bullets"
    provenance_relation: direct_support
  - source: CC
    formulation: Risk-oriented and incremental integration expose boundary problems early and keep failures attributable.
    locator: "CC: chapters/039-chapter-29-integration.md :: #### Risk-Oriented Integration"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Strategic programming can proceed incrementally if each increment builds coherent abstractions rather than tactical feature patches.
    locator: "APOSD: chapters/008-3-working-code-isnt-enough.md :: # 3: Working Code Isn’t Enough"
    provenance_relation: refinement
```

#### NODE-IMPL-027

```yaml
id: NODE-IMPL-027
label: Contract-derived protection
kind: proof-obligation
source_formulations:
  - source: CC
    formulation: Tests should be derived from control/data paths, equivalence classes, boundaries, good/bad inputs, state combinations, and error-prone areas, not just from lines executed.
    locator: "CC: chapters/031-chapter-22-developer-testing.md :: #### 22.3 Bag of Testing Tricks"
    provenance_relation: direct_support
  - source: PP
    formulation: Test units against their contracts, include integration, validation, resource/error/recovery/performance concerns, automate regressions, and test the tests.
    locator: "PP: chapters/013-chapter-8-pragmatic-projects.md :: ### What to Test"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Unit tests create a safety net for structural change, and a reproducible defect should receive a failing test before repair.
    locator: "APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends"
    provenance_relation: refinement
```

#### NODE-IMPL-028

```yaml
id: NODE-IMPL-028
label: Coverage-as-adequacy
kind: anti-pattern
source_formulations:
  - source: CC
    formulation: Coverage tools show what executed but testing remains incomplete and must be combined with boundary, data-flow, error, review, and other quality techniques.
    locator: "CC: chapters/031-chapter-22-developer-testing.md :: #### Coverage Monitors"
    provenance_relation: direct_support
  - source: PP
    formulation: Thorough testing concerns states, contracts, errors, data, and the validity of tests themselves; line execution is not a sufficient oracle.
    locator: "PP: chapters/013-chapter-8-pragmatic-projects.md :: ### Testing Thoroughly"
    provenance_relation: corroboration
```

#### NODE-IMPL-029

```yaml
id: NODE-IMPL-029
label: Scientific debugging loop
kind: pattern
source_formulations:
  - source: CC
    formulation: Stabilize the failure, gather data, form and test hypotheses, narrow and locate the source, understand root cause, then repair carefully and verify.
    locator: "CC: chapters/032-chapter-23-debugging.md :: #### The Scientific Method of Debugging"
    provenance_relation: direct_support
  - source: PP
    formulation: Reproduce, visualize/trace, explain, eliminate hypotheses, question assumptions, and treat surprise as evidence that the mental model is wrong.
    locator: "PP: chapters/008-chapter-3-the-basic-tools.md :: ### Debugging Strategies"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Obvious code and explicit invariants reduce debugging uncertainty, but the source does not present a full debugging procedure.
    locator: "APOSD: chapters/023-18-code-should-be-obvious.md :: # 18: Code Should be Obvious"
    provenance_relation: derived_inference
```

#### NODE-IMPL-030

```yaml
id: NODE-IMPL-030
label: Semantic-structural separation
kind: constraint
source_formulations:
  - source: PP
    formulation: Refactor in deliberate small steps with tests and avoid combining refactoring with feature work so failures remain attributable.
    locator: "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### How Do You Refactor?"
    provenance_relation: direct_support
  - source: CC
    formulation: Safe refactoring preserves behavior through small transformations and verification; bad timing and insufficient protection are reasons not to proceed.
    locator: "CC: chapters/033-chapter-24-refactoring.md :: #### 24.4 Refactoring Safely"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Strategic improvement while modifying code should not collapse into tactical patches, but the source does not explicitly define commit/slice separation.
    locator: "APOSD: chapters/021-16-modifying-existing-code.md :: # 16: Modifying Existing Code"
    provenance_relation: refinement
```

#### NODE-IMPL-031

```yaml
id: NODE-IMPL-031
label: Measured optimization
kind: proof-obligation
source_formulations:
  - source: CC
    formulation: Establish performance requirements, measure/profile, optimize the actual hotspot iteratively, and compare before/after because low-level results are environment-specific.
    locator: "CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.4 Measurement"
    provenance_relation: direct_support
  - source: APOSD
    formulation: Use naturally efficient design, measure the critical path, preserve a baseline, and remove changes that do not deliver measurable benefit unless they simplify code.
    locator: "APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance"
    provenance_relation: corroboration
  - source: PP
    formulation: Estimate algorithmic growth, test with target data, and remember that setup cost and dataset size can reverse theoretical expectations.
    locator: "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Algorithm Speed in Practice"
    provenance_relation: refinement
```

#### NODE-IMPL-032

```yaml
id: NODE-IMPL-032
label: Performance specialization
kind: tradeoff
source_formulations:
  - source: CC
    formulation: Hot code may justify caching, data transformation, loop specialization, inlining, or low-level recoding, but each technique is contingent on measurement and safeguards.
    locator: "CC: chapters/035-chapter-26-code-tuning-techniques.md :: #### 26.7 The More Things Change, the More They Stay the Same"
    provenance_relation: direct_support
  - source: APOSD
    formulation: Restructure only the measured critical path and move exceptional cases off it while preserving simpler abstractions elsewhere.
    locator: "APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance"
    provenance_relation: refinement
  - source: PP
    formulation: Performance can be a legitimate reason to compromise decoupling or duplicate cached state, but costs and consistency must be explicit.
    locator: "PP: chapters/010-chapter-5-bend-or-break.md :: ### Does It Really Make a Difference?"
    provenance_relation: corroboration
```

#### NODE-IMPL-033

```yaml
id: NODE-IMPL-033
label: Temporal coupling
kind: smell
source_formulations:
  - source: PP
    formulation: Unnecessary sequencing constraints prevent independent work and can conceal opportunities for asynchronous or parallel execution.
    locator: "PP: chapters/010-chapter-5-bend-or-break.md :: ## **<sup>28</sup>** Temporal Coupling"
    provenance_relation: direct_support
  - source: CC
    formulation: Hidden statement and routine ordering should be made explicit or encapsulated so callers do not reproduce fragile sequences.
    locator: "CC: chapters/022-chapter-14-organizing-straight-line-code.md :: #### 14.1 Statements That Must Be in a Specific Order"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Decomposing by execution order often leaks shared knowledge and should be replaced by information-owning modules where possible.
    locator: "APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)"
    provenance_relation: refinement
```

#### NODE-IMPL-034

```yaml
id: NODE-IMPL-034
label: Concurrency pressure
kind: proof-obligation
source_formulations:
  - source: PP
    formulation: Identify genuine ordering dependencies and design valid object states before exploiting concurrency; the source advocates broad concurrency readiness.
    locator: "PP: chapters/010-chapter-5-bend-or-break.md :: ### Design for Concurrency"
    provenance_relation: direct_support
  - source: CC
    formulation: Performance, resource, correctness, and project context are competing design goals, so a concurrency mechanism must be selected against explicit priorities.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Design Is About Tradeoffs and Priorities"
    provenance_relation: refinement
  - source: APOSD
    formulation: Optimize what matters and avoid making irrelevant details important; applying this to concurrency requires a demonstrated external or measured driver.
    locator: "APOSD: chapters/026-21-decide-what-matters.md :: # 21: Decide What Matters"
    provenance_relation: derived_inference
```

#### NODE-IMPL-035

```yaml
id: NODE-IMPL-035
label: Global mutable state
kind: anti-pattern
source_formulations:
  - source: CC
    formulation: Global data obscures ownership, access order, side effects, and change impact and should be a last resort with mediated access and explicit safeguards.
    locator: "CC: chapters/020-chapter-13-unusual-data-types.md :: #### Use Global Data Only as a Last Resort"
    provenance_relation: direct_support
  - source: PP
    formulation: Globals and shared state undermine orthogonality, testing, and concurrency safety.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Coding"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Broad context objects can become grab-bags and thread hazards even when introduced to reduce pass-through parameters.
    locator: "APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction"
    provenance_relation: refinement
```

#### NODE-IMPL-036

```yaml
id: NODE-IMPL-036
label: Authority discipline
kind: constraint
source_formulations:
  - source: PP
    formulation: Responsibility means being honest about what one can undertake, communicating uncertainty and options, and accepting consequences rather than inventing excuses.
    locator: "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Take Responsibility"
    provenance_relation: direct_support
  - source: CC
    formulation: Requirements, architecture, configuration, and code changes have distinct owners and controls; construction decisions must fit the project's management and change process.
    locator: "CC: chapters/038-chapter-28-managing-construction.md :: #### Requirements and Design Changes"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Deciding what matters requires exposing externally important constraints while hiding irrelevant mechanism; an agent-authority transition model is not explicit in the source.
    locator: "APOSD: chapters/026-21-decide-what-matters.md :: # 21: Decide What Matters"
    provenance_relation: derived_inference
```

#### NODE-IMPL-037

```yaml
id: NODE-IMPL-037
label: Coherent routine extraction
kind: transformation
source_formulations:
  - source: CC
    formulation: Extract code when a named routine reduces complexity, introduces an understandable abstraction, hides a sequence or representation, centralizes knowledge, or isolates a cohesive operation.
    locator: "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine"
    provenance_relation: direct_support
  - source: APOSD
    formulation: Extract only a clean independent subtask or a distinct abstraction; otherwise the new method can add a shallow interface and scatter related knowledge.
    locator: "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
    provenance_relation: refinement
  - source: PP
    formulation: Extraction is useful for one authoritative piece of knowledge, but should not manufacture a common abstraction from unrelated copies.
    locator: "PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication"
    provenance_relation: refinement
```

#### NODE-IMPL-038

```yaml
id: NODE-IMPL-038
label: Arbitrary size threshold
kind: anti-pattern
source_formulations:
  - source: CC
    formulation: Routine length should follow cohesion, nesting, variable/decision burden, and understandability rather than a fixed line limit; empirical thresholds are contextual warnings.
    locator: "CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.4 How Long Can a Routine Be?"
    provenance_relation: direct_support
  - source: APOSD
    formulation: Long methods can be appropriate when their interface is simple and their body remains readable; splitting for length can increase complexity.
    locator: "APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?"
    provenance_relation: corroboration
```

#### NODE-IMPL-039

```yaml
id: NODE-IMPL-039
label: Metadata-driven configuration
kind: pattern
source_formulations:
  - source: PP
    formulation: Keep stable abstractions in code and place volatile policy or details in metadata when this allows controlled behavior changes without code rewrites.
    locator: "PP: chapters/010-chapter-5-bend-or-break.md :: ### Metadata-Driven Applications"
    provenance_relation: direct_support
  - source: CC
    formulation: Binding time and table-driven approaches can move choices from hard-coded control into data, but the representation and access must remain clear.
    locator: "CC: chapters/026-chapter-18-table-driven-methods.md :: ### 18.1 General Considerations in Using Table-Driven Methods"
    provenance_relation: corroboration
  - source: APOSD
    formulation: Exposed configuration can be a pass-through burden; a deep module should often absorb technical choices and offer simple defaults.
    locator: "APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction"
    provenance_relation: refinement
```

#### NODE-IMPL-040

```yaml
id: NODE-IMPL-040
label: Pull complexity downward
kind: heuristic
source_formulations:
  - source: APOSD
    formulation: A module should absorb complexity closely related to its task when doing so simplifies all callers, but must not absorb unrelated caller policy.
    locator: "APOSD: chapters/013-8-pull-complexity-downwards.md :: # 8: Pull Complexity Downwards"
    provenance_relation: direct_support
  - source: CC
    formulation: Hide details and centralize common decisions so callers operate at a higher problem-domain abstraction.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Make Central Points of Control"
    provenance_relation: corroboration
```

#### NODE-IMPL-041

```yaml
id: NODE-IMPL-041
label: Law of Demeter
kind: heuristic
source_formulations:
  - source: PP
    formulation: Limit a method's knowledge to itself, its parameters, created objects, and direct components to reduce structural coupling, while acknowledging wrapper and performance costs.
    locator: "PP: chapters/010-chapter-5-bend-or-break.md :: ### The Law of Demeter for Functions"
    provenance_relation: direct_support
  - source: CC
    formulation: Loose coupling and narrow class interaction support the same locality goal without prescribing an exact traversal rule.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### Keep Coupling Loose"
    provenance_relation: corroboration
```

#### NODE-IMPL-042

```yaml
id: NODE-IMPL-042
label: Direct dependency when indirection hides nothing
kind: heuristic
source_formulations:
  - source: APOSD
    formulation: Eliminate pass-through methods or same-abstraction layers that add an interface without hiding a distinct decision; direct use can be simpler.
    locator: "APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction"
    provenance_relation: direct_support
  - source: PP
    formulation: Demeter-style decoupling has wrapper and runtime costs and may be inappropriate for tightly coupled performance-critical structures.
    locator: "PP: chapters/010-chapter-5-bend-or-break.md :: ### Does It Really Make a Difference?"
    provenance_relation: refinement
```

#### NODE-IMPL-043

```yaml
id: NODE-IMPL-043
label: Test-first feedback
kind: pattern
source_formulations:
  - source: CC
    formulation: Writing tests before code can shorten the feedback loop and clarify expected behavior, but test-last remains a valid contextual choice.
    locator: "CC: chapters/031-chapter-22-developer-testing.md :: #### Test First or Test Last?"
    provenance_relation: direct_support
  - source: PP
    formulation: Unit tests and contract tests are developed alongside code to expose design/testability and preserve behavior.
    locator: "PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Unit Testing"
    provenance_relation: corroboration
  - source: APOSD
    formulation: A failing test should precede a defect repair, but feature-by-feature TDD can become tactical if it replaces broader interface design.
    locator: "APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends"
    provenance_relation: refinement
```

#### NODE-IMPL-044

```yaml
id: NODE-IMPL-044
label: Abstraction design before feature-test sequence
kind: heuristic
source_formulations:
  - source: APOSD
    formulation: For a new shared module, consider the broader abstraction and alternative interfaces before allowing a sequence of feature tests to dictate tactical structure.
    locator: "APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends"
    provenance_relation: direct_support
  - source: CC
    formulation: Design is iterative and should be carried far enough that routine/class responsibilities and implementation are understandable before detailed coding.
    locator: "CC: chapters/011-chapter-5-design-in-construction.md :: #### How Much Design Is Enough?"
    provenance_relation: corroboration
```

#### NODE-IMPL-045

```yaml
id: NODE-IMPL-045
label: Comments-first design probe
kind: transformation
source_formulations:
  - source: APOSD
    formulation: Draft interface and implementation comments before code to expose a complex or incoherent abstraction while it is still cheap to redesign.
    locator: "APOSD: chapters/020-15-write-the-comments-first.md :: # 15: Write The Comments First"
    provenance_relation: direct_support
  - source: CC
    formulation: Intent-level pseudocode and a header contract can guide routine design and then become useful commentary, though other design workflows are also valid.
    locator: "CC: chapters/015-chapter-9-the-pseudocode-programming-process.md :: #### Design the Routine"
    provenance_relation: corroboration
```

#### NODE-IMPL-046

```yaml
id: NODE-IMPL-046
label: Leave stable code alone
kind: constraint
source_formulations:
  - source: CC
    formulation: Do not refactor when the change is not needed, behavior cannot be protected, timing is poor, or replacement is more appropriate; refactoring has explicit contraindications.
    locator: "CC: chapters/033-chapter-24-refactoring.md :: #### Reasons Not to Refactor"
    provenance_relation: direct_support
  - source: APOSD
    formulation: Invest strategically when changing code, but the value comes from reducing actual complexity rather than from aesthetic activity detached from a task.
    locator: "APOSD: chapters/021-16-modifying-existing-code.md :: # 16: Modifying Existing Code"
    provenance_relation: refinement
  - source: PP
    formulation: Know when to stop adding quality or polish once stakeholder needs and trade-offs are met.
    locator: "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Know When to Stop"
    provenance_relation: corroboration
```

#### NODE-IMPL-047

```yaml
id: NODE-IMPL-047
label: Broken window
kind: smell
source_formulations:
  - source: PP
    formulation: Visible uncorrected disorder can normalize further careless change and signal that quality is not protected.
    locator: "PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ## **<sup>2</sup>** Software Entropy"
    provenance_relation: direct_support
  - source: CC
    formulation: Warning signs and deteriorating quality should trigger investigation, but method selection and cleanup must remain contextual.
    locator: "CC: chapters/045-chapter-34-themes-in-software-craftsmanship.md :: #### 34.7 Watch for Falling Rocks"
    provenance_relation: refinement
```

#### NODE-IMPL-048

```yaml
id: NODE-IMPL-048
label: Composition over implementation inheritance
kind: heuristic
source_formulations:
  - source: APOSD
    formulation: Interface inheritance can support multiple implementations, but implementation inheritance leaks state and couples subclasses; composition is generally safer.
    locator: "APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends"
    provenance_relation: direct_support
  - source: CC
    formulation: Prefer containment in most cases and use inheritance only for a genuine is-a relationship that simplifies rather than complicates the design.
    locator: "CC: chapters/012-chapter-6-working-classes.md :: #### Containment (\"has a\" Relationships)"
    provenance_relation: corroboration
```

#### NODE-IMPL-049

```yaml
id: NODE-IMPL-049
label: Configuration is a public interface cost
kind: constraint
source_formulations:
  - source: APOSD
    formulation: Configuration variables passed through layers expose mechanism and add concepts every user must understand; choose simple defaults and contain them when possible.
    locator: "APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction"
    provenance_relation: direct_support
  - source: PP
    formulation: Configuration is justified when policy or volatile detail truly needs independent change and cooperative management.
    locator: "PP: chapters/010-chapter-5-bend-or-break.md :: ### When to Configure"
    provenance_relation: refinement
```

#### NODE-IMPL-050

```yaml
id: NODE-IMPL-050
label: Normal result versus exception
kind: tradeoff
source_formulations:
  - source: PP
    formulation: Use ordinary control/results for routinely expected outcomes and exceptions for conditions that cannot be treated as normal by the operation.
    locator: "PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### What Is Exceptional?"
    provenance_relation: direct_support
  - source: CC
    formulation: Compare exceptions with return/status, neutral value, retry, logging, and containment according to language, caller needs, and error policy.
    locator: "CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.4 Exceptions"
    provenance_relation: refinement
  - source: APOSD
    formulation: Change semantics to remove error cases only when the result remains natural and caller-relevant failure information is not lost.
    locator: "APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence"
    provenance_relation: refinement
```

### Candidate typed edges

Every edge below is directional. `provenance` cites the source formulation that most directly supports the relationship; when the edge is synthesis across sources, it is labeled `derived_inference` and cites both endpoints' supporting locators.

| From | Edge type | To | Provenance and preserved qualification |
|---|---|---|---|
| `NODE-IMPL-001` | `prerequisite_for` | `NODE-IMPL-012` | `direct_support` — an abstraction cannot be earned before its problem/pressure is evidenced. `CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### 3.1 Importance of Prerequisites`; `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine`. |
| `NODE-IMPL-002` | `guards` | `NODE-IMPL-024` | `derived_inference` — repository/project convention determines which consistency is authoritative. `CC: chapters/009-chapter-4-key-construction-decisions.md :: #### 4.2 Programming Conventions`; `APOSD: chapters/022-17-consistency.md :: # 17: Consistency`. |
| `NODE-IMPL-036` | `guards` | `NODE-IMPL-001` | `refinement` — available evidence does not grant execution/acceptance authority. `PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ### Take Responsibility`; `CC: chapters/038-chapter-28-managing-construction.md :: #### Requirements and Design Changes`. |
| `NODE-IMPL-004` | `indicates` | `NODE-IMPL-003` | `direct_support` — change amplification is a primary complexity symptom. `APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity`. |
| `NODE-IMPL-005` | `indicates` | `NODE-IMPL-003` | `direct_support` — cognitive load is a primary complexity symptom. `APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity`. |
| `NODE-IMPL-006` | `indicates` | `NODE-IMPL-003` | `direct_support` — unknown unknowns are a primary complexity symptom. `APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity`. |
| `NODE-IMPL-007` | `mitigates` | `NODE-IMPL-005` | `corroboration` — locally understandable units reduce mental juggling. `CC: chapters/011-chapter-5-design-in-construction.md :: #### Importance of Managing Complexity`. |
| `NODE-IMPL-007` | `mitigates` | `NODE-IMPL-006` | `derived_inference` — explicit local dependencies reduce hidden knowledge. `APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity`; `PP: chapters/011-chapter-6-while-you-are-coding.md :: ## **<sup>31</sup>** Programming by Coincidence`. |
| `NODE-IMPL-008` | `operationalizes` | `NODE-IMPL-007` | `direct_support` — callers reason without internal decisions. `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`. |
| `NODE-IMPL-008` | `mitigates` | `NODE-IMPL-004` | `corroboration` — central hidden decisions localize change. `CC: chapters/011-chapter-5-design-in-construction.md :: #### Value of Information Hiding`. |
| `NODE-IMPL-009` | `causes` | `NODE-IMPL-004` | `direct_support` — leaked knowledge must be changed in multiple modules. `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`. |
| `NODE-IMPL-009` | `causes` | `NODE-IMPL-006` | `derived_inference` — nonlocal leaked dependencies become undiscoverable requirements. `APOSD: chapters/007-2-the-nature-of-complexity.md :: # 2: The Nature of Complexity`; `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`. |
| `NODE-IMPL-010` | `operationalizes` | `NODE-IMPL-008` | `direct_support` — a deep module hides substantial implementation behind a simple interface. `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`. |
| `NODE-IMPL-010` | `supports` | `NODE-IMPL-007` | `direct_support` — deep interfaces reduce caller knowledge. `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`. |
| `NODE-IMPL-011` | `contradicts` | `NODE-IMPL-010` | `direct_support` — shallow modules expose interface burden without comparable hidden benefit. `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`. |
| `NODE-IMPL-012` | `guards` | `NODE-IMPL-010` | `derived_inference` — depth is desirable only when the abstraction is evidenced and coherent. `CC: chapters/013-chapter-7-high-quality-routines.md :: #### Summary of Reasons to Create a Routine`; `APOSD: chapters/009-4-modules-should-be-deep.md :: # 4: Modules Should Be Deep`. |
| `NODE-IMPL-013` | `refines` | `NODE-IMPL-009` | `direct_support` — duplication is leakage when the copies encode the same knowledge. `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication`; `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`. |
| `NODE-IMPL-013` | `in_tension_with` | `NODE-IMPL-012` | `refinement` — duplication creates abstraction pressure but does not by itself prove a coherent abstraction. `APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?`. |
| `NODE-IMPL-014` | `contradicts` | `NODE-IMPL-012` | `direct_support` — hypothetical variation cannot satisfy the evidence obligation. `APOSD: chapters/011-6-general-purpose-modules-are-deeper.md :: # 6: General-Purpose Modules are Deeper`; `CC: chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: #### Overengineering`. |
| `NODE-IMPL-015` | `supports` | `NODE-IMPL-012` | `direct_support` — comparing alternatives exposes whether an abstraction actually lowers caller and implementation cost. `APOSD: chapters/016-11-design-it-twice.md :: # 11: Design it Twice`. |
| `NODE-IMPL-015` | `operationalizes` | `NODE-IMPL-001` | `corroboration` — design alternatives are evidence collection before commitment. `CC: chapters/011-chapter-5-design-in-construction.md :: #### Iterate`. |
| `NODE-IMPL-016` | `prerequisite_for` | `NODE-IMPL-027` | `direct_support` — tests need a contract to determine expected behavior. `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Testing Against Contract`. |
| `NODE-IMPL-017` | `refines` | `NODE-IMPL-016` | `direct_support` — invariants are persistent contract conditions. `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Other Uses of Invariants`. |
| `NODE-IMPL-027` | `guards` | `NODE-IMPL-017` | `corroboration` — boundary/state/error tests demonstrate invariant preservation. `CC: chapters/031-chapter-22-developer-testing.md :: #### Combinations of Data States`; `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### Testing Against Contract`. |
| `NODE-IMPL-018` | `operationalizes` | `NODE-IMPL-016` | `refinement` — error propagation/recovery is an interface semantic. `CC: chapters/014-chapter-8-defensive-programming.md :: #### 8.3 Error-Handling Techniques`; `APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence`. |
| `NODE-IMPL-019` | `guards` | `NODE-IMPL-018` | `direct_support` — error-surface reduction must not continue after unsafe corruption or crash in contexts requiring recovery. `CC: chapters/014-chapter-8-defensive-programming.md :: #### Robustness vs. Correctness`; `APOSD: chapters/015-10-define-errors-out-of-existence.md :: # 10: Define Errors Out Of Existence`. |
| `NODE-IMPL-050` | `refines` | `NODE-IMPL-018` | `direct_support` — ordinary outcomes and exceptional failures require different caller contracts. `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### What Is Exceptional?`. |
| `NODE-IMPL-020` | `refines` | `NODE-IMPL-016` | `direct_support` — ownership/lifetime is part of the contract. `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ## **<sup>25</sup>** How to Balance Resources`. |
| `NODE-IMPL-020` | `prerequisite_for` | `NODE-IMPL-034` | `derived_inference` — concurrent execution is unsafe without shared resource/state ownership. `PP: chapters/009-chapter-4-pragmatic-paranoia.md :: ### Nest Allocations`; `PP: chapters/010-chapter-5-bend-or-break.md :: ### Design for Concurrency`. |
| `NODE-IMPL-021` | `operationalizes` | `NODE-IMPL-007` | `direct_support` — obvious code is locally understandable to readers. `APOSD: chapters/023-18-code-should-be-obvious.md :: # 18: Code Should be Obvious`. |
| `NODE-IMPL-022` | `supports` | `NODE-IMPL-021` | `direct_support` — precise names remove obscurity. `APOSD: chapters/019-14-choosing-names.md :: # 14: Choosing Names`; `CC: chapters/018-chapter-11-the-power-of-variable-names.md :: #### The Most Important Naming Consideration`. |
| `NODE-IMPL-023` | `supports` | `NODE-IMPL-021` | `direct_support` — non-obvious contract and rationale become discoverable. `APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code`. |
| `NODE-IMPL-023` | `guards` | `NODE-IMPL-016` | `direct_support` — comments capture the informal interface the signature cannot encode. `APOSD: chapters/018-13-comments-should-describe-things-that-arent-obvious-from-the-code.md :: # 13: Comments Should Describe Things that Aren’t Obvious from the Code`. |
| `NODE-IMPL-024` | `supports` | `NODE-IMPL-021` | `direct_support` — consistency lets readers transfer knowledge. `APOSD: chapters/022-17-consistency.md :: # 17: Consistency`. |
| `NODE-IMPL-024` | `in_tension_with` | `NODE-IMPL-047` | `refinement` — preserving consistency can entrench harmful convention, while broken-window cleanup can create arbitrary variation. `APOSD: chapters/022-17-consistency.md :: # 17: Consistency`; `PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ## **<sup>2</sup>** Software Entropy`. |
| `NODE-IMPL-025` | `operationalizes` | `NODE-IMPL-001` | `direct_support` — a disposable prototype obtains targeted evidence before implementation. `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Things to Prototype`; `CC: chapters/011-chapter-5-design-in-construction.md :: #### Experimental Prototyping`. |
| `NODE-IMPL-025` | `contradicts_if_retained_as` | `NODE-IMPL-026` | `direct_support` — prototype code is disposable; tracer code is production-quality and retained. `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Tracer Code versus Prototyping`. |
| `NODE-IMPL-026` | `operationalizes` | `NODE-IMPL-001` | `refinement` — a tracer supplies end-to-end evidence while becoming the implementation spine. `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>10</sup>** Tracer Bullets`. |
| `NODE-IMPL-027` | `guards` | `NODE-IMPL-030` | `direct_support` — behavior protection is required to separate safe structural transformation from semantic change. `CC: chapters/033-chapter-24-refactoring.md :: #### 24.4 Refactoring Safely`; `PP: chapters/011-chapter-6-while-you-are-coding.md :: ### How Do You Refactor?`. |
| `NODE-IMPL-028` | `contradicts` | `NODE-IMPL-027` | `direct_support` — executed lines alone do not prove contract protection. `CC: chapters/031-chapter-22-developer-testing.md :: #### Coverage Monitors`; `PP: chapters/013-chapter-8-pragmatic-projects.md :: ### Testing Thoroughly`. |
| `NODE-IMPL-029` | `prerequisite_for` | `NODE-IMPL-030` | `derived_inference` — root-cause diagnosis and a failing regression identify the authorized semantic delta before structural cleanup. `CC: chapters/032-chapter-23-debugging.md :: #### 23.3 Fixing a Defect`; `CC: chapters/033-chapter-24-refactoring.md :: #### 24.4 Refactoring Safely`. |
| `NODE-IMPL-031` | `guards` | `NODE-IMPL-032` | `direct_support` — specialization is warranted only by repeatable measured gain with preserved semantics. `CC: chapters/034-chapter-25-code-tuning-strategies.md :: #### 25.4 Measurement`; `APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance`. |
| `NODE-IMPL-032` | `in_tension_with` | `NODE-IMPL-021` | `direct_support` — hot-path specialization can reduce readability and abstraction quality. `CC: chapters/035-chapter-26-code-tuning-techniques.md :: #### 26.7 The More Things Change, the More They Stay the Same`; `APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance`. |
| `NODE-IMPL-032` | `in_tension_with` | `NODE-IMPL-010` | `refinement` — representation may need exposure or specialization, but should stay behind a deep semantic interface where possible. `APOSD: chapters/025-20-designing-for-performance.md :: # 20: Designing for Performance`. |
| `NODE-IMPL-033` | `refines` | `NODE-IMPL-009` | `direct_support` — execution-order knowledge repeated across modules is information leakage. `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`. |
| `NODE-IMPL-033` | `creates_pressure_for` | `NODE-IMPL-034` | `direct_support` — removing unnecessary ordering can enable concurrency, but does not prove concurrency is needed. `PP: chapters/010-chapter-5-bend-or-break.md :: ## **<sup>28</sup>** Temporal Coupling`. |
| `NODE-IMPL-034` | `guards` | `NODE-IMPL-033` | `refinement` — do not respond to temporal coupling by adding concurrency unless a quality driver and lifecycle model exist. `CC: chapters/011-chapter-5-design-in-construction.md :: #### Design Is About Tradeoffs and Priorities`; `PP: chapters/010-chapter-5-bend-or-break.md :: ### Design for Concurrency`. |
| `NODE-IMPL-035` | `causes` | `NODE-IMPL-006` | `corroboration` — global mutable state hides who can change a value and when. `CC: chapters/020-chapter-13-unusual-data-types.md :: #### Common Problems with Global Data`. |
| `NODE-IMPL-035` | `contradicts` | `NODE-IMPL-007` | `direct_support` — nonlocal mutable state defeats local reasoning and orthogonal tests. `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ### Coding`; `CC: chapters/020-chapter-13-unusual-data-types.md :: #### Common Problems with Global Data`. |
| `NODE-IMPL-037` | `operationalizes` | `NODE-IMPL-012` | `direct_support` — an earned routine extraction is one concrete abstraction transformation. `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine`. |
| `NODE-IMPL-037` | `in_tension_with` | `NODE-IMPL-010` | `direct_support` — extraction improves abstraction only when the new interface is deep enough; excessive extraction creates shallow modules. `APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?`; `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.1 Valid Reasons to Create a Routine`. |
| `NODE-IMPL-038` | `contradicts` | `NODE-IMPL-037` | `direct_support` — line count alone cannot justify extraction. `CC: chapters/013-chapter-7-high-quality-routines.md :: #### 7.4 How Long Can a Routine Be?`; `APOSD: chapters/014-9-better-together-or-better-apart.md :: # 9: Better Together Or Better Apart?`. |
| `NODE-IMPL-039` | `in_tension_with` | `NODE-IMPL-040` | `direct_support` — configurable external policy can be appropriate, but technical choices pushed to callers violate caller simplification. `PP: chapters/010-chapter-5-bend-or-break.md :: ### When to Configure`; `APOSD: chapters/013-8-pull-complexity-downwards.md :: # 8: Pull Complexity Downwards`. |
| `NODE-IMPL-049` | `guards` | `NODE-IMPL-039` | `refinement` — configuration must earn its interface/operational cost through real external variability. `APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction`; `PP: chapters/010-chapter-5-bend-or-break.md :: ### When to Configure`. |
| `NODE-IMPL-040` | `supports` | `NODE-IMPL-010` | `direct_support` — a deep module absorbs related complexity to simplify callers. `APOSD: chapters/013-8-pull-complexity-downwards.md :: # 8: Pull Complexity Downwards`. |
| `NODE-IMPL-040` | `guards` | `NODE-IMPL-008` | `refinement` — hide related mechanism, but not caller-owned policy or required operational facts. `APOSD: chapters/013-8-pull-complexity-downwards.md :: # 8: Pull Complexity Downwards`; `APOSD: chapters/010-5-information-hiding-and-leakage.md :: # 5: Information Hiding (and Leakage)`. |
| `NODE-IMPL-041` | `supports` | `NODE-IMPL-007` | `direct_support` — limiting collaborator knowledge can improve locality. `PP: chapters/010-chapter-5-bend-or-break.md :: ### The Law of Demeter for Functions`. |
| `NODE-IMPL-041` | `in_tension_with` | `NODE-IMPL-042` | `direct_support` — strict traversal avoidance can create pass-through wrappers; direct coupling can be simpler when no decision is hidden. `PP: chapters/010-chapter-5-bend-or-break.md :: ### Does It Really Make a Difference?`; `APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction`. |
| `NODE-IMPL-042` | `mitigates` | `NODE-IMPL-011` | `direct_support` — removing pass-through indirection eliminates shallow interface burden. `APOSD: chapters/012-7-different-layer-different-abstraction.md :: # 7: Different Layer, Different Abstraction`. |
| `NODE-IMPL-043` | `operationalizes` | `NODE-IMPL-027` | `direct_support` — test-first is one feedback order for contract protection, not the definition of adequate protection. `CC: chapters/031-chapter-22-developer-testing.md :: #### Test First or Test Last?`. |
| `NODE-IMPL-043` | `in_tension_with` | `NODE-IMPL-044` | `direct_support` — feature-test sequence can aid behavior feedback but can also constrain broader module design if used as the sole design method. `APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends`; `CC: chapters/031-chapter-22-developer-testing.md :: #### Test First or Test Last?`. |
| `NODE-IMPL-044` | `supports` | `NODE-IMPL-015` | `corroboration` — considering the abstraction before individual feature tests is one form of alternative design. `APOSD: chapters/016-11-design-it-twice.md :: # 11: Design it Twice`; `APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends`. |
| `NODE-IMPL-045` | `operationalizes` | `NODE-IMPL-015` | `direct_support` — comments-first can expose a weak interface before code commitment. `APOSD: chapters/020-15-write-the-comments-first.md :: # 15: Write The Comments First`. |
| `NODE-IMPL-045` | `supports` | `NODE-IMPL-023` | `direct_support` — drafting comments identifies required non-obvious interface information. `APOSD: chapters/020-15-write-the-comments-first.md :: # 15: Write The Comments First`. |
| `NODE-IMPL-046` | `guards` | `NODE-IMPL-047` | `refinement` — a broken-window signal must not automatically authorize risky or aesthetic cleanup. `CC: chapters/033-chapter-24-refactoring.md :: #### Reasons Not to Refactor`; `PP: chapters/006-chapter-1-a-pragmatic-philosophy.md :: ## **<sup>2</sup>** Software Entropy`. |
| `NODE-IMPL-046` | `in_tension_with` | `NODE-IMPL-030` | `direct_support` — structural improvement is beneficial only when pressure/protection/timing justify it. `CC: chapters/033-chapter-24-refactoring.md :: #### Bad Times to Refactor`; `APOSD: chapters/021-16-modifying-existing-code.md :: # 16: Modifying Existing Code`. |
| `NODE-IMPL-048` | `mitigates` | `NODE-IMPL-009` | `refinement` — composition can prevent base-state/implementation details leaking into subclasses. `APOSD: chapters/024-19-software-trends.md :: # 19: Software Trends`. |
| `NODE-IMPL-048` | `guards` | `NODE-IMPL-013` | `derived_inference` — do not use inheritance solely to deduplicate implementation without substitutable semantics. `CC: chapters/012-chapter-6-working-classes.md :: #### Inheritance ("is a" Relationships)`; `PP: chapters/007-chapter-2-a-pragmatic-approach.md :: ## **<sup>7</sup>** The Evils of Duplication`. |

### Graph disagreement preservation notes

- `NODE-IMPL-010` (deep module), `NODE-IMPL-037` (coherent routine extraction), and `NODE-IMPL-038` (arbitrary size threshold) must remain distinct. The graph must not reduce them to “prefer medium-sized routines.” The decision is based on abstraction coherence and interface burden, not averaging size preferences.
- `NODE-IMPL-013` (knowledge duplication) creates pressure for `NODE-IMPL-012` (earned abstraction), but the `in_tension_with` edge is essential: repeated syntax is not proof of shared knowledge.
- `NODE-IMPL-039` (metadata-driven configuration), `NODE-IMPL-040` (pull complexity downward), and `NODE-IMPL-049` (configuration interface cost) encode a real policy/ownership conflict. The graph must route operator/user policy toward configuration while keeping derivable technical mechanism inside the module.
- `NODE-IMPL-041` (Law of Demeter) and `NODE-IMPL-042` (direct dependency when indirection hides nothing) are competing heuristics, not a deprecation relationship. Ownership hiding and accepted dependency architecture choose between them.
- `NODE-IMPL-043` (test-first feedback) and `NODE-IMPL-044` (abstraction design before feature-test sequence) must remain in tension. The corpus supports test-first repair strongly, test-first feature work contextually, and independent abstraction reasoning for consequential shared APIs.
- `NODE-IMPL-047` (broken window) is a diagnostic/cultural smell, while `NODE-IMPL-046` (leave stable code alone) is an execution constraint. Neither node defeats the other without change pressure, preservation, scope, and authority evidence.
- `NODE-IMPL-018`, `NODE-IMPL-019`, and `NODE-IMPL-050` preserve three different decisions: reduce handler sites, choose fail-fast versus recovery by consequence, and choose ordinary result versus exception by semantic normality/language idiom.
- `NODE-IMPL-031` is a proof obligation for `NODE-IMPL-032`, not generic support for optimization. Without the measured baseline and semantic oracle, the performance-specialization node must not activate.
