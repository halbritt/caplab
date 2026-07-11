# Change and Legacy Sources: Evidence Extraction

Status: complete source-lane extraction for synthesis. This artifact mines operational doctrine from three sources; it is not a chapter summary, and none of the sources is treated as repository-independent authority.

## Scope, source IDs, and locator convention

The complete converted Markdown chapter sets were inspected for all three assigned sources, including front matter, part dividers, endnotes, appendices, bibliography, glossary, contents, and indexes.

- `SRC-REF` — *Refactoring: Improving the Design of Existing Code* (first-edition conversion).
  - `REF_ROOT = books/refactoring-improving-the-design-of-existing-code`
- `SRC-WELC` — *Working Effectively with Legacy Code*.
  - `WELC_ROOT = books/programming-working-effectively-with-legacy-code`
- `SRC-SDX` — *Software Design X-Rays: Fix Technical Debt with Behavioral Code Analysis*.
  - `SDX_ROOT = books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725`

Every locator has the form `SOURCE_ID: chapters/<file> :: <exact Markdown heading>` and is relative to the declared root. Claims are paraphrases. Page anchors are not canonical locators.

## Complete chapter coverage ledger

### SRC-REF coverage (21/21 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `REF_ROOT/chapters/001-refactoring-improving-the-design-of-existing-code.md` | Refactoring: Improving the Design of Existing Code | Publication/title context only. |
| `REF_ROOT/chapters/002-foreword.md` | Foreword | Small behavior-preserving transformation, test feedback, and language/tool context; perspective, not independent rule. |
| `REF_ROOT/chapters/003-preface.md` | Preface | Definition, intended audience, catalog scope, and Smalltalk/Java-era assumptions. |
| `REF_ROOT/chapters/004-acknowledgments.md` | Acknowledgments | Publication context only. |
| `REF_ROOT/chapters/005-chapter-1-refactoring-a-first-example.md` | Chapter 1: Refactoring, a First Example | Tests first; small-step extraction/movement; local variables; responsibility placement; polymorphism case study; change-driven need. |
| `REF_ROOT/chapters/006-chapter-2-principles-in-refactoring.md` | Chapter 2: Principles in Refactoring | Definition; two hats; reasons, timing, constraints, interfaces, databases, design, performance, and leave-alone conditions. |
| `REF_ROOT/chapters/007-chapter-3-bad-smells-in-code.md` | Chapter 3: Bad Smells in Code | Smells as fallible indications; duplication, change dispersion, low cohesion, speculative generality, indirection, data and inheritance concerns. |
| `REF_ROOT/chapters/008-chapter-4-building-tests.md` | Chapter 4: Building Tests | Self-checking automated feedback; unit/functional distinction; risk-oriented cases; boundaries and failures; limits of test proof. |
| `REF_ROOT/chapters/009-chapter-5-toward-a-catalog-of-refactorings.md` | Chapter 5: Toward a Catalog of Refactorings | Transformation record format; mechanics, motivation, examples, reference discovery, and catalog maturity limits. |
| `REF_ROOT/chapters/010-chapter-6-composing-methods.md` | Chapter 6: Composing Methods | Extract/inline, query-versus-temp, explaining variables, state separation, method objects, and algorithm substitution. |
| `REF_ROOT/chapters/011-chapter-7-moving-features-between-objects.md` | Chapter 7: Moving Features Between Objects | Move/extract/inline class and field; delegation trade-offs; local extension of external code. |
| `REF_ROOT/chapters/012-chapter-8-organizing-data.md` | Chapter 8: Organizing Data | Representation, value/reference identity, associations, collection encapsulation, domain values, type codes, and state/strategy trade-offs. |
| `REF_ROOT/chapters/013-chapter-9-simplifying-conditional-expressions.md` | Chapter 9: Simplifying Conditional Expressions | Decompose/consolidate conditionals, guards, null objects, and explicit assertions. |
| `REF_ROOT/chapters/014-chapter-10-making-method-calls-simpler.md` | Chapter 10: Making Method Calls Simpler | Naming/signature evolution, query/command separation, parameters, constructors, exceptions, and published API risk. |
| `REF_ROOT/chapters/015-chapter-11-dealing-with-generalization.md` | Chapter 11: Dealing with Generalization | Pull/push hierarchy moves, template methods, delegation/inheritance, interface extraction, and hierarchy removal. |
| `REF_ROOT/chapters/016-chapter-12-big-refactorings.md` | Chapter 12: Big Refactorings | Long-running directions rather than one-shot recipes; inheritance separation, procedural-to-object conversion, domain/presentation separation, hierarchy extraction. |
| `REF_ROOT/chapters/017-chapter-13-refactoring-reuse-and-reality.md` | Chapter 13: Refactoring, Reuse, and Reality | Adoption limits, economics, safety, near-term benefits, language/tool effects, and practitioner evidence. |
| `REF_ROOT/chapters/018-endnotes.md` | Endnotes | Attribution and historical notes; no independent doctrine. |
| `REF_ROOT/chapters/019-chapter-14-refactoring-tools.md` | Chapter 14: Refactoring Tools | Semantic accuracy, program model, speed, undo, and workflow integration as tool-trust conditions. |
| `REF_ROOT/chapters/020-chapter-15-putting-it-all-together.md` | Chapter 15: Putting It All Together | Goal selection, uncertainty stop, backtracking, pairing, semantic-issue deferral, and continuous small campaigns. |
| `REF_ROOT/chapters/021-bibliography.md` | Bibliography | Source trail only. |

### SRC-WELC coverage (37/37 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `WELC_ROOT/chapters/001-working-effectively-with-legacy-code.md` | Working Effectively with Legacy Code | Publication/title context only. |
| `WELC_ROOT/chapters/002-contents.md` | Contents | Navigation and chapter-boundary cross-check. |
| `WELC_ROOT/chapters/003-foreword.md` | Foreword | Change safety and feedback motivation; perspective only. |
| `WELC_ROOT/chapters/004-preface.md` | Preface | Legacy-change scope, dependency difficulty, and language mix. |
| `WELC_ROOT/chapters/005-acknowledgments.md` | Acknowledgments | Publication context only. |
| `WELC_ROOT/chapters/006-introduction.md` | Introduction | Operational definition of legacy code and test-feedback emphasis; definition is deliberately narrow and contextual. |
| `WELC_ROOT/chapters/007-part-i.md` | Part I | Part divider. |
| `WELC_ROOT/chapters/008-chapter-1-changing-software.md` | Chapter 1: Changing Software | Feature, repair, refactoring, and optimization distinctions; preservation and risk questions. |
| `WELC_ROOT/chapters/009-chapter-2-working-with-feedback.md` | Chapter 2: Working with Feedback | Cover-and-modify, fast local feedback, test coverings, the legacy dilemma, and change algorithm. |
| `WELC_ROOT/chapters/010-chapter-3-sensing-and-separation.md` | Chapter 3: Sensing and Separation | Observation and execution isolation; fakes versus mocks; localized tests. |
| `WELC_ROOT/chapters/011-chapter-4-the-seam-model.md` | Chapter 4: The Seam Model | Seams, enabling points, and preprocessing/link/object seam trade-offs. |
| `WELC_ROOT/chapters/012-chapter-5-tools.md` | Chapter 5: Tools | Refactoring and test tools as leverage; tool/library versions are historical. |
| `WELC_ROOT/chapters/013-part-ii.md` | Part II | Part divider. |
| `WELC_ROOT/chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md` | Chapter 6: I Don't Have Much Time and I Have to Change It | Sprout/wrap methods and classes as pressure adaptations with integration and design costs. |
| `WELC_ROOT/chapters/015-chapter-7-it-takes-forever-to-make-a-change.md` | Chapter 7: It Takes Forever to Make a Change | Lag time, build/test feedback, dependency structure, and incremental improvement. |
| `WELC_ROOT/chapters/016-chapter-8-how-do-i-add-a-feature.md` | Chapter 8: How Do I Add a Feature? | TDD loop, legacy adaptation, programming by difference, and substitutability. |
| `WELC_ROOT/chapters/017-chapter-9-i-can-t-get-this-class-into-a-test-harness.md` | Chapter 9: I Can't Get This Class into a Test Harness | Constructor/global/hidden dependencies, parameterization, extraction, and subclass seams. |
| `WELC_ROOT/chapters/018-chapter-10-i-can-t-run-this-method-in-a-test-harness.md` | Chapter 10: I Can't Run This Method in a Test Harness | Hidden methods, side effects, command/query separation, and access/test trade-offs. |
| `WELC_ROOT/chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md` | Chapter 11: I Need to Make a Change. What Methods Should I Test? | Effect reasoning and propagation; test-surface selection; encapsulation tension. |
| `WELC_ROOT/chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md` | Chapter 12: I Need to Make Many Changes in One Area. Do I Have to Break Dependencies for All the Classes Involved? | Interception/pinch points, higher-level coverings, hidden responsibilities, and traps. |
| `WELC_ROOT/chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md` | Chapter 13: I Need to Make a Change, but I Don't Know What Tests to Write | Characterization of actual behavior, suspicious behavior handling, targeted tests, and stopping heuristic. |
| `WELC_ROOT/chapters/022-chapter-14-dependencies-on-libraries-are-killing-me.md` | Chapter 14: Dependencies on Libraries Are Killing Me | Library boundaries, wrapper decisions, ownership and change risk. |
| `WELC_ROOT/chapters/023-chapter-15-my-application-is-all-api-calls.md` | Chapter 15: My Application Is All API Calls | Skin/wrapper strategy and separating application policy from API mechanics. |
| `WELC_ROOT/chapters/024-chapter-16-i-don-t-understand-the-code-well-enough-to-change-it.md` | Chapter 16: I Don't Understand the Code Well Enough to Change It | Notes, listing markup, effect sketches, scratch refactoring, and unused-code investigation. |
| `WELC_ROOT/chapters/025-chapter-17-my-application-has-no-structure.md` | Chapter 17: My Application Has No Structure | Narrative/system understanding and growth around emerging structure. |
| `WELC_ROOT/chapters/026-chapter-18-my-test-code-is-in-the-way.md` | Chapter 18: My Test Code Is in the Way | Test duplication, fixtures, naming, localization, and refactoring tests. |
| `WELC_ROOT/chapters/027-chapter-19-my-project-is-not-object-oriented-how-do-i-make-safe-changes.md` | Chapter 19: My Project Is Not Object Oriented. How Do I Make Safe Changes? | Procedural seams, functions, globals, linker/preprocessor techniques, and language-specific constraints. |
| `WELC_ROOT/chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md` | Chapter 20: This Class Is Too Big and I Don't Want It to Get Any Bigger | Responsibility discovery, current-work lens, implementation/interface sequencing, strategy and tactics. |
| `WELC_ROOT/chapters/029-chapter-21-i-m-changing-the-same-code-all-over-the-place.md` | Chapter 21: I'm Changing the Same Code All Over the Place | Repeated edit sites, duplication, hierarchy and extraction alternatives. |
| `WELC_ROOT/chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md` | Chapter 22: I Need to Change a Monster Method and I Can't Write Tests for It | Automated versus manual extraction, sensing variables, dependency gleaning, sequence discovery, tiny pieces, redo. |
| `WELC_ROOT/chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md` | Chapter 23: How Do I Know That I'm Not Breaking Anything? | Hyperaware/single-goal editing, signature preservation, compiler support, and pairing. |
| `WELC_ROOT/chapters/032-chapter-24-we-feel-overwhelmed-it-isn-t-going-to-get-any-better.md` | Chapter 24: We Feel Overwhelmed. It Isn't Going to Get Any Better | Incremental improvement, local wins, team visibility, and avoiding total-rewrite paralysis. |
| `WELC_ROOT/chapters/033-part-iii.md` | Part III | Part divider. |
| `WELC_ROOT/chapters/034-chapter-25-dependency-breaking-techniques.md` | Chapter 25: Dependency-Breaking Techniques | Catalog of parameter, extraction, override, interface, linker, function-pointer, global, subclass, and text/preprocessor seams. |
| `WELC_ROOT/chapters/035-appendix.md` | Appendix | Refactoring names and cross-reference support. |
| `WELC_ROOT/chapters/036-glossary.md` | Glossary | Terminology cross-check. |
| `WELC_ROOT/chapters/037-index.md` | Index | Retrieval aid; conversion is noisy and contributes no independent rule. |

### SRC-SDX coverage (22/22 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `SDX_ROOT/chapters/001-software-design-x-rays.md` | Software Design X-Rays | Publication/title context and endorsements only. |
| `SDX_ROOT/chapters/002-contents.md` | Contents | Navigation and chapter-boundary cross-check. |
| `SDX_ROOT/chapters/003-acknowledgments.md` | Acknowledgments | Publication context only. |
| `SDX_ROOT/chapters/004-the-world-of-behavioral-code-analysis.md` | The World of Behavioral Code Analysis | Version-control-as-behavioral evidence, prioritization purpose, examples, and practitioner scope. |
| `SDX_ROOT/chapters/005-part-i-prioritize-and-react-to-technical-debt.md` | Part I: Prioritize and React to Technical Debt | Part divider. |
| `SDX_ROOT/chapters/006-chapter-1-why-technical-debt-isn-t-technical.md` | Chapter 1: Why Technical Debt Isn't Technical | Debt as time/context/business cost; decision logs; organizational causes; cognitive load; contextual metrics. |
| `SDX_ROOT/chapters/007-chapter-2-identify-code-with-high-interest-rates.md` | Chapter 2: Identify Code with High Interest Rates | Hotspots from change frequency plus rough complexity; trends and X-rays; prioritization, not verdict. |
| `SDX_ROOT/chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md` | Chapter 3: Coupling in Time: A Heuristic for the Concept of Surprise | Co-change, thresholds, surprising dependencies, test code, clone prioritization, polyglot analysis. |
| `SDX_ROOT/chapters/009-chapter-4-pay-off-your-technical-debt.md` | Chapter 4: Pay Off Your Technical Debt | Proximity, splinter campaigns, congestion, temporary protection, deletion hypotheses, cognitive chunks. |
| `SDX_ROOT/chapters/010-chapter-5-the-principles-of-code-age.md` | Chapter 5: The Principles of Code Age | Code-age heuristics, stable/active regions, domain precedence, package evolution, dead code caveat. |
| `SDX_ROOT/chapters/011-part-ii-work-with-large-codebases-and-organizations.md` | Part II: Work with Large Codebases and Organizations | Part divider. |
| `SDX_ROOT/chapters/012-chapter-6-spot-your-system-s-tipping-point-is-software-too-hard-divide-and-conquer-with-architectural-hotspots-analyze-subsystems-fight-the-normalization-of-deviance-toward-team-oriented-measures-exercises.md` | Chapter 6: Spot Your System's Tipping Point… | Logical components, subsystem drill-down, function hotspots, complexity trends, normalization of deviance, team-scoped analysis. |
| `SDX_ROOT/chapters/013-chapter-7-beyond-conway-s-law.md` | Chapter 7: Beyond Conway's Law | Coordination/diffusion, ownership, operational versus knowledge boundaries, organizational bias, non-performance use. |
| `SDX_ROOT/chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md` | Chapter 8: Toward Modular Monoliths through the Social View of Code | Rewrite risk, layered change cost, component/feature alternatives, deletion test, bounded-context candidates, team alignment. |
| `SDX_ROOT/chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md` | Chapter 9: Systems of Systems: Analyzing Multiple Repositories and Microservices | Multi-repository evidence, distributed coupling, architectural shotgun surgery, sociotechnical fit, technical sprawl. |
| `SDX_ROOT/chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md` | Chapter 10: An Extra Team Member: Predictive and Proactive Analyses | Early warnings, relative trends, rising hotspots, omission prompts, knowledge loss, data biases and workarounds. |
| `SDX_ROOT/chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md` | Appendix A1: The Hazards of Productivity and Performance Metrics | Goodhart effects, invisible context, ethics/legal context, and prohibition on individual performance scoring. |
| `SDX_ROOT/chapters/018-appendix-a2-code-maat-an-open-source-analysis-engine.md` | Appendix A2: Code Maat: An Open Source Analysis Engine | Historical tooling and data-transformation mechanics. |
| `SDX_ROOT/chapters/019-appendix-a3-data-mining-with-git-cloc-and-codescene.md` | Appendix A3: Data Mining with Git, cloc, and CodeScene | Git/cloc command mechanics, cleaning, scope, and historical tool-version caveats. |
| `SDX_ROOT/chapters/020-appendix-a4-hints-and-solutions-to-the-exercises.md` | Appendix A4: Hints and Solutions to the Exercises | Case-study answers; reinforces alternatives and manual validation. |
| `SDX_ROOT/chapters/021-bibliography.md` | Bibliography | Source trail only. |
| `SDX_ROOT/chapters/022-index.md` | Index | Retrieval aid; heavily flattened conversion with no independent doctrine. |

## Per-source corpus map

### SRC-REF — Refactoring

- **Primary domain:** behavior-preserving structural improvement and a catalog of small transformations, primarily in late-1990s Java/Smalltalk object-oriented code.
- **Strongest contributions:** an operational definition of refactoring; conscious separation of functionality and structure; tiny compile/test-backed moves; preservation of observable behavior; reversible sequencing; explicit mechanics; smell humility; interface/database constraints; long-running refactoring directions.
- **Contextual assumptions:** a mostly working program; rapid automated tests; compiler/tool support; OO dispatch and class structures; direct control over at least some callers.
- **Limitations:** many mechanics and names predate modern IDEs, generics, modules, functional idioms, gradual typing, distributed schemas, and current Java. Polymorphism and objects are frequent remedies because of source context, not universal destinations. Catalog recipes do not prove a repository needs the transformation.
- **Known tensions:** continuous opportunistic refactoring versus a broader evidence-ranked campaign; small methods/classes versus module depth and local readability; polymorphism versus a stable small conditional; comments as smell versus comments that preserve rationale; indirection benefits versus indirection cost.
- **Likely roles:** coding, refactoring, review, repair, legacy modernization, architecture assessment.
- **Concepts worth mining:** semantic/structural separation, preservation boundary, test-change rhythm, smell hypothesis, responsibility movement, earned abstraction, public-boundary migration, near-term campaign value, stop/backtrack.
- **Representative locators:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`; `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Duplicated Code`; `SRC-REF: chapters/008-chapter-4-building-tests.md :: ## The Value of Self-testing Code`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ### Stop when you are unsure.`

### SRC-WELC — Working Effectively with Legacy Code

- **Primary domain:** safe modification when behavior is poorly characterized and dependencies prevent fast local feedback.
- **Strongest contributions:** cover-and-modify algorithm; characterization tests of actual behavior; seams and enabling points; sensing/separation; effect reasoning; interception and pinch points; pressure adaptations; incremental dependency breaking; disciplined testless edits when no protection can yet exist.
- **Contextual assumptions:** a valuable existing system; incomplete tests; C++/Java/C#/C and build/linker contexts common circa 2004; some compiler or link leverage; change is required rather than optional.
- **Limitations:** “legacy code is code without tests” is a productive operational lens, not an exhaustive definition. Its strict unit-test boundary (no filesystem/database/network) is narrower than current usage. Preprocessor/link seams, inheritance-heavy techniques, and named tools are language/build-era specific. Testability pressure does not itself justify permanent public API exposure.
- **Known tensions:** test coverage versus encapsulation; temporary seam quality versus long-term design quality; sprout/wrap speed versus integration confidence; compiler-supported untested mechanics versus tests-before-change; working around dependencies versus redesigning them.
- **Likely roles:** legacy, repair, refactoring, coding, review, repository assessment.
- **Concepts worth mining:** characterization surface, preservation surface, dependency seam, enabling point, effect surface, pinch point, temporary scaffolding, single-goal edit, scratch refactor, change-local responsibility discovery.
- **Representative locators:** `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing`.

### SRC-SDX — Software Design X-Rays

