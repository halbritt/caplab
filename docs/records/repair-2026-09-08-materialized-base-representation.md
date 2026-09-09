# Refuse compact anchored objects claimed as expanded bases

Date: 2026-09-08. Baseline: `0ad1e2c`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Reproduce the object-representation gap in
`src/caplab/advisory/materialize.py` with newly authored synthetic objects.
Add regression tests to `tests/test_advisory_materialize.py`. If reproduced,
reject non-null anchors for `materialized_base`, and for `product-object`
claimed as `whole-tree`, at source loading and manifest verification. Load
and validate a replacement source before deleting existing case payloads.
Update owner docstrings and this record. These are the only repository edit
targets. This is a semantic defect repair, not a structural refactoring.

Preserve explicitly partial anchored product views, unanchored full products,
Git archives, absent bases, canonical serialization, hash arithmetic, overlay
semantics, and reuse of valid cached manifests. Do not introduce implicit Git
expansion, a new schema, or a broader cache-identity policy. A cached manifest
containing the contradiction must fail verification; failed source validation
must leave its existing bytes in place. This does not make rebuilding atomic
against every later write failure.

Run focused tests and `make check`, including the existing suite's prescribed
read-only store checks. New tests and probes use synthetic inputs. Retain
baseline source, authorization snapshots, test logs and verification receipts
under `/tmp/caplab-base-representation-*`; consolidate advisory provenance and
remove only named advisory scratch. Commit the three changed files locally;
authorization expires at commit. Stop if reproduction contradicts this
diagnosis or the repair needs broader effects.

No historical evidence copying, admission, rewrite, purge or reprocessing;
no native harness/model attempt, study run, score, qualification, tracker
mutation, external message, push, service change or dependency change.
Preserve unrelated `docs/designs/`, sibling worktrees and timers.

## Decision and bounded rationale

The materializer describes `materialized_base` as the tree expanded by the
production driver, but currently reads only `files` from any supplied product
and retains its anchor in the manifest. Content hashes establish byte identity;
they cannot establish that an anchored overlay includes its referenced tree.
The selected repair refuses this contradictory representation. Doing nothing
would permit an overlay-only view to verify under a whole-tree claim. Implicit
expansion would add source resolution and historical-custody effects outside
this repair. Partial views retain their explicit, narrower meaning.

The corrected historical calculation in
[the review-scope inspection](inspection-2026-09-08-production-review-403617-scope.md)
motivates checking this boundary. It is not evidence that any historical
CAPLAB case actually passed a mislabeled base to this materializer, and no new
historical reads are authorized by that reference. Test success will establish
the local representation guard, not reviewer correctness or acceptance.

## Reproduction and implementation

The baseline failed 13 subcases across three new test methods: nine fresh
contradictory inputs, three self-consistent contradictory cached manifests,
and one incomplete case receiving an invalid replacement source. The fourth
new method protects valid partial and expanded views and reuse after the
synthetic store object becomes unavailable. The retained failure log is
`/tmp/caplab-base-representation-red.log`.

One local predicate now checks the same representation rule in `base_files`
and `verify_manifest`. Non-null includes empty or false-valued anchors;
JSON null remains an unanchored representation. A contradiction raises
`ValueError` during source loading and returns false during manifest
verification. Replacement source loading happens before old base/evidence
directories are removed. A verified valid cache still returns immediately.

The focused materializer and tree-v1 suite passed all 30 tests in 0.279 seconds.
The log is `/tmp/caplab-base-representation-focused.log`. The tests redirect
only the external object-store root: compression, content hashing, decoding,
manifest persistence and payload reads use their real implementations.

A separate inspectable probe retained a synthetic object and the old writer's
manifest in `/tmp/caplab-base-representation-probe-r9rr715f/`. The old writer
claimed `whole-tree` with `materialized_base`, wrote only `overlay.txt`, and
verified the manifest. The repaired verifier returns false for those same
bytes; materialization raises, preserving both manifest and overlay hashes.
Inputs, outputs, source hashes and preservation checks are recorded in
`/tmp/caplab-base-representation-probe.json`; its script and baseline source
remain under the same prefix.

Seven function source segments are unchanged: `store_object`,
`canonical_product`, `tree_hash`, `apply_overlay`, `declared_base_hash`,
`git_archive_files`, and `write_files`. Thus the representation refusal does
not change the compact or expanded hash calculations. The caller still must
supply the correct source object. This check does not establish external Git
tree completeness, registry-to-cache identity, or atomicity of later writes.

## Advisory closure

Pincite's validated release is
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`; retrieval-state verification
reported fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
The final packet is `pkt-eac3507f91bc74bc`, with four typed observations
covering authorization/contracts, source structure, tests and the runtime
probe. Packet identity, full content hash, corpus/doctrine/retriever versions,
evidence locators and citation classification are retained in
`/tmp/caplab-base-representation-verification.json`.

Selected guidance keeps repository authority first, requires reproduction,
separates a semantic repair from refactoring, preserves supported behavior,
and shares this one rule across its two consumers. The 31 remaining generic
obligations are retained individually with nonmaterial classifications and
rationales in that receipt. They concern database identity, bulk discovery,
symbolic references, ranking, production monitoring/endpoints/gate parity,
historical incidents, optional co-change history, broader future-change/risk
assessment and formal procedure exports. None is used to claim a broader
audit, live integration, historical incident, or acceptance. The scoped
preservation matrix, reproduction and authorized alternative analysis remain
the evidence for this repair.

## Verification and completion

`make check` exited 0: 1,182 tests in 216.612 seconds, four skips. The retained
log is `/tmp/caplab-base-representation-make-check.log`. Final source and test
hashes are recorded with the probe and focused/full-suite log hashes. All six
selected doctrine citations classified as valid packet citations. Ten named
advisory scratch files were consolidated into the verification receipt and
removed; baseline source, authorization, probe inputs and results remain.

The final diff contains the materializer owner, four new regression test
methods and this record. No new test substitutes decoded object bytes or a
manifest verification result. Test and documentation guard checks found no
additional repair needed in the changed surface; the source docstring states
the external completeness limit. Local integration consumes this bounded
authorization. There is no independent acceptance or study qualification
claim, and the broader measurement roadmap remains incomplete.
