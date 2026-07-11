# Change and Legacy Canonicalization Ledger

Status: proposed final-candidate canonicalization of the REF/WELC/SDX extraction lane. This artifact proposes stable IDs, records, conflicts, procedures, and graph candidates; it does not edit final doctrine, graph, concept, routing, or other shared artifacts.

## Scope, source registry, and evidence rules

| Stable source ID | Source root | Files inspected in extraction |
|---|---|---|
| `SRC-REF` | `books/refactoring-improving-the-design-of-existing-code` | 21/21 |
| `SRC-WELC` | `books/programming-working-effectively-with-legacy-code` | 37/37 |
| `SRC-SDX` | `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725` | 22/22 |

- Input extraction: `doctrine/_work/extractions/change-legacy-sources.md`.
- Locator form: `SOURCE: chapters/file.md :: exact converted Markdown heading`.
- Proposed IDs are lowercase, source-independent, and intentionally reuse stable candidates already present in adjacent canonicalization ledgers when the operational meaning is genuinely the same.
- Kinds: `principle`, `constraint`, `proof-obligation`, `evidence-rule`, `evidence-signal`, `heuristic`, `pattern`, `technique`, `tradeoff`, `prohibition`, `terminal-decision`, and `terminology`.
- Repository evidence, accepted contracts, explicit authority, current runtime behavior, and current toolchain facts outrank this source-derived ledger.

Provenance relations:

- `direct_support`: the source explicitly advances substantially the canonical proposition.
- `corroboration`: the source independently supports materially the same proposition.
- `refinement`: the source adds an evidence gate, exception, mechanism, or narrower applicability.
- `derived_inference`: bounded cross-source synthesis, not a direct author claim.
- `tension`: a materially competing position that must remain visible.
- `negative_support`: a prohibition or non-entailment derived directly from the cited source warning.

## Canonical concept registry

| Proposed stable ID | Kind | Priority | Extraction candidates normalized | Canonical disposition |
|---|---|---|---|---|
| `change.type-classification` | terminology | core | CHG-UNI-001; change-type taxonomy; PROC-CL-001 | Classify feature, repair, refactoring, architecture, migration, optimization, cleanup/deletion, upgrade, hardening, or documentation work by purpose and semantic permission. |
| `universal.behavior-preservation` | constraint | core | CHG-UNI-002; preservation portions of CHG-LEG-002/007/013 | Reuses the adjacent implementation canonical ID; explicitly name preserved observable surfaces and authorized deltas. |
| `change.semantic-structural-separation` | constraint | core | CHG-UNI-003; CONF-CL-001 | Reuses adjacent canonical ID; semantic and structural work remain separately attributable and verified. |
| `change.verified-small-step-loop` | pattern | core | CHG-UNI-004; CHG-LEG-011 mechanics; PROC-CL-004 | Small move, cheapest relevant check, coherent checkpoint, broader verification, repeat. |
| `change.stop-backtrack-escalate` | constraint | core | CHG-UNI-005; CHG-LEG-003 authority facet; PROC-CL-015 | Stop when preservation, causality, or authority is lost; retain a green subset, backtrack own slice, or escalate. |
| `change.refactoring-pressure` | proof-obligation | core | CHG-REF-001; historical-pressure facets of CHG-HIST-001/002 | Reuses adjacent canonical ID; present or imminent maintenance pressure must earn structural action. |
| `change.smell-as-hypothesis` | evidence-rule | core | CHG-REF-002; NEG-CL-004/005 | A smell nominates investigation and never selects a remedy by itself. |
| `design.knowledge-duplication` | smell | high | diagnosis facet of CHG-REF-003; CHG-HIST-003 similarity use | Reuses adjacent canonical ID; repeated semantic knowledge, not text alone, creates inconsistent-change risk. |
| `design.earned-abstraction` | proof-obligation | core | action facet of CHG-REF-003; PROC-CL-009 | Reuses adjacent canonical ID; shared meaning and expected co-evolution must repay indirection and ownership cost. |
| `change-locality-cohesion` | principle | core | CHG-REF-004; CHG-LEG-009; responsibility facet of CHG-HIST-009 | Reuses architecture/domain candidate; group behavior by semantic responsibility and demonstrated change/invariant/data forces. |
| `change.compatibility-migration` | pattern | high | CHG-REF-005; migration taxonomy; CONF-CL-012 | Published API, protocol, schema, or independent deployment turns restructuring into phased compatibility work. |
| `change.transformation-tool-trust` | proof-obligation | high | CHG-REF-006; automated facet of CHG-LEG-011/014; PROC-CL-016 | Tool trust ends at its semantic model and requires preview, blind-spot audit, reversal, and repository verification. |
| `change.directional-campaign` | pattern | high | CHG-REF-007; general campaign facet of CHG-HIST-010 | A broad target is a revisable direction delivered through independently useful protected intermediate states. |
| `change.leave-stable-code-alone` | terminal-decision | core | CHG-REF-008; CHG-HIST-005 action gate; PROC-CL-014 | Reuses adjacent canonical ID; return no intervention when benefit is speculative and risk dominates, with revisit triggers. |
| `legacy.cover-and-modify` | pattern | core | CHG-LEG-001; PROC-CL-005 | Change point → effect/test point → minimum dependency break → characterization → semantic change → optional refactoring. |
| `testing.characterization` | technique | core | CHG-LEG-002; suspicious-behavior handling from CHG-LEG-003; PROC-CL-006 | Encode actual relevant behavior without granting it moral correctness; route discrepancies to authority. |
| `legacy.controllable-seam` | technique | high | CHG-LEG-004; seam/enabling-point graph nodes; PROC-CL-007 | Merge seam and enabling-point candidates into one operational concept because substitution is unusable without explicit control. |
| `testing.test-double-scope` | proof-obligation | high | CHG-LEG-005 | Fakes/mocks provide local sensing or separation, not evidence that real integration works. |
| `legacy.provisional-dependency-break` | pattern | high | CHG-LEG-006; temporary-structure graph candidate | Break only the dependency blocking required feedback; track whether the resulting scar is provisional or durable. |
| `testing.effect-surface` | evidence-concept | core | CHG-LEG-007; PROC-CL-008 | Select protection from reachable values, mutations, errors, I/O, callbacks, and deferred effects rather than class shape. |
| `testing.pinch-point` | technique | specialist | CHG-LEG-008; broad-covering facet of CHG-LEG-013 | A stable convergence observation can protect a cluster, trading localization for preparation cost. |
| `legacy.current-work-responsibility-discovery` | heuristic | high | CHG-LEG-009; responsibility-discovery facet of CHG-LEG-011 | Current authorized work supplies the first reliable lens for discovering one responsibility in unclear code. |
| `learning.scratch-refactoring` | technique | high | CHG-LEG-010 | Disposable structural editing produces understanding, not a production diff by default. |
| `legacy.sprout-wrap` | pattern | specialist | CHG-LEG-012 | Under evidenced time/test constraints, place new logic beside or around legacy behavior with explicit integration and follow-up risk. |
| `testing.provisional-safety-net` | pattern | specialist | CHG-LEG-013; high-level covering-test material | Temporary black-box/E2E characterization may enable the first seam, then should narrow or justify retention. |
| `legacy.unprotected-enabling-edit` | proof-obligation | specialist | CHG-LEG-014; CONF-CL-006 | A last-resort testless mechanical edit must be singular, reversible, signature-preserving where possible, compiler/tool-audited, and followed immediately by protection. |
| `metric-as-signal` | evidence-rule | core | CHG-HIST-001; general metric facets of CHG-HIST-002/004/005 | Reuses architecture/domain candidate; behavioral metrics allocate attention and never authorize intervention. |
| `evidence.hotspot` | evidence-signal | high | CHG-HIST-002; PROC-CL-010 | Recent activity plus rough complexity prioritizes where poor maintainability would recur. |
| `evidence.change-coupling` | evidence-signal | high | CHG-HIST-003; duplication/boundary/omission uses | Repeated co-change nominates a relationship; expected coupling may be healthy and direction remains unknown. |
| `evidence.complexity-trend` | evidence-signal | normal | CHG-HIST-004; trend facet of CHG-HIST-012 | Relative trajectory warns more usefully than universal absolute thresholds. |
| `evidence.code-age` | evidence-signal | normal | CHG-HIST-005; CHG-REF-008 corroboration | Age suggests stability only after product activity, runtime use, support, domain, and dead-code alternatives are checked. |
| `evidence.behavioral-data-fitness` | proof-obligation | core | CHG-HIST-006; PROC-CL-011 | Audit VCS identity, time, task, author, generated, and migration assumptions before inference. |
| `team-topology-force` | socio-technical context | high | CHG-HIST-007; sociotechnical graph node | Reuses architecture/domain candidate; contributor/team congestion is contextual architecture risk evidence, never blame. |
| `agent.behavioral-metrics-not-performance` | prohibition | core | CHG-HIST-008; NEG-CL-022 | No behavioral-code metric is admissible for individual productivity/performance scoring. |
| `domain.behavioral-boundary-candidate` | heuristic | specialist | CHG-HIST-009; PROC-CL-012 | Co-change can nominate a domain/component boundary; language, invariants, data/authority ownership, and experts decide it. |
| `change.splinter-campaign` | pattern | specialist | CHG-HIST-010; PROC-CL-013 | Extract one high-pressure responsibility behind the old API to reduce active congestion while deferring client migration. |
| `evidence.logical-change-set` | technique | specialist | CHG-HIST-011 | Group multi-commit/repository work by explicit task ID or a lower-confidence documented temporal/organizational window. |
| `review.behavioral-early-warning` | technique | normal | CHG-HIST-012 | Rising hotspot, relative complexity, or missing expected co-change creates a bypassable review prompt, not a blocker. |

## Normalization decisions

### Genuine merges

| Extraction candidates | Canonical ID | Reason |
|---|---|---|
| CHG-UNI-002 plus preservation facets of characterization/effect/safety-net records | `universal.behavior-preservation` | Same obligation: no unauthorized observable semantic delta. Characterization and tests remain proof mechanisms, not synonyms. |
| CHG-UNI-003 and two-hats/single-goal formulations | `change.semantic-structural-separation` | Same causal-isolation constraint across feature, repair, and structural work. |
| CHG-REF-001 plus action-gate facets of hotspot history | `change.refactoring-pressure` | Hotspots may supply evidence, but the canonical concept is the proof obligation to earn intervention. |
| Diagnosis half of CHG-REF-003 | `design.knowledge-duplication` | Text similarity is not canonical; duplicated evolving knowledge is. |
| Action half of CHG-REF-003 | `design.earned-abstraction` | Extraction requires an independent proof obligation and must not be collapsed into the smell. |
| CHG-REF-004 and placement facet of CHG-LEG-009 | `change-locality-cohesion` | Both seek local ownership of semantically cohesive behavior; current-work discovery remains a separate technique. |
| CHG-LEG-004 seam plus enabling point | `legacy.controllable-seam` | A seam without an enabling point is not operational; the enabling point remains a graph property, not a separately routable doctrine record. |
| CHG-HIST-001 and broad “history is triage, not verdict” formulations | `metric-as-signal` | Same epistemic rule as adjacent architecture metrics; specialist signals remain distinct children. |
| CHG-HIST-007 | `team-topology-force` | Same canonical architectural force already proposed elsewhere, enriched here with attribution/coordination evidence limits. |
| Suspicious-behavior CHG-LEG-003 | `testing.characterization` plus `change.stop-backtrack-escalate` | Suspicion is a characterization outcome requiring an authority transition, not a general design concept. |
| Monster-method CHG-LEG-011 | `change.verified-small-step-loop` plus `legacy.current-work-responsibility-discovery` | “Extract what you know,” current-owner-first, and redo are specialized mechanics, retained in procedure refinement rather than duplicate concepts. |

### Deliberately distinct concepts

| Concepts kept distinct | Operational difference |
|---|---|
| `universal.behavior-preservation` vs `testing.characterization` | Preservation is an obligation; characterization is one method for discovering/protecting observed behavior. |
| `change.refactoring-pressure` vs `metric-as-signal` | Pressure is the action proof; a metric only nominates evidence to investigate. |
| `design.knowledge-duplication` vs `design.earned-abstraction` | One diagnoses repeated semantic authority; the other decides whether an indirection is worth its costs. |
| `change.directional-campaign` vs `change.splinter-campaign` | The former governs any broad structural direction; the latter is a congestion-specific facade-preserving first pattern. |
| `legacy.provisional-dependency-break` vs `legacy.sprout-wrap` | A dependency break enables feedback on existing code; sprout/wrap isolates new behavior under pressure. |
| `testing.pinch-point` vs `testing.provisional-safety-net` | Pinch point is an observation topology; a provisional safety net is a lifecycle-governed broad test asset. |
| `change.transformation-tool-trust` vs `legacy.unprotected-enabling-edit` | Tool trust governs automated mechanics generally; unprotected enabling edits are last-resort, initially testless, legacy-specific actions. |
| `evidence.hotspot` vs `evidence.complexity-trend` | A hotspot ranks activity × rough difficulty; a trend describes structural trajectory and can corroborate or falsify a hotspot concern. |
| `evidence.change-coupling` vs `evidence.logical-change-set` | Co-change is the relationship measure; logical change set is the grouping mechanism required across split commits/repos. |
| `evidence.code-age` vs `change.leave-stable-code-alone` | Age is an ambiguous signal; leaving code alone is a terminal evidence-and-risk decision. |
| `team-topology-force` vs `agent.behavioral-metrics-not-performance` | Team topology informs system risk; the prohibition constrains any individual-evaluation use regardless of data quality. |
| `domain.behavioral-boundary-candidate` vs `bounded-context` | Historical clustering nominates a candidate; semantic coherence and explicit ownership establish a Bounded Context. |

## Source-formulation ledger

Claims are canonical paraphrases, not quotations. Source silence is not support.