- **Primary domain:** prioritizing technical and sociotechnical investigation with version-control history, rough complexity, ownership, and change-pattern evidence.
- **Strongest contributions:** distinguishes ugly inactive code from costly evolving code; combines change frequency and complexity; treats co-change/age/ownership as hypotheses; narrows large systems to inspectable regions; adds team congestion and history-data quality; sizes splinter campaigns around parallel development.
- **Contextual assumptions:** meaningful version history, enough recent commits, clean file identity across renames/moves/repositories, traceable commits or tickets, domain experts available to inspect prioritized candidates.
- **Limitations:** practitioner heuristics and case studies do not establish causation. Specific thresholds (for example 20 commits, 50 percent coupling, 10 percent complexity growth, or 150–200 commits) are illustrative defaults, not universal gates. LOC/indentation/cyclomatic proxies are language/style sensitive. Author data is biased by pairing, aliases, squashes, generated files, copied history, and organizational change.
- **Known tensions:** proactive continuous small refactoring versus hotspot-ranked investment; duplicated local clarity versus shared abstraction; stable old code versus latent risk/dead code; repository boundaries versus logical system boundaries; team ownership versus broad knowledge; modular monolith versus distribution.
- **Likely roles:** repository assessment, refactoring, architecture, review, legacy, planning, risk assessment.
- **Concepts worth mining:** change pressure, hotspot, co-change, surprise, clone cost, code age, architectural hotspot, complexity trend, developer congestion, sociotechnical congruence, data-quality gate, splinter campaign, relative early warning.
- **Representative locators:** `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ### What Is Change Coupling?`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis`.

## Source-role classification

| Source | Source roles | Appropriate doctrinal weight |
|---|---|---|
| SRC-REF | Universal safe-change foundation; refactoring mechanics; implementation craft; OO design vocabulary | Strong for definition, separation, small-step mechanics, and preservation; contextual for particular smells and OO destinations. |
| SRC-WELC | Safe-change and legacy systems; characterization; dependency breaking; change-surface reasoning | Strong for poorly characterized code procedures; contextual/historical for seam mechanics, test taxonomy, and language techniques. |
| SRC-SDX | Historical/hotspot analysis; refactoring prioritization; sociotechnical architecture; repository assessment | Strong for evidence triangulation and data-quality cautions; contextual for thresholds, metrics, inferred boundaries, and organizational remedies. |

## Conversion and evidence caveats

- SRC-REF is the 1999 first edition. Code formatting, page callouts, sidebar names, and some catalog headings were promoted into Markdown headings. Catalog mechanics remain evidence about transformation discipline, not current language syntax.
- SRC-WELC is a 2004 text. Page headers occasionally became headings, code comments can appear as Markdown headings, and the index is flattened. Linker, preprocessor, subclass, and C++ techniques require repository/toolchain verification.
- SRC-SDX is circa 2018. Its CodeScene, Code Maat, Git, cloc, Java, Python 2, and hosted snapshot instructions are historical. Commands and thresholds are examples, not present-day tool contracts.
- Wide tables and figures are often mangled across all three conversions. Claims below use surrounding prose and exact section headings, not reconstructed cells.
- None of the three books supplies repository-specific authorization, accepted architecture, user requirements, or current runtime evidence. Those evidence classes always outrank the extracted doctrine.
- History establishes where and how people changed code; it does not by itself establish intent, defect, domain boundary, causation, current runtime use, or authority to restructure.

## Canonical doctrine records

The records are compact renderings of the requested concept schema. “Required / insufficient” is an evidence gate. “Routes” contains activation role, task, repository signal, language, risk, exclusions, prerequisites, retrieval priority/budget, and related concepts.

### CHG-UNI-001 — Change-type honesty

- **Category / claim:** universal, refactoring, agent-conduct. Feature implementation, defect repair, behavior-preserving refactoring, optimization, migration, and cleanup have different semantic permissions and must not share a misleading label.
- **Decision rule:** classify the requested outcome before editing. If any accepted output, error, side effect, timing/resource contract, persistence shape, or compatibility contract is intentionally changed, the work is not solely refactoring; identify and authorize the semantic change separately.
- **Why / applicable / not:** classification determines protection, review, authority, and rollback. Applies to every change plan; taxonomy alone does not forbid a narrow, explicitly partitioned campaign containing sequential semantic and structural phases.
- **Required / insufficient evidence:** required—request/acceptance criteria, observed current behavior, accepted contracts, tests, call sites, operational constraints. Insufficient—commit title, issue label, “cleanup” wording, or the fact that code also moves.
- **Inputs / outputs:** task authority plus current/desired behavior; output is a named change type, semantic delta, preservation list, and phase boundary.
- **Preservation / safe / unsafe:** preserve all behavior outside authorized deltas. Safe—repair with a failing regression test, then separately refactor on green. Unsafe—hide a repair, API migration, exception-policy change, or optimization approximation inside “refactoring.”
- **Failure modes / counterexample:** semantic drift, review confusion, missing rollback, false confidence. Counterexample: renaming a private local while tests remain green is ordinary refactoring.
- **Interactions / conflicts:** CHG-UNI-002, CHG-UNI-003, CHG-REF-004; conflict `CONF-CL-001`.
- **Confidence / roles / languages / archetypes:** universal; all engineering agents; language-independent; all repositories.
- **Routes:** activate for every change proposal and mixed diff; all risk classes; exclude pure observation; prerequisite authority inventory; core, 250–400 tokens; related `change-taxonomy`, `semantic-delta`, `two-hats`.
- **Source support:** `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software`; `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Adding Features and Fixing Bugs`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`.

### CHG-UNI-002 — Explicit preservation boundary

- **Category / claim:** universal, refactoring, legacy, repair. Safe change begins by naming what must remain invariant, at which observable surfaces, and for whom.
- **Decision rule:** enumerate authorized behavior changes; treat every other externally observable result, side effect, stored format, protocol, timing/durability guarantee, and supported caller interaction as preserved until evidence or authority narrows it.
- **Why / applicable / not:** tests only protect encoded observations; a boundary prevents accidental assumptions. Applies to refactoring, repair, migration, and optimization; not every incidental implementation detail belongs in the boundary.
- **Required / insufficient evidence:** required—accepted requirements/ADRs, callers, tests, runtime traces, schemas, user-visible behavior, incident history. Insufficient—current unit tests alone, internal method shape, or an agent’s aesthetic reading.
- **Inputs / outputs:** authority and observation inventory; output is a preservation matrix with surface, invariant, evidence, protection, and owner.
- **Preservation / safe / unsafe:** safe—characterize a boundary and explicitly record unknowns. Unsafe—claim “behavior preserved” when only compilation or a narrow happy path was checked.
- **Failure modes / counterexample:** freezing accidental internals; omitting error behavior; preserving a known defect without escalation. Counterexample: an authorized defect repair changes the failing case while retaining the surrounding boundary.
- **Interactions / conflicts:** CHG-UNI-001, CHG-UNI-004, CHG-LEG-002, CHG-LEG-007.
- **Confidence / roles / languages / archetypes:** universal; all execution/review roles; language-independent; all, especially weakly tested and durable systems.
- **Routes:** activate for any write, migration, optimization, or repair; high priority at high risk; exclude read-only assessment; prerequisite authority; core, 350–550 tokens; related `characterization-surface`, `effect-surface`.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`; `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Risky Change`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests`.

### CHG-UNI-003 — Separate structural and semantic work

- **Category / claim:** universal, refactoring, repair. An agent should wear one change “hat” at a time so test failures retain diagnostic meaning.
- **Decision rule:** establish a green or explicitly characterized baseline; perform either a semantic slice or a structural slice; verify and commit/review at the boundary before switching. Keep discovered defects or adjacent improvements on a separate ledger unless they block the authorized goal.
- **Why / applicable / not:** mixing axes makes failures ambiguous and rollback coarse. Applies whenever structure and behavior both need work; mechanical setup strictly required to enable a test can precede characterization if isolated under CHG-LEG-006.
- **Required / insufficient evidence:** required—diff intent per slice, baseline result, named verification, explicit authorization for semantic deltas. Insufficient—small total diff or confidence that both changes are “obvious.”
- **Inputs / outputs:** campaign goal and work ledger; output is ordered single-purpose slices.
- **Preservation / safe / unsafe:** preserve semantic baseline during structural slices. Safe—add regression test/fix/green, then extract. Unsafe—change an algorithm while moving it and call the combined diff behavior-preserving.
- **Failure modes / counterexample:** bisect-resistant commits, false refactoring claims, debugging multiple causes. Counterexample: an IDE’s atomic, semantically verified rename may update declarations and all uses in one structural operation.
- **Interactions / conflicts:** CHG-UNI-001, CHG-UNI-004, CHG-UNI-005, CHG-LEG-010.
- **Confidence / roles / languages / archetypes:** universal; coding, repair, refactoring, review; language-independent; all.
- **Routes:** activate for mixed concerns or discovered defects; all risk; exclude pure docs-only edits; prerequisite change classification; core, 250–400; related `single-goal-edit`, `campaign-slicing`.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ## Get used to picking a goal.`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing`.

### CHG-UNI-004 — Short verified transformation loop

- **Category / claim:** universal, refactoring. Refactoring safety comes from a sequence of small, reviewable, independently verified moves rather than the intended end state alone.
- **Decision rule:** choose the smallest move that advances the named goal, run the cheapest relevant fast check, then broader protection at stable checkpoints. If a failure cannot be localized to the last move, the step was too large or the feedback too weak.
- **Why / applicable / not:** short feedback minimizes simultaneous uncertainty and preserves easy reversal. Applies to manual and automated transformations; redundant full-suite execution after every keystroke is not required when layered checks exist.
- **Required / insufficient evidence:** required—known baseline, reliable fast check, move-specific expected effect, clean diff/reversal point. Insufficient—successful compilation alone where semantics matter or a final suite after an opaque rewrite.
- **Inputs / outputs:** transformation target, check ladder, rollback point; output is a sequence with evidence per step.
- **Preservation / safe / unsafe:** safe—extract, compile, targeted test; commit only at coherent green points. Unsafe—long-lived refactoring branch with extensive simultaneous moves and deferred integration.
- **Failure modes / counterexample:** false locality from flaky tests, busywork steps, excessive merge exposure. Counterexample: a trusted compiler/IDE can safely perform one internally atomic repository-wide rename, still followed by repository checks.
- **Interactions / conflicts:** CHG-UNI-002, CHG-UNI-005, CHG-REF-006, CHG-LEG-010; conflict `CONF-CL-006`.
- **Confidence / roles / languages / archetypes:** universal/strong; refactoring, coding, repair; language-independent; all.
- **Routes:** structural campaign, fragile code, large diff; all risk; prerequisite baseline/check ladder; core, 300–500; related `reversibility`, `localization`.
- **Source support:** `SRC-REF: chapters/005-chapter-1-refactoring-a-first-example.md :: ## Final Thoughts`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: #### Backtrack.`; `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ### Software Vise`.

### CHG-UNI-005 — Stop, backtrack, or escalate on lost certainty

- **Category / claim:** universal, agent-conduct, refactoring. Uncertainty is a stop signal when the agent can no longer state what changed, what must remain invariant, or why a check failed.
- **Decision rule:** stop at the last known-good state. If the partial result is independently better and protected, retain it as a smaller campaign; otherwise revert only the agent’s slice. Escalate when behavior is disputed, authority is missing, protection cannot be made adequate, or reversal would affect external state.
- **Why / applicable / not:** pushing forward converts uncertainty into hidden risk. “Unsure” does not mean stop before safe read-only investigation, characterization, or scratch work.
- **Required / insufficient evidence:** required—baseline, diff, failure output, ownership/authority. Insufficient—time spent, sunk cost, or confidence unsupported by a reproducer.
- **Inputs / outputs:** current slice and evidence ledger; output is continue/backtrack/retain-smaller/escalate decision with reason.
- **Preservation / safe / unsafe:** safe—discard scratch extraction, retain green preparatory seam. Unsafe—debug forward through many unverified edits or silently pick desired behavior.
- **Failure modes / counterexample:** premature abandonment when one more safe observation exists; destroying user edits during reversal. Counterexample: a clearly explained new expected failure may authorize the next semantic step.
- **Interactions / conflicts:** CHG-UNI-004, CHG-LEG-003, CHG-LEG-010, authority doctrine.
- **Confidence / roles / languages / archetypes:** universal; all agents; language-independent; all.
- **Routes:** activate on failing checks, ambiguous behavior, external-state risk, or authority gap; high risk; core, 250–400; related `stop-condition`, `rollback`.
- **Source support:** `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ### Stop when you are unsure.`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: #### Backtrack.`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Hyperaware Editing`.

### CHG-REF-001 — Structural pressure earns refactoring

- **Category / claim:** refactoring, review. Unattractive structure is not enough; refactoring is earned when present or imminent work demonstrates avoidable change, comprehension, defect, review, test, or coordination cost.
- **Decision rule:** require a concrete goal plus at least one verified pressure: repeated coupled edits, dispersed responsibility, difficult effect isolation, recurring defect locus, rising complexity in actively changed code, blocked testing, or material reviewer/cognitive load. Select the smallest change that reduces that pressure.
- **Why / applicable / not:** this prevents aesthetic campaigns and focuses limited risk budget. Not applicable to an explicitly authorized modernization with independent contractual goals, though that work still needs protection.
- **Required / insufficient evidence:** required—current task/call sites, history/co-change, failures, test friction, review evidence, domain responsibilities. Insufficient—file length, age, smell name, generic style, or high churn alone.
- **Inputs / outputs:** pressure ledger and candidate transformations; output is act/leave-alone decision, target, expected pressure reduction, and verification.
- **Preservation / safe / unsafe:** safe—refactor adjacent to a required change or a measured hotspot. Unsafe—schedule broad cleanup solely because code “looks bad.”
- **Failure modes / counterexample:** under-refactoring because history is unavailable; metric-driven churn; fixing the wrong bottleneck. Counterexample: security or support migration may require structural change even without prior churn.
- **Interactions / conflicts:** CHG-REF-002, CHG-REF-003, CHG-HIST-001, CHG-REF-008; conflict `CONF-CL-002`.
- **Confidence / roles / languages / archetypes:** strong; refactoring, review, architecture, repository assessment; language-independent; mature repositories.
- **Routes:** smells, hotspot, change friction, requested cleanup; medium/high structural risk; exclude generated/vendor; prerequisite repository evidence; core, 350–600; related `change-pressure`, `leave-alone`.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?`; `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data`; `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work`.

### CHG-REF-002 — Smells are hypotheses, not verdicts

- **Category / claim:** refactoring, review. A smell names a question to investigate; it does not establish defect, low maintainability, or the correct remedy.
- **Decision rule:** translate the smell into an operational hypothesis, test it against call sites, change history, responsibilities, runtime constraints, and repository idiom, and act only if a transformation improves the demonstrated pressure without worsening information hiding.
- **Why / applicable / not:** surface form is context-sensitive. Applies to long methods/classes, switches, duplication, comments, middle men, inheritance, and data classes; hard contractual violations can be defects without smell analysis.
- **Required / insufficient evidence:** required—specific maintenance consequence and plausible causal link. Insufficient—threshold count, smell detector, catalog match, or reviewer preference.
- **Inputs / outputs:** candidate smell and evidence; output is confirmed/refuted/uncertain hypothesis and next observation or action.
- **Preservation / safe / unsafe:** safe—inspect why a long method changes, or whether a middle man hides volatility. Unsafe—split by size, replace every switch with polymorphism, or delete explanatory comments automatically.
- **Failure modes / counterexample:** cargo-cult OO, shallow modules, indirection inflation, suppressed rationale. Counterexample: repeated dispersed condition updates with omissions can strongly confirm shotgun surgery.
- **Interactions / conflicts:** CHG-REF-001, CHG-REF-003, CHG-HIST-003; conflicts `CONF-CL-003`, `CONF-CL-004`.
- **Confidence / roles / languages / archetypes:** strong; refactoring/review/coding; language-independent though source examples are OO; all nongenerated code.
- **Routes:** activate for smell/static-analysis findings; all risk; exclude generated/vendor; prerequisite consequence hypothesis; core, 300–450; related `smell-hypothesis`.
- **Source support:** `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code`; `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ### Switch Statements`; `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ### Comments`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Are You Telling Me Code Quality Isn't Important?`.

### CHG-REF-003 — Duplication is evaluated by coupled knowledge

- **Category / claim:** refactoring, implementation. Similar text earns abstraction only when it represents one concept or policy expected to evolve together; divergent concepts may be safer duplicated.
- **Decision rule:** compare semantic responsibility, change coupling, defect/omission history, variation shape, ownership, and readability. Extract the stable common concept when repeated edits or shared invariants demonstrate one knowledge source; retain duplication when examples communicate distinct domains or are expected to diverge.
- **Why / applicable / not:** removing text can create control flags and cross-boundary coupling. Generated duplication follows generator ownership, not this rule.
- **Required / insufficient evidence:** required—call/context comparison, history or repeated change, stable variation axis, nameable common responsibility. Insufficient—clone percentage or two occurrences alone.
- **Inputs / outputs:** duplicate sites and evolution evidence; output is retain/proximity/extract decision with expected change-locality effect.
- **Preservation / safe / unsafe:** safe—move related clones near each other as low-risk signaling; extract repeated postcondition or algorithm. Unsafe—parameterize semantically distinct tests until their behavior becomes obscure.
- **Failure modes / counterexample:** premature abstraction, boolean-parameter maze, shared ownership bottleneck, omission risk when true clones remain. Counterexample: two protocol adapters may remain locally duplicated because their vendors evolve independently.
- **Interactions / conflicts:** CHG-REF-002, CHG-HIST-002, CHG-HIST-003; conflict `CONF-CL-003`.
- **Confidence / roles / languages / archetypes:** strong/contextual; coding/refactoring/review; language-independent; application and test code.
- **Routes:** duplication, repeated edits, clone alert; normal/high; exclude generated code; prerequisite semantic/history comparison; high, 400–600; related `earned-abstraction`, `proximity`.
- **Source support:** `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Duplicated Code`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`.

### CHG-REF-004 — Responsibility movement follows evidence

- **Category / claim:** refactoring, architecture, domain. Move behavior or split a unit when dependencies, invariants, domain language, and independent change show that another unit can own the responsibility more cohesively.
- **Decision rule:** map data read/written, policies enforced, callers, co-change, lifecycle and authority ownership. Move only when the destination owns most relevant information/invariants and the move reduces knowledge or change dispersion without exposing internals.
- **Why / applicable / not:** responsibility placement controls local reasoning and change amplification. Directory proximity, size, or feature envy score alone cannot establish ownership.
- **Required / insufficient evidence:** required—effect/data map, invariant owner, call sites, current and anticipated changes, domain confirmation. Insufficient—naming similarity, directory name, or diagram symmetry.
- **Inputs / outputs:** responsibility and ownership map; output is retain/move/extract decision plus caller/API migration plan.
- **Preservation / safe / unsafe:** safe—delegate through old boundary while clients migrate. Unsafe—move behavior away from the data authority or split a deep coherent module into chatty pieces.
- **Failure modes / counterexample:** anemic domain, cycles, middle-man growth, semantic duplication. Counterexample: a cohesive large parser may remain one module despite many methods.
- **Interactions / conflicts:** CHG-REF-001, CHG-REF-007, CHG-LEG-009, CHG-HIST-009.
- **Confidence / roles / languages / archetypes:** strong/contextual; refactoring/architecture/coding; language-independent; domain-heavy and legacy systems.
- **Routes:** class/module split, feature envy, boundary selection; medium/high; exclude directory-only inference; prerequisite ownership map; high, 450–650; related `semantic-cohesion`, `data-ownership`.
- **Source support:** `SRC-REF: chapters/011-chapter-7-moving-features-between-objects.md :: ## Move Method`; `SRC-REF: chapters/011-chapter-7-moving-features-between-objects.md :: ### Extract Class`; `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## Seeing Responsibilities`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`.

