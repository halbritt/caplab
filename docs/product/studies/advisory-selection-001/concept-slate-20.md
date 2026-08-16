# Doctrine sample — 20 concepts

Random sample of **20** from **227** concepts in `halbritt/pincite` `doctrine/concepts/*.yaml`.

Drawn 2026-07-29 with `random.seed(20260729)` and `random.sample`, so the selection is reproducible. Sorted by category then id for reading; the draw itself was unordered.

| # | id | category |
|---:|---|---|
| 1 | `data-single-authority-change-propagation` | data |
| 2 | `domain-anticorruption-layer` | domain |
| 3 | `domain-factory-lifecycle` | domain |
| 4 | `domain-service-operation` | domain |
| 5 | `go-explicit-contextual-errors` | go |
| 6 | `go-goroutine-resource-lifecycle` | go |
| 7 | `implementation-attention-budget-presentation` | implementation |
| 8 | `implementation-error-surface-reduction` | implementation |
| 9 | `implementation-minimal-coherent-api` | implementation |
| 10 | `legacy-provisional-safety-net` | legacy |
| 11 | `operations-contract-conformance-testing` | operations |
| 12 | `operations-ephemeral-instance-design` | operations |
| 13 | `operations-synchronized-demand-dispersion` | operations |
| 14 | `python-compatible-property-evolution` | python |
| 15 | `refactoring-demonstrated-pressure` | refactoring |
| 16 | `testing-database-production-fidelity` | testing |
| 17 | `testing-shared-dependency-substitution` | testing |
| 18 | `universal-earned-abstraction` | universal |
| 19 | `universal-evidence-before-intervention` | universal |
| 20 | `universal-separate-semantic-structural-change` | universal |

---

## 1. `data-single-authority-change-propagation`

**Synchronize derived systems from one change authority**  
_category: data · languages: language-independent_

**Claim**

Propagate changes to derived systems from one ordering authority rather than independent dual writes; make downstream lag, replay, schema, and recovery semantics explicit.

**Decision rule**

Commit each fact first through one ordering authority, derive downstream changes from its durable change stream, and specify bootstrap snapshot, offset, schema, lag, replay, idempotence, and recovery behavior; reject independent dual writes for the same fact.

**Why it matters**

Independent writes to a database and an index or cache can succeed in different orders or only partly, creating permanent divergence even when neither system reports an error.

**Common failure modes**

- dual-write race
- partial cross-system update
- snapshot-log gap
- consumer schema break
- unbounded lag

**Counterexamples**

- An audit service may author its own observation that references a transaction without being a derived copy of the transaction record.

**Activation signals**

- dual write
- CDC connector
- outbox table
- search-index sync
- cache invalidation stream

---

## 2. `domain-anticorruption-layer`

**Earn an Anticorruption Layer from semantic conflict**  
_category: domain · languages: language-independent_

**Claim**

An Anticorruption Layer protects a valuable local model from a necessary, materially different foreign or legacy model through explicit semantic translation; it is not merely a transport client or generic facade.

**Decision rule**

Verify required integration, concrete model conflict, local-model value, and ownership limits; compare Conformist, direct integration, Separate Ways, and translation; build local services, adapters, and translators only when semantic protection exceeds mapping and operational cost.

**Why it matters**

Foreign concepts can corrupt core meaning, but unnecessary translation creates a third model, duplicate data, latency, and permanent maintenance burden.

**Common failure modes**

- translation swamp
- third accidental model
- stale identity mapping
- unbounded bidirectional coupling

**Counterexamples**

- A stable standards-based value format shared by both contexts may need a direct adapter rather than a full Anticorruption Layer.

**Activation signals**

- legacy API
- foreign model leakage
- translator
- vendor schema
- phased retirement

---

## 3. `domain-factory-lifecycle`

**Use Factory only for complex valid creation**  
_category: domain · languages: language-independent_

**Claim**

A Factory is justified only when creation or reconstitution must establish a complex valid whole or lifecycle transition that a clear constructor cannot express safely.

**Decision rule**

Identify invariants that must hold at creation, distinguish new creation from reconstitution, use the simplest constructor when sufficient, and place Factory behavior where domain meaning and identity generation remain explicit.

**Why it matters**

Factories can protect invariant construction, but routine factory layers hide novelty, failure, identity, and lifecycle behind unnecessary indirection.

**Common failure modes**

