# Language and Performance Sources: Evidence Extraction

Status: complete source-lane extraction for synthesis. This artifact mines operational doctrine; it is not a pair of book summaries and does not make either source universally normative.

## Scope, source IDs, and locator convention

The complete converted Markdown chapter sets were inspected for both assigned sources, including front matter, part dividers, index/about/colophon files, and every substantive chapter.

- `FP` — *Fluent Python, Second Edition* (converted early-release text).
  - `FP_ROOT = books/fluent-python-2nd-edition-z-lib-org`
- `EGO` — *Efficient Go: Data-Driven Performance Optimization*.
  - `EGO_ROOT = books/efficient-go-data-driven-performance-optimization-bartlomiej-plotka-z-library`

Every source locator below has the form `SOURCE_ID: chapters/<file> :: <Markdown heading>` and is relative to the declared source root. Claims are paraphrases. Page anchors are intentionally not canonical locators.

## Chapter coverage ledger

### FP coverage (33/33 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `FP_ROOT/chapters/001-fluent-python.md` | Fluent Python | Edition/revision metadata; July 2021 early-release status; no independent doctrine. |
| `FP_ROOT/chapters/002-preface.md` | Preface | Existing facilities before custom abstraction; experimentation, REPL, doctest, tests; stale first-edition passages explicitly acknowledged. |
| `FP_ROOT/chapters/003-acknowledgments.md` | Acknowledgments | Publication context only. |
| `FP_ROOT/chapters/004-part-i-prologue.md` | Part I. Prologue | Part divider. |
| `FP_ROOT/chapters/005-chapter-1-the-python-data-model.md` | Chapter 1: The Python Data Model | Special-method protocols; built-in interoperability; representations; collection protocols; protocol-conforming behavior. |
| `FP_ROOT/chapters/006-part-ii-data-structures.md` | Part II. Data Structures | Part divider. |
| `FP_ROOT/chapters/007-chapter-2-an-array-of-sequences.md` | Chapter 2: An Array of Sequences | Sequence representation; comprehensions versus generators; records/tuples; unpacking; slicing; arrays, memory views, NumPy, deques. |
| `FP_ROOT/chapters/008-chapter-3-dictionaries-and-sets.md` | Chapter 3: Dictionaries and Sets | Hashability; mappings/sets; missing-key policy; specialized mappings; immutable façades; views; mapping extension. |
| `FP_ROOT/chapters/009-chapter-4-text-versus-bytes.md` | Chapter 4: Text Versus Bytes | Text/binary boundary; explicit codecs; failures; normalization/casefolding; collation; lossy transformations; filesystem APIs. |
| `FP_ROOT/chapters/010-chapter-5-data-class-builders.md` | Chapter 5: Data Class Builders | Data-carrier choices; no runtime enforcement from hints; dataclass options; data-class smell as hypothesis; scaffolding and interchange records. |
| `FP_ROOT/chapters/011-chapter-6-object-references-mutability-and-recycling.md` | Chapter 6: Object References, Mutability, and Recycling | Identity/equality; aliasing; shallow/deep copies; call by sharing; mutable defaults; ownership; GC/weak references. |
| `FP_ROOT/chapters/012-part-iii-functions-as-objects.md` | Part III. Functions as Objects | Part divider. |
| `FP_ROOT/chapters/013-chapter-7-functions-as-first-class-objects.md` | Chapter 7: Functions as First-Class Objects | Higher-order functions; callables; parameter API design; standard functional helpers; class-free behavior injection. |
| `FP_ROOT/chapters/014-chapter-8-type-hints-in-functions.md` | Chapter 8: Type Hints in Functions | Gradual typing; `Any`; duck/nominal/static protocol relations; annotation scope; tests versus type checking; checker limitations. |
| `FP_ROOT/chapters/015-chapter-9-decorators-and-closures.md` | Chapter 9: Decorators and Closures | Import-time execution; closures; decorator transparency; registration; cache/lru-cache risks; single dispatch. |
| `FP_ROOT/chapters/016-chapter-10-design-patterns-with-first-class-functions.md` | Chapter 10: Design Patterns with First-Class Functions | Function-oriented Strategy/Command; patterns as intermediate designs; stateful callable trade-off; registration discovery. |
| `FP_ROOT/chapters/017-part-iv-classes-and-protocols.md` | Part IV. Classes and Protocols | Part divider. |
| `FP_ROOT/chapters/018-chapter-11-a-pythonic-object.md` | Chapter 11: A Pythonic Object | Requirement-proportional objects; repr/format/equality/hash contracts; alternate constructors; immutability; `__slots__` contraindications. |
| `FP_ROOT/chapters/019-chapter-12-writing-special-methods-for-sequences.md` | Chapter 12: Writing Special Methods for Sequences | Informal sequence protocol; correct slicing; dynamic attributes; equality/hash; consistency with standard objects. |
| `FP_ROOT/chapters/020-chapter-13-interfaces-protocols-and-abcs.md` | Chapter 13: Interfaces, Protocols, and ABCs | Duck, goose, nominal, and static duck typing; fail-fast use; ABCs; minimal protocols; runtime-check limitations. |
| `FP_ROOT/chapters/021-chapter-14-inheritance-for-good-or-for-worse.md` | Chapter 14: Inheritance: For Good or For Worse | Built-in subclass hazards; MRO; mixin constraints; interface versus implementation inheritance; composition preference. |
| `FP_ROOT/chapters/022-chapter-15-more-about-type-hints.md` | Chapter 15: More About Type Hints | Overloads; `TypedDict` false security; casts; runtime annotation hazards; generics/variance; rapidly evolving typing system. |
| `FP_ROOT/chapters/023-chapter-16-operator-overloading-doing-it-right.md` | Chapter 16: Operator Overloading: Doing It Right | Conventional operator semantics; `NotImplemented`; mixed operands; nonmutation; comparison/hash consistency; augmented assignment. |
| `FP_ROOT/chapters/024-chapter-17-iterables-iterators-and-generators.md` | Chapter 17: Iterables, Iterators, and Generators | Iterable/iterator distinction; lazy streaming; generator boundaries; standard iterators; large-data pipelines; single-use behavior. |
| `FP_ROOT/chapters/025-chapter-18-context-managers-and-else-blocks.md` | Chapter 18: Context Managers and else Blocks | Deterministic setup/teardown; exception boundaries; `contextlib`; EAFP/LBYL; pattern-matching case study. |
| `FP_ROOT/chapters/026-chapter-19-classic-coroutines.md` | Chapter 19: Classic Coroutines | Generator-based coroutine mechanics; cooperative scheduling; termination/exception propagation; primarily historical guidance. |
| `FP_ROOT/chapters/027-chapter-20-concurrency-models-in-python.md` | Chapter 20: Concurrency Models in Python | Concurrency versus parallelism; thread/process/async trade-offs; GIL-era constraints; CPU/I/O distinction; scaling caution. |
| `FP_ROOT/chapters/028-chapter-21-concurrency-with-futures.md` | Chapter 21: Concurrency with Futures | Thread/process executors; completion order; future-owned state; exceptions; bounded clients; realistic concurrent testing. |
| `FP_ROOT/chapters/029-chapter-22-asynchronous-programming.md` | Chapter 22: Asynchronous Programming | Event-loop nonblocking discipline; async context/iteration; semaphores; executor escape hatch; backpressure; CPU-bound traps. |
| `FP_ROOT/chapters/030-chapter-23-dynamic-attributes-and-properties.md` | Chapter 23: Dynamic Attributes and Properties | Data-driven attributes; property-based API evolution/validation; cache semantics; attribute-lookup risk; simplest-mechanism preference. |
| `FP_ROOT/chapters/031-chapter-24-attribute-descriptors.md` | Chapter 24: Attribute Descriptors | Reusable managed-field behavior; overriding/non-overriding descriptors; shadowing; narrow framework-level applicability. |
| `FP_ROOT/chapters/032-chapter-25-class-metaprogramming.md` | Chapter 25: Class Metaprogramming | Class factories/hooks/decorators/metaclasses; import-time effects; conflict and maintenance costs; application-level restraint. |
| `FP_ROOT/chapters/033-about-the-author.md` | About the Author | Author background and perspective only. |

### EGO coverage (18/18 files)

| Path | Converted title | Operational themes or disposition |
|---|---|---|
| `EGO_ROOT/chapters/001-data-driven-performance-optimizations.md` | Data-Driven Performance Optimizations | Title/publication metadata only. |
| `EGO_ROOT/chapters/002-table-of-contents.md` | Table of Contents | Navigation and chapter-boundary cross-check. |
| `EGO_ROOT/chapters/003-preface.md` | Preface | Data-driven scope; non-generalizability of optimizations; Go 1.18+ assumption; pedagogical omission of some error handling. |
| `EGO_ROOT/chapters/004-acknowledgments.md` | Acknowledgments | Publication context only. |
| `EGO_ROOT/chapters/005-chapter-1-software-efficiency-matters.md` | Chapter 1: Software Efficiency Matters | Accuracy/speed/efficiency distinction; total cost; premature pessimization; scaling cost; doing less work; readability tension. |
| `EGO_ROOT/chapters/006-chapter-2-efficient-introduction-to-go.md` | Chapter 2: Efficient Introduction to Go | Go simplicity; package/export/dependency discipline; explicit errors; composition/interfaces/generics; no blanket speed claims. |
| `EGO_ROOT/chapters/007-chapter-3-conquering-efficiency.md` | Chapter 3: Conquering Efficiency | Reasonable versus deliberate optimization; Resource-Aware Efficiency Requirements; issue triage; TFBO loop; design levels. |
| `EGO_ROOT/chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md` | Chapter 4: How Go Uses the CPU Resource (or Two) | Compiler/scheduler/cache behavior; simple hot paths; contiguous data; goroutine/channel costs; concurrency as late optimization. |
| `EGO_ROOT/chapters/009-chapter-5-how-go-uses-memory-resource.md` | Chapter 5: How Go Uses Memory Resource | VSS/RSS/heap distinction; paging; values/pointers/slices; allocation/escape/GC; `GOMEMLIMIT`; allocate-less-first rule. |
| `EGO_ROOT/chapters/010-chapter-6-efficiency-observability.md` | Chapter 6: Efficiency Observability | Signal selection; instrumentation cost; metric semantics/granularity; percentiles; cardinality; CPU/wall time; heap/RSS/WSS. |
| `EGO_ROOT/chapters/011-chapter-7-data-driven-efficiency-assessment.md` | Chapter 7: Data-Driven Efficiency Assessment | Estimated and asymptotic complexity; constant factors; expected-versus-observed scaling; empirical verification. |
| `EGO_ROOT/chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md` | Chapter 8: Benchmarking Versus Stress and Load Tests | Benchmark validity; versions/workloads/variance; production/macro/micro levels; Go benchmarks; compiler traps; containerized macro tests. |
| `EGO_ROOT/chapters/013-chapter-9-data-driven-bottleneck-analysis.md` | Chapter 9: Data-Driven Bottleneck Analysis | Root cause versus symptom; pprof semantics; sample uncertainty; flat/cumulative cost; heap/goroutine/CPU/off-CPU profiles. |
| `EGO_ROOT/chapters/014-chapter-10-optimization-examples.md` | Chapter 10: Optimization Examples | One-variable optimization; specialization; streaming; unsafe trade-offs; sharded/bounded concurrency; target-based stopping. |
| `EGO_ROOT/chapters/015-chapter-11-optimization-patterns.md` | Chapter 11: Optimization Patterns | Do less work; time/space trade-offs; reduce/reuse/recycle; resource/goroutine lifecycle; preallocation; pooling and retention traps. |
| `EGO_ROOT/chapters/016-index.md` | Index | Retrieval aid; conversion is heavily table-mangled; no independent doctrine. |
| `EGO_ROOT/chapters/017-about-the-author.md` | About the Author | Observability/SRE/Go-systems experience; source-perspective context. |
| `EGO_ROOT/chapters/018-colophon.md` | Colophon | Publication metadata only. |

## Per-source corpus-map evidence

### FP — Fluent Python

- **Primary domain:** Python implementation craft: effective use and design of data structures, functions, objects, protocols, typing, resource management, concurrency, and metaprogramming.
- **Strongest contributions:** makes language protocols operational; distinguishes representation and ownership choices; exposes runtime/static boundaries; supplies decision alternatives among functions, classes, protocols, ABCs, inheritance, generators, context managers, and dynamic mechanisms; repeatedly constrains sophistication by actual application/library requirements.
- **Contextual assumptions:** Python 3.9/3.10-era APIs, often CPython; a developer can inspect language/standard-library behavior; examples favor idiomatic interoperability; most examples are pedagogical rather than production workload evidence.
- **Limitations and dating:** the conversion is an early-release build with revision notes through July 2021, and the preface admits stale first-edition material. GIL, coroutine, typing, cache thread-safety, framework, and API claims are especially version-sensitive. Classic generator coroutines are historical for most new code. `cached_property` thread-safety and several typing recommendations have changed in later Python versions. Repository interpreter/support matrix and current official docs outrank the text.
- **Known tensions:** idiomatic use can conflict with repository compatibility or established API contracts; duck typing can conflict with fail-fast/static guarantees; dynamic mechanisms can reduce boilerplate while hiding control flow; generators reduce memory but add single-pass/lifetime constraints; `__slots__`, caching, zero-copy views, and concurrency can improve efficiency while narrowing semantics.
- **Likely agent roles:** coding, review, debugging/repair, performance, library/API design, legacy modernization, repository assessment.
- **Concepts worth mining:** protocol conformance, representational fit, ownership and aliasing, explicit encoding boundaries, runtime-validation boundary, gradual typing, function-oriented design, minimal protocols, composition, deterministic cleanup, streaming, concurrency-model fit, bounded async, dynamic-mechanism escalation, cache validity.
- **Representative locators:** `FP: chapters/005-chapter-1-the-python-data-model.md :: ## How Special Methods Are Used`; `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## Defensive Programming with Mutable Parameters`; `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## Flawed Typing and Strong Testing`; `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Designing a static protocol`; `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## Processes, threads, and Python's Infamous GIL`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Metaclasses in the Real world`.

### EGO — Efficient Go

- **Primary domain:** evidence-driven performance engineering, with Go-specific runtime, benchmark, profiling, allocation, concurrency, and resource-lifecycle mechanics.
- **Strongest contributions:** formalizes performance goals as workload/resource/percentile constraints; separates reasonable from deliberate optimization; provides a reproducible test-first/benchmark/profile/one-change loop; distinguishes measurement semantics and benchmark levels; makes concurrency, pooling, unsafe conversion, and runtime tuning late, evidence-earned options.
- **Contextual assumptions:** Go 1.18+ circa 2022; service and systems workloads with observable CPU/memory/latency behavior; teams can retain benchmark artifacts and profiles; examples often use Prometheus, containers, Linux, and pprof.
- **Limitations and dating:** runtime/compiler/container behavior drifts. Error wrapping advice predates later standard-library practice; `GOMAXPROCS`, container awareness, compiler optimization, GC, and runtime profile details must be checked against the repository toolchain. Napkin latency figures and hardware observations are illustrative, not portable requirements. Many examples are controlled demonstrations, not proof that the transformation generalizes.
- **Known tensions:** small obvious efficiency habits versus YAGNI; readability versus specialized hot paths; microbenchmark wins versus macro memory/GC regressions; generic abstractions versus direct specialized code; concurrency throughput versus coordination/scheduling/nondeterminism; allocation reduction versus retention or aliasing risk.
- **Likely agent roles:** performance, coding, review, architecture, debugging/repair, operational hardening, repository assessment.
- **Concepts worth mining:** Resource-Aware Efficiency Requirements, efficiency triage, TFBO loop, measurement semantics, benchmark validity, benchmark-level selection, profile-led bottleneck analysis, complexity/algorithm-first optimization, semantic equivalence, memory/accounting boundaries, late bounded concurrency, reduce/reuse/recycle, goroutine/resource lifecycle, performance regression gates.
- **Representative locators:** `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Resource-Aware Efficiency Requirements`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Efficiency-Aware Development Flow`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Reliability of Experiments`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: #### Profile First, Ask Questions Later`; `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Optimize One Thing at a Time`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### The Three Rs Optimization Method`.

## Source-role classification

| Source | Source roles | Appropriate doctrinal weight |
|---|---|---|
| FP | Language-specific implementation craft; API/protocol design; runtime semantics; concurrency orientation; framework-mechanism restraint | Strong for Python semantic hazards and mechanism selection within a compatible repository; contextual and version-sensitive for runtime/concurrency/performance claims. |
| EGO | Performance engineering; measurement and profiling; Go implementation craft; operational observability; resource lifecycle | Strong for performance procedure and evidence thresholds; contextual for particular optimizations and Go/runtime facts. |

## Conversion and evidence caveats

- FP is explicitly an early-release conversion. Several chapters carry raw/unedited notices; the preface includes older Python discussion; chapter guidance spans Python 3.9 and 3.10. Treat edition date as part of every applicability test.
- EGO Chapter 7 continues at the start of `012-chapter-8-benchmarking-versus-stress-and-load-tests.md` before the later `## Benchmarking` heading. The filename/title boundary is therefore not a reliable semantic boundary by itself.
- Wide tables are frequently flattened or malformed, most visibly FP special-method/typing tables, EGO latency tables, and the EGO index. Claims below rely on surrounding prose and executable examples rather than attempting to reconstruct broken cells.
- Some code formatting is merged into headings or callout text. Locators use actual converted headings where possible; chapter-summary claims are corroborated against the substantive section, not inferred from the summary alone.
- Both sources are practitioner books, not controlled empirical studies. Benchmark examples establish procedures and failure modes; they do not establish that their result sizes generalize.
- All interpreter, compiler, runtime, standard-library, dependency, OS, and hardware facts require current repository/toolchain verification before execution.

## Candidate doctrine records: Python implementation

The fields are compact but map directly to the requested concept schema. `Required / insufficient` separates evidence that earns action from signals that merely suggest investigation. `Routes` supplies role, task, repository-signal, language, risk, exclusion, prerequisite, priority, budget, and related-concept metadata.

### FP-IMPL-001 — Repository-shaped Python idiom

- **Category / claim:** implementation, review. Pythonic form is a contextual interoperability property, not permission to overwrite repository contracts with a book's preferred syntax.
- **Decision rule:** use a language idiom when the supported interpreter/dependency matrix accepts it, neighboring code establishes or tolerates it, and it makes the required behavior easier to understand or integrate. Preserve an established alternative when changing it would widen compatibility, review, or migration risk without task benefit.
- **Applicable / not:** applies to all Python changes; does not authorize style-only rewrites, version-floor changes, or public API migration.
- **Required / insufficient evidence:** required—project metadata, CI matrix, formatter/linter/type-checker configuration, adjacent code, accepted API contracts, tests. Insufficient—newness, elegance, author preference, or isolated REPL success.
- **Inputs / outputs:** input is repository contract plus task behavior; output is a compatible implementation and an explicit note for any intentionally newer construct.
- **Preserve; safe / unsafe:** preserve runtime compatibility, import behavior, serialization, public signatures, formatting policy. Safe—reuse existing constructs and standard protocols. Unsafe—introduce pattern matching, newer typing syntax, async APIs, or dynamic features without version and integration proof.
- **Failure modes / counterexample:** cargo-cult idiom, drive-by modernization, rejecting deliberately conservative library code. Counterexample: greenfield code with an explicit current-version floor may adopt current idioms immediately.
- **Interactions / conflicts:** FP-IMPL-002, FP-IMPL-007, FP-IMPL-016; conflict `CONF-LP-001`.
- **Confidence / routes:** strong; roles coding/review/repair; tasks any Python edit; signals `pyproject.toml`, `tox.ini`, version guards, compatibility shims; language Python; all risks; exclude vendored/generated code; prerequisite repository orientation; priority core; budget 200–350 tokens.
- **Source support:** `FP: chapters/002-preface.md :: # Preface`; `FP: chapters/005-chapter-1-the-python-data-model.md :: ## How Special Methods Are Used`; `FP: chapters/018-chapter-11-a-pythonic-object.md :: ## Chapter Summary`.