### CHG-REF-005 — Published boundaries require migration, not casual refactoring

- **Category / claim:** refactoring, architecture. A structurally desirable API or data change becomes a compatibility migration when callers, persisted data, or deployed components are not changed atomically under the same authority.
- **Decision rule:** inventory boundary consumers and control. For fully controlled atomic callers, change and verify together. Otherwise preserve an adapter/old signature/schema, introduce the new form, migrate consumers with observability, then remove only under deprecation authority.
- **Why / applicable / not:** internal behavior preservation does not cover independent consumers or old data. Not required for truly private, proven-unreferenced symbols.
- **Required / insufficient evidence:** required—caller/deployment/schema inventory, compatibility contract, ownership, rollout/rollback, usage telemetry where available. Insufficient—repository search alone for a published library, or compiler success in one component.
- **Inputs / outputs:** boundary map; output is atomic edit or phased migration plan.
- **Preservation / safe / unsafe:** preserve wire/storage/public compatibility during transition. Safe—compatibility wrapper and dual-read/write as authorized. Unsafe—rename public API or mutate schema while labeling it behavior-preserving.
- **Failure modes / counterexample:** orphaned clients, unreadable historical data, permanent adapters. Counterexample: a private method with all callers in one compilation unit can be renamed atomically.
- **Interactions / conflicts:** CHG-UNI-001, CHG-UNI-002, CHG-REF-006.
- **Confidence / roles / languages / archetypes:** universal/strong; architecture/refactoring/coding/review; language-independent; libraries, services, durable systems.
- **Routes:** public API, DB/schema, event contract, multi-repo; high risk; prerequisite consumer/authority inventory; core, 350–550; related `migration`, `compatibility`.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Changing Interfaces`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Databases`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Preserve Signatures`.

### CHG-REF-006 — Trust transformation tools by semantic coverage

- **Category / claim:** refactoring, agent-conduct. Tool automation reduces mechanical error only within the language, build, generated-code, reflection, configuration, and repository surfaces the tool actually models.
- **Decision rule:** establish tool/version support, preview the edit set, inspect unresolved/dynamic references, keep undo/reversal, and run repository-native verification. Allow untested automated mechanics only when the tool is demonstrably semantics-aware for the exact operation and no manual edits are mixed in.
- **Why / applicable / not:** speed is not proof of accuracy. Applies to IDE refactors, codemods, compiler assists, and search/replace; plain text replacement never earns semantic trust by scale.
- **Required / insufficient evidence:** required—tool contract/version, preview, language boundaries, representative prior use, post-checks. Insufficient—vendor claim, successful edit command, or compilation where runtime/config references exist.
- **Inputs / outputs:** operation and reference surfaces; output is trust level, manual-review exceptions, and verification.
- **Preservation / safe / unsafe:** safe—semantic rename with preview and tests. Unsafe—automated hierarchy/move across reflection, templates, SQL, serialized names, or foreign languages without additional evidence.
- **Failure modes / counterexample:** stale strings/config, shadowing/inheritance errors, generated drift. Counterexample: a compiler-enforced private symbol rename may need only compile plus focused tests.
- **Interactions / conflicts:** CHG-UNI-004, CHG-LEG-010; conflict `CONF-CL-006`.
- **Confidence / roles / languages / archetypes:** strong; coding/refactoring/review; all languages with tool-specific activation; mixed-language repos need stricter gate.
- **Routes:** codemod/IDE/refactoring tool; medium/high; exclude unreviewed bulk rewrite; prerequisite tool support; high, 300–500; related `mechanical-change`.
- **Source support:** `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`; `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ### Undo`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: ## Tackling Monsters with Automated Refactoring Support`.

### CHG-REF-007 — Large refactorings are directional campaigns

- **Category / claim:** refactoring, architecture. Broad structural outcomes are achieved through a sequence of opportunistic, protected intermediate states; the named end pattern is a direction, not a single transaction.
- **Decision rule:** define the demonstrated force and target property, select the first boundary that reduces risk or change coupling, preserve compatibility, deliver a small useful state, remeasure, and revise the direction as knowledge grows.
- **Why / applicable / not:** large transformations reveal requirements and domain structure during execution. Not authority for indefinite architecture work or a preselected pattern without forces.
- **Required / insufficient evidence:** required—architectural pressure, current constraints, protected boundary, incremental value, integration cadence, stop/reversal criteria. Insufficient—future diagram, source prestige, or promise of eventual cleanup.
- **Inputs / outputs:** target force and campaign map; output is first campaign plus optional later candidates, not a monolithic rewrite plan.
- **Preservation / safe / unsafe:** safe—facade/delegation around extracted responsibility. Unsafe—months-long isolation, simultaneous subsystem rewrite, or destroying old path before equivalence proof.
- **Failure modes / counterexample:** transitional architecture becomes permanent; goal drift; parallel-merge conflict. Counterexample: a tiny isolated subsystem may permit one atomic transformation.
- **Interactions / conflicts:** CHG-REF-004, CHG-HIST-010, CHG-LEG-006; conflict `CONF-CL-005`.
- **Confidence / roles / languages / archetypes:** strong/contextual; architecture/refactoring/legacy; language-independent; large active systems.
- **Routes:** big refactoring, modularization, architecture migration; high risk; prerequisite pressure and campaign authority; high, 450–650; related `campaign-sizing`, `option-preservation`.
- **Source support:** `SRC-REF: chapters/016-chapter-12-big-refactorings.md :: ## The Nature of the Game`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## The Trade-Off Between Architectural Refinements and Replacement Systems`.

### CHG-REF-008 — Leave stable or low-value code alone

- **Category / claim:** refactoring, agent-conduct. Hard-to-read code should remain unchanged when it has no demonstrated cost, no authorized adjacent change, and intervention risk exceeds expected near-term benefit.
- **Decision rule:** compare current change/incident/use pressure and required future work against characterization, dependency, integration, and domain-knowledge cost. Choose no structural action when benefit is speculative; record the observation only if useful.
- **Why / applicable / not:** mature odd code may encode hard-won behavior, and touching it resets defect risk. Inactivity does not override security, unsupported platform, imminent feature, legal, safety, or confirmed defect evidence.
- **Required / insufficient evidence:** required—recent history, runtime use, incidents, roadmap, ownership, support constraints. Insufficient—old age alone, folklore, complaints, or no recent commits in a paused product.
- **Inputs / outputs:** value/risk comparison; output is leave-alone, characterize-only, isolate, delete-investigation, or campaign decision.
- **Preservation / safe / unsafe:** safe—avoid or isolate stable dependency; unsafe—rewrite because maintainers dislike it, or declare dead solely because it is old.
- **Failure modes / counterexample:** fossilizing dangerous code; false stability from inactivity; fear-driven avoidance. Counterexample: unsupported compiler/runtime can earn migration despite low churn.
- **Interactions / conflicts:** CHG-REF-001, CHG-HIST-004, CHG-LEG-003; conflict `CONF-CL-007`.
- **Confidence / roles / languages / archetypes:** strong/contextual; assessment/refactoring/architecture/review; language-independent; legacy/stable products.
- **Routes:** ugly old module, rewrite proposal, cleanup audit; medium/high; prerequisite usage/roadmap evidence; core, 300–500; related `no-change-decision`.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`; `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: #### Interest Rate Is a Function of Time`.

### CHG-LEG-001 — Cover-and-modify change algorithm

- **Category / claim:** legacy, repair, refactoring. In poorly characterized code, safe implementation proceeds from change point to observation point to dependency break to characterization, then to the required change and optional refactoring.
- **Decision rule:** identify where behavior must change; trace effects to the narrowest observable test point; break only dependencies blocking execution/observation; characterize current relevant behavior; make the authorized semantic change; refactor only on a protected baseline.
- **Why / applicable / not:** it resolves the legacy dilemma without demanding a redesign first. Not required where existing fast tests already protect the complete change surface.
- **Required / insufficient evidence:** required—change point, effect path, test point, dependency obstacle, baseline observation, authority. Insufficient—global coverage percentage, whole-system understanding, or a mockable type alone.
- **Inputs / outputs:** requested delta plus dependency/effect sketch; output is a minimum safe-change route and checks.
- **Preservation / safe / unsafe:** safe—one seam and targeted characterization. Unsafe—break every dependency, redesign surrounding architecture, or edit-and-pray.
- **Failure modes / counterexample:** test point too high to localize; seam changes production behavior; characterization misses side effects. Counterexample: a pure function with exhaustive tests can be modified directly.
- **Interactions / conflicts:** CHG-UNI-002, CHG-LEG-002, CHG-LEG-004, CHG-LEG-007.
- **Confidence / roles / languages / archetypes:** strong; legacy/repair/coding/refactoring; language-independent; weakly tested systems.
- **Routes:** poorly tested change, hard-to-instantiate code, unknown behavior; high correctness risk; prerequisite change authorization; core, 450–650; related `cover-and-modify`.
- **Source support:** `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### The Legacy Code Dilemma`; `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm`; `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Make Changes and Refactor`.

### CHG-LEG-002 — Characterize actual behavior, not desired behavior

- **Category / claim:** legacy, testing. A characterization test records what the system does at a relevant observation surface so an intended change can distinguish preserved behavior from regression.
- **Decision rule:** invoke a relevant path, make an initial assertion, observe the actual result, investigate enough to rule out harness error, then encode the observed behavior and boundary cases needed to sense the planned change. Stop when the change surface is protected, not when the entire unit is exhaustively specified.
- **Why / applicable / not:** undocumented deployed behavior may be contractual even when surprising. Do not characterize irrelevant dead paths or turn observations into claims of correctness.
- **Required / insufficient evidence:** required—representative setup, actual output/effect, repeatability, caller/use context, path relevance. Insufficient—what behavior “should” be, snapshot approval without inspection, or coverage percentage alone.
- **Inputs / outputs:** change/effect surface; output is targeted baseline tests and an uncertainty/suspicion ledger.
- **Preservation / safe / unsafe:** preserve observed relevant behavior unless separately authorized. Safe—encode odd result with explanatory test name. Unsafe—silently “correct” it during baseline creation.
- **Failure modes / counterexample:** golden-master noise, nondeterminism, accidental environment capture, ossifying irrelevant defects. Counterexample: a formally specified protocol can use the specification as primary oracle, with characterization as comparison evidence.
- **Interactions / conflicts:** CHG-UNI-002, CHG-LEG-003, CHG-LEG-007.
- **Confidence / roles / languages / archetypes:** strong; legacy/repair/refactoring/testing; language-independent; undocumented and weakly tested systems.
- **Routes:** no tests/unknown behavior; high risk; exclude generated outputs unless normalized; prerequisite observation surface; core, 400–600; related `characterization-surface`.
- **Source support:** `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## A Heuristic for Writing Characterization Tests`; `SRC-REF: chapters/008-chapter-4-building-tests.md :: ### Adding More Tests`.

### CHG-LEG-003 — Suspicious behavior is an escalation item

- **Category / claim:** legacy, repair, agent-conduct. Unexpected behavior found during characterization is evidence of a possible defect, not authorization to repair it and not proof it is correct.
- **Decision rule:** verify the observation, search requirements/history/callers/incidents, label it suspicious, and ask the authorized owner to choose preserve, repair, or investigate when the choice changes behavior. Continue around it only if the authorized task can preserve it safely.
- **Why / applicable / not:** old clients may depend on accidental behavior; silent correction widens scope. If explicit acceptance criteria already define the case as a defect, implement under repair authority.
- **Required / insufficient evidence:** required—repeatable observation, expected-source evidence, client impact, authorization. Insufficient—developer surprise, awkward code, or disagreement with a book.
- **Inputs / outputs:** observed/expected comparison; output is preserve/repair/escalate decision and regression/characterization handling.
- **Preservation / safe / unsafe:** safe—mark suspicious and freeze temporarily. Unsafe—fold fix into extraction or rewrite.
- **Failure modes / counterexample:** preserving security vulnerability; escalating every oddity without investigation; tests blessing harness bugs. Counterexample: unambiguous memory-safety violation under repair authority warrants immediate bounded fix.
- **Interactions / conflicts:** CHG-UNI-001, CHG-UNI-005, CHG-LEG-002, review authority.
- **Confidence / roles / languages / archetypes:** universal/strong; legacy/repair/review; language-independent; deployed systems.
- **Routes:** unexpected baseline, undocumented edge case; high semantic risk; prerequisite verify/search; core, 300–450; related `uncertainty-reporting`.
- **Source support:** `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ### When You Find Bugs`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ### Stop when you are unsure.`.

### CHG-LEG-004 — A seam needs an explicit enabling point

- **Category / claim:** legacy, architecture. A seam is useful only when the agent can identify the place where alternate behavior is selected and constrain that selection to the intended harness or runtime context.
- **Decision rule:** name the behavior to substitute, locate the enabling point, choose the least invasive language/build/runtime mechanism, prove production selection remains unchanged, and document removal or permanence. Prefer ordinary object/function/configuration seams over implicit link/preprocessor tricks when both are feasible.
- **Why / applicable / not:** “add an interface” is not a seam plan; control must be exercisable. Not every dependency needs substitution—only those blocking required sensing or separation.
- **Required / insufficient evidence:** required—dependency obstacle, enabling point, production/test selection path, concurrency/lifetime implications, verification. Insufficient—interface existence, mocking-framework availability, or desire for generic decoupling.
- **Inputs / outputs:** dependency and desired alternate; output is seam type, enabling point, scope, test, and cleanup policy.
- **Preservation / safe / unsafe:** preserve production binding. Safe—constructor parameter with existing default under compatible API authority. Unsafe—ambient global switch, hidden preprocessor branch, or public exposure solely for tests without contract review.
- **Failure modes / counterexample:** test-only production mode, global leakage, parallel-test races, permanent indirection. Counterexample: stable external boundary already injected needs no new seam.
- **Interactions / conflicts:** CHG-LEG-001, CHG-LEG-005, CHG-LEG-006; conflict `CONF-CL-008`.
- **Confidence / roles / languages / archetypes:** strong; legacy/repair/refactoring/architecture; language-independent principle, mechanics language-specific; weakly tested code.
- **Routes:** hard dependency, nondeterministic collaborator, static/global call; high; prerequisite identified test point; core, 400–600; related `enabling-point`.
- **Source support:** `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ### Object Seams`; `SRC-WELC: chapters/034-chapter-25-dependency-breaking-techniques.md :: ## Extract Interface`.

### CHG-LEG-005 — Separate sensing from collaborator realism

- **Category / claim:** legacy, testing. A fake or mock can make a local effect observable or isolate execution; it does not establish that the real collaborator, protocol, timing, persistence, or deployment integration works.
- **Decision rule:** use the simplest substitute that exposes the behavior under test. Pair it with contract/integration evidence when correctness depends on an external boundary. Prefer state/result observation over interaction assertions unless the interaction itself is contractual.
- **Why / applicable / not:** substitutes shrink feedback loops but can create false models. Not needed for cheap deterministic value collaborators.
- **Required / insufficient evidence:** required—what must be sensed, collaborator contract, substitute fidelity, integration layer. Insufficient—passing mocked test or number of verified calls alone.
- **Inputs / outputs:** observation need and boundary contract; output is fake/mock/stub/real choice plus missing-evidence note.
- **Preservation / safe / unsafe:** safe—small in-memory fake for a narrow owned protocol. Unsafe—reimplement a third-party system in a fake and infer integration correctness.
- **Failure modes / counterexample:** brittle interaction tests, divergent fake, overmocking internals. Counterexample: an interaction such as exactly-once durable enqueue may itself be the behavior under test.
- **Interactions / conflicts:** CHG-LEG-004, CHG-LEG-007, evidence taxonomy.
- **Confidence / roles / languages / archetypes:** strong; legacy/testing/repair/review; language-independent; services and external dependencies.
- **Routes:** mocks/fakes, hard collaborator; medium/high; prerequisite boundary contract; high, 300–500; related `sensing`, `separation`.
- **Source support:** `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: ## Faking Collaborators`; `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: #### Fake Objects Support Real Tests`; `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: ## Mock Objects`.

### CHG-LEG-006 — Minimal dependency breaking may be temporary scaffolding

- **Category / claim:** legacy, refactoring. Break only the dependency preventing a required observation or change; tolerate a clearly marked local design scar when it buys protection, then reassess it after the semantic goal is safe.
- **Decision rule:** rank candidate seams by production impact, scope, reversibility, and test leverage. Choose the smallest; isolate and name any temporary compromise; verify production behavior; schedule removal only if it remains costly after the change.
- **Why / applicable / not:** insisting on final architecture before tests recreates the legacy dilemma. Temporary does not excuse unsafe globals, hidden modes, or public-contract changes without authority.
- **Required / insufficient evidence:** required—blocking dependency, alternatives, scope, production invariants, removal/permanence criteria. Insufficient—testability as an abstract virtue.
- **Inputs / outputs:** obstacle/options; output is bounded enabling change and debt disposition.
- **Preservation / safe / unsafe:** safe—extract-and-override call under controlled subclass harness; parameterize method with current production value. Unsafe—redesign all dependencies or leave an untracked test hook.
- **Failure modes / counterexample:** scaffolding fossilizes, parallel state leaks, API pollution. Counterexample: a clean durable interface may be the smallest option if multiple production implementations already exist.
- **Interactions / conflicts:** CHG-LEG-004, CHG-LEG-008, CHG-REF-007; conflict `CONF-CL-008`.
- **Confidence / roles / languages / archetypes:** strong/contextual; legacy/refactoring/repair; mechanics language-specific; poorly tested systems.
- **Routes:** dependency blocks harness; high; prerequisite protection goal; high, 350–550; related `temporary-structure`.
- **Source support:** `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Break Dependencies`; `SRC-WELC: chapters/034-chapter-25-dependency-breaking-techniques.md :: ## Extract and Override Call`; `SRC-WELC: chapters/034-chapter-25-dependency-breaking-techniques.md :: ## Parameterize Method`.

### CHG-LEG-007 — Select tests from the effect surface

- **Category / claim:** legacy, testing, repair. Tests needed for a change are determined by the observable effects reachable from the change point, not by class boundaries or coverage targets alone.
- **Decision rule:** trace returned values, mutated parameters/objects, globals/statics, I/O, callbacks/events, exceptions, and downstream decisions; choose the nearest stable observations covering authorized and preserved paths; add broader coverage only for effects that cannot be localized.
- **Why / applicable / not:** effect reasoning controls test scope and identifies hidden coupling. Not a substitute for security, concurrency, or end-to-end tests whose risks cross the local graph.
- **Required / insufficient evidence:** required—call/effect sketch, mutation/side-effect inventory, exception paths, observation points. Insufficient—testing every public method, changed-line coverage, or class adjacency.
- **Inputs / outputs:** change point and effect graph; output is test-point list and uncovered uncertainty.
- **Preservation / safe / unsafe:** safe—test a pinch point plus a critical leaf. Unsafe—assume no returned value means no effect or expose private detail publicly without trade-off analysis.
- **Failure modes / counterexample:** missing async/deferred effect; overspecified internals; enormous high-level covering test. Counterexample: a pure local transformation’s effect surface may be only its return value.
- **Interactions / conflicts:** CHG-UNI-002, CHG-LEG-001, CHG-LEG-008.
- **Confidence / roles / languages / archetypes:** universal/strong; legacy/repair/testing/review; language-independent; all change types.
- **Routes:** what to test, hidden effects, weak coverage; high; prerequisite effect sketch; core, 350–550; related `effect-propagation`.
- **Source support:** `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Reasoning About Effects`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ### Effects and Encapsulation`.

### CHG-LEG-008 — Use interception and pinch points proportionally