- factory ceremony
- invalid partially built object
- hidden identity creation
- confused reconstitution

**Counterexamples**

- A small immutable Value Object with one validation rule normally needs only a validating constructor.

**Activation signals**

- factory class
- builder
- find or create
- invalid construction
- rehydration

---

## 4. `domain-service-operation`

**Use Domain Service only for ownerless domain operations**  
_category: domain · languages: language-independent_

**Claim**

A Domain Service expresses an important stateless domain operation that does not naturally belong to an Entity or Value Object; it is not an application service, deployable service, or microservice.

**Decision rule**

Try to place behavior with the Entity or Value Object owning its data and invariant; use a Domain Service only when expert language names a cross-concept operation whose inputs and outputs remain domain concepts and whose side effects are explicit.

**Why it matters**

Domain Services can clarify genuine processes but easily become procedural dumping grounds that strip behavior from the model.

**Common failure modes**

- anemic domain model
- god service
- technical orchestration mislabeled domain
- service terminology collision

**Counterexamples**

- A repository adapter or HTTP handler is not a Domain Service even when it invokes domain behavior.

**Activation signals**

- domain service
- god service
- anemic entity
- cross-entity operation

---

## 5. `go-explicit-contextual-errors`

**Keep Go error paths explicit and contextual**  
_category: go · languages: Go_

**Claim**

Go errors are ordinary explicit control flow; every material error must be handled, returned, or deliberately classified while preserving causal inspection, stable context, cleanup, and caller recovery semantics.

**Decision rule**

At each error site, identify recovery ownership, add operation context at the boundary that knows it, preserve cause using the current repository and toolchain convention, avoid duplicate logging and propagation, and test important failure and cleanup paths.

**Why it matters**

Discarded or repeatedly transformed errors lose root cause, break errors.Is or errors.As behavior, duplicate reports, and leak resources.

**Common failure modes**

- lost cause
- noisy duplicate logs
- broken sentinel or typed inspection
- leaked resource
- misleading success

**Counterexamples**

- A best-effort close during shutdown may be secondary
- but data-loss or durability consequences still require reporting or combination.

**Activation signals**

- ignored error
- fmt errorf
- errors Is
- errors As
- double log

---

## 6. `go-goroutine-resource-lifecycle`

**Own Go goroutine and resource lifecycles**  
_category: go · languages: Go_

**Claim**

Every goroutine and opened or exhaustible resource needs an owner, stop condition, completion observation, cleanup, and error behavior on success, failure, cancellation, and partial consumption.

**Decision rule**

At creation or acquisition, state who cancels or closes, whether and how the caller waits, how errors propagate, what partial consumption requires, and how completion is tested; use defer immediately after successful acquisition when its timing matches the required lifetime.

**Why it matters**

Go makes concurrent work and resource acquisition concise, but orphan goroutines, unread bodies, lost errors, and wrong close ownership cause leaks and deadlocks.

**Common failure modes**

- goroutine leak
- file or socket leak
- deadlock
- lost error
- premature close

**Counterexamples**

- Process-owned telemetry may be intentionally detached but still requires bounded buffers and shutdown semantics.

**Activation signals**

- go statement
- defer
- Close
- response body
- timer
- channel close

---

## 7. `implementation-attention-budget-presentation`

**Budget output for the consumer's attention**  
_category: implementation · languages: language-independent_

**Claim**

Output delivered into a consumer's finite attention or context budget - a report, packet, escalation queue, or summary - must be a prioritized, deduplicated, size-bounded presentation view rendered over unchanged canonical data; an unbounded dump of internal state is not a report, and unbudgeted delivery quietly converts the consumer into the system's overflow buffer.

**Decision rule**

Name the consumer and their budget before rendering; rank content by decision-relevance, deduplicate repeated reasons, bound total size, and keep canonical data unchanged underneath the view - and when the consumer is a human decision gate, budget the claims and decisions escalated to them as deliberately as the bytes.

**Why it matters**

An unprioritized dump transfers the triage cost to the reader, and a human adjudication gate fed unbudgeted escalations accumulates a queue that silently converts the owner's attention into the system's bottleneck.

**Common failure modes**

- cost-ordered dump where the consumer needed a decision-ordered brief
- duplicated activation reasons repeated across items
- unbudgeted escalation of decisions to a human gate until the queue outgrows the gate
- presentation edits leaking into canonical data

**Counterexamples**