### FP-IMPL-002 — Earn behavior through existing protocols

- **Category / claim:** implementation, architecture. A custom type should expose an existing Python protocol when clients already consume that behavior; protocol conformance earns interoperability without a bespoke API.
- **Decision rule:** identify the actual operations clients require, inspect the corresponding standard protocol, and implement the smallest semantically complete set. Add special methods only when callers or library integration need them and their conventional semantics can be honored.
- **Applicable / not:** custom collections, numeric/domain values, context managers, iterables, callables; not for decorative completeness or when an ordinary named method communicates a domain action better.
- **Required / insufficient evidence:** required—call sites, expected built-in/library operations, behavior tests including edge cases, mutability and error semantics. Insufficient—method-name symmetry, hypothetical future reuse, or ability to implement a dunder.
- **Inputs / outputs:** required operations and standard behavior; output is a protocol-conformant type plus contract tests.
- **Preserve; safe / unsafe:** preserve return types, exhaustion/slicing/mutation rules, exception forms, equality/hash invariants. Safe—delegate to proven built-ins and call built-ins rather than dunders. Unsafe—invent undocumented double-underscore names or partially emulate a protocol in surprising ways.
- **Failure modes / counterexample:** feature-parade objects, public implementation leakage, `__getattr__` masking missing data. Counterexample: a domain command such as `approve()` should not be disguised as a generic operator merely to look Pythonic.
- **Interactions / conflicts:** FP-IMPL-009, FP-IMPL-011, FP-IMPL-012.
- **Confidence / routes:** strong; coding/API/review roles; tasks custom type or library integration; signals repeated adapter code, built-in operation failures; Python; medium API risk; exclude generated models; prerequisite caller inventory; priority high; budget 350–500 tokens.
- **Source support:** `FP: chapters/005-chapter-1-the-python-data-model.md :: ## A Pythonic Card Deck`; `FP: chapters/005-chapter-1-the-python-data-model.md :: ## Collection API`; `FP: chapters/019-chapter-12-writing-special-methods-for-sequences.md :: ## Protocols and Duck Typing`.

### FP-IMPL-003 — Select representation by semantic and workload fit

- **Category / claim:** implementation, performance. Choose list, tuple, deque, set, mapping, flat array, memory view, or generator from required operations, ownership, size, and access pattern—not habit.
- **Decision rule:** first specify ordering, uniqueness, mutability, random access, endpoint operations, record semantics, element homogeneity, expected cardinality, and materialization need. Use the simplest standard representation satisfying those needs; optimize representation only after memory or latency evidence.
- **Applicable / not:** collection-heavy code and data pipelines; not a license for low-level buffers in small cold paths.
- **Required / insufficient evidence:** required—operation profile, data shape/size, mutation and lifetime contract, benchmark/profile for efficiency claims. Insufficient—container name, theoretical compactness alone, or a microbenchmark excluding conversion and downstream work.
- **Inputs / outputs:** workload/semantics; output is selected representation and tests for ordering, aliasing, mutation, and boundary conversion.
- **Preserve; safe / unsafe:** preserve iteration order where contractual, equality, duplicates, precision, ownership. Safe—`deque` for measured endpoint queues, `array`/NumPy for homogeneous numeric workloads, views for intentional shared memory. Unsafe—`list.pop(0)` on demonstrated large queues, zero-copy views without alias-lifetime analysis, set conversion when order/duplicates matter.
- **Failure modes / counterexample:** premature NumPy, accidental quadratic operations, retained backing buffers, representation leaking into API. Counterexample: a small fixed configuration list values clarity over compactness.
- **Interactions / conflicts:** FP-IMPL-004, FP-IMPL-012, EGO-PERF-009, EGO-PERF-010.
- **Confidence / routes:** strong; coding/performance/review; tasks data-structure choice; signals large cardinality, endpoint churn, numeric loops, memory pressure; Python; normal-to-high risk; exclude trivial constants; prerequisite behavior/workload inventory; priority high; budget 400–600.
- **Source support:** `FP: chapters/007-chapter-2-an-array-of-sequences.md :: ## Overview of Built-In Sequences`; `FP: chapters/007-chapter-2-an-array-of-sequences.md :: ## When a List Is Not the Answer`; `FP: chapters/008-chapter-3-dictionaries-and-sets.md :: ## Practical Consequences of How dict Works`.

### FP-IMPL-004 — Make mutable ownership explicit

- **Category / claim:** universal, implementation, repair. In Python, assignment and parameter passing share references; code must deliberately decide whether a mutable input is borrowed, consumed, copied, or owned.
- **Decision rule:** for every stored or mutated input, state whether caller-visible mutation is part of the contract. Copy at the boundary when internal ownership is intended; retain an alias only when shared mutation is explicit and tested. Never use a mutable default as per-call state.
- **Applicable / not:** constructors, caches, collections, nested data, concurrency; copying is not automatically appropriate for intentionally shared buffers or objects whose identity is the contract.
- **Required / insufficient evidence:** required—mutation call sites, identity/equality expectations, lifetime, data size, concurrency, tests. Insufficient—type annotation alone, shallow `copy()` without nested analysis, or assumption that tuples imply deep immutability.
- **Inputs / outputs:** ownership contract and object graph; output is explicit copy/borrow/mutate behavior and aliasing tests.
- **Preserve; safe / unsafe:** preserve intentional identity and performance boundaries. Safe—`None` sentinel then allocate; convert incoming iterable to owned list; document in-place operations. Unsafe—store caller list then mutate silently; shallow-copy nested structures while claiming isolation; compare value with `is`.
- **Failure modes / counterexample:** ghost state across calls, action-at-a-distance, race-prone caches, expensive defensive copying on a proven hot path. Counterexample: `memoryview` deliberately shares storage and should make that fact part of the API.
- **Interactions / conflicts:** FP-IMPL-003, FP-IMPL-011, FP-IMPL-017, EGO-PERF-012.
- **Confidence / routes:** universal/strong; coding/repair/review/performance; signals mutable defaults, constructor assignment, in-place operators, shared caches; Python; high correctness risk; exclude immutable scalar-only paths; prerequisite ownership inspection; core; budget 300–500.
- **Source support:** `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## Function Parameters as References`; `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## Mutable Types as Parameter Defaults: Bad Idea`; `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## Defensive Programming with Mutable Parameters`.

### FP-IMPL-005 — Treat text/bytes conversion as a policy boundary

- **Category / claim:** implementation, repair. Decode bytes to text at a known external boundary and encode text to bytes when leaving it; make codec and error policy explicit.
- **Decision rule:** determine the producer's encoding/metadata and the domain's comparison/display requirements. Decode once near ingress, operate on `str`, normalize/casefold only for a stated domain purpose, and encode once near egress.
- **Applicable / not:** files, subprocesses, sockets, databases, serialization, filesystem names; not for opaque binary payloads whose bytes must remain uninterpreted.
- **Required / insufficient evidence:** required—protocol/file metadata, representative non-ASCII samples, round-trip and failure tests, normalization/search requirements. Insufficient—platform default, successful ASCII sample, encoding guess treated as certainty.
- **Inputs / outputs:** byte-source contract and domain text policy; output is explicit codec/error/normalization behavior.
- **Preserve; safe / unsafe:** preserve exact bytes where required, user-visible characters, normalization-sensitive identifiers. Safe—explicit `encoding=`, strict failure by default, domain-authorized replacement/loss. Unsafe—silent lossy decode, indiscriminate accent removal, confusing code points with bytes, default-encoding dependence.
- **Failure modes / counterexample:** mojibake, cross-platform corruption, security/identity collisions after normalization. Counterexample: binary hashes, images, or compressed streams should remain bytes.
- **Interactions / conflicts:** FP-IMPL-001, FP-IMPL-004; evidence taxonomy runtime observation + user/protocol requirements.
- **Confidence / routes:** universal/strong; coding/repair/review; signals `.encode`, `.decode`, `open()` without encoding, mixed `str`/`bytes`, Unicode bugs; Python; high data-integrity risk; prerequisite external-format contract; core; budget 300–450.
- **Source support:** `FP: chapters/009-chapter-4-text-versus-bytes.md :: ## Character Issues`; `FP: chapters/009-chapter-4-text-versus-bytes.md :: ## Handling Text Files`; `FP: chapters/009-chapter-4-text-versus-bytes.md :: ## Beware of Encoding Defaults`; `FP: chapters/009-chapter-4-text-versus-bytes.md :: ## Extreme "Normalization": Taking Out Diacritics`.

### FP-IMPL-006 — Distinguish domain objects from data carriers

- **Category / claim:** implementation, domain, review. A behaviorless data class is appropriate for interchange, snapshots, or temporary scaffolding; in domain code it becomes a restructuring candidate only when policies manipulating it are scattered or duplicated.
- **Decision rule:** keep a carrier when its purpose is boundary transport or immutable intermediate representation. Move behavior/invariants toward it when recurring operations depend on its fields, change together, and a cohesive domain responsibility emerges.
- **Applicable / not:** dataclass/NamedTuple/TypedDict decisions; not a blanket prohibition on records, DTOs, schemas, event payloads, or functional designs.
- **Required / insufficient evidence:** required—call sites, invariant ownership, co-change/duplication, lifecycle and serialization role. Insufficient—presence of `@dataclass`, getters, or no methods by itself.
- **Inputs / outputs:** role of record and behavior map; output is retain/move-behavior decision and preservation plan.
- **Preserve; safe / unsafe:** preserve wire/schema compatibility, equality/order/hash and mutability semantics. Safe—immutable boundary record, named construction, explicit validation elsewhere. Unsafe—assume annotations validate at runtime; add domain behavior to generated/vendor schema models; refactor based on smell alone.
- **Failure modes / counterexample:** anemic domain, overstuffed entity, serialization coupled to behavior. Counterexample: JSON import/export record should often remain a simple carrier.
- **Interactions / conflicts:** FP-IMPL-007, FP-IMPL-018; domain-integrity concepts from other lanes.
- **Confidence / routes:** contextual; coding/domain/review/refactoring; signals widely manipulated dataclass, scattered field logic; Python; medium structural risk; exclude generated records; prerequisite caller/history evidence; normal; budget 400–550.
- **Source support:** `FP: chapters/010-chapter-5-data-class-builders.md :: ## Data class as a code smell`; `FP: chapters/010-chapter-5-data-class-builders.md :: ## Data class as scaffolding`; `FP: chapters/010-chapter-5-data-class-builders.md :: ## Data class as intermediate representation`.

### FP-IMPL-007 — Static hints do not create runtime guarantees

- **Category / claim:** implementation, review. Type hints are optional static evidence; they do not validate untrusted data, enforce business invariants, prove behavior, or replace tests.
- **Decision rule:** add or strengthen annotations where the repository checker consumes them and they clarify a stable boundary or catch demonstrated classes of mistakes. Add runtime validation at trust boundaries and tests for behavior/invariants regardless of annotation coverage.
- **Applicable / not:** typed and gradually typed Python; not a mandate for complete annotation coverage or for removing useful hints.
- **Required / insufficient evidence:** required—configured checker/version, boundary importance, observed defect class, annotation maintenance cost, runtime input trust. Insufficient—green checker alone, `TypedDict`, `cast`, annotation percentage, or `isinstance` against a runtime-checkable protocol as semantic proof.
- **Inputs / outputs:** checker/repository contract and trust model; output is appropriate hint, validation, test, or explicit omission.
- **Preserve; safe / unsafe:** preserve runtime API and expressive behavior. Safe—annotate public/stable boundaries, use `get_type_hints` only with import/evaluation care, narrow `Any`. Unsafe—cast away real uncertainty, parse untrusted JSON into `TypedDict` without checks, contort runtime design solely for checker appeasement.
- **Failure modes / counterexample:** false security, checker-specific lock-in, false positives suppressing useful code, missing business validation. Counterexample: internal pure transformation with stable types may gain substantial value from strict annotations.
- **Interactions / conflicts:** FP-IMPL-009; conflict `CONF-LP-006`; authority doctrine should distinguish static finding from runtime defect.
- **Confidence / routes:** strong; coding/review/repair; signals typing configuration, external input, `Any`, casts, `TypedDict`; Python; medium/high correctness risk; prerequisite checker/toolchain evidence; high; budget 350–550.
- **Source support:** `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## About gradual typing`; `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## Flawed Typing and Strong Testing`; `FP: chapters/022-chapter-15-more-about-type-hints.md :: ## TypedDict`; `FP: chapters/022-chapter-15-more-about-type-hints.md :: ## Problems with Annotations at Runtime`.

### FP-IMPL-008 — Prefer a function when behavior has no independent state

- **Category / claim:** implementation, architecture. First-class functions can implement single-operation strategies or commands with less indirection than parallel one-method class hierarchies.
- **Decision rule:** use a function/callable reference when variants share a stable call shape and require no meaningful lifecycle or encapsulated state. Use a callable object or class when state, identity, multiple related operations, substitution contracts, or framework integration justify it.
- **Applicable / not:** callbacks, policies, transformations, simple strategies; not for eliminating cohesive objects or violating an accepted class-based plugin contract.
- **Required / insufficient evidence:** required—variant state/lifecycle, call sites, discovery/configuration needs, existing extension contract. Insufficient—line count alone, dislike of classes, or abstract pattern names.
- **Inputs / outputs:** behavior-variant inventory; output is function, callable object, or class with rationale.
- **Preserve; safe / unsafe:** preserve strategy identity, configuration, error behavior, discoverability, test seams. Safe—named functions and explicit registry. Unsafe—anonymous lambdas for complex policy, import-time global registration without ownership, closures hiding mutable lifecycle.
- **Failure modes / counterexample:** boilerplate hierarchy, inscrutable closure, global registry coupling. Counterexample: stateful retry policy with metrics and lifecycle may deserve an object.
- **Interactions / conflicts:** FP-IMPL-016, FP-IMPL-017; abstraction doctrine from implementation lane.
- **Confidence / routes:** contextual/strong; coding/architecture/review; signals many one-method classes, stateless variants; Python; normal risk; exclude framework-mandated classes; prerequisite call/state inventory; normal; budget 300–450.
- **Source support:** `FP: chapters/013-chapter-7-functions-as-first-class-objects.md :: ## User-Defined Callable Types`; `FP: chapters/016-chapter-10-design-patterns-with-first-class-functions.md :: ## Function-Oriented Strategy`; `FP: chapters/016-chapter-10-design-patterns-with-first-class-functions.md :: ## Chapter Summary`.

### FP-IMPL-009 — Choose the least powerful interface mechanism that proves the contract

- **Category / claim:** implementation, architecture, review. Duck typing, static `Protocol`, ABC, and concrete nominal type are complementary mechanisms with increasing explicitness and runtime coupling.
- **Decision rule:** use ordinary duck typing for local/simple immediate use; a static `Protocol` when multiple unrelated implementations need checked structural substitution; an ABC when runtime membership, shared framework behavior, registration, or an explicit extension contract is required; a concrete type when substitution is not intended.
- **Applicable / not:** API boundaries and plugin/framework design; not permission to create interfaces before variation or independent consumers exist.
- **Required / insufficient evidence:** required—number/ownership of implementations, consumer operations, runtime versus static enforcement need, extension stability, failure timing. Insufficient—test mocking alone, directory separation, or desire to “decouple.”
- **Inputs / outputs:** consumers, implementations, enforcement timing; output is no abstraction, protocol, ABC, or concrete dependency.
- **Preserve; safe / unsafe:** preserve behavioral contract beyond method presence. Safe—small consumer-shaped protocols, fail-fast attempted operation, standard ABC reuse. Unsafe—large speculative protocol, runtime-check result treated as behavior proof, monkey-patching uncontrolled production objects.
- **Failure modes / counterexample:** interface inflation, nominal coupling, false structural compatibility. Counterexample: framework authors may need a stable ABC before third-party implementations exist when the extension authority and lifecycle are explicit.
- **Interactions / conflicts:** FP-IMPL-002, FP-IMPL-007, FP-IMPL-010; conflict `CONF-LP-004`.
- **Confidence / routes:** strong/contextual; coding/architecture/review; signals multiple adapters, plugin points, checker errors, `isinstance`; Python; medium API risk; prerequisite consumer evidence; high; budget 450–650.
- **Source support:** `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Two kinds of protocols`; `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Defensive programming and "fail fast"`; `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Designing a static protocol`; `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## DUCK TYPING IS YOUR FRIEND`.

### FP-IMPL-010 — Constrain inheritance to substitutability or narrow reuse

- **Category / claim:** architecture, implementation, review. Prefer composition and delegation unless inheritance expresses a stable is-a contract or framework-required extension; keep mixins narrow and avoid multiple concrete parents.
- **Decision rule:** identify whether the need is interface substitution or implementation reuse. Use an ABC/protocol for the former; prefer a collaborator/delegate for the latter unless a small, stateless, explicitly named mixin fits the repository's hierarchy.
- **Applicable / not:** class design and legacy hierarchy review; not grounds to rewrite a working framework hierarchy without demonstrated change/test pressure.
- **Required / insufficient evidence:** required—substitution behavior, MRO, override calls, framework constraints, co-change and test burden. Insufficient—tall diagram, multiple inheritance alone, aesthetic preference.
- **Inputs / outputs:** class graph and call behavior; output is retain, compose, or bounded hierarchy change.
- **Preserve; safe / unsafe:** preserve MRO, cooperative `super()`, serialization, plugin discovery, public type checks. Safe—`UserDict`/`UserList` wrappers when extension is needed, one concrete parent plus narrow mixins. Unsafe—direct built-in subclass relying on internal overridden-method dispatch; multiple concrete bases; composition migration bundled with semantic change.
- **Failure modes / counterexample:** brittle MRO, hidden coupling, duplicated delegation, abstract ceremony. Counterexample: a framework explicitly designed around cooperative mixins may justify them when tests cover order and contracts.
- **Interactions / conflicts:** FP-IMPL-009, FP-IMPL-016.
- **Confidence / routes:** strong/contextual; architecture/coding/review/refactoring; signals built-in subclass, MRO conflicts, mixin forests; Python; high structural risk; prerequisite behavior characterization; normal/high; budget 400–600.
- **Source support:** `FP: chapters/021-chapter-14-inheritance-for-good-or-for-worse.md :: ## Subclassing Built-In Types Is Tricky`; `FP: chapters/021-chapter-14-inheritance-for-good-or-for-worse.md :: ## Coping with Multiple Inheritance`; `FP: chapters/021-chapter-14-inheritance-for-good-or-for-worse.md :: ## 8. "Favor Object Composition Over Class Inheritance."`.