- **Category / claim:** legacy, testing. A higher-level interception or pinch point can protect many effects with one test, but breadth trades away localization and may preserve unrelated behavior.
- **Decision rule:** choose the closest stable point that intercepts the relevant effect set. Use a higher pinch point first when breaking all leaf dependencies is disproportionate; then add narrower tests around changed logic and retire temporary broad tests if their maintenance cost exceeds continuing value.
- **Why / applicable / not:** this bounds preparation in tangled clusters. Not appropriate when the high-level path is nondeterministic, destructive, too slow, or misses the changed path.
- **Required / insufficient evidence:** required—effect sketch, paths converging at point, harness stability/cost, critical leaf gaps. Insufficient—architectural height or coverage percentage.
- **Inputs / outputs:** effect cluster; output is interception point, scope, supplemental tests, retention rule.
- **Preservation / safe / unsafe:** safe—temporary service-boundary characterization around a cluster. Unsafe—one end-to-end happy path claimed as comprehensive unit protection.
- **Failure modes / counterexample:** false confidence, slow/flaky suite, pinching at incidental implementation. Counterexample: stable public protocol boundary may be the enduring correct contract-test surface.
- **Interactions / conflicts:** CHG-LEG-007, CHG-LEG-013; conflict `CONF-CL-009`.
- **Confidence / roles / languages / archetypes:** strong/contextual; legacy/testing/refactoring; language-independent; tangled subsystems.
- **Routes:** many dependencies, cluster change, slow characterization; high; prerequisite effect graph; high, 350–550; related `pinch-point`.
- **Source support:** `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ## Interception Points`; `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: #### Pinch Point`; `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ## Traps Pinch Point Traps`.

### CHG-LEG-009 — Current work reveals responsibilities

- **Category / claim:** legacy, refactoring, domain. In a large unclear unit, the behavior currently being changed is the most reliable starting lens for discovering a responsibility; a complete ideal decomposition is not prerequisite.
- **Decision rule:** mark methods/data/effects involved in the current change, name their shared purpose, extract only when a cohesive boundary and protection exist, and defer unrelated clusters. Revisit after subsequent changes supply more evidence.
- **Why / applicable / not:** live change supplies semantic and temporal evidence. Not permission to force every current task into a new class/module.
- **Required / insufficient evidence:** required—current call/effect path, data relationships, change reason, nameable policy, test seam. Insufficient—class size, method grouping by position, or imagined full design.
- **Inputs / outputs:** current task slice; output is local responsibility map and retain/extract choice.
- **Preservation / safe / unsafe:** safe—extract implementation behind old interface before broader caller migration. Unsafe—design a complete hierarchy from a static read alone.
- **Failure modes / counterexample:** task-shaped fragmentation, duplicated invariants, temporary boundary mistaken as final. Counterexample: strong accepted domain architecture may already identify the right owner before current work.
- **Interactions / conflicts:** CHG-REF-004, CHG-LEG-010, CHG-HIST-009.
- **Confidence / roles / languages / archetypes:** strong/contextual; legacy/refactoring/coding/domain; language-independent; big class/module.
- **Routes:** large class, unclear responsibility, feature in legacy code; medium/high; prerequisite current change map; high, 350–550; related `responsibility-discovery`.
- **Source support:** `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## Seeing Responsibilities`; `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work`; `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## After Extract Class`.

### CHG-LEG-010 — Scratch refactoring is disposable investigation

- **Category / claim:** legacy, agent-conduct. Temporary structural edits can expose method structure, responsibilities, and effects, but insight—not the scratch diff—is the deliverable unless the edits are independently protected and authorized.
- **Decision rule:** work on an isolated/reversible copy, aggressively rename/extract/delete to learn, record discoveries, then discard. Reimplement only the smallest justified production campaign from the clean baseline with tests and review.
- **Why / applicable / not:** scratch work lowers fear without smuggling unverified edits into production. It is not necessary when static reading and tests already answer the question.
- **Required / insufficient evidence:** required—explicit scratch status, clean baseline, no external side effects, captured findings. Insufficient—scratch code “looks better” or happened to compile.
- **Inputs / outputs:** understanding question; output is responsibility/effect/dead-code hypotheses and no production diff by default.
- **Preservation / safe / unsafe:** safe—throwaway extraction on branch/worktree and discard. Unsafe—merge exploratory edits or delete apparently unused code without dynamic/build/deployment evidence.
- **Failure modes / counterexample:** user changes lost during discard; scratch becomes production; false dead-code conclusion. Counterexample: a protected extract performed during scratch may later be recreated as the first campaign.
- **Interactions / conflicts:** CHG-UNI-005, CHG-LEG-009, CHG-LEG-011.
- **Confidence / roles / languages / archetypes:** strong; legacy/assessment/refactoring; language-independent; poorly understood code.
- **Routes:** “don’t understand,” monster method, boundary discovery; medium; prerequisite isolation; normal, 300–450; related `disposable-probe`.
- **Source support:** `SRC-WELC: chapters/024-chapter-16-i-don-t-understand-the-code-well-enough-to-change-it.md :: ## Scratch Refactoring`; `SRC-WELC: chapters/024-chapter-16-i-don-t-understand-the-code-well-enough-to-change-it.md :: #### Understand the Effects of a Change`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: #### Backtrack.`.

### CHG-LEG-011 — Monster-method extraction starts with known, tiny pieces

- **Category / claim:** legacy, refactoring. When a large method lacks adequate tests, extract the smallest behavior whose inputs, outputs, and dependencies are understood; keep it in the current owner first and expect to redo it.
- **Decision rule:** prefer trusted automated extraction without mixed manual edits. Otherwise identify low-coupling sequences, introduce temporary sensing only if necessary, characterize critical effects, extract inside the current class/module, verify, and repeat. Move ownership only after responsibilities become clear.
- **Why / applicable / not:** this reduces simultaneous uncertainty and avoids premature destination design. Not a license for untested manual surgery in safety-critical paths.
- **Required / insufficient evidence:** required—sequence boundaries, variables/dependencies, effect observations, tool trust, reversal. Insufficient—line range, indentation alone, or desired final class diagram.
- **Inputs / outputs:** method/effect sketch; output is one bounded extraction or a stop decision.
- **Preservation / safe / unsafe:** safe—extract zero/low-dependency chunk and rerun checks. Unsafe—large manual move across classes while redesigning behavior.
- **Failure modes / counterexample:** parameter explosion, wrong chunk, sensing variable retained, extraction churn. Counterexample: a fully covered method can use ordinary catalog refactorings more directly.
- **Interactions / conflicts:** CHG-UNI-004, CHG-REF-006, CHG-LEG-010.
- **Confidence / roles / languages / archetypes:** strong/contextual; legacy/refactoring; language-independent principle; monster methods.
- **Routes:** long tangled method, no unit tests; high; prerequisite effect sketch; specialist, 450–650; related `extract-what-you-know`.
- **Source support:** `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: #### Extract What You Know`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: ### Extract to the Current Class First`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: #### Extract Small Pieces`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: #### Be Prepared to Redo Extractions`.

### CHG-LEG-012 — Sprout or wrap under deadline pressure

- **Category / claim:** legacy, implementation. When required behavior cannot safely enter an untestable body in time, place new logic in tested code and integrate it through a narrow sprout or wrapper, while recording its integration and design costs.
- **Decision rule:** use sprout when new behavior can be computed separately and called from the old path; use wrap when behavior must occur before/after or around the old behavior. Test new logic, characterize the call boundary if feasible, and treat the shape as staging unless it is cohesive on its own.
- **Why / applicable / not:** this confines new uncertainty but may not verify the old/new integration. Not appropriate when a small seam can cheaply bring the original path under test.
- **Required / insufficient evidence:** required—deadline/change need, inability to protect old body, narrow integration point, new-logic tests, explicit uncovered integration risk. Insufficient—desire to avoid understanding old code.
- **Inputs / outputs:** required feature and old boundary; output is sprout/wrap slice plus follow-up disposition.
- **Preservation / safe / unsafe:** safe—tested helper called once from characterized path. Unsafe—parallel subsystem, duplicated policy, or decorator stack with no integration verification.
- **Failure modes / counterexample:** architectural scar, stale duplication, untested call, context split. Counterexample: ordinary TDD inside already testable code is preferable.
- **Interactions / conflicts:** CHG-LEG-001, CHG-LEG-006, CHG-UNI-003; conflict `CONF-CL-008`.
- **Confidence / roles / languages / archetypes:** contextual/strong; coding/legacy/repair; language-independent; deadline-constrained legacy systems.
- **Routes:** urgent feature in untestable code; high; prerequisite narrow call point; specialist, 350–550; related `sprout-method`, `wrap-method`.
- **Source support:** `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Sprout Method`; `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ### Sprout Class`; `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Wrap Method`; `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Wrap Class`.

### CHG-LEG-013 — Temporary high-level safety nets are provisional

- **Category / claim:** legacy, testing. A broad end-to-end or UI characterization suite can enable initial restructuring when local tests are impossible, but its brittleness, cost, and localization weakness must be explicit.
- **Decision rule:** select critical user-visible scenarios and complex uncovered paths; stabilize environment and assertions; use the suite to protect the first seam/splinter; add narrower tests as code becomes separable; then retain or delete the provisional suite based on enduring contract value.
- **Why / applicable / not:** broad protection may be the only initial route, but “more realistic” is not automatically better. Avoid destructive live dependencies unless explicitly isolated and authorized.
- **Required / insufficient evidence:** required—critical scenarios, repeatability, environment controls, path coverage, maintenance cost, retirement criteria. Insufficient—one happy-path recording, screenshot count, or aggregate coverage alone.
- **Inputs / outputs:** user scenarios/change surface; output is provisional safety net and narrowing plan.
- **Preservation / safe / unsafe:** safe—black-box API characterization in isolated environment. Unsafe—flaky GUI playback treated as permanent comprehensive proof.
- **Failure modes / counterexample:** brittle tests block unrelated UI change, false confidence, leaked data/state. Counterexample: stable protocol end-to-end tests may remain valuable after local tests exist.
- **Interactions / conflicts:** CHG-LEG-008, CHG-HIST-010; conflict `CONF-CL-009`.
- **Confidence / roles / languages / archetypes:** contextual; legacy/testing/refactoring; language-independent; untestable central systems.
- **Routes:** no local seam, hotspot campaign; high; prerequisite isolated environment; specialist, 400–600; related `temporary-safety-net`.
- **Source support:** `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Introduce Provisional End-to-End Tests`; `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ### Test Coverings`.

### CHG-LEG-014 — Hyperaware testless editing is a last-resort bridge

- **Category / claim:** legacy, agent-conduct. When no meaningful test can exist before a dependency-breaking edit, risk is reduced—not eliminated—by one mechanical goal, preserved signatures, compiler/linker assistance, pairing/review, and immediate characterization afterward.
- **Decision rule:** first exhaust safe test/seam alternatives. If still blocked and the required enabling edit is authorized, make the smallest signature-preserving mechanical change; avoid design improvement; use compiler/static references and diff inspection; stop on ambiguity; add protection before semantic work.
- **Why / applicable / not:** sometimes protection requires an initial edit. It is contraindicated for broad semantic work, weak compilers/dynamic references, or irreversible external state.
- **Required / insufficient evidence:** required—proof no pre-change harness is practical, narrow enabling goal, reference/effect map, compiler/tool coverage, peer or heightened review, rollback. Insufficient—deadline alone or confidence from experience.
- **Inputs / outputs:** blocked harness and enabling edit; output is minimal mechanical bridge and immediate tests.
- **Preservation / safe / unsafe:** safe—signature-preserving extraction with compiler-checked references. Unsafe—rename/move across reflection or manually alter logic without observations.
- **Failure modes / counterexample:** compiler blind spots, accidental semantic reordering, bridge expands. Counterexample: trusted automated refactor with complete semantic model fits CHG-REF-006 instead.
- **Interactions / conflicts:** CHG-UNI-005, CHG-REF-006, CHG-LEG-006; conflict `CONF-CL-006`.
- **Confidence / roles / languages / archetypes:** contextual/contested; legacy/refactoring/repair; strongest in statically compiled code; weakly tested systems.
- **Routes:** first seam impossible under test; high/critical; prerequisite explicit last-resort justification; specialist, 400–600; related `single-goal-edit`.
- **Source support:** `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Hyperaware Editing`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Preserve Signatures`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Lean on the Compiler`.

### CHG-HIST-001 — Historical evidence prioritizes attention

- **Category / claim:** refactoring, review, architecture. Repository history is a triage lens that ranks where expert investigation may pay off; it does not diagnose bad design or authorize change.
- **Decision rule:** use history to form a candidate, then validate with current source, tests, runtime/incident evidence, roadmap, domain experts, and repository contracts before recommending action.
- **Why / applicable / not:** temporal evidence exposes forces invisible in a snapshot, but lacks causal and semantic context. Not applicable when history is absent, rewritten, irrelevant to the current product phase, or dominated by generated/migration churn.
- **Required / insufficient evidence:** required—clean scoped history plus at least one independent current evidence class. Insufficient—rank, churn count, heatmap color, ownership percentage, or code age alone.
- **Inputs / outputs:** repository log and current context; output is investigation queue with hypotheses/confidence, not a defect ledger.
- **Preservation / safe / unsafe:** safe—inspect top active complex files. Unsafe—auto-open refactoring tickets or evaluate authors from a metric.
- **Failure modes / counterexample:** metric reification, historical artifact bias, inactive branch pollution. Counterexample: a repeated incident can justify action independently, with history merely helping localization.
- **Interactions / conflicts:** CHG-REF-001, CHG-HIST-002, CHG-HIST-006; conflict `CONF-CL-010`.
- **Confidence / roles / languages / archetypes:** strong; repository assessment/refactoring/architecture/review; language-neutral; version-controlled systems.
- **Routes:** repo assessment, technical-debt prioritization; normal/high; exclude generated/vendor and corrupted history; prerequisite data audit; core, 300–450; related `evidence-triangulation`.
- **Source support:** `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Your Code Is Still a Crime Scene`.

### CHG-HIST-002 — Hotspot means active plus costly-to-reason-about candidate

- **Category / claim:** refactoring, repository assessment. A hotspot combines recent change activity with a rough complexity/size signal to locate code where poor maintainability would impose recurring cost.
- **Decision rule:** choose a product-relevant interval, clean noncode/generated/mass-migration data, rank change frequency, add an interpretable complexity proxy, then inspect the top candidates and their function-level distribution. Treat change frequency or size alone as incomplete.
- **Why / applicable / not:** frequently changed simple code and large stable code have different economics. Hotspots do not establish defects, low cohesion, or causation.
- **Required / insufficient evidence:** required—meaningful interval, clean file identity, frequency plus complexity, current inspection, task/roadmap relevance. Insufficient—raw LOC, cyclomatic threshold, lifetime commit count, or hottest file alone.
- **Inputs / outputs:** scoped history and source metrics; output is prioritized candidate list with reasons and false-positive notes.
- **Preservation / safe / unsafe:** safe—drill into functions and verify responsibilities. Unsafe—split hottest file automatically or call its authors poor performers.
- **Failure modes / counterexample:** generated files, formatting commits, historic refactor still ranked, frequency driven by healthy tests. Counterexample: stable safety-critical code may need review despite low hotspot rank.
- **Interactions / conflicts:** CHG-HIST-001, CHG-HIST-004, CHG-HIST-010.
- **Confidence / roles / languages / archetypes:** strong/contextual; assessment/refactoring/review; language-neutral with metric caveats; active products.
- **Routes:** hotspot/churn/large active file; normal/high; prerequisite data cleaning; high, 350–550; related `change-pressure`.
- **Source support:** `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## A Proxy for Interest Rate`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Use X-Rays to Get Deep Insights into Code`.

### CHG-HIST-003 — Co-change exposes a relationship hypothesis

- **Category / claim:** architecture, refactoring, repository assessment. Repeated co-change suggests a logical, technical, process, test, or organizational relationship that deserves explanation; expected coupling may be healthy.
- **Decision rule:** normalize commits/logical change sets, require enough support and coupling to reduce coincidences, search for surprising pairs/clusters, inspect the actual diffs and domain, and classify the relationship as expected, accidental, missing abstraction, omission risk, process artifact, or unresolved.
- **Why / applicable / not:** static dependencies miss cross-language, configuration, data, and workflow coupling. Co-change cannot prove the relationship’s direction or that it should be removed.
- **Required / insufficient evidence:** required—repeated normalized changes, denominator/degree, meaningful interval, diff inspection, task/ticket/domain context. Insufficient—one commit, percentage without support count, or adjacency in a graph.
- **Inputs / outputs:** history and file identity; output is classified relationship and next action/observation.
- **Preservation / safe / unsafe:** safe—use expected coupling as a change-planning reminder. Unsafe—merge modules solely because they co-change or demand tests always change with implementation.
- **Failure modes / counterexample:** broad commits, squash policy, codegen, mechanical renames, staged commits split one task. Counterexample: test and production file co-change may be desirable.
- **Interactions / conflicts:** CHG-REF-003, CHG-HIST-006, CHG-HIST-009, CHG-HIST-011.
- **Confidence / roles / languages / archetypes:** strong/contextual; architecture/refactoring/assessment/review; language-neutral; mono- and multi-repo.
- **Routes:** temporal/change coupling, omitted companion change, distributed dependency; normal/high; prerequisite clean logical changes; high, 400–600; related `surprise`, `co-change`.
- **Source support:** `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ### What Is Change Coupling?`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Detect Cochanging Files`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Learn More About Change Coupling`.

### CHG-HIST-004 — Trends matter more than absolute complexity scores

- **Category / claim:** refactoring, review. A complexity proxy becomes more actionable when its trajectory shows active accumulation or an unusual delta relative to the repository’s own baseline.
- **Decision rule:** select a stable proxy and sampling method, inspect the trend across relevant releases/branches, correlate increases with change purpose and function-level hotspots, and use relative warnings as prompts. Never treat a universal threshold as a blocker without repository validation.
- **Why / applicable / not:** languages, formatting, generated code, and local style bias absolute values. A falling score does not by itself prove improved design or behavior.
- **Required / insufficient evidence:** required—consistent metric, cleaned history, trend window, current source inspection, workload/product context. Insufficient—single present value or arbitrary ten-percent threshold.
- **Inputs / outputs:** historical revisions and metric; output is stable/rising/falling/step-change hypothesis with investigation target.
- **Preservation / safe / unsafe:** safe—review a steep increase in an active already-large unit. Unsafe—fail CI or refactor based only on score.
- **Failure modes / counterexample:** formatting/style effect, added necessary behavior, refactor moved complexity elsewhere. Counterexample: a formally bounded algorithm may have high essential branching but stable, well-tested behavior.
- **Interactions / conflicts:** CHG-HIST-002, CHG-HIST-012, CHG-REF-001.
- **Confidence / roles / languages / archetypes:** contextual/strong; assessment/refactoring/review; language-neutral proxy with language bias; active systems.
- **Routes:** complexity alert/trend, normalization of deviance; normal/high; prerequisite comparable samples; normal, 350–500; related `relative-baseline`.
- **Source support:** `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Evaluate Hotspots with Complexity Trends`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Know the Biases in Complexity Trends`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Wouldn't an Absolute and Universal Threshold Be Better?`.

### CHG-HIST-005 — Code age is a stability clue, not a quality verdict