- A completeness-contract artifact - an evidence ledger or exhibit table - is correctly unbounded; it must be labeled an archive and paired with a budgeted brief
- not served as the report.

**Activation signals**

- report or packet rendering code
- escalation or adjudication queues
- output size unbounded by consumer capacity

---

## 8. `implementation-error-surface-reduction`

**Reduce error surfaces without erasing failure meaning**  
_category: implementation · languages: language-independent_

**Claim**

Error handling may be simplified by natural total semantics, reliable masking, or aggregation at a useful boundary only when the change preserves caller-relevant failure information and operational safety.

**Decision rule**

For each proposed eliminated handler, prove that the operation's new semantics are natural for callers, the lower-level failure is fully contained, or a higher boundary owns an equivalent decision; otherwise retain explicit propagation.

**Why it matters**

Repeated low-level handling increases complexity, but defining away a material failure converts visible risk into silent corruption or misleading success.

**Common failure modes**

- false success
- lost cause
- duplicated translation
- inaccessible operational failure

**Counterexamples**

- A module may reliably hide transient storage retries if it owns idempotency
- limits
- and final failure reporting.

**Activation signals**

- repeated handlers
- low-level error leakage
- idempotent operation
- batch failure

---

## 9. `implementation-minimal-coherent-api`

**Expose a minimal coherent API contract**  
_category: implementation · languages: language-independent_

**Claim**

An API must state the non-obvious meaning callers depend on while exposing no more mechanism, configuration, or surface than demonstrated consumers require.

**Decision rule**

Inventory real consumers and specify inputs, outputs, units, ranges, ownership, mutation, ordering, side effects, failure, concurrency, lifecycle, and compatibility; remove a surface only if callers retain the required capability, and add indirection only when it hides coherent complexity or enables demonstrated variation.

**Why it matters**

A signature alone omits material obligations, while oversized or pass-through APIs increase compatibility burden and leak decisions.

**Common failure modes**

- signature-only contract
- configuration leakage
- parameter soup
- accidental public surface
- shallow interface

**Counterexamples**

- A stable public library may need deliberate extension points established by an accepted compatibility mission.

**Activation signals**

- public symbol
- interface
- protocol
- service endpoint
- configuration parameter

---

## 10. `legacy-provisional-safety-net`

**Provisional broad characterization safety net**  
_category: legacy · languages: language-independent_

**Claim**

A broad black-box or E2E suite may temporarily protect initial restructuring when local tests are impossible, with explicit brittleness and retirement rules.

**Decision rule**

Cover critical user scenarios and complex paths in an isolated stable environment, use them to enable the first seam, add narrower tests, then retain only enduring contract value.

**Why it matters**

Broad tests may be the only initial route but are slow, brittle, and weak at localization.

**Common failure modes**

- brittleness blocks unrelated change
- leaked state
- false confidence

**Counterexamples**

- Stable protocol E2E tests may retain enduring value after local tests exist.

**Activation signals**

- no local tests
- stable external boundary

---

## 11. `operations-contract-conformance-testing`

**Test each side's conformance to the shared contract**  
_category: operations · languages: language-independent_

**Claim**

Cross-service integration confidence comes from each side testing its own conformance to the shared specification - consumer-owned contract tests plus separate request-construction and response-tolerance checks - because either party can deploy a new version at any time.

**Decision rule**

Split integration testing into request-side conformance and response-side tolerance without invoking the real dependency; have consumers own contract tests against the provider's staging surface as an early-warning system; and require consumers to handle any allowed combination of new, missing, or partial fields since callers and suppliers deploy independently.

**Why it matters**

Overspecified end-to-end request/response loop tests verify only current behavior, not contract conformance - they pass until the day an independently deployed version change breaks production.

**Common failure modes**

- integration suite green while contract drift breaks production
- mock drift from the real contract
- consumer breaking on a legally added field

**Counterexamples**

- Characterization tests of an unspecified legacy dependency assert observed behavior deliberately - that is discovery
- not contract conformance.

**Activation signals**

- integration test suite
- service client
- mock of remote API
- staging environment
- pact file

---

## 12. `operations-ephemeral-instance-design`

**Treat instance identity, storage, and clock as ephemeral**  
_category: operations · languages: language-independent_

**Claim**

Services must treat machine identity, IP address, local storage, and clock as ephemeral and unreliable, tolerating the loss or slowdown of any single instance, avoiding irreplaceable special machines, and letting new instances volunteer for work instead of being individually configured.

