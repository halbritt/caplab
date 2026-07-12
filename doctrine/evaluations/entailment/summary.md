# Claim-to-source entailment screening summary

Generated deterministically from `results.jsonl` by
`doctrine/tools/entailment_eval.py --summarize`. Do not edit by hand.

Each verdict is an observation of model output supporting an inference
about entailment. It is screening evidence, not verification and not
acceptance; it does not modify doctrine.

Records: 1762 unique judgment keys (1780 result lines).

## Verdict counts

| verdict | count |
|---|---|
| supported | 1487 |
| partially_supported | 140 |
| not_supported | 21 |
| contradicted | 4 |
| insufficient_context | 4 |
| unparseable | 1 |
| quote_not_found | 105 |

## Verdicts by source

| source | supported | partially_supported | not_supported | contradicted | insufficient_context | resolution_failed | unparseable | transport_error | quote_not_found | total |
|---|---|---|---|---|---|---|---|---|---|---|
| SRC-APOSD | 83 | 2 | 1 | 1 | 1 | 0 | 0 | 0 | 2 | 90 |
| SRC-CA | 130 | 4 | 1 | 1 | 0 | 0 | 0 | 0 | 5 | 141 |
| SRC-CC | 106 | 16 | 6 | 2 | 0 | 0 | 0 | 0 | 11 | 141 |
| SRC-DDD | 192 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 209 |
| SRC-EGO | 148 | 19 | 2 | 0 | 3 | 0 | 0 | 0 | 18 | 190 |
| SRC-FP | 167 | 9 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 184 |
| SRC-FSA | 137 | 20 | 4 | 0 | 0 | 0 | 0 | 0 | 10 | 171 |
| SRC-PP | 70 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 83 |
| SRC-REF | 71 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 77 |
| SRC-RI | 140 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 158 |
| SRC-SDX | 100 | 19 | 2 | 0 | 0 | 0 | 1 | 0 | 9 | 131 |
| SRC-UT | 77 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 88 |
| SRC-WELC | 66 | 21 | 3 | 0 | 0 | 0 | 0 | 0 | 9 | 99 |

## Flagged entries (negative, incomplete, or invalid screening evidence)

