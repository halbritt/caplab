# Resolve retained review bodies from source object locators

Baseline `2fdcd8b`. Decision mechanism: primary agent under the continuing
CAPLAB improvement goal and [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Observations and decision

Striatum's older `admission.go` emits body store/address/size/compression but
no body content_hash. The newer `admission_v2.go` objectPin emits both address
and content_hash. CAPLAB only reads content_hash, so the address-only form
cannot reach the object reader. Its tests currently replace that reader and
use invented hash strings, leaving this compatibility gap undetected.

Resolve an exact `sha256/<64 lowercase hex digits>` address or a complete
bare content_hash. When both are supplied, require agreement. Reject malformed
or conflicting references before filesystem access; do not fall back from an
invalid address to another field. Check optional store/compression/size
metadata against the supported object representation and returned body bytes.
Continue using the existing hash-verifying object reader. Keep source body
locators and explicit missingness in each observation. Expose an optional
object-store root in both CLIs and record the resolved root, retaining the
current graph root as the default. Version the prospective method/report.

No change leaves the address-only population unreadable. Using arbitrary
paths or silently choosing one contradictory hash would weaken custody.
This is a semantic repair, not evidence admission or review adjudication.

## Authorization before execution

Authorize edits to the criterion reader, canary, their tests, new
`tests/test_review_body_address.py`, and this record. Construct local SOB1/zstd
objects and ledger fixtures in temporary directories, exercise both CLIs
against those stores, and run focused/full checks before committing this scope.
Read no live graph objects or production ledger exports for this repair.

Retain current source snapshots and private verification artifacts under
`/tmp/caplab-review-body-address-*`. Copy only the inspected Striatum
`internal/store/admission.go`, `internal/store/admission_v2.go`,
`internal/store/object.go` and `schema/ledger-records/artifact_admitted.schema.json`
there, recording source commit, original path and SHA-256. Those are external
interface evidence, not imported governing research or historical admission.
Preserve all existing reports and historical records. No provider/model/native
calls, credentials, spend, tracker writes, outbound messages, push, changes to
Striatum or its live store. Preserve unrelated files, `docs/designs/`, worktrees
and services. Stop for unexplained failures or a contradictory source contract;
retain failed evidence. This authorization expires at the local commit.

Body-to-review subject attribution remains a separate unresolved question.
This repair establishes locator resolution and verified bytes only.

## Execution and verification evidence

The external source snapshot is Striatum commit
`5ea87ca65c1bd25f228c0447110d991a3f0de8c8`; the private source manifest at
`/tmp/caplab-review-body-address-sources.json` binds original paths, copies,
commits and hashes. Both admission writers and `object.go` were inspected.
The older writer's missing body.content_hash is a specific compatibility gap;
the newer writer already supplied that field and was readable before repair.

The first constructed-store test retained a real SOB1 header and zstd frame
containing UTF-8 JSON. The old reader reported no verdict for the address-only
admission. The initial assertion was strengthened from generic falsiness to
an exact `False` check so missingness could not satisfy a refusal expectation;
the preserved strict red run then failed explicitly on `None`. Resolving the
address recovered the exact refusal and Unicode summary.

Subsequent red tests demonstrated that invalid/conflicting references could
reach object access, mismatched size metadata did not suppress a verdict, and
both CLIs lacked the store-root option. The completed repair validates the
locator and optional metadata before access, checks returned byte length,
and records the selected absolute root in `snapshot.object_store`.

Both readers report `sha256-address-or-hash-agreement/1`; the canary version is
`caplab-review-canary/8`. Baseline versions 1–7 remain readable and their source
hash/window handling is unchanged. A follow-up may use a newly selected store;
the root is recorded, but it is not an immutable inventory or a claim that body
availability is identical to the older report. Existing report directories
remain protected against overwrite.

`review_body_reference` owns the source-locator interpretation in the existing
criterion reader. Raw body-reference metadata is preserved in each observation.
Address and bare hash must have exact lowercase hexadecimal SHA-256 form;
traversal, unsupported prefixes, malformed values and disagreeing fields supply
no object path. Optional store/compression tags must be object/zstd, and size
must be a nonnegative integer excluding booleans. A valid locator whose object
is missing, corrupt or hash-mismatched remains unavailable/unverified. A
verified body whose recorded size differs is reported as body-size-mismatch.

The existing `M.store_object` still owns decompression and returned-byte hash
verification. It is unchanged. This repair does not claim to validate every
SOB1 header field, impose decompression resource limits, or make a mutable
store snapshot immutable. No object lookup was added for metadata that fails
the new reference checks, and no arbitrary file path is accepted as a locator.

The five new tests exercise real private filesystem objects: address-only,
hash-only and matching dual references, 20 invalid-reference/metadata variants,
wrong-sized/missing/corrupt/hash-mismatched objects, both CLIs, read preservation,
existing-report protection and an empty alternate store. The Unicode payload
is compared after actual decompression and JSON parsing. Existing parser tests
now use syntactically valid hash placeholders; their object-reader doubles
continue to isolate parser behavior and are not used as storage-integrity proof.
An older direct observer call retains its default store argument compatibility.

The focused set passed 59 tests; Ruff F and diff checks passed. Retained failure
and success logs distinguish the original locator gap, reference rejection,
size checks, CLI support and fixture reconciliation.

The private comparison at `/tmp/caplab-review-body-address-fixture-check.json`
records two constructed admissions over the same 64-byte body. The address-only
case changes from unknown to refused, while the dual-reference case remains
refused. Both CLIs read the retained private store, and the stored object's
bytes remain unchanged. The fixture root contains both ledgers, the object and
CLI outputs. This demonstrates compatibility and custody for these constructed
inputs, not the number of affected production reviews or reviewer accuracy.

## Doctrine and final checks

The release retrieval gate passed with fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`
and retriever `retriever-ec995ecdd083b2c8`. Initial packet
`pkt-f89186a451c5c08e` was reassembled once with four typed evidence records.
Final packet `pkt-577fb44a5c9fc0f0` has hash
`577fb44a5c9fc0f0b8f237c368d33744384e20368f83b17ee4c3587ed6de6e39`.
The question nominated no precise concepts; this is baseline/routed guidance,
with the repository and inspected producer defining the actual contract.

Applied `universal-repository-contract-precedence`,
`universal-evidence-before-intervention`, `agent-conduct-authority-bounded-action`,
`implementation-placement-by-ownership`, `python-runtime-static-boundary`,
`python-text-bytes-boundary`, and `universal-preserve-behavior-by-default`.
The AI failure-mode review focused on a plausible but unsupported field name,
mocked storage hiding the gap, and falsiness accidentally equating an unknown
verdict with refusal. The stronger real-store test distinguishes all three.

Fifteen residual obligations are nonmaterial: recurring-change evidence (1)
and expected future change (1) are unnecessary to establish this current gap;
toolchain/version/configuration inventories (6) and annotation/checker costs
(2) concern no new language facility or typing claim; resource acquisition,
nesting and cancellation policy (5) concern the unchanged object reader rather
than a new resource-lifetime mechanism. No decompression-limit or whole-store
integrity claim is made. Authority, runtime reference checks, source semantics,
and actual byte round trips have their own evidence above.

`make check` exited zero: 1,320 tests in 169.796 seconds, four skips. The full
log is `/tmp/caplab-review-body-address-make-check.log`. No runtime/test edits
followed the run. This is verification of the scoped repair, not reviewer
qualification, independent acceptance, production replay or roadmap closure.

Private verification manifest:
`/tmp/caplab-review-body-address-verification.json`, SHA-256
`9a7a2780ebade600abf5a7dab169c0df49e9021dfd159c7164819e733b418775`.
It covers 45 artifacts, source snapshots checked against commits, five current
runtime/test hashes, both constructed admission payloads checked against the
copied schema, the actual stored body hash and seven valid doctrine citation
classifications. The schema's open body object does not establish locator
semantics; the source writers and real-object tests supply that evidence.
Ten temporary packet/evidence/citation files were embedded byte-for-byte,
verified and removed by exact path. Source copies, failed checks, constructed
store and ledgers, CLI reports and verification scripts remain available.