- **Category / claim:** refactoring, architecture. Time since change can distinguish active from stable regions and suggest closure boundaries, but old may also mean dead, abandoned, paused, or too frightening to touch.
- **Decision rule:** choose a meaningful reference date, exclude generated content, interpret age inside domain/business boundaries, combine with runtime use, roadmap, incidents, tests, and ownership, then decide whether to leave, isolate, delete-investigate, or reorganize.
- **Why / applicable / not:** stable modules reduce cognitive load, but age cannot establish semantic cohesion or safety. Tests and specifications need not “age” in the same way as implementation.
- **Required / insufficient evidence:** required—last-change reference, product activity, runtime/dependency use, domain map, current risks. Insufficient—age histogram, no recent commits, or old authorship alone.
- **Inputs / outputs:** age map and current context; output is stability hypothesis and bounded action.
- **Preservation / safe / unsafe:** safe—avoid stable code or isolate behind an existing boundary. Unsafe—extract old package as library or delete it without use proof.
- **Failure modes / counterexample:** paused repo appears stable, dead code mistaken for valuable library, latent vulnerability. Counterexample: an old supported cryptographic implementation may require migration due to external standards.
- **Interactions / conflicts:** CHG-REF-008, CHG-HIST-006; conflict `CONF-CL-007`.
- **Confidence / roles / languages / archetypes:** contextual; architecture/refactoring/assessment; language-independent; mature repositories.
- **Routes:** old code, package stability, dead-code question; normal/high; prerequisite use/product evidence; normal, 350–550; related `stability`, `code-age`.
- **Source support:** `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Stabilize Code by Age`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### The Business Domain Is Above Age`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Scale from Files to Systems`.

### CHG-HIST-006 — Audit behavioral-data fitness before inference

- **Category / claim:** repository assessment, agent-conduct. History analysis is admissible only after checking whether repository practices preserve the entity, time, task, and author relationships the analysis assumes.
- **Decision rule:** inspect renames/moves, imports, squashes, code generation, vendoring, merge style, aliases/mailmap, pair/mob attribution, bots, formatting/migrations, branch scope, organizational change, and multi-repo ticket discipline. Downgrade or omit analyses whose assumptions fail.
- **Why / applicable / not:** clean-looking charts can encode bad provenance. Technical file-level history can remain usable when author-level social inference is not.
- **Required / insufficient evidence:** required—sample raw commits and repository policy; explicit exclusions/normalizations. Insufficient—tool success, commit count alone, or visually plausible output.
- **Inputs / outputs:** raw history/policies; output is fitness report per analysis: usable, corrected, limited, or invalid.
- **Preservation / safe / unsafe:** safe—exclude generated/noncode and consolidate aliases. Unsafe—silently repair uncertain attribution or present biased author metrics as fact.
- **Failure modes / counterexample:** erased history, copied repo credit, pair work attributed to one person, ticketless logical changes. Counterexample: source snapshot review needs no history fitness gate if it makes no historical claim.
- **Interactions / conflicts:** CHG-HIST-001, CHG-HIST-003, CHG-HIST-007, CHG-HIST-011.
- **Confidence / roles / languages / archetypes:** universal/strong; assessment/architecture/refactoring/review; language-independent; any history-mining task.
- **Routes:** Git mining, hotspot/co-change/ownership; all risk; prerequisite raw-log audit; core, 400–600; related `provenance-quality`.
- **Source support:** `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: #### Exclude Autogenerated Content`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: #### Watch Out for Authors with Multiple Aliases`.

### CHG-HIST-007 — Developer congestion is a risk hypothesis, not blame

- **Category / claim:** architecture, review, agent-conduct. Many independently acting contributors or teams in the same active code can indicate coordination and knowledge-diffusion pressure, but cannot establish individual fault or prescribe ownership in isolation.
- **Decision rule:** normalize team/author data, choose an organizationally meaningful interval, identify active fragmented areas, correlate with lead time, conflicts, defects, ownership and architecture, then consider review focus, test focus, boundary redesign, or responsibility changes with human context.
- **Why / applicable / not:** organizational structure can amplify change cost, yet contribution diversity may be deliberate and healthy. Pairing, rotations, bots, incident swarms, and open-source contribution models distort interpretation.
- **Required / insufficient evidence:** required—clean attribution, team structure, interval, actual coordination symptoms, interviews/context, technical dependency evidence. Insufficient—author count, fractal value, or “minor contributor” status alone.
- **Inputs / outputs:** social and technical maps; output is coordination hypothesis and options, never a personnel judgment.
- **Preservation / safe / unsafe:** safe—prioritize review/support in congested hotspot. Unsafe—restrict contributors or reorganize teams solely from Git statistics.
- **Failure modes / counterexample:** gatekeeper bottleneck, silo creation, attribution bias, fundamental attribution error. Counterexample: a broad emergency fix may legitimately touch the same code from many teams briefly.
- **Interactions / conflicts:** CHG-HIST-006, CHG-HIST-008, CHG-HIST-009; conflict `CONF-CL-011`.
- **Confidence / roles / languages / archetypes:** contextual/contested; architecture/review/assessment; language-independent; multi-team systems.
- **Routes:** ownership/congestion/Conway analysis; high social risk; prerequisite human/privacy authority and data audit; specialist, 450–650; related `sociotechnical-congruence`.
- **Source support:** `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Measure Coordination Needs`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: #### React to Developer Fragmentation`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Combine Social and Technical Information`.

### CHG-HIST-008 — Never use behavioral metrics for individual performance evaluation

- **Category / claim:** agent-conduct, review. Commit, LOC, hotspot, ownership, defect-attribution, and knowledge-map data must not be converted into individual productivity or performance judgments.
- **Decision rule:** restrict social metrics to communication, risk simulation, knowledge transfer, and system/team-level investigation under applicable privacy policy. Refuse individual ranking, scoring, or blame; explain missing situational context and Goodhart/adaptive effects.
- **Why / applicable / not:** measurement changes behavior, destroys the evidence source, discourages deletion/help/risky work, and cannot see task difficulty or mandate. Ordinary peer review of a concrete contribution is not aggregate performance scoring.
- **Required / insufficient evidence:** no evidence threshold earns automated individual productivity scoring from these signals. Human performance processes require separate lawful, contextual, authorized methods outside this doctrine.
- **Inputs / outputs:** proposed social analysis; output is allowed communication/risk use or refusal.
- **Preservation / safe / unsafe:** safe—find someone likely familiar with a module and ask. Unsafe—rank employees by commits, LOC, bugs, or knowledge-map area.
- **Failure modes / counterexample:** covert scoring under “risk,” public shaming, biased authorship. Counterexample: identifying maintainers for review routing is operational communication, not evaluation.
- **Interactions / conflicts:** CHG-HIST-007, authority/privacy doctrine.
- **Confidence / roles / languages / archetypes:** universal/strong prohibition; all agents; language-independent; all organizations.
- **Routes:** productivity, contributor rank, performance metric, blame; critical ethical/social risk; prerequisite none; core, 250–350; related `authority-discipline`.
- **Source support:** `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Don't Turn Knowledge Maps into Performance Evaluations`; `SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## Adaptive Behavior and the Destruction of a Data Source`; `SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## The Situation Is Invisible in Code`.

### CHG-HIST-009 — Co-change can nominate, not define, a domain boundary

- **Category / claim:** domain, architecture. Clusters that evolve together can nominate a cohesive component or bounded-context candidate, but domain language, invariants, data/authority ownership, and team responsibilities decide the boundary.
- **Decision rule:** find stable co-change clusters across technical layers, inspect repeated policies/data and semantic names, consult domain experts, map transactions and ownership, compare alternative cuts, and use a prototype/deletion test before committing to a migration.
- **Why / applicable / not:** history reveals how work cuts through the current structure, while commits may bundle convenience, rollout, or process artifacts. Directory names alone are equally insufficient.
- **Required / insufficient evidence:** required—co-change support, source similarity/policy, domain vocabulary, invariant/transaction ownership, caller/dependency map, team and deployment constraints. Insufficient—graph cluster, shared noun, or layer crossing alone.
- **Inputs / outputs:** temporal cluster and domain model; output is boundary candidate, alternatives, costs, and confidence.
- **Preservation / safe / unsafe:** safe—prototype extraction behind current facade. Unsafe—declare bounded context from Git or merge semantically distinct features because they co-change.
- **Failure modes / counterexample:** shared infrastructure masquerades as domain, feature bundle commits, distributed transaction cost ignored. Counterexample: a stable explicit ADR may outweigh a weak recent co-change pattern.
- **Interactions / conflicts:** CHG-REF-004, CHG-HIST-003, CHG-HIST-007; conflict `CONF-CL-012`.
- **Confidence / roles / languages / archetypes:** contextual; architecture/domain/refactoring; language-independent; layered monoliths and distributed systems.
- **Routes:** modularization, bounded context, cross-layer coupling; high; prerequisite domain expertise; specialist, 450–700; related `domain-integrity`.
- **Source support:** `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Look for Clusters of Cochanging Files`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### The Big Win Is in the Problem Domain`.

### CHG-HIST-010 — Splinter a congested hotspot through its stable facade

- **Category / claim:** refactoring, architecture, legacy. In an actively changed oversized hotspot, the first campaign may optimize safe parallel evolution rather than achieve the final design: extract one evidenced responsibility while retaining the original API as a temporary facade.
- **Decision rule:** verify active complexity/congestion and tests; identify responsibility groups; improve proximity; pick the group with highest relevant activity and a recognizable seam; copy/extract behind delegation; run regression checks; integrate quickly; repeat or stop based on new evidence.
- **Why / applicable / not:** short-lived facade-preserving slices reduce ripple and merge exposure. Not warranted by size alone, and a quiet coherent module may not need splintering.
- **Required / insufficient evidence:** required—hotspot plus complexity trend, parallel-development/roadmap pressure, responsibility map, safety net, short integration path. Insufficient—20,000 lines or crowded file alone.
- **Inputs / outputs:** hotspot evidence/candidate groups; output is first 1–small-slice campaign, facade, tests, and follow-up signals.
- **Preservation / safe / unsafe:** safe—one behavior extraction with original signatures. Unsafe—long branch, all-at-once split, client migration before local equivalence.
- **Failure modes / counterexample:** permanent middle man, low-cohesion splinters, duplicate shared code, branch drift. Counterexample: inactive hotspot-like historic file should first pass CHG-REF-008.
- **Interactions / conflicts:** CHG-REF-007, CHG-LEG-013, CHG-HIST-002; conflict `CONF-CL-005`.
- **Confidence / roles / languages / archetypes:** contextual/strong; refactoring/architecture/legacy; language-independent; large active modules.
- **Routes:** congested hotspot, large-file campaign; high; prerequisite safety net and campaign authority; specialist, 500–750; related `facade-preservation`, `campaign-sizing`.
- **Source support:** `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Parallel Development Is at Conflict with Refactoring`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters`.

### CHG-HIST-011 — Build logical change sets across repository boundaries

- **Category / claim:** architecture, repository assessment. Repository and process boundaries do not eliminate logical coupling; cross-repository analysis must group commits by a defensible shared task before inferring co-change.
- **Decision rule:** prefer explicit ticket/change identifiers; otherwise use a documented time-plus-author/team window with lower confidence. Prefix entity identity by repository, normalize clocks/authors, inspect cross-boundary clusters, then verify protocols, deployments, tests, and team ownership.
- **Why / applicable / not:** same-commit coupling cannot see work split across repos, while time windows create false positives. Not needed for a monorepo with atomic task commits unless commits still split one logical change.
- **Required / insufficient evidence:** required—repository inventory, task linkage or window rationale, support/degree, source/protocol inspection. Insufficient—same-day changes alone or shared filenames.
- **Inputs / outputs:** multi-repo logs and task data; output is cross-repo dependency hypothesis with confidence and affected teams/protocols.
- **Preservation / safe / unsafe:** safe—use coupling to plan companion tests/reviews. Unsafe—collapse services or transfer ownership solely from correlation.
- **Failure modes / counterexample:** release trains, dependency bumps, synchronized formatting, timezone errors. Counterexample: explicit ticket linking the same feature across repos provides stronger evidence.
- **Interactions / conflicts:** CHG-HIST-003, CHG-HIST-006, CHG-HIST-007; conflict `CONF-CL-012`.
- **Confidence / roles / languages / archetypes:** contextual; architecture/assessment/planning; language-independent; multi-repo and microservice systems.
- **Routes:** distributed system, microservices, multi-repo change planning; high; prerequisite task/history quality; specialist, 400–650; related `logical-change-set`.
- **Source support:** `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: #### Use Logical Change Sets to Group Commits`; `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Detect Implicit Dependencies Between Microservices`; `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Detect Microservices Shotgun Surgery`.

### CHG-HIST-012 — Early warnings remain review prompts

- **Category / claim:** review, refactoring. Rising hotspot rank, steep relative complexity growth, or a missing usually co-changed file should trigger focused review, never automatic rejection or forced companion edits.
- **Decision rule:** compare against a repository-relative baseline; suppress small/noisy/generated cases; present the specific historical pattern; let the author explain intentional divergence; inspect current semantics and tests; update the baseline as coupling changes.
- **Why / applicable / not:** proactive evidence catches risk early but must allow legitimate growth and refactoring that breaks old coupling.
- **Required / insufficient evidence:** required—clean baseline, minimum support, meaningful delta, current diff, author/domain context. Insufficient—universal percentage/rank threshold or historical habit alone.
- **Inputs / outputs:** pending diff plus trend/coupling baseline; output is warning, explanation, and accepted/changed/escalated disposition.
- **Preservation / safe / unsafe:** safe—nonblocking warning with bypass rationale. Unsafe—CI forces historical coupling or complexity ceiling regardless of task.
- **Failure modes / counterexample:** alert fatigue, normalization of bad baseline, coupling fossilization, gaming. Counterexample: repository contract may make a generated companion update mandatory for reasons independent of history.
- **Interactions / conflicts:** CHG-HIST-003, CHG-HIST-004, CHG-HIST-006.
- **Confidence / roles / languages / archetypes:** contextual; review/refactoring/coding; language-neutral; active CI repositories.
- **Routes:** rising hotspot, complexity delta, omitted co-change; medium/high; prerequisite clean baseline; normal, 300–500; related `review-prompt`.
- **Source support:** `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Identify Steep Increases in Complexity`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Detect Future Hotspots`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Catch the Absence of Change`.

## Negative doctrine

These prohibitions are deliberately narrower than slogans. Each states the evidence boundary that makes it operational.

| ID | Prohibition and evidence boundary | Source support |
|---|---|---|
| `NEG-CL-001` | Never label behavior-changing work “refactoring.” If accepted outputs, errors, side effects, persisted state, protocols, resource semantics, or compatibility intentionally change, classify and authorize that semantic delta separately. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`; `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software` |
| `NEG-CL-002` | Never combine an unverified semantic repair with a nominally behavior-preserving move. Establish the repair with its own oracle and green boundary before structural work. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing` |
| `NEG-CL-003` | Never infer preservation from compilation, a type checker, or a narrow happy-path test alone. Name observable boundaries and check proportionally to their risk. | `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Risky Change`; `SRC-REF: chapters/008-chapter-4-building-tests.md :: ## The Value of Self-testing Code` |
| `NEG-CL-004` | Never refactor solely because a file, class, or method is large. Require independently evolving responsibilities, a current change/test/review pressure, and a seam whose extraction improves locality. | `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## Seeing Responsibilities`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge` |
| `NEG-CL-005` | Never treat a smell or metric as a verdict. Convert it to a falsifiable maintenance hypothesis and inspect current repository context. | `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code`; `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ### Complex Questions Require Context` |
| `NEG-CL-006` | Never remove duplication before establishing shared knowledge and expected co-evolution. Similar text in distinct domains, examples, tests, vendors, or independently owned code may be intentionally local. | `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity` |
| `NEG-CL-007` | Never add an interface merely to “decouple” or “make testable.” Identify the blocked dependency, the enabling point, the substitute behavior, and why a smaller seam is insufficient. | `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point`; `SRC-WELC: chapters/034-chapter-25-dependency-breaking-techniques.md :: ## Extract Interface` |
| `NEG-CL-008` | Never expose private implementation publicly solely for a test without API and encapsulation trade-off review. Prefer a seam at an existing boundary or temporary controlled hook. | `SRC-WELC: chapters/018-chapter-10-i-can-t-run-this-method-in-a-test-harness.md :: # Chapter 10: I Can't Run This Method in a Test Harness`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ### Effects and Encapsulation` |
| `NEG-CL-009` | Never make a production test mode implicit. Every seam must have an explicit enabling point, production default, scope/lifetime, and parallel-execution safety. | `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point` |
| `NEG-CL-010` | Never silently fix surprising behavior found during characterization. Verify, document, seek expected-behavior evidence, and obtain repair authority. | `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ### When You Find Bugs`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests` |
| `NEG-CL-011` | Never demand complete legacy-system understanding or global coverage before a bounded change. Protect the relevant effect surface and report remaining uncertainty. | `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## A Heuristic for Writing Characterization Tests` |
| `NEG-CL-012` | Never let a temporary seam, sensing variable, sprout, wrapper, facade, or broad characterization test become permanent by omission. Record whether it is durable, provisional, or scheduled for reassessment. | `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ### Summary`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Introduce Provisional End-to-End Tests` |
| `NEG-CL-013` | Never perform a broad manual refactor without intermediate verification because the final design is clearer. Reduce the step or improve the feedback surface first. | `SRC-REF: chapters/005-chapter-1-refactoring-a-first-example.md :: ## Final Thoughts`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: ## The Manual Refactoring Challenge` |
| `NEG-CL-014` | Never trust bulk textual replacement as semantic refactoring. Preview the edit set, account for dynamic/config/generated/foreign-language references, and run repository checks. | `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`; `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ### Undo` |
| `NEG-CL-015` | Never change a published API, deployed protocol, or persisted schema under an internal-refactoring assumption. Inventory independent consumers and use a compatibility migration unless atomic control is proven. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Changing Interfaces`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Databases` |
| `NEG-CL-016` | Never call high churn poor design without examining why the code changes. Healthy tests, central policy, active new capability, migrations, or generated artifacts can all churn. | `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Detect Future Hotspots` |
| `NEG-CL-017` | Never infer a defect, dependency direction, or architectural remedy from co-change alone. Inspect diffs, support count, task context, source, protocols, and domain meaning. | `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Detect Cochanging Files`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Learn More About Change Coupling` |
| `NEG-CL-018` | Never infer a domain or team boundary from folders, graph clusters, or directory names alone. Require domain language, invariant/data authority, transaction/change forces, and human context. | `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### The Big Win Is in the Problem Domain` |
| `NEG-CL-019` | Never interpret old code as good, dead, safe, or reusable solely because it is unchanged. Verify product activity, runtime use, roadmap, defects, and external support/security constraints. | `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code` |
| `NEG-CL-020` | Never delete tests because they are old, small, or do not co-grow with production code. Prove they exercise no supported risk, duplicate stronger protection, impose real cost, and are removable under test-owner authority. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Reduce Debt by Deleting Cost Sinks`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Test Cases Don't Age Well` |
| `NEG-CL-021` | Never let generated, vendored, formatting, merge, migration, or noncode artifacts dominate a maintainer-facing hotspot/co-change inventory. Clean or separately classify them and disclose exclusions. | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ### Clean Your Input Data`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: #### Exclude Autogenerated Content` |
| `NEG-CL-022` | Never use commit, LOC, defect-attribution, ownership, hotspot, or knowledge-map data for individual productivity/performance scoring. No threshold makes the missing situational context or adaptive harm acceptable. | `SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## Adaptive Behavior and the Destruction of a Data Source`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Don't Turn Knowledge Maps into Performance Evaluations` |
| `NEG-CL-023` | Never treat author/team history as current truth before resolving aliases, pair/mob work, bots, squashes, copied repositories, and organizational-change dates. Downgrade or omit the social inference if repair is unreliable. | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ### Specify a Start Date with Organizational Significance` |
| `NEG-CL-024` | Never force historically co-changed files to remain co-changed. A warning must allow intentional divergence, because refactoring may remove the old relationship. | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Catch the Absence of Change`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Learn More About Change Coupling` |
| `NEG-CL-025` | Never start a long isolated refactoring branch for a congested hotspot without explicit integration evidence. Prefer small facade-preserving slices with short lead time; use isolation only when repository workflow proves it reduces rather than defers conflict. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Parallel Development Is at Conflict with Refactoring`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters` |
| `NEG-CL-026` | Never assume distribution, microservices, or repository splits remove dependencies. Trace protocols, data, deployment, logical change sets, and ownership; distributed coupling may be harder to see and operate. | `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Distribution Won't Cure the Dependency Blues`; `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Detect Microservices Shotgun Surgery` |

