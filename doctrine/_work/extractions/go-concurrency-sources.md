# Go and Concurrency Sources: Evidence Extraction

Status: complete source-lane extraction for synthesis. This ledger records observations and candidate integrations; it does not treat either source as normative by reputation, and it does not turn recommendations into repository decisions or authorization.

## Scope, source IDs, and locator convention

Every converted Markdown chapter in both assigned corpora was inspected, including front matter, indexes, appendices, and structural files. Structural and reference-only files remain in the coverage ledger but do not independently support actionable doctrine.

- `GO` — *100 Go Mistakes and How to Avoid Them* (Teiva Harsanyi, 2022).
  - `GO_ROOT = books/100-go-mistakes-and-how-to-avoid-them-teiva-harsanyi-bibis-ir`
- `CIG` — *Concurrency in Go: Tools and Techniques for Developers* (Katherine Cox-Buday, 2017).
  - `CIG_ROOT = books/concurrency-in-go`

Doctrine locators use repository-relative chapter paths followed by an exact Markdown heading. Every candidate locator was checked for unique resolution and `role: section` in the corresponding section map. Claims are paraphrases. Source-era implementation details remain contextual until checked against the current repository toolchain.

## Complete chapter coverage ledger

### GO coverage (17/17 files)

| Path | Converted title | Go themes or disposition |
|---|---|---|
| `GO_ROOT/chapters/001-100-go-mistakes-and-how-to-avoid-them.md` | 100 Go Mistakes and How to Avoid Them | structural; title and publication data; table of contents. |
| `GO_ROOT/chapters/002-preface.md` | Preface | reference-only; source origin; mistake-catalog method. |
| `GO_ROOT/chapters/003-acknowledgments.md` | Acknowledgments | reference-only; acknowledgments; audience and roadmap; code and forum access. |
| `GO_ROOT/chapters/004-about-the-author.md` | About the Author | structural; author biography; cover illustration. |
| `GO_ROOT/chapters/005-chapter-1-go-simple-to-learn-but-hard-to-master.md` | Chapter 1: Go: Simple to Learn but Hard to Master | substantive; simple syntax versus difficult mastery; learning from mistakes; bug complexity readability API performance and productivity categories. |
| `GO_ROOT/chapters/006-chapter-2-code-and-project-organization.md` | Chapter 2: Code and Project Organization | substantive; scope and control-flow readability; interfaces generics and embedding; package API and project organization. |
| `GO_ROOT/chapters/007-chapter-3-data-types.md` | Chapter 3: Data Types | substantive; numeric semantics; slice aliasing capacity and retention; map allocation retention and comparison. |
| `GO_ROOT/chapters/008-chapter-4-control-structures.md` | Chapter 4: Control Structures | substantive; range copy and evaluation semantics; map iteration nondeterminism; loop exit and defer lifetime. |
| `GO_ROOT/chapters/009-chapter-5-strings.md` | Chapter 5: Strings | substantive; bytes UTF-8 code points and runes; string iteration and trimming; allocation and backing-storage retention. |
| `GO_ROOT/chapters/010-chapter-6-functions-and-methods.md` | Chapter 6: Functions and Methods | substantive; value and pointer receivers; named results and defer evaluation; typed nil interfaces and reader-shaped APIs. |
| `GO_ROOT/chapters/011-chapter-7-error-management.md` | Chapter 7: Error Management | substantive; panic boundaries; wrapping typed and sentinel errors; single handling and cleanup errors. |
| `GO_ROOT/chapters/012-chapter-8-concurrency-foundations.md` | Chapter 8: Concurrency: Foundations | substantive; concurrency versus parallelism; channels mutexes races and memory ordering; workload-sensitive bounds and context. |
| `GO_ROOT/chapters/013-chapter-9-concurrency-practice.md` | Chapter 9: Concurrency: Practice | substantive; context and goroutine lifetime; channel selection notification and capacity; shared collection synchronization and group completion. |
| `GO_ROOT/chapters/014-chapter-10-the-standard-library.md` | Chapter 10: The Standard Library | substantive; time JSON and SQL contracts; transient resource closure; production HTTP timeout configuration. |
| `GO_ROOT/chapters/015-chapter-11-testing.md` | Chapter 11: Testing | substantive; test classification and execution modes; race detection and deterministic asynchronous tests; benchmark validity and coverage limits. |
| `GO_ROOT/chapters/016-chapter-12-optimizations.md` | Chapter 12: Optimizations | substantive; hardware and compiler-sensitive optimization; allocation and garbage-collection behavior; profiling tracing and container runtime constraints. |
| `GO_ROOT/chapters/017-index.md` | Index | reference-only; back-of-book index; back-cover description and endorsements. |