**Decision rule**

Design so any instance can disappear or lag - no whole-cluster synchronous responses, no event-ordering or trusted-clock assumptions on virtualized hosts, no addresses baked into configuration files - and have instances join work through autoscaling groups, load balancers, or competing consumers.

**Why it matters**

Individual cloud VMs have worse availability and ephemeral identity compared with physical machines, and oversubscribed hosts make VM performance and clocks unpredictable; designs that assume stable identity break at exactly the wrong time.

**Common failure modes**

- pet server whose loss is an outage
- config drift between hand-managed instances
- ordering bugs from non-monotonic VM clocks
- containers baking secrets into images

**Counterexamples**

- A licensed appliance bound to hardware identity is a constraint to isolate behind an interface
- not a pattern to copy.

**Activation signals**

- hardcoded host address
- container image
- autoscaling group
- clock-based ordering
- special machine

---

## 13. `operations-synchronized-demand-dispersion`

**Anticipate and disperse synchronized demand pulses**  
_category: operations · languages: language-independent_

**Claim**

Synchronized stimuli - promotions and deep links, mass restarts, on-the-hour cron jobs, cache invalidation storms, and fixed retry intervals - concentrate demand into pulses that require far more than steady-state capacity; anticipate them and disperse the load with communication, waves, jitter, backoff, and pre-scaling.

**Decision rule**

Before any synchronized stimulus - marketing event, fleet restart, scheduled job, config push - estimate the pulse it creates; add jitter to periodic work, increasing backoff to retries, waves to fleet operations, and static fallback paths to promotions, and pre-scale where the pulse is known in advance.

**Why it matters**

The organization can conspire against its own system - a marketing email or a midnight cron line can produce a dogpile no steady-state capacity plan survives.

**Common failure modes**

- dogpile at startup or midnight
- thundering herd after cache flush
- retry synchronization amplifying a blip into an outage

**Counterexamples**

- A deadline-driven regulatory batch that must run at a fixed time needs capacity for its pulse rather than dispersion.

**Activation signals**

- cron schedule
- retry interval
- fleet restart script
- cache invalidation
- scheduled batch

---

## 14. `python-compatible-property-evolution`

**Evolve Python attributes through compatible properties**  
_category: python · languages: Python_

**Claim**

A plain public attribute can evolve to a property when real validation or computation appears, provided ordinary caller and framework behavior remains compatible; speculative getters and setters are unnecessary.

**Decision rule**

Start with the simplest public attribute allowed by the contract, add a property only when an earned rule exists, verify assignment access introspection serialization and framework behavior, and avoid surprising work or I/O behind attribute access.

**Why it matters**

Python properties preserve a useful evolution option without imposing boilerplate up front, but can also hide expensive work and compatibility changes.

**Common failure modes**

- surprising access cost
- framework bypass
- changed serialization
- recursive property
- compatibility break

**Counterexamples**

- A descriptor framework may require field declarations from the beginning; its repository contract outranks this evolution option.

**Activation signals**

- property
- getter
- setter
- public attribute
- new validation

---

## 15. `refactoring-demonstrated-pressure`

**Evidence that earns refactoring**  
_category: refactoring · languages: language-independent_

**Claim**

Structural intervention requires demonstrated present or imminent maintenance pressure, not unattractiveness alone.

**Decision rule**

Require a concrete goal and verified pressure such as repeated coupled edits, dispersed responsibility, blocked testing, recurring defects, active complexity growth, or material review/cognitive cost; select the smallest response.

**Why it matters**

Refactoring spends risk and review capacity and should target recurring cost.

**Common failure modes**

- metric-driven churn
- wrong bottleneck
- under-refactoring where history is unavailable

**Counterexamples**

- A security-driven structural migration can be earned by external risk rather than prior churn.

**Activation signals**

- smell
- hotspot
- change friction
- test blockage

---

## 16. `testing-database-production-fidelity`

**Test the database with production semantics**  
_category: testing · languages: language-independent_

**Claim**

Integration tests against a managed database earn trust only by matching production semantics - the same DBMS vendor (no in-memory substitutes), a separate transaction or unit of work per arrange/act/assert section instead of a shared or umbrella transaction, sequential execution, and leftover-data cleanup at the start of each test.

**Decision rule**