## Conflict registry

### CONF-CL-001 — Refactoring versus concurrent defect repair

- **Positions:** (A) keep strict behavior preservation and separate hats; (B) correct suspicious behavior while restructuring because the defect is visible and nearby.
- **Hidden assumptions:** A assumes current behavior is valuable or at least not authorized to change; B assumes an authoritative oracle exists and bundling will not obscure regression attribution.
- **Evidence favoring A / B:** A—undocumented/deployed behavior, weak tests, independent callers, disputed expectation. B—explicit acceptance criteria, failing regression test, repair authority, isolated semantic delta.
- **Decision rule:** default to A. If B’s evidence exists, make repair and refactoring separate verified slices even when in one larger authorized work item.
- **Unresolved questions:** whether a behavior is a defect; whether old clients rely on it; whether regulatory/security urgency changes sequencing.
- **Roles affected:** repair, refactoring, coding, review, legacy.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ### When You Find Bugs`.

### CONF-CL-002 — Opportunistic refactoring versus evidence-ranked campaigns

- **Positions:** (A) refactor in small bursts adjacent to feature/repair work; (B) prioritize deliberate hotspot/splinter campaigns based on recurring historical and organizational cost.
- **Hidden assumptions:** A assumes pressure is locally visible and ordinary work can pay the cost; B assumes debt is too central/congested for incidental improvement and history is fit for ranking.
- **Evidence favoring A / B:** A—small local friction, adequate tests, limited coordination, immediate change goal. B—active complexity trend, repeated co-change/defects, many teams, blocked flow, no single feature can safely absorb the work.
- **Decision rule:** choose A for bounded local pressure; choose B when triangulated evidence shows system-level recurring cost and campaign authority exists. In B, still deliver small verified slices.
- **Unresolved questions:** roadmap stability, opportunity cost, capacity, ownership, and whether measurement excludes migrations/generated churn.
- **Roles affected:** refactoring, architecture, repository assessment, planning.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern`.

### CONF-CL-003 — Abstraction versus duplication/proximity

- **Positions:** (A) extract shared code to one source of truth; (B) retain or colocate duplication to preserve local clarity and independent evolution.
- **Hidden assumptions:** A assumes one semantic concept and stable variation; B assumes different domain meanings, ownership, or future trajectories despite text similarity.
- **Evidence favoring A / B:** A—repeated coupled edits, omission defects, same invariant/policy, strong similarity with nameable variation. B—little duplicated knowledge, independently owned contexts, examples/tests lose communicative value, control flags needed to unify.
- **Decision rule:** extract only when semantic identity plus co-evolution outweigh abstraction/ownership cost; otherwise retain and optionally apply proximity with a rationale.
- **Unresolved questions:** future divergence, acceptable local code volume, and whether cross-boundary coordination will exceed omission risk.
- **Roles affected:** coding, refactoring, review, architecture.
- **Source support:** `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Duplicated Code`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`.

### CONF-CL-004 — Small methods/classes versus deep cohesive modules

- **Positions:** (A) extract small named chunks and classes to lower working-memory load; (B) keep behavior together when extraction creates navigation, delegation, parameter, or information-hiding cost.
- **Hidden assumptions:** A assumes names replace detail and boundaries align with responsibilities; B assumes the unit has one policy, shared invariants, and a compact interface despite internal size.
- **Evidence favoring A / B:** A—independently changing sequences, distinct data, mixed abstraction levels, high local effect complexity. B—one cohesive algorithm, shared state/invariants, few stable entry points, extraction would make chatty shallow units.
- **Decision rule:** optimize for local reasoning at the caller and change site, not raw size. Extract a nameable independently evolving chunk; retain deep cohesive implementation details behind a small boundary.
- **Unresolved questions:** navigation/tooling cost, language conventions, and whether future changes will separate responsibilities.
- **Roles affected:** coding, refactoring, review, architecture.
- **Source support:** `SRC-REF: chapters/010-chapter-6-composing-methods.md :: ## Extract Method`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: #### Extract Small Pieces`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Turn Hotspot Methods into Brain-Friendly Chunks`.

### CONF-CL-005 — Broad redesign/rewrite versus incremental transformation

- **Positions:** (A) replace a deeply flawed system with a new coherent architecture; (B) evolve the existing system through protected facades, splinters, and migrations.
- **Hidden assumptions:** A assumes requirements can be rediscovered, replacement can catch up, and technology/architecture blocks incremental change; B assumes old behavior remains valuable and seams can be introduced safely.
- **Evidence favoring A / B:** A—unsupported platform, hard performance/scale ceiling, recruitment/support impossibility, inability to stabilize even after bounded attempts. B—hidden domain rules, active feature stream, valuable deployed behavior, feasible compatibility seams, high replacement catch-up risk.
- **Decision rule:** default to B. Recommend A only with explicit business authority, requirements-discovery/migration plan, parallel-maintenance cost, acceptance proof, and evidence that incremental options cannot meet constraints.
- **Unresolved questions:** true feature set, data migration, cutover/rollback, old-system lifetime, and knowledge reset.
- **Roles affected:** architecture, legacy, refactoring, planning.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?`; `SRC-WELC: chapters/032-chapter-24-we-feel-overwhelmed-it-isn-t-going-to-get-any-better.md :: # Chapter 24: We Feel Overwhelmed. It Isn't Going to Get Any Better`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## The Trade-Off Between Architectural Refinements and Replacement Systems`.

### CONF-CL-006 — Tests-before-change versus compiler/tool-supported enabling edits

- **Positions:** (A) establish tests before production edits; (B) use trusted automated mechanics or hyperaware compiler-assisted edits to create the first test seam.
- **Hidden assumptions:** A assumes a harness is reachable without changing code; B assumes the operation is mechanical, compiler/tool coverage is strong, and scope can remain singular.
- **Evidence favoring A / B:** A—existing observation point or cheap nonproduction seam. B—circular legacy dilemma, statically resolved references, preserved signatures, reversible tiny edit, no semantic goal yet.
- **Decision rule:** exhaust A first. Permit B only as explicit last-resort enabling work with no mixed redesign, preview/diff review, rollback, and immediate characterization.
- **Unresolved questions:** reflection/configuration blind spots, concurrency effects, and tool semantic model coverage.
- **Roles affected:** legacy, refactoring, repair, review.
- **Source support:** `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### The Legacy Code Dilemma`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Lean on the Compiler`; `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`.

### CONF-CL-007 — Stable old code versus proactive improvement

- **Positions:** (A) leave old stable code untouched because time has reduced active defect/change cost; (B) improve or replace it before latent design, security, support, or knowledge risk materializes.
- **Hidden assumptions:** A assumes stability reflects use-tested maturity; B assumes inactivity hides unacceptable external or future risk.
- **Evidence favoring A / B:** A—runtime use, low incidents/churn, no roadmap pressure, supported dependencies, high characterization risk. B—known vulnerability, unsupported platform, imminent change, durability/safety gap, abandoned expertise in a critical domain, or dead-code proof.
- **Decision rule:** age adjusts priority but never decides. Combine runtime/roadmap/incidents/support/criticality and choose leave, isolate, characterize, delete, migrate, or repair.
- **Unresolved questions:** hidden users, dormant feature, upcoming regulation, and whether “stable” is merely fear-driven avoidance.
- **Roles affected:** architecture, legacy, refactoring, security/review.
- **Source support:** `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?`.

### CONF-CL-008 — Temporary seam quality versus long-term design quality

- **Positions:** (A) accept a local seam/sprout/wrapper scar to gain feedback quickly; (B) introduce only a durable architecture-quality boundary.
- **Hidden assumptions:** A assumes immediate characterization value dominates temporary complexity; B assumes final design is sufficiently understood and affordable now.
- **Evidence favoring A / B:** A—urgent required change, untestable dependency, narrow reversible hook, uncertainty about final responsibility. B—multiple real implementations, stable policy/mechanism boundary, public extension need, or temporary hook would create global/runtime risk.
- **Decision rule:** choose the least risky option that enables protection; label lifecycle explicitly. Prefer B when its boundary is independently earned, otherwise use A and reassess after learning.
- **Unresolved questions:** cleanup ownership/date, public compatibility, and whether the temporary seam will attract production use.
- **Roles affected:** legacy, coding, architecture, refactoring.
- **Source support:** `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`; `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ### Advantages and Disadvantages`; `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Break Dependencies`.

### CONF-CL-009 — Broad characterization versus narrow unit protection

- **Positions:** (A) use high-level covering/end-to-end tests to protect tangled behavior quickly; (B) break dependencies and write fast localized tests.
- **Hidden assumptions:** A assumes stable broad observable behavior and manageable environment cost; B assumes seams can be introduced without disproportionate risk.
- **Evidence favoring A / B:** A—cluster converges at a stable pinch point, local harness impossible initially, critical user scenarios. B—deterministic local seam, need for fault localization, repeated development, expensive/flaky E2E environment.
- **Decision rule:** start at the narrowest practical stable observation. If that is broad, make it provisional and narrow protection as structure permits; retain broad tests only for enduring system contracts.
- **Unresolved questions:** acceptable runtime/flakiness, missing rare paths, and retirement criteria.
- **Roles affected:** legacy, testing, repair, refactoring.
- **Source support:** `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: #### Higher-Level Interception Points`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net`.

### CONF-CL-010 — Static snapshot judgment versus behavioral prioritization

- **Positions:** (A) inspect current structure/tests directly; (B) use history to rank hotspots, co-change, trends, age, and ownership.
- **Hidden assumptions:** A assumes current structure exposes the relevant problem; B assumes history is clean and past behavior predicts near-term cost.
- **Evidence favoring A / B:** A—new repo, rewritten/imported history, explicit current defect/security contract. B—large mature repo, scarce review capacity, meaningful activity, need to prioritize among many plausible candidates.
- **Decision rule:** use B to allocate investigation attention when fit; use A and runtime/domain evidence to decide. Neither replaces repository contracts.
- **Unresolved questions:** analysis window, structural moves, seasonality, and roadmap discontinuity.
- **Roles affected:** repository assessment, refactoring, architecture, review.
- **Source support:** `SRC-SDX: chapters/004-the-world-of-behavioral-code-analysis.md :: # The World of Behavioral Code Analysis`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Inspect the Code`; `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code`.

### CONF-CL-011 — Code ownership versus broad knowledge boundaries

- **Positions:** (A) give a person/pair/small team clear operational responsibility and acceptance authority; (B) allow broad shared contribution to avoid silos and single-person risk.
- **Hidden assumptions:** A assumes responsibility reduces diffusion and coordination; B assumes shared knowledge improves resilience/innovation and contribution can be coordinated.
- **Evidence favoring A / B:** A—fragmented congested hotspot, no maintainer, repeated conflicts, quality drift. B—knowledge-loss risk, cross-team dependencies, need for rotations/reviews, excessive gatekeeper delay.
- **Decision rule:** keep operational responsibility narrower than knowledge boundaries: named accountable team, open contribution with review, deliberate cross-team learning and backup expertise. Do not infer personnel action from Git alone.
- **Unresolved questions:** team scale, reviewer capacity, succession, motivation, and organizational authority.
- **Roles affected:** architecture, review, repository assessment, management-facing agents.
- **Source support:** `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Code Ownership Means Responsibility`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Provide Broad Knowledge Boundaries`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Not All Teams Are Equal`.

### CONF-CL-012 — Direct coupling/collocation versus boundary indirection/distribution

- **Positions:** (A) colocate code that changes together and use direct coupling for local clarity; (B) separate behind interfaces/services/repositories for independent evolution, deployment, ownership, or policy/mechanism boundaries.
- **Hidden assumptions:** A assumes a single concept/owner/lifecycle; B assumes independence is real enough to repay protocol, operation, testing, and coordination cost.
- **Evidence favoring A / B:** A—persistent co-change, same domain capability, cross-boundary shotgun surgery, no independent deployment/security need. B—different scaling/deployment/security/data authority, multiple implementations, stable protocol, independent teams and release cadence.
- **Decision rule:** pick the boundary that localizes the dominant demonstrated forces. Do not distribute to cure code coupling, and do not merge solely from co-change; prototype and measure change/deployment effects.
- **Unresolved questions:** transaction ownership, failure modes, latency, rollback, team structure, and future variation.
- **Roles affected:** architecture, refactoring, domain, operations.
- **Source support:** `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`; `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Optimize for Sociotechnical Congruence Across Boundaries`; `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Distribution Won't Cure the Dependency Blues`.

### CONF-CL-013 — Comments versus self-documenting structure

- **Positions:** (A) extract/rename so code communicates itself and remove comments that narrate mechanics; (B) retain comments that preserve rationale, constraints, intentional duplication, uncertainty, or nonlocal contracts.
- **Hidden assumptions:** A assumes structure can encode the knowledge; B assumes the knowledge is causal/contextual and absent from syntax.
- **Evidence favoring A / B:** A—comment paraphrases code or marks a nameable block/responsibility. B—why-not alternatives, external constraint, protocol nuance, deliberate divergence, safety invariant.
- **Decision rule:** improve structure when it can carry the meaning; keep concise verified rationale that code cannot express, and update it with the governed behavior.
- **Unresolved questions:** documentation ownership and how to test comment-linked assumptions.
- **Roles affected:** coding, review, refactoring, legacy.
- **Source support:** `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ### Comments`; `SRC-SDX: chapters/012-chapter-6-spot-your-system-s-tipping-point-is-software-too-hard-divide-and-conquer-with-architectural-hotspots-analyze-subsystems-fight-the-normalization-of-deviance-toward-team-oriented-measures-exercises.md :: ## Ask the Right Questions`.

## Deterministic procedures

### PROC-CL-001 — Classify a proposed change

- **Inputs:** user request, acceptance criteria, current/desired observations, API/schema/deployment contracts, proposed diff.
- **Evidence required:** authoritative desired behavior and current boundary observations.
- **Decision steps:** (1) list intended observable deltas; (2) list invariants; (3) classify primary purpose as feature, repair, refactoring, optimization, migration, cleanup/deletion, or hardening; (4) split mixed purposes into ordered slices; (5) map authority and protection per slice.
- **Outputs:** change-type record, semantic delta, preservation boundary, slice order.
- **Stop conditions:** desired behavior or caller contract is unknown; label conflicts with actual delta.
- **Escalation:** behavior choice, public compatibility, irreversible data/operational change, or missing authority.
- **Common false positives:** calling a behavior change refactoring because code moves; calling dead-code deletion semantic-free without runtime/build proof; treating resource-semantic optimization as structure only.
- **Source support:** `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`.

### PROC-CL-002 — Establish preservation boundaries

- **Inputs:** classified change, requirements/ADRs, callers, tests, schemas/protocols, runtime/incident evidence.
- **Evidence required:** at least one authoritative or observed source for each material surface; unknowns explicitly marked.
- **Decision steps:** (1) inventory outputs, errors, side effects, persisted data, ordering/timing/durability, compatibility; (2) remove authorized deltas; (3) rank remaining invariants by consequence and uncertainty; (4) assign test/characterization/static/runtime protection; (5) identify unprotected unknowns and owner.
- **Outputs:** surface × invariant × evidence × check × confidence matrix.
- **Stop conditions:** a high-consequence surface lacks both evidence and a safe observation method.
- **Escalation:** disputed behavior, external consumer, destructive data/state, safety/security implications.
- **Common false positives:** preserving private implementation shape; assuming existing tests enumerate all behavior; omitting errors or side effects.
- **Source support:** `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Risky Change`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation`.

### PROC-CL-003 — Determine whether refactoring is earned

- **Inputs:** requested/current work, smell/metric findings, change/defect/review/test history, responsibility and dependency map.
- **Evidence required:** concrete current/imminent pressure and a causal hypothesis connecting structure to cost.
- **Decision steps:** (1) state the goal without a transformation name; (2) enumerate pressure evidence; (3) falsify metric/smell artifacts; (4) generate retain, document, proximity, local refactor, and campaign options; (5) predict pressure reduction and new costs; (6) choose the smallest net-positive reversible option.
- **Outputs:** earned/not-earned/uncertain decision, first action, verification and no-change rationale.
- **Stop conditions:** only aesthetics or generic doctrine supports action; preservation cannot be protected; target architecture not authorized.
- **Escalation:** work crosses public/architectural/data boundaries or requires product capacity.
- **Common false positives:** large file, old code, high churn, smell detector, disliked style, low coverage alone.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge`.

### PROC-CL-004 — Select the first refactoring campaign

- **Inputs:** ranked pressures/candidates, preservation matrix, test seams, ownership/parallel-work map, integration cadence.
- **Evidence required:** candidate whose change pressure, protection, and seam are stronger than alternatives.
- **Decision steps:** (1) exclude semantic repairs and migrations into separate slices; (2) rank candidates by recurring cost × risk reduction × seam quality × reversibility ÷ coordination cost; (3) choose one responsibility or effect surface; (4) define ≤ one coherent independently useful outcome; (5) order enabling characterization, mechanical moves, verification, and integration; (6) set stop/reversal signals.
- **Outputs:** one bounded campaign, not a backlog dump; deferred-candidate ledger.
- **Stop conditions:** no candidate has adequate protection or local value; parallel changes make the slice stale before integration.
- **Escalation:** campaign needs architectural authority, long freeze, schema/API migration, or cross-team scheduling.
- **Common false positives:** highest LOC/complexity automatically first; easiest cleanup unrelated to goal; selecting final architecture before first seam.
- **Source support:** `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ## Get used to picking a goal.`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities`.

### PROC-CL-005 — Work safely in poorly characterized code

- **Inputs:** authorized change, suspected change point, build/run path, dependencies and current tests.
- **Evidence required:** repeatable baseline at some observation level and reversible edit path.
- **Decision steps:** (1) identify change points; (2) trace effects; (3) choose nearest viable test point; (4) identify the one dependency blocking execution/sensing; (5) add the least invasive seam; (6) characterize relevant actual behavior; (7) implement semantic slice; (8) verify preservation; (9) optionally refactor on green.
- **Outputs:** safe-change route, tests, semantic diff, uncertainty ledger.
- **Stop conditions:** no safe baseline, destructive environment cannot be isolated, or behavior/authority is disputed.
- **Escalation:** suspected defect, public boundary, production-only state, safety/durability risk.
- **Common false positives:** demanding all dependencies be broken; global coverage target; treating fake-based unit result as integration proof.
- **Source support:** `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm`; `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: # Chapter 3: Sensing and Separation`.

### PROC-CL-006 — Write targeted characterization tests

- **Inputs:** planned change/effect surface, runnable observation point, representative inputs and state.
- **Evidence required:** repeatable actual observations and relevance to the change.
- **Decision steps:** (1) choose one relevant invocation/path; (2) make an initial assertion; (3) observe actual value/effect; (4) rule out harness error/nondeterminism; (5) encode actual behavior; (6) add boundary/error/special cases likely to distinguish the planned change; (7) stop when the relevant effect surface can detect unintended change.
- **Outputs:** targeted baseline tests and suspicious/unknown behavior ledger.
- **Stop conditions:** results are nondeterministic or destructive without control; observed behavior conflicts with authoritative specification.
- **Escalation:** possible defect or unclear expected behavior.
- **Common false positives:** snapshots without review; broad output captures containing timestamps/IDs; characterizing irrelevant branches; assuming observed means correct.
- **Source support:** `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## A Heuristic for Writing Characterization Tests`.

### PROC-CL-007 — Select a dependency seam