### FP-IMPL-011 — Preserve special-method algebra and expectations

- **Category / claim:** implementation, review. Operator, equality, hash, slicing, representation, and formatting methods must obey Python's conventional invariants; syntactic convenience does not justify surprising semantics.
- **Decision rule:** implement a special method only when the domain operation is recognizable and tests can state its laws. Non-in-place arithmetic should not mutate operands; equal hashable objects must hash equally; unsupported mixed operands should normally return `NotImplemented`; slicing should follow the represented collection's expected result semantics.
- **Applicable / not:** library/domain values and custom collections; not for arbitrary domain verbs or clever notation.
- **Required / insufficient evidence:** required—domain meaning, standard precedent, operand/result types, laws and property/edge tests. Insufficient—operator availability, reduced character count, or one happy-path example.
- **Inputs / outputs:** domain algebra and client expectation; output is method or explicit named alternative.
- **Preserve; safe / unsafe:** preserve mutation, commutativity/order where promised, exception dispatch, hash stability. Safe—delegate and return `NotImplemented`. Unsafe—mutate under `+`, hash mutable state, make `repr` perform I/O, accept operands with ambiguous meaning.
- **Failure modes / counterexample:** broken dict/set lookup, asymmetric equality, surprising side effects. Counterexample: in-place `+=` may mutate when that matches the type's documented mutable-sequence semantics.
- **Interactions / conflicts:** FP-IMPL-002, FP-IMPL-004.
- **Confidence / routes:** strong; coding/review/repair; signals dunder implementation, custom value/collection; Python; high correctness/API risk; prerequisite invariant tests; high; budget 350–500.
- **Source support:** `FP: chapters/018-chapter-11-a-pythonic-object.md :: ## A Hashable Vector2d`; `FP: chapters/019-chapter-12-writing-special-methods-for-sequences.md :: ## A Slice-Aware \_\_getitem\_\_`; `FP: chapters/023-chapter-16-operator-overloading-doing-it-right.md :: ## Chapter Summary`.

### FP-IMPL-012 — Stream when materialization is not part of the contract

- **Category / claim:** implementation, performance. Generators and iterators reduce peak memory and decouple stages when consumers can process items incrementally; their single-pass and deferred-execution semantics are real costs.
- **Decision rule:** choose streaming when input may be large/unbounded, stages can consume sequentially, and ownership/resource lifetime can span iteration. Materialize when callers require replay, random access, stable snapshot, count, eager validation, or independent lifetime.
- **Applicable / not:** ETL, file/database traversal, transform pipelines; not automatically for small reused collections or APIs promising sequences.
- **Required / insufficient evidence:** required—cardinality, access/replay pattern, error timing, resource lifetime, memory baseline. Insufficient—generator syntax alone or theoretical O(1) memory without accounting for downstream buffering.
- **Inputs / outputs:** consumption contract and data size; output is iterable/iterator/sequence API and lifetime tests.
- **Preserve; safe / unsafe:** preserve ordering, exception timing where contractual, cleanup/cancellation. Safe—separate iterable from iterator, generator function for multi-line logic, context-manage underlying resource. Unsafe—return generator over a closed file/session, make reusable object its own iterator, silently change eager validation to deferred failure.
- **Failure modes / counterexample:** exhausted iterator reuse, resource leak, partial side effects, hidden latency. Counterexample: materializing a small result for atomic validation and repeat access can be clearer and safer.
- **Interactions / conflicts:** FP-IMPL-003, FP-IMPL-013, EGO-PERF-009; conflict `CONF-LP-005`.
- **Confidence / routes:** strong/contextual; coding/performance/review; signals large input, list built only to feed loop, memory pressure; Python; medium correctness/resource risk; prerequisite consumer/lifetime inventory; high; budget 350–550.
- **Source support:** `FP: chapters/007-chapter-2-an-array-of-sequences.md :: ## Generator Expressions`; `FP: chapters/024-chapter-17-iterables-iterators-and-generators.md :: ## Don't make the iterable an iterator for itself`; `FP: chapters/024-chapter-17-iterables-iterators-and-generators.md :: ## Case Study: Generators in a Database Conversion Utility`.

### FP-IMPL-013 — Bind cleanup to lexical or structured lifetime

- **Category / claim:** universal, implementation, repair. External resources and paired state transitions should be released deterministically through context managers or an equivalently explicit lifecycle, including error and cancellation paths.
- **Decision rule:** whenever acquisition requires release/commit/rollback/restore, use `with`/`async with`, `contextlib`, or an existing structured owner. Rely on garbage collection only when the resource API explicitly makes nondeterministic cleanup acceptable.
- **Applicable / not:** files, locks, transactions, temporary state, network sessions, executors; not every plain in-memory object needs a context manager.
- **Required / insufficient evidence:** required—acquire/release pairs, exception and cancellation paths, runtime implementation portability. Insufficient—CPython reference-count behavior observed once or `__del__` presence.
- **Inputs / outputs:** resource lifecycle; output is structured cleanup plus failure-path tests.
- **Preserve; safe / unsafe:** preserve exception propagation/suppression contract and commit/rollback semantics. Safe—small generator context manager with `try/finally`; `ExitStack` for dynamic collections. Unsafe—silent broad exception suppression, finalizer as primary release, returning before cleanup ownership transfers.
- **Failure modes / counterexample:** descriptor/socket/file leaks, swallowed errors, double close. Counterexample: a process-lifetime singleton may have process-owned cleanup if explicitly accepted.
- **Interactions / conflicts:** FP-IMPL-012, FP-IMPL-015, EGO-PERF-014.
- **Confidence / routes:** universal/strong; coding/repair/review; signals `open`, acquire/close, transaction, lock, session; Python and language-independent; high durability risk; prerequisite lifecycle map; core; budget 250–400.
- **Source support:** `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## del and Garbage Collection`; `FP: chapters/025-chapter-18-context-managers-and-else-blocks.md :: ## Context Managers and with Blocks`; `FP: chapters/025-chapter-18-context-managers-and-else-blocks.md :: ## The contextlib Utilities`.

### FP-IMPL-014 — Select Python concurrency from workload and runtime evidence

- **Category / claim:** performance, implementation, architecture. Threads, processes, and async solve different scheduling/parallelism problems; choose from workload, dependency, deployment, and current interpreter facts rather than labels such as “I/O-bound.”
- **Decision rule:** inventory blocking operations, CPU-heavy regions, task count/duration, state sharing, cancellation, library compatibility, process serialization/startup, and deployment limits. Prefer sequential code until concurrency has a requirement; then select the least complex model meeting measured throughput/latency.
- **Applicable / not:** concurrent Python workloads; not a timeless rule that threads never run CPU in parallel—the active interpreter/build and native extensions must be verified.
- **Required / insufficient evidence:** required—profile/trace, representative load, interpreter/build, dependency blocking/GIL behavior, error/cancellation needs. Insufficient—CPU utilization snapshot, “async is faster,” `async def` syntax, core count alone, 2021 GIL assumptions.
- **Inputs / outputs:** workload/runtime matrix; output is model decision, bounded worker count, failure/cleanup plan, benchmark.
- **Preserve; safe / unsafe:** preserve ordering/atomicity/idempotency/error propagation. Safe—threads for compatible blocking I/O, processes for sufficiently coarse serializable CPU work, async for large compatible concurrent waits. Unsafe—CPU loop on event-loop thread, process pool for tiny tasks, shared mutable state without synchronization, unbounded worker/task creation.
- **Failure modes / counterexample:** slower threaded CPU path, process overhead, event-loop stalls, nondeterministic repair. Counterexample: sequential execution is correct when concurrency overhead exceeds waiting or requirement.
- **Interactions / conflicts:** FP-IMPL-015, EGO-PERF-011; conflict `CONF-LP-003`.
- **Confidence / routes:** contextual/strong procedure; performance/architecture/coding/review; signals queues, executors, async, throughput need; Python; high concurrency risk; prerequisite current runtime and profile; specialist; budget 550–800.
- **Source support:** `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## A Bit of Jargon`; `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## Processes, threads, and Python's Infamous GIL`; `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## Thread-based Non-solution`; `FP: chapters/028-chapter-21-concurrency-with-futures.md :: ## Launching Processes with concurrent.futures`.

### FP-IMPL-015 — Bound async work and keep the event loop nonblocking

- **Category / claim:** implementation, performance, durability. Cooperative concurrency is safe only if every long operation yields or is delegated, concurrency is bounded, and tasks/resources have structured completion and cancellation.
- **Decision rule:** trace each async call chain for blocking I/O/CPU and unbounded fan-out. Use async-native dependencies, semaphores/queues/backpressure, async context managers, and explicit task ownership; offload unavoidable blocking work to an appropriate executor and await completion where durability matters.
- **Applicable / not:** async services/clients; not a reason to convert synchronous code absent concurrent-wait pressure or ecosystem support.
- **Required / insufficient evidence:** required—event-loop lag/profile, dependency APIs, task cardinality, upstream/downstream capacity, timeout/cancellation/cleanup contract. Insufficient—high request count alone or a fast toy downloader against warm cache.
- **Inputs / outputs:** await graph and capacity limits; output is bounded task topology and error/cancellation tests.
- **Preserve; safe / unsafe:** preserve completion, retry/idempotency, ordering, resource closure. Safe—semaphore around scarce remote work; `async with`; `as_completed` for incremental handling; executor for demonstrated blocker. Unsafe—blocking filesystem/network/CPU call in event loop, fire-and-forget durable write, unlimited `gather`, load-test public systems irresponsibly.
- **Failure modes / counterexample:** event-loop starvation, remote DoS, lost exception/write, task leak, async contagion without benefit. Counterexample: a small synchronous CLI can remain synchronous.
- **Interactions / conflicts:** FP-IMPL-013, FP-IMPL-014, EGO-PERF-014.
- **Confidence / routes:** strong/contextual; coding/performance/review/repair; signals `asyncio`, task creation, HTTP/database clients, loop lag; Python; high operational risk; prerequisite workload/capacity contract; specialist; budget 500–750.
- **Source support:** `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## The all-or-nothing problem`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Using asyncio.as\_completed and a semaphore`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Using an Executor to Avoid Blocking the Event Loop`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Avoiding CPU-bound Traps`.

### FP-IMPL-016 — Escalate dynamic mechanisms only after repetition and framework need

- **Category / claim:** architecture, implementation, review. Properties, decorators, descriptors, class decorators, `__init_subclass__`, and metaclasses form an escalation ladder; select the least powerful mechanism that removes demonstrated repetition while keeping control flow inspectable.
- **Decision rule:** start with an ordinary function/method/attribute. Use a property to preserve a public attribute while computing or validating it; a decorator for cross-cutting callable transformation with transparent metadata; a descriptor for the same managed-field behavior repeated across fields/classes; class hooks/decorators for controlled subclass creation; a metaclass only when class-creation behavior cannot be achieved more simply and the code is framework-level.
- **Applicable / not:** libraries/frameworks and proven repeated infrastructure; generally contraindicated in application code for one-off behavior.
- **Required / insufficient evidence:** required—at least repeated concrete cases or explicit framework extension contract, import-time/lifecycle analysis, maintainer capability, tests of introspection/inheritance/serialization. Insufficient—fewer lines, novelty, hypothetical reuse, or desire to emulate another language.
- **Inputs / outputs:** repetition and extension map; output is simplest mechanism plus documented import-time effects.
- **Preserve; safe / unsafe:** preserve public access, introspection, pickling, MRO, import determinism, type-checker behavior. Safe—property-based compatible API evolution; `functools.wraps`; metaclass hidden behind regular base. Unsafe—global side effects at import without ownership, `__getattribute__` for a narrow case, metaclass exposed as user requirement, mechanism change bundled with behavior repair.
- **Failure modes / counterexample:** hidden execution, recursion, descriptor shadowing, metaclass conflicts, type-checker blind spots. Counterexample: ORM/serialization frameworks may legitimately centralize class creation behind tested metaprogramming.
- **Interactions / conflicts:** FP-IMPL-008, FP-IMPL-009, FP-IMPL-018; conflict `CONF-LP-004`.
- **Confidence / routes:** strong/contextual; architecture/coding/review; signals repeated properties, descriptors, decorators, metaclass, dynamic attrs; Python; high cognitive/framework risk; prerequisite simpler-alternative analysis; specialist; budget 600–900.
- **Source support:** `FP: chapters/030-chapter-23-dynamic-attributes-and-properties.md :: ## Special Methods for Attribute Handling`; `FP: chapters/031-chapter-24-attribute-descriptors.md :: ## Descriptor Usage Tips`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Modern Features Simplify or Replace Metaclasses`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Metaclasses Should be Implementation Details`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Wrapping up`.

### FP-IMPL-017 — Cache only with validity, ownership, and bounds

- **Category / claim:** performance, implementation. Caching is a time/space/consistency trade, not a free decorator; a cache is earned by repeated expensive work and a definable validity policy.
- **Decision rule:** before caching, identify key identity, result determinism, invalidation/freshness, maximum cardinality/memory, concurrency, failure caching, observability, and lifecycle. Prefer bounded standard mechanisms and prove macro benefit.
- **Applicable / not:** repeated pure or tolerably stale work; not for cheap operations, unbounded high-cardinality inputs, mutable/unhashable semantics, or data requiring immediate freshness without invalidation.
- **Required / insufficient evidence:** required—profile/repeated-call evidence, hit-rate estimate/measurement, memory and stale-data limits, concurrency behavior, representative benchmark. Insufficient—function “looks expensive,” micro hit timing, or decorator availability.
- **Inputs / outputs:** workload and validity contract; output is cache design or explicit no-cache decision with metrics/regression gate.
- **Preserve; safe / unsafe:** preserve freshness, authorization/tenant isolation, exceptions, object ownership. Safe—bounded LRU with measured size; explicit invalidation; process-lifetime scope stated. Unsafe—unbounded `cache` in long process, mutable result shared unexpectedly, key omits policy/tenant/version, relying on dated thread-safety claims.
- **Failure modes / counterexample:** OOM, stale/cross-tenant data, thundering herd, key-sharing/memory regression. Counterexample: short-lived CLI with a small finite key space may use an unbounded memoization cache safely.
- **Interactions / conflicts:** FP-IMPL-004, EGO-PERF-010, EGO-PERF-013; conflict `CONF-LP-007`.
- **Confidence / routes:** strong; performance/coding/review/repair; signals `cache`, `lru_cache`, `cached_property`, bespoke dict cache; Python and language-independent; high correctness/memory risk; prerequisite profile and validity policy; high; budget 400–650.
- **Source support:** `FP: chapters/015-chapter-9-decorators-and-closures.md :: ## Memoization with functools.cache`; `FP: chapters/015-chapter-9-decorators-and-closures.md :: ## Using lru\_cache`; `FP: chapters/030-chapter-23-dynamic-attributes-and-properties.md :: ## Step 4: Bespoke Property Cache`; `FP: chapters/030-chapter-23-dynamic-attributes-and-properties.md :: ## Step 5: Caching Properties with functools`.

### FP-IMPL-018 — Evolve simple public attributes through compatible properties

- **Category / claim:** implementation, API design. Python properties allow an initially simple public attribute to gain validation or computation without a gratuitous getter/setter API; this lowers the need for speculative encapsulation.
- **Decision rule:** begin with a plain attribute when no invariant/computation exists. Convert to a property when a demonstrated invariant or compatible computation appears and public attribute syntax is already accepted.
- **Applicable / not:** owned Python APIs; not when wire/schema layout, dataclass machinery, `__slots__`, ORM instrumentation, or performance semantics make the transition incompatible.
- **Required / insufficient evidence:** required—actual invariant/computation, callers, assignment/read semantics, framework introspection, tests. Insufficient—future possibility that validation might be needed.
- **Inputs / outputs:** current API and new constraint; output is compatible property or explicit breaking-change proposal.
- **Preserve; safe / unsafe:** preserve public name, error type, serialization/introspection where contractual. Safe—setter validates at construction because `__init__` uses the public attribute. Unsafe—property performs surprising expensive I/O, caches without invalidation, silently changes mutability.
- **Failure modes / counterexample:** hidden cost, recursion, framework bypass. Counterexample: a cross-language public API may require explicit methods/schema rather than Python property semantics.
- **Interactions / conflicts:** FP-IMPL-006, FP-IMPL-016.
- **Confidence / routes:** contextual/strong; coding/API/review; signals new validation on existing field; Python; medium API risk; prerequisite caller/framework analysis; normal; budget 250–400.
- **Source support:** `FP: chapters/018-chapter-11-a-pythonic-object.md :: ## Properties Help Reduce Upfront Costs`; `FP: chapters/030-chapter-23-dynamic-attributes-and-properties.md :: ## Using a Property for Attribute Validation`.

## Candidate doctrine records: performance and Go

### EGO-PERF-001 — Disambiguate every performance claim

- **Category / claim:** universal, performance, review. “Performance” is not a decision metric until it names workload, correctness, resource, statistic, and boundary.
- **Decision rule:** rewrite a performance request as an observable claim: operation, input/data shape and scale, environment, success/failure population, latency/throughput statistic, CPU/memory/disk/network budget, and time horizon. Stop before optimization if these cannot be made meaningful.
- **Applicable / not:** all performance diagnosis/recommendation; not needed for a purely functional defect except to avoid scope drift.
- **Required / insufficient evidence:** required—user/SLO/operational requirement and measurement semantics. Insufficient—“slow,” average alone, CPU percentage without interval/capacity, heap bytes presented as total process memory, or isolated anecdote.
- **Inputs / outputs:** complaint and system boundary; output is a falsifiable efficiency requirement or a request for missing authority/input.
- **Preserve; safe / unsafe:** preserve correctness and workload meaning. Safe—distinguish accuracy, speed, and efficiency; record uncertainty. Unsafe—optimize an unspecified metric or silently select a favorable percentile.
- **Failure modes / counterexample:** metric substitution, benchmark theater, improvement of irrelevant operation. Counterexample: an obvious infinite loop is first a correctness defect; it may be repaired without a formal performance campaign.
- **Interactions / conflicts:** EGO-PERF-003, EGO-PERF-005, authority model observation→diagnosis.
- **Confidence / routes:** universal; performance/review/architecture/repair; tasks triage or recommendation; signals “slow,” “uses too much”; language-independent; all risk; prerequisite measurable boundary; core; budget 250–400.
- **Source support:** `EGO: chapters/005-chapter-1-software-efficiency-matters.md :: ### Clarify When Someone Uses the Word "Performance"`; `EGO: chapters/010-chapter-6-efficiency-observability.md :: ### Efficiency Metrics Semantics`.

### EGO-PERF-002 — Separate reasonable efficiency from deliberate optimization

