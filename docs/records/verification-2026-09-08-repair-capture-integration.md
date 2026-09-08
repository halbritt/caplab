# Exercise repair assessment from retained capture

Date: 2026-09-08. Baseline: `b0a62d8`. Primary-agent decision and bounded
execution authority: [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `tests/test_repair_capture_integration.py` and this record. Exercise the
existing task capture, native runtime preparation, native output collection,
bundle verification and root/final-message linkage owners without changing them.
Use both configured native-format layouts as synthetic data formats only.
Execute a new trusted Python fixture through an isolated, network-unshared
Bubblewrap namespace, never either native harness or a model. Its only host
writable mounts are the newly created task and private runtime directories.

Copy the current `TASK.md`, `parent/transfer.py`, both `repairs/*.py` and both
`negatives/*.py` from the authored `atomic-transfer-v1` development world into
fresh disposable fixtures as needed; record source commit, path and content
hashes. Retain before/after task bytes, binary process streams, synthetic session
and diagnostic records, and new reports under `/tmp/caplab-repair-capture-*`.
Assess only those known authored transfer functions using the current v2 oracle
and disposable SQLite databases. No generic execution of captured code is
authorized. Include a no-write fixture whose optimistic completion text cannot
substitute for a task change or a passing oracle.

Verify each completed bundle and its root linkage before deleting exactly the
new task, prepared runtime and fixture-input directories. Re-verify and assess
from retained custody after that deletion. Keep custody, reports and logs.
Run focused and full checks, consolidate advisory evidence, delete exact named
advisory scratch files, and make a local commit. Authorization expires at commit.

Preserve all current world files and dossiers, capture/runtime source, prior
evidence, `docs/designs/`, sibling worktrees, services and credentials. No study
admission, historical campaign inspection/copy, score, ranking, placement,
native execution, model spend, tracker change, external message or push.
The development world and derivatives remain permanently excluded from the
unobserved study population. Stop on a need to weaken existing contracts,
execute unknown code, access credentials, or represent synthetic events as a
native execution or independent verdict. Self-verification is not acceptance.

## Selected verification boundary

Existing root/final-message linkage fixtures use empty task trees. The missing
integration observation is whether their retained task counterpart supports
assessment of a concrete repair after source removal. A small test fixture
composes existing owners. A general study runner would add authority and runtime
requirements beyond this observation; leaving the tests unchanged would leave
the connection to repair assessment unexercised.

All fixture variants may claim completion in their synthetic messages. Task
inventory and oracle results must continue to distinguish two repair strategies,
two plausible but defective edits, and the unchanged parent. This checks evidence
plumbing and preserves discrimination; it does not measure a reviewer, native
capture legibility, resource requirements for real episodes, or blinding.

## Observations and verification

The fixture uses the canonical policy to prepare a `/work` task and `/episode`
runtime layout. Its separately recorded command executes `/usr/bin/python3 -B`
against a trusted, read-only fixture mount in Bubblewrap. The producer copies
one known authored replacement into `transfer.py` or performs no task write,
then writes synthetic stdout, stderr, session and diagnostic bytes. It never
invokes the configured Codex or Claude command. Only the new task and runtime
are host-writable mounts; the new custody directories are outside the namespace.
This is a contained fixture, not a production launcher or an untrusted-code
sandbox qualification.

The task capture owns before/after inventories and process evidence. Native
collection owns retained invocation/preparation records and selected runtime
artifacts. Existing linkage verifies both anchored bundles and the root fields;
Codex additionally checks exact final-message agreement. All three source
directories are then removed, and linkage is repeated from custody. The tests
recover exact task, parent, replacement, supplied prompt, opaque stderr and
diagnostic bytes, preserving non-ASCII text and invalid UTF-8 diagnostic bytes.
Custody hashes remain unchanged across re-verification and assessment.

Only recovered bytes that exactly equal an enumerated authored witness execute
under the existing development oracle. This test-local step is not a generic
captured-code loader. Assessment results name the after-file and oracle hashes;
the retained attempt anchor binds that file to the before/after inventories and
process capture. The report keeps task changes, synthetic linkage and oracle
outcomes separate.

Both transaction and savepoint repairs pass all nine oracle checks after
recovery. The retry-only and false-success edits retain their passing retry
behavior and failing statement-failure behavior. The no-write variant records
an empty change set and the parent's failing retry and atomicity checks even
though its synthetic message claims completion. That diagnostic audit does not
make a no-write fixture an eligible study attempt or assign it a behavior code.

Ten retained probe cases (five variants in each layout) are under
`/tmp/caplab-repair-capture-probe-eaupu7eq/`. The script, reports, source check and
logs use the `/tmp/caplab-repair-capture-` prefix. Source provenance identifies
the full baseline commit, path and SHA-256 of every world file and the unchanged
capture owners and policy. The probe removed only each case's newly created
`task`, `prepared` and `fixture` directories after successful verification.
Original source, prior evidence and retained custody remain.

The first focused run exposed a wrong diagnostic-field name in the new Claude
fixture setup (`debug_file` instead of the contract's `diagnostic_file`). The
fixture was corrected; no runtime or contract was changed. Its failed log is
retained at `/tmp/caplab-repair-capture-focused-initial.log`. The corrected
focused run passed two parameterized tests covering all ten cases in 2.326
seconds. Test-guard review kept the two distinct scenarios (edits and no-write),
used actual filesystem/process/SQLite boundaries, and added no mock assertions
or duplicate tamper-verifier tests.

## Limits and remaining work

Every emitted native-shaped record is authored fixture data. Root and final-file
agreement remains compatible with `executed_invocation_bound=false` and unknown
native completeness. No native version, account, provider, model or reviewer was
observed. Recorded byte counts describe these small fixtures and exclude receipt
overhead; they cannot estimate representative episode cost or compare harnesses.
The current producer emits no child or tool-call sequence, and these tests make
no child-linkage, verification-command legibility or redaction claim.

All oracle outcomes are same-author development checks, not independent accuracy
validation. The world, its dossiers and capture owners remain unchanged, so no
new dossier version is needed. CAPLAB-84's real repair integration and resource
measurement, CAPLAB-63's harness comparison, CAPLAB-66's blinding feasibility,
and independent criterion validation remain open. No roadmap item is closed.

## Advisory disposition

The retrieval-state gate passed against the validated Pincite release at
`/home/halbritt/.local/share/pincite/release`, commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Five typed records supplied authority,
contracts, source, focused tests and retained synthetic observations. Final packet:
`pkt-ffef7f65b1edb02f`, content SHA-256
`ffef7f65b1edb02ffadf0c1413624cd254118ea047222b736eab55dda8c140a7`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`.

Applied `universal-repository-contract-precedence` to the native/synthetic
boundary, `universal-evidence-before-intervention` to the missing repair-capture
integration observation, `universal-no-change-option` to leaving runtime owners
unchanged, and `python-text-bytes-boundary` to exact input and opaque output
preservation. All four citations classified as valid. These are advisory
engineering principles, not CAPLAB product authority.

Twenty-three unmet obligations remain nonmaterial to this bounded verification:

| Concept | Unmet requirements | Scope reason |
| --- | --- | --- |
| implementation-repository-language-conformance | CI and build matrix; formatter and static-tool configuration | No toolchain or platform change; existing local checks are the claimed validation. |
| performance-measurable-objective | accepted workload and operation boundary; authority to inspect the target and identify the objective owner; environment, input distribution and scale, concurrency, and success/failure population; latency percentile, throughput, CPU, memory, I/O, network, cost, or other metric with a target; owner for the objective and any quality tradeoff | No performance objective, representative workload or deployment tradeoff is selected. |
| performance-metric-semantics | access to instrumentation definition or benchmark harness; instrumentation definition and configuration; instrumentation overhead and data-loss limits; sanity check against actual runtime behavior; unit, aggregation window, population, and sampling behavior | Byte totals describe these authored fixtures only; no native cost, sampling or performance conclusion is made. |
| performance-representative-baseline | correctness validation for the measured workload; exact code, dependency, build, benchmark, data, and environment versions; known resource limits and warmup/cache state; repeated raw measurements and variance | No performance improvement, population extrapolation or native resource estimate is claimed. |
| python-concurrency-model-selection | baseline; blocking and CPU map; current Python build and deployment; task-size distribution; workload profile | Fixtures run sequentially through the existing bounded process owner; no concurrency model or throughput change is selected. |
| python-repository-shaped-idiom | Python and dependency version matrix; formatter linter and type-checker configuration | No new dependency, formatter or supported-version claim; local Python is 3.12.3. |

## Closure

`make check` completed with exit 0: **1,163 tests, four skipped, 157.175
seconds**. Both new integration tests ran. The full log is retained at
`/tmp/caplab-repair-capture-make-check.log`. No additional runtime change or
criterion revision was needed. The source check confirms the current world,
capture owners and policy remain byte-identical to the baseline.

`/tmp/caplab-repair-capture-verification.json` consolidates source and probe
provenance, test logs, advisory packet identities, typed evidence, citation
classification, unmet-obligation disposition and the exact scratch cleanup
list. Eleven named advisory scratch files are deleted after consolidation;
probe custody, script, reports and logs remain. The two authorized new files
are committed locally. No push, tracker change or independent acceptance is
part of this closure. Authorization expires at that commit.
