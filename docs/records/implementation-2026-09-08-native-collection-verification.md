# Verify anchored native output collections

Date: 2026-09-08. Baseline: `2a64190`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `src/caplab/native_collection_verify.py`, its focused test module,
`scripts/verify_native_collection.py`, a versioned verification contract and this
record; link the collection contract. Inspect current source/contracts and only
new synthetic collections made in this execution. Exercise malformed receipts,
missing/changed bytes, quota and link boundaries, and the CLI. Run focused/full
tests and a local commit. Preserve existing source, policies, profiles, launchers,
frozen manifests, `docs/designs/`, sibling worktrees and services. No historical
custody reads or writes, inference, credentials, admission, tracker write,
external message, ranking or placement. Retain verification logs/probes; remove
only enumerated doctrine scratch after consolidation. Authorization expires at
commit. Stop if verification requires opening original runtime/task paths,
changing accepted capture semantics or admitting unlinked native evidence.

## Decision and boundary

An anchored read-only verifier will check the collection, intent, copied
preparation and invocation receipts under one caller-supplied byte allowance.
It will reconstruct canonical configured invocation identity, compare selected
paths and missingness, and check all referenced payload hashes, sizes, tree
structure and shared quotas. Reuse the task capture reader and inventory verifier;
project native selection roots under one in-memory inventory root for structural
validation without changing the retained receipt. No source or task path is
opened, allowing inspection after source deletion or custody relocation.

A matching hash alone leaves contradictory summaries and forged location maps
unchecked. Re-reading the mutable runtime would conflate retained observation
with later state. A separate general inventory verifier would duplicate existing
rules. This reader therefore checks retained bytes and internal consistency,
while leaving session linkage, native identity, completeness, containment,
publication history and eligibility unproven. Native output stays opaque and
private. Reopen for new collection schemas or actual session-linking consumers.

## Execution and verification evidence

The new API uses the existing bounded receipt reader, canonical invocation
validator and inventory verifier. Native entries are projected under a temporary
in-memory root solely for existing tree checks; retained bytes and counts exclude
that root. Source paths are lexical metadata. The reader opens only custody and
the explicit canonical policy input. It owns no worker, cache or persistent
state, mutates no caller-owned document and provides no native-output parser.
Known capture exceptions remain authoritative over any later integrity report.

Eleven new focused tests passed in 1.125 seconds:
`/tmp/caplab-native-verify-focused.log`. Both harness layouts verify after source
deletion and custody relocation, with all retained file bytes unchanged. Tests
exercise all four receipt links, independent anchors, contradictory summaries
and selected maps after rehashing, unsupported but self-rehashed invocation
commands, exact combined receipt limits, boolean/undersized quotas, duplicate
and invalid paths/objects, invalid link targets and modes, payload mutation,
no-follow symlink/FIFO boundaries, and descriptor closure after a detected read
mutation. Opaque binary/CRLF bytes and a non-ASCII child filename are retained.
A 70,000-byte payload verifies with read requests no larger than 65,536 bytes.
An all-missing collection verifies integrity without claiming native completeness.
Malformed JSON, duplicate keys and non-finite constants are rejected.

The actual CLI test returns JSON on exit zero, including missingness, and returns
exit two with no stdout for a wrong anchor. An unreferenced FIFO is not opened.
The separate retained CLI probe is `/tmp/caplab-native-verify-probe.py` with
receipt `/tmp/caplab-native-verify-probe.json`; retained root:
`/tmp/caplab-native-verify-probe-8pp6nd5k`. Original source/task paths were moved
aside before verification. Collection SHA-256:
`ae8da913ce5876243d042589c52241a353fd2b6336f815d8d24d4dbc57f0bf78`.
The reader checks 6,656 receipt bytes, 47 artifact bytes and four entries, and
preserves missing `final_message`. Custody file hashes stay unchanged. A bad
anchor exits two with zero stdout bytes. No native process or inference ran;
these deliberately non-native bytes establish reader mechanics only.

`/tmp/caplab-native-verify-source-check.json` retains source/test/CLI hashes,
direct-import checks, Python 3.12.3 and ten protected-source comparisons against
baseline `2a64190`. No unused direct imports were found. Existing collection,
runtime, invocation, task/process capture and verification, native policy/subject
validation and both launchers are unchanged. No dependency or tooling settings
changed. Documentation links resolve; API, CLI, error and missingness claims
were checked against source and the exercised entry points. The wording gives
specific limits; the prose pass found no generic claim requiring removal.

Full `make check` passed: 1,043 tests in 121.301 seconds, four skips, exit zero.
Log: `/tmp/caplab-native-verify-make-check.log`. Source/test/CLI hashes still match
the earlier check; all ten protected sources were compared again with baseline.
No source or test changed during the full run.

## Advisory doctrine and completion

Retrieval passed the release gate at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-4b61732cfc6f043b`, content SHA-256
`4b61732cfc6f043b1d49a89032a06e6b3a876ec05f9b7dfbd37068e55770b59c`,
uses `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9` and
`retriever-ec995ecdd083b2c8`. One evidence-gathering pass supplied five typed
records. Four citations classify as valid: `implementation-minimal-coherent-api`
for a read-only inspection API and CLI, `python-structured-cleanup` for scoped
read descriptors, `python-text-bytes-boundary` for strict receipt decoding and
opaque payload hashing, and `agent-conduct-authority-bounded-action` for integrity
without native identity or admission. Repository contracts govern the effect.

Five unmet obligations are nonmaterial to this feature:

- `implementation-repository-language-conformance`: `CI and build matrix` and
  `formatter and static-tool configuration`; neither changes, and no new
  platform or tooling qualification is claimed.
- `python-repository-shaped-idiom`: `formatter linter and type-checker configuration`;
  the reader uses adjacent capture owners, with no formatter/checker claim.
- `python-runtime-static-boundary`: `annotation maintenance cost` and
  `configured checker and Python version`; no static-proof or annotation-cost
  claim is made. The actual local Python version is recorded separately.

`/tmp/caplab-native-verify-verification.json` consolidates packet identity,
citations, obligations, source/probe checks and test results. It retains hashes
and paths of exactly eleven removed doctrine scratch files. Test logs, probes,
source checks and the new synthetic custody remain available.

This reader is implemented and technically verified within its contract. It
advances the evidence-consumption requirement of CAPLAB-84; that roadmap item,
CAPLAB-85 containment, session/attempt linkage and native adapter integration
remain incomplete. Further linkage must use an independently anchored attempt
and retained native session observations, not configured identity alone. No
native capability, eligibility, placement or independent acceptance judgment
is recorded. The active objective remains incomplete.
