# Claim-to-source entailment screening summary

Generated deterministically from `results.jsonl` by
`doctrine/tools/entailment_eval.py --summarize`. Do not edit by hand.

Each verdict is an observation of model output supporting an inference
about entailment. It is screening evidence, not verification and not
acceptance; it does not modify doctrine.

Records: 356 unique judgment keys (368 result lines).

## Verdict counts

| verdict | count |
|---|---|
| supported | 319 |
| partially_supported | 23 |
| not_supported | 13 |
| contradicted | 1 |

## Verdicts by source

| source | supported | partially_supported | not_supported | contradicted | insufficient_context | resolution_failed | unparseable | transport_error | quote_not_found | total |
|---|---|---|---|---|---|---|---|---|---|---|
| SRC-APOSD | 20 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 22 |
| SRC-CA | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 30 |
| SRC-CC | 26 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 34 |
| SRC-DDD | 48 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 49 |
| SRC-EGO | 45 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 47 |
| SRC-FP | 40 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 46 |
| SRC-FSA | 31 | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 36 |
| SRC-PP | 19 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 |
| SRC-REF | 18 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 19 |
| SRC-SDX | 24 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 30 |
| SRC-WELC | 18 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 23 |

## Flagged entries (negative, incomplete, or invalid screening evidence)

- `not_supported` — concept `agent-conduct-authority-bounded-action` — `books/code-complete-2nd-edition-v413hav/chapters/038-chapter-28-managing-construction.md :: Requirements and Design Changes`
- `not_supported` — concept `architecture-contextual-style-selection` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/024-chapter-18-choosing-the-appropriate-architecture-style.md :: Shifting "Fashion" in Architecture`
- `not_supported` — concept `architecture-distribution-readiness` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/015-chapter-9-foundations.md :: Other Distributed Considerations`
- `not_supported` — concept `architecture-earned-boundary` — `books/oreilly-fundamentals-of-software-architecture-2020-1/chapters/013-chapter-8-component-based-thinking.md :: Component Granularity`
- `contradicted` — concept `implementation-explicit-failure-policy` — `books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217/chapters/015-10-define-errors-out-of-existence.md :: 10: Define Errors Out Of Existence`
- `not_supported` — concept `implementation-fail-fast-or-recover` — `books/dokumen-pub-a-philosophy-of-software-design-2nd-edition-2nbsped-173210221x-9781732102217/chapters/015-10-define-errors-out-of-existence.md :: 10: Define Errors Out Of Existence`
- `not_supported` — concept `implementation-risk-driven-tests` — `books/code-complete-2nd-edition-v413hav/chapters/031-chapter-22-developer-testing.md :: 22.3 Bag of Testing Tricks`
- `not_supported` — concept `legacy-seams-and-enabling-points` — `books/programming-working-effectively-with-legacy-code/chapters/011-chapter-4-the-seam-model.md :: Seam Types`
- `not_supported` — concept `legacy-unprotected-enabling-edit` — `books/programming-working-effectively-with-legacy-code/chapters/031-chapter-23-how-do-i-know-that-i-m-not-breaking-anything.md :: Hyperaware Editing`
- `not_supported` — concept `python-runtime-static-boundary` — `books/fluent-python-2nd-edition-z-lib-org/chapters/022-chapter-15-more-about-type-hints.md :: TypedDict`
- `not_supported` — concept `python-streaming-iteration` — `books/fluent-python-2nd-edition-z-lib-org/chapters/024-chapter-17-iterables-iterators-and-generators.md :: Don't make the iterable an iterator for itself`
- `not_supported` — concept `repository-assessment-behavioral-boundary-candidate` — `books/dokumen-pub-software-design-x-rays-fix-technical-debt-with-behavioral-code-analysis-1nbsped-1680502727-978-1680502725/chapters/014-chapter-8-toward-modular-monoliths-through-the-social-view-of-code.md :: The Big Win Is in the Problem Domain`
- `not_supported` — concept `testing-coverage-is-not-adequacy` — `books/code-complete-2nd-edition-v413hav/chapters/031-chapter-22-developer-testing.md :: Coverage Monitors`
- `not_supported` — concept `universal-local-reasoning` — `books/code-complete-2nd-edition-v413hav/chapters/011-chapter-5-design-in-construction.md :: Software's Primary Technical Imperative: Managing Complexity`

## Locator-resolution failures

None.

## Latency

Mean latency over 356 model-judged records: 45.93s.
