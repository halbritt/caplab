# Part 1 — retrieval, 2026-07-29

Does each scenario's task text cause Pincite to serve the concept it was built for?

Deterministic, offline, trace disabled. **Zero model calls.** Pinned release `corpus-2026-07-12-a11702cc9217`; role `coding-agent`, task `defect-repair`, question only.

## Result: **0 / 18**

Eighteen eligible scenarios, none served its own concept. Two of the twenty are always-load (`universal-evidence-before-intervention`, `universal-separate-semantic-structural-change`): they appear in every packet regardless of query, so retrieval cannot fail to serve them and part 1 is undefined.

| # | scenario | target concept | served |
|---:|---|---|:--:|
| 1 | `01-data-single-authority-change-propagation` | `data-single-authority-change-propagation` | miss |
| 2 | `02-domain-anticorruption-layer` | `domain-anticorruption-layer` | miss |
| 3 | `03-domain-factory-lifecycle` | `domain-factory-lifecycle` | miss |
| 4 | `04-domain-service-operation` | `domain-service-operation` | miss |
| 5 | `05-go-explicit-contextual-errors` | `go-explicit-contextual-errors` | miss |
| 6 | `06-go-goroutine-resource-lifecycle` | `go-goroutine-resource-lifecycle` | miss |
| 7 | `07-implementation-attention-budget-presentation` | `implementation-attention-budget-presentation` | miss |
| 8 | `08-implementation-error-surface-reduction` | `implementation-error-surface-reduction` | miss |
| 9 | `09-implementation-minimal-coherent-api` | `implementation-minimal-coherent-api` | miss |
| 10 | `10-legacy-provisional-safety-net` | `legacy-provisional-safety-net` | miss |
| 11 | `11-operations-contract-conformance-testing` | `operations-contract-conformance-testing` | miss |
| 12 | `12-operations-ephemeral-instance-design` | `operations-ephemeral-instance-design` | miss |
| 13 | `13-operations-synchronized-demand-dispersion` | `operations-synchronized-demand-dispersion` | miss |
| 14 | `14-python-compatible-property-evolution` | `python-compatible-property-evolution` | miss |
| 15 | `15-refactoring-demonstrated-pressure` | `refactoring-demonstrated-pressure` | miss |
| 16 | `16-testing-database-production-fidelity` | `testing-database-production-fidelity` | miss |
| 17 | `17-testing-shared-dependency-substitution` | `testing-shared-dependency-substitution` | miss |
| 18 | `18-universal-earned-abstraction` | `universal-earned-abstraction` | miss |
| 19 | `19-universal-evidence-before-intervention` | `universal-evidence-before-intervention` | n/a |
| 20 | `20-universal-separate-semantic-structural-change` | `universal-separate-semantic-structural-change` | n/a |

## Why this measurement is trustworthy

- **Slate is representative, not chosen.** 20 concepts drawn from 227 with `random.seed(20260729)`.
- **Task text authored blind.** Authors received claim, decision_rule, why_it_matters, common_failure_modes and counterexamples; `retrieval_terms` and `routing` were withheld structurally, not by instruction.
- **Scored on eligibility.** Always-load concepts excluded; scoring against the whole packet would make any of them a trivial hit.
- **Tasks are rich.** 87–105 words with reproduction steps, not terse subjects.

## Relation to prior measurements

| instrument | recall |
|---|---|
| retro-replay, terse commit subjects (2026-07-22) | 3/24 = 12.5% |
| ten ad-hoc queries (2026-07-25) | 0/10 |
| re-baseline of 11 ranking-miss rows, current corpus | 5/11 |
| **this slate, blind-authored, representative** | **0/18** |

The retro-replay caveated 12.5% as a lower bound tied to minimal-context queries. These tasks are an order of magnitude richer and recall is zero. **Query richness is not the deficit.**

## Consequence for part 2

The hit stratum is empty, so retrieval-versus-none has nothing to measure on this slate. Part 2 reduces to **injection versus none** — does the concept change behaviour when delivered — which needs no retrieval and is the contrast the owner's own titration ran.