- **Category / claim:** universal, performance, implementation. Small obvious reductions of unnecessary work can be ordinary implementation choices; transformations with trade-offs require a measured campaign.
- **Decision rule:** treat a change as reasonable only when it removes evident work, does not reduce functionality or readability materially, has a local proof, and introduces negligible semantic/maintenance risk. Otherwise require baseline, target, profile, alternatives, and regression protection.
- **Applicable / not:** coding and performance planning; not permission to smuggle speculative micro-optimization into feature work.
- **Required / insufficient evidence:** required for reasonable change—direct local evidence and tests; for deliberate change—EGO-PERF-003 through EGO-PERF-008. Insufficient—“best practice,” theoretical cycle saving, or hardware/scaling optimism.
- **Inputs / outputs:** candidate and trade-offs; output is ordinary implementation, deferred hypothesis, or authorized performance campaign.
- **Preserve; safe / unsafe:** preserve behavior, clarity, portability. Safe—avoid duplicate conversion/work in a hot or obvious local path. Unsafe—unsafe conversion, pooling, concurrency, caching, runtime tuning, or specialization under the “reasonable” label.
- **Failure modes / counterexample:** premature pessimization on one side; premature optimization on the other. Counterexample: an inefficient but cold clear path should normally remain unchanged.
- **Interactions / conflicts:** EGO-PERF-004, EGO-PERF-012; conflict `CONF-LP-002`.
- **Confidence / routes:** strong; coding/performance/review; tasks feature implementation or optimization classification; signals optimization mixed into feature diff; language-independent; medium scope risk; prerequisite trade-off inventory; core; budget 300–450.
- **Source support:** `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Reasonable Optimizations`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Deliberate Optimizations`; `EGO: chapters/005-chapter-1-software-efficiency-matters.md :: ### The Key to Pragmatic Code Performance`.

### EGO-PERF-003 — Resource-Aware Efficiency Requirement

- **Category / claim:** performance, agent-conduct. A performance change is earned by a requirement that binds an important operation and representative input to explicit resource/latency limits.
- **Decision rule:** record operation, input shape/scale, environment, concurrency, correctness precondition, latency percentile or throughput, CPU time/quota, memory measure/peak, disk/network limits, and acceptable variance. Negotiate or escalate when constraints conflict.
- **Applicable / not:** deliberate optimization, capacity and architecture decisions; not every low-risk coding choice needs a full record.
- **Required / insufficient evidence:** required—accepted user/SLO/incident/operational constraint and representative workload. Insufficient—historical benchmark detached from version, averages without distribution, arbitrary “faster is better.”
- **Inputs / outputs:** accepted constraint; output is RAER-like target plus baseline and owner.
- **Preserve; safe / unsafe:** preserve functional requirements and define acceptable trade space. Safe—prioritize important operations/resources. Unsafe—optimize all operations or choose target after seeing favorable result.
- **Failure modes / counterexample:** impossible multi-resource target, workload gaming, requirement drift. Counterexample: exploratory profiling may proceed without authorization to change, but must not become an execution recommendation.
- **Interactions / conflicts:** EGO-PERF-001, EGO-PERF-004, EGO-PERF-017; authority selection/authorization.
- **Confidence / routes:** strong; performance/architecture/review; signals SLO breach, capacity issue, cost target; language-independent; high operational risk; prerequisite authorized objective; core; budget 400–600.
- **Source support:** `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Efficiency Requirements Should Be Formalized`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Resource-Aware Efficiency Requirements`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Acquiring and Assessing Efficiency Goals`.

### EGO-PERF-004 — Test–Benchmark–Profile–Optimize loop

- **Category / claim:** universal, performance procedure. A deliberate optimization campaign must minimize simultaneous uncertainty: prove behavior, measure baseline, locate bottleneck, change one lever, then re-prove behavior and measurement.
- **Decision rule:** run functional/characterization tests; capture versioned baseline against EGO-PERF-003; if within target stop; otherwise profile representative run, choose one bottleneck and one design level, make one reversible transformation, rerun identical correctness and performance gates, retain or revert based on target and trade-offs.
- **Applicable / not:** deliberate optimization; not necessary for trivial compile-time cleanup with no performance claim.
- **Required / insufficient evidence:** required—stable tests, valid baseline, profile, controlled comparison. Insufficient—before/after wall-clock once, several simultaneous changes, or profile from a different workload/version.
- **Inputs / outputs:** RAER, tests, benchmark, profile; output is verified gain, rejected hypothesis, or escalation.
- **Preserve; safe / unsafe:** preservation boundary includes functional output, errors, ordering, resource cleanup, concurrency semantics, public APIs unless authorized. Safe—small commits and artifact retention. Unsafe—fix correctness and tune structure in the same comparison; move benchmark goalposts.
- **Failure modes / counterexample:** causal ambiguity, benchmark overfit, unreproducible gain. Counterexample: emergency mitigation may use a reversible operational limit before full diagnosis, but needs follow-up and explicit authority.
- **Interactions / conflicts:** EGO-PERF-006, EGO-PERF-008, EGO-PERF-017; change-type taxonomy optimization versus repair/refactoring.
- **Confidence / routes:** universal/strong; performance/coding/repair/review; signals deliberate optimization; language-independent; high risk; prerequisite authority and preservation boundary; core; budget 500–700.
- **Source support:** `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Efficiency-Aware Development Flow`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Functionality Phase`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Efficiency Phase`; `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Optimize One Thing at a Time`.

### EGO-PERF-005 — Document measurement semantics before interpreting a signal

- **Category / claim:** performance, observability. A metric is usable evidence only when its boundary, unit, aggregation, granularity, population, and collection overhead are known.
- **Decision rule:** for every signal, record what starts/stops the measurement, success/failure inclusion, wall versus CPU time, instantaneous gauge versus cumulative counter, heap versus RSS/WSS, percentile/window, sampling/aggregation, labels/cardinality, and instrumentation cost.
- **Applicable / not:** logs, traces, metrics, profiles, benchmarks; not a demand to instrument every path.
- **Required / insufficient evidence:** required—instrument definition/config and a sanity check against runtime behavior. Insufficient—metric name, dashboard label, gauge that can miss spikes, high-cardinality raw events presented as sustainable metric.
- **Inputs / outputs:** signal and collection path; output is evidence statement with limitations.
- **Preserve; safe / unsafe:** preserve system reliability and privacy; measurement must not materially perturb target without disclosure. Safe—measure both successful and failed operations when relevant; percentiles for tails. Unsafe—average away tail requirements, confuse CPU time with elapsed time, compare heap to container RSS as equivalents.
- **Failure modes / counterexample:** wrong-boundary optimization, cardinality outage, observer effect. Counterexample: a temporary high-detail trace can be justified for bounded diagnosis if overhead/retention is controlled.
- **Interactions / conflicts:** EGO-PERF-001, EGO-PERF-006, EGO-PERF-010.
- **Confidence / routes:** universal/strong; performance/repair/review/operations; signals dashboards/profiles/telemetry; language-independent; high evidence risk; prerequisite instrumentation access; core; budget 350–550.
- **Source support:** `EGO: chapters/010-chapter-6-efficiency-observability.md :: ### Observability`; `EGO: chapters/010-chapter-6-efficiency-observability.md :: #### High Metric Cardinality`; `EGO: chapters/010-chapter-6-efficiency-observability.md :: ### Efficiency Metrics Semantics`; `EGO: chapters/010-chapter-6-efficiency-observability.md :: ### Latency`; `EGO: chapters/010-chapter-6-efficiency-observability.md :: ### Memory Usage`.

### EGO-PERF-006 — Benchmark validity precedes benchmark interpretation

- **Category / claim:** performance, review. A benchmark comparison is evidence only when code, dependencies, benchmark, workload, environment, correctness, and variance are controlled closely enough for the claimed conclusion.
- **Decision rule:** record exact versions/configuration; validate benchmark output and setup boundaries; use representative inputs; compare nearby A/B runs on stable infrastructure; repeat long enough to expose variance; report distributions/significance without using statistics to conceal instability; reject stale or nonreproducible comparisons.
- **Applicable / not:** micro, macro, load, and stress tests; not all diagnostics require CI-stable numeric gates.
- **Required / insufficient evidence:** required—artifact versions, correctness assertions, environment/resource limits, repeated samples, raw results, variance. Insufficient—single run, shared noisy CI without controls, old number, different hardware/config, compiler-eliminated work, warm-cache-only claim.
- **Inputs / outputs:** benchmark design and claim; output is valid comparison, bounded observational result, or invalid-evidence finding.
- **Preserve; safe / unsafe:** preserve workload equivalence and functional results. Safe—version benchmark/container image; inspect implausible iteration rates. Unsafe—compare across unrelated runs, delete outliers without cause, use sink variables everywhere without elimination evidence.
- **Failure modes / counterexample:** benchmark lies through interpretation, thermal/background noise, data compressibility mismatch, dead-code elimination. Counterexample: exploratory benchmark can guide the next hypothesis if labeled non-decisive.
- **Interactions / conflicts:** EGO-PERF-004, EGO-PERF-007; evidence taxonomy profiling/runtime observation.
- **Confidence / routes:** universal/strong; performance/review; signals benchmark result or regression claim; language-independent with Go specialization; high evidence risk; prerequisite EGO-PERF-003; core; budget 500–750.
- **Source support:** `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Benchmarks Lie`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Reliability of Experiments`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Reproducing Production`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Performance Nondeterminism`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Test Your Benchmark for Correctness!`.

### EGO-PERF-007 — Match benchmark level to the claim

- **Category / claim:** performance. Microbenchmarks isolate causal code-level differences; macrobenchmarks establish process/system behavior; production monitoring establishes deployed behavior. None substitutes for the others.
- **Decision rule:** use microbenchmarks for a profiled local bottleneck and relative implementation A/B; macrobenchmarks for end-to-end latency, dependencies, scheduler/GC interactions, maximum memory, and resource limits; production signals for actual workload drift and SLOs. Require a higher-level gate when a local change can alter system behavior.
- **Applicable / not:** performance campaign design; not a requirement to build an expensive macro harness for a harmless local experiment.
- **Required / insufficient evidence:** required—claim-to-level mapping and known omissions. Insufficient—allocs/op used to claim peak RSS/GC latency; macro throughput without correctness or load-generator validation; production average without controlled comparison.
- **Inputs / outputs:** proposed claim; output is experiment level(s) and escalation gate.
- **Preserve; safe / unsafe:** preserve end-to-end semantics/dependency behavior. Safe—micro feedback followed by relevant macro regression. Unsafe—extrapolate absolute production capacity from a microbenchmark.
- **Failure modes / counterexample:** local win/system loss, harness dominates result, dependency cache artifacts. Counterexample: a pure algorithm chosen for a reusable library can reasonably be compared with a parameterized microbenchmark before any application exists, with limited claims.
- **Interactions / conflicts:** EGO-PERF-006, EGO-PERF-010, EGO-PERF-013.
- **Confidence / routes:** strong; performance/review/architecture; signals microbenchmark or end-to-end claim; language-independent; medium/high evidence risk; prerequisite claim definition; high; budget 350–500.
- **Source support:** `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Benchmarking Levels`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Microbenchmarks`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Macrobenchmarks`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Microbenchmarks Versus Memory Management`.

### EGO-PERF-008 — Profile representative work before changing a bottleneck

- **Category / claim:** performance, debugging. Resource consumption visible near a symptom is not necessarily root cause; use an appropriate profile and understand its sampling/granularity semantics before selecting work.
- **Decision rule:** reproduce the target workload; choose CPU, allocation/in-use heap, goroutine, block/mutex, trace/off-CPU or continuous profile by symptom; inspect direct and cumulative contribution; account for goroutine boundaries, hidden nodes, sample rate, and time interval; correlate with code and runtime observations.
- **Applicable / not:** deliberate optimization and unexplained resource issue; not proof that the highest frame is inherently defective.
- **Required / insufficient evidence:** required—representative profile with versions and interval, profile semantics, reproducible contribution. Insufficient—one stack sample, cumulative parent across asynchronous boundary, sampled percent treated as exact absolute time, “unknown” frame assumption.
- **Inputs / outputs:** symptom/RAER and workload; output is ranked bottleneck hypotheses with confidence and next experiment.
- **Preserve; safe / unsafe:** profiling should be bounded and overhead/retention understood. Safe—compare/merge profiles only with compatible samples; retain raw artifact. Unsafe—optimize a red herring, expose sensitive profile data, start always-on profiling without cost analysis.
- **Failure modes / counterexample:** profiler blind spot, attribution error, profile perturbation, goroutine leak mistaken for CPU issue. Counterexample: complexity analysis may identify an unavoidable asymptotic problem before a mature profiler exists, but empirical verification remains required.
- **Interactions / conflicts:** EGO-PERF-005, EGO-PERF-009, EGO-PERF-010.
- **Confidence / routes:** universal/strong; performance/repair/review; signals CPU/memory/latency issue; Go specialist and language-independent principle; high; prerequisite reproducible workload; core; budget 550–800.
- **Source support:** `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: ## Root Cause Analysis, but for Efficiency`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: #### Statistical Profiles Are Not 100% Precise`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: ### Choose Your Granularity`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: #### Be Careful When Goroutines Are Involved`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: #### Profile First, Ask Questions Later`.

### EGO-PERF-009 — Prefer work elimination and algorithm/data change before micro-tuning

- **Category / claim:** universal, performance. The highest-leverage optimization usually changes how much work or memory is required; compiler/runtime/hardware tricks come after system and algorithm/data choices are exhausted or disproven.
- **Decision rule:** for the profiled bottleneck, ask in order: can the work be removed/avoided/batched/streamed/precomputed; can algorithmic complexity or representation improve for the target distribution; can data movement/allocation reduce; only then consider code, runtime/OS, or hardware tuning. Verify constant factors empirically.
- **Applicable / not:** deliberate optimization; sometimes a fixed tiny hot loop legitimately favors micro-tuning when algorithm cannot change.
- **Required / insufficient evidence:** required—profile contribution, input scaling/distribution, complexity model, equivalent behavior tests, benchmark. Insufficient—Big O alone, because constants and real input range can reverse it; “standard library must be fastest.”
- **Inputs / outputs:** bottleneck, algorithm, data shape; output is ranked transformations at the least risky effective level.
- **Preserve; safe / unsafe:** preserve result, precision, ordering, failure, memory and latency budgets. Safe—stream instead of materialize when contract permits; specialize parser for proven narrow format. Unsafe—select asymptotically better algorithm that loses at actual range without measurement; reduce work by silently reducing functionality.
- **Failure modes / counterexample:** micro-tuning irrelevant code, complexity theater, hidden conversion cost. Counterexample: compiler-friendly local rewrite can be appropriate when it is the measured remaining bottleneck and clearer or equally clear.
- **Interactions / conflicts:** FP-IMPL-003, FP-IMPL-012, EGO-PERF-012.
- **Confidence / routes:** universal/strong; performance/architecture/coding; signals scaling curve or hot algorithm; language-independent; high semantic risk; prerequisite profile and input distribution; core; budget 400–650.
- **Source support:** `EGO: chapters/011-chapter-7-data-driven-efficiency-assessment.md :: ### Practical Applications`; `EGO: chapters/011-chapter-7-data-driven-efficiency-assessment.md :: #### Worse Is Sometimes Better!`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Optimization Design Levels`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Do Less Work`.

### EGO-PERF-010 — Match memory evidence to ownership and lifecycle

- **Category / claim:** performance, repair. Memory diagnosis must distinguish virtual address space, resident/working set, Go heap, allocation rate, live objects, stack, mappings, and retained backing storage; each supports different conclusions.
- **Decision rule:** start from the violated memory requirement; choose the corresponding OS/runtime measure and time series; profile allocation and in-use objects; trace ownership/lifetime; inspect slices/views/pools/caches/goroutines that retain larger structures; reduce live work/allocations before GC/off-heap tuning.
- **Applicable / not:** OOM, memory-limit, GC/CPU, latency, or retention issues; not every small heap delta is actionable.
- **Required / insufficient evidence:** required—metric semantics, peak/steady timeline, heap and OS correlation, live-object/retention evidence, representative macro run. Insufficient—VSS alone, small KB microbenchmark change, allocs/op alone for peak memory, `GOMEMLIMIT` assumed hard cap.
- **Inputs / outputs:** memory requirement, metrics/profile, ownership graph; output is leak/retention/allocation hypothesis and bounded remedy.
- **Preserve; safe / unsafe:** preserve data lifetime/aliasing, correctness, OS/container limits. Safe—release references/resources, stream, right-size/preallocate known bounds. Unsafe—off-heap/mmap/forced GC first, pool without lifecycle proof, reslice tiny view of huge backing array indefinitely.
- **Failure modes / counterexample:** optimize heap while RSS is mapping/page-cache issue, pool increases retention, pointer rewrite increases escape. Counterexample: a deliberate mmap design can be right for large random-access datasets when OS and lifetime semantics are understood.
- **Interactions / conflicts:** FP-IMPL-004, FP-IMPL-017, EGO-PERF-013, EGO-PERF-014.
- **Confidence / routes:** strong; performance/repair/review; signals OOM, RSS/heap gap, GC spike, memory limit; Go specialist + universal principle; high durability risk; prerequisite metric boundary; specialist; budget 600–850.
- **Source support:** `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: ### Do We Have a Memory Problem?`; `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: ### Go Memory Management`; `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: #### Most of the Time, It's Enough to Optimize the Heap Usage`; `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: #### GOMEMLIMIT Does Not Prevent Your Program from Allocating More than the Set Value!`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Overusing Memory with Arrays`.

### EGO-PERF-011 — Earn and bound concurrency in Go

- **Category / claim:** performance, implementation. Goroutines and channels are not free parallelism; add concurrency only when a measured bottleneck is parallelizable and work per task can amortize scheduling, coordination, synchronization, and memory costs.
- **Decision rule:** first remove unnecessary work and improve sequential algorithm/data path. Then model dependency/ordering, choose bounded worker count or sharding, establish cancellation/error/closure ownership, and compare sequential versus concurrent implementations under representative load and resource limits.
- **Applicable / not:** independent/coarsely partitionable work with throughput/latency pressure; not tiny operations, sequential dependencies, or unbounded per-item goroutines.
- **Required / insufficient evidence:** required—profile, task-size distribution, concurrency requirement, baseline, race/leak tests, macro CPU/memory/latency. Insufficient—idle cores, goroutine syntax, micro throughput ignoring coordination or errors.
- **Inputs / outputs:** work graph and target; output is no-concurrency, worker pool, sharding, or other bounded topology.
- **Preserve; safe / unsafe:** preserve result ordering if contractual, error/cancellation, exactly/at-least-once semantics, resource ownership. Safe—bounded concurrency and explicit wait/stop. Unsafe—goroutine per item without cap, channel-heavy coordination dominating work, shared mutation without synchronization, GOMAXPROCS folklore applied without current verification.
- **Failure modes / counterexample:** slower path, leaks, races, nondeterminism, memory explosion. Counterexample: naturally independent long network waits may justify concurrency from functional throughput requirements even before CPU profiling.
- **Interactions / conflicts:** FP-IMPL-014, EGO-PERF-014; conflict `CONF-LP-003`.
- **Confidence / routes:** strong/contextual; performance/coding/review; signals goroutines/channels/worker pools; Go; high concurrency risk; prerequisite profile and lifecycle design; specialist; budget 550–800.
- **Source support:** `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: ### When to Use Concurrency`; `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: #### Adding Concurrency Should Be One of Our Last Deliberate Optimizations to Try`; `EGO: chapters/014-chapter-10-optimization-examples.md :: ### Optimizing Latency Using Concurrency`; `EGO: chapters/014-chapter-10-optimization-examples.md :: ### A Worker Approach Without Coordination (Sharding)`.