Run database integration tests against the production DBMS vendor (version or edition may differ); give each test section its own transaction or unit of work because production gives each business operation its own; execute sequentially and clean leftover data at the beginning of each test rather than relying on teardown or rollback-only umbrella transactions.

**Why it matters**

In-memory analogs and umbrella transactions diverge from production behavior in locking, constraints, and visibility, producing both false positives and false negatives exactly where database tests are supposed to provide confidence.

**Common failure modes**

- functional mismatch between in-memory analog and production DBMS
- umbrella transactions hiding visibility bugs
- teardown skipped leaving state for the next run

**Counterexamples**

- Widely practiced sqlite-in-memory and parallel testcontainers patterns contradict this record; where a repository has adopted them as convention
- universal-repository-contract-precedence governs before enforcement.

**Activation signals**

- sqlite in tests with another production DBMS
- shared transaction in tests
- parallel database tests
- teardown cleanup

---

## 17. `testing-shared-dependency-substitution`

**Substitute shared and slow dependencies, keep collaborators real**  
_category: testing · languages: language-independent_

**Claim**

Replace with test doubles only the dependencies that are shared between tests or slow out-of-process ones, so tests stay fast and mutually independent, and keep private mutable collaborators and value objects real.

**Decision rule**

Classify each dependency as shared, private, out-of-process, or volatile and distinguish collaborators from value objects; substitute shared and slow out-of-process dependencies to isolate tests from each other, and keep in-process private collaborators and immutable values real rather than isolating the unit from them.

**Why it matters**

Isolating units from their collaborators couples tests to internal communication patterns, while isolating tests from each other targets the actual sources of interference and slowness.

**Common failure modes**

- mock-everything suites that break on refactor
- tests coupled through a shared database
- doubles hiding real collaborator defects

**Counterexamples**

- In untested legacy code
- substituting a private in-process collaborator at a seam can be the only way to gain feedback; that move is governed by the legacy records and their provisional status rules.

**Activation signals**

- mock-heavy suite
- shared test database
- tests interfering through state
- mocking framework configuration

---

## 18. `universal-earned-abstraction`

**Earn abstractions through demonstrated pressure**  
_category: universal · languages: language-independent_

**Claim**

Introduce or retain an abstraction only when it hides coherent knowledge or mechanism and reduces total caller reasoning, coordinated change, or substitution cost more than its interface and indirection add.

**Decision rule**

Identify stable meaning and actual variation, compare direct code, duplication, composition, helper, configuration, and abstraction, and count concepts, navigation, errors, lifecycle, testing, and operational cost on both sides.

**Why it matters**

An abstraction can create local reasoning, but a shallow or speculative one freezes the wrong model and adds permanent interface burden.

**Common failure modes**

- speculative generality
- wrong commonality
- leaky abstraction
- mock-shaped production API

**Activation signals**

- multiple implementations
- duplicated rule
- wrapper layer
- plugin request

---

## 19. `universal-evidence-before-intervention`

**Evidence before intervention**  
_category: universal · languages: language-independent_

**Claim**

An engineering intervention is earned only by evidence capable of establishing the claimed problem and distinguishing the proposed response from no change or a lower-cost response.

**Decision rule**

State the observable condition, evidence class, causal hypothesis, and remedy prediction; gather the cheapest discriminating evidence before recommending or executing material change.

**Why it matters**

Static unattractiveness, source prestige, and plausible stories can otherwise become unbounded refactoring, architecture, or optimization mandates.

**Common failure modes**

- aesthetic debt declaration
- architecture astronomy
- speculative optimization

**Activation signals**

- smell
- hotspot
- metric
- incident
- complaint
- proposed architecture

---

## 20. `universal-separate-semantic-structural-change`

**Separate semantic and structural work**  
_category: universal · languages: language-independent_

**Claim**

Feature behavior, defect repair, refactoring, architecture, migration, optimization, cleanup, deletion, and dependency changes remain distinct checkpoints even when one task needs several.

**Decision rule**

Classify each edit by intended observable effect; preserve the failing reproducer or baseline through preparation; make semantic effect appear in an isolated checkpoint and justify follow-up structure independently.

**Why it matters**

Mixed changes make causality, review, rollback, benchmark interpretation, and authority impossible to audit.

**Common failure modes**

- behavior-changing refactor
- repair hidden in move/rename
- untraceable benchmark or regression

**Activation signals**

- mixed diff
- behavior plus moves
- benchmark plus cleanup
- migration plus deletion

---