- `not_supported` — concept `agent-conduct-authority-bounded-action` — `books/code-complete-2nd-edition-v413hav/chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: Boss-Readiness Test`
- `not_supported` — concept `agent-conduct-authority-bounded-action` — `books/code-complete-2nd-edition-v413hav/chapters/008-chapter-3-measure-twice-cut-once-upstream-prerequisites.md :: Boss-Readiness Test`
- `not_supported` — concept `agent-conduct-authority-bounded-action` — `books/code-complete-2nd-edition-v413hav/chapters/038-chapter-28-managing-construction.md :: Requirements and Design Changes`
- `quote_not_found` — concept `agent-conduct-authority-bounded-action` — `books/code-complete-2nd-edition-v413hav/chapters/038-chapter-28-managing-construction.md :: Requirements and Design Changes`
- `quote_not_found` — concept `agent-conduct-authority-bounded-action` — `books/the-pragmatic-programmer/chapters/006-chapter-1-a-pragmatic-philosophy.md :: Take Responsibility`
- `quote_not_found` — concept `architecture-boundary-strength` — `books/clean-architecture-a-craftsman-guide-to-software-structure-and-design/chapters/029-chapter-18-boundary-anatomy.md :: BOUNDARY CROSSING`
- `quote_not_found` — concept `architecture-boundary-strength` — `books/clean-architecture-a-craftsman-guide-to-software-structure-and-design/chapters/035-chapter-24-partial-boundaries.md :: FACADES`
- `quote_not_found` — concept `architecture-boundary-strength` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: Monolith versus distributed`
- `not_supported` — concept `architecture-contextual-style-selection` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: Shifting "Fashion" in Architecture`
- `not_supported` — concept `architecture-distribution-readiness` — `books/clean-architecture-a-craftsman-guide-to-software-structure-and-design/chapters/038-chapter-27-services-great-and-small.md :: THE DECOUPLING FALLACY`
- `not_supported` — concept `architecture-distribution-readiness` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/015-chapter-9-foundations.md :: Other Distributed Considerations`
- `quote_not_found` — concept `architecture-distribution-readiness` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/015-chapter-9-foundations.md :: Other Distributed Considerations`
- `quote_not_found` — concept `architecture-distribution-readiness` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/015-chapter-9-foundations.md :: Other Distributed Considerations`
- `quote_not_found` — concept `architecture-earned-boundary` — `books/clean-architecture-a-craftsman-guide-to-software-structure-and-design/chapters/028-chapter-17-boundaries-drawing-lines.md :: WHICH LINES DO YOU DRAW, AND WHEN DO YOU DRAW THEM?`
- `quote_not_found` — concept `architecture-earned-boundary` — `books/clean-architecture-a-craftsman-guide-to-software-structure-and-design/chapters/028-chapter-17-boundaries-drawing-lines.md :: WHICH LINES DO YOU DRAW, AND WHEN DO YOU DRAW THEM?`
- `not_supported` — concept `architecture-earned-boundary` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/013-chapter-8-component-based-thinking.md :: Component Granularity`
- `quote_not_found` — concept `architecture-earned-boundary` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/013-chapter-8-component-based-thinking.md :: Component Granularity`
- `quote_not_found` — concept `architecture-event-temporal-semantics` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/020-chapter-14-event-driven-architecture-style.md :: Error Handling`
- `quote_not_found` — concept `architecture-event-temporal-semantics` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/020-chapter-14-event-driven-architecture-style.md :: Preventing Data Loss`
- `quote_not_found` — concept `architecture-interaction-synchrony` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/020-chapter-14-event-driven-architecture-style.md :: Choosing Between Request-Based and Event-Based`
- `not_supported` — concept `architecture-metrics-as-signals` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/011-chapter-6-measuring-and-governing-architecture-characteristics.md :: They aren't physics`
- `quote_not_found` — concept `architecture-scoped-characteristics` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/009-chapter-4-architecture-characteristics-defined.md :: Influences some structural aspect of the design`
- `quote_not_found` — concept `architecture-scoped-characteristics` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/012-chapter-7-scope-of-architecture-characteristics.md :: Architectural Quanta and Granularity`
- `quote_not_found` — concept `architecture-selective-option-preservation` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/024-chapter-16-adaptation.md :: System Architecture`
- `quote_not_found` — concept `architecture-structural-constraint-enforcement` — `books/clean-architecture-a-craftsman-guide-to-software-structure-and-design/chapters/046-chapter-34-the-missing-chapter.md :: ENCAPSULATION`
- `quote_not_found` — concept `debugging-causal-repair` — `books/code-complete-2nd-edition-v413hav/chapters/032-chapter-23-debugging.md :: 23.3 Fixing a Defect`
- `quote_not_found` — concept `debugging-hypothesis-led-investigation` — `books/code-complete-2nd-edition-v413hav/chapters/032-chapter-23-debugging.md :: The Scientific Method of Debugging`
- `quote_not_found` — concept `debugging-hypothesis-led-investigation` — `books/code-complete-2nd-edition-v413hav/chapters/032-chapter-23-debugging.md :: The Scientific Method of Debugging`
- `quote_not_found` — concept `domain-aggregate-invariant-boundary` — `books/domain-driven-design-tackling-complexity-in-the-heart-of-software-eric-evans/chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: Aggregates`
- `contradicted` — concept `domain-anticorruption-layer` — `books/clean-architecture-a-craftsman-guide-to-software-structure-and-design/chapters/035-chapter-24-partial-boundaries.md :: FACADES`
- `quote_not_found` — concept `domain-bounded-context` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/024-chapter-16-adaptation.md :: Information Architecture`
- `quote_not_found` — concept `domain-context-relationship-selection` — `books/domain-driven-design-tackling-complexity-in-the-heart-of-software-eric-evans/chapters/016-chapter-14-maintaining-model-integrity.md :: Choosing Your Model Context Strategy`
- `quote_not_found` — concept `domain-core-domain-priority` — `books/domain-driven-design-tackling-complexity-in-the-heart-of-software-eric-evans/chapters/017-chapter-15-distillation.md :: Generic Subdomains`
- `quote_not_found` — concept `domain-factory-lifecycle` — `books/domain-driven-design-tackling-complexity-in-the-heart-of-software-eric-evans/chapters/007-chapter-6-the-life-cycle-of-a-domain-object.md :: Factories`
- `quote_not_found` — concept `domain-language-model-loop` — `books/domain-driven-design-tackling-complexity-in-the-heart-of-software-eric-evans/chapters/004-chapter-3-binding-model-and-implementation.md :: Model-Driven Design`
- `quote_not_found` — concept `go-bounded-concurrency` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: Adding Concurrency Should Be One of Our Last Deliberate Optimizations to Try`
- `quote_not_found` — concept `go-bounded-concurrency` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/014-chapter-10-optimization-examples.md :: A Worker Approach Without Coordination (Sharding)`
- `not_supported` — concept `go-explicit-contextual-errors` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/006-chapter-2-efficient-introduction-to-go.md :: How to Wrap Errors?`
- `not_supported` — concept `go-explicit-contextual-errors` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/006-chapter-2-efficient-introduction-to-go.md :: How to Wrap Errors?`
- `quote_not_found` — concept `go-explicit-contextual-errors` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/006-chapter-2-efficient-introduction-to-go.md :: Never Ignore Errors!`
- `quote_not_found` — concept `go-goroutine-resource-lifecycle` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/015-chapter-11-optimization-patterns.md :: Control the Lifecycle of Your Goroutines`
- `quote_not_found` — concept `go-goroutine-resource-lifecycle` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/015-chapter-11-optimization-patterns.md :: Control the Lifecycle of Your Goroutines`
- `quote_not_found` — concept `go-goroutine-resource-lifecycle` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/015-chapter-11-optimization-patterns.md :: Reliably Close Things`
- `quote_not_found` — concept `go-goroutine-resource-lifecycle` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/015-chapter-11-optimization-patterns.md :: Reliably Close Things`
- `quote_not_found` — concept `go-semantics-before-performance-constructs` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/006-chapter-2-efficient-introduction-to-go.md :: Generic Code Will Be Faster?`
- `quote_not_found` — concept `go-semantics-before-performance-constructs` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/006-chapter-2-efficient-introduction-to-go.md :: Generic Code Will Be Faster?`
- `quote_not_found` — concept `go-semantics-before-performance-constructs` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/006-chapter-2-efficient-introduction-to-go.md :: Generic Code Will Be Faster?`
- `contradicted` — concept `implementation-duplication-as-evidence` — `books/code-complete-2nd-edition-v413hav/chapters/013-chapter-7-high-quality-routines.md :: 7.1 Valid Reasons to Create a Routine`
- `contradicted` — concept `implementation-duplication-as-evidence` — `books/code-complete-2nd-edition-v413hav/chapters/013-chapter-7-high-quality-routines.md :: 7.1 Valid Reasons to Create a Routine`
- `quote_not_found` — concept `implementation-duplication-as-evidence` — `books/the-pragmatic-programmer/chapters/007-chapter-2-a-pragmatic-approach.md :: **7** The Evils of Duplication`
- `quote_not_found` — concept `implementation-explicit-failure-policy` — `books/code-complete-2nd-edition-v413hav/chapters/014-chapter-8-defensive-programming.md :: 8.3 Error-Handling Techniques`
- `contradicted` — concept `implementation-explicit-failure-policy` — `books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217/chapters/015-10-define-errors-out-of-existence.md :: 10: Define Errors Out Of Existence`
- `insufficient_context` — concept `implementation-explicit-failure-policy` — `books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217/chapters/015-10-define-errors-out-of-existence.md :: 10: Define Errors Out Of Existence`
- `quote_not_found` — concept `implementation-explicit-failure-policy` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/015-chapter-9-interconnect.md :: Migratory Virtual IP Addresses`
- `quote_not_found` — concept `implementation-explicit-failure-policy` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/015-chapter-9-interconnect.md :: Migratory Virtual IP Addresses`
- `not_supported` — concept `implementation-fail-fast-or-recover` — `books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217/chapters/015-10-define-errors-out-of-existence.md :: 10: Define Errors Out Of Existence`
- `quote_not_found` — concept `implementation-minimal-coherent-api` — `books/code-complete-2nd-edition-v413hav/chapters/013-chapter-7-high-quality-routines.md :: 7.5 How to Use Routine Parameters`
- `quote_not_found` — concept `implementation-minimal-coherent-api` — `books/code-complete-2nd-edition-v413hav/chapters/013-chapter-7-high-quality-routines.md :: 7.5 How to Use Routine Parameters`
- `quote_not_found` — concept `implementation-normal-result-or-exception` — `books/code-complete-2nd-edition-v413hav/chapters/014-chapter-8-defensive-programming.md :: 8.4 Exceptions`
- `quote_not_found` — concept `implementation-readiness` — `books/the-pragmatic-programmer/chapters/012-chapter-7-before-the-project.md :: **36** The Requirements Pit`
- `quote_not_found` — concept `implementation-representation-fit` — `books/fluent-python-2nd-edition-z-lib-org/chapters/007-chapter-2-an-array-of-sequences.md :: When a List Is Not the Answer`
- `not_supported` — concept `implementation-risk-driven-tests` — `books/code-complete-2nd-edition-v413hav/chapters/031-chapter-22-developer-testing.md :: 22.3 Bag of Testing Tricks`
- `quote_not_found` — concept `implementation-risk-driven-tests` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/011-chapter-5-mocks-and-test-fragility.md :: 5.2 Observable behavior vs. implementation details`
- `quote_not_found` — concept `implementation-risk-driven-tests` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/011-chapter-5-mocks-and-test-fragility.md :: 5.2 Observable behavior vs. implementation details`
- `quote_not_found` — concept `implementation-risk-driven-tests` — `books/the-pragmatic-programmer/chapters/013-chapter-8-pragmatic-projects.md :: What to Test`
- `quote_not_found` — concept `implementation-risk-driven-tests` — `books/the-pragmatic-programmer/chapters/013-chapter-8-pragmatic-projects.md :: What to Test`
- `quote_not_found` — concept `legacy-characterization-surfaces` — `books/programming-working-effectively-with-legacy-code/chapters/004-preface.md :: Preface`
- `quote_not_found` — concept `legacy-effect-surface` — `books/programming-working-effectively-with-legacy-code/chapters/019-chapter-11-i-need-to-make-a-change-what-methods-should-i-test.md :: Effect Propagation`
- `quote_not_found` — concept `legacy-provisional-dependency-break` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/009-chapter-4-pay-off-your-technical-debt.md :: Signal Incompleteness with Names`
- `quote_not_found` — concept `legacy-provisional-dependency-break` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/009-chapter-4-pay-off-your-technical-debt.md :: Signal Incompleteness with Names`
- `quote_not_found` — concept `legacy-provisional-dependency-break` — `books/programming-working-effectively-with-legacy-code/chapters/009-chapter-2-working-with-feedback.md :: Break Dependencies`
- `not_supported` — concept `legacy-seams-and-enabling-points` — `books/programming-working-effectively-with-legacy-code/chapters/011-chapter-4-the-seam-model.md :: Seam Types`
- `quote_not_found` — concept `legacy-sensing-and-separation` — `books/programming-working-effectively-with-legacy-code/chapters/010-chapter-3-sensing-and-separation.md :: Chapter 3: Sensing and Separation`
- `quote_not_found` — concept `legacy-sensing-and-separation` — `books/programming-working-effectively-with-legacy-code/chapters/010-chapter-3-sensing-and-separation.md :: Chapter 3: Sensing and Separation`
- `not_supported` — concept `legacy-unprotected-enabling-edit` — `books/programming-working-effectively-with-legacy-code/chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: Hyperaware Editing`
- `not_supported` — concept `legacy-unprotected-enabling-edit` — `books/programming-working-effectively-with-legacy-code/chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: Hyperaware Editing`
- `quote_not_found` — concept `legacy-unprotected-enabling-edit` — `books/programming-working-effectively-with-legacy-code/chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: Lean on the Compiler`
- `quote_not_found` — concept `legacy-unprotected-enabling-edit` — `books/programming-working-effectively-with-legacy-code/chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: Lean on the Compiler`
- `quote_not_found` — concept `operations-automation-safeguards` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/009-chapter-4-stability-antipatterns.md :: Force Multiplier`
- `quote_not_found` — concept `operations-bounded-accumulation` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/010-chapter-5-stability-patterns.md :: Steady State`
- `quote_not_found` — concept `operations-cascading-failure-halting` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/009-chapter-4-stability-antipatterns.md :: Cascading Failures`
- `quote_not_found` — concept `operations-chaos-experiment-discipline` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/025-chapter-17-chaos-engineering.md :: Injecting Chaos`
- `quote_not_found` — concept `operations-designed-failure-modes` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/008-chapter-3-stabilize-your-system.md :: Chain of Failure`
- `quote_not_found` — concept `operations-ephemeral-instance-design` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/013-chapter-7-foundations.md :: Virtual Machines in the Data Center`
- `quote_not_found` — concept `operations-integration-point-distrust` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/009-chapter-4-stability-antipatterns.md :: Integration Points`
- `quote_not_found` — concept `operations-synchronized-demand-dispersion` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/009-chapter-4-stability-antipatterns.md :: Dogpile`
- `quote_not_found` — concept `operations-zero-downtime-rollout` — `books/release-it-design-and-deploy-production-ready-software-pdfdrive/chapters/020-chapter-13-design-for-deployment.md :: Phases of Deployment`
- `quote_not_found` — concept `performance-cache-validity` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/015-chapter-11-optimization-patterns.md :: Reuse Memory`
- `quote_not_found` — concept `performance-cache-validity` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/015-chapter-11-optimization-patterns.md :: Reuse Memory`
- `quote_not_found` — concept `performance-cache-validity` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/015-chapter-11-optimization-patterns.md :: Reuse Memory`
- `quote_not_found` — concept `performance-cache-validity` — `books/fluent-python-2nd-edition-z-lib-org/chapters/030-chapter-23-dynamic-attributes-and-properties.md :: Step 4: Bespoke Property Cache`
- `quote_not_found` — concept `performance-earned-bounded-concurrency` — `books/fluent-python-2nd-edition-z-lib-org/chapters/029-chapter-22-asynchronous-programming.md :: Using asyncio.as_completed and a semaphore`
- `quote_not_found` — concept `performance-experiment-level-fit` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: Microbenchmarks Versus Memory Management`
- `quote_not_found` — concept `performance-measurable-objective` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/005-chapter-1-software-efficiency-matters.md :: Clarify When Someone Uses the Word "Performance"`
- `quote_not_found` — concept `performance-measurable-objective` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/007-chapter-3-conquering-efficiency.md :: Resource-Aware Efficiency Requirements`
- `quote_not_found` — concept `performance-memory-lifecycle` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: Microbenchmarks Versus Memory Management`
- `insufficient_context` — concept `performance-profile-causal-bottleneck` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: Root Cause Analysis, but for Efficiency`
- `insufficient_context` — concept `performance-profile-causal-bottleneck` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: Root Cause Analysis, but for Efficiency`
- `insufficient_context` — concept `performance-profile-causal-bottleneck` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: Root Cause Analysis, but for Efficiency`
- `quote_not_found` — concept `performance-representative-baseline` — `books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library/chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: Reliability of Experiments`
- `quote_not_found` — concept `python-dynamic-mechanism-escalation` — `books/fluent-python-2nd-edition-z-lib-org/chapters/032-chapter-25-class-metaprogramming.md :: Modern Features Simplify or Replace Metaclasses`
- `quote_not_found` — concept `python-inheritance-constraints` — `books/fluent-python-2nd-edition-z-lib-org/chapters/021-chapter-14-inheritance-for-good-or-for-worse.md :: Multiple Inheritance and Method Resolution Order`
- `quote_not_found` — concept `python-representation-fit` — `books/fluent-python-2nd-edition-z-lib-org/chapters/008-chapter-3-dictionaries-and-sets.md :: Practical Consequences of How dict Works`
- `not_supported` — concept `python-runtime-static-boundary` — `books/fluent-python-2nd-edition-z-lib-org/chapters/022-chapter-15-more-about-type-hints.md :: TypedDict`
- `not_supported` — concept `python-streaming-iteration` — `books/fluent-python-2nd-edition-z-lib-org/chapters/024-chapter-17-iterables-iterators-and-generators.md :: Don't make the iterable an iterator for itself`
- `quote_not_found` — concept `refactoring-directional-campaign` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: The Trade-Off Between Architectural Refinements and Replacement Systems`
- `quote_not_found` — concept `refactoring-hotspot-prioritization` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: Prioritize Technical Debt with Hotspots`
- `not_supported` — concept `refactoring-splinter-campaign` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/009-chapter-4-pay-off-your-technical-debt.md :: Refactor Congested Code with the Splinter Pattern`
- `quote_not_found` — concept `refactoring-transformation-tool-trust` — `books/programming-working-effectively-with-legacy-code/chapters/030-chapter-22-i-need-to-change-a-monster-method-and-i-can-t-write-tests-for-it.md :: Tackling Monsters with Automated Refactoring Support`
- `quote_not_found` — concept `refactoring-transformation-tool-trust` — `books/refactoring-improving-the-design-of-existing-code/chapters/019-chapter-14-refactoring-tools.md :: Accuracy`
- `not_supported` — concept `repository-assessment-behavioral-boundary-candidate` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: The Big Win Is in the Problem Domain`
- `quote_not_found` — concept `repository-assessment-behavioral-data-fitness` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/013-chapter-7-beyond-conway-s-law.md :: Watch Out for Authors with Multiple Aliases`
- `quote_not_found` — concept `repository-assessment-code-age` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/010-chapter-5-the-principles-of-code-age.md :: Dead Code Is Stable Code`
- `unparseable` — concept `repository-assessment-code-age` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/010-chapter-5-the-principles-of-code-age.md :: Dead Code Is Stable Code`
- `quote_not_found` — concept `repository-assessment-complexity-trend` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/007-chapter-2-identify-code-with-high-interest-rates.md :: Evaluate Hotspots with Complexity Trends`
- `quote_not_found` — concept `repository-assessment-logical-change-set` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/015-chapter-9-systems-of-systems-analyzing-multiple-repositories-and-microservices.md :: Use Logical Change Sets to Group Commits`
- `quote_not_found` — concept `repository-assessment-metrics-not-performance` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/017-appendix-a1-the-hazards-of-productivity-and-performance-metrics.md :: Adaptive Behavior and the Destruction of a Data Source`
- `quote_not_found` — concept `testing-assert-observable-outcomes` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/010-chapter-4-the-four-pillars-of-a-good-unit-test.md :: 4.1 Diving into the four pillars of a good unit test`
- `quote_not_found` — concept `testing-assert-observable-outcomes` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/010-chapter-4-the-four-pillars-of-a-good-unit-test.md :: 4.2 The intrinsic connection between the first two attributes`
- `not_supported` — concept `testing-coverage-is-not-adequacy` — `books/code-complete-2nd-edition-v413hav/chapters/031-chapter-22-developer-testing.md :: Coverage Monitors`
- `quote_not_found` — concept `testing-coverage-is-not-adequacy` — `books/code-complete-2nd-edition-v413hav/chapters/031-chapter-22-developer-testing.md :: Coverage Monitors`
- `quote_not_found` — concept `testing-design-before-feature-tests` — `books/code-complete-2nd-edition-v413hav/chapters/011-chapter-5-design-in-construction.md :: How Much Design Is Enough?`
- `quote_not_found` — concept `testing-humble-object-testability-split` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/013-chapter-7-refactoring-toward-valuable-unit-tests.md :: 7.1.1 The four types of code`
- `quote_not_found` — concept `testing-humble-object-testability-split` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/013-chapter-7-refactoring-toward-valuable-unit-tests.md :: 7.4 Handling conditional logic in controllers`
- `quote_not_found` — concept `testing-no-test-privileged-access` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/019-chapter-11-unit-testing-anti-patterns.md :: 11.5 Mocking concrete classes`
- `quote_not_found` — concept `testing-self-contained-test-anatomy` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/008-chapter-3-the-anatomy-of-a-unit-test.md :: 3.1 How to structure a unit test`
- `quote_not_found` — concept `testing-shared-dependency-substitution` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/007-chapter-2-what-is-a-unit-test.md :: 2.1 The definition of "unit test"`
- `quote_not_found` — concept `testing-suite-net-value` — `books/manning-unit-testing-principles-practices-and-patterns-2020-1/chapters/006-chapter-1-the-goal-of-unit-testing.md :: 1.4 What makes a successful test suite?`
- `quote_not_found` — concept `universal-earned-abstraction` — `books/the-pragmatic-programmer/chapters/007-chapter-2-a-pragmatic-approach.md :: The Evils of Duplication`
- `quote_not_found` — concept `universal-explicit-invariants` — `books/code-complete-2nd-edition-v413hav/chapters/014-chapter-8-defensive-programming.md :: 8.2 Assertions`
- `quote_not_found` — concept `universal-information-hiding` — `books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217/chapters/010-5-information-hiding-and-leakage.md :: 5: Information Hiding (and Leakage)`
- `not_supported` — concept `universal-local-reasoning` — `books/code-complete-2nd-edition-v413hav/chapters/011-chapter-5-design-in-construction.md :: Software's Primary Technical Imperative: Managing Complexity`
- `quote_not_found` — concept `universal-preserve-behavior-by-default` — `books/programming-working-effectively-with-legacy-code/chapters/008-chapter-1-changing-software.md :: Four Reasons to Change Software`
- `quote_not_found` — concept `universal-repository-contract-precedence` — `books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217/chapters/022-17-consistency.md :: 17: Consistency`
- `quote_not_found` — concept `universal-reversible-reviewable-change` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/026-chapter-19-architecture-decisions.md :: Covering Your Assets Anti-Pattern`

## Locator-resolution failures

None.

## Latency

Mean latency over 1758 model-judged records: 31.20s.