### EGO-PERF-012 — Specialize only a proven critical path

- **Category / claim:** performance, architecture. A direct/specialized implementation may outperform a generic abstraction, but it is earned only by a stable narrow workload and a measured material gain exceeding duplication and semantic risk.
- **Decision rule:** retain generic/library path by default. Specialize when a profile identifies it as material, input/semantics can be narrowed explicitly, tests compare against a reference implementation, and macro benefit clears the target. Isolate specialization behind a local boundary and retain an easy fallback.
- **Applicable / not:** parsers, encoders, layouts, zero-copy conversions, hot generic calls; not cold paths or speculative future load.
- **Required / insufficient evidence:** required—profile contribution, representative A/B, stable input contract, equivalence tests/fuzzing, maintenance owner, reversal plan. Insufficient—genericity dislike or micro gain without end-to-end impact.
- **Inputs / outputs:** hot operation and reference semantics; output is retained generic path or bounded specialized path.
- **Preserve; safe / unsafe:** preserve all authorized inputs/errors/edge cases or explicitly narrow contract with authority. Safe—specialized parser with reference oracle. Unsafe—unsafe zero-copy without lifetime/immutability proof, forked standard-library logic with no parity tests.
- **Failure modes / counterexample:** divergence, security edge-case loss, optimization spread. Counterexample: generic implementation remains right when savings are below RAER significance.
- **Interactions / conflicts:** EGO-PERF-002, EGO-PERF-009; conflict `CONF-LP-002`.
- **Confidence / routes:** contextual/strong; performance/coding/review; signals generic function in hot profile, unsafe conversion; Go and language-independent; high correctness/maintenance risk; prerequisite valid benchmark and preservation oracle; specialist; budget 500–750.
- **Source support:** `EGO: chapters/014-chapter-10-optimization-examples.md :: ### Optimizing bytes.Split`; `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Standard Functions Might Not Be Perfect for All Cases`; `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Deliberate Trade-offs`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: #### Generic Implementations`.

### EGO-PERF-013 — Reduce, then reuse, then recycle

- **Category / claim:** performance. For allocation/GC pressure, first eliminate or shrink allocations, then safely reuse owned memory, and only then consider pooling, GC tuning, or off-heap recycling.
- **Decision rule:** use allocation profile and macro memory evidence; remove work/copies; preallocate when size is reliably known; reuse only with exclusive ownership and reset rules; pool only when allocation cost remains material and retention/concurrency behavior improves at macro level.
- **Applicable / not:** allocation/GC bottlenecks; not a blanket rule to preallocate/pool all objects.
- **Required / insufficient evidence:** required—allocation hot spot, object size/lifetime, upper-bound estimate, macro GC/RSS result. Insufficient—one fewer alloc/op, theoretical reuse, microbenchmark that omits pool retention or contention.
- **Inputs / outputs:** allocation/lifecycle evidence; output is selected R stage and regression gate.
- **Preserve; safe / unsafe:** preserve ownership, zeroing/sensitive data, alias validity. Safe—capacity hint for known count, local buffer reuse. Unsafe—reuse while references escape, oversized permanent capacity, `sync.Pool` as cache, manual GC/off-heap before reduce/reuse.
- **Failure modes / counterexample:** memory retention, stale data, race, pool slower than allocation. Counterexample: unknown/unbounded size should grow normally or stream rather than reserve worst case.
- **Interactions / conflicts:** EGO-PERF-010, EGO-PERF-007, FP-IMPL-017.
- **Confidence / routes:** strong; performance/coding/review; signals alloc profile, GC CPU, pooling; Go specialist; high memory/concurrency risk; prerequisite profile and macro gate; specialist; budget 450–700.
- **Source support:** `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### The Three Rs Optimization Method`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Reduce Allocations`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Reuse Memory`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Recycle`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Memory Reuse and Pooling`.

### EGO-PERF-014 — Own goroutine and resource lifecycles

- **Category / claim:** universal, durability, implementation. Every spawned goroutine and opened/iterated resource needs a defined owner, stop condition, completion observation, and cleanup on every return/error/cancellation path.
- **Decision rule:** at creation, state who cancels/closes, whether caller waits, how errors propagate, what happens on partial consumption, and how completion is tested. Prefer structured scopes and `defer` placed immediately after successful acquisition where its timing is correct.
- **Applicable / not:** goroutines, files, response bodies, iterators/streams, timers; not a demand that every background process terminate before program exit when process-lifetime ownership is explicit.
- **Required / insufficient evidence:** required—control-flow/error-path audit, leak/race tests, cancellation test, resource counters where possible. Insufficient—happy path, finalizer, assumption that receiver closes sender-owned channel, or empty goroutine profile once.
- **Inputs / outputs:** lifecycle graph; output is ownership contract and cleanup implementation/tests.
- **Preserve; safe / unsafe:** preserve partial-result/error semantics and close ordering. Safe—exhaust or close body as API requires; stop and wait when caller owns goroutine. Unsafe—leak on early return, close from wrong owner, launch without cancellation or error observation.
- **Failure modes / counterexample:** goroutine/file/socket leak, deadlock, lost error, premature close. Counterexample: intentionally detached telemetry may be process-owned but must have bounded buffers and shutdown semantics.
- **Interactions / conflicts:** FP-IMPL-013, FP-IMPL-015, EGO-PERF-011.
- **Confidence / routes:** universal/strong; coding/repair/review/performance; signals `go`, `Open`, response body, stream; Go and language-independent; high durability risk; prerequisite lifecycle inventory; core; budget 350–550.
- **Source support:** `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Don't Leak Resources`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Control the Lifecycle of Your Goroutines`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Reliably Close Things`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Exhaust Things`.

### EGO-GO-001 — Keep Go packages and APIs cohesive and minimally exported

- **Category / claim:** implementation, architecture. Go package and API boundaries should expose only demonstrated consumer needs and keep implementation/private dependencies local; simplicity and standard tooling are compatibility assets.
- **Decision rule:** place behavior with the cohesive responsibility and existing package conventions; export only required cross-package names; use `internal` for enforced implementation scope; add a dependency or package only when it reduces real complexity or provides needed capability.
- **Applicable / not:** Go repository changes; not authority to repack an established module based on generic style.
- **Required / insufficient evidence:** required—package call graph, consumers, change history, tests, module/dependency policy. Insufficient—file/package size, generic “clean architecture,” or aesthetic symmetry.
- **Inputs / outputs:** repository topology and feature; output is placement/export/dependency decision.
- **Preserve; safe / unsafe:** preserve import paths, API compatibility, initialization order, build tags. Safe—unexported implementation, consumer-side narrow interface when earned. Unsafe—framework-style abstraction, broad utility package, exported symbol for testing convenience, repackaging beyond task authority.
- **Failure modes / counterexample:** package cycles, public-API burden, dependency opacity, overfragmentation. Counterexample: stable public library API may deliberately expose broader capability with compatibility commitments.
- **Interactions / conflicts:** EGO-GO-002, FP-IMPL-001, abstraction doctrine.
- **Confidence / routes:** contextual/strong; coding/architecture/review; signals Go package/API change; Go; medium/high API risk; prerequisite repo contract; high; budget 350–550.
- **Source support:** `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: ### Simplicity, Safety, and Readability Are Paramount`; `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: ### Packaging and Modules`; `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: #### Internal Packages`; `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: ### Dependencies Transparency by Default`.

### EGO-GO-002 — Keep error paths explicit and contextual

- **Category / claim:** implementation, repair, review. Go errors are ordinary explicit control flow; handle, return, or deliberately classify each error without erasing context or pretending it cannot occur.
- **Decision rule:** at each error, determine recovery ownership. Add stable contextual information at the boundary that knows it; preserve causal inspection using the repository/toolchain's accepted standard; test important failure paths and cleanup.
- **Applicable / not:** Go code; intentionally ignored errors require documented API-specific reason.
- **Required / insufficient evidence:** required—callee contract, caller recovery, current Go version/repository convention, failure tests. Insufficient—example code omitting error handling, belief the operation “cannot fail,” or dated wrapping-library recommendation.
- **Inputs / outputs:** operation/error contract; output is handled/propagated/classified error with preserved cause.
- **Preserve; safe / unsafe:** preserve sentinel/type inspection, message context, cleanup, retry semantics. Safe—wrap once with operation context using current standard/convention. Unsafe—drop error, double-log-and-return without policy, compare unstable message text, introduce third-party wrapping solely because source recommends it.
- **Failure modes / counterexample:** lost root cause, noisy duplicate logs, broken `errors.Is/As`, leaked resource. Counterexample: best-effort cleanup error may be secondary but should be combined/reported when durability requires it.
- **Interactions / conflicts:** EGO-PERF-014; failure-mode doctrine.
- **Confidence / routes:** strong but version-sensitive mechanics; coding/repair/review; signals ignored errors or wrapping change; Go; high correctness/durability risk; prerequisite current repository convention; core; budget 250–450.
- **Source support:** `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: ### Single Way of Handling Errors`; `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: #### How to Wrap Errors?`; `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: #### Never Ignore Errors!`; `EGO: chapters/003-preface.md :: ### Using Code Examples`.

### EGO-GO-003 — Do not assume pointers, generics, or Go itself are faster

- **Category / claim:** implementation, performance. Language constructs have workload- and compiler-dependent cost; pointer use, interface/generic dispatch, and specialization must be chosen for semantics first and measured on critical paths.
- **Decision rule:** choose value versus pointer from ownership, mutation, size, copy, escape, nil, and API semantics; choose generics/interfaces/specialization from consumer clarity and variation. Benchmark/profile only when the choice is material to an accepted target.
- **Applicable / not:** Go implementation and hot-path review; not a reason to benchmark every ordinary type decision.
- **Required / insufficient evidence:** required—escape/build analysis where relevant, profile, representative benchmark, semantics. Insufficient—“pointers avoid copies,” “generics are zero cost,” “Go is fast,” or one compiler version extrapolated forever.
- **Inputs / outputs:** semantic requirements and hot-path evidence; output is simplest correct construct or measured specialization.
- **Preserve; safe / unsafe:** preserve aliasing, nil behavior, interface/API, compiler compatibility. Safe—simple code that enables compiler optimization. Unsafe—manual inlining, pointer proliferation, generic abstraction before variants, relying on implementation details without toolchain pin.
- **Failure modes / counterexample:** extra allocations/escapes, alias races, larger API, benchmark-dependent design. Counterexample: a pointer is mandatory for shared mutation or large identity-bearing object independent of speed.
- **Interactions / conflicts:** EGO-PERF-009, EGO-PERF-012, EGO-GO-001.
- **Confidence / routes:** contextual/strong; coding/performance/review; signals pointer conversion, generics/interface hot path, “Go is fast”; Go; normal-to-high semantic risk; prerequisite semantics then profile; normal; budget 350–550.
- **Source support:** `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: ### Generics`; `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: #### Generic Code Will Be Faster?`; `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: ### Is Go "Fast"?`; `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: ### Values, Pointers, and Memory Blocks`; `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: #### Manual Inlining Is Rarely Needed`.

### EGO-PERF-017 — Stop when the authorized target is met or evidence fails

- **Category / claim:** universal, performance, agent-conduct. Optimization is not an open-ended search for maximum speed; stop when the accepted requirement is met, marginal gains are immaterial, preservation risk rises, or evidence becomes unreliable.
- **Decision rule:** after each single-variable comparison, check functional gates, RAER, other resource regressions, complexity/maintenance cost, and confidence. Retain only net-beneficial changes; revert failed hypotheses; escalate if meeting the target requires semantic/architectural authority not granted.
- **Applicable / not:** every performance campaign.
- **Required / insufficient evidence:** required—same validated benchmark, target, preservation tests, trade-off ledger. Insufficient—personal desire for better number, competitive benchmark, or sunk effort.
- **Inputs / outputs:** campaign result and authority; output is accept/revert/stop/escalate decision with artifacts.
- **Preserve; safe / unsafe:** preserve authorized scope and explicit uncertainty. Safe—document residual headroom and rejected paths. Unsafe—continue into unsafe/concurrent/architectural changes silently, redefine success after result.
- **Failure modes / counterexample:** optimization spiral, complexity debt, unauthorized behavior loss. Counterexample: a security/durability regression discovered during optimization blocks acceptance even if performance target is met.
- **Interactions / conflicts:** EGO-PERF-003, EGO-PERF-004; agent authority model.
- **Confidence / routes:** universal; all performance roles; signals target met or next change widens scope; language-independent; all risk; prerequisite explicit target/authority; core; budget 250–400.
- **Source support:** `EGO: chapters/007-chapter-3-conquering-efficiency.md :: #### 5. Are we within RAERs?`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### 9. Release and enjoy!`; `EGO: chapters/014-chapter-10-optimization-examples.md :: ## Sum Examples`; `EGO: chapters/014-chapter-10-optimization-examples.md :: ### Summary`.

## Negative doctrine candidates

Only operationally testable prohibitions are included. “Activation evidence” is the threshold for applying the prohibition, not an excuse to infer a defect from syntax alone.

| ID | Prohibition | Activation evidence and qualification | Source support |
|---|---|---|---|
| `NEG-LP-001` | Never replace repository-compatible Python with a preferred idiom solely because it is newer or more “Pythonic.” | Supported-version/configuration or accepted contract differs; no task benefit or migration authority. | `FP: chapters/002-preface.md :: # Preface`; `FP: chapters/018-chapter-11-a-pythonic-object.md :: ## Chapter Summary` |
| `NEG-LP-002` | Never use a comprehension only for side effects or when its transformation is no longer locally legible. | Produced collection is discarded, or control/error logic obscures intent. A short clear comprehension remains valid. | `FP: chapters/007-chapter-2-an-array-of-sequences.md :: ## List Comprehensions and Readability` |
| `NEG-LP-003` | Never assume tuple/frozen syntax makes the entire reachable value immutable. | Container holds mutable referents or hash/ownership is relied upon. | `FP: chapters/007-chapter-2-an-array-of-sequences.md :: ## Tuples as Immutable Lists`; `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## The Relative Immutability of Tuples` |
| `NEG-LP-004` | Never rely on platform-default text encoding for a persistent or cross-system format. | Data crosses process/machine/time boundary and format does not explicitly delegate encoding choice. | `FP: chapters/009-chapter-4-text-versus-bytes.md :: ## Beware of Encoding Defaults` |
| `NEG-LP-005` | Never apply lossy Unicode transformations to identifiers or user text without domain authorization. | Accent removal/case/normalization may collapse distinct values; no explicit search/display policy. | `FP: chapters/009-chapter-4-text-versus-bytes.md :: ## Extreme "Normalization": Taking Out Diacritics` |
| `NEG-LP-006` | Never use a mutable object as shared per-call default state. | Default is mutated or escapes; allocation should occur per call. | `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## Mutable Types as Parameter Defaults: Bad Idea` |
| `NEG-LP-007` | Never mutate a caller-owned argument unless mutation is an explicit API contract. | Function stores/changes mutable input and callers reasonably expect isolation. Copy cost may justify a documented borrowed/shared contract instead. | `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## Defensive Programming with Mutable Parameters` |
| `NEG-LP-008` | Never treat type hints, `TypedDict`, `cast`, or runtime-checkable method presence as runtime validation. | Values originate outside trusted typed code or business invariants matter. | `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## Flawed Typing and Strong Testing`; `FP: chapters/022-chapter-15-more-about-type-hints.md :: ## TypedDict` |
| `NEG-LP-009` | Never demand 100% annotation coverage when it degrades a useful API or implementation without risk evidence. | Metric is the only justification; repository does not mandate it for a supported reason. | `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## About gradual typing` |
| `NEG-LP-010` | Never add a custom protocol/ABC solely to enable one test double or to “decouple” one stable implementation. | No independent consumer/evolution/runtime contract; direct dependency is simpler. | `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Designing a static protocol`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Wrapping up` |
| `NEG-LP-011` | Never directly subclass a built-in mapping/list/string while assuming its internal methods honor user overrides. | Correctness depends on overridden method dispatch from other built-in operations. Prefer wrapper/User* or verify every operation. | `FP: chapters/021-chapter-14-inheritance-for-good-or-for-worse.md :: ## Subclassing Built-In Types Is Tricky` |
| `NEG-LP-012` | Never make a reusable iterable its own iterator unless the public abstraction is intentionally single-pass. | Callers need independent or repeated iteration. | `FP: chapters/024-chapter-17-iterables-iterators-and-generators.md :: ## Don't make the iterable an iterator for itself` |
| `NEG-LP-013` | Never depend on garbage collection or `__del__` as the primary cleanup protocol for scarce/external resources. | Correctness/durability needs timely release across runtimes and error paths. | `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## del and Garbage Collection`; `FP: chapters/025-chapter-18-context-managers-and-else-blocks.md :: ## Context Managers and with Blocks` |
| `NEG-LP-014` | Never block an event-loop thread with substantial synchronous I/O or CPU work without an explicit bounded delegation decision. | Async path is active and profiler/operation semantics show the call can block. | `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## The all-or-nothing problem`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Using an Executor to Avoid Blocking the Event Loop` |
| `NEG-LP-015` | Never create unbounded concurrent requests, tasks, goroutines, workers, or channels from unbounded input. | Cardinality is not hard-bounded below downstream/service capacity. | `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Using asyncio.as\_completed and a semaphore`; `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: ### When to Use Concurrency` |
| `NEG-LP-016` | Never introduce a metaclass when a function, property, descriptor, class decorator, or `__init_subclass__` satisfies the demonstrated requirement. | Simpler mechanism has not been eliminated by concrete constraints. | `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Modern Features Simplify or Replace Metaclasses`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Metaclasses Should be Implementation Details` |
| `NEG-LP-017` | Never add an unbounded cache to a long-lived or high-cardinality process without a memory and validity policy. | Key space/lifetime can grow; freshness/tenant/failure semantics are unspecified. | `FP: chapters/015-chapter-9-decorators-and-closures.md :: ## Memoization with functools.cache`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Trading Space for Time` |
| `NEG-LP-018` | Never optimize an unspecified “performance” complaint. | Operation, workload, resource/statistic, boundary, or target is missing; observation/profiling may continue but recommendation must stop. | `EGO: chapters/005-chapter-1-software-efficiency-matters.md :: ### Clarify When Someone Uses the Word "Performance"`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Resource-Aware Efficiency Requirements` |
| `NEG-LP-019` | Never claim a benchmark win from one run, stale results, changed workload/version/environment, or an unchecked benchmark. | Any causal-control item is absent or variance exceeds claimed effect. | `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Reliability of Experiments`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Avoid Comparing Efficiency with Older Experiment Results!`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Test Your Benchmark for Correctness!` |
| `NEG-LP-020` | Never use a microbenchmark alone to claim end-to-end latency, peak memory, GC behavior, or production capacity. | Claim includes process/dependency/runtime behavior excluded by isolated experiment. | `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Microbenchmarks Versus Memory Management`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Macrobenchmarks` |
| `NEG-LP-021` | Never optimize the most visible frame or highest cumulative profile entry without validating contribution and execution boundary. | Sampling/granularity/goroutine/off-CPU semantics could make it symptom or aggregator. | `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: ### Choose Your Granularity`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: #### Be Careful When Goroutines Are Involved` |
| `NEG-LP-022` | Never add concurrency as the first response to a slow algorithm or unnecessary work. | Sequential path has not been profiled/simplified and coordination cost is unmeasured. | `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: #### Adding Concurrency Should Be One of Our Last Deliberate Optimizations to Try`; `EGO: chapters/014-chapter-10-optimization-examples.md :: ### A Naive Concurrency` |
| `NEG-LP-023` | Never treat `GOMEMLIMIT` or a runtime knob as a hard allocation/container-memory guarantee. | Correctness depends on staying below a hard external limit. | `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: #### GOMEMLIMIT Does Not Prevent Your Program from Allocating More than the Set Value!` |
| `NEG-LP-024` | Never pool/reuse memory while ownership, reset, sensitivity, and retained capacity are unknown. | References may escape, concurrency exists, or macro memory benefit is unproven. | `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Reuse Memory`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Memory Reuse and Pooling` |
| `NEG-LP-025` | Never ignore a Go error because a pedagogical example omitted handling. | Production path can fail and no explicit best-effort policy owns the loss. | `EGO: chapters/003-preface.md :: ### Using Code Examples`; `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: #### Never Ignore Errors!` |
| `NEG-LP-026` | Never continue optimizing after the authorized target is met merely to improve a benchmark score. | Functional and RAER gates pass; next work adds risk/complexity without accepted requirement. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: #### 5. Are we within RAERs?`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### 9. Release and enjoy!` |