- **Inputs:** blocked test/change, dependency call path, language/build/runtime mechanisms, API constraints.
- **Evidence required:** exact obstacle and explicit alternate behavior needed.
- **Decision steps:** (1) state sensing/separation goal; (2) locate candidate enabling points; (3) enumerate existing boundary, parameter/function, object, factory/getter, subclass override, link/build, and preprocessor options; (4) rank by production impact, scope, concurrency safety, compatibility, reversibility, and durability; (5) implement smallest; (6) prove production binding unchanged; (7) document lifecycle.
- **Outputs:** seam/enabling-point record and tests.
- **Stop conditions:** all options alter public/production semantics without authority or rely on unsafe ambient state.
- **Escalation:** published API, global process state, linker/deployment changes, security boundary.
- **Common false positives:** interface without selectable implementation; static setter leaking across tests; overengineered generic injection.
- **Source support:** `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ### Seam Types`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point`; `SRC-WELC: chapters/034-chapter-25-dependency-breaking-techniques.md :: # Chapter 25: Dependency-Breaking Techniques`.

### PROC-CL-008 — Determine tests from effects

- **Inputs:** proposed edit/change point, call graph, state and I/O boundaries.
- **Evidence required:** forward effect trace including values, mutation, globals, I/O, exceptions, callbacks, concurrency/deferred work.
- **Decision steps:** (1) mark direct effects; (2) propagate through callers/consumers until language/system firewalls or stable observations; (3) identify convergence/pinch points; (4) rank observation points by relevance, locality, determinism, and cost; (5) choose nearest coverage plus critical broad contracts; (6) record unreachable/unknown effects.
- **Outputs:** required test/characterization set and confidence.
- **Stop conditions:** dynamic/reflection/distributed effects cannot be bounded safely.
- **Escalation:** unobservable high-consequence effect, production-only integration, uncertain async ordering.
- **Common false positives:** class boundary equals effect boundary; no return equals no effect; one end-to-end path covers all branches.
- **Source support:** `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Reasoning About Effects`; `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ## Interception Points`.

### PROC-CL-009 — Evaluate duplication

- **Inputs:** duplicate/clone sites, domain meanings, callers/owners, history/co-change, tests and variation.
- **Evidence required:** semantic comparison and expected evolution; history when fit.
- **Decision steps:** (1) identify repeated knowledge rather than text; (2) compare invariants and ownership; (3) measure/inspect co-change and omission history; (4) model extraction API/parameters/dependencies; (5) compare retain, proximity, generated source, and abstraction; (6) select option minimizing change amplification while preserving readability.
- **Outputs:** retain/proximity/extract/generate decision and rationale.
- **Stop conditions:** common concept cannot be named or variation is unstable; cross-owner contract cost unknown.
- **Escalation:** abstraction crosses bounded context/public package/team boundary.
- **Common false positives:** clone percentage; two similar tests; repeated syntax implementing different policies; DRY as absolute rule.
- **Source support:** `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`.

### PROC-CL-010 — Assess a hotspot

- **Inputs:** repository history, file identity, source metrics, current source/tests, roadmap/incidents.
- **Evidence required:** cleaned relevant interval; frequency plus rough complexity; current manual inspection.
- **Decision steps:** (1) audit data; (2) choose interval by product/release activity; (3) remove/partition nonmaintainer artifacts; (4) rank change frequency; (5) combine with size/complexity; (6) inspect trends; (7) drill to function/method; (8) correlate with responsibilities, defects, tests, roadmap, and congestion; (9) classify healthy-active, investigate, refactor-candidate, or false positive.
- **Outputs:** evidence-backed candidate queue and nonfindings.
- **Stop conditions:** history/data is unfit or current product phase invalidates interval.
- **Escalation:** recommendation implies broad architecture/team/resource decision.
- **Common false positives:** Makefile/version file/generated code; completed historical refactor; central but simple policy; active feature development.
- **Source support:** `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Evaluate Hotspots with Complexity Trends`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Inspect the Code`.

### PROC-CL-011 — Audit repository-history evidence

- **Inputs:** VCS logs, repo structure/policies, branch/merge history, team map, analysis goal.
- **Evidence required:** sampled raw commits spanning the selected interval and known repository events.
- **Decision steps:** (1) define claim and required fields; (2) inspect aliases/bots/pairing; (3) inspect squashes/merges/branch imports; (4) trace renames/moves and copied history; (5) identify generated/vendor/noncode/migrations; (6) align start date with product/organizational changes; (7) validate task IDs or windowing; (8) mark each intended metric usable/corrected/limited/invalid.
- **Outputs:** provenance/fitness ledger and exclusions.
- **Stop conditions:** identity/time/task/author assumptions cannot be repaired for the proposed claim.
- **Escalation:** privacy/legal/social-metric use or uncertain personnel attribution.
- **Common false positives:** tool parsing success; large commit count; `.mailmap` assumed complete; main branch assumed representative.
- **Source support:** `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ### Specify a Start Date with Organizational Significance`.

### PROC-CL-012 — Assess an architectural boundary from change evidence

- **Inputs:** co-change clusters, static dependencies, domain language, invariants/data/transactions, team/deployment ownership, current ADRs.
- **Evidence required:** repeated history pattern plus domain and operational evidence.
- **Decision steps:** (1) state driver—change locality, ownership, deployment, scaling, security, or failure isolation; (2) map current accepted boundary; (3) inspect co-change and source similarities; (4) identify domain concepts/invariant/data owners; (5) generate retain, collocate, extract component, or protocol alternatives; (6) assess interface chatter, migration, operations and reversal; (7) prototype/deletion-test the strongest candidate; (8) recommend only if driver improves.
- **Outputs:** boundary assessment, alternatives, evidence, costs, confidence, migration authority need.
- **Stop conditions:** only directory/metric evidence exists; domain ownership disputed; no driver beyond diagram preference.
- **Escalation:** cross-team/data/deployment/public contract or organizational restructuring.
- **Common false positives:** co-change due to release train, tests, codegen, mass edits; service/repo boundary mistaken for domain boundary.
- **Source support:** `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### Use the Deletion Test`.

### PROC-CL-013 — Select a splinter campaign

- **Inputs:** validated congested hotspot, responsibility groups, X-ray/function activity, protection, parallel-development plan.
- **Evidence required:** active complex hotspot, recognizable group, facade/signature preservation route, fast integration.
- **Decision steps:** (1) establish safety net; (2) identify behavior groups; (3) colocate related functions where useful; (4) select highest-pressure cohesive group; (5) copy/extract to named unit while original remains; (6) delegate original methods; (7) verify regression; (8) integrate immediately; (9) remeasure and choose repeat/stop; (10) later migrate callers/remove facade only with separate authority.
- **Outputs:** one extracted responsibility, original API facade, verification and follow-up signals.
- **Stop conditions:** group not cohesive, required tests absent, slice cannot integrate quickly, or parallel edits invalidate it.
- **Escalation:** client migration, shared data/schema, cross-team freeze, or long-lived branch required.
- **Common false positives:** file size alone; splitting by technical syntax rather than behavior; final-design perfection in first slice.
- **Source support:** `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters`.

### PROC-CL-014 — Decide whether to leave code alone

- **Inputs:** proposed target, recent/history activity, runtime use, incidents, roadmap, support/security constraints, characterization cost.
- **Evidence required:** current use/product/support context; age/churn only as supplementary evidence.
- **Decision steps:** (1) identify requested benefit; (2) verify current and imminent pressure; (3) check confirmed defects/security/support obligations; (4) estimate behavior-discovery and integration risk; (5) compare leave, isolate, characterize, delete-investigate, local refactor, migrate/rewrite; (6) choose no change if no authorized option has positive evidence-adjusted value.
- **Outputs:** leave-alone or action decision with trigger for reassessment.
- **Stop conditions:** runtime use or criticality cannot be established and proposed action is destructive.
- **Escalation:** suspected dead code with external consumers, safety/security concern, unsupported platform, imminent major change.
- **Common false positives:** stable equals good; ugly equals costly; old equals dead; no commits in paused system equals stable.
- **Source support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`.

### PROC-CL-015 — Decide when to stop or escalate a campaign

- **Inputs:** goal, authority, current diff, baseline/check results, unknowns, external effects, budget/integration state.
- **Evidence required:** last known-good point and explicit campaign stop criteria.
- **Decision steps:** (1) ask whether goal remains singular; (2) verify behavior boundary and last move; (3) check new semantic choice/architecture/API/data/production action; (4) check failure localization and reversal; (5) continue only if next move is authorized, protected, and smaller than uncertainty; (6) otherwise retain independently green subset, backtrack own slice, or escalate with options/evidence.
- **Outputs:** continue/stop/backtrack/retain/escalate and reason.
- **Stop conditions:** any failed gate above.
- **Escalation:** explicit human choice, new authority, disputed expected behavior, irreversible state, cross-team commitment.
- **Common false positives:** sunk cost, “almost done,” aesthetics, deadline as permission, or stopping before safe read-only diagnosis.
- **Source support:** `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ### Stop when you are unsure.`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: #### Backtrack.`.

### PROC-CL-016 — Validate an automated transformation

- **Inputs:** tool/version, operation, target languages/files, dynamic/config/generated references, repository checks.
- **Evidence required:** documented semantic coverage for the operation and previewable/reversible edit.
- **Decision steps:** (1) record tool/language/version support; (2) enumerate surfaces outside its model; (3) run preview on bounded target; (4) inspect declarations/references/diff; (5) run compile/static/targeted tests and broader suite; (6) search unresolved symbolic/config/serialized forms; (7) keep coherent rollback; (8) downgrade to manual campaign if coverage uncertain.
- **Outputs:** verified transformation or rejected/limited tool plan.
- **Stop conditions:** opaque bulk output, no undo, unsupported language construct, mixed semantic edits, or unresolved dynamic references.
- **Escalation:** public symbols, schema/serialization names, cross-repo consumers, generated-source owner.
- **Common false positives:** compiler green; IDE brand trust; all textual matches assumed references; no textual match assumed no dynamic reference.
- **Source support:** `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Technical Criteria for a Refactoring Tool`; `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: ## Tackling Monsters with Automated Refactoring Support`.

## Change-type taxonomy contribution

| Change type | Purpose and allowable semantic change | Evidence / authority / protection | Invalid bundling or label traps |
|---|---|---|---|
| Feature implementation | Add an authorized capability; changes behavior only within acceptance criteria. | Product/user requirement and implementation authority; tests for new behavior plus preserved adjacent effects. | Do not hide architectural redefinition or unrelated cleanup inside feature necessity. |
| Defect repair | Change a specific current behavior to an authoritative expected behavior. | Reproducer/failing test plus oracle and repair authority; regression protection and blast-radius checks. | Do not characterize desired behavior as if it were current; do not mix structural campaign before repair is green. |
| Refactoring | Improve internal structure while preserving observable behavior. | Demonstrated structural pressure, preservation boundary, green/characterized baseline, reversible verified sequence. | Any intentional output/error/side-effect/protocol/data/resource semantic delta invalidates the pure-refactoring label. |
| Architectural restructuring | Change system boundaries, dependency direction, ownership, deployment, data authority, or quality-attribute trade-offs. | Architectural drivers, accepted contracts, option/cost analysis, architecture authority, migration and fitness evidence. | Do not call every class extraction architecture; do not smuggle behavior/product policy changes. |
| Migration | Move callers, data, protocol, platform, or implementation between compatible states. Transitional semantics may be authorized. | Source/target contracts, consumer/data inventory, compatibility period, rollout/rollback/observability, migration authority. | Do not call public/schema migration refactoring; avoid simultaneous unrelated redesign and defect repair. |
| Optimization | Improve resource use under specified workload while preserving non-resource semantics and authorized resource/latency goals. | Baseline/profile/benchmark, semantic equivalence, performance authority, regression gate. | Do not mix algorithmic semantic change or approximate result without explicit authorization; do not relabel speculative tuning. |
| Cleanup | Remove local nonbehavioral clutter or obsolete scaffolding. | Proof behavior/build/package/deployment outputs are unchanged; scope authority. | “Cleanup” is not a safe umbrella for API change, dependency upgrade, test deletion, or architectural move. |
| Deletion | Remove unused behavior/code/data/test or obsolete capability; semantic change may be none or explicitly intended. | Static plus runtime/deployment/use evidence, ownership and retention requirements, rollback or recovery, deletion authority. | Old/unchanged/unreferenced-by-local-search is insufficient; test deletion needs protection comparison. |
| Dependency upgrade | Change externally supplied code/version and resulting transitive, build, runtime, license, or security behavior. | Compatibility/security motivation, changelog/API review, lockfile/build/runtime tests, rollback; dependency authority. | Do not hide it inside refactoring or formatting; separate broad generated/lock churn from source changes where possible. |
| Operational hardening | Improve failure, durability, security, observability, recovery, or operational limits; may intentionally alter failure behavior. | Threat/failure/incident/operational requirement, production authority, fault/recovery tests and rollout evidence. | Do not call new retries/timeouts/logging behavior cleanup; avoid structural campaigns that obscure failure semantics. |
| Documentation repair | Correct externally or internally consumed explanation without changing runtime behavior. | Current code/contracts/tool output and doc ownership; executable examples/checks where available. | If generated docs/API schema or examples drive runtime/config behavior, treat affected portion under its actual change type. |

