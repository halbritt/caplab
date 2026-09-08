# Preserve the intended mutation and freeze resumable experiments

Date: 2026-09-08. Observation, execution, and verification under the active
CAPLAB improvement goal. The preceding goal turn was progress: `d1ffd9e` is
present and refuses unsupported pair oracles. No model calls, historical
evidence admission, or human-owned judgment were performed in this turn.

## Findings

At `d1ffd9e`, `refuted_conclusion` selected a heading and inserted its
paragraph immediately after the title text. For a heading such as
`## Results {#el:results}`, the element identifier moved below the inserted
paragraph and ceased to identify the heading. CAPLAB's own heading parser
observed `results` on the control heading and no anchor on the mutant, while
the pair gate accepted the contrast. The reviewer could therefore refuse a
missing anchor instead of detecting the intended conclusion defect.

The old implementation also located a selected heading with `body.index` of
its title. Repeated titles could direct the insertion to a different
occurrence from the one selected by the random seed.

While checking reproducibility of the repair, the local resume regression
showed that an existing result directory accepted changed backend labels,
adapter declarations, replication counts, timeouts, worker counts, partitions,
and sweep seeds when case IDs stayed the same. That could replace a summary
with new configuration labels while retaining old observations. Logs:
`/tmp/caplab-spec-red.log` and `/tmp/caplab-spec-focused.log`.

## Repair

The prospective CAPLAB conclusion operator inserts after the complete selected
heading occurrence. It preserves the heading identifiers and existing
section content. Removing the recorded inserted paragraph recovers the exact
control bytes. The historical implementation remains untouched in the
vendored module. This repairs an unintended structural cue; it is not a
semantic validation of every generated conclusion.

Before any pool attempt, `run-spec.json` now freezes the ordered case plan,
anchor membership, backend label, declaration hash, requested measurement
parameters, concurrency settings, environment, sandbox availability,
base-registry hash, response and oracle contracts, Python version, and
advisory-package source hashes. It stores a canonical YAML hash of the
declaration, preserving date types, rather than its possibly sensitive
configuration values. Source hashes distinguish
the corrected generator from earlier code using the same operator name.

Each new result row and summary names that specification's SHA-256.
Resumption checks the retained specification, requested configuration, and
all retained row references before invoking an adapter or modifying results.
Unknown or missing specifications cannot be manufactured around old rows.
Changed declarations, inputs, parameters, or instrument source require a new
directory. The scorer checks the retained record's digest and consistency
with row and summary references and backend labels, and includes its digest
in run provenance.

The historical scoring path remains available for unversioned runs. No
historical rows, summaries, claims, or exports were rewritten or reissued.
The unrelated untracked design draft was preserved.

## Boundaries

The specification binds recorded local configuration and source hashes. It
does not attest to a native harness binary, model identity, account state,
all ambient environment variables, third-party dependencies, or modules
already loaded before an on-disk source change. It is not one-shot execution
custody: recovery of an invocation lost before its row was persisted remains
a separate concern. It is not a concurrency lock for two invocations writing
one output directory.

Matching or different specification hashes alone cannot establish whether
two bindings are experimentally comparable: backend declarations are supposed
to differ, while common task and protocol conditions must be checked
separately. No comparison or qualification rule was changed here. Other
marker-based operators and the semantic status of their assertions still
need independent scrutiny. Production outcome requirements and the confirmed
placement freeze remain in force; the broader goal is not complete.

## Verification

The focused suites passed 148 tests. Full `make check` passed **732 tests
with four existing skips** in 116.634 seconds, logged at
`/tmp/caplab-spec-make-check.log`. A final duplicate-heading assertion verified
that the reported anchor identifies the heading preceding the insertion;
all three focused operator tests passed after that test-only addition
(`/tmp/caplab-spec-final-anchor-check.log`). The skipped campaign and
PostgreSQL integration checks remain outside this verification.

Tests cover exact control recovery, preserved heading identifiers, duplicate
titles, unchanged vendored mutations for unaffected operators, unchanged
configuration resumption, incompatible measurement parameters, changed case
hashes and declaration/source hashes, absent or altered specification files,
inconsistent row references, and backend relabeling despite an intact spec
reference. A read-only serialization check passed for all 102 installed
backend declarations (`/tmp/caplab-spec-declaration-check.json`); the YAML
date regression preserves the distinction between dates and strings.
`git diff --check` passed. No model was
invoked; pool integration tests use authored local subprocess fixtures.

## Engineering guidance and alternatives

Pincite's validated release supplied packet `pkt-4e2ce4a2191748f7`, content
SHA-256 `4e2ce4a2191748f76406a4d85d8a56356ab801da769b1117fab5be1890e10844`,
doctrine `doctrine-f6bbb5196a3f8bf9`, retriever
`retriever-ec995ecdd083b2c8`. Applied guidance:
`testing-test-first-feedback`, `universal-repository-contract-precedence`,
and `universal-preserve-behavior-by-default`.

No change would retain an extra structural defect and permit mislabeled
resumption. Only fixing paragraph placement would leave pre-repair and
post-repair observations able to share one run. Per-operator version labels
would not cover declaration, replication, input, or other source changes.
The frozen specification protects those observed configuration boundaries
without claiming the full native-harness custody contract.

Material requirements concern the authorized scope, single-mutation
invariant, exact local configuration, evidence preservation, and rejection
before invocation or result writes. Current repository contracts, source
inspection, and the regression checks above supply that evidence. The
packet's remaining generic ingest, deduplication, asynchronous UI, attention
budget, top-N selection, operational paging, and whole-system gate inventory
requirements are nonmaterial to this bounded repair. Configuration-reference
checks are covered by specification and row mismatch tests. Native serving
parity, production incidence, and semantic correctness remain unverified;
the boundaries above exclude those claims. Doctrine is advisory and supplies
no CAPLAB decision or acceptance authority.