## Conflict registry

### CONF-LP-001 — Python idiom versus repository contract

- **Positions:** (A) conform to current Python idioms and standard protocols to reduce bespoke code; (B) retain local/older constructs to preserve compatibility, consistency, and public behavior.
- **Hidden assumptions:** A assumes current runtime/tooling and low migration cost; B assumes compatibility/stability costs exceed readability gains and that local form is understood.
- **Evidence favoring A:** explicit current-version floor, clean CI/tool support, new/owned API, adjacent adoption, measurable removal of adapter code.
- **Evidence favoring B:** multi-version library, framework/tool checker limitations, serialized/public contracts, vendored/generated code, narrow task authority.
- **Decision rule:** repository contracts win. Within them, prefer existing standard protocol/idiom when it improves the task; propose version-floor or broad style change separately.
- **Unresolved questions:** whether ecosystem deprecation/security pressure independently authorizes migration; current official support status must be checked.
- **Roles affected:** coding, review, repair, architecture.
- **Source support:** `FP: chapters/002-preface.md :: # Preface`; `FP: chapters/005-chapter-1-the-python-data-model.md :: ## How Special Methods Are Used`; `FP: chapters/018-chapter-11-a-pythonic-object.md :: ## Chapter Summary`.

### CONF-LP-002 — General abstraction versus hot-path specialization

- **Positions:** (A) retain generic/library abstraction for correctness, reuse, and maintenance; (B) specialize a narrow implementation to remove demonstrated critical-path work.
- **Hidden assumptions:** A assumes generic overhead is acceptable and edge-case coverage matters; B assumes workload/contract is stable, the frame is material, and equivalence can be tested.
- **Evidence favoring A:** cold/variable workload, small macro impact, broad input contract, high security/correctness surface, weak test oracle.
- **Evidence favoring B:** representative profile, RAER miss, stable narrow input, material macro gain, reference/fuzz tests, local containment and reversal.
- **Decision rule:** default to generic. Specialize only the profiled critical path with explicit narrowed assumptions and a retained semantic oracle; revert if end-to-end target benefit is immaterial.
- **Unresolved questions:** long-term drift cost and whether upstream library/compiler improvements erase the gain.
- **Roles affected:** performance, coding, review, architecture.
- **Source support:** `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Standard Functions Might Not Be Perfect for All Cases`; `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Deliberate Trade-offs`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Wrapping up`.

### CONF-LP-003 — Concurrency versus sequential simplicity

- **Positions:** (A) sequential flow minimizes coordination, nondeterminism, lifecycle, and debugging cost; (B) bounded threads/processes/coroutines/goroutines can overlap waits or parallelize appropriate work.
- **Hidden assumptions:** A assumes target is met or work is not parallelizable; B assumes sufficient independent/coarse work, resource headroom, compatible dependencies, and managed failure.
- **Evidence favoring A:** target met; tiny tasks; shared/ordered state; coordination dominates; no cancellation/leak tests; event-loop/process cost exceeds gain.
- **Evidence favoring B:** measured wait/CPU bottleneck; independent units; representative throughput gain; bounded capacity; explicit error/cancel/cleanup; macro resource gate.
- **Decision rule:** keep sequential by default. Add the least complex bounded model after simpler work reduction; select model from runtime/workload evidence and current language implementation.
- **Unresolved questions:** current CPython free-threaded/build-specific behavior and Go scheduler/container defaults; verify, do not inherit dated claims.
- **Roles affected:** performance, coding, architecture, review, repair.
- **Source support:** `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## Processes, threads, and Python's Infamous GIL`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## The Myth of I/O Bound Systems`; `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: ### When to Use Concurrency`.

### CONF-LP-004 — Dynamic protocols/metaprogramming versus explicit structure

- **Positions:** (A) structural protocols, decorators, descriptors, and class hooks remove boilerplate and enable interoperable frameworks; (B) named functions/classes and direct control flow improve local reasoning, typing, debugging, and import predictability.
- **Hidden assumptions:** A assumes repeated stable mechanism and users shielded from machinery; B assumes repetition is affordable and extension flexibility is not required.
- **Evidence favoring A:** multiple proven cases, public framework extension, protocol-shaped consumers, property-compatible API evolution, comprehensive import/introspection/inheritance tests.
- **Evidence favoring B:** one-off application need, few maintainers, checker/debugging limitations, import-order sensitivity, simpler direct implementation available.
- **Decision rule:** use the least powerful mechanism that removes demonstrated repetition; keep metaclass/descriptor machinery behind a normal API and make import-time behavior observable.
- **Unresolved questions:** whether future external consumers justify a framework—do not assume without authority/evidence.
- **Roles affected:** coding, architecture, review, legacy.
- **Source support:** `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Two kinds of protocols`; `FP: chapters/030-chapter-23-dynamic-attributes-and-properties.md :: ## Special Methods for Attribute Handling`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Modern Features Simplify or Replace Metaclasses`.

### CONF-LP-005 — Lazy streaming versus eager materialization

- **Positions:** (A) lazy generators lower peak memory and decouple producers/consumers; (B) materialized collections provide replay, random access, eager validation, atomicity, length, and independent resource lifetime.
- **Hidden assumptions:** A assumes sequential one-pass consumption and safe extended lifetime; B assumes result size is bounded and memory cost acceptable.
- **Evidence favoring A:** large/unbounded data, one-pass pipeline, memory pressure, natural backpressure, stage boundaries.
- **Evidence favoring B:** repeated access, stable snapshot/atomic validation, collection protocol, producer resource must close before return, small bounded data.
- **Decision rule:** select from consumer contract and lifecycle; do not expose deferred execution merely to save an unmeasured allocation.
- **Unresolved questions:** error-timing compatibility and partial-side-effect acceptability.
- **Roles affected:** coding, performance, review, repair.
- **Source support:** `FP: chapters/007-chapter-2-an-array-of-sequences.md :: ## Generator Expressions`; `FP: chapters/024-chapter-17-iterables-iterators-and-generators.md :: ## Case Study: Generators in a Database Conversion Utility`; `EGO: chapters/014-chapter-10-optimization-examples.md :: ### Moving to Streaming Algorithm`.

### CONF-LP-006 — Static typing versus runtime testing/validation

- **Positions:** (A) annotations and static protocols catch interface/type mistakes cheaply; (B) runtime tests and validation cover behavior, external values, and invariants the type system cannot express.
- **Hidden assumptions:** A assumes checker coverage and expressible stable types; B assumes representative tests and reachable failure cases.
- **Evidence favoring A:** typed stable boundary, recurring type mismatch, configured CI checker, low annotation distortion.
- **Evidence favoring B:** untrusted input, business constraints, dynamic/metaprogrammed behavior, checker false positive/negative, runtime compatibility.
- **Decision rule:** use both according to boundary. Static types document/check supported operations; runtime validation protects trust boundaries; tests protect semantics. Neither is an acceptance substitute for the other.
- **Unresolved questions:** checker/version-specific expressiveness; verify current tool behavior.
- **Roles affected:** coding, review, repair.
- **Source support:** `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## About gradual typing`; `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## Flawed Typing and Strong Testing`; `FP: chapters/022-chapter-15-more-about-type-hints.md :: ## TypedDict`.

### CONF-LP-007 — Caching versus recomputation/freshness

- **Positions:** (A) cache repeated expensive results to trade space for latency/CPU; (B) recompute to retain freshness, bounded memory, isolation, and simpler concurrency.
- **Hidden assumptions:** A assumes high reuse, stable keys/results, manageable invalidation; B assumes computation is affordable and source available.
- **Evidence favoring A:** profile contribution, measured repeated keys, acceptable staleness, bounded capacity, macro benefit.
- **Evidence favoring B:** high-cardinality/low-hit workload, mutable/tenant-sensitive result, invalidation ambiguity, memory pressure, cheap operation.
- **Decision rule:** cache only after specifying validity, key identity, bound, concurrency, and observability; prefer recomputation otherwise.
- **Unresolved questions:** failure caching and cross-process consistency policy.
- **Roles affected:** performance, coding, architecture, review.
- **Source support:** `FP: chapters/015-chapter-9-decorators-and-closures.md :: ## Memoization with functools.cache`; `FP: chapters/030-chapter-23-dynamic-attributes-and-properties.md :: ## Step 4: Bespoke Property Cache`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Trading Space for Time`.

### CONF-LP-008 — Readability versus low-level efficiency

- **Positions:** (A) simple idiomatic code improves reviewability and compiler optimization, avoiding maintenance risk; (B) explicit low-level layout, zero-copy, unsafe, batching, or specialized parsing can meet hard resource targets.
- **Hidden assumptions:** A assumes target is met or compiler/library path sufficient; B assumes a proven hot path, stable environment/representation, and reviewers able to maintain invariants.
- **Evidence favoring A:** no RAER miss, cold path, unclear causal gain, broad portability needs.
- **Evidence favoring B:** valid profile/benchmark, material target miss, semantic oracle, localized implementation, documented assumptions and fallback.
- **Decision rule:** clarity is the default constraint. Spend complexity only in a bounded critical path when measured gain is required; recover readability with names, tests, rationale, and containment—not by denying the trade-off.
- **Unresolved questions:** future compiler/runtime/library behavior can invalidate specialization.
- **Roles affected:** performance, coding, review.
- **Source support:** `EGO: chapters/005-chapter-1-software-efficiency-matters.md :: ### Optimized Code Is Not Readable`; `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: #### The Simpler the Code, the More Effective Compiler Optimizations Will Be`; `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Deliberate Trade-offs`; `FP: chapters/018-chapter-11-a-pythonic-object.md :: ## Chapter Summary`.

## Deterministic procedures and rubrics

### PROC-LP-001 — Decide whether performance work is justified

- **Inputs:** reported symptom; repository/environment version; user/SLO/incident/cost constraints; supported workload; current authority.
- **Evidence required:** functional reproduction or accepted observation; metric semantics; representative baseline; EGO-PERF-003 target or explicit exploration-only status.
- **Steps:**
  1. Classify the complaint as correctness, latency, throughput, CPU, memory, disk/network, scalability, energy/cost, or mixed.
  2. Verify supported functionality and prerequisites; deduplicate against known incidents/issues.
  3. Rewrite the complaint with EGO-PERF-001 boundary and EGO-PERF-005 semantics.
  4. Compare a current representative observation to the accepted target.
  5. If within target, record no performance defect and stop unless authority requests exploratory headroom work.
  6. If outside target, rank impact × likelihood × recurrence × reversibility; select deliberate campaign only if priority and authority justify it.
- **Outputs:** `no-action`, `observation-needed`, `performance-campaign-candidate`, or `functional/operational-defect` classification; target and evidence ledger.
- **Stop conditions:** no meaningful target; unsupported workload; target already met; measurement perturbation/privacy risk unacceptable.
- **Escalation conditions:** target requires functionality loss, architecture/deployment change, production load, cost commitment, or scope beyond authorization.
- **Common false positives:** cold start called steady-state latency; average masking tail; high CPU while throughput/latency target is met; heap growth that plateaus; benchmark-only regression with no relevant workload.
- **Source support:** `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Got an Efficiency Problem? Keep Calm!`; `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Resource-Aware Efficiency Requirements`.

### PROC-LP-002 — Design and validate a performance experiment

- **Inputs:** falsifiable claim; target operation/resource; implementation alternatives; environment access.
- **Evidence required:** exact code/dependency/benchmark versions; representative data; correctness oracle; environment/resource configuration; anticipated variance sources.
- **Steps:**
  1. Select production observation, macrobenchmark, microbenchmark, stress, or load test from the claim—not convenience.
  2. Define setup/measurement/teardown boundaries and exclude setup only when production claim excludes it.
  3. Assert functional output and errors inside or beside the benchmark.
  4. Pin/record versions, data generation, compiler flags, runtime, hardware/container limits, dependency fakes/real services, cache state.
  5. Run pilot; inspect whether load generator, logging, GC, compiler elimination, thermal scaling, or background work dominates.
  6. Run nearby A/B repetitions long enough for stable distribution; retain raw results and profiles.
  7. Report effect size, variability, limitations, and claim boundary; do not promote a micro result to a macro conclusion.
- **Outputs:** versioned reproducible experiment and valid/invalid/limited result.
- **Stop conditions:** benchmark incorrect, implausible rate suggests elimination, variance swamps effect, environment cannot represent claim.
- **Escalation conditions:** production traffic/data required; shared infrastructure could be harmed; dependency owner or cost authorization needed.
- **Common false positives:** warm cache only; shared CI neighbor; compressible toy input; `allocs/op` interpreted as peak; ordered `map` consumption mistaken for task completion order.
- **Source support:** `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Reliability of Experiments`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### What Level Should You Use?`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Compiler Optimizations Versus Benchmark`.

### PROC-LP-003 — Locate a performance bottleneck

- **Inputs:** validated workload/benchmark; violated metric; current binary/source and symbols.
- **Evidence required:** synchronized metric/profile interval and known profiler semantics.
- **Steps:**
  1. Choose CPU profile for on-CPU work, allocation/in-use heap for allocation/retention, goroutine/block/mutex/trace for waiting/lifecycle, and OS signals for RSS/WSS/mappings.
  2. Capture during the representative phase, recording sample rate and duration.
  3. Inspect both direct and cumulative contribution; expand hidden nodes; distinguish code, runtime, GC, syscall, and dependency work.
  4. Treat goroutine/task/process boundaries as causal breaks until trace/correlation proves continuation.
  5. Compare profile contribution to wall/CPU/memory metrics and complexity expectation.
  6. Generate at least two causal hypotheses and one disconfirming experiment for the leading hypothesis.
  7. Select the smallest bottleneck whose removal could materially affect the target.
- **Outputs:** ranked hypothesis ledger with profile locator, expected target impact, confidence, next experiment.
- **Stop conditions:** workload not representative; sample too sparse; metric/profile boundaries do not align; bottleneck is outside authorized component.
- **Escalation conditions:** dependency/vendor/runtime/OS change needed; profile contains sensitive data; production-only issue cannot be reproduced safely.
- **Common false positives:** cumulative dispatcher frame; sampled percentage as exact time; allocator frame blamed instead of caller; goroutine count without leak/lifetime proof; off-CPU time inferred from absent CPU samples alone.
- **Source support:** `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: ## Root Cause Analysis, but for Efficiency`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: ### Choose Your Granularity`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: ### Common Profile Instrumentation`.

### PROC-LP-004 — Execute one behavior-preserving optimization campaign

- **Inputs:** authorized RAER; preservation boundary; valid benchmark; ranked bottleneck; candidate transformations.
- **Evidence required:** passing functional/characterization tests, baseline artifacts, profile support, rollback path.
- **Steps:**
  1. Order candidates: remove work → algorithm/data/streaming → allocation/data movement → local code/compiler → bounded concurrency → runtime/OS/hardware.
  2. Choose one candidate at one level; document assumptions and predicted metric/resource effects.
  3. Make the smallest reviewable change without unrelated cleanup or semantic repair.
  4. Run the exact functional/characterization gate.
  5. Run the same valid performance experiment and relevant macro resource gate.
  6. Inspect regressions in latency distribution, CPU, memory, errors, determinism, readability, and portability.
  7. Retain if target/net benefit passes; otherwise revert. Reprofile before choosing the next candidate.
  8. Stop per EGO-PERF-017 and preserve artifacts for regression protection.
- **Outputs:** verified optimization with causal evidence, or reverted hypothesis and updated ledger.
- **Stop conditions:** behavior differs without authority; target met; benchmark invalid; marginal gain below noise/requirement; complexity cost disproportionate.
- **Escalation conditions:** unsafe operation, contract narrowing, architecture/concurrency/deployment change, new dependency, resource budget trade, or production rollout.
- **Common false positives:** several “related” tweaks in one diff; result caused by changed input/cache; micro gain offset by GC/RSS; concurrency masks slower per-item work.
- **Source support:** `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Efficiency-Aware Development Flow`; `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Optimize One Thing at a Time`.

### PROC-LP-005 — Diagnose and reduce memory pressure

- **Inputs:** memory complaint/limit; time-series heap/RSS/VSS/WSS/container metrics; representative workload; allocation/in-use profiles.
- **Evidence required:** exact metric definitions; peak and post-idle behavior; ownership/lifecycle map; OS/runtime/container versions.
- **Steps:**
  1. State violated boundary: allocation rate, live heap, peak RSS, working set, GC CPU/latency, OOM, or mapping/address-space issue.
  2. Correlate runtime heap with OS resident/working-set and container limit over the same interval.
  3. Compare allocation-space to in-use-space profiles; identify high-rate temporaries versus retained objects.
  4. Trace retained ownership through slices/views/caches/pools/goroutines/resources; test post-work release.
  5. Apply Three Rs in order: eliminate/shrink allocation; safe reuse/preallocation; pooling/recycling only after macro proof.
  6. Recheck correctness, peak and steady state, GC CPU/latency, RSS, and other resources.
- **Outputs:** classified allocation/retention/mapping/limit cause and verified remedy or escalation.
- **Stop conditions:** delta is beneath meaningful threshold; metric mismatch; external page cache/mapping is intended and target met.
- **Escalation conditions:** hard container sizing, off-heap/mmap, runtime tuning, data-retention policy, or semantic streaming change required.
- **Common false positives:** VSS called leak; heap gauge misses spike; pool reduces allocations but increases RSS; small subslice retains huge array; `GOMEMLIMIT` assumed hard ceiling.
- **Source support:** `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: ### Do We Have a Memory Problem?`; `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: ### Heap`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### The Three Rs Optimization Method`.

### PROC-LP-006 — Decide whether and how to add concurrency