Source basis: `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Refactoring and Performance`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Changing Interfaces`.

## Evidence taxonomy contribution

| Evidence class | Can establish | Cannot establish by itself | Use / cautions from this lane |
|---|---|---|---|
| Accepted requirements / ADRs / project contracts | Desired behavior, accepted boundaries, authority and constraints when current | Runtime conformance or completeness | Highest generic-doctrine override; verify current acceptance and scope. |
| Static source structure | Dependencies visible to parser/search, data/control shape, candidate responsibilities, transformation surface | Runtime use, hidden configuration/reflection, historical cost, domain intent, defect | Use to validate—not replace—history hypotheses; language/tool coverage matters. |
| Automated tests | Encoded observations under their setup; regression detection for exercised paths | Absence of defects, full contract, production integration, desired behavior unless oracle is authoritative | Distinguish characterization, regression, contract, and broad covering purpose. |
| Compilation/static analysis/refactoring tool | Syntax/type/reference properties within the tool’s model | Runtime semantics, dynamic/config/serialized references, full behavior preservation | Stronger for small mechanical edits; audit blind spots and tool version. |
| Runtime observation | Actual behavior under observed workload/environment | General correctness, all clients/paths, desired intent | Stabilize environment and distinguish incidental from contractual output. |
| Incidents/defects | Real failure modes, consequences, affected paths under reported context | General architecture diagnosis or cause without investigation | High priority for pressure; connect to reproducer and causal analysis. |
| Change history/frequency | Where effort occurred, relative activity, potential recurring cost | Bad quality, cause, current runtime use, author performance | Clean and scope; use as prioritization only. |
| Co-change / logical change sets | Repeated temporal relationship and omission/planning hypothesis | Static dependency, semantic identity, dependency direction, boundary prescription | Report support and degree; inspect diffs/tasks; allow expected coupling. |
| Complexity/size trends | Relative structural growth under consistent proxy | Maintainability/defect in absolute terms or necessity of a split | Prefer trends and repository-relative baselines; inspect current code. |
| Code age | Time since last recorded modification relative to reference | Goodness, deadness, safety, cohesion, continued use | Combine with product activity, runtime use, support and domain. |
| Ownership/contribution history | Likely familiarity and operational contribution patterns when attribution is sound | Skill, productivity, intent, current knowledge, blame, fair performance | Privacy/authority gate; team/system risk use only; pairing/squash/alias bias. |
| Domain language/expert evidence | Meaning, policy, invariants, concept distinctions, likely ownership boundaries | Implementation conformance or operational fitness | Required to turn co-change/static clusters into domain boundaries. |
| Deployment/protocol/schema artifacts | Concrete compatibility and operational boundaries | Actual consumer population or desired policy alone | Inventory versions/consumers/data; generated artifacts need source-of-truth identification. |
| Generated/vendored artifacts | Build/runtime inputs and outputs when authoritative | Maintainer design pressure in generated text or license to edit output | Exclude from maintainability ranking; trace generator/vendor owner. |

## Routing index contribution

### Role routing

| Role | Core concepts | Conditional concepts | Exclude by default |
|---|---|---|---|
| Coding agent | CHG-UNI-001–005, CHG-REF-003–006 | CHG-LEG-001/004/005/012 when weakly tested; CHG-HIST-003 for companion changes | Sociotechnical metrics, broad hotspot/architecture campaigns without request |
| Refactoring agent | CHG-UNI-001–005, CHG-REF-001–008 | CHG-LEG-001–014 for weak characterization; CHG-HIST-001–005/010 for prioritization | Semantic repair execution and organizational recommendations without authority |
| Legacy-code agent | CHG-UNI-001–005, CHG-LEG-001–014, CHG-REF-008 | CHG-HIST-002/003/005/010 for large mature systems | Final architecture patterns before behavior discovery |
| Repair/debugging agent | CHG-UNI-001–005, CHG-LEG-002/003/005/007/008 | CHG-LEG-001/004/006/014 when harness blocked | Structural campaigns until the repaired behavior is green and separately authorized |
| Architecture agent | CHG-UNI-001/002/005, CHG-REF-004/005/007/008, CHG-HIST-001/003/005–011 | CHG-HIST-002/004/012 for repository evidence | Method-level catalog mechanics unless needed for migration feasibility |
| Review agent | CHG-UNI-001–005, CHG-REF-001–006, CHG-HIST-001/006/008/012 | Legacy protection concepts when tests weak; social concepts only with privacy authority | Preferences as blockers; individual performance inference |
| Repository-assessment agent | CHG-REF-001/002/008, CHG-HIST-001–008/011/012 | CHG-HIST-009/010 when recommendation scope includes architecture/refactoring | Execution, team reorganization, or inferred authorization |

### Task and signal routing

| Task / repository signal | Activate | Retrieval priority / budget | Exclude / prerequisite |
|---|---|---|---|
| “Refactor/cleanup” request | CHG-UNI-001–004, CHG-REF-001/002/008, PROC-CL-001–004 | core, 900–1400 tokens | Require preservation and refactoring pressure before mechanics. |
| Behavior poorly understood / few tests | CHG-LEG-001–008, PROC-CL-005–008 | core, 1400–2200 | Do not load hotspot/social doctrine unless system-scale prioritization is needed. |
| Long/large class or monster method | CHG-REF-002/004, CHG-LEG-009–011 | high, 900–1400 | Size is only candidate signal; require current effects/responsibilities. |
| Duplication / clone finding | CHG-REF-003, CHG-HIST-003, PROC-CL-009 | high, 600–900 | Exclude generated code; require semantic/evolution comparison. |
| Public API/schema/protocol change | CHG-UNI-001/002, CHG-REF-005 | core, 600–1000 | Require consumer/authority/migration inventory. |
| Hard dependency blocks tests | CHG-LEG-004–006/012/014, PROC-CL-007 | high/specialist, 900–1400 | Identify enabling point; no generic interface mandate. |
| Hotspot/technical-debt inventory | CHG-HIST-001/002/004/006, PROC-CL-010/011 | high, 1000–1600 | Data fitness first; output investigation candidates, not findings. |
| Co-change / omitted companion edit | CHG-HIST-003/006/011/012 | high, 800–1300 | Require support/degree/task inspection; warnings remain bypassable. |
| Modularization/bounded-context assessment | CHG-REF-004/007, CHG-HIST-003/007/009/011 | specialist, 1400–2200 | Domain and authority evidence required; no directory-only boundaries. |
| Old/stable/dead code | CHG-REF-008, CHG-HIST-005, PROC-CL-014 | high, 600–1000 | Require runtime/product/support evidence before deletion or migration. |
| Multi-team congestion/ownership | CHG-HIST-006–009 | specialist, 1200–1800 | Privacy/legal/human-context authority; never individual scoring. |
| Automated refactor/codemod | CHG-REF-006, CHG-LEG-014, PROC-CL-016 | high, 700–1100 | Verify tool semantic coverage and dynamic surfaces. |
| Generated/vendored code | NEG-CL-021, evidence taxonomy | core, 200–350 | Route to source generator/vendor boundary; exclude direct refactoring by default. |

## Graph candidates

Provenance relation vocabulary:

- `direct_support`: the source explicitly formulates the node or relation.
- `corroboration`: the source independently supports substantially the same operational claim.
- `refinement`: the source narrows, conditions, or extends another formulation.
- `derived_inference`: the canonical node/edge is an explicit synthesis from multiple source claims and is not attributed verbatim to one source.

### Candidate nodes and per-source formulations

| Node ID | Kind | Canonical formulation | Per-source formulations and provenance |
|---|---|---|---|
| `G-CL-CHANGE-TYPE` | taxonomy | Name the purpose and allowable semantic delta before editing. | SRC-WELC: four reasons to change (`direct_support`); SRC-REF: refactoring definition and performance contrast (`corroboration`); synthesis separates migration/hardening/deletion (`derived_inference`). |
| `G-CL-PRESERVATION` | universal principle | Explicitly bound observable behavior that must survive the change. | SRC-REF: observable behavior preserved (`direct_support`); SRC-WELC: behavior-preservation questions under risky change (`corroboration`); SRC-SDX: facade/provisional-test protection in hotspot work (`refinement`). |
| `G-CL-TWO-HATS` | conduct constraint | Do one semantic or structural goal at a time. | SRC-REF: two hats (`direct_support`); SRC-WELC: single-goal editing (`corroboration`); SRC-SDX: short splinter slices under parallel work (`refinement`). |
| `G-CL-REF-PRESSURE` | evidence gate | Structural change requires demonstrated current or imminent maintenance pressure. | SRC-REF: refactor while adding/fixing/reviewing (`direct_support`); SRC-WELC: current-work heuristic (`refinement`); SRC-SDX: time-dependent interest/hotspot ranking (`refinement`). |
| `G-CL-SMELL-HYP` | epistemic rule | A smell is a hypothesis requiring repository validation. | SRC-REF: intuitive smell catalog rather than precise measure (`direct_support`); SRC-SDX: contextual quality and improve-not-judge (`corroboration`); SRC-WELC: responsibility heuristics (`refinement`). |
| `G-CL-SMALL-STEP` | procedure property | Advance through the smallest verifiable structural move. | SRC-REF: repeated test-small-change rhythm (`direct_support`); SRC-WELC: feedback/monster small-piece tactics (`corroboration`); SRC-SDX: fast one-responsibility splinters (`refinement`). |
| `G-CL-REVERSAL` | safety property | Keep a last-known-good state and backtrack when certainty is lost. | SRC-REF: backtrack/stop when unsure (`direct_support`); SRC-WELC: hyperaware editing and compiler feedback (`corroboration`); SRC-SDX: short lead time/avoid long branch (`refinement`). |
| `G-CL-CHAR-SURFACE` | test concept | Encode actual relevant behavior at an observation surface before uncertain change. | SRC-WELC: characterization tests (`direct_support`); SRC-REF: self-testing code (`corroboration`); SRC-SDX: provisional black-box safety net (`refinement`). |
| `G-CL-EFFECT-SURFACE` | analysis concept | Trace all reachable observable effects to choose protection. | SRC-WELC: effect propagation (`direct_support`); SRC-REF: observable behavior framing (`corroboration`); SRC-SDX: cross-repository logical dependencies (`refinement`). |
| `G-CL-SEAM` | legacy mechanism | A selectable place to substitute behavior without editing the use site. | SRC-WELC: seam model (`direct_support`); SRC-REF: indirection can isolate change (`corroboration`); SRC-SDX: facade/splinter boundary (`refinement`). |
| `G-CL-ENABLING-POINT` | control point | The explicit location where alternate seam behavior is selected. | SRC-WELC: enabling point (`direct_support`); other sources do not name it; production-default requirement is `derived_inference`. |
| `G-CL-SENSING` | test purpose | Break a dependency to observe effects. | SRC-WELC: sensing/fakes (`direct_support`); SRC-REF: tests detect mistakes (`corroboration`); SRC-SDX: behavior analysis directs observation targets (`refinement`). |
| `G-CL-SEPARATION` | test purpose | Break a dependency to execute the code independently. | SRC-WELC: separation/fakes (`direct_support`); SRC-REF: decomposed responsibilities aid testing (`corroboration`); SRC-SDX: splinters create local contexts (`refinement`). |
| `G-CL-PINCH-POINT` | test topology | One stable observation can intercept effects from a change cluster. | SRC-WELC: pinch points (`direct_support`); SRC-SDX: temporary E2E safety net around hotspot (`refinement`); trade-off with localization is `derived_inference`. |
| `G-CL-TEMP-STRUCT` | lifecycle concept | A seam/sprout/wrapper/facade/test may be provisional scaffolding with an explicit disposition. | SRC-WELC: dependency scars, sprout/wrap (`direct_support`); SRC-SDX: temporary tests and splinter facade (`corroboration`); SRC-REF: intermediate steps/backtracking (`refinement`). |
| `G-CL-RESPONSIBILITY` | design concept | Cohesive behavior belongs with its data, policy, invariants, and independently evolving responsibility. | SRC-REF: move/extract class (`direct_support`); SRC-WELC: seeing responsibilities/current work (`refinement`); SRC-SDX: domain/co-change candidates (`refinement`). |
| `G-CL-EARNED-ABSTRACTION` | design gate | Abstract repeated knowledge only when shared meaning and evolution repay indirection. | SRC-REF: duplication/simplification (`direct_support` but less conditional); SRC-SDX: co-change plus similarity and proximity alternative (`refinement`); SRC-WELC: repeated-change and extract options (`corroboration`). |
| `G-CL-HOTSPOT` | evidence signal | Active change plus rough complexity ranks investigation value. | SRC-SDX: hotspot method (`direct_support`); SRC-REF: no direct history formulation; SRC-WELC: change difficulty motivates local focus (`refinement`). |
| `G-CL-COCHANGE` | evidence signal | Repeated co-change nominates a relationship requiring explanation. | SRC-SDX: change coupling (`direct_support`); SRC-REF: shotgun/divergent change concepts (`corroboration`); SRC-WELC: repeated changes/effect clusters (`refinement`). |
| `G-CL-COMPLEXITY-TREND` | evidence signal | Relative structural trajectory is a warning, not an absolute verdict. | SRC-SDX: complexity trends/relative warnings (`direct_support`); SRC-REF: no historical metric; SRC-WELC: no historical metric. |
| `G-CL-CODE-AGE` | evidence signal | Age suggests stability only when product/use/domain context supports it. | SRC-SDX: code age and caveats (`direct_support`); SRC-REF: leave-alone conditions (`corroboration`); SRC-WELC: fear/unknown behavior complicates age (`refinement`). |
| `G-CL-DATA-FITNESS` | evidence gate | Audit version-control provenance before behavioral inference. | SRC-SDX: biases/workarounds (`direct_support`); SRC-REF/WELC: no direct historical-data formulation. |
| `G-CL-SPLINTER` | campaign pattern | Extract one active responsibility behind the old API to reduce congestion incrementally. | SRC-SDX: splinter pattern (`direct_support`); SRC-REF: big refactorings as gradual (`corroboration`); SRC-WELC: extract current class first / current work (`refinement`). |
| `G-CL-DOMAIN-BOUNDARY` | architecture concept | A boundary must be justified by domain/invariant/data/change forces, not graph or directory shape alone. | SRC-SDX: bounded contexts through change patterns plus domain expertise (`direct_support`); SRC-REF: domain/presentation separation (`corroboration`); SRC-WELC: hidden classes/responsibilities (`refinement`). |
| `G-CL-SOCIOTECHNICAL` | architecture evidence | Technical dependencies and team coordination patterns must be interpreted together. | SRC-SDX: Conway/coordination/congruence (`direct_support`); SRC-REF/WELC: no organization-level formulation. |
| `G-CL-NO-PERF-SCORING` | prohibition | Never turn behavioral code metrics into individual performance evaluation. | SRC-SDX: explicit prohibition and adaptive-behavior rationale (`direct_support`); SRC-REF/WELC: no direct formulation. |
| `G-CL-LEAVE-ALONE` | decision outcome | Prefer no intervention when benefit is speculative and preservation risk dominates. | SRC-REF: when not to refactor (`direct_support`); SRC-SDX: inactive ugly code may have no interest cost (`corroboration`); SRC-WELC: preserve poorly understood behavior (`refinement`). |
| `G-CL-TOOL-TRUST` | evidence gate | Trust automation only to the boundary of its semantic model, preview, and reversal. | SRC-REF: accuracy/undo/integration criteria (`direct_support`); SRC-WELC: automated monster refactor/lean on compiler (`refinement`); SRC-SDX: tooling output still needs inspection (`corroboration`). |
| `G-CL-COMPAT-MIGRATION` | change pattern | Independent consumers turn internal restructuring into a phased compatibility migration. | SRC-REF: published interface/database constraints (`direct_support`); SRC-WELC: preserve signatures (`corroboration`); SRC-SDX: facade and multi-repo dependencies (`refinement`). |
| `G-CL-STOP-ESCALATE` | authority rule | Stop or escalate when the next step needs a behavior choice, wider authority, or unavailable protection. | SRC-REF: stop when unsure (`direct_support`); SRC-WELC: suspicious behavior and hyperaware scope (`corroboration`); cross-source authority formulation (`derived_inference`). |

### Candidate typed edges with provenance

| From | Edge type | To | Provenance and operational meaning |
|---|---|---|---|
| `G-CL-CHANGE-TYPE` | `determines` | `G-CL-PRESERVATION` | SRC-WELC `direct_support`: each change kind preserves and changes different behavior. |
| `G-CL-CHANGE-TYPE` | `constrains` | `G-CL-TWO-HATS` | SRC-REF `direct_support`: functionality and restructuring modes are consciously separated. |
| `G-CL-PRESERVATION` | `requires_when_uncertain` | `G-CL-CHAR-SURFACE` | SRC-WELC `direct_support`: characterization makes current relevant behavior observable. |
| `G-CL-PRESERVATION` | `scopes` | `G-CL-EFFECT-SURFACE` | Cross-source `derived_inference`: the boundary tells effect reasoning what must be protected. |
| `G-CL-TWO-HATS` | `reduces_ambiguity_in` | `G-CL-SMALL-STEP` | SRC-REF `direct_support`: one purpose plus small steps localizes failures. |
| `G-CL-SMALL-STEP` | `enables` | `G-CL-REVERSAL` | SRC-REF `direct_support`: backtracking is cheap when the last move is small. |
| `G-CL-REVERSAL` | `supports` | `G-CL-STOP-ESCALATE` | SRC-REF `direct_support`: stop/backtrack on lost certainty. |
| `G-CL-REF-PRESSURE` | `earns` | `G-CL-SMALL-STEP` | SRC-REF/SRC-WELC `corroboration`: refactor toward a current goal through local moves. |
| `G-CL-SMELL-HYP` | `requires_validation_by` | `G-CL-REF-PRESSURE` | SRC-REF + SRC-SDX `derived_inference`: smell becomes action only with actual cost. |
| `G-CL-HOTSPOT` | `supplies_candidate_evidence_for` | `G-CL-REF-PRESSURE` | SRC-SDX `direct_support`: hotspots prioritize refactoring investigation. |
| `G-CL-COMPLEXITY-TREND` | `corroborates` | `G-CL-HOTSPOT` | SRC-SDX `direct_support`: trend distinguishes active accumulation from raw frequency. |
| `G-CL-CODE-AGE` | `downranks_or_qualifies` | `G-CL-HOTSPOT` | SRC-SDX `direct_support`: historic/stable candidates need current relevance. |
| `G-CL-DATA-FITNESS` | `gates` | `G-CL-HOTSPOT` | SRC-SDX `direct_support`: generated/imported/noisy data biases rankings. |
| `G-CL-DATA-FITNESS` | `gates` | `G-CL-COCHANGE` | SRC-SDX `direct_support`: commit/task structure determines meaningful coupling. |
| `G-CL-DATA-FITNESS` | `gates` | `G-CL-SOCIOTECHNICAL` | SRC-SDX `direct_support`: aliases, squashes, pairing, and team dates bias author inference. |
| `G-CL-COCHANGE` | `corroborates` | `G-CL-EARNED-ABSTRACTION` | SRC-SDX `direct_support`: similarity plus co-evolution identifies costly clones. |
| `G-CL-COCHANGE` | `nominates` | `G-CL-DOMAIN-BOUNDARY` | SRC-SDX `direct_support`, explicitly nondecisive. |
| `G-CL-RESPONSIBILITY` | `validates` | `G-CL-DOMAIN-BOUNDARY` | SRC-REF/SRC-WELC/SRC-SDX `corroboration`: semantic responsibility must confirm temporal cluster. |
| `G-CL-EARNED-ABSTRACTION` | `may_reduce` | `G-CL-COCHANGE` | SRC-SDX `direct_support`: shared knowledge can remove repeated parallel edits. |
| `G-CL-EARNED-ABSTRACTION` | `conflicts_with_when_local_clarity_wins` | `G-CL-RESPONSIBILITY` | SRC-SDX `direct_support`: cross-domain abstraction can give one unit multiple reasons to change. |
| `G-CL-EFFECT-SURFACE` | `selects` | `G-CL-CHAR-SURFACE` | SRC-WELC `direct_support`: forward effect reasoning identifies test points. |
| `G-CL-EFFECT-SURFACE` | `may_converge_at` | `G-CL-PINCH-POINT` | SRC-WELC `direct_support`. |
| `G-CL-PINCH-POINT` | `broadens` | `G-CL-CHAR-SURFACE` | SRC-WELC `direct_support`: one point covers multiple affected paths. |
| `G-CL-PINCH-POINT` | `trades_off` | `G-CL-SENSING` | Cross-source `derived_inference`: broad coverage can weaken precise localization. |
| `G-CL-SEAM` | `is_controlled_at` | `G-CL-ENABLING-POINT` | SRC-WELC `direct_support`. |
| `G-CL-SEAM` | `enables` | `G-CL-SENSING` | SRC-WELC `direct_support`. |
| `G-CL-SEAM` | `enables` | `G-CL-SEPARATION` | SRC-WELC `direct_support`. |
| `G-CL-SEAM` | `may_be` | `G-CL-TEMP-STRUCT` | SRC-WELC/SRC-SDX `corroboration`: first seam/facade can be provisional. |
| `G-CL-TEMP-STRUCT` | `requires_disposition_by` | `G-CL-STOP-ESCALATE` | Cross-source `derived_inference`: retain/remove/publicly adopt may need authority. |
| `G-CL-SENSING` | `supports` | `G-CL-CHAR-SURFACE` | SRC-WELC `direct_support`: substitutes expose otherwise hidden effects. |
| `G-CL-SEPARATION` | `supports` | `G-CL-CHAR-SURFACE` | SRC-WELC `direct_support`: isolation gets code into the harness. |
| `G-CL-RESPONSIBILITY` | `guides` | `G-CL-SPLINTER` | SRC-SDX `direct_support`: splinter along behavioral responsibilities. |
| `G-CL-HOTSPOT` | `prioritizes` | `G-CL-SPLINTER` | SRC-SDX `direct_support`: active complex region earns first splinter attention. |
| `G-CL-SOCIOTECHNICAL` | `raises_need_for` | `G-CL-SPLINTER` | SRC-SDX `direct_support`: parallel congestion motivates facade-preserving separation. |
| `G-CL-SPLINTER` | `preserves_temporarily` | `G-CL-COMPAT-MIGRATION` | SRC-SDX `refinement`: original API facade defers client migration. |
| `G-CL-COMPAT-MIGRATION` | `extends` | `G-CL-PRESERVATION` | SRC-REF/SRC-SDX `corroboration`: preservation spans independently deployed callers/data. |
| `G-CL-TOOL-TRUST` | `may_accelerate` | `G-CL-SMALL-STEP` | SRC-REF `direct_support`: accurate fast tools make small refactors practical. |
| `G-CL-TOOL-TRUST` | `cannot_replace` | `G-CL-PRESERVATION` | Cross-source `derived_inference`: semantic blind spots still require repository verification. |
| `G-CL-CODE-AGE` | `may_favor` | `G-CL-LEAVE-ALONE` | SRC-SDX/SRC-REF `corroboration`, only with current context. |
| `G-CL-REF-PRESSURE` | `overrides_when_strong` | `G-CL-LEAVE-ALONE` | Cross-source `derived_inference`: confirmed current pressure can earn intervention. |
| `G-CL-STOP-ESCALATE` | `protects` | `G-CL-PRESERVATION` | SRC-REF/SRC-WELC `corroboration`: uncertainty or suspicious behavior stops unauthorized drift. |
| `G-CL-SOCIOTECHNICAL` | `must_not_feed` | `G-CL-NO-PERF-SCORING` | SRC-SDX `direct_support`: system/team insight is not individual evaluation. |
| `G-CL-NO-PERF-SCORING` | `constrains_use_of` | `G-CL-DATA-FITNESS` | SRC-SDX `refinement`: even accurate data lacks situational/performance authority. |
| `G-CL-DOMAIN-BOUNDARY` | `may_conflict_with` | `G-CL-EARNED-ABSTRACTION` | SRC-SDX `direct_support`: sharing across bounded contexts can create ownership conflict. |
| `G-CL-DOMAIN-BOUNDARY` | `should_localize` | `G-CL-COCHANGE` | SRC-SDX `direct_support`: architecture should support ordinary change patterns, not force cross-boundary edits. |

Exact-locator inheritance for graph ingestion: `G-CL-CHANGE-TYPE→CHG-UNI-001`; `G-CL-PRESERVATION→CHG-UNI-002`; `G-CL-TWO-HATS→CHG-UNI-003`; `G-CL-SMALL-STEP→CHG-UNI-004`; `G-CL-REVERSAL,G-CL-STOP-ESCALATE→CHG-UNI-005`; `G-CL-REF-PRESSURE→CHG-REF-001`; `G-CL-SMELL-HYP→CHG-REF-002`; `G-CL-EARNED-ABSTRACTION→CHG-REF-003`; `G-CL-RESPONSIBILITY→CHG-REF-004`; `G-CL-COMPAT-MIGRATION→CHG-REF-005`; `G-CL-TOOL-TRUST→CHG-REF-006`; `G-CL-LEAVE-ALONE→CHG-REF-008`; `G-CL-CHAR-SURFACE→CHG-LEG-002`; `G-CL-SEAM,G-CL-ENABLING-POINT→CHG-LEG-004`; `G-CL-SENSING,G-CL-SEPARATION→CHG-LEG-005`; `G-CL-EFFECT-SURFACE→CHG-LEG-007`; `G-CL-PINCH-POINT→CHG-LEG-008`; `G-CL-TEMP-STRUCT→CHG-LEG-006/012/013`; `G-CL-HOTSPOT→CHG-HIST-002`; `G-CL-COCHANGE→CHG-HIST-003`; `G-CL-COMPLEXITY-TREND→CHG-HIST-004`; `G-CL-CODE-AGE→CHG-HIST-005`; `G-CL-DATA-FITNESS→CHG-HIST-006`; `G-CL-SOCIOTECHNICAL→CHG-HIST-007`; `G-CL-NO-PERF-SCORING→CHG-HIST-008`; `G-CL-DOMAIN-BOUNDARY→CHG-HIST-009`; `G-CL-SPLINTER→CHG-HIST-010`. Each linked doctrine record carries its exact source locators and routing metadata.

## Coverage and extraction summary

- Complete files inspected: SRC-REF `21/21`; SRC-WELC `37/37`; SRC-SDX `22/22`; total `80/80`.
- Canonical doctrine records: `39` (13 universal/refactoring, 14 legacy, 12 history/sociotechnical).
- Negative-doctrine records: `26`.
- Material conflict records: `13`.
- Deterministic procedures: `16`.
- Graph candidates: `30` nodes and `45` typed edges.
- Source locators are mechanically verifiable exact Markdown headings; verification result is recorded after generation rather than inferred from this statement.
