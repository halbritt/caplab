---
id: adr-0003
artifact_type: architecture-decision-record
title: Compiled doctrine retrieval
status: decided
decision_owner: books-1-implementation-delegate
decision_authority: direct-repository-owner-delegation
created: 2026-07-15
decided_at: 2026-07-15
supersedes: []
superseded_by: null
affected_contexts:
  - doctrine-retrieval
related_specs: []
related_plans: []
related_receipts: []
---

# Compiled doctrine retrieval

Status interpretation: the repository owner's BOOKS-1 request authorized the
active implementation agent to make the design decisions needed to execute the
work item. This record selects and authorizes the compiled retrieval path. The
repository owner has not accepted the result.

## Decision question and scope

Should evidence-packet retrieval remain a Python process that parses the YAML
doctrine graph on every call, become a daemon, or move only the retrieval hot
path to a stateless Go executable over a compiled SQLite read model?

This decision governs packet assembly, derived-index compilation, runtime
integrity checks, compatibility, and the performance gate. Doctrine authoring,
validation, graph projection, evaluation, book conversion, and source text stay
outside the Go runtime.

## Observations and evidence

- The canonical Python request took 560.174 ms at the median and 598.279 ms at
  p95 in the initial 25-sample baseline. YAML-backed `Corpus` construction was
  the largest instrumented stage. The command and method are recorded in
  [`doctrine-packet-assembler-baseline-2026-07-15.md`](../benchmarks/doctrine-packet-assembler-baseline-2026-07-15.md).
- The existing assembler emits `evidence-packet/2`; its schema rejects unknown
  packet fields. Adding an index identity to that packet would change the
  runtime contract.
- `routing-index.yaml`, `concepts/*.yaml`, the operational registries, and the
  doctrine graph are authoritative repository artifacts. SQLite did not exist
  as a doctrine authority before BOOKS-1.
- The repository already uses Python for doctrine generation, validation, and
  evaluation. Go 1.23 is available for a scoped runtime module.
- Plane work item BOOKS-1 requires a stateless CGO-free Go executable,
  `modernc.org/sqlite`, a Python-built read model, oracle parity, and retention
  of the Python assembler for one release. It rejects a daemon, runtime YAML
  parsing in Go, and ports of the offline doctrine tools.

## Inferences, rivals, assumptions, and uncertainty

Moving YAML parsing to a deterministic build step removes the dominant request
cost without adding a resident service. A daemon could also amortize Python
startup and parsing, but it would add process lifecycle, health, socket, and
loaded-state freshness concerns.

The principal risk is semantic drift between Python and Go, especially in JSON
serialization, Unicode normalization, CLI failure behavior, route ordering,
and packet hashing. A strict Python oracle is a stronger migration boundary
than independently reinterpreting the packet schema.

The benchmark is host-specific. It establishes a regression gate for this
repository and machine class; it does not predict latency on every host.

## Recommendation and alternatives

Select a scoped Go module under `doctrine/` with one `assemble-packet` command.
Compile the authoritative YAML into a checked-in SQLite read model using
Python. Build an untracked static executable with a content-derived retriever
identity. Keep the Python assembler as the compatibility oracle and fallback.

Alternatives considered:

- **No change:** preserves one implementation but retains measured startup and
  YAML parsing on every retrieval.
- **Python daemon:** can reduce steady-state latency but adds lifecycle and
  stale-loaded-state failure modes.
- **Python cache or pickle:** reduces parsing but retains Python startup and
  introduces a Python-specific runtime artifact.
- **Port all doctrine tools:** removes the language seam but expands BOOKS-1
  into unrelated generation, validation, graph, and evaluation behavior.

## Decision, owner, authority, and rationale

The BOOKS-1 implementation delegate selects the Go-plus-SQLite option under the
repository owner's direct 2026-07-15 delegation of design authority.

The selected boundary is:

- YAML remains canonical;
- `build_doctrine_index.py` compiles `doctrine-index/1` and its file checksum;
- the Go executable opens the index read-only and immutable, verifies its file
  checksum, rejects an incompatible schema or stale YAML fingerprint, and
  assembles the packet without parsing YAML;
- `assemble_packet.py` remains the one-release fallback and semantic oracle;
- offline Python tools remain Python; and
- there is no daemon.

The logical `index_content_hash` stays in SQLite metadata. A companion SHA-256
file protects the complete SQLite artifact because a file cannot contain its
own file hash. `built_at` is omitted because wall-clock data would make equal
inputs produce different index bytes. `source_commit` is replaced by a source
fingerprint so an uncommitted or differently checked-out but byte-identical
source tree compiles identically. `retriever_version` belongs to the executable
and packet, not the index, so a retriever-only change does not rebuild an
unchanged read model.