### CIG coverage (14/14 files)

| Path | Converted title | Concurrency themes or disposition |
|---|---|---|
| `CIG_ROOT/chapters/001-o-reilly.md` | O'REILLY® | structural; title and publication data; book description and endorsements. |
| `CIG_ROOT/chapters/002-table-of-contents.md` | Table of Contents | reference-only; table of contents. |
| `CIG_ROOT/chapters/003-preface.md` | Preface | reference-only; audience and chapter roadmap; source conventions and resources. |
| `CIG_ROOT/chapters/004-acknowledgments.md` | Acknowledgments | structural; acknowledgments. |
| `CIG_ROOT/chapters/005-chapter-1-an-introduction-to-concurrency.md` | Chapter 1: An Introduction to Concurrency | substantive; race and atomicity; memory synchronization; deadlock livelock starvation and concurrency safety. |
| `CIG_ROOT/chapters/006-chapter-2-modeling-your-code-communicating-sequential-processes.md` | Chapter 2: Modeling Your Code: Communicating Sequential Processes | substantive; concurrency versus parallelism; communicating sequential processes; channels versus shared-memory synchronization. |
| `CIG_ROOT/chapters/007-chapter-3-go-s-concurrency-building-blocks.md` | Chapter 3: Go's Concurrency Building Blocks | substantive; goroutines and sync primitives; channel ownership and selection; scheduler configuration. |
| `CIG_ROOT/chapters/008-chapter-4-concurrency-patterns-in-go.md` | Chapter 4: Concurrency Patterns in Go | substantive; confinement and goroutine cancellation; pipelines fan-out and channel composition; queueing and context propagation. |
| `CIG_ROOT/chapters/009-chapter-5-concurrency-at-scale.md` | Chapter 5: Concurrency at Scale | substantive; error timeout and cancellation propagation; heartbeats replicated requests and rate limits; supervision and restart behavior. |
| `CIG_ROOT/chapters/010-chapter-6-goroutines-and-the-go-runtime.md` | Chapter 6: Goroutines and the Go Runtime | substantive; work-stealing scheduler; task versus continuation stealing; runtime abstraction with substantial version sensitivity. |
| `CIG_ROOT/chapters/011-appendix.md` | Appendix | substantive; panic stack traces; runtime race detection; pprof concurrency diagnostics. |
| `CIG_ROOT/chapters/012-index.md` | Index | reference-only; back-of-book index. |
| `CIG_ROOT/chapters/013-about-the-author.md` | About the Author | structural; author biography. |
| `CIG_ROOT/chapters/014-colophon.md` | Colophon | structural; cover animal and production credits. |

## Limitations and preserved tensions

The 2022 source is sensitive to Go runtime and standard-library evolution; loop-variable capture, timer lifetime, scheduler, and container CPU guidance require current verification and were not generalized mechanically. The 2017 source predates substantial runtime and tooling changes; its statements about cheap goroutines, scheduling, preemption, context, and libraries are contextual. Both conversions contain probable OCR damage in code blocks, so candidate doctrine relies on prose semantics and exact section provenance rather than treating converted code as byte-faithful.

The lane preserves concurrency versus sequential simplicity, channel versus mutex fit, bounded lifecycle versus cheap-goroutine rhetoric, queue smoothing versus overload and latency cost, replicated-request resilience versus capacity cost, and internal heartbeats versus external liveness observation as explicit tensions.

## Candidate disposition

The integration blueprint derived from this ledger proposes 36 normalized source-support additions: 22 extensions to existing concepts and 14 support records for 11 new concepts. `implementation-concurrency-ordering-contract`, `go-synchronization-mechanism-fit`, and `testing-deterministic-async-observation` each retain support from both sources rather than collapsing independent provenance.