- **Inputs:** target; profiled sequential work graph; task size/distribution; ordering/state/dependency constraints; current Python/Go runtime; capacity limits.
- **Evidence required:** sequential baseline after work/algorithm improvements; model-compatible libraries; bounded representative load; error/cancellation/lifecycle requirements.
- **Steps:**
  1. Split work into compute, blocking wait, scheduling/coordination, and shared-state regions.
  2. Reject concurrency if target is met, work is too fine, dependencies serialize it, or state/ordering cost dominates.
  3. For Python, verify interpreter/build/extensions: choose bounded threads for compatible blocking work, processes for coarse serializable CPU parallelism, async for many compatible waits. For Go, compare bounded workers versus deterministic sharding/direct sequential flow.
  4. Define maximum concurrency from downstream capacity and memory, not input cardinality.
  5. Define owner, cancellation, error aggregation, ordering, retries/idempotency, cleanup, and wait semantics before implementation.
  6. Implement the smallest topology; run functional, race/leak/cancellation, and macro performance/resource tests.
  7. Prefer sequential if gain is immaterial or nondeterminism/complexity exceeds accepted benefit.
- **Outputs:** no-concurrency decision or bounded topology with proof and operational limits.
- **Stop conditions:** model relies on stale runtime fact; downstream capacity unknown; no safe cancellation/cleanup; load test unsafe.
- **Escalation conditions:** architecture/distribution, production capacity, external service limits, data-consistency semantics, or deployment/process model changes.
- **Common false positives:** idle CPU as evidence; “I/O-bound system”; number of cores as worker count; async syntax as nonblocking proof; goroutine count as throughput.
- **Source support:** `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## Processes, threads, and Python's Infamous GIL`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## The Myth of I/O Bound Systems`; `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: ### When to Use Concurrency`.

### PROC-LP-007 — Select a Python interface or dynamic mechanism

- **Inputs:** consumer operations; implementation count/ownership; runtime/static enforcement need; repetition; public API and framework constraints.
- **Evidence required:** call sites, repository toolchain, actual repeated cases, failure timing, maintainers and compatibility surface.
- **Steps:**
  1. If one concrete implementation and no variation pressure, depend directly.
  2. If only callable behavior and no state, consider a named function/callable.
  3. If local structural use suffices, rely on ordinary protocol/attempted operation.
  4. If checked unrelated implementations exist, define a small consumer-shaped static `Protocol`.
  5. If runtime membership/shared framework lifecycle is required, use an existing or justified ABC.
  6. For repeated attribute behavior, escalate plain attribute → property → descriptor.
  7. For class creation, escalate function/factory → class decorator/`__init_subclass__` → metaclass only if earlier mechanisms cannot satisfy a framework-level requirement.
  8. Test introspection, import-time effects, inheritance, serialization, typing, and public behavior at the selected level.
- **Outputs:** direct/function/protocol/ABC/property/descriptor/hook/metaclass decision with rejected simpler alternatives.
- **Stop conditions:** only hypothetical reuse; generated/vendored ownership; toolchain incompatible; metaclass conflict or public behavior unclear.
- **Escalation conditions:** new public extension framework, version-floor change, broad hierarchy/API migration.
- **Common false positives:** mock as second implementation; repeated syntax without repeated policy; duck-typed method presence mistaken for semantic contract; class size mistaken for abstraction pressure.
- **Source support:** `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Two kinds of protocols`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Modern Features Simplify or Replace Metaclasses`; `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Wrapping up`.

### PROC-LP-008 — Review a Python async path for safety

- **Inputs:** async entry point and await graph; task/resource inventory; downstream capacities; cancellation/timeout policy.
- **Evidence required:** dependency blocking semantics, maximum cardinality, event-loop lag/load observation, durable operation ownership.
- **Steps:**
  1. Trace every called operation; mark async-yielding, CPU, blocking I/O, synchronous trivial, and fire-and-forget.
  2. Require bounded semaphore/queue/worker capacity for fan-out and align it with downstream limit.
  3. Move unavoidable blocking work to a bounded thread/process executor appropriate to work; await durable completion.
  4. Use async context managers for sessions/transactions and structured ownership for tasks.
  5. Verify exception retrieval/aggregation, timeouts, cancellation propagation, partial results, and cleanup.
  6. Test under failures, slow dependency, cancellation, high cardinality, and event-loop lag measurement.
- **Outputs:** blocker/limit/lifecycle findings classified as defect, risk, or accepted behavior.
- **Stop conditions:** dependency semantics unknown; load test could harm public service; no authority to change externally visible completion semantics.
- **Escalation conditions:** process/task queue/distributed architecture, retry/idempotency policy, service capacity contract.
- **Common false positives:** filesystem assumed harmless; `run_in_executor` call not awaited; bounded workers but unbounded pending queue; `gather` result ordering confused with completion order.
- **Source support:** `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Using asyncio.as\_completed and a semaphore`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Using an Executor to Avoid Blocking the Event Loop`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## How Async Works and How It Doesn't`.

### PROC-LP-009 — Establish performance preservation and regression gates

- **Inputs:** candidate optimization; authorized behavior delta (normally none); API/data/error/concurrency/operational contracts; target metrics.
- **Evidence required:** existing tests, call sites, representative inputs including failures/edge cases, baseline metrics.
- **Steps:**
  1. Enumerate observable outputs, errors, ordering, precision, mutation/ownership, timing assumptions, resource cleanup, public API/format, concurrency/cancellation, and operational limits.
  2. Mark each as invariant, authorized change, unknown, or irrelevant with rationale.
  3. Add characterization for unknown behavior that clients may rely on before structural/performance change.
  4. Choose micro gate for causal local result and macro/runtime gate for user/resource effect.
  5. Set regression thresholds above normal variance and define environment/version.
  6. Require functional gate before interpreting every performance result; retain baseline and post-change artifacts.
- **Outputs:** preservation-boundary record and executable correctness/performance gates.
- **Stop conditions:** behavior cannot be characterized, authority for semantics unclear, benchmark variance prevents threshold.
- **Escalation conditions:** proposed optimization intentionally drops functionality, changes public format/API, weakens durability/security, or changes architecture.
- **Common false positives:** tests cover only happy output but not errors/order/mutation; type checker substituted for behavior; alloc microgate substituted for process memory; benchmark improvement accepted despite correctness drift.
- **Source support:** `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Functionality Phase`; `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Comparison to Functional Testing`; `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## Flawed Typing and Strong Testing`.

## Routing index candidates

`Budget` is a suggested retrieval-token range. All rows inherit `exclude generated/vendored code unless explicitly in scope` and `repository contracts first`.

| Concept | Activate for roles | Tasks | Repository signals | Languages | Risk | Exclude when / prerequisites | Priority / budget | Retrieval terms and related concepts |
|---|---|---|---|---|---|---|---|---|
| `FP-IMPL-001` | coding, review, repair | any Python change | version matrix, compatibility shims, formatter/checker | Python | all | need repo/toolchain inspection | core / 200–350 | Python idiom, compatibility, repository convention; `FP-IMPL-007` |
| `FP-IMPL-002` | coding, API, review | custom type/library integration | bespoke adapter, dunder, failed built-in op | Python | medium API | need client operations | high / 350–500 | protocol conformance, special methods; `FP-IMPL-009`, `FP-IMPL-011` |
| `FP-IMPL-003` | coding, performance, review | representation choice | list queue, huge collection, numeric data, memory pressure | Python | normal–high | skip trivial small constants; need workload | high / 400–600 | list deque array memoryview mapping set; `FP-IMPL-012`, `EGO-PERF-010` |
| `FP-IMPL-004` | coding, repair, review | ownership/mutation | mutable default, stored input, in-place op | Python | high correctness | need identity/lifetime analysis | core / 300–500 | aliasing, call by sharing, copy, mutable default; `FP-IMPL-017` |
| `FP-IMPL-005` | coding, repair, review | text/file/protocol handling | encode/decode, `open`, mixed str/bytes | Python | high integrity | skip opaque binary; need format policy | core / 300–450 | Unicode, bytes, encoding, normalization |
| `FP-IMPL-006` | coding, domain, refactoring, review | record/domain placement | dataclass with scattered behavior | Python | medium structural | exclude transport/generated record; need call sites/history | normal / 400–550 | dataclass smell, DTO, intermediate representation |
| `FP-IMPL-007` | coding, review, repair | typing/validation | `Any`, `TypedDict`, `cast`, external input | Python | medium–high | need checker and trust boundary | high / 350–550 | gradual typing, runtime validation, tests; `CONF-LP-006` |
| `FP-IMPL-008` | coding, architecture, review | Strategy/Command/callback | one-method stateless classes | Python | normal | framework class contract present | normal / 300–450 | first-class function, callable, strategy |
| `FP-IMPL-009` | coding, architecture, review | interface/extension design | ABC, Protocol, adapters, mocks | Python | medium API | no variation/consumer evidence; need consumers | high / 450–650 | duck typing, ABC, Protocol, interface; `CONF-LP-004` |
| `FP-IMPL-010` | architecture, coding, refactoring, review | hierarchy change | built-in subclass, MRO, mixins | Python | high structural | do not rewrite stable framework; need characterization | high / 400–600 | composition, inheritance, mixin, UserDict |
| `FP-IMPL-011` | coding, repair, review | operator/custom collection | equality/hash/operator/slice dunder | Python | high API/correctness | need algebra/invariant tests | high / 350–500 | operator overloading, hash, NotImplemented, slicing |
| `FP-IMPL-012` | coding, performance, review | stream/materialize decision | huge list, iterator/generator, ETL | Python | medium resource | need replay/lifetime contract | high / 350–550 | generator, iterator, lazy, streaming; `CONF-LP-005` |
| `FP-IMPL-013` | coding, repair, review | resource lifecycle | file/lock/session/transaction | Python, universal | high durability | need acquire/release map | core / 250–400 | context manager, with, cleanup; `EGO-PERF-014` |
| `FP-IMPL-014` | performance, architecture, coding | concurrency selection | executor, threads, processes, async | Python | high concurrency | need current runtime/profile | specialist / 550–800 | GIL, thread, process, asyncio; `CONF-LP-003` |
| `FP-IMPL-015` | coding, performance, repair, review | async implementation/review | `create_task`, `gather`, semaphore, blocking client | Python | high operational | no async workload pressure; need capacity/cancellation | specialist / 500–750 | event loop, backpressure, semaphore, executor |
| `FP-IMPL-016` | architecture, coding, review | dynamic mechanism/framework | decorator, descriptor, metaclass, dynamic attr | Python | high cognitive/API | one-off/simple alternative; need repeated cases | specialist / 600–900 | metaprogramming escalation, import time; `CONF-LP-004` |
| `FP-IMPL-017` | performance, coding, review | caching | `cache`, LRU, cached property, cache dict | Python, universal | high memory/integrity | cheap/low-reuse work; need validity/bound | high / 400–650 | cache invalidation, hit rate, freshness; `CONF-LP-007` |
| `FP-IMPL-018` | coding, API, review | add validation/computation to field | public attribute gains invariant | Python | medium API | schema/ORM incompatibility; need caller analysis | normal / 250–400 | property, compatible API evolution |
| `EGO-PERF-001` | performance, review, architecture | performance triage | vague slow/high-resource report | all | all | need meaningful measurable boundary | core / 250–400 | latency throughput efficiency metric boundary |
| `EGO-PERF-002` | coding, performance, review | classify optimization | optimization embedded in feature | all | medium scope | need trade-off inventory | core / 300–450 | reasonable optimization, deliberate optimization |
| `EGO-PERF-003` | performance, architecture, review | set target | SLO/capacity/cost/incident | all | high | exploratory-only without authority; need owner | core / 400–600 | RAER, resource budget, percentile, workload |
| `EGO-PERF-004` | performance, coding, repair | optimization campaign | target miss + candidate | all | high | no authority/preservation boundary | core / 500–700 | TFBO, test benchmark profile optimize |
| `EGO-PERF-005` | performance, repair, operations | interpret telemetry | metrics/traces/profiles/dashboard | all | high evidence | need instrumentation definition | core / 350–550 | metric semantics, granularity, percentiles, RSS WSS |
| `EGO-PERF-006` | performance, review | benchmark result/design | benchmark PR/report/regression | all, Go specialist | high evidence | invalid versions/workload/correctness | core / 500–750 | benchmark validity, variance, A/B, compiler elimination |
| `EGO-PERF-007` | performance, architecture | choose experiment level | micro claim about system or vice versa | all | medium–high | need exact claim | high / 350–500 | microbenchmark, macrobenchmark, production monitoring |
| `EGO-PERF-008` | performance, repair, review | bottleneck diagnosis | CPU/heap/goroutine profile | all, Go specialist | high evidence | need representative workload/profile semantics | core / 550–800 | pprof, flat cum, sampling, off-CPU |
| `EGO-PERF-009` | performance, architecture, coding | rank optimization candidates | scaling/hot algorithm | all | high semantic | need input distribution/profile | core / 400–650 | do less work, Big O, streaming, algorithm |
| `EGO-PERF-010` | performance, repair, review | memory diagnosis | OOM, GC, RSS/heap gap | all, Go specialist | high durability | need metric boundary/timeline | specialist / 600–850 | heap RSS VSS WSS retention allocation |
| `EGO-PERF-011` | performance, coding, review | add/review Go concurrency | goroutines, channels, workers | Go | high concurrency | need sequential baseline/lifecycle | specialist / 550–800 | bounded goroutine, channel overhead, sharding |
| `EGO-PERF-012` | performance, coding, review | specialize hot path | generic call hot, unsafe/zero-copy | all, Go examples | high correctness | need oracle and macro benefit | specialist / 500–750 | specialization, generic overhead, unsafe; `CONF-LP-002` |
| `EGO-PERF-013` | performance, coding, review | allocation optimization | alloc/GC profile, pooling | Go, universal principle | high memory | need macro gate/ownership | specialist / 450–700 | reduce reuse recycle, preallocate, pool |
| `EGO-PERF-014` | coding, repair, review | resource/goroutine lifecycle | `go`, open/body/stream | Go, universal | high durability | need owner/stop/wait map | core / 350–550 | goroutine leak, close, exhaust, cancellation |
| `EGO-GO-001` | coding, architecture, review | package/API placement | Go package/export/dependency change | Go | medium–high API | need call graph/repo convention | high / 350–550 | package cohesion, internal, export, dependency |
| `EGO-GO-002` | coding, repair, review | error handling | ignored/wrapped Go error | Go | high correctness | need current convention/toolchain | core / 250–450 | errors Is As wrap context, cleanup |
| `EGO-GO-003` | coding, performance, review | value/pointer/generic choice | pointer conversion, generic hot path | Go | normal–high | no material target; semantics first | normal / 350–550 | pointer escape, generics, interface, compiler |
| `EGO-PERF-017` | performance, all agents | stop/accept optimization | target met, next step widens scope | all | all | need target and authority | core / 250–400 | stop condition, revert, escalation, marginal gain |

## Residual uncertainties and synthesis cautions

- The corpus does not resolve current CPython concurrency behavior. The 2021 source assumes the traditional GIL in mainstream CPython; current repository interpreter/build facts must determine whether those mechanics still apply. The stable doctrine is workload/runtime verification and bounded-model selection, not “threads cannot parallelize Python” as a universal.
- FP states Python 3.8 `cached_property` is thread-safe; this is version-specific and cannot be routed as current doctrine. The stable doctrine is to verify cache concurrency semantics for the active version.
- FP classic-coroutine coverage is valuable for control-transfer semantics but weak as implementation guidance for new native-async code. Route it mainly for legacy understanding.
- EGO's Go 1.18-era recommendations for error wrapping, `GOMAXPROCS` in containers, compiler optimization, runtime scheduler, GC, and profiling defaults are contextual. Retain the decision procedures; verify mechanics against the repository toolchain.
- Neither source deeply covers security side channels, real-time systems, GPU performance, databases, networks, or distributed consistency. Their performance loop generalizes; their concrete transformations do not fill those specialist gaps.
- Both sources use simplified examples. EGO explicitly notes omitted error handling; FP examples sometimes prioritize one language feature over production lifecycle/error concerns. Examples are evidence for mechanics, never ready-made patches.
- Exact numeric speedups, hardware latencies, worker counts, and allocation deltas are nonportable and were not promoted to doctrine.

## Graph candidates

These are first-class candidates for the canonical doctrine graph. IDs are intentionally source-independent. Repeated node rows are distinct provenance assertions for the same canonical node. `derived_inference` is used only where the operational formulation is synthesized rather than explicitly stated by a source.

### Candidate nodes and provenance assertions