| Canonical ID | Source | Relation | Source-specific formulation | Exact locator |
|---|---|---|---|---|
| `change.type-classification` | SRC-WELC | direct_support | Feature addition, defect repair, design improvement/refactoring, and optimization differ by purpose and by which existing behavior may change. | `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software`; `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Adding Features and Fixing Bugs` |
| `change.type-classification` | SRC-REF | refinement | Refactoring is explicitly behavior-preserving structural change and should be distinguished from cleanup or performance work. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Refactoring and Performance` |
| `universal.behavior-preservation` | SRC-REF | direct_support | Refactoring changes internal structure without changing observable behavior. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring` |
| `universal.behavior-preservation` | SRC-WELC | corroboration | Safe change asks what must change and how both correctness and nonbreakage will be known. | `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Risky Change` |
| `universal.behavior-preservation` | SRC-SDX | refinement | Hotspot splitting keeps the old API/facade and uses regression protection to contain ripple during intermediate states. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters` |
| `change.semantic-structural-separation` | SRC-REF | direct_support | Adding functionality and restructuring are separate hats; switch consciously rather than blending them. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats` |
| `change.semantic-structural-separation` | SRC-WELC | corroboration | Testless dependency breaking should have one goal, preserve signatures, and avoid simultaneous design improvement. | `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Preserve Signatures` |
| `change.verified-small-step-loop` | SRC-REF | direct_support | Repeated test–small-change cycles localize errors, and uncertainty should trigger backtracking. | `SRC-REF: chapters/005-chapter-1-refactoring-a-first-example.md :: ## Final Thoughts`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: #### Backtrack.` |
| `change.verified-small-step-loop` | SRC-WELC | corroboration | Extract only small understood pieces from a monster method and be willing to redo them as understanding improves. | `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: #### Extract Small Pieces`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: #### Be Prepared to Redo Extractions` |
| `change.verified-small-step-loop` | SRC-SDX | refinement | A congested hotspot is split one quickly integrated responsibility at a time to limit parallel merge exposure. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Parallel Development Is at Conflict with Refactoring`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities` |
| `change.stop-backtrack-escalate` | SRC-REF | direct_support | Stop when unsure; retain an independently better state or return to the last safe point. | `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ### Stop when you are unsure.`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: #### Backtrack.` |
| `change.stop-backtrack-escalate` | SRC-WELC | refinement | Unexpected characterized behavior should be marked and investigated rather than silently changed. | `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ### When You Find Bugs` |
| `change.refactoring-pressure` | SRC-REF | direct_support | Refactoring is normally performed in service of feature, repair, or review work, with explicit conditions where it should not be done. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?` |
| `change.refactoring-pressure` | SRC-WELC | refinement | In a large class, current work is the most useful guide to which responsibility, if any, should be separated. | `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work` |
| `change.refactoring-pressure` | SRC-SDX | refinement | Change frequency, complexity, co-change, and trends prioritize where maintenance pressure is likely to repay expert attention. | `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots` |
| `change.smell-as-hypothesis` | SRC-REF | direct_support | Smells are intuitive indications and their catalog remedies depend on context; switches, comments, large units, and inheritance are not automatic defects. | `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code`; `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ### Switch Statements`; `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ### Comments` |
| `change.smell-as-hypothesis` | SRC-SDX | corroboration | Code quality is contextual and hotspot findings should improve investigation, not judge code or people. | `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Are You Telling Me Code Quality Isn't Important?`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge` |
| `design.knowledge-duplication` | SRC-REF | direct_support | Duplicated code may force parallel changes and is a smell to investigate. | `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Duplicated Code` |
| `design.knowledge-duplication` | SRC-SDX | refinement | Copy-paste matters when clones continue to change together; similarity alone is common and insufficient. | `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ### Clone Detection 101` |
| `design.earned-abstraction` | SRC-SDX | direct_support | A shared abstraction is warranted by enough common knowledge and evolution; otherwise proximity or deliberate duplication may communicate better and avoid flags. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste` |
| `design.earned-abstraction` | SRC-REF | corroboration | Repeated change can justify consolidation, while speculative generality should be removed when its variation is unused. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Rule of Three`; `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Speculative Generality` |
| `change-locality-cohesion` | SRC-REF | direct_support | Move or extract behavior toward the object that owns the data and responsibility, or inline an unjustified boundary. | `SRC-REF: chapters/011-chapter-7-moving-features-between-objects.md :: ## Move Method`; `SRC-REF: chapters/011-chapter-7-moving-features-between-objects.md :: ### Extract Class`; `SRC-REF: chapters/011-chapter-7-moving-features-between-objects.md :: ### Inline Class` |
| `change-locality-cohesion` | SRC-WELC | refinement | Discover responsibilities from method/data relationships and current work rather than from size or an ideal static decomposition. | `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## Seeing Responsibilities`; `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work` |
| `change-locality-cohesion` | SRC-SDX | refinement | Co-changing functions and domain concepts can suggest proximity or component candidates, but domain knowledge decides their meaning. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns` |
| `change.compatibility-migration` | SRC-REF | direct_support | Published callers and database data make an otherwise local refactoring a compatibility and migration problem. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Changing Interfaces`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Databases` |
| `change.compatibility-migration` | SRC-WELC | corroboration | Preserve signatures while creating an initial safe seam so existing clients are not broadened into the first uncertain edit. | `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Preserve Signatures` |
| `change.compatibility-migration` | SRC-SDX | refinement | A hotspot facade can preserve existing clients while internal responsibilities are extracted and later caller migration is separately considered. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters` |
| `change.transformation-tool-trust` | SRC-REF | direct_support | Refactoring-tool safety depends on semantic accuracy, program representation, speed, undo, and integration—not operation naming alone. | `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Technical Criteria for a Refactoring Tool`; `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`; `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ### Undo` |
| `change.transformation-tool-trust` | SRC-WELC | refinement | Trusted automated extraction can be safer without tests only when manual edits are not mixed; compiler assistance still has blind spots. | `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: ## Tackling Monsters with Automated Refactoring Support`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Lean on the Compiler` |
| `change.directional-campaign` | SRC-REF | direct_support | Big refactorings are long-running directions that discover intermediate structure rather than single catalog operations. | `SRC-REF: chapters/016-chapter-12-big-refactorings.md :: ## The Nature of the Game`; `SRC-REF: chapters/016-chapter-12-big-refactorings.md :: ### Why Big Refactorings Are Important` |
| `change.directional-campaign` | SRC-SDX | refinement | Replacement risks hidden requirements and catch-up; large improvement should proceed through protected, quickly integrated states. | `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## The Trade-Off Between Architectural Refinements and Replacement Systems`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern` |
| `change.leave-stable-code-alone` | SRC-REF | direct_support | Do not refactor when code cannot be stabilized, a rewrite is more appropriate, or near-term timing and protection do not justify it. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?` |
| `change.leave-stable-code-alone` | SRC-SDX | corroboration | Ugly code with little active cost may be lower priority, while old code can also be dead or risky and must be contextualized. | `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: #### Interest Rate Is a Function of Time`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code` |
| `legacy.cover-and-modify` | SRC-WELC | direct_support | Identify change points and test points, break blocking dependencies, write tests, then make the change and refactor. | `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm`; `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Make Changes and Refactor` |
| `legacy.cover-and-modify` | SRC-REF | corroboration | A working test surface precedes the small structural steps of ordinary refactoring. | `SRC-REF: chapters/005-chapter-1-refactoring-a-first-example.md :: ## The First Step in Refactoring`; `SRC-REF: chapters/008-chapter-4-building-tests.md :: ## The Value of Self-testing Code` |
| `testing.characterization` | SRC-WELC | direct_support | Characterization tests discover and encode what relevant code actually does; they stop when enough behavior is known to sense the intended change. | `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## A Heuristic for Writing Characterization Tests` |
| `testing.characterization` | SRC-SDX | refinement | When local tests are unavailable, a black-box provisional suite can capture current user-visible behavior for the first restructuring step. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Introduce Provisional End-to-End Tests` |
| `legacy.controllable-seam` | SRC-WELC | direct_support | A seam is a place where behavior can vary without editing the use site, and every usable seam has an enabling point that selects the variation. | `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ### Object Seams` |
| `legacy.controllable-seam` | SRC-REF | corroboration | Indirection can isolate change, but its value and cost must be evaluated rather than added categorically. | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Indirection and Refactoring` |
| `testing.test-double-scope` | SRC-WELC | direct_support | A fake supports a real local test by making behavior observable or executable; mock interaction is not automatically the application contract. | `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: ## Faking Collaborators`; `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: #### Fake Objects Support Real Tests`; `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: ## Mock Objects` |
| `legacy.provisional-dependency-break` | SRC-WELC | direct_support | The legacy dilemma may require a small production edit to create tests; dependency-breaking scars can be tolerated locally and reconsidered after feedback exists. | `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### The Legacy Code Dilemma`; `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Break Dependencies` |
| `legacy.provisional-dependency-break` | SRC-SDX | corroboration | A temporary facade or provocative name can make an incomplete intermediate state explicit during an iterative hotspot split. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Signal Incompleteness with Names`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters` |
| `testing.effect-surface` | SRC-WELC | direct_support | Effects propagate through returns, mutation, globals/statics, and downstream calls; tests should be selected from that forward effect graph. | `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Reasoning About Effects`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ### Effects and Encapsulation` |
| `testing.pinch-point` | SRC-WELC | direct_support | A pinch point intercepts effects for a cluster and can avoid breaking every dependency, but higher-level points have traps and weaker localization. | `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ## Interception Points`; `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: #### Pinch Point`; `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ## Traps Pinch Point Traps` |
| `testing.pinch-point` | SRC-SDX | refinement | A broad temporary E2E surface may initially protect a hotspot until narrower tests become possible. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net` |
| `legacy.current-work-responsibility-discovery` | SRC-WELC | direct_support | Method/data relationships and the present change reveal one responsibility more reliably than attempting a complete decomposition from static size. | `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## Seeing Responsibilities`; `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work` |
| `legacy.current-work-responsibility-discovery` | SRC-SDX | corroboration | Function-level activity can select which recognized behavior group to extract first from a hotspot. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities` |
| `learning.scratch-refactoring` | SRC-WELC | direct_support | Aggressive disposable extraction, renaming, and deletion can reveal structure and effects; production work should restart from a clean baseline. | `SRC-WELC: chapters/024-chapter-16-i-don-t-understand-the-code-well-enough-to-change-it.md :: ## Scratch Refactoring`; `SRC-WELC: chapters/024-chapter-16-i-don-t-understand-the-code-well-enough-to-change-it.md :: #### Understand the Effects of a Change` |
| `legacy.sprout-wrap` | SRC-WELC | direct_support | Sprout places new tested behavior beside old code; wrap inserts behavior around it; both trade speed for integration/design costs. | `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Sprout Method`; `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ### Sprout Class`; `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Wrap Method`; `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Wrap Class` |
| `testing.provisional-safety-net` | SRC-SDX | direct_support | Brittle black-box/E2E tests may be justified as temporary refactoring protection and should be disposed of or narrowed after the intermediate goal. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Introduce Provisional End-to-End Tests` |
| `testing.provisional-safety-net` | SRC-WELC | corroboration | A higher-level test covering can provide initial safety while localized tests are unavailable. | `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ### Test Coverings` |
| `legacy.unprotected-enabling-edit` | SRC-WELC | direct_support | When no test can exist before the first seam, use hyperaware single-goal editing, preserve signatures, lean on compiler/reference checks, and pair/review. | `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Hyperaware Editing`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Lean on the Compiler`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: #### Pair Programming` |
| `metric-as-signal` | SRC-SDX | direct_support | Behavioral metrics and visualizations focus human expertise and do not make design or quality decisions. | `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ### Complex Questions Require Context`; `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Your Code Is Still a Crime Scene` |
| `metric-as-signal` | SRC-REF | corroboration | Smells and catalog transformations require human contextual judgment rather than metric-like automatic application. | `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code`; `SRC-REF: chapters/009-chapter-5-toward-a-catalog-of-refactorings.md :: ### How Mature Are These Refactorings?` |
| `evidence.hotspot` | SRC-SDX | direct_support | Change frequency combined with rough complexity/size ranks code where future changes would repeatedly pay maintenance cost. | `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## A Proxy for Interest Rate`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Use X-Rays to Get Deep Insights into Code` |
| `evidence.change-coupling` | SRC-SDX | direct_support | Files/functions that repeatedly change in the same logical changes have a relationship to explain; expected test/implementation coupling may be healthy. | `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ### What Is Change Coupling?`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Detect Cochanging Files`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Learn More About Change Coupling` |
| `evidence.change-coupling` | SRC-REF | refinement | Divergent change and shotgun surgery name static/observed symptoms that historical co-change can help corroborate. | `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ### Divergent Change`; `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Shotgun Surgery` |
| `evidence.complexity-trend` | SRC-SDX | direct_support | Trends and repository-relative deltas reveal accumulation while avoiding noisy universal thresholds; language/style biases remain. | `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Evaluate Hotspots with Complexity Trends`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Know the Biases in Complexity Trends`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Wouldn't an Absolute and Universal Threshold Be Better?` |
| `evidence.code-age` | SRC-SDX | direct_support | Last-change age distinguishes active and stable regions only after reference date, product activity, domain, generated content, tests, and dead-code alternatives are considered. | `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Stabilize Code by Age`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### The Business Domain Is Above Age`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code` |
| `evidence.behavioral-data-fitness` | SRC-SDX | direct_support | Aliases, pair/mob work, squashes, copied history, generated/noncode files, organizational shifts, and task grouping can invalidate social or technical inference. | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: #### Watch Out for Authors with Multiple Aliases`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ### Specify a Start Date with Organizational Significance` |
| `team-topology-force` | SRC-SDX | direct_support | Fragmented active ownership may reveal coordination/diffusion risk; operational responsibility can be narrow while knowledge boundaries remain broad. | `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Measure Coordination Needs`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Code Ownership Means Responsibility`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Provide Broad Knowledge Boundaries` |
| `team-topology-force` | SRC-SDX | refinement | Technical dependencies and team ownership should be considered together; neither alone dictates an organizational boundary. | `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Combine Social and Technical Information`; `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Optimize for Sociotechnical Congruence Across Boundaries` |
| `agent.behavioral-metrics-not-performance` | SRC-SDX | direct_support | Knowledge/commit/LOC/defect metrics used for individual evaluation create adaptive gaming, erase context, damage collaboration, and destroy the data source. | `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Don't Turn Knowledge Maps into Performance Evaluations`; `SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## Adaptive Behavior and the Destruction of a Data Source`; `SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## The Situation Is Invisible in Code` |
| `domain.behavioral-boundary-candidate` | SRC-SDX | direct_support | Co-change clusters across technical layers can nominate components or bounded contexts, but source inspection and domain expertise choose the model. | `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Look for Clusters of Cochanging Files`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### The Big Win Is in the Problem Domain` |
| `domain.behavioral-boundary-candidate` | SRC-WELC | refinement | Effect sketches and current-work responsibility discovery can reveal hidden classes but do not establish final domain boundaries. | `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ### Using Effect Sketches to Find Hidden Classes`; `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work` |
| `change.splinter-campaign` | SRC-SDX | direct_support | In a congested active hotspot, extract one high-activity behavior behind the old API, regress, integrate quickly, and repeat based on new evidence. | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters` |
| `change.splinter-campaign` | SRC-REF | corroboration | Big refactorings advance through many ordinary transformations and intermediate states. | `SRC-REF: chapters/016-chapter-12-big-refactorings.md :: ## The Nature of the Game` |
| `evidence.logical-change-set` | SRC-SDX | direct_support | Cross-repository or split-commit coupling requires grouping by ticket/task ID where possible, or a lower-confidence same-author/team time window. | `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: #### Use Logical Change Sets to Group Commits`; `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Detect Implicit Dependencies Between Microservices` |
| `review.behavioral-early-warning` | SRC-SDX | direct_support | Rising hotspot rank, relative complexity increase, or absent expected co-change should focus early review while permitting intentional divergence. | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Identify Steep Increases in Complexity`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Detect Future Hotspots`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Catch the Absence of Change` |

## Full canonical concept records

### Core change and refactoring records

```yaml
id: change.type-classification
title: Classify change by purpose and semantic permission
category: agent-conduct
claim: A change label is valid only when its purpose and allowable observable delta match the actual work.
decision_rule: Inventory intended observable deltas, classify the primary purpose, and split mixed purposes into separately authorized and verified slices.
why_it_matters: Classification determines authority, preservation, tests, review, rollout, and rollback; misleading labels hide risk.
applicable_when: [planning any repository write, reviewing a mixed diff, describing a campaign]
not_applicable_when: [pure observation with no proposed mutation]
required_evidence: [request and acceptance criteria, current behavior, accepted contracts, proposed semantic delta]
insufficient_evidence: [issue label, commit title, cleanup wording, code movement]
required_inputs: [authority statement, current and desired behavior, affected boundaries]
expected_outputs: [change type, authorized delta, invariant list, ordered slices]
preservation_boundaries: All observable behavior outside the authorized delta.
safe_actions: [repair then refactor on green, name migration explicitly, separate optimization from semantics]
unsafe_actions: [call behavior change refactoring, hide API migration in cleanup, bundle unrelated repair]
common_failure_modes: [review ambiguity, missing rollback, untested semantic drift]
counterexamples: [A private local rename with unchanged behavior is ordinary refactoring.]
interactions: [universal.behavior-preservation, change.semantic-structural-separation, change.compatibility-migration]
conflicts: [conflict.change.refactoring-versus-repair]
source_support:
  - "`SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software`"
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`"
confidence: universal
roles: [coding-agent, refactoring-agent, legacy-agent, repair-agent, review-agent, architecture-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [change type, refactoring versus repair, semantic delta, cleanup, migration]
activate_for_roles: [all execution and review roles]
activate_for_tasks: [implementation, repair, refactoring, migration, optimization, cleanup, deletion]
activate_for_repository_signals: [mixed-purpose diff, public contract, behavior change]
activate_for_languages: [all]
activate_for_risk_classes: [all]
exclude_when: [read-only orientation without recommendation]
prerequisites: [request and authority inventory]
retrieval_priority: core
retrieval_budget_hint: 250-400 tokens
related_concepts: [universal.behavior-preservation, change.semantic-structural-separation]
```

```yaml
id: universal.behavior-preservation
title: Explicit behavior-preservation boundary
category: universal
claim: Unless change is authorized, externally observable behavior remains invariant across structural work.
decision_rule: Enumerate authorized deltas; treat every other output, error, side effect, stored format, protocol, ordering, timing, durability, and supported caller interaction as preserved until evidence narrows it.
why_it_matters: Tests expose only selected observations; an explicit boundary prevents silent semantic assumptions.
applicable_when: [refactoring, repair, migration, optimization, legacy change]
not_applicable_when: [an implementation detail with no observable or contractual consequence]
required_evidence: [requirements or ADRs, callers, tests, runtime observations, schemas, incidents]
insufficient_evidence: [green unit tests alone, compilation alone, internal method shape]
required_inputs: [authorized delta, observable-surface inventory]
expected_outputs: [preservation matrix, check per material invariant, unknowns]
preservation_boundaries: The concept defines the preservation boundary; each surface must name its owner and evidence.
safe_actions: [characterize uncertain behavior, explicitly record gaps, use layered checks]
unsafe_actions: [claim preservation from compilation, ignore errors or side effects, freeze irrelevant internals]
common_failure_modes: [incomplete surface inventory, accidental behavior frozen indiscriminately, false test confidence]
counterexamples: [An authorized defect repair changes the failing case while preserving the surrounding boundary.]
interactions: [testing.characterization, testing.effect-surface, change.compatibility-migration]
conflicts: [conflict.change.refactoring-versus-repair]
source_support:
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`"
  - "`SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Risky Change`"
confidence: universal
roles: [all engineering agents]
languages: [language-independent]
repository_archetypes: [all, especially weakly-tested and durable systems]
retrieval_terms: [behavior preservation, invariant, regression boundary, semantic equivalence]
activate_for_roles: [all execution and review roles]
activate_for_tasks: [any code or data change]
activate_for_repository_signals: [weak tests, public API, persistence, side effects]
activate_for_languages: [all]
activate_for_risk_classes: [all, highest priority for high consequence]
exclude_when: [pure observation]
prerequisites: [change.type-classification]
retrieval_priority: core
retrieval_budget_hint: 350-550 tokens
related_concepts: [testing.characterization, testing.effect-surface]
```

```yaml
id: change.semantic-structural-separation
title: Separate semantic and structural work
category: refactoring
claim: An agent should pursue one semantic or structural goal at a time so evidence remains attributable.
decision_rule: Establish a green or characterized baseline, complete and verify one purpose, then switch hats at an explicit checkpoint.
why_it_matters: Mixed axes make failures ambiguous, rollback coarse, and review claims misleading.
applicable_when: [feature plus cleanup, repair plus extraction, optimization plus algorithm change]
not_applicable_when: [one atomic semantics-aware mechanical operation]
required_evidence: [slice intent, baseline result, named verification, authority for semantic deltas]
insufficient_evidence: [small total diff, obviousness, one issue containing both goals]
required_inputs: [campaign goal, work ledger]
expected_outputs: [ordered single-purpose slices, deferred-finding ledger]
preservation_boundaries: Structural slices preserve all behavior; semantic slices change only their accepted cases.
safe_actions: [write failing test and repair, return green, then refactor]
unsafe_actions: [move and alter algorithm together, fix incidental behavior during characterization]
common_failure_modes: [bisect-resistant commits, false refactoring label, multi-cause failures]
counterexamples: [A semantics-aware private rename updates declaration and callers as one structural operation.]
interactions: [change.type-classification, change.verified-small-step-loop, change.stop-backtrack-escalate]
conflicts: [conflict.change.refactoring-versus-repair]
source_support:
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`"
  - "`SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing`"
confidence: universal
roles: [coding-agent, repair-agent, refactoring-agent, legacy-agent, review-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [two hats, single goal, semantic versus structural, mixed diff]
activate_for_roles: [execution and review roles]
activate_for_tasks: [mixed implementation and refactoring, repair, optimization]
activate_for_repository_signals: [unrelated diff hunks, failing checks after broad edit]
activate_for_languages: [all]
activate_for_risk_classes: [all]
exclude_when: [read-only assessment]
prerequisites: [change.type-classification, universal.behavior-preservation]
retrieval_priority: core
retrieval_budget_hint: 250-400 tokens
related_concepts: [change.verified-small-step-loop, change.stop-backtrack-escalate]
```

```yaml
id: change.verified-small-step-loop
title: Short verified transformation loop
category: refactoring
claim: Structural safety comes from small reversible moves with feedback, not from the intended final design alone.
decision_rule: Make the smallest move that advances one goal, run the cheapest relevant check, checkpoint coherent green states, and broaden checks at integration boundaries.
why_it_matters: Short feedback minimizes simultaneous uncertainty and localizes error to the last move.
applicable_when: [manual refactoring, legacy extraction, hotspot campaign, codemod staging]
not_applicable_when: [requiring an expensive full suite after every keystroke when a reliable check ladder exists]
required_evidence: [known baseline, move-specific expectation, fast check, rollback point]
insufficient_evidence: [only a final suite after an opaque rewrite, compile-only for semantic risk]
required_inputs: [target, check ladder, campaign goal]
expected_outputs: [verified step sequence, green checkpoints]
preservation_boundaries: Each structural step preserves the established boundary.
safe_actions: [extract then targeted test, commit coherent green slice, redo an early extraction]
unsafe_actions: [defer all verification, accumulate unrelated moves, long isolated refactor without integration]
common_failure_modes: [steps too large, flaky feedback, ritual microsteps with no causal value]
counterexamples: [A trusted tool may perform an internally atomic repository-wide rename, followed by repository checks.]
interactions: [universal.minimize-simultaneous-uncertainty, change.transformation-tool-trust, change.stop-backtrack-escalate]
conflicts: [conflict.change.tests-before-enabling-edit]
source_support:
  - "`SRC-REF: chapters/005-chapter-1-refactoring-a-first-example.md :: ## Final Thoughts`"
  - "`SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: #### Extract Small Pieces`"
