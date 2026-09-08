# Restrict and sync rollout custody files

Date: 2026-09-08. Baseline: `2024275`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Repair rollout leaf-file reads and durability barriers in
`src/caplab/artifact_rater.py`. Permitted additional files:
`tests/test_native_capture_custody.py`, `tests/test_rollout_file_boundary.py`,
`docs/product/contracts/rollout-custody-file-boundary-v1.md`, and this record.
Require regular, non-symlink leaf files for source reads, existing custody reuse
and direct attestation. Make special-file rejection nonblocking. Sync custody
file and parent directory before returning a preservation attestation, including
byte-identical reuse. Preserve returned fields, retained-byte snapshot semantics,
tuple/JSON validation, exclusive creation and refusal to overwrite different
or partial custody. Adapt the existing mutation fixture to the new read boundary
and explicitly verify that it still mutates the source.

Authorize new synthetic files, symlinks, FIFOs and bounded local Python probes
in temporary directories; mocked faults; focused checks and `make check`.
No historical session inspection/copy/admission/rescoring/purge, native process
or model call, campaign, ranking, placement, tracker write or external message.
Preserve frozen instruments/manifests, `docs/designs/`, sibling worktrees and
services. Retain `/tmp` verification receipts; remove only named task doctrine
scratch after retaining its receipt. Stop on unexplained compatibility changes.
Authorization expires at commit.

## Decision and scope

`read_rollout_attestation` and `preserve_rollout_attestation` currently use
`Path.read_bytes`, which follows a leaf symlink and can wait on a FIFO. Discovery
checks do not protect direct retained reads or a leaf replaced after discovery.
Preservation closes the output but has no explicit file/directory sync barrier.
Select descriptor-based nonblocking opens, regular-file checks and explicit
custody sync. No change retains these gaps. Selecting a newest file or treating
a failed read/sync as empty evidence would weaken linkage rather than repair it.

This remains an attestation of retained snapshot bytes. The existing mutation
test deliberately permits a live source to change after its snapshot was read;
that does not change what the retained bytes say. CAPLAB-79's prospective stable
source sealing, bounded native session/child collection and native integration
remain separate, incomplete requirements. Parent paths and custody ownership
must be trusted; this repair is not an atomic snapshot or provider authentication.


## Execution and verification

Added one shared regular-file context owner for the three rollout read paths.
It opens without following the leaf, uses nonblocking open to avoid waiting on
FIFOs, validates the descriptor type, and closes it even if stream construction
or reading fails. New writes flush and sync their original write descriptor;
identical reuse syncs the descriptor used for comparison. Both paths sync the
custody parent before interpreting retained bytes and returning attestation.
The [file-boundary contract](../product/contracts/rollout-custody-file-boundary-v1.md)
records these semantics and their limits.

The initial six tests produced five assertion failures and three timeout errors
in 6.013 seconds: `/tmp/caplab-rollout-custody-red.log`. Linked source and direct
attestation leaves were accepted. The three real local FIFO probes (source,
existing custody, direct read) each exceeded a two-second subprocess timeout;
the test runner killed and reaped those synthetic probes. Sync fault injections
were not reached because the old implementation made no sync calls.

Eight new tests now cover those cases, a leaf replaced after the preliminary
symlink check, and descriptor cleanup when stream setup fails. The existing
retained-snapshot mutation test now patches the actual source-read boundary
and additionally proves that its source changed; it still verifies attestation
against the old retained bytes. This preserves its intended contract instead of
letting a stale Path mock make it pass without exercising mutation.

The focused suites passed 44 tests in 1.508 seconds:
`/tmp/caplab-rollout-custody-focused.log`. Existing cases continue to reject
partial/different custody, malformed JSON, inconsistent tuples and failed
native event evidence, and to withhold caller publication after custody errors.
All native processes in these tests are synthetic stubs or local Python probes.

A baseline probe compares complete preservation and direct-attestation results
against `2024275` across 32 valid combinations of model, effort, CLI version,
LF/CRLF bytes, Unicode and old-first/new-first creation. No fields are excluded;
all results match, source bytes are unchanged, and identical reuse preserves
custody modification time. Receipts: `/tmp/caplab-rollout-custody-parity.py`
and `/tmp/caplab-rollout-custody-parity.json`.

Source hashes and direct-import checks are retained in
`/tmp/caplab-rollout-custody-source-check.json`; no unused imports were found.
The verified local runtime is Python 3.12.3 on Linux 6.8.0-138-generic. The
Linux man-pages open/fsync contracts were opened on September 8 and are linked
in the file-boundary guide. They support the leaf, nonblocking and directory-sync
semantics; no hardware power-cut or replication test is claimed.

## Remaining boundary

This does not freeze live source bytes, constrain parent path substitution,
provide a bounded native session collector, or establish provider identity.
The caller still owns private, trusted custody and runtime isolation. File size
and regular-file I/O time remain unbounded in these existing APIs. CAPLAB-79/84
still require the prospective stable/bounded session and child capture path.
No retained historical capture or score was inspected or changed by this repair,
and no native launch or campaign was authorized. Reopen this boundary if the
selected filesystem cannot honor these barriers; do not ignore sync failures.


## Doctrine receipt

The release retrieval-state gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`.

Final packet `pkt-fc46e7bbb389ef56`, content SHA-256
`fc46e7bbb389ef56ffd8ee5d8ea46d4174b48d279cb87c4005adc79e9d3df0f4`,
uses five typed records after one evidence-gathering pass. Applied
`universal-evidence-before-intervention` to require the symlink/FIFO/sync
reproduction; `python-structured-cleanup` to own descriptors through errors;
`universal-preserve-behavior-by-default` to retain snapshot semantics and compare
whole valid results; and `agent-conduct-authority-bounded-action` to restrict
verification to synthetic custody. Four citations classified as
`valid-packet-citation`.

All 12 remaining obligations have a bounded nonmaterial classification here:

| Concept | Exact unmet requirements | Classification and reason |
|---|---|---|
| `data-replication-guarantee-selection` | acknowledgment and replication topology; durability and availability objectives; durability, latency, availability, and recovery objectives; failure and failover behavior; replication and failover topology | Nonmaterial: no replication topology, failover policy or remote durability claim is selected. The repair adds local file/parent barriers only. |
| `data-transaction-guarantee-verification` | datastore guarantee and configuration; vendor or protocol guarantee for the exact configuration | Nonmaterial to the bounded syscall/error-handling claim: no datastore transaction or physical device survival is asserted. Linux API semantics are cited, and read/sync failures are exercised; a power-cut or exact hardware/configuration guarantee remains unverified. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI/static-tool conformance claim or tooling change; verification uses the existing local Makefile/Python suite. |
| `python-mutable-ownership` | concurrency; lifetime and size | Nonmaterial: no worker, retained cache or mutable shared input is introduced. Whole-file memory use and concurrent parent/custody substitution remain outside the claim. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no formatter, linter or checker policy change or conformance claim. |


## Completion checks

`make check` passed 985 tests with four skips in 119.312 seconds:
`/tmp/caplab-rollout-custody-make-check.log`. No source or test file changed
after that run began. Final source/link checks and the consolidated receipt
are retained in `/tmp/caplab-rollout-custody-verification.json`.

The eleven named doctrine scratch files were removed after retaining packet,
citation and obligation receipts. Regression logs and parity probes remain.
No tracker field, frozen source binding or external message changed. Commit
closes this repair, not stable native capture integration or the CAPLAB goal.