| Canonical node ID | Label | Kind | Source-specific paraphrased formulation | Exact locator | Provenance relation |
|---|---|---|---|---|---|
| `U.REPOSITORY-CONTRACT-PRECEDENCE` | Repository contracts precede generic doctrine | universal-doctrine | A Python object is only “Pythonic” relative to its application/library requirements; simplicity and supported behavior determine which features belong. | `FP: chapters/018-chapter-11-a-pythonic-object.md :: ## Chapter Summary` | `refinement` |
| `U.REPOSITORY-CONTRACT-PRECEDENCE` | Repository contracts precede generic doctrine | universal-doctrine | Performance techniques do not generalize automatically; workload and codebase facts must select them. | `EGO: chapters/003-preface.md :: ## Why I Wrote This Book` | `corroboration` |
| `U.EVIDENCE-BEFORE-INTERVENTION` | Evidence before intervention | universal-doctrine | Reasonable local efficiency differs from deliberate optimization; the latter is measurement- and trade-off-driven. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Deliberate Optimizations` | `direct_support` |
| `U.BEHAVIOR-PRESERVATION` | Preserve behavior unless change is authorized | universal-doctrine | Functional tests precede efficiency assessment, and must pass again after change. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Functionality Phase` | `direct_support` |
| `U.BEHAVIOR-PRESERVATION` | Preserve behavior unless change is authorized | universal-doctrine | Types and static checks cannot establish runtime business behavior; executable tests remain required. | `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## Flawed Typing and Strong Testing` | `corroboration` |
| `U.MINIMIZE-SIMULTANEOUS-UNCERTAINTY` | Change one causal variable at a time | universal-doctrine | Optimize one bottleneck/transformation at a time so a result can be causally attributed. | `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Optimize One Thing at a Time` | `direct_support` |
| `U.EARN-ABSTRACTION` | Earn abstractions from demonstrated pressure | universal-doctrine | Framework-class machinery is usually extracted from repeated needs; application code should not invent powerful class mechanisms prematurely. | `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Wrapping up` | `direct_support` |
| `U.STRUCTURED-LIFECYCLE` | Bind resource lifetime to an explicit owner | universal-doctrine | Context managers factor paired setup/teardown and guarantee release across exceptions. | `FP: chapters/025-chapter-18-context-managers-and-else-blocks.md :: ## Context Managers and with Blocks` | `direct_support` |
| `U.STRUCTURED-LIFECYCLE` | Bind resource lifetime to an explicit owner | universal-doctrine | Goroutines and closeable/exhaustible resources need stop, wait, close, and error-path ownership. | `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Control the Lifecycle of Your Goroutines` | `corroboration` |
| `LANG.PY.PROTOCOL-CONFORMANCE` | Use Python protocols for required interoperability | language-specialization | Implement the standard special-method protocol needed by clients instead of inventing a parallel bespoke interface. | `FP: chapters/005-chapter-1-the-python-data-model.md :: ## How Special Methods Are Used` | `direct_support` |
| `LANG.PY.REPRESENTATION-FIT` | Select Python representation from semantics and workload | language-specialization | Flat/container sequence, mutable/immutable, array/deque/view/generator choices encode different operations, ownership, and memory costs. | `FP: chapters/007-chapter-2-an-array-of-sequences.md :: ## When a List Is Not the Answer` | `direct_support` |
| `LANG.PY.MUTABLE-OWNERSHIP` | Make Python aliasing and mutation ownership explicit | language-specialization | Parameters receive shared references; mutate a received object only by contract and avoid mutable defaults. | `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## Defensive Programming with Mutable Parameters` | `direct_support` |
| `LANG.PY.TEXT-BYTES-BOUNDARY` | Decode/encode at explicit boundaries | language-specialization | Text and binary representations are distinct; codecs/default/error and normalization policy must be explicit. | `FP: chapters/009-chapter-4-text-versus-bytes.md :: ## Handling Text Files` | `direct_support` |
| `LANG.PY.RUNTIME-STATIC-BOUNDARY` | Static hints do not create runtime guarantees | language-specialization | Gradual typing is optional, does not enforce runtime values or improve runtime performance, and cannot replace validation/tests. | `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## About gradual typing` | `direct_support` |
| `LANG.PY.MINIMAL-INTERFACE-MECHANISM` | Choose duck typing, Protocol, ABC, or concrete coupling by enforcement need | language-specialization | Dynamic protocols, static protocols, ABCs, and nominal types are complementary rather than one universal interface style. | `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Chapter Summary` | `direct_support` |
| `LANG.PY.DYNAMIC-MECHANISM-ESCALATION` | Escalate Python metaprogramming only as needed | language-specialization | Modern class decorators, descriptors, and subclass hooks often replace metaclasses; metaclasses should be hidden implementation details. | `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Modern Features Simplify or Replace Metaclasses` | `direct_support` |
| `LANG.PY.STREAMING-ITERATION` | Stream only when single-pass deferred semantics fit | language-specialization | Generators decouple producer/consumer and bound memory, but iterator identity, exhaustion, and deferred resource lifetime matter. | `FP: chapters/024-chapter-17-iterables-iterators-and-generators.md :: ## Case Study: Generators in a Database Conversion Utility` | `direct_support` |
| `LANG.PY.CONCURRENCY-MODEL-SELECTION` | Select Python concurrency from workload and current runtime | language-specialization | Thread, process, and async models have different waiting, parallelism, state-sharing, and event-loop constraints. | `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## Processes, threads, and Python's Infamous GIL` | `direct_support` |
| `LANG.PY.BOUNDED-ASYNC` | Bound async concurrency and avoid event-loop blocking | language-specialization | Async code must yield through compatible APIs, throttle concurrent work, and delegate blocking calls. | `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Using asyncio.as\_completed and a semaphore` | `direct_support` |
| `LANG.GO.PACKAGE-API-SIMPLICITY` | Keep Go packages/APIs cohesive and minimally exported | language-specialization | Simplicity, internal packages, transparent dependencies, and standard tooling support serious codebases. | `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: ### Packaging and Modules` | `direct_support` |
| `LANG.GO.EXPLICIT-ERRORS` | Handle or propagate every material Go error explicitly | language-specialization | Errors are ordinary return values; ignored errors erase failure evidence, though wrapping mechanics depend on current toolchain. | `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: #### Never Ignore Errors!` | `direct_support` |
| `LANG.GO.BOUNDED-CONCURRENCY` | Add bounded Go concurrency only after evidence | language-specialization | Goroutines/channels add scheduling, coordination, memory, and nondeterminism; concurrency should be a late deliberate optimization. | `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: #### Adding Concurrency Should Be One of Our Last Deliberate Optimizations to Try` | `direct_support` |
| `PERF.CLAIM-SPECIFICATION` | Specify performance claim boundary | performance-doctrine | “Performance” must be separated into accuracy, speed, and resource efficiency for a named operation/workload. | `EGO: chapters/005-chapter-1-software-efficiency-matters.md :: ### Clarify When Someone Uses the Word "Performance"` | `direct_support` |
| `PERF.RAER` | Resource-Aware Efficiency Requirement | evidence-obligation | An efficiency target binds operation/input to latency statistic and CPU/memory/disk or other resource bounds. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Resource-Aware Efficiency Requirements` | `direct_support` |
| `PERF.MEASUREMENT-SEMANTICS` | Define metric semantics before interpretation | evidence-obligation | Metric value is meaningless without semantic boundary, unit, granularity, aggregation, and population. | `EGO: chapters/010-chapter-6-efficiency-observability.md :: ### Efficiency Metrics Semantics` | `direct_support` |
| `PERF.BENCHMARK-VALIDITY` | Establish benchmark validity | evidence-obligation | Results require known code/benchmark versions, representative production conditions/workload, correctness, repeated stable comparison, and acknowledged nondeterminism. | `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Reliability of Experiments` | `direct_support` |
| `PERF.EXPERIMENT-LEVEL-FIT` | Match experiment level to claim | evidence-obligation | Micro, macro, and production observations answer different questions; isolated results do not establish full-system behavior. | `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### What Level Should You Use?` | `direct_support` |
| `PERF.PROFILE-BEFORE-OPTIMIZE` | Locate causal bottleneck before changing it | evidence-obligation | Profiles are sampled and granular; direct/cumulative, heap/goroutine/CPU/off-CPU semantics must be interpreted before selecting a frame. | `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: #### Profile First, Ask Questions Later` | `direct_support` |
| `PERF.PROOF-OBLIGATION` | Performance recommendation proof obligation | evidence-obligation | An actionable recommendation requires an accepted target, valid representative baseline, causal profile, preservation tests, controlled one-variable result, and relevant macro regression gate. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Efficiency-Aware Development Flow` | `derived_inference` |
| `PERF.OPTIMIZATION-LOOP` | Test–benchmark–profile–optimize loop | procedure | Test functionality, assess against target, profile main bottleneck, choose one design level, optimize, retest, and stop at target. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Efficiency-Aware Development Flow` | `direct_support` |
| `PERF.ALGORITHM-BEFORE-MICRO` | Remove work and improve algorithm/data before micro-tuning | performance-doctrine | Complexity analysis screens alternatives, while empirical constants decide real workload fit; doing less work is the primary pattern. | `EGO: chapters/011-chapter-7-data-driven-efficiency-assessment.md :: ### Practical Applications` | `direct_support` |
| `PERF.MEMORY-LIFECYCLE-EVIDENCE` | Diagnose memory by metric and ownership lifetime | evidence-obligation | Heap, RSS/WSS, mappings, allocation rate, and retained objects are distinct; trace ownership before GC/off-heap tuning. | `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: ### Go Memory Management` | `direct_support` |
| `PERF.THREE-RS` | Reduce, reuse, recycle in order | performance-doctrine | Eliminate allocations first, reuse safely second, and pool/tune/recycle only after the first two and macro evidence. | `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### The Three Rs Optimization Method` | `direct_support` |
| `PERF.TARGET-BASED-STOP` | Stop optimization at authorized target | agent-conduct | If the RAER is met, release/stop; further trade-offs need a new requirement and authority. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: #### 5. Are we within RAERs?` | `direct_support` |
| `CONFLICT.ABSTRACTION-VS-SPECIALIZATION` | Generic abstraction versus hot-path specialization | conflict | Generic functions support reuse and correctness, but measured stable hot paths can justify specialized direct work with explicit trade-offs. | `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Standard Functions Might Not Be Perfect for All Cases` | `direct_support` |
| `CONFLICT.ABSTRACTION-VS-SPECIALIZATION` | Generic abstraction versus hot-path specialization | conflict | Powerful reusable framework mechanisms should be extracted from repeated application needs, not invented speculatively. | `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Wrapping up` | `corroboration` |
| `CONFLICT.CONCURRENCY-VS-SIMPLICITY` | Concurrency versus sequential simplicity | conflict | Python model choice depends on waiting/CPU/runtime/dependency facts; CPU work can stall async and process/thread overhead varies. | `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## The Myth of I/O Bound Systems` | `direct_support` |
| `CONFLICT.CONCURRENCY-VS-SIMPLICITY` | Concurrency versus sequential simplicity | conflict | Go concurrency adds coordination cost and is a late optimization after simpler work reduction. | `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: ### When to Use Concurrency` | `corroboration` |
| `CONFLICT.DYNAMIC-VS-EXPLICIT` | Dynamic mechanisms versus explicit local reasoning | conflict | Protocols/metaprogramming can remove boilerplate, but class machinery is difficult enough that simpler mechanisms should win when adequate. | `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Metaclasses in the Real world` | `direct_support` |
| `CONFLICT.LAZY-VS-MATERIALIZED` | Lazy streaming versus eager materialization | conflict | Generator pipelines bound memory and decouple stages; the inferred counterposition is that consumer replay, eager validation, and independent lifetime can require materialization. | `FP: chapters/024-chapter-17-iterables-iterators-and-generators.md :: ## Lazy sentences` | `derived_inference` |

### Candidate typed edges with provenance

| Edge ID | From | Typed edge | To | Edge meaning | Exact provenance locator(s) | Provenance relation |
|---|---|---|---|---|---|---|
| `GE-LP-001` | `LANG.PY.PROTOCOL-CONFORMANCE` | `specializes` | `U.EARN-ABSTRACTION` | Existing Python protocols are the first earned abstraction for required interoperability. | `FP: chapters/005-chapter-1-the-python-data-model.md :: ## How Special Methods Are Used` | `refinement` |
| `GE-LP-002` | `LANG.PY.MINIMAL-INTERFACE-MECHANISM` | `specializes` | `U.EARN-ABSTRACTION` | Protocol/ABC strength is selected from consumer and enforcement evidence. | `FP: chapters/020-chapter-13-interfaces-protocols-and-abcs.md :: ## Two kinds of protocols` | `refinement` |
| `GE-LP-003` | `LANG.PY.DYNAMIC-MECHANISM-ESCALATION` | `specializes` | `U.EARN-ABSTRACTION` | Python class machinery follows a least-powerful-mechanism ladder. | `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Modern Features Simplify or Replace Metaclasses` | `refinement` |
| `GE-LP-004` | `LANG.GO.PACKAGE-API-SIMPLICITY` | `specializes` | `U.EARN-ABSTRACTION` | Go package/export/interface scope stays minimal until consumers earn more. | `EGO: chapters/006-chapter-2-efficient-introduction-to-go.md :: ### Simplicity, Safety, and Readability Are Paramount` | `refinement` |
| `GE-LP-005` | `LANG.PY.MUTABLE-OWNERSHIP` | `specializes` | `U.STRUCTURED-LIFECYCLE` | Shared references make data ownership/lifetime an explicit Python obligation. | `FP: chapters/011-chapter-6-object-references-mutability-and-recycling.md :: ## Function Parameters as References` | `refinement` |
| `GE-LP-006` | `LANG.GO.BOUNDED-CONCURRENCY` | `specializes` | `U.STRUCTURED-LIFECYCLE` | Every goroutine topology requires stop/wait/error ownership. | `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Control the Lifecycle of Your Goroutines` | `refinement` |
| `GE-LP-007` | `LANG.PY.BOUNDED-ASYNC` | `specializes` | `U.STRUCTURED-LIFECYCLE` | Async tasks/sessions must have bounded capacity, cancellation, and structured cleanup. | `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Asynchronous Context Managers`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Using asyncio.as\_completed and a semaphore` | `refinement` |
| `GE-LP-008` | `PERF.RAER` | `requires` | `PERF.CLAIM-SPECIFICATION` | A resource-aware target can only be written after the operation/workload/metric is named. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Resource-Aware Efficiency Requirements`; `EGO: chapters/005-chapter-1-software-efficiency-matters.md :: ### Clarify When Someone Uses the Word "Performance"` | `derived_inference` |
| `GE-LP-009` | `PERF.PROOF-OBLIGATION` | `requires` | `PERF.RAER` | Recommendation needs an accepted threshold, not merely a faster number. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Understand Your Goals` | `direct_support` |
| `GE-LP-010` | `PERF.PROOF-OBLIGATION` | `requires` | `PERF.MEASUREMENT-SEMANTICS` | Evidence cannot support action until its metric meaning is defined. | `EGO: chapters/010-chapter-6-efficiency-observability.md :: ### Efficiency Metrics Semantics` | `direct_support` |
| `GE-LP-011` | `PERF.PROOF-OBLIGATION` | `requires` | `PERF.BENCHMARK-VALIDITY` | Causal effect requires a valid controlled experiment. | `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### Reliability of Experiments` | `direct_support` |
| `GE-LP-012` | `PERF.PROOF-OBLIGATION` | `requires` | `PERF.EXPERIMENT-LEVEL-FIT` | The experiment must observe the level named by the claim. | `EGO: chapters/012-chapter-8-benchmarking-versus-stress-and-load-tests.md :: ### What Level Should You Use?` | `direct_support` |
| `GE-LP-013` | `PERF.PROOF-OBLIGATION` | `requires` | `PERF.PROFILE-BEFORE-OPTIMIZE` | Recommendation must address a representative causal bottleneck. | `EGO: chapters/013-chapter-9-data-driven-bottleneck-analysis.md :: #### Profile First, Ask Questions Later` | `direct_support` |
| `GE-LP-014` | `PERF.PROOF-OBLIGATION` | `requires` | `U.BEHAVIOR-PRESERVATION` | A faster implementation is unacceptable if unauthorized behavior changes. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Functionality Phase` | `direct_support` |
| `GE-LP-015` | `PERF.OPTIMIZATION-LOOP` | `operationalizes` | `PERF.PROOF-OBLIGATION` | The TFBO sequence discharges the proof obligations step by step. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Efficiency-Aware Development Flow` | `derived_inference` |
| `GE-LP-016` | `U.MINIMIZE-SIMULTANEOUS-UNCERTAINTY` | `constrains` | `PERF.OPTIMIZATION-LOOP` | Each iteration changes one bottleneck/lever before remeasurement. | `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Optimize One Thing at a Time` | `direct_support` |
| `GE-LP-017` | `PERF.TARGET-BASED-STOP` | `terminates` | `PERF.OPTIMIZATION-LOOP` | Meeting the accepted target is a positive stop condition. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: #### 5. Are we within RAERs?` | `direct_support` |
| `GE-LP-018` | `PERF.ALGORITHM-BEFORE-MICRO` | `precedes` | `CONFLICT.ABSTRACTION-VS-SPECIALIZATION` | Remove work/choose algorithm before paying specialization cost. | `EGO: chapters/007-chapter-3-conquering-efficiency.md :: ### Optimization Design Levels`; `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### Do Less Work` | `direct_support` |
| `GE-LP-019` | `CONFLICT.ABSTRACTION-VS-SPECIALIZATION` | `resolved_by` | `PERF.PROOF-OBLIGATION` | Specialization wins only with material profiled macro benefit and semantic protection. | `EGO: chapters/014-chapter-10-optimization-examples.md :: #### Deliberate Trade-offs` | `derived_inference` |
| `GE-LP-020` | `CONFLICT.CONCURRENCY-VS-SIMPLICITY` | `resolved_by` | `PERF.PROOF-OBLIGATION` | Add concurrency only after representative evidence and lifecycle/capacity proof. | `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: ### When to Use Concurrency`; `FP: chapters/029-chapter-22-asynchronous-programming.md :: ## Avoiding CPU-bound Traps` | `derived_inference` |
| `GE-LP-021` | `LANG.PY.CONCURRENCY-MODEL-SELECTION` | `specializes` | `CONFLICT.CONCURRENCY-VS-SIMPLICITY` | Python resolves the tension using current interpreter, dependency blocking, and workload shape. | `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## Processes, threads, and Python's Infamous GIL` | `refinement` |
| `GE-LP-022` | `LANG.GO.BOUNDED-CONCURRENCY` | `specializes` | `CONFLICT.CONCURRENCY-VS-SIMPLICITY` | Go resolves the tension with late, bounded, benchmarked worker/shard designs. | `EGO: chapters/014-chapter-10-optimization-examples.md :: ### Optimizing Latency Using Concurrency` | `refinement` |
| `GE-LP-023` | `CONFLICT.DYNAMIC-VS-EXPLICIT` | `resolved_by` | `U.EARN-ABSTRACTION` | Use dynamic machinery only for demonstrated repeated/framework pressure. | `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Wrapping up` | `direct_support` |
| `GE-LP-024` | `LANG.PY.DYNAMIC-MECHANISM-ESCALATION` | `constrains` | `CONFLICT.DYNAMIC-VS-EXPLICIT` | Property/descriptor/hook/metaclass escalation preserves the simplest adequate explicit form. | `FP: chapters/032-chapter-25-class-metaprogramming.md :: ## Modern Features Simplify or Replace Metaclasses` | `refinement` |
| `GE-LP-025` | `LANG.PY.STREAMING-ITERATION` | `specializes` | `CONFLICT.LAZY-VS-MATERIALIZED` | Streaming is chosen only if consumer/lifetime semantics permit deferred one-pass behavior. | `FP: chapters/024-chapter-17-iterables-iterators-and-generators.md :: ## Lazy sentences`; `FP: chapters/024-chapter-17-iterables-iterators-and-generators.md :: ## Don't make the iterable an iterator for itself` | `refinement` |
| `GE-LP-026` | `PERF.MEMORY-LIFECYCLE-EVIDENCE` | `requires` | `PERF.MEASUREMENT-SEMANTICS` | Memory action depends on knowing whether the signal is heap, RSS/WSS, allocation, or mapping. | `EGO: chapters/010-chapter-6-efficiency-observability.md :: ### Memory Usage`; `EGO: chapters/009-chapter-5-how-go-uses-memory-resource.md :: ### Go Memory Management` | `direct_support` |
| `GE-LP-027` | `PERF.THREE-RS` | `operationalizes` | `PERF.MEMORY-LIFECYCLE-EVIDENCE` | Once allocation/retention cause is known, reduce/reuse/recycle supplies the ordered intervention ladder. | `EGO: chapters/015-chapter-11-optimization-patterns.md :: ### The Three Rs Optimization Method` | `refinement` |
| `GE-LP-028` | `LANG.PY.RUNTIME-STATIC-BOUNDARY` | `constrains` | `U.BEHAVIOR-PRESERVATION` | Static success is not behavior acceptance; runtime validation/tests remain preservation evidence. | `FP: chapters/014-chapter-8-type-hints-in-functions.md :: ## Flawed Typing and Strong Testing` | `direct_support` |
| `GE-LP-029` | `U.REPOSITORY-CONTRACT-PRECEDENCE` | `constrains` | `LANG.PY.CONCURRENCY-MODEL-SELECTION` | Dated GIL/runtime guidance cannot override the active interpreter/build and deployment contract. | `FP: chapters/027-chapter-20-concurrency-models-in-python.md :: ## Processes, threads, and Python's Infamous GIL` | `derived_inference` |
| `GE-LP-030` | `U.REPOSITORY-CONTRACT-PRECEDENCE` | `constrains` | `LANG.GO.BOUNDED-CONCURRENCY` | Scheduler/GOMAXPROCS/container advice must be verified against the current Go toolchain and repository. | `EGO: chapters/008-chapter-4-how-go-uses-the-cpu-resource-or-two.md :: #### Recommended GOMAXPROCS Configuration` | `derived_inference` |