confidence: strong
roles: [coding-agent, refactoring-agent, legacy-agent, repair-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [small steps, test change rhythm, reversible refactoring, green checkpoint]
activate_for_roles: [execution roles]
activate_for_tasks: [refactoring, dependency breaking, codemod, legacy extraction]
activate_for_repository_signals: [fragile tests, large diff, merge congestion]
activate_for_languages: [all]
activate_for_risk_classes: [all]
exclude_when: [pure analysis]
prerequisites: [baseline and check ladder]
retrieval_priority: core
retrieval_budget_hint: 300-500 tokens
related_concepts: [universal.minimize-simultaneous-uncertainty, change.stop-backtrack-escalate]
```

```yaml
id: change.stop-backtrack-escalate
title: Stop, backtrack, or escalate on lost certainty
category: agent-conduct
claim: The agent must stop when it can no longer state what changed, what remains invariant, why a check failed, or whether it has authority.
decision_rule: Return to the last known-good state; retain only an independently useful protected subset; otherwise reverse the agent-owned slice or escalate the behavior/authority choice.
why_it_matters: Continuing converts explicit uncertainty into hidden risk and unauthorized decisions.
applicable_when: [ambiguous failure, surprising behavior, authority gap, irreversible next step]
not_applicable_when: [safe read-only investigation can still reduce uncertainty]
required_evidence: [baseline, current diff, failure output, ownership and authority]
insufficient_evidence: [sunk cost, deadline, confidence without reproducer]
required_inputs: [campaign goal, last green point, uncertainty ledger]
expected_outputs: [continue, retain-smaller, backtrack, or escalate decision with reason]
preservation_boundaries: Do not cross an unresolved semantic, public, data, production, or authority boundary.
safe_actions: [discard scratch work, keep green seam, present alternatives]
unsafe_actions: [debug forward through many edits, silently choose expected behavior, reverse user changes]
common_failure_modes: [premature abandonment, destructive rollback, escalation without prior safe investigation]
counterexamples: [A newly authorized semantic delta can resume as a separately classified slice.]
interactions: [universal.authority-discipline, testing.characterization, change.verified-small-step-loop]
conflicts: [conflict.change.stable-code-versus-proactive-work]
source_support:
  - "`SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ### Stop when you are unsure.`"
  - "`SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ### When You Find Bugs`"
confidence: universal
roles: [all agents]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [stop condition, backtrack, escalate, uncertain behavior, authority]
activate_for_roles: [all]
activate_for_tasks: [any active campaign]
activate_for_repository_signals: [failing checks, ambiguous behavior, public or production boundary]
activate_for_languages: [all]
activate_for_risk_classes: [all]
exclude_when: [none]
prerequisites: [last known-good state]
retrieval_priority: core
retrieval_budget_hint: 250-400 tokens
related_concepts: [universal.authority-discipline, change.verified-small-step-loop]
```

```yaml
id: change.refactoring-pressure
title: Evidence that earns refactoring
category: refactoring
claim: Structural intervention requires demonstrated present or imminent maintenance pressure, not unattractiveness alone.
decision_rule: Require a concrete goal and verified pressure such as repeated coupled edits, dispersed responsibility, blocked testing, recurring defects, active complexity growth, or material review/cognitive cost; select the smallest response.
why_it_matters: Refactoring spends risk and review capacity and should target recurring cost.
applicable_when: [refactoring proposal, cleanup request, architecture improvement assessment]
not_applicable_when: [an independently authorized platform migration, though it needs its own evidence]
required_evidence: [current task, call sites, history, defects, test friction, review or domain evidence]
insufficient_evidence: [file length, smell name, generic style, churn alone]
required_inputs: [pressure ledger, candidate responses]
expected_outputs: [earned, not-earned, or uncertain decision and verification target]
preservation_boundaries: Any selected structural action remains behavior-preserving unless separately authorized.
safe_actions: [refactor adjacent to required work, rank a measured hotspot for inspection]
unsafe_actions: [broad aesthetic cleanup, automatic split from a threshold]
common_failure_modes: [metric-driven churn, wrong bottleneck, under-refactoring where history is unavailable]
counterexamples: [A security-driven structural migration can be earned by external risk rather than prior churn.]
interactions: [metric-as-signal, evidence.hotspot, change.leave-stable-code-alone]
conflicts: [conflict.change.opportunistic-versus-ranked-campaign]
source_support:
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?`"
  - "`SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data`"
confidence: strong
roles: [refactoring-agent, review-agent, architecture-agent, repository-assessment-agent]
languages: [language-independent]
repository_archetypes: [all nongenerated code]
retrieval_terms: [refactoring evidence, structural pressure, technical debt, leave alone]
activate_for_roles: [refactoring, review, assessment, architecture]
activate_for_tasks: [decide whether to refactor, select campaign]
activate_for_repository_signals: [smell, hotspot, change friction, test blockage]
activate_for_languages: [all]
activate_for_risk_classes: [all]
exclude_when: [generated or vendored code without source-owner task]
prerequisites: [repository orientation, preservation feasibility]
retrieval_priority: core
retrieval_budget_hint: 350-600 tokens
related_concepts: [metric-as-signal, change.leave-stable-code-alone]
```

```yaml
id: change.smell-as-hypothesis
title: Treat smells as falsifiable hypotheses
category: refactoring
claim: A smell names an investigation question and neither proves a defect nor selects a transformation.
decision_rule: Translate the smell into an operational maintenance consequence, test it against callers, change history, responsibilities, runtime constraints, and repository idiom, then act only when the hypothesis survives.
why_it_matters: Surface forms are context-sensitive and automatic remedies often create indirection or destroy rationale.
applicable_when: [long method, large class, switch, comments, duplication, middle man, inheritance findings]
not_applicable_when: [a direct contractual violation already establishes a defect]
required_evidence: [specific consequence, causal link, repository context]
insufficient_evidence: [detector output, threshold count, catalog match, reviewer taste]
required_inputs: [smell candidate, current source and use evidence]
expected_outputs: [confirmed, refuted, or uncertain hypothesis and next observation]
preservation_boundaries: Investigation does not authorize structural or semantic change.
safe_actions: [inspect why a long unit changes, retain rationale comments, compare alternative remedies]
unsafe_actions: [split by size, replace every switch with polymorphism, delete comments automatically]
common_failure_modes: [cargo-cult patterns, shallow modules, false blocker review]
counterexamples: [Repeated dispersed edits with omission defects can strongly confirm shotgun surgery.]
interactions: [change.refactoring-pressure, metric-as-signal, design.earned-abstraction]
conflicts: [conflict.change.small-units-versus-deep-module, conflict.change.comments-versus-structure]
source_support:
  - "`SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code`"
  - "`SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge`"
confidence: strong
roles: [coding-agent, refactoring-agent, review-agent, repository-assessment-agent]
languages: [language-independent, with source OO bias]
repository_archetypes: [all nongenerated code]
retrieval_terms: [code smell, heuristic not verdict, long method, large class]
activate_for_roles: [refactoring, review, assessment]
activate_for_tasks: [evaluate smell, review structure]
activate_for_repository_signals: [static smell finding, size threshold, style objection]
activate_for_languages: [all]
activate_for_risk_classes: [all]
exclude_when: [generated and vendored output]
prerequisites: [maintenance-consequence hypothesis]
retrieval_priority: core
retrieval_budget_hint: 300-450 tokens
related_concepts: [change.refactoring-pressure, metric-as-signal]
```

```yaml
id: design.knowledge-duplication
title: Repeated semantic knowledge
category: refactoring
claim: Duplication is harmful when multiple sites encode one policy, invariant, or postcondition and must evolve together.
decision_rule: Compare semantic meaning, co-change, omission history, variation, domain context, and ownership before diagnosing duplicated knowledge.
why_it_matters: Token similarity is common; semantic duplication creates change amplification and inconsistency risk.
applicable_when: [clone findings, repeated assertions, parallel conditionals, repeated policy]
not_applicable_when: [generated derivatives with one source, independently evolving domain examples]
required_evidence: [semantic comparison, expected evolution, repeated changes or shared invariant]
insufficient_evidence: [clone percentage, two occurrences, syntactic resemblance]
required_inputs: [duplicate sites, call contexts, history and ownership]
expected_outputs: [knowledge-duplication diagnosis or explicit nonfinding]
preservation_boundaries: Diagnosis does not yet authorize extraction.
safe_actions: [identify authoritative knowledge, document intentional local duplication]
unsafe_actions: [equate text with knowledge, cross bounded contexts automatically]
common_failure_modes: [false DRY finding, missed omission risk, generator output refactored directly]
counterexamples: [Two protocol adapters may resemble each other but evolve under independent vendors.]
interactions: [design.earned-abstraction, evidence.change-coupling, change-locality-cohesion]
conflicts: [conflict.change.abstraction-versus-duplication]
source_support:
  - "`SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Duplicated Code`"
  - "`SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste`"
confidence: strong
roles: [coding-agent, refactoring-agent, review-agent]
languages: [language-independent]
repository_archetypes: [application, test, infrastructure code]
retrieval_terms: [duplication, clone, repeated knowledge, DRY, co-change]
activate_for_roles: [coding, refactoring, review]
activate_for_tasks: [evaluate duplication]
activate_for_repository_signals: [clone alert, repeated edits, omission defects]
activate_for_languages: [all]
activate_for_risk_classes: [normal, high when cross-boundary]
exclude_when: [generated artifacts unless analyzing generator]
prerequisites: [semantic comparison]
retrieval_priority: high
retrieval_budget_hint: 300-500 tokens
related_concepts: [design.earned-abstraction, evidence.change-coupling]
```

```yaml
id: design.earned-abstraction
title: Evidence gate for abstraction
category: implementation
claim: Shared indirection is earned only when demonstrated semantic commonality and expected co-evolution outweigh interface, navigation, ownership, and migration costs.
decision_rule: Model retain, proximity, generation, and extraction options; abstract only a stable nameable concept with a tractable variation axis and lower total change cost.
why_it_matters: Removing text can create boolean flags, shallow layers, blurred ownership, and cross-context coupling.
applicable_when: [duplicate knowledge, interface proposal, shared helper, reusable component]
not_applicable_when: [decorative symmetry, hypothetical reuse, independent domain evolution]
required_evidence: [shared invariant or policy, co-evolution, consumers, stable variation, cost comparison]
insufficient_evidence: [similarity, Rule of Three alone, one consumer, taste]
required_inputs: [candidate sites, consumer and ownership map, evolution evidence]
expected_outputs: [retain, proximity, generate, or abstract decision with rationale]
preservation_boundaries: Preserve local readability, semantics, ownership, and compatibility.
safe_actions: [extract repeated postcondition, colocate intentional clones, delay uncertain abstraction]
unsafe_actions: [parameter maze, shared abstraction across conflicting bounded contexts]
common_failure_modes: [premature abstraction, common utility dumping ground, ownership bottleneck]
counterexamples: [Distinct tests may remain explicit even when setup text is similar.]
interactions: [design.knowledge-duplication, change-locality-cohesion, bounded-context]
conflicts: [conflict.change.abstraction-versus-duplication]
source_support:
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`"
  - "`SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Speculative Generality`"
confidence: strong-contextual
roles: [coding-agent, refactoring-agent, review-agent, architecture-agent]
languages: [language-independent]
repository_archetypes: [all nongenerated code]
retrieval_terms: [earned abstraction, duplication versus abstraction, shared helper, interface]
activate_for_roles: [coding, refactoring, review, architecture]
activate_for_tasks: [introduce abstraction, remove duplication]
activate_for_repository_signals: [repeated policy, clone, proposed interface]
activate_for_languages: [all]
activate_for_risk_classes: [normal, high for public or cross-team abstraction]
exclude_when: [generated output]
prerequisites: [design.knowledge-duplication or other demonstrated variation pressure]
retrieval_priority: core
retrieval_budget_hint: 400-600 tokens
related_concepts: [design.knowledge-duplication, change-locality-cohesion]
```

```yaml
id: change-locality-cohesion
title: Place behavior by semantic and change locality
category: architecture
claim: Behavior belongs where its data, policy, invariants, authority, and independent evolution can be understood locally.
decision_rule: Map data read and written, policies and invariants, callers, co-change, lifecycle, and authority; move or split only when the new owner reduces knowledge/change dispersion without leaking internals.
why_it_matters: Placement controls cognitive load, change amplification, and boundary chatter.
applicable_when: [move method, class/module split, feature envy, component boundary]
not_applicable_when: [directory symmetry, uniform size, a cohesive deep implementation]
required_evidence: [effect and data map, invariant owner, call sites, domain and change evidence]
insufficient_evidence: [directory name, file size, naming similarity, diagram aesthetics]
required_inputs: [responsibility and ownership map]
expected_outputs: [retain, move, extract, or inline decision plus migration plan]
preservation_boundaries: Preserve invariant authority, information hiding, and external behavior.
safe_actions: [delegate through old boundary, move policy toward owned data]
unsafe_actions: [create chatty shallow units, move away from authority, infer domain from folders]
common_failure_modes: [cycles, anemic domain, middle-man growth, duplicated invariants]
counterexamples: [A large cohesive parser can remain one module behind a small interface.]
interactions: [design.earned-abstraction, legacy.current-work-responsibility-discovery, domain.behavioral-boundary-candidate]
conflicts: [conflict.change.small-units-versus-deep-module]
source_support:
  - "`SRC-REF: chapters/011-chapter-7-moving-features-between-objects.md :: ## Move Method`"
  - "`SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## Seeing Responsibilities`"
confidence: strong-contextual
roles: [coding-agent, refactoring-agent, architecture-agent, legacy-agent]
languages: [language-independent]
repository_archetypes: [domain-heavy, large legacy, modular systems]
retrieval_terms: [responsibility placement, cohesion, move method, change locality]
activate_for_roles: [coding, refactoring, architecture, legacy]
activate_for_tasks: [place behavior, split or merge module]
activate_for_repository_signals: [feature envy, shotgun surgery, mixed responsibilities]
activate_for_languages: [all]
activate_for_risk_classes: [medium, high for boundary migration]
exclude_when: [directory-only evidence]
prerequisites: [data, effect, invariant, caller map]
retrieval_priority: core
retrieval_budget_hint: 450-650 tokens
related_concepts: [design.earned-abstraction, testing.effect-surface]
```

```yaml
id: change.compatibility-migration
title: Published structural change is a compatibility migration
category: architecture
claim: Independent consumers or persisted data turn a desirable internal restructuring into a phased migration.
decision_rule: Inventory consumers and control; change atomically only when all are proven controlled, otherwise preserve an adapter or old representation, migrate observably, then remove under deprecation authority.
why_it_matters: Internal green tests do not protect deployed clients, old data, or independently released components.
applicable_when: [public API, wire protocol, event, schema, file format, multi-repo consumer]
not_applicable_when: [private proven-unreferenced symbol with atomic callers]
required_evidence: [consumer inventory, compatibility contract, ownership, rollout, rollback, telemetry where available]
insufficient_evidence: [local repository search, one-component compile, internal tests]
required_inputs: [boundary and consumer map]
expected_outputs: [atomic-edit proof or phased migration plan]
preservation_boundaries: Old clients/data remain usable through the authorized compatibility interval.
safe_actions: [adapter, dual read/write when authorized, staged deprecation]
unsafe_actions: [rename public API as refactoring, mutate schema without migration]
common_failure_modes: [orphan clients, unreadable data, permanent adapter]
counterexamples: [A private method and all callers in one compilation unit can change atomically.]
interactions: [universal.behavior-preservation, change.type-classification, change.splinter-campaign]
conflicts: [conflict.change.direct-coupling-versus-boundary]
source_support:
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Changing Interfaces`"
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Databases`"
confidence: universal-strong
roles: [architecture-agent, coding-agent, refactoring-agent, review-agent]
languages: [language-independent]
repository_archetypes: [library, service, durable system, multi-repo]
retrieval_terms: [API migration, schema migration, compatibility, deprecation, facade]
activate_for_roles: [architecture, coding, refactoring, review]
activate_for_tasks: [public rename, schema change, protocol evolution]
activate_for_repository_signals: [external callers, persisted data, multiple deployables]
activate_for_languages: [all]
activate_for_risk_classes: [high, critical for durable data]
exclude_when: [proven private atomic scope]
prerequisites: [consumer and authority inventory]
retrieval_priority: core
retrieval_budget_hint: 350-550 tokens
related_concepts: [universal.behavior-preservation, change.splinter-campaign]
```

```yaml
id: change.transformation-tool-trust
title: Bound automation trust by semantic coverage
category: refactoring
claim: Automated transformation reduces mechanical error only within the language and repository surfaces the tool models.
decision_rule: Verify tool/version support, preview edits, enumerate dynamic/config/generated/foreign-language blind spots, retain undo, and run repository-native checks.
why_it_matters: Speed and a refactoring label do not establish semantic accuracy.
applicable_when: [IDE refactor, codemod, compiler-assisted rename, bulk transformation]
not_applicable_when: [ordinary hand edit without automation, though normal verification still applies]
required_evidence: [tool contract, preview, modeled references, blind-spot inventory, post-checks]
insufficient_evidence: [vendor claim, successful command, compilation alone]
required_inputs: [operation, files/languages, dynamic and generated surfaces]
expected_outputs: [trust level, exceptions requiring review, verification plan]
preservation_boundaries: All semantic, serialized, configured, reflected, and cross-language references remain valid.
safe_actions: [semantic private rename with preview, staged codemod]
unsafe_actions: [text replace treated as semantic, opaque bulk output, no undo]
common_failure_modes: [stale config strings, reflection breakage, generated drift, shadowing errors]
counterexamples: [Compiler-enforced private rename may need compile plus focused tests, not manual reference audit everywhere.]
interactions: [change.verified-small-step-loop, legacy.unprotected-enabling-edit]
conflicts: [conflict.change.tests-before-enabling-edit]
source_support:
  - "`SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`"
  - "`SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: ## Tackling Monsters with Automated Refactoring Support`"
confidence: strong
roles: [coding-agent, refactoring-agent, review-agent, legacy-agent]
languages: [tool-specific]
repository_archetypes: [all, especially mixed-language]
retrieval_terms: [codemod, IDE refactor, automated rename, compiler trust]
activate_for_roles: [coding, refactoring, review, legacy]
activate_for_tasks: [automated transformation]
activate_for_repository_signals: [reflection, templates, generated code, serialization]
activate_for_languages: [all]
activate_for_risk_classes: [medium, high for public/dynamic surfaces]
exclude_when: [none]
prerequisites: [tool support and preview]
retrieval_priority: high
retrieval_budget_hint: 300-500 tokens
related_concepts: [change.verified-small-step-loop, legacy.unprotected-enabling-edit]
```

```yaml
id: change.directional-campaign
title: Broad refactoring as a revisable direction
category: refactoring
claim: A broad structural outcome should be delivered through protected independently valuable intermediate states and revised as knowledge grows.
decision_rule: Name the demonstrated force and target property, choose the first boundary that reduces cost/risk, preserve compatibility, integrate, remeasure, and revise or stop.
why_it_matters: Large transformations reveal requirements and domain structure during execution; a fixed end diagram creates long-lived uncertainty.
applicable_when: [modularization, legacy restructuring, inheritance separation, domain/presentation separation]
not_applicable_when: [tiny isolated atomic transformation]
required_evidence: [architectural pressure, protected first boundary, incremental value, integration cadence, stop criteria]
insufficient_evidence: [future diagram, source prestige, promise of cleanup later]
required_inputs: [force, target property, campaign options]
expected_outputs: [first bounded campaign, later candidates, remeasurement and stop signals]
preservation_boundaries: Intermediate states retain supported behavior and compatibility.
safe_actions: [facade/delegation, one useful extraction, short integration]
unsafe_actions: [months-long branch, all-at-once rewrite, destroy old path before proof]
common_failure_modes: [permanent transition, goal drift, merge conflicts, architecture astronautics]
counterexamples: [A small independent subsystem can sometimes change atomically.]
interactions: [change.splinter-campaign, change.compatibility-migration, change.stop-backtrack-escalate]
conflicts: [conflict.change.rewrite-versus-incremental]
source_support:
  - "`SRC-REF: chapters/016-chapter-12-big-refactorings.md :: ## The Nature of the Game`"
  - "`SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## The Trade-Off Between Architectural Refinements and Replacement Systems`"
confidence: strong-contextual
roles: [architecture-agent, refactoring-agent, legacy-agent]
languages: [language-independent]
repository_archetypes: [large active legacy systems]
retrieval_terms: [big refactoring, campaign, incremental transformation, rewrite]
activate_for_roles: [architecture, refactoring, legacy]
activate_for_tasks: [broad restructuring, rewrite assessment]
activate_for_repository_signals: [large active hotspot, architecture migration]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [no campaign authority]
prerequisites: [change.refactoring-pressure, protection and integration plan]
retrieval_priority: high
retrieval_budget_hint: 450-650 tokens
related_concepts: [change.splinter-campaign, change.compatibility-migration]
```

```yaml
id: change.leave-stable-code-alone
title: Evidence-governed no-change decision
category: refactoring
claim: Leave unattractive code unchanged when it has no demonstrated cost or authorized imminent change and intervention risk exceeds near-term benefit.
decision_rule: Compare activity, incidents, runtime use, roadmap and support obligations against characterization, dependency, integration, and knowledge cost; choose no change when benefit remains speculative.
why_it_matters: Mature odd code can embody hard-won behavior, and touching it resets defect risk.
applicable_when: [old stable module, rewrite proposal, cleanup audit]
not_applicable_when: [confirmed defect, vulnerability, unsupported platform, imminent required change]
required_evidence: [recent history, runtime use, incidents, roadmap, support constraints, ownership]
insufficient_evidence: [age alone, folklore, complaints, no commits in paused product]
required_inputs: [value-risk comparison]
expected_outputs: [leave, isolate, characterize, delete-investigate, or act decision with revisit trigger]
preservation_boundaries: Existing behavior remains untouched; observations do not become authorization.
safe_actions: [avoid stable code, isolate through existing boundary, record trigger]
unsafe_actions: [rewrite from dislike, declare dead from age, permanent freeze despite new risk]
common_failure_modes: [fear-driven avoidance, false stability, latent external risk]
counterexamples: [An unsupported runtime can earn migration despite low churn.]
interactions: [change.refactoring-pressure, evidence.code-age, metric-as-signal]
conflicts: [conflict.change.stable-code-versus-proactive-work]
source_support:
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?`"
  - "`SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`"
confidence: strong-contextual
roles: [refactoring-agent, architecture-agent, review-agent, repository-assessment-agent]
languages: [language-independent]
repository_archetypes: [legacy, stable products]
retrieval_terms: [leave code alone, stable code, no change, rewrite risk]
activate_for_roles: [refactoring, architecture, review, assessment]
activate_for_tasks: [cleanup, rewrite assessment, old-code review]
activate_for_repository_signals: [old or ugly low-churn code]
activate_for_languages: [all]
activate_for_risk_classes: [medium, high]
exclude_when: [confirmed urgent external obligation]
prerequisites: [runtime, roadmap, support evidence]
retrieval_priority: core
retrieval_budget_hint: 300-500 tokens
related_concepts: [change.refactoring-pressure, evidence.code-age]
```

### Legacy and characterization records

```yaml
id: legacy.cover-and-modify
title: Cover-and-modify change algorithm
category: legacy
claim: Poorly characterized code should be changed through a minimum route from change point to effect/test point, dependency seam, characterization, semantic edit, and optional refactoring.
decision_rule: Identify change and test points, break only dependencies blocking sensing or separation, characterize relevant behavior, implement the authorized delta, then refactor only on green.
why_it_matters: It resolves the need-tests-before-change versus need-change-before-tests dilemma without redesigning the system first.
applicable_when: [valuable weakly-tested existing code, difficult construction or execution]
not_applicable_when: [fast existing tests already protect the full change surface]
required_evidence: [change point, effect path, observation point, dependency obstacle, baseline]
insufficient_evidence: [global coverage percentage, whole-system understanding, mockability alone]
required_inputs: [authorized delta, dependency and effect sketch]
expected_outputs: [minimum safe-change route, tests, uncertainty ledger]
preservation_boundaries: All behavior outside the accepted semantic delta.
safe_actions: [one seam, targeted characterization, semantic slice, optional later refactor]
unsafe_actions: [break every dependency, redesign surrounding architecture, edit and pray]
common_failure_modes: [test point too high, seam changes production binding, missed side effects]
counterexamples: [A pure fully tested function can be modified directly.]
interactions: [testing.effect-surface, legacy.controllable-seam, testing.characterization]
conflicts: [conflict.change.tests-before-enabling-edit]
source_support:
  - "`SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm`"
  - "`SRC-REF: chapters/005-chapter-1-refactoring-a-first-example.md :: ## The First Step in Refactoring`"
confidence: strong
roles: [legacy-agent, repair-agent, coding-agent, refactoring-agent]
languages: [language-independent]
repository_archetypes: [weakly-tested legacy systems]
retrieval_terms: [legacy change algorithm, cover and modify, change point, test point]
activate_for_roles: [legacy, repair, coding, refactoring]
activate_for_tasks: [change poorly characterized code]
activate_for_repository_signals: [few tests, hard constructor, hidden dependency]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [complete reliable local protection already exists]
prerequisites: [authorized semantic goal]
retrieval_priority: core
retrieval_budget_hint: 450-650 tokens
related_concepts: [testing.effect-surface, legacy.controllable-seam, testing.characterization]
```

```yaml
id: testing.characterization
title: Characterize actual relevant behavior
category: legacy
claim: A characterization test records what the system does at a relevant observation surface; it does not declare that behavior correct.
decision_rule: Invoke a relevant path, assert and observe, rule out harness error, encode repeatable actual behavior and change-sensitive boundaries, and stop when the intended change can be sensed.
why_it_matters: Undocumented deployed behavior may be relied upon, while desired-behavior assumptions can silently widen a change.
applicable_when: [unknown or undocumented behavior, legacy refactoring, suspected regressions]
not_applicable_when: [irrelevant dead paths, formally specified behavior with a stronger oracle except as comparison]
required_evidence: [representative setup, actual output or effect, repeatability, path relevance]
insufficient_evidence: [what code should do, snapshot approval without inspection, coverage alone]
required_inputs: [change and effect surface, observation harness]
expected_outputs: [targeted baseline tests, suspicious-behavior and uncertainty ledger]
preservation_boundaries: Observed relevant behavior is provisionally preserved unless repair authority changes it.
safe_actions: [name an odd observation explicitly, normalize nondeterministic noise, escalate discrepancy]
unsafe_actions: [silently correct behavior, treat observation as moral correctness, capture unstable environment wholesale]
common_failure_modes: [golden-master noise, nondeterminism, ossified irrelevant behavior, harness bug]
counterexamples: [A protocol specification can supply the desired oracle while characterization shows the current deviation.]
interactions: [universal.behavior-preservation, testing.effect-surface, change.stop-backtrack-escalate]
conflicts: [conflict.change.refactoring-versus-repair, conflict.testing.broad-versus-narrow]
source_support:
  - "`SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests`"
  - "`SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ### When You Find Bugs`"
confidence: strong
roles: [legacy-agent, repair-agent, refactoring-agent, review-agent]
languages: [language-independent]
repository_archetypes: [weakly-tested, undocumented, deployed systems]
retrieval_terms: [characterization test, golden master, actual behavior, suspected bug]
activate_for_roles: [legacy, repair, refactoring]
activate_for_tasks: [discover baseline, protect refactor]
activate_for_repository_signals: [unknown behavior, no tests, odd deployed result]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [irrelevant generated output without normalization]
prerequisites: [repeatable observation surface]
retrieval_priority: core
retrieval_budget_hint: 400-600 tokens
related_concepts: [testing.effect-surface, change.stop-backtrack-escalate]
```

```yaml
id: legacy.controllable-seam
title: Dependency seam with explicit enabling point
category: legacy
claim: A test seam is operational only when alternate behavior can be selected explicitly at a known enabling point without changing production semantics.
decision_rule: Name the behavior to substitute, locate enabling points, choose the least invasive mechanism, prove production selection is unchanged, and govern lifecycle and concurrency.
why_it_matters: An interface or hook without controllable selection does not enable sensing or separation and may only add indirection.
applicable_when: [dependency blocks execution or observation, nondeterministic or external collaborator]
not_applicable_when: [cheap deterministic value dependency, existing sufficient injection]
required_evidence: [blocking dependency, substitute behavior, enabling point, production/test selection]
insufficient_evidence: [interface existence, mocking framework, generic decoupling goal]
required_inputs: [dependency path, language/build/runtime seam options]
expected_outputs: [seam mechanism, enabling point, production default, tests, disposition]
preservation_boundaries: Production binding, lifetime, concurrency, and public API remain unchanged unless authorized.
safe_actions: [constructor/function parameter, controlled object seam, explicit existing default]
unsafe_actions: [ambient global switch, hidden test mode, public exposure solely for tests]
common_failure_modes: [parallel-test leakage, permanent indirection, test-only production branch]
counterexamples: [An already injected owned protocol needs no new seam.]
interactions: [legacy.cover-and-modify, legacy.provisional-dependency-break, testing.test-double-scope]
conflicts: [conflict.legacy.temporary-seam-versus-final-design]
source_support:
  - "`SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`"
  - "`SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point`"
confidence: strong
roles: [legacy-agent, repair-agent, refactoring-agent, architecture-agent]
languages: [language-independent principle, language-specific mechanics]
repository_archetypes: [weakly-tested systems, external-dependency code]
retrieval_terms: [seam, enabling point, dependency breaking, test hook]
activate_for_roles: [legacy, repair, refactoring]
activate_for_tasks: [get code under test, substitute collaborator]
activate_for_repository_signals: [global, static call, nondeterminism, hard constructor]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [no blocked sensing or separation need]
prerequisites: [identified observation goal]
retrieval_priority: high
retrieval_budget_hint: 400-600 tokens
related_concepts: [legacy.provisional-dependency-break, testing.test-double-scope]
```

```yaml
id: testing.test-double-scope
title: Scope the evidence supplied by test doubles
category: review
claim: A fake, stub, or mock supplies localized sensing or separation evidence and does not establish real protocol, timing, persistence, or deployment integration.
decision_rule: Use the simplest substitute that exposes the behavior; add contract or integration evidence when correctness depends on the real boundary; assert interactions only when interactions are contractual.
why_it_matters: A passing substitute-based test can encode a false model or overspecify implementation details.
applicable_when: [mock, fake, stub, external dependency, nondeterministic collaborator]
not_applicable_when: [cheap deterministic value object]
required_evidence: [observation need, collaborator contract, substitute fidelity, integration layer]
insufficient_evidence: [passing mocked test, verified call count, type compatibility]
required_inputs: [boundary contract, desired observation]
expected_outputs: [real or double choice, scope statement, missing integration evidence]
preservation_boundaries: The substitute must not redefine the production contract.
safe_actions: [small owned in-memory fake, boundary contract test]
unsafe_actions: [reimplement vendor behavior and infer integration correctness, mock internals broadly]
common_failure_modes: [brittle interaction tests, divergent fake, false integration confidence]
counterexamples: [Exactly-once enqueue interaction may itself be the required behavior.]
interactions: [legacy.controllable-seam, testing.effect-surface]
conflicts: []
source_support:
  - "`SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: #### Fake Objects Support Real Tests`"
  - "`SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: ## Mock Objects`"
confidence: strong
roles: [coding-agent, legacy-agent, repair-agent, review-agent]
languages: [language-independent]
repository_archetypes: [services, external dependency systems]
retrieval_terms: [mock, fake, test double, integration proof]
activate_for_roles: [coding, legacy, repair, review]
activate_for_tasks: [design or review isolated tests]
activate_for_repository_signals: [heavy mocking, external collaborator]
activate_for_languages: [all]
activate_for_risk_classes: [normal, high for external side effects]
exclude_when: [no substitution]
prerequisites: [collaborator contract]
retrieval_priority: high
retrieval_budget_hint: 300-500 tokens
related_concepts: [legacy.controllable-seam, testing.effect-surface]
```

```yaml
id: legacy.provisional-dependency-break
title: Minimum provisional dependency break
category: legacy
claim: Break only the dependency that prevents required feedback, and make any resulting design scar explicit and revisitable.
decision_rule: Rank seam options by production impact, scope, reversibility, and test leverage; choose the smallest, verify production behavior, and record retain/remove criteria.
why_it_matters: Demanding final architecture before tests recreates the legacy dilemma, while untracked hooks fossilize.
applicable_when: [one dependency blocks harness or observation]
not_applicable_when: [durable boundary is independently earned or no protection benefit exists]
required_evidence: [blocking dependency, alternatives, production invariant, lifecycle criteria]
insufficient_evidence: [testability as an abstract virtue]
required_inputs: [obstacle, seam options, protection goal]
expected_outputs: [bounded enabling change, tests, debt disposition]
preservation_boundaries: Production behavior and selection remain stable.
safe_actions: [parameterize with current production value, extract-and-override in harness]
unsafe_actions: [redesign all dependencies, leave hidden global hook]
common_failure_modes: [temporary scar becomes permanent, API pollution, global leakage]
counterexamples: [Multiple production implementations can independently earn a durable interface.]
interactions: [legacy.controllable-seam, legacy.unprotected-enabling-edit, legacy.sprout-wrap]
conflicts: [conflict.legacy.temporary-seam-versus-final-design]
source_support:
  - "`SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Break Dependencies`"
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Signal Incompleteness with Names`"
confidence: strong-contextual
roles: [legacy-agent, repair-agent, refactoring-agent]
languages: [language-independent principle, language-specific mechanics]
repository_archetypes: [weakly-tested legacy systems]
retrieval_terms: [dependency break, temporary seam, design scar, testability]
activate_for_roles: [legacy, repair, refactoring]
activate_for_tasks: [enable characterization]
activate_for_repository_signals: [hard dependency, no test harness]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [no actual feedback blockage]
prerequisites: [legacy.controllable-seam analysis]
retrieval_priority: high
retrieval_budget_hint: 350-550 tokens
related_concepts: [legacy.controllable-seam, legacy.unprotected-enabling-edit]
```

```yaml
id: testing.effect-surface
title: Select protection from effect propagation
category: legacy
claim: Required tests follow all observable effects reachable from a change point, not class boundaries or coverage targets alone.
decision_rule: Trace returns, mutations, globals/statics, I/O, callbacks/events, exceptions, and deferred effects to stable observations; choose the nearest reliable points plus critical broad contracts.
why_it_matters: It bounds test preparation and reveals hidden coupling without demanding global coverage.
applicable_when: [planning tests for change, legacy characterization, repair blast radius]
not_applicable_when: [as a replacement for cross-cutting security or concurrency analysis]
required_evidence: [call and effect sketch, side effects, exception paths, observation points]
insufficient_evidence: [testing every public method, line coverage, class adjacency]
required_inputs: [change point, execution and state graph]
expected_outputs: [test-point list, uncovered high-risk effects, confidence]
preservation_boundaries: Every preserved material effect needs a check or explicit uncertainty.
safe_actions: [test return and mutation, include async completion, use pinch point where justified]
unsafe_actions: [assume void means no effect, expose internals without trade-off review]
common_failure_modes: [missed deferred effect, enormous high-level test, internal overspecification]
counterexamples: [A pure function's effect surface may be only its return value.]
interactions: [testing.characterization, testing.pinch-point, legacy.cover-and-modify]
conflicts: [conflict.testing.broad-versus-narrow]
source_support:
  - "`SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation`"
  - "`SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ### Effects and Encapsulation`"
confidence: strong
roles: [legacy-agent, repair-agent, coding-agent, review-agent]
languages: [language-independent]
repository_archetypes: [all]
retrieval_terms: [effect analysis, what to test, side effect, blast radius]
activate_for_roles: [legacy, repair, coding, review]
activate_for_tasks: [determine tests, establish preservation boundary]
activate_for_repository_signals: [hidden mutation, globals, callbacks, I/O]
activate_for_languages: [all]
activate_for_risk_classes: [all, especially high]
exclude_when: [none]
prerequisites: [identified change point]
retrieval_priority: core
retrieval_budget_hint: 350-550 tokens
related_concepts: [testing.characterization, testing.pinch-point]
```

```yaml
id: testing.pinch-point
title: Protect a change cluster at a stable convergence point
category: legacy
claim: One stable observation can intercept effects from several changed paths, trading localization for reduced preparation.
decision_rule: Choose the closest stable convergence point covering the relevant effect set; supplement critical leaves and narrow or retire the broad test as seams improve.
why_it_matters: It can make a bounded change feasible without breaking every dependency in a tangled area.
applicable_when: [many connected classes or effects, no economical local harness]
not_applicable_when: [point is nondeterministic, destructive, too slow, or misses the changed path]
required_evidence: [effect convergence, stable harness, scope, cost, critical gaps]
insufficient_evidence: [architectural height, aggregate coverage]
required_inputs: [effect graph, candidate interception points]
expected_outputs: [selected point, covered paths, supplemental tests, retention rule]
preservation_boundaries: Broad coverage protects only observed effects; unrelated behavior is not declared correct.
safe_actions: [temporary service-boundary characterization, targeted leaf tests]
unsafe_actions: [one happy-path E2E test claimed comprehensive]
common_failure_modes: [flaky slow suite, incidental convergence, weak failure localization]
counterexamples: [A stable public protocol may be the enduring correct contract surface.]
interactions: [testing.effect-surface, testing.provisional-safety-net]
conflicts: [conflict.testing.broad-versus-narrow]
source_support:
  - "`SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: #### Pinch Point`"
  - "`SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ## Traps Pinch Point Traps`"
confidence: strong-contextual
roles: [legacy-agent, repair-agent, refactoring-agent]
languages: [language-independent]
repository_archetypes: [tangled legacy subsystems]
retrieval_terms: [pinch point, interception point, test covering]
activate_for_roles: [legacy, repair, refactoring]
activate_for_tasks: [choose broad characterization surface]
activate_for_repository_signals: [many dependencies, effect convergence]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [stable narrow test point exists cheaply]
prerequisites: [testing.effect-surface]
retrieval_priority: specialist
retrieval_budget_hint: 350-550 tokens
related_concepts: [testing.effect-surface, testing.provisional-safety-net]
```

```yaml
id: legacy.current-work-responsibility-discovery
title: Discover responsibility through current work
category: legacy
claim: The behavior being changed supplies the most reliable initial evidence for one responsibility inside an unclear large unit.
decision_rule: Mark methods, data, and effects involved in current work; name their shared purpose; extract only with a cohesive seam and protection; defer unrelated groups.
why_it_matters: Live change supplies semantic and temporal evidence without requiring an ideal full decomposition.
applicable_when: [large unclear class/module, feature or repair in legacy code]
not_applicable_when: [forcing every task into a new type, accepted domain boundary already resolves placement]
required_evidence: [current path, data relationships, change reason, nameable policy, test seam]
insufficient_evidence: [size, position grouping, imagined class diagram]
required_inputs: [current task slice, effect and data map]
expected_outputs: [local responsibility hypothesis, retain or extract choice]
preservation_boundaries: Initial extraction remains behind existing interfaces where possible.
safe_actions: [extract in current owner first, revisit after more changes]
unsafe_actions: [design complete hierarchy from static read, move ownership before understanding]
common_failure_modes: [task-shaped fragmentation, duplicated invariants, provisional boundary mistaken final]
counterexamples: [Strong accepted domain architecture may already identify the owner.]
interactions: [change-locality-cohesion, learning.scratch-refactoring, change.verified-small-step-loop]
conflicts: [conflict.change.small-units-versus-deep-module]
source_support:
  - "`SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work`"
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities`"
confidence: strong-contextual
roles: [legacy-agent, refactoring-agent, coding-agent]
languages: [language-independent]
repository_archetypes: [large legacy units]
retrieval_terms: [current work, responsibility discovery, large class]
activate_for_roles: [legacy, refactoring, coding]
activate_for_tasks: [change large unclear unit]
activate_for_repository_signals: [large class, mixed methods, unclear owner]
activate_for_languages: [all]
activate_for_risk_classes: [medium, high]
exclude_when: [no current or imminent work]
prerequisites: [current change and effect map]
retrieval_priority: high
retrieval_budget_hint: 350-550 tokens
related_concepts: [change-locality-cohesion, learning.scratch-refactoring]
```

```yaml
id: learning.scratch-refactoring
title: Disposable refactoring for understanding
category: legacy
claim: Aggressive reversible structural edits can reveal behavior and responsibilities, but insight—not the scratch diff—is the default deliverable.
decision_rule: Work in an isolated reversible copy, rename/extract/delete to learn, capture findings, discard, and recreate only the smallest justified production campaign from a clean baseline.
why_it_matters: It permits exploration without laundering unverified edits into production.
applicable_when: [poorly understood code, monster method, suspected dead code]
not_applicable_when: [static reading and existing tests already answer the question]
required_evidence: [explicit scratch status, clean baseline, no external side effects, recorded findings]
insufficient_evidence: [scratch code compiles, scratch structure looks better]
required_inputs: [understanding question, isolated workspace]
expected_outputs: [effect/responsibility/dead-code hypotheses, no production diff by default]
preservation_boundaries: Scratch mutations never alter shared or external state and are not merged without a fresh protected campaign.
safe_actions: [throwaway extraction, exploratory rename, discard]
unsafe_actions: [merge exploration, delete from production based on scratch only, destroy user work]
common_failure_modes: [scratch becomes production, findings not recorded, false dead-code conclusion]
counterexamples: [A protected extraction discovered in scratch can be recreated as the first production slice.]
interactions: [legacy.current-work-responsibility-discovery, change.stop-backtrack-escalate]
conflicts: []
source_support:
  - "`SRC-WELC: chapters/024-chapter-16-i-don-t-understand-the-code-well-enough-to-change-it.md :: ## Scratch Refactoring`"
confidence: strong
roles: [legacy-agent, repository-assessment-agent, refactoring-agent]
languages: [language-independent]
repository_archetypes: [poorly understood legacy code]
retrieval_terms: [scratch refactoring, throwaway extraction, code understanding]
activate_for_roles: [legacy, assessment, refactoring]
activate_for_tasks: [understand code before change]
activate_for_repository_signals: [unknown behavior, monster method]
activate_for_languages: [all]
activate_for_risk_classes: [medium, high]
exclude_when: [cannot isolate external side effects]
prerequisites: [clean baseline and disposable workspace]
retrieval_priority: high
retrieval_budget_hint: 300-450 tokens
related_concepts: [legacy.current-work-responsibility-discovery, change.stop-backtrack-escalate]
```

```yaml
id: legacy.sprout-wrap
title: Sprout or wrap behavior under deadline pressure
category: legacy
claim: When required behavior cannot safely enter an untestable body in time, tested logic may be placed beside or around it through a narrow integration point.
decision_rule: Sprout separable new computation; wrap required before/after behavior; test new logic, characterize integration where feasible, and record the design and integration gap.
why_it_matters: It confines new uncertainty but may create a staging scar and leave old/new integration weakly protected.
applicable_when: [urgent authorized feature or repair in untestable code]
not_applicable_when: [small seam can cheaply bring original path under test]
required_evidence: [deadline and change need, protection obstacle, narrow integration, new-logic tests]
insufficient_evidence: [desire to avoid understanding old code]
required_inputs: [required behavior, old call boundary]
expected_outputs: [sprout or wrap slice, integration-risk statement, follow-up disposition]
preservation_boundaries: Existing old behavior remains unchanged except the authorized added wrapper/sprout effect.
safe_actions: [tested helper called once, explicit decorator/wrapper with contract]
unsafe_actions: [parallel subsystem, duplicated long-term policy, untested integration claimed safe]
common_failure_modes: [architectural scar, stale duplication, context split]
counterexamples: [Ordinary TDD inside already testable code is preferable.]
interactions: [legacy.cover-and-modify, legacy.provisional-dependency-break]
conflicts: [conflict.legacy.temporary-seam-versus-final-design]
source_support:
  - "`SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Sprout Method`"
  - "`SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Wrap Method`"
confidence: contextual
roles: [coding-agent, legacy-agent, repair-agent]
languages: [language-independent]
repository_archetypes: [deadline-constrained legacy systems]
retrieval_terms: [sprout method, wrap method, urgent legacy change]
activate_for_roles: [coding, legacy, repair]
activate_for_tasks: [urgent feature in untestable code]
activate_for_repository_signals: [deadline, no harness, narrow call point]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [existing local protection]
prerequisites: [explicit integration-risk acceptance]
retrieval_priority: specialist
retrieval_budget_hint: 350-550 tokens
related_concepts: [legacy.provisional-dependency-break, testing.provisional-safety-net]
```

```yaml
id: testing.provisional-safety-net
title: Provisional broad characterization safety net
category: legacy
claim: A broad black-box or E2E suite may temporarily protect initial restructuring when local tests are impossible, with explicit brittleness and retirement rules.
decision_rule: Cover critical user scenarios and complex paths in an isolated stable environment, use them to enable the first seam, add narrower tests, then retain only enduring contract value.
why_it_matters: Broad tests may be the only initial route but are slow, brittle, and weak at localization.
applicable_when: [central untestable hotspot, stable black-box boundary]
not_applicable_when: [destructive live environment, reliable narrow seam already available]
required_evidence: [critical scenarios, repeatability, environment controls, coverage gaps, retirement criteria]
insufficient_evidence: [one recorded happy path, screenshots, aggregate coverage]
required_inputs: [user-visible scenarios, change surface]
expected_outputs: [temporary safety net, scope statement, narrowing plan]
preservation_boundaries: Only recorded stable external behavior is protected.
safe_actions: [isolated API characterization, DOM/component identity over pixels]
unsafe_actions: [production live test, flaky GUI playback claimed comprehensive]
common_failure_modes: [brittleness blocks unrelated change, leaked state, false confidence]
counterexamples: [Stable protocol E2E tests may retain enduring value after local tests exist.]
interactions: [testing.pinch-point, change.splinter-campaign]
conflicts: [conflict.testing.broad-versus-narrow]
source_support:
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net`"
  - "`SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ### Test Coverings`"
confidence: contextual
roles: [legacy-agent, refactoring-agent, repair-agent]
languages: [language-independent]
repository_archetypes: [untestable central systems]
retrieval_terms: [temporary E2E, safety net, black-box characterization]
activate_for_roles: [legacy, refactoring, repair]
activate_for_tasks: [protect first legacy restructure]
activate_for_repository_signals: [no local tests, stable external boundary]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [unisolated destructive environment]
prerequisites: [critical scenario inventory]
retrieval_priority: specialist
retrieval_budget_hint: 400-600 tokens
related_concepts: [testing.pinch-point, change.splinter-campaign]
```

```yaml
id: legacy.unprotected-enabling-edit
title: Last-resort unprotected mechanical enabling edit
category: legacy
claim: A first testless production edit is permissible only when it is the smallest reversible bridge required to make protection possible and no safer path exists.
decision_rule: Exhaust pre-change tests/seams; if blocked, make one signature-preserving mechanical goal, use compiler/tool/reference checks and peer review, stop on ambiguity, then add characterization before semantic work.
why_it_matters: The legacy dilemma sometimes requires an edit before tests, but normalizing this exception invites unbounded edit-and-pray.
applicable_when: [first seam impossible without production edit, statically checkable mechanics]
not_applicable_when: [semantic change, broad dynamic/reference surface, irreversible external state]
required_evidence: [no practical pre-change harness, singular goal, reference map, tool coverage, rollback]
insufficient_evidence: [deadline, confidence, code simplicity]
required_inputs: [blocked harness, candidate bridge]
expected_outputs: [minimal enabling edit, heightened review, immediate protection]
preservation_boundaries: No semantic or public contract change; signatures preserved where possible.
safe_actions: [compiler-checked extraction, pair review, immediate characterization]
unsafe_actions: [rename across reflection, manual logic alteration, design cleanup]
common_failure_modes: [compiler blind spots, bridge expands, reordered side effects]
counterexamples: [A proven semantics-aware automated refactor falls primarily under change.transformation-tool-trust.]
interactions: [legacy.provisional-dependency-break, change.transformation-tool-trust, change.stop-backtrack-escalate]
conflicts: [conflict.change.tests-before-enabling-edit]
source_support:
  - "`SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Hyperaware Editing`"
  - "`SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Lean on the Compiler`"
confidence: contextual-contested
roles: [legacy-agent, refactoring-agent, repair-agent, review-agent]
languages: [strongest in statically compiled code]
repository_archetypes: [weakly-tested legacy systems]
retrieval_terms: [hyperaware editing, testless refactor, first seam, compiler]
activate_for_roles: [legacy, refactoring, repair, review]
activate_for_tasks: [create first test seam]
activate_for_repository_signals: [no harness possible, compiler-visible references]
activate_for_languages: [compiled languages primarily]
activate_for_risk_classes: [high, critical scrutiny]
exclude_when: [semantic edit, dynamic blind spots, irreversible state]
prerequisites: [documented exhaustion of safer options]
retrieval_priority: specialist
retrieval_budget_hint: 400-600 tokens
related_concepts: [legacy.provisional-dependency-break, change.transformation-tool-trust]
```

### Historical and sociotechnical evidence records

```yaml
id: metric-as-signal
title: Metrics trigger investigation, not intervention
category: review
claim: Behavioral and structural metrics allocate expert attention and never prove defect, bad design, causation, or authority.
decision_rule: Form a candidate from a metric, then validate it with current source, tests, runtime/incidents, roadmap, domain evidence, and repository contracts before recommendation.
why_it_matters: Temporal evidence exposes invisible forces but lacks semantic and causal context.
applicable_when: [hotspot, churn, co-change, age, complexity, ownership analysis]
not_applicable_when: [history is absent or demonstrably irrelevant to the claim]
required_evidence: [fit metric dataset, at least one independent current evidence class]
insufficient_evidence: [rank, count, color, threshold, score alone]
required_inputs: [analysis claim, repository data, current context]
expected_outputs: [hypothesis and investigation queue, not defect ledger]
preservation_boundaries: Observation does not authorize code, architecture, or team changes.
safe_actions: [inspect candidates, communicate uncertainty, record false positives]
unsafe_actions: [automatic refactoring tickets, blocker from threshold, people judgment]
common_failure_modes: [metric reification, stale interval, generated artifacts, causal overclaim]
counterexamples: [A direct reproduced defect can justify repair independently of metrics.]
interactions: [evidence.behavioral-data-fitness, evidence.hotspot, change.refactoring-pressure]
conflicts: [conflict.evidence.static-versus-behavioral]
source_support:
  - "`SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data`"
  - "`SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Your Code Is Still a Crime Scene`"
confidence: strong
roles: [repository-assessment-agent, review-agent, refactoring-agent, architecture-agent]
languages: [language-independent]
repository_archetypes: [meaningfully version-controlled systems]
retrieval_terms: [metric signal, not verdict, behavioral analysis, evidence triangulation]
activate_for_roles: [assessment, review, refactoring, architecture]
activate_for_tasks: [repository analysis, debt prioritization]
activate_for_repository_signals: [metric output, heatmap, score]
activate_for_languages: [all]
activate_for_risk_classes: [all]
exclude_when: [purely authoritative direct contract violation does not need metric gate]
prerequisites: [evidence.behavioral-data-fitness]
retrieval_priority: core
retrieval_budget_hint: 300-450 tokens
related_concepts: [evidence.behavioral-data-fitness, change.refactoring-pressure]
```

```yaml
id: evidence.hotspot
title: Active-cost hotspot signal
category: review
claim: Recent change activity combined with rough complexity or size prioritizes code where poor maintainability would impose recurring cost.
decision_rule: Clean and scope history, combine frequency with a consistent complexity proxy, inspect trends, drill to function level, and validate current responsibilities and roadmap.
why_it_matters: Frequently changed simple code and large stable code have different maintenance economics.
applicable_when: [large mature active repository, limited investigation capacity]
not_applicable_when: [history is corrupted, product phase discontinuity dominates]
required_evidence: [meaningful interval, clean identity, frequency, complexity, current source inspection]
insufficient_evidence: [LOC alone, change count alone, lifetime rank]
required_inputs: [scoped history, source metrics, roadmap and incidents]
expected_outputs: [healthy-active, investigate, refactor-candidate, or false-positive classification]
preservation_boundaries: A hotspot is not a defect or action authorization.
safe_actions: [drill into active functions, compare trend, validate test/infrastructure hotspots]
unsafe_actions: [split hottest file automatically, blame authors]
common_failure_modes: [formatting migration, generated file, historic completed refactor, healthy test churn]
counterexamples: [Stable safety-critical code may deserve review despite low hotspot rank.]
interactions: [metric-as-signal, evidence.complexity-trend, change.refactoring-pressure]
conflicts: [conflict.evidence.static-versus-behavioral]
source_support:
  - "`SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots`"
  - "`SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Use X-Rays to Get Deep Insights into Code`"
confidence: strong-contextual
roles: [repository-assessment-agent, refactoring-agent, review-agent]
languages: [language-neutral with metric caveats]
repository_archetypes: [active mature repositories]
retrieval_terms: [hotspot, churn, interest rate, active complex code]
activate_for_roles: [assessment, refactoring, review]
activate_for_tasks: [prioritize investigation or campaign]
activate_for_repository_signals: [many files, technical debt inventory]
activate_for_languages: [all]
activate_for_risk_classes: [normal, high]
exclude_when: [generated or unfit history]
prerequisites: [evidence.behavioral-data-fitness]
retrieval_priority: high
retrieval_budget_hint: 350-550 tokens
related_concepts: [metric-as-signal, evidence.complexity-trend]
```

```yaml
id: evidence.change-coupling
title: Repeated co-change relationship signal
category: review
claim: Repeated co-change nominates a technical, semantic, test, process, or organizational relationship that requires explanation; expected coupling can be healthy.
decision_rule: Normalize logical changes, require meaningful support and degree, inspect surprising pairs or clusters, review actual diffs and domain context, and classify the relationship.
why_it_matters: Static dependencies miss cross-language, configuration, data, and workflow coupling.
applicable_when: [companion-change planning, duplication, boundary assessment, omission warning]
not_applicable_when: [single commit or ungroupable split work]
required_evidence: [support count, coupling degree, interval, task/diff/source/domain inspection]
insufficient_evidence: [one commit, percentage without support, graph adjacency]
required_inputs: [fit logical change history, entity identity]
expected_outputs: [expected, accidental, missing abstraction, omission risk, process artifact, or unresolved classification]
preservation_boundaries: Correlation does not establish direction or authorize merging/splitting.
safe_actions: [change-planning reminder, deeper source inspection]
unsafe_actions: [merge modules from correlation, force all historical companions]
common_failure_modes: [broad commits, squash, code generation, staged commits, release trains]
counterexamples: [Test and production code changing together may be desirable.]
interactions: [evidence.logical-change-set, design.knowledge-duplication, domain.behavioral-boundary-candidate]
conflicts: [conflict.evidence.cochange-versus-domain]
source_support:
  - "`SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ### What Is Change Coupling?`"
  - "`SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Detect Cochanging Files`"
confidence: strong-contextual
roles: [repository-assessment-agent, architecture-agent, refactoring-agent, review-agent]
languages: [language-independent]
repository_archetypes: [mono-repo, multi-repo with logical changes]
retrieval_terms: [change coupling, temporal coupling, co-change, surprise]
activate_for_roles: [assessment, architecture, refactoring, review]
activate_for_tasks: [companion change, clone analysis, boundary analysis]
activate_for_repository_signals: [repeated joint edits, omitted companion]
activate_for_languages: [all]
activate_for_risk_classes: [normal, high for architecture]
exclude_when: [insufficient or unfit logical changes]
prerequisites: [evidence.behavioral-data-fitness, evidence.logical-change-set where needed]
retrieval_priority: high
retrieval_budget_hint: 400-600 tokens
related_concepts: [evidence.logical-change-set, metric-as-signal]
```

```yaml
id: evidence.complexity-trend
title: Repository-relative structural trajectory
category: review
claim: A consistent relative trajectory or unusual delta is more actionable than an absolute universal complexity threshold.
decision_rule: Use a stable proxy and sampling method, inspect trend over relevant revisions, correlate increases with change purpose and function hotspots, and emit investigation prompts only.
why_it_matters: Language, formatting, generated code, and local style bias absolute values.
applicable_when: [active large code, rising hotspot, normalization-of-deviance check]
not_applicable_when: [metric cannot be compared consistently across revisions]
required_evidence: [consistent cleaned samples, relevant window, current source inspection]
insufficient_evidence: [one current number, arbitrary ten-percent rule]
required_inputs: [historical revisions, metric definition]
expected_outputs: [stable, rising, falling, step-change, or noisy hypothesis]
preservation_boundaries: A warning does not block or demand refactoring.
safe_actions: [review steep growth in active already-large code]
unsafe_actions: [universal CI ceiling, infer design improvement from a fall alone]
common_failure_modes: [formatting effects, necessary behavior, complexity moved elsewhere]
counterexamples: [A well-tested essential branching algorithm may be high but stable.]
interactions: [evidence.hotspot, review.behavioral-early-warning]
conflicts: []
source_support:
  - "`SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Evaluate Hotspots with Complexity Trends`"
  - "`SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Know the Biases in Complexity Trends`"
confidence: contextual-strong
roles: [repository-assessment-agent, refactoring-agent, review-agent]
languages: [language-neutral proxy with language bias]
repository_archetypes: [active repositories with comparable history]
retrieval_terms: [complexity trend, rising complexity, relative threshold]
activate_for_roles: [assessment, refactoring, review]
activate_for_tasks: [trend analysis, early warning]
activate_for_repository_signals: [complexity growth, hotspot]
activate_for_languages: [all]
activate_for_risk_classes: [normal]
exclude_when: [incomparable metric samples]
prerequisites: [evidence.behavioral-data-fitness]
retrieval_priority: normal
retrieval_budget_hint: 300-500 tokens
related_concepts: [evidence.hotspot, review.behavioral-early-warning]
```

```yaml
id: evidence.code-age
title: Code-age stability clue
category: review
claim: Time since modification can suggest stable or active regions but cannot establish quality, safety, use, cohesion, or deadness.
decision_rule: Choose a meaningful reference date, exclude generated content, interpret age within domain boundaries, and combine it with product activity, runtime use, incidents, roadmap, support, tests, and ownership.
why_it_matters: Stable modules reduce cognitive load, while paused, abandoned, dead, or feared code can look equally old.
applicable_when: [mature repository, stability or dead-code assessment]
not_applicable_when: [inactive repository without an appropriate reference event]
required_evidence: [reference date, product activity, runtime/dependency use, domain and support context]
insufficient_evidence: [age histogram, no recent commits]
required_inputs: [age map, current product/use context]
expected_outputs: [stability hypothesis and leave, isolate, characterize, delete-investigate, or migrate option]
preservation_boundaries: Age never authorizes deletion or extraction.
safe_actions: [downrank inactive low-risk code, verify deadness before deletion]
unsafe_actions: [declare old code good/dead/reusable]
common_failure_modes: [paused repo, latent vulnerability, dead package mistaken library]
counterexamples: [Old cryptographic code may require standards-driven migration.]
interactions: [change.leave-stable-code-alone, metric-as-signal]
conflicts: [conflict.change.stable-code-versus-proactive-work]
source_support:
  - "`SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Stabilize Code by Age`"
  - "`SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code`"
confidence: contextual
roles: [repository-assessment-agent, architecture-agent, refactoring-agent]
languages: [language-independent]
repository_archetypes: [mature stable products]
retrieval_terms: [code age, stable code, dead code, old code]
activate_for_roles: [assessment, architecture, refactoring]
activate_for_tasks: [stability, deletion, package reorganization]
activate_for_repository_signals: [old unchanged code]
activate_for_languages: [all]
activate_for_risk_classes: [normal, high for deletion]
exclude_when: [no meaningful activity reference]
prerequisites: [runtime and product evidence]
retrieval_priority: normal
retrieval_budget_hint: 350-550 tokens
related_concepts: [change.leave-stable-code-alone, metric-as-signal]
```

```yaml
id: evidence.behavioral-data-fitness
title: Version-history evidence fitness gate
category: agent-conduct
claim: Behavioral inference is admissible only after checking whether repository practice preserves the entity, time, task, and author relationships the analysis assumes.
decision_rule: Audit moves/imports/squashes/merges, generation/vendor/migrations, aliases/bots/pairing, branch scope, organizational dates, and logical-task linkage; mark each metric usable, corrected, limited, or invalid.
why_it_matters: Plausible charts can encode false provenance and socially harmful attribution.
applicable_when: [any history, hotspot, co-change, ownership, or age analysis]
not_applicable_when: [snapshot-only review making no historical claim]
required_evidence: [sample raw commits, repository policy and event history, exclusions]
insufficient_evidence: [tool success, commit volume, plausible output]
required_inputs: [raw history, analysis claim, repository practices]
expected_outputs: [fitness ledger by metric, corrections, exclusions, confidence]
preservation_boundaries: Never silently invent uncertain identity or attribution.
safe_actions: [exclude generated/noncode, consolidate verified aliases, downgrade social metrics]
unsafe_actions: [present biased author data as fact, repair uncertain history silently]
common_failure_modes: [copy-paste repository credit, squash erasure, pairing attributed to one, formatting noise]
counterexamples: [Static source review does not require history fitness if it makes no temporal claim.]
interactions: [metric-as-signal, evidence.logical-change-set, team-topology-force]
conflicts: []
source_support:
  - "`SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis`"
  - "`SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: #### Watch Out for Authors with Multiple Aliases`"
confidence: universal-strong
roles: [repository-assessment-agent, architecture-agent, review-agent]
languages: [language-independent]
repository_archetypes: [version-controlled systems]
retrieval_terms: [history bias, git data quality, mailmap, squash, generated files]
activate_for_roles: [assessment, architecture, review]
activate_for_tasks: [any behavioral analysis]
activate_for_repository_signals: [VCS mining, social metrics]
activate_for_languages: [all]
activate_for_risk_classes: [all, critical for people-related claims]
exclude_when: [no historical claim]
prerequisites: [raw history access]
retrieval_priority: core
retrieval_budget_hint: 400-600 tokens
related_concepts: [metric-as-signal, agent.behavioral-metrics-not-performance]
```

```yaml
id: team-topology-force
title: Team topology as contextual architecture force
category: architecture
claim: Ownership, communication, knowledge, cadence, and contributor congestion can shape architecture risk, but never dictate a one-team/one-context/one-service mapping alone.
decision_rule: Normalize attribution and interval, correlate active fragmentation with actual coordination, defects, lead time and technical dependencies, then generate technical and organizational options with human context.
why_it_matters: Organizational distance amplifies coupled change, while rigid ownership can create silos and gatekeepers.
applicable_when: [multi-team active code, coordination bottleneck, ownership assessment]
not_applicable_when: [individual performance evaluation, attribution-unfit history]
required_evidence: [fit team data, current organization, actual coordination symptoms, interviews, technical dependency]
insufficient_evidence: [author count, fractal value, minor-contributor label]
required_inputs: [team and technical maps, privacy and authority constraints]
expected_outputs: [coordination hypothesis and options, no personnel judgment]
preservation_boundaries: Operational responsibility may narrow while knowledge boundaries remain broad.
safe_actions: [focus review/support, consider boundary or ownership options, broaden knowledge]
unsafe_actions: [reorganize solely from Git, restrict contributors automatically, blame individuals]
common_failure_modes: [gatekeeper bottleneck, silo, alias/pair bias, fundamental attribution error]
counterexamples: [A short emergency response can legitimately involve many teams in one area.]
interactions: [agent.behavioral-metrics-not-performance, evidence.behavioral-data-fitness, domain.behavioral-boundary-candidate]
conflicts: [conflict.sociotechnical.ownership-versus-broad-knowledge]
source_support:
  - "`SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Measure Coordination Needs`"
  - "`SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Provide Broad Knowledge Boundaries`"
confidence: contextual-contested
roles: [architecture-agent, repository-assessment-agent, review-agent]
languages: [language-independent]
repository_archetypes: [multi-team systems]
retrieval_terms: [Conway, ownership, developer congestion, coordination, knowledge boundary]
activate_for_roles: [architecture, assessment, review]
activate_for_tasks: [team-boundary and coordination assessment]
activate_for_repository_signals: [many teams in active hotspot, cross-team co-change]
activate_for_languages: [all]
activate_for_risk_classes: [high social risk]
exclude_when: [no privacy/human-context authority]
prerequisites: [evidence.behavioral-data-fitness, human context]
retrieval_priority: high
retrieval_budget_hint: 450-650 tokens
related_concepts: [agent.behavioral-metrics-not-performance, domain.behavioral-boundary-candidate]
```

```yaml
id: agent.behavioral-metrics-not-performance
title: Prohibit individual performance scoring from behavioral code data
category: agent-conduct
claim: Commit, LOC, ownership, defect-attribution, hotspot, and knowledge-map data must never be converted into individual productivity or performance judgments.
decision_rule: Restrict these data to communication, risk simulation, knowledge transfer, and system/team investigation under privacy policy; refuse ranking, scoring, or blame.
why_it_matters: Measurement changes behavior, destroys the evidence source, discourages help/deletion/risky work, and cannot see task context.
applicable_when: [any proposal to evaluate contributors from repository data]
not_applicable_when: [concrete code review of a specific contribution, maintainer routing]
required_evidence: [No evidence threshold makes individual performance scoring admissible from these signals.]
insufficient_evidence: [clean history, large sample, normalized score, managerial request]
required_inputs: [proposed use, privacy and authority context]
expected_outputs: [allowed communication/risk use or explicit refusal]
preservation_boundaries: Protect individual privacy, team dynamics, and non-evaluative purpose.
safe_actions: [find likely expert and ask, simulate knowledge-loss risk]
unsafe_actions: [rank employees by commits, LOC, bugs, ownership, hotspot work]
common_failure_modes: [covert scoring under risk, public shame, biased attribution]
counterexamples: [Review routing identifies familiarity and is not a performance evaluation.]
interactions: [team-topology-force, universal.authority-discipline]
conflicts: []
source_support:
  - "`SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## Adaptive Behavior and the Destruction of a Data Source`"
  - "`SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## The Situation Is Invisible in Code`"
confidence: universal
roles: [all agents]
languages: [language-independent]
repository_archetypes: [all organizations]
retrieval_terms: [developer productivity, performance metric, commit count, LOC, blame]
activate_for_roles: [all]
activate_for_tasks: [social or productivity analysis]
activate_for_repository_signals: [author metrics, employee ranking]
activate_for_languages: [all]
activate_for_risk_classes: [critical ethical and social]
exclude_when: [none]
prerequisites: [none]
retrieval_priority: core
retrieval_budget_hint: 200-350 tokens
related_concepts: [team-topology-force, evidence.behavioral-data-fitness]
```

```yaml
id: domain.behavioral-boundary-candidate
title: Co-change-nominated domain boundary candidate
category: domain
claim: Historical clusters can nominate a component or bounded-context candidate, but semantic language, invariants, data/authority ownership, transactions, and experts establish the boundary.
decision_rule: Inspect stable co-change across technical layers, repeated policy and names, consult experts, map ownership and transactions, compare alternative cuts, and prototype before migration.
why_it_matters: History reveals how work traverses current structure but commits can reflect convenience, rollout, or process artifacts.
applicable_when: [layered monolith modularization, cross-layer co-change, context discovery]
not_applicable_when: [directory or graph clustering without domain evidence]
required_evidence: [co-change support, source policy, domain vocabulary, invariants, data and team ownership]
insufficient_evidence: [graph cluster, shared noun, folders, layer crossing alone]
required_inputs: [temporal cluster, current domain model and contracts]
expected_outputs: [boundary candidate, alternatives, costs, confidence]
preservation_boundaries: Candidate status does not grant architecture or data migration authority.
safe_actions: [prototype behind current facade, validate deletion/independence]
unsafe_actions: [declare bounded context from Git, merge semantically distinct features]
common_failure_modes: [shared infrastructure mistaken domain, feature-bundle commits, ignored transactions]
counterexamples: [An accepted ADR and domain model can outweigh a weak recent co-change pattern.]
interactions: [bounded-context, evidence.change-coupling, team-topology-force, change-locality-cohesion]
conflicts: [conflict.evidence.cochange-versus-domain]
source_support:
  - "`SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`"
  - "`SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### The Big Win Is in the Problem Domain`"
confidence: contextual
roles: [architecture-agent, domain-agent, refactoring-agent, repository-assessment-agent]
languages: [language-independent]
repository_archetypes: [layered monolith, distributed system]
retrieval_terms: [bounded context candidate, co-change cluster, domain boundary]
activate_for_roles: [architecture, domain, refactoring, assessment]
activate_for_tasks: [modularization, boundary selection]
activate_for_repository_signals: [cross-layer co-change, shared model bloat]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [no domain expertise or authority]
prerequisites: [evidence.change-coupling, domain and ownership evidence]
retrieval_priority: specialist
retrieval_budget_hint: 450-700 tokens
related_concepts: [bounded-context, change-locality-cohesion]
```

```yaml
id: change.splinter-campaign
title: Facade-preserving hotspot splinter campaign
category: refactoring
claim: In an active congested hotspot, the first campaign may improve safe parallel evolution by extracting one evidenced responsibility while retaining the old API.
decision_rule: Validate hotspot and congestion, establish protection, group behaviors, choose the highest-pressure cohesive group, extract behind delegation, verify, integrate quickly, and remeasure.
why_it_matters: It reduces ripple and merge exposure without pretending the first split is the final architecture.
applicable_when: [large active complex hotspot under parallel development]
not_applicable_when: [size alone, quiet cohesive module, no safety net]
required_evidence: [hotspot and trend, parallel pressure, responsibility map, tests, short integration path]
insufficient_evidence: [LOC, one complaint, final diagram]
required_inputs: [hotspot evidence, behavior groups, protection]
expected_outputs: [one extracted responsibility, old facade, checks, follow-up signals]
preservation_boundaries: Original signatures and behavior remain available during the first campaign.
safe_actions: [one behavior extraction, immediate integration, later remeasurement]
unsafe_actions: [all-at-once split, long branch, early client migration]
common_failure_modes: [permanent middle man, low-cohesion splinter, branch drift]
counterexamples: [A historic inactive large file should first pass the leave-alone decision.]
interactions: [change.directional-campaign, evidence.hotspot, testing.provisional-safety-net, change.compatibility-migration]
conflicts: [conflict.change.opportunistic-versus-ranked-campaign, conflict.change.rewrite-versus-incremental]
source_support:
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern`"
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters`"
confidence: contextual-strong
roles: [refactoring-agent, architecture-agent, legacy-agent]
languages: [language-independent]
repository_archetypes: [large active hotspot systems]
retrieval_terms: [splinter pattern, facade refactor, congested hotspot]
activate_for_roles: [refactoring, architecture, legacy]
activate_for_tasks: [first hotspot campaign]
activate_for_repository_signals: [large active file, parallel changes, merge conflict]
activate_for_languages: [all]
activate_for_risk_classes: [high]
exclude_when: [no protection or campaign authority]
prerequisites: [evidence.hotspot, responsibility map, safety net]
retrieval_priority: specialist
retrieval_budget_hint: 500-750 tokens
related_concepts: [change.directional-campaign, change.compatibility-migration]
```

```yaml
id: evidence.logical-change-set
title: Cross-commit logical change grouping
category: architecture
claim: Co-change across split commits or repositories requires a defensible grouping of commits into one logical task.
decision_rule: Prefer explicit ticket/task identifiers; otherwise use a documented same-author/team temporal window with reduced confidence, normalized identity, clocks, and repository roots.
why_it_matters: Same-commit analysis misses distributed work, while temporal windows create false positives.
applicable_when: [multi-repo, microservice, split-commit workflow]
not_applicable_when: [atomic monorepo task commits unless one task still spans commits]
required_evidence: [repo inventory, task linkage or window rationale, support, source/protocol inspection]
insufficient_evidence: [same-day change, shared filename]
required_inputs: [multi-repo logs, task data, identity normalization]
expected_outputs: [logical changes with confidence and grouping rule]
preservation_boundaries: Grouping does not establish semantic dependency or authority.
safe_actions: [use ticket-linked clusters for planning, report heuristic confidence]
unsafe_actions: [infer coupling solely from time proximity, hide grouping assumptions]
common_failure_modes: [release train, dependency bump, timezone error, batch formatting]
counterexamples: [Explicit ticket IDs spanning repositories provide much stronger grouping evidence.]
interactions: [evidence.change-coupling, evidence.behavioral-data-fitness]
conflicts: []
source_support:
  - "`SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: #### Use Logical Change Sets to Group Commits`"
confidence: contextual
roles: [repository-assessment-agent, architecture-agent, review-agent]
languages: [language-independent]
repository_archetypes: [multi-repo, microservice]
retrieval_terms: [logical change set, ticket commit, cross repository coupling]
activate_for_roles: [assessment, architecture, review]
activate_for_tasks: [cross-repo co-change analysis]
activate_for_repository_signals: [multiple repositories, split commits]
activate_for_languages: [all]
activate_for_risk_classes: [normal, high]
exclude_when: [no defensible task grouping]
prerequisites: [evidence.behavioral-data-fitness]
retrieval_priority: specialist
retrieval_budget_hint: 400-650 tokens
related_concepts: [evidence.change-coupling, evidence.behavioral-data-fitness]
```

```yaml
id: review.behavioral-early-warning
title: Nonblocking behavioral review warning
category: review
claim: Rising hotspot rank, steep relative complexity growth, or missing expected co-change should focus review and allow intentional divergence.
decision_rule: Compare against a clean repository-relative baseline, suppress small/noisy cases, show the pattern, inspect the diff and explanation, and record accepted, changed, or escalated disposition.
why_it_matters: Early evidence can catch risk before it hardens, but forced historical conformity prevents healthy refactoring.
applicable_when: [CI or review with stable behavioral baseline]
not_applicable_when: [dirty baseline, generated churn, no meaningful support]
required_evidence: [clean baseline, minimum support, meaningful delta, current diff and context]
insufficient_evidence: [universal percentage or rank threshold]
required_inputs: [pending diff, trend and coupling baseline]
expected_outputs: [warning, rationale, disposition]
preservation_boundaries: Warning remains a prompt unless an independent repository contract makes it a blocker.
safe_actions: [bypass with reason, update baseline as coupling disappears]
unsafe_actions: [force companion edit, freeze complexity ceiling, score authors]
common_failure_modes: [alert fatigue, gaming, fossilized coupling, bad baseline]
counterexamples: [A generated companion file can be mandatory under an explicit generator contract, independent of history.]
interactions: [evidence.change-coupling, evidence.complexity-trend, metric-as-signal]
conflicts: []
source_support:
  - "`SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Detect Future Hotspots`"
  - "`SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Catch the Absence of Change`"
confidence: contextual
roles: [review-agent, coding-agent, repository-assessment-agent]
languages: [language-independent]
repository_archetypes: [active CI repositories]
retrieval_terms: [rising hotspot, missing co-change, complexity warning]
activate_for_roles: [review, coding, assessment]
activate_for_tasks: [pull request review, CI warning]
activate_for_repository_signals: [behavioral baseline, rising rank]
activate_for_languages: [all]
activate_for_risk_classes: [normal, high]
exclude_when: [unfit or noisy baseline]
prerequisites: [evidence.behavioral-data-fitness]
retrieval_priority: normal
retrieval_budget_hint: 300-500 tokens
related_concepts: [evidence.change-coupling, evidence.complexity-trend]
```

## High-confidence negative doctrine

| Negative ID | Operational prohibition and evidence boundary | Canonical targets | Exact support |
|---|---|---|---|
| `negative.change.no-mislabelled-refactoring` | Never label intentional observable behavior, error, side-effect, data, protocol, or resource-semantic change as refactoring; classify and authorize the delta separately. | `change.type-classification`, `change.semantic-structural-separation` | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`; `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software` |
| `negative.change.no-mixed-unverified-repair` | Never combine an unverified repair with a behavior-preserving move; establish the repair with its own oracle and green checkpoint. | `change.semantic-structural-separation` | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing` |
| `negative.change.no-preservation-from-compile-alone` | Never infer behavior preservation from compilation, static analysis, or a narrow happy path alone; name and protect observable effects. | `universal.behavior-preservation`, `testing.effect-surface` | `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Risky Change`; `SRC-REF: chapters/008-chapter-4-building-tests.md :: ## The Value of Self-testing Code` |
| `negative.refactoring.no-size-only-split` | Never split a file, class, or method solely because it is large; require a cohesive independent responsibility and demonstrated pressure. | `change.smell-as-hypothesis`, `change-locality-cohesion` | `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## Seeing Responsibilities`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge` |
| `negative.refactoring.no-smell-verdict` | Never treat a smell or metric as a structural verdict; translate it into a falsifiable maintenance hypothesis. | `change.smell-as-hypothesis`, `metric-as-signal` | `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code`; `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ### Complex Questions Require Context` |
| `negative.design.no-text-only-dry` | Never remove duplication before establishing shared semantic knowledge and expected co-evolution; similarity alone is insufficient. | `design.knowledge-duplication`, `design.earned-abstraction` | `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity` |
| `negative.legacy.no-interface-without-enabling-point` | Never add an interface merely for testability/decoupling without the blocked dependency, alternate behavior, and explicit enabling point. | `legacy.controllable-seam`, `design.earned-abstraction` | `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point`; `SRC-WELC: chapters/034-chapter-25-dependency-breaking-techniques.md :: ## Extract Interface` |
| `negative.testing.no-public-internals-for-test-only` | Never expose private implementation publicly solely for tests without API and information-hiding review; prefer an existing or controlled seam. | `legacy.controllable-seam` | `SRC-WELC: chapters/018-chapter-10-i-can-t-run-this-method-in-a-test-harness.md :: # Chapter 10: I Can't Run This Method in a Test Harness`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ### Effects and Encapsulation` |
| `negative.legacy.no-implicit-test-mode` | Never make production test selection implicit; every seam needs a production default, explicit enabling point, scope, lifetime, and concurrency safety. | `legacy.controllable-seam` | `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point` |
| `negative.legacy.no-silent-characterization-fix` | Never silently fix surprising behavior discovered during characterization; verify, record, seek an oracle, and obtain repair authority. | `testing.characterization`, `change.stop-backtrack-escalate` | `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ### When You Find Bugs`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests` |
| `negative.legacy.no-global-understanding-gate` | Never require complete system understanding or global coverage before a bounded change; protect the relevant effect surface and report residual uncertainty. | `legacy.cover-and-modify`, `testing.effect-surface` | `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## A Heuristic for Writing Characterization Tests` |
| `negative.legacy.no-untracked-temporary-structure` | Never let a temporary seam, sprout, wrapper, facade, sensing variable, or broad safety net become permanent by omission; record its lifecycle. | `legacy.provisional-dependency-break`, `legacy.sprout-wrap`, `testing.provisional-safety-net` | `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ### Summary`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Introduce Provisional End-to-End Tests` |
| `negative.change.no-broad-manual-unverified-refactor` | Never perform a broad manual refactor with only final verification because the end state appears clearer; reduce the step or improve feedback first. | `change.verified-small-step-loop` | `SRC-REF: chapters/005-chapter-1-refactoring-a-first-example.md :: ## Final Thoughts`; `SRC-WELC: chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: ## The Manual Refactoring Challenge` |
| `negative.change.no-text-replace-as-semantic-refactor` | Never trust bulk textual replacement as semantic refactoring; preview, audit dynamic/config/generated/foreign references, retain undo, and verify. | `change.transformation-tool-trust` | `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`; `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ### Undo` |
| `negative.change.no-public-migration-as-refactoring` | Never change a published API, protocol, deployed boundary, or persisted schema under an internal-refactoring assumption. | `change.compatibility-migration` | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Changing Interfaces`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Databases` |
| `negative.evidence.no-churn-equals-bad-design` | Never call high churn bad design without inspecting its cause; healthy tests, central policy, active capability, migrations, and generation can churn. | `evidence.hotspot`, `metric-as-signal` | `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge`; `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Detect Future Hotspots` |
| `negative.evidence.no-cochange-causation` | Never infer defect, dependency direction, or architectural remedy from co-change alone; inspect support, diffs, tasks, source, protocols, and domain. | `evidence.change-coupling` | `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Detect Cochanging Files`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Learn More About Change Coupling` |
| `negative.domain.no-boundary-from-folders-or-clusters` | Never infer a domain/team boundary from folders, graph clusters, or names alone; require language, invariants, data/authority, transaction, and human evidence. | `domain.behavioral-boundary-candidate`, `team-topology-force` | `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### The Big Win Is in the Problem Domain` |
| `negative.evidence.no-age-verdict` | Never interpret old code as good, dead, safe, or reusable solely because it is unchanged; verify use, activity, roadmap, support, defects, and criticality. | `evidence.code-age`, `change.leave-stable-code-alone` | `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code` |
| `negative.testing.no-test-deletion-from-age-or-drift` | Never delete tests because they are old, small, or do not co-grow; prove no supported risk, stronger replacement protection, real cost, and deletion authority. | `testing.provisional-safety-net`, `change.type-classification` | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Reduce Debt by Deleting Cost Sinks`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Test Cases Don't Age Well` |
| `negative.evidence.no-generated-inventory-dominance` | Never let generated, vendored, formatting, migration, or noncode artifacts dominate a maintainer-facing hotspot/co-change result; classify or exclude and disclose. | `evidence.behavioral-data-fitness` | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ### Clean Your Input Data`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: #### Exclude Autogenerated Content` |
| `negative.agent.no-behavioral-performance-scoring` | Never use repository behavioral data for individual productivity/performance scoring; no sample size or normalization repairs missing context and Goodhart effects. | `agent.behavioral-metrics-not-performance` | `SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## Adaptive Behavior and the Destruction of a Data Source`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Don't Turn Knowledge Maps into Performance Evaluations` |
| `negative.evidence.no-unverified-author-truth` | Never treat author/team history as current truth before aliases, pairing/mob work, bots, squashes, copied history, and organizational dates are audited. | `evidence.behavioral-data-fitness`, `team-topology-force` | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ### Specify a Start Date with Organizational Significance` |
| `negative.review.no-forced-historical-cochange` | Never force historically coupled files to remain coupled; warnings must allow intentional divergence because refactoring can remove the relationship. | `review.behavioral-early-warning`, `evidence.change-coupling` | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Catch the Absence of Change`; `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## Learn More About Change Coupling` |
| `negative.change.no-long-isolated-hotspot-branch` | Never start a long isolated congested-hotspot refactor without evidence the branch reduces rather than defers integration conflict; prefer short facade-preserving slices. | `change.splinter-campaign` | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ### Parallel Development Is at Conflict with Refactoring`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters` |
| `negative.architecture.no-distribution-cures-dependency` | Never assume services or repository splits remove dependency; trace protocols, data, deployment, logical changes, and ownership. | `evidence.logical-change-set`, `evidence.change-coupling` | `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Distribution Won't Cure the Dependency Blues`; `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Detect Microservices Shotgun Surgery` |

## Canonical conflict records

```yaml
conflict_id: conflict.change.refactoring-versus-repair
positions:
  - Preserve current behavior strictly during structural work.
  - Correct suspicious nearby behavior while restructuring.
hidden_assumptions: The first assumes current behavior is valuable or unauthorized to change; the second assumes an authoritative oracle and separable causality.
evidence_favoring_each_position:
  preserve: [undocumented deployed behavior, weak tests, independent clients, disputed expectation]
  repair: [explicit acceptance criteria, failing regression test, repair authority, bounded delta]
decision_rule: Default to preservation; when repair evidence exists, complete repair and refactoring as separate verified slices.
unresolved_questions: [client reliance, security urgency, true expected behavior]
roles_affected: [repair-agent, refactoring-agent, coding-agent, review-agent, legacy-agent]
source_support:
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`"
  - "`SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ### When You Find Bugs`"
```

```yaml
conflict_id: conflict.change.opportunistic-versus-ranked-campaign
positions: [Refactor in small bursts adjacent to ordinary work., Fund a deliberate evidence-ranked hotspot campaign.]
hidden_assumptions: Opportunistic work assumes pressure is locally visible and affordable; campaigns assume system-level congestion cannot be paid by one feature and history is fit.
evidence_favoring_each_position:
  opportunistic: [small local friction, adequate tests, limited coordination, immediate change goal]
  campaign: [active complexity growth, repeated defects or co-change, many teams, blocked flow]
decision_rule: Use opportunistic work for bounded pressure; use a ranked campaign for triangulated recurring system cost, while still delivering small slices.
unresolved_questions: [roadmap stability, capacity, ownership, data quality]
roles_affected: [refactoring-agent, architecture-agent, repository-assessment-agent]
source_support:
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?`"
  - "`SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots`"
```

```yaml
conflict_id: conflict.change.abstraction-versus-duplication
positions: [Extract one source of truth., Retain or colocate duplication for local clarity and independent evolution.]
hidden_assumptions: Extraction assumes one stable concept; retention assumes different domain meaning, ownership, or future trajectory.
evidence_favoring_each_position:
  abstraction: [repeated coupled edits, omission defects, same invariant, stable variation]
  duplication: [small repeated knowledge, separate contexts or owners, clarity loss, flag-heavy unification]
decision_rule: Extract only when semantic identity and co-evolution outweigh interface and ownership cost; otherwise retain with proximity/rationale.
unresolved_questions: [future divergence, cross-team coordination cost, omission risk]
roles_affected: [coding-agent, refactoring-agent, review-agent, architecture-agent]
source_support:
  - "`SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ## Duplicated Code`"
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`"
```

```yaml
conflict_id: conflict.change.small-units-versus-deep-module
positions: [Extract small named methods/classes to reduce working memory., Keep cohesive behavior together to preserve information hiding and navigation locality.]
hidden_assumptions: Extraction assumes names replace detail and boundaries align; retention assumes one policy/shared invariant and a compact external interface.
evidence_favoring_each_position:
  extraction: [independent change, mixed abstraction levels, distinct data, high local effect complexity]
  retention: [one algorithm, shared invariants, few stable entry points, extraction creates chatter]
decision_rule: Optimize local reasoning at caller and change site, not raw size; extract an independently evolving named chunk and retain coherent hidden detail.
unresolved_questions: [navigation cost, language idiom, future change directions]
roles_affected: [coding-agent, refactoring-agent, review-agent, architecture-agent]
source_support:
  - "`SRC-REF: chapters/010-chapter-6-composing-methods.md :: ## Extract Method`"
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Turn Hotspot Methods into Brain-Friendly Chunks`"
```

```yaml
conflict_id: conflict.change.rewrite-versus-incremental
positions: [Replace the system with a coherent new implementation., Evolve the existing system through seams, facades, and migrations.]
hidden_assumptions: Rewrite assumes requirements can be rediscovered and catch-up funded; incremental assumes valuable behavior and feasible seams remain.
evidence_favoring_each_position:
  rewrite: [unsupported platform, hard performance or scale ceiling, inability to stabilize after bounded attempts]
  incremental: [hidden domain rules, active features, valuable deployed behavior, high catch-up risk]
decision_rule: Default incremental; recommend replacement only with business authority, requirements and migration proof, parallel-maintenance cost, cutover, and evidence incremental options fail constraints.
unresolved_questions: [true feature set, data migration, cutover, old-system lifetime, knowledge reset]
roles_affected: [architecture-agent, legacy-agent, refactoring-agent]
source_support:
  - "`SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## The Trade-Off Between Architectural Refinements and Replacement Systems`"
  - "`SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?`"
```

```yaml
conflict_id: conflict.change.tests-before-enabling-edit
positions: [Establish tests before production edits., Use a trusted mechanical or hyperaware edit to create the first seam.]
hidden_assumptions: Tests-first assumes a harness is reachable; enabling-edit assumes mechanics are singular, statically visible, reversible, and semantics-preserving.
evidence_favoring_each_position:
  tests_first: [existing observation point, cheap nonproduction seam]
  enabling_edit: [circular legacy dilemma, preserved signatures, strong compiler/tool coverage, tiny reversible change]
decision_rule: Exhaust tests-first; permit the edit only as explicit last resort with no redesign, heightened review, rollback, and immediate characterization.
unresolved_questions: [reflection/config blind spots, reordering effects, tool semantic coverage]
roles_affected: [legacy-agent, refactoring-agent, repair-agent, review-agent]
source_support:
  - "`SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### The Legacy Code Dilemma`"
  - "`SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Lean on the Compiler`"
```

```yaml
conflict_id: conflict.change.stable-code-versus-proactive-work
positions: [Leave old stable code untouched., Improve, isolate, migrate, or replace it before latent risk materializes.]
hidden_assumptions: Leave-alone assumes stability reflects mature low-cost behavior; proactive work assumes inactivity hides unacceptable future or external risk.
evidence_favoring_each_position:
  leave: [runtime use, low incidents and churn, no roadmap pressure, supported dependencies, high characterization risk]
  act: [known vulnerability, unsupported platform, imminent change, durability gap, critical knowledge loss, dead-code proof]
decision_rule: Age adjusts priority only; combine use, roadmap, incidents, support, criticality, and intervention risk.
unresolved_questions: [hidden users, dormant feature, future regulation, fear-driven avoidance]
roles_affected: [architecture-agent, legacy-agent, refactoring-agent, review-agent]
source_support:
  - "`SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`"
  - "`SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code`"
```

```yaml
conflict_id: conflict.legacy.temporary-seam-versus-final-design
positions: [Accept a local provisional seam/sprout/wrapper to gain feedback., Introduce only a durable architecture-quality boundary.]
hidden_assumptions: Temporary structure assumes feedback value dominates short-lived complexity; durable design assumes final responsibility is sufficiently known and affordable.
evidence_favoring_each_position:
  temporary: [urgent required change, untestable dependency, narrow reversible hook, uncertain final owner]
  durable: [multiple real implementations, stable policy/mechanism boundary, public extension need, unsafe temporary global]
decision_rule: Choose the least risky option that enables protection; use durable structure only when independently earned and govern temporary lifecycle explicitly.
unresolved_questions: [cleanup ownership, API compatibility, production adoption risk]
roles_affected: [legacy-agent, coding-agent, architecture-agent, refactoring-agent]
source_support:
  - "`SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`"
  - "`SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ### Advantages and Disadvantages`"
```

```yaml
conflict_id: conflict.testing.broad-versus-narrow
positions: [Use broad covering or E2E characterization quickly., Break dependencies and create fast localized tests.]
hidden_assumptions: Broad coverage assumes a stable affordable observable boundary; narrow coverage assumes seams can be introduced safely.
evidence_favoring_each_position:
  broad: [stable pinch point, local harness initially impossible, critical user scenarios]
  narrow: [deterministic seam, need localization, repeated development, flaky or expensive E2E]
decision_rule: Use the narrowest practical stable observation; if broad is necessary, make it provisional and narrow as structure permits.
unresolved_questions: [runtime, flakiness, rare paths, retirement criteria]
roles_affected: [legacy-agent, repair-agent, refactoring-agent, testing-agent]
source_support:
  - "`SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: #### Higher-Level Interception Points`"
  - "`SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net`"
```

```yaml
conflict_id: conflict.evidence.static-versus-behavioral
positions: [Inspect current structure and tests directly., Use history to rank hotspots, co-change, trends, age, and ownership.]
hidden_assumptions: Static review assumes current structure exposes the issue; history assumes past change is clean and predictive of near-term cost.
evidence_favoring_each_position:
  static: [new repository, imported or rewritten history, explicit current defect/security contract]
  behavioral: [large mature active repository, scarce attention, many plausible candidates]
decision_rule: Use behavioral evidence to allocate attention when fit; use static, runtime, domain, and contract evidence to decide.
unresolved_questions: [window, moves, seasonality, roadmap discontinuity]
roles_affected: [repository-assessment-agent, refactoring-agent, architecture-agent, review-agent]
source_support:
  - "`SRC-SDX: chapters/004-the-world-of-behavioral-code-analysis.md :: # The World of Behavioral Code Analysis`"
  - "`SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Inspect the Code`"
```

```yaml
conflict_id: conflict.sociotechnical.ownership-versus-broad-knowledge
positions: [Give a person/pair/small team clear operational responsibility., Encourage broad contribution and knowledge to avoid silos.]
hidden_assumptions: Ownership assumes responsibility reduces diffusion; broad access assumes knowledge improves resilience and can be coordinated.
evidence_favoring_each_position:
  ownership: [fragmented congested hotspot, no maintainer, repeated conflict, quality drift]
  broad_knowledge: [knowledge-loss risk, cross-team dependency, reviewer bottleneck, succession need]
decision_rule: Keep operational responsibility narrower than knowledge boundaries through accountable teams, open reviewed contribution, and deliberate backup expertise.
unresolved_questions: [team scale, reviewer capacity, succession, motivation, authority]
roles_affected: [architecture-agent, review-agent, repository-assessment-agent]
source_support:
  - "`SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Code Ownership Means Responsibility`"
  - "`SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Provide Broad Knowledge Boundaries`"
```

```yaml
conflict_id: conflict.change.direct-coupling-versus-boundary
positions: [Collocate co-changing code and use direct coupling for local clarity., Separate behind an interface/service/repository for independent policy, ownership, or operation.]
hidden_assumptions: Direct coupling assumes one concept/owner/lifecycle; boundary assumes independence repays protocol, test, operational, and coordination cost.
evidence_favoring_each_position:
  direct: [persistent co-change, same domain capability, no independent deployment or security need]
  boundary: [different scaling, deployment, security, data authority, implementations, or release cadence]
decision_rule: Choose the boundary strength that localizes dominant demonstrated forces; neither distribute to cure code coupling nor merge solely from co-change.
unresolved_questions: [transactions, failure, latency, rollback, ownership, future variation]
roles_affected: [architecture-agent, refactoring-agent, domain-agent]
source_support:
  - "`SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Optimize for Sociotechnical Congruence Across Boundaries`"
  - "`SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Distribution Won't Cure the Dependency Blues`"
```

```yaml
conflict_id: conflict.change.comments-versus-structure
positions: [Extract and rename so code explains itself., Preserve comments that carry rationale, constraints, uncertainty, or nonlocal contracts.]
hidden_assumptions: Structural improvement assumes syntax can carry the meaning; comments assume the knowledge is causal or contextual.
evidence_favoring_each_position:
  structure: [comment paraphrases mechanics or marks a nameable block]
  comment: [why-not alternatives, external constraint, intentional duplication, safety invariant]
decision_rule: Improve structure where it can carry meaning; retain concise verified rationale code cannot express.
unresolved_questions: [documentation ownership, checking comment assumptions]
roles_affected: [coding-agent, review-agent, refactoring-agent, legacy-agent]
source_support:
  - "`SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: ### Comments`"
  - "`SRC-SDX: chapters/012-chapter-6-spot-your-system-s-tipping-point-is-software-too-hard-divide-and-conquer-with-architectural-hotspots-analyze-subsystems-fight-the-normalization-of-deviance-toward-team-oriented-measures-exercises.md :: ## Ask the Right Questions`"
```

```yaml
conflict_id: conflict.evidence.cochange-versus-domain
positions: [Use co-change clusters as candidate modular/domain boundaries., Let domain language, invariants, data and authority define boundaries even when history differs.]
hidden_assumptions: Co-change assumes work patterns reveal semantics; domain-first assumes experts and current model are sufficiently accurate and history artifacts are secondary.
evidence_favoring_each_position:
  cochange: [strong repeated support across technical layers, repeated policy, stable task grouping]
  domain: [clear language discontinuity, invariant/transaction owner, accepted context, co-change explained by release/process]
decision_rule: Co-change nominates; domain and operational evidence decide. Preserve disagreement when the two remain inconsistent and prototype alternatives.
unresolved_questions: [task bundling, organizational cause, transaction cost, future roadmap]
roles_affected: [architecture-agent, domain-agent, refactoring-agent, repository-assessment-agent]
source_support:
  - "`SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`"
  - "`SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### The Big Win Is in the Problem Domain`"
```

## Procedure refinements

### `procedure.change.classify`

- **Refines:** PROC-CL-001; canonical entry concepts `change.type-classification`, `change.semantic-structural-separation`.
- **Inputs / evidence:** request, acceptance criteria, current/desired observations, contracts, proposed work; an authoritative desired-behavior source is required.
- **Steps:** enumerate intended observable deltas → classify primary purpose → enumerate invariants → split mixed purposes → map authority/protection per slice.
- **Outputs:** type, authorized semantic delta, preservation list, slice order.
- **Stop / escalate:** stop when desired behavior or caller contract is unknown; escalate public, data, production, safety, or authority choices.
- **False positives:** “cleanup” assumed harmless; deletion assumed semantic-free; resource-semantic optimization called structure.
- **Exact support:** `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring`.

### `procedure.change.establish-preservation`

- **Refines:** PROC-CL-002; `universal.behavior-preservation`, `testing.effect-surface`.
- **Inputs / evidence:** classified change, requirements/ADRs, callers, tests, schemas/protocols, runtime and incident evidence.
- **Steps:** inventory outputs/errors/side effects/data/ordering/timing/durability/compatibility → remove authorized deltas → rank consequence × uncertainty → assign checks → record unprotected unknowns and owners.
- **Outputs:** surface × invariant × evidence × check × confidence matrix.
- **Stop / escalate:** stop when a high-consequence surface has neither evidence nor safe observation; escalate disputed or irreversible boundaries.
- **False positives:** preserving internal shape; omitting failures/side effects; treating current tests as full contract.
- **Exact support:** `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Risky Change`; `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation`.

### `procedure.refactoring.earn`

- **Refines:** PROC-CL-003; `change.refactoring-pressure`, `change.smell-as-hypothesis`, `metric-as-signal`.
- **Inputs / evidence:** current work, smell/metric, change/defect/review/test history, responsibility/dependency map; require a causal structural-pressure hypothesis.
- **Steps:** state goal without transformation → enumerate pressure → falsify smell/metric artifacts → compare retain/document/proximity/local/campaign options → predict pressure reduction and costs → select smallest net-positive reversible response.
- **Outputs:** earned/not-earned/uncertain, first action, verification/no-change rationale.
- **Stop / escalate:** stop if aesthetics are the only support or protection is inadequate; escalate architecture/API/data or capacity commitments.
- **False positives:** size, age, churn, smell detector, disliked style, low coverage alone.
- **Exact support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge`.

### `procedure.refactoring.select-first-campaign`

- **Refines:** PROC-CL-004; `change.directional-campaign`, `change.verified-small-step-loop`.
- **Inputs / evidence:** ranked pressures, preservation matrix, seams/tests, ownership/parallel work, integration cadence.
- **Steps:** separate semantic work → rank recurring cost × risk reduction × seam × reversibility ÷ coordination → select one responsibility/effect → define one useful outcome → order protection/mechanics/checks/integration → set reversal signals.
- **Outputs:** one bounded campaign and deferred-candidate ledger.
- **Stop / escalate:** stop without local value or protection; escalate architecture authority, long freeze, schema/API migration, or cross-team scheduling.
- **False positives:** highest LOC first; easiest unrelated cleanup; final architecture chosen before first seam.
- **Exact support:** `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ## Get used to picking a goal.`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities`.

### `procedure.legacy.safe-change`

- **Refines:** PROC-CL-005; `legacy.cover-and-modify`.
- **Inputs / evidence:** authorized delta, suspected change point, build/run path, dependencies, tests; require a repeatable baseline at some level.
- **Steps:** identify change point → trace effects → choose closest viable test point → identify one blocking dependency → add least invasive seam → characterize → implement semantic slice → verify preservation → optionally refactor on green.
- **Outputs:** safe-change route, tests, semantic diff, uncertainty ledger.
- **Stop / escalate:** stop without safe baseline or isolated environment; escalate disputed behavior, public boundary, production-only state, safety/durability risk.
- **False positives:** break all dependencies; global coverage goal; fake test treated as integration proof.
- **Exact support:** `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm`; `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: # Chapter 3: Sensing and Separation`.

### `procedure.testing.characterize`

- **Refines:** PROC-CL-006; `testing.characterization`.
- **Inputs / evidence:** change/effect surface, runnable observation, representative state; require repeatable actual observation.
- **Steps:** choose relevant path → assert and observe → rule out harness error/nondeterminism → encode actual behavior → add change-sensitive boundaries/errors → stop when unintended change is detectable.
- **Outputs:** targeted tests plus suspicious/unknown ledger.
- **Stop / escalate:** stop for uncontrolled destructive/nondeterministic behavior; escalate authoritative-spec conflict or possible defect.
- **False positives:** unreviewed snapshots; timestamps/IDs captured; irrelevant branches; observed equals correct.
- **Exact support:** `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests`; `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## A Heuristic for Writing Characterization Tests`.

### `procedure.legacy.select-seam`

- **Refines:** PROC-CL-007; `legacy.controllable-seam`, `legacy.provisional-dependency-break`.
- **Inputs / evidence:** blocked test/change, dependency path, language/build/runtime mechanisms, API constraints; require exact obstacle and alternate behavior.
- **Steps:** state sensing/separation goal → locate enabling points → enumerate existing boundary/parameter/function/object/factory/subclass/link/preprocessor options → rank impact/scope/concurrency/compatibility/reversal → implement smallest → prove production default → set lifecycle.
- **Outputs:** seam, enabling point, tests, disposition.
- **Stop / escalate:** stop if all options alter semantics or use unsafe ambient state; escalate public API, global process, linker/deployment, or security boundary.
- **False positives:** unselectable interface; static setter leakage; generic injection framework.
- **Exact support:** `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ### Seam Types`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point`.

### `procedure.testing.select-from-effects`

- **Refines:** PROC-CL-008; `testing.effect-surface`, `testing.pinch-point`.
- **Inputs / evidence:** change point, call graph, state/I/O boundaries; require forward trace of direct and deferred effects.
- **Steps:** mark direct effects → propagate to firewalls/stable observations → find convergence points → rank locality/determinism/cost → choose nearest coverage plus critical broad contracts → record unknowns.
- **Outputs:** required test/characterization set and confidence.
- **Stop / escalate:** stop when high-consequence dynamic/distributed effects cannot be safely bounded; escalate production-only or uncertain asynchronous effects.
- **False positives:** class boundary equals effect boundary; no return equals no effect; one E2E path covers all.
- **Exact support:** `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Reasoning About Effects`; `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ## Interception Points`.

### `procedure.design.evaluate-duplication`

- **Refines:** PROC-CL-009; `design.knowledge-duplication`, `design.earned-abstraction`.
- **Inputs / evidence:** candidate clones, domain meanings, callers/owners, history/co-change, variation; require semantic and evolution comparison.
- **Steps:** identify repeated knowledge → compare invariants/owners → inspect co-change/omissions → model extraction interface and variation → compare retain/proximity/generate/abstract → select lowest change-amplification option preserving clarity.
- **Outputs:** diagnosis plus retain/proximity/generate/extract decision.
- **Stop / escalate:** stop if concept cannot be named or variation is unstable; escalate public/cross-context/team abstraction.
- **False positives:** clone percentage; two similar tests; repeated syntax with different policy.
- **Exact support:** `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity`.

### `procedure.evidence.assess-hotspot`

- **Refines:** PROC-CL-010; `evidence.hotspot`, `evidence.complexity-trend`.
- **Inputs / evidence:** fit history, file identity, source metrics, current source/tests, roadmap/incidents.
- **Steps:** audit data → choose product-relevant interval → partition nonmaintainer artifacts → rank frequency → add complexity → inspect trend → drill to functions → correlate responsibilities/defects/tests/roadmap/congestion → classify.
- **Outputs:** evidence-backed candidate queue and nonfindings.
- **Stop / escalate:** stop if history is unfit or product phase invalidates it; escalate broad architecture/team/resource recommendations.
- **False positives:** version/Makefile/generated artifact; completed historical refactor; simple central policy; active healthy feature work.
- **Exact support:** `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Evaluate Hotspots with Complexity Trends`.

### `procedure.evidence.audit-history`

- **Refines:** PROC-CL-011; `evidence.behavioral-data-fitness`.
- **Inputs / evidence:** VCS logs, policies, branch/merge events, team map, analysis claim; sample raw commits across the interval.
- **Steps:** define required fields → inspect aliases/bots/pairing → squashes/merges/imports → renames/moves/copied history → generated/vendor/noncode/migrations → align dates → validate tasks/windows → mark each metric usable/corrected/limited/invalid.
- **Outputs:** provenance ledger and disclosed exclusions.
- **Stop / escalate:** stop when claim assumptions cannot be repaired; escalate privacy/legal/people attribution.
- **False positives:** parser success; commit volume; `.mailmap` assumed complete; main branch assumed representative.
- **Exact support:** `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ### Specify a Start Date with Organizational Significance`.

### `procedure.architecture.assess-behavioral-boundary`

- **Refines:** PROC-CL-012; `domain.behavioral-boundary-candidate`.
- **Inputs / evidence:** co-change, static dependencies, domain language, invariants/data/transactions, team/deployment ownership, ADRs; require history plus domain/operational evidence.
- **Steps:** state driver → map accepted boundary → inspect co-change/source → identify concepts/invariants/data owner → generate retain/collocate/component/protocol options → assess chatter/migration/operations/reversal → prototype/deletion-test → recommend only if driver improves.
- **Outputs:** boundary assessment, alternatives, costs, confidence, authority needs.
- **Stop / escalate:** stop with only directory/metric evidence or disputed domain; escalate cross-team/data/deployment/public contract.
- **False positives:** release train, test/codegen coupling, mass edits, service/repo assumed domain.
- **Exact support:** `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns`; `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### Use the Deletion Test`.

### `procedure.refactoring.select-splinter`

- **Refines:** PROC-CL-013; `change.splinter-campaign`.
- **Inputs / evidence:** validated congested hotspot, behavior groups, function activity, safety net, parallel plan.
- **Steps:** establish protection → identify groups → improve proximity → select highest-pressure cohesive group → extract while original remains → delegate → regress → integrate → remeasure → separately migrate callers later if authorized.
- **Outputs:** one extracted responsibility, original facade, verification, follow-up signals.
- **Stop / escalate:** stop if group lacks cohesion/protection or cannot integrate quickly; escalate caller migration, schema, freeze, or cross-team coordination.
- **False positives:** size-only split; technical syntax grouping; final-design perfection in first slice.
- **Exact support:** `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Split a Hotspot File Along Its Responsibilities`; `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters`.

### `procedure.change.leave-alone`

- **Refines:** PROC-CL-014; `change.leave-stable-code-alone`, `evidence.code-age`.
- **Inputs / evidence:** target, activity, runtime use, incidents, roadmap, support/security, characterization cost.
- **Steps:** identify benefit → verify current/imminent pressure → check confirmed obligations → estimate discovery/integration risk → compare leave/isolate/characterize/delete-investigate/refactor/migrate → choose no change if no authorized positive option.
- **Outputs:** no-change or action decision with revisit trigger.
- **Stop / escalate:** stop destructive action when use/criticality is unknown; escalate external consumers, safety/security, unsupported platform, imminent major change.
- **False positives:** stable means good; ugly means costly; old means dead; paused means stable.
- **Exact support:** `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?`; `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`.

### `procedure.change.stop-escalate`

- **Refines:** PROC-CL-015; `change.stop-backtrack-escalate`.
- **Inputs / evidence:** goal, authority, diff, baseline/check results, unknowns, external effects, integration state.
- **Steps:** verify singular goal → preservation and last move → new semantic/architecture/API/data/production decision → failure localization/reversal → continue only if next step is authorized/protected/smaller than uncertainty → otherwise retain/backtrack/escalate.
- **Outputs:** continue, stop, retain, backtrack, or escalate with reason.
- **Stop / escalate:** each failed gate is a stop; escalation carries options, evidence, and explicit missing authority.
- **False positives:** sunk cost, almost done, deadline as permission, stopping before safe diagnosis.
- **Exact support:** `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ### Stop when you are unsure.`; `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: #### Backtrack.`.

### `procedure.change.validate-transformation-tool`

- **Refines:** PROC-CL-016; `change.transformation-tool-trust`.
- **Inputs / evidence:** tool/version, operation, languages/files, dynamic/config/generated surfaces, repository checks.
- **Steps:** record support → enumerate blind spots → preview bounded target → inspect declarations/references/diff → run compile/static/targeted/broad checks → search unresolved symbolic/config/serialized forms → retain rollback → downgrade if uncertain.
- **Outputs:** verified transformation or rejected/limited plan.
- **Stop / escalate:** stop opaque output, no undo, unsupported construct, mixed semantic edit, unresolved dynamic references; escalate public/schema/serialization/cross-repo/generator boundaries.
- **False positives:** compiler green; brand trust; text match equals reference; no text match equals no dynamic use.
- **Exact support:** `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Technical Criteria for a Refactoring Tool`; `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`.

## Graph node and formulation candidates

Canonical IDs are the proposed semantic node IDs; `Graph node` supplies a collision-resistant ingestion handle. The complete multi-source formulations are in the source-formulation ledger above.

| Graph node | Canonical concept | Kind | Extraction aliases normalized | Primary exact formulation anchor | Relation |
|---|---|---|---|---|---|
| `node.changelegacy.001` | `change.type-classification` | terminology | CHG-UNI-001; G-CL-CHANGE-TYPE | `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software` | direct_support |
| `node.changelegacy.002` | `universal.behavior-preservation` | constraint | CHG-UNI-002; G-CL-PRESERVATION | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ## Defining Refactoring` | direct_support |
| `node.changelegacy.003` | `change.semantic-structural-separation` | constraint | CHG-UNI-003; G-CL-TWO-HATS | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats` | direct_support |
| `node.changelegacy.004` | `change.verified-small-step-loop` | pattern | CHG-UNI-004; G-CL-SMALL-STEP; G-CL-REVERSAL | `SRC-REF: chapters/005-chapter-1-refactoring-a-first-example.md :: ## Final Thoughts` | direct_support |
| `node.changelegacy.005` | `change.stop-backtrack-escalate` | constraint | CHG-UNI-005; G-CL-STOP-ESCALATE | `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: ### Stop when you are unsure.` | direct_support |
| `node.changelegacy.006` | `change.refactoring-pressure` | proof-obligation | CHG-REF-001; G-CL-REF-PRESSURE | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?` | direct_support |
| `node.changelegacy.007` | `change.smell-as-hypothesis` | evidence-rule | CHG-REF-002; G-CL-SMELL-HYP | `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code` | direct_support |
| `node.changelegacy.008` | `design.knowledge-duplication` | smell | CHG-REF-003 diagnosis; G-CL-EARNED-ABSTRACTION precursor | `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste` | refinement |
| `node.changelegacy.009` | `design.earned-abstraction` | proof-obligation | CHG-REF-003 action; G-CL-EARNED-ABSTRACTION | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity` | direct_support |
| `node.changelegacy.010` | `change-locality-cohesion` | principle | CHG-REF-004; G-CL-RESPONSIBILITY | `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: ## Seeing Responsibilities` | refinement |
| `node.changelegacy.011` | `change.compatibility-migration` | pattern | CHG-REF-005; G-CL-COMPAT-MIGRATION | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Changing Interfaces` | direct_support |
| `node.changelegacy.012` | `change.transformation-tool-trust` | proof-obligation | CHG-REF-006; G-CL-TOOL-TRUST | `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy` | direct_support |
| `node.changelegacy.013` | `change.directional-campaign` | pattern | CHG-REF-007 | `SRC-REF: chapters/016-chapter-12-big-refactorings.md :: ## The Nature of the Game` | direct_support |
| `node.changelegacy.014` | `change.leave-stable-code-alone` | terminal-decision | CHG-REF-008; G-CL-LEAVE-ALONE | `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?` | direct_support |
| `node.changelegacy.015` | `legacy.cover-and-modify` | pattern | CHG-LEG-001 | `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: ## The Legacy Code Change Algorithm` | direct_support |
| `node.changelegacy.016` | `testing.characterization` | technique | CHG-LEG-002; CHG-LEG-003; G-CL-CHAR-SURFACE | `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests` | direct_support |
| `node.changelegacy.017` | `legacy.controllable-seam` | technique | CHG-LEG-004; G-CL-SEAM; G-CL-ENABLING-POINT | `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: ## Seams`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point` | direct_support |
| `node.changelegacy.018` | `testing.test-double-scope` | proof-obligation | CHG-LEG-005; G-CL-SENSING; G-CL-SEPARATION | `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: #### Fake Objects Support Real Tests` | direct_support |
| `node.changelegacy.019` | `legacy.provisional-dependency-break` | pattern | CHG-LEG-006; G-CL-TEMP-STRUCT | `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Break Dependencies` | direct_support |
| `node.changelegacy.020` | `testing.effect-surface` | evidence-concept | CHG-LEG-007; G-CL-EFFECT-SURFACE | `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation` | direct_support |
| `node.changelegacy.021` | `testing.pinch-point` | technique | CHG-LEG-008; G-CL-PINCH-POINT | `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: #### Pinch Point` | direct_support |
| `node.changelegacy.022` | `legacy.current-work-responsibility-discovery` | heuristic | CHG-LEG-009; CHG-LEG-011 | `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work` | direct_support |
| `node.changelegacy.023` | `learning.scratch-refactoring` | technique | CHG-LEG-010 | `SRC-WELC: chapters/024-chapter-16-i-don-t-understand-the-code-well-enough-to-change-it.md :: ## Scratch Refactoring` | direct_support |
| `node.changelegacy.024` | `legacy.sprout-wrap` | pattern | CHG-LEG-012 | `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Sprout Method`; `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ## Wrap Method` | direct_support |
| `node.changelegacy.025` | `testing.provisional-safety-net` | pattern | CHG-LEG-013 | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net` | direct_support |
| `node.changelegacy.026` | `legacy.unprotected-enabling-edit` | proof-obligation | CHG-LEG-014 | `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Hyperaware Editing` | direct_support |
| `node.changelegacy.027` | `metric-as-signal` | evidence-rule | CHG-HIST-001; G-CL-HISTORY-priority | `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data` | direct_support |
| `node.changelegacy.028` | `evidence.hotspot` | evidence-signal | CHG-HIST-002; G-CL-HOTSPOT | `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots` | direct_support |
| `node.changelegacy.029` | `evidence.change-coupling` | evidence-signal | CHG-HIST-003; G-CL-COCHANGE | `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ### What Is Change Coupling?` | direct_support |
| `node.changelegacy.030` | `evidence.complexity-trend` | evidence-signal | CHG-HIST-004; G-CL-COMPLEXITY-TREND | `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Evaluate Hotspots with Complexity Trends` | direct_support |
| `node.changelegacy.031` | `evidence.code-age` | evidence-signal | CHG-HIST-005; G-CL-CODE-AGE | `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Stabilize Code by Age` | direct_support |
| `node.changelegacy.032` | `evidence.behavioral-data-fitness` | proof-obligation | CHG-HIST-006; G-CL-DATA-FITNESS | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis` | direct_support |
| `node.changelegacy.033` | `team-topology-force` | socio-technical context | CHG-HIST-007; G-CL-SOCIOTECHNICAL | `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Measure Coordination Needs` | direct_support |
| `node.changelegacy.034` | `agent.behavioral-metrics-not-performance` | prohibition | CHG-HIST-008; G-CL-NO-PERF-SCORING | `SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## Adaptive Behavior and the Destruction of a Data Source` | direct_support |
| `node.changelegacy.035` | `domain.behavioral-boundary-candidate` | heuristic | CHG-HIST-009; G-CL-DOMAIN-BOUNDARY | `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns` | direct_support |
| `node.changelegacy.036` | `change.splinter-campaign` | pattern | CHG-HIST-010; G-CL-SPLINTER | `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern` | direct_support |
| `node.changelegacy.037` | `evidence.logical-change-set` | technique | CHG-HIST-011 | `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: #### Use Logical Change Sets to Group Commits` | direct_support |
| `node.changelegacy.038` | `review.behavioral-early-warning` | technique | CHG-HIST-012 | `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Catch the Absence of Change` | direct_support |

## Typed graph edge candidates

| Edge ID | From | Relationship label | To | Condition / interpretation | Provenance relation and exact source |
|---|---|---|---|---|---|
| `edge.changelegacy.001` | `change.type-classification` | `determines` | `universal.behavior-preservation` | Change purpose determines authorized deltas and preserved remainder. | direct_support: `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ## Four Reasons to Change Software` |
| `edge.changelegacy.002` | `change.type-classification` | `constrains` | `change.semantic-structural-separation` | Mixed types are split into attributable slices. | direct_support: `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats` |
| `edge.changelegacy.003` | `universal.behavior-preservation` | `requires_when_uncertain` | `testing.characterization` | Characterization discovers and protects current relevant behavior. | direct_support: `SRC-WELC: chapters/021-chapter-13-i-need-to-make-a-change-but-i-don-t-know-what-tests-to-write.md :: ## Characterization Tests` |
| `edge.changelegacy.004` | `testing.effect-surface` | `scopes` | `universal.behavior-preservation` | Reachable effects enumerate material preservation surfaces. | derived_inference: `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation`; `SRC-WELC: chapters/008-chapter-1-changing-software.md :: ### Risky Change` |
| `edge.changelegacy.005` | `change.semantic-structural-separation` | `constrains` | `change.verified-small-step-loop` | Each verified loop carries one purpose. | corroboration: `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### The Two Hats`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Single-Goal Editing` |
| `edge.changelegacy.006` | `change.verified-small-step-loop` | `enables` | `change.stop-backtrack-escalate` | Small green checkpoints make reversal and retention precise. | direct_support: `SRC-REF: chapters/020-chapter-15-putting-it-all-together.md :: #### Backtrack.` |
| `edge.changelegacy.007` | `change.refactoring-pressure` | `prerequisite_for` | `change.directional-campaign` | A broad campaign needs stronger demonstrated pressure than a local move. | derived_inference: `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Should You Refactor?`; `SRC-REF: chapters/016-chapter-12-big-refactorings.md :: ## The Nature of the Game` |
| `edge.changelegacy.008` | `change.smell-as-hypothesis` | `provides_candidate_evidence_for` | `change.refactoring-pressure` | A validated consequence may help earn action; the smell alone cannot. | refinement: `SRC-REF: chapters/007-chapter-3-bad-smells-in-code.md :: # Chapter 3: Bad Smells in Code`; `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ### Use Hotspots to Improve, Not Judge` |
| `edge.changelegacy.009` | `metric-as-signal` | `may_inform_but_not_decide` | `change.refactoring-pressure` | Metrics allocate attention; repository evidence decides. | direct_support: `SRC-SDX: chapters/006-chapter-1-why-technical-debt-isn-t-technical.md :: ## Prioritize Improvements Guided by Data` |
| `edge.changelegacy.010` | `design.knowledge-duplication` | `creates_pressure_for` | `design.earned-abstraction` | Repeated knowledge is a candidate reason to abstract, not proof. | refinement: `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste` |
| `edge.changelegacy.011` | `evidence.change-coupling` | `corroborates` | `design.knowledge-duplication` | Co-evolving similar sites make duplicated knowledge more plausible. | direct_support: `SRC-SDX: chapters/008-chapter-3-coupling-in-time-a-heuristic-for-the-concept-of-surprise.md :: ## The Dirty Secret of Copy-Paste` |
| `edge.changelegacy.012` | `design.earned-abstraction` | `may_improve` | `change-locality-cohesion` | A good abstraction localizes one evolving policy; a bad one can worsen locality. | refinement: `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Follow the Principle of Proximity` |
| `edge.changelegacy.013` | `legacy.current-work-responsibility-discovery` | `provides_semantic_evidence_for` | `change-locality-cohesion` | Current work reveals a candidate cohesive responsibility. | direct_support: `SRC-WELC: chapters/028-chapter-20-this-class-is-too-big-and-i-don-t-want-it-to-get-any-bigger.md :: #### Heuristic #7: Focus on the Current Work` |
| `edge.changelegacy.014` | `change.compatibility-migration` | `extends` | `universal.behavior-preservation` | Preservation spans independently released callers and historical data. | direct_support: `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Changing Interfaces`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### Databases` |
| `edge.changelegacy.015` | `change.transformation-tool-trust` | `guards` | `change.verified-small-step-loop` | Automation can accelerate a move only within verified semantic coverage. | direct_support: `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy` |
| `edge.changelegacy.016` | `change.transformation-tool-trust` | `does_not_replace` | `universal.behavior-preservation` | Tool success is not full repository behavior proof. | derived_inference: `SRC-REF: chapters/019-chapter-14-refactoring-tools.md :: ## Accuracy`; `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Lean on the Compiler` |
| `edge.changelegacy.017` | `change.leave-stable-code-alone` | `terminal_when_unmet` | `change.refactoring-pressure` | If pressure/protection/authority does not clear the gate, no action is the result. | direct_support: `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?` |
| `edge.changelegacy.018` | `legacy.cover-and-modify` | `requires` | `testing.effect-surface` | Finding useful test points depends on tracing effects from the change. | refinement: `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Reasoning About Effects` |
| `edge.changelegacy.019` | `legacy.cover-and-modify` | `may_require` | `legacy.controllable-seam` | A blocking dependency is broken at an explicit controllable point. | direct_support: `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Break Dependencies`; `SRC-WELC: chapters/011-chapter-4-the-seam-model.md :: #### Enabling Point` |
| `edge.changelegacy.020` | `legacy.controllable-seam` | `enables` | `testing.characterization` | Seam selection makes relevant code executable or observable. | corroboration: `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: # Chapter 3: Sensing and Separation` |
| `edge.changelegacy.021` | `testing.test-double-scope` | `constrains_evidence_from` | `testing.characterization` | A double-backed observation proves local behavior only. | direct_support: `SRC-WELC: chapters/010-chapter-3-sensing-and-separation.md :: #### Fake Objects Support Real Tests` |
| `edge.changelegacy.022` | `legacy.provisional-dependency-break` | `may_instantiate` | `legacy.controllable-seam` | The first seam may be provisional when its purpose is feedback. | direct_support: `SRC-WELC: chapters/009-chapter-2-working-with-feedback.md :: #### Break Dependencies` |
| `edge.changelegacy.023` | `testing.effect-surface` | `selects` | `testing.characterization` | Effects determine what observations need characterization. | direct_support: `SRC-WELC: chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: ## Effect Propagation` |
| `edge.changelegacy.024` | `testing.effect-surface` | `may_converge_at` | `testing.pinch-point` | Several effect paths can share one stable observation. | direct_support: `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: #### Pinch Point` |
| `edge.changelegacy.025` | `testing.pinch-point` | `trades_localization_for` | `testing.characterization` | Broader interception reduces dependency work but weakens diagnosis. | refinement: `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: ## Traps Pinch Point Traps` |
| `edge.changelegacy.026` | `learning.scratch-refactoring` | `supports` | `legacy.current-work-responsibility-discovery` | Disposable extraction makes hidden responsibilities visible. | direct_support: `SRC-WELC: chapters/024-chapter-16-i-don-t-understand-the-code-well-enough-to-change-it.md :: ## Scratch Refactoring` |
| `edge.changelegacy.027` | `legacy.sprout-wrap` | `specializes_under_pressure` | `legacy.provisional-dependency-break` | Sprout/wrap is a deadline-oriented isolation alternative, not a generic seam mandate. | refinement: `SRC-WELC: chapters/014-chapter-6-i-don-t-have-much-time-and-i-have-to-change-it.md :: ### Summary` |
| `edge.changelegacy.028` | `testing.provisional-safety-net` | `may_realize` | `testing.pinch-point` | Broad black-box protection can be the initial convergence surface. | corroboration: `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Build Temporary Tests as a Safety Net`; `SRC-WELC: chapters/020-chapter-12-i-need-to-make-many-changes-in-one-area-do-i-have-to-break-dependencies-for-all-the-classes-involved.md :: #### Higher-Level Interception Points` |
| `edge.changelegacy.029` | `legacy.unprotected-enabling-edit` | `exception_under_gate_to` | `legacy.provisional-dependency-break` | A testless bridge is allowed only when it creates the first protection and no safer seam exists. | direct_support: `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ## Hyperaware Editing` |
| `edge.changelegacy.030` | `change.transformation-tool-trust` | `guards` | `legacy.unprotected-enabling-edit` | Compiler/tool coverage constrains the last-resort bridge but does not eliminate risk. | refinement: `SRC-WELC: chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: ### Lean on the Compiler` |
| `edge.changelegacy.031` | `evidence.hotspot` | `specializes` | `metric-as-signal` | Hotspots are a particular attention-ranking signal. | direct_support: `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Prioritize Technical Debt with Hotspots` |
| `edge.changelegacy.032` | `evidence.complexity-trend` | `corroborates` | `evidence.hotspot` | Active structural growth strengthens a hotspot hypothesis. | direct_support: `SRC-SDX: chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: ## Evaluate Hotspots with Complexity Trends` |
| `edge.changelegacy.033` | `evidence.code-age` | `may_support` | `change.leave-stable-code-alone` | Stable age can downrank intervention only with current context. | corroboration: `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ## Your Best Bug Fix Is Time`; `SRC-REF: chapters/006-chapter-2-principles-in-refactoring.md :: ### When Shouldn't You Refactor?` |
| `edge.changelegacy.034` | `evidence.code-age` | `does_not_entail` | `change.leave-stable-code-alone` | Old may mean dead, paused, abandoned, or risky; age alone cannot decide. | negative_support: `SRC-SDX: chapters/010-chapter-5-the-principles-of-code-age.md :: ### Dead Code Is Stable Code` |
| `edge.changelegacy.035` | `evidence.behavioral-data-fitness` | `prerequisite_for` | `metric-as-signal` | A metric claim is inadmissible when its history assumptions fail. | direct_support: `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis` |
| `edge.changelegacy.036` | `evidence.behavioral-data-fitness` | `prerequisite_for` | `evidence.change-coupling` | Logical entity and task history must be fit before co-change. | direct_support: `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Know the Biases and Workarounds for Behavioral Code Analysis` |
| `edge.changelegacy.037` | `evidence.behavioral-data-fitness` | `prerequisite_for` | `team-topology-force` | Aliases, pairing, squashes, and organization dates gate social inference. | direct_support: `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: #### Watch Out for Authors with Multiple Aliases`; `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ### Specify a Start Date with Organizational Significance` |
| `edge.changelegacy.038` | `evidence.change-coupling` | `nominates` | `domain.behavioral-boundary-candidate` | Co-change supplies candidate evidence and not a final semantic boundary. | direct_support: `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ## Discover Bounded Contexts Through Change Patterns` |
| `edge.changelegacy.039` | `domain.behavioral-boundary-candidate` | `does_not_entail` | `bounded-context` | A candidate becomes a Bounded Context only with semantic coherence and ownership. | derived_inference: `SRC-SDX: chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: ### The Big Win Is in the Problem Domain` |
| `edge.changelegacy.040` | `team-topology-force` | `provides_contextual_evidence_for` | `domain.behavioral-boundary-candidate` | Coordination may strengthen a boundary case only with semantic and operational evidence. | refinement: `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Combine Social and Technical Information` |
| `edge.changelegacy.041` | `team-topology-force` | `does_not_entail` | `distribution-readiness` | Separate teams do not by themselves earn separate services or repositories. | negative_support: `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: ## Distribution Won't Cure the Dependency Blues` |
| `edge.changelegacy.042` | `team-topology-force` | `must_not_feed` | `agent.behavioral-metrics-not-performance` | System/team risk evidence is never individual performance evidence. | direct_support: `SRC-SDX: chapters/013-chapter-7-beyond-conway-s-law.md :: ## Don't Turn Knowledge Maps into Performance Evaluations` |
| `edge.changelegacy.043` | `evidence.hotspot` | `provides_candidate_evidence_for` | `change.splinter-campaign` | A validated active congested hotspot can earn the campaign. | direct_support: `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Refactor Congested Code with the Splinter Pattern` |
| `edge.changelegacy.044` | `change.splinter-campaign` | `specializes` | `change.directional-campaign` | Splinter is one facade-preserving implementation of a broader directional campaign. | corroboration: `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters`; `SRC-REF: chapters/016-chapter-12-big-refactorings.md :: ## The Nature of the Game` |
| `edge.changelegacy.045` | `change.splinter-campaign` | `temporarily_preserves` | `change.compatibility-migration` | The old API facade delays independent caller migration. | direct_support: `SRC-SDX: chapters/009-chapter-4-pay-off-your-technical-debt.md :: ## Know the Consequences of Splinters` |
| `edge.changelegacy.046` | `evidence.logical-change-set` | `prerequisite_for_cross_repository` | `evidence.change-coupling` | Cross-repository coupling needs defensible task grouping. | direct_support: `SRC-SDX: chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: #### Use Logical Change Sets to Group Commits` |
| `edge.changelegacy.047` | `review.behavioral-early-warning` | `consumes` | `evidence.change-coupling` | Missing expected companion change may prompt review. | direct_support: `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Catch the Absence of Change` |
| `edge.changelegacy.048` | `review.behavioral-early-warning` | `consumes` | `evidence.complexity-trend` | A steep relative change may prompt early design review. | direct_support: `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Identify Steep Increases in Complexity` |
| `edge.changelegacy.049` | `review.behavioral-early-warning` | `does_not_entail` | `review.blocker` | Historical warnings must allow intentional divergence unless another contract makes them blocking. | direct_support: `SRC-SDX: chapters/016-chapter-10-an-extra-team-member-predictive-and-proactive-analyses.md :: ## Catch the Absence of Change` |
| `edge.changelegacy.050` | `agent.behavioral-metrics-not-performance` | `constrains_use_of` | `evidence.behavioral-data-fitness` | Even perfectly fit data lacks authority for individual scoring. | direct_support: `SRC-SDX: chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: ## The Situation Is Invisible in Code` |

## Coverage and provenance audit

### Canonical split and artifact counts

| Proposed final lane | Registry range | Concepts | Intended final use |
|---|---|---:|---|
| Core change and refactoring | `node.changelegacy.001`–`node.changelegacy.014` | 14 | Universal change control, refactoring proof obligations, abstraction/locality decisions, campaign control, and no-action decisions. |
| Legacy and testing | `node.changelegacy.015`–`node.changelegacy.026` | 12 | Poorly characterized systems, characterization surfaces, seams, test scope, provisional structures, and last-resort enabling edits. |
| Historical and sociotechnical evidence | `node.changelegacy.027`–`node.changelegacy.038` | 12 | Behavioral-code-analysis fitness, prioritization signals, coordination forces, boundary candidates, and review warnings. |
| **Total** |  | **38** | Each concept has the full Concept Record Schema and retrieval-routing fields. |

| Artifact class | Count | Audit result |
|---|---:|---|
| Canonical concept records | 38 | 38/38 contain every required concept and routing field; no duplicate concept IDs. |
| High-confidence prohibitions | 26 | Each prohibition carries an activation threshold, exception/limit, and exact support. |
| Material conflict records | 14 | Competing positions, assumptions, evidence gates, decision rules, unresolved questions, roles, and exact support are preserved. |
| Procedure refinements | 16 | Each includes inputs/evidence, deterministic steps, outputs, stop/escalation conditions, false positives, and exact support. |
| Graph node candidates | 38 | One graph candidate per canonical concept; aliases and formulation anchors are retained. |
| Typed graph edge candidates | 50 | Relation labels distinguish support, prerequisite, constraint, non-entailment, and other operational relations. |

### Corpus and locator coverage

| Source | Source role in this lane | Files read during extraction | Canonical contribution and contextual limit |
|---|---|---:|---|
| `SRC-REF` | refactoring foundation and mechanics | 21/21 | Defines behavior-preserving structural work, two-hat causal isolation, small verified transformations, tool criteria, and directional campaigns. Its 1999 object-oriented examples, language mechanics, and tooling assumptions are contextual rather than universal mandates. |
| `SRC-WELC` | safe change and legacy systems | 37/37 | Supplies characterization, effect reasoning, seams/enabling points, dependency-breaking, provisional structures, and hyperaware editing. C++, Java, C#, C, linker, and preprocessor mechanisms are implementation examples; their safety purpose is the portable doctrine. |
| `SRC-SDX` | historical, hotspot, and sociotechnical analysis | 22/22 | Supplies data fitness, hotspot/co-change/trend/age signals, team-topology evidence, splinter campaigns, and metric misuse prohibitions. Tool-specific workflows and numeric heuristics are contextual; correlation nominates investigation and does not prove causation or authorize action. |
| **Total** |  | **80/80** | Every supplied file in the three-source lane was read before canonicalization. |

- Mechanical provenance check: 140/140 unique `(source, chapter file, exact Markdown heading)` locators in this artifact resolve; zero files or headings are missing.
- Claims are canonical paraphrases. `direct_support`, `corroboration`, `refinement`, `derived_inference`, `tension`, and `negative_support` remain distinct; source silence is never counted as support.
- Cross-lane graph references `universal.minimize-simultaneous-uncertainty`, `universal.authority-discipline`, `bounded-context`, `distribution-readiness`, and `review.blocker` are integration targets, not concepts defined by this lane. Final graph assembly must resolve them against their owning canonical ledgers and must not create duplicate local definitions.
- The canonical count is intentionally smaller than the extraction candidate count: only operational synonyms were merged. Evidence signals remain separate from decisions, diagnostic hypotheses remain separate from remedies, and temporary safety mechanisms remain separate from durable design.