`evidence-packet/2` remains unchanged. The current schema has a closed field
set, so `index_content_hash` is not added to the packet during this migration.
Packet reproduction instead depends on the recorded doctrine and retriever
identities; runtime index integrity is checked before retrieval.

## Authorization and execution scope

The owner's request to pick up BOOKS-1, followed by explicit delegation of
decision authority, authorizes changes to:

- the doctrine index compiler and generated index;
- the scoped Go module and packet command;
- the build, parity, benchmark, and repository check commands;
- packet-runtime tests and compatibility fixtures;
- doctrine invocation documentation and the deployed doctrine skill; and
- the ADR, benchmark records, README surfaces, and changelog.

The authorization does not cover doctrine content changes, schema promotion to
`evidence-packet/3`, evaluation results, human dispositions, book conversion,
or a new service.

## Consequences and preservation boundaries

- A doctrine source change must rebuild the SQLite file and checksum. The
  release gate rejects stale generated state.
- A retrieval-logic or dependency change produces a new content-derived
  `retriever-<16 hex>` identity without changing the index.
- The generated executable is platform-specific and is not committed;
  `make doctrine-runtime` builds it with `CGO_ENABLED=0`.
- `modernc.org/sqlite` and its checksummed transitive modules are now runtime
  build dependencies.
- Compact retrieval decodes full concept records only after selection. Full
  detail retains the Python packet contract.
- Packet semantics, ordering, Unicode behavior, code paths outside retrieval,
  YAML authority, and the version 2 packet schema must remain unchanged.

## Verification and fitness criteria

Execution conforms when:

- fresh index builds are byte-identical within one Python/SQLite toolchain,
  logically current files survive a SQLite writer-version change, unchanged
  output is not replaced, and `--check` detects a missing, stale, or mismatched
  index/checksum pair;
- the executable is statically linked and `ldd` reports no dynamic executable;
- the bounded success and failure matrix is byte-identical to Python when the
  oracle retriever identity is injected;
- a production identity changes only `retriever_version`,
  `packet_content_sha256`, and `packet_id`, and both hashes recompute;
- all 72 canonical role-task combinations match the Python oracle;
- malformed evidence, stale or corrupt indexes, URI metacharacters, and tested
  Unicode boundary and normalization cases fail or route identically to Python;
- the benchmark reports median at most 50 ms, p95 at most 75 ms, at least 8x
  median speedup, and semantic parity; and
- `make check`, `make doctrine-check`, the Go tests, and `git diff --check`
  pass without changing generated state.

The recorded final run passed: 32.954 ms candidate median, 41.231 ms candidate
p95, 18.573x median speedup over the same-run Python baseline, and semantic
parity. The complete report is
[`doctrine-packet-assembler-2026-07-15.json`](../benchmarks/doctrine-packet-assembler-2026-07-15.json).

These checks verify the implementation against this decision. They do not
establish the doctrine skill's engineering-judgment quality, which remains a
separate human-adjudicated evaluation concern.

## Acceptance owner and outcome

The repository owner is the acceptance owner. Acceptance is pending owner
review of the verified BOOKS-1 result.

## Reopening and supersession conditions

Reopen if the Go and Python outputs diverge, the index or source-fingerprint
checks become a material share of latency, the read model cannot represent a
new routing rule, static builds cease to be supportable, or the retained Python
fallback is proposed for removal.

Changing the packet schema, adopting a daemon, making SQLite authoritative, or
porting offline tools requires a new decision. Supersession must link both ADRs.

## Related artifacts

- Plane work item `BOOKS-1`
- [`../../doctrine/tools/build_doctrine_index.py`](../../doctrine/tools/build_doctrine_index.py)
- [`../../doctrine/tools/build_packet_assembler.py`](../../doctrine/tools/build_packet_assembler.py)
- [`../../doctrine/tools/benchmark_assemble_packet.py`](../../doctrine/tools/benchmark_assemble_packet.py)
- [`../../doctrine/runtime/README.md`](../../doctrine/runtime/README.md)
- [`doctrine-packet-assembler-baseline-2026-07-15.md`](../benchmarks/doctrine-packet-assembler-baseline-2026-07-15.md)
- [`doctrine-packet-assembler-2026-07-15.json`](../benchmarks/doctrine-packet-assembler-2026-07-15.json)

## Status history

- `2026-07-15` — `decided` — repository owner delegated BOOKS-1 design and
  execution authority; the delegate selected and implemented compiled doctrine
  retrieval. Owner acceptance remains pending.
