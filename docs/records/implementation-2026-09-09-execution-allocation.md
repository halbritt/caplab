# Plan treatment allocation across declared accounts and lanes

Baseline `f2b837e`. Decision owner: primary agent under the continuing CAPLAB
goal and [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Observation and decision

The live work-instance Plane projection contains 86 items, 12 open.
CAPLAB-80 requires account and lane allocation within world, arm and parallel
batch, avoiding treatment assignment that systematically follows execution
conditions. CAPLAB-84 remains In Progress and requires representative repair
measurements. Its native error-path diagnostics do not complete that task.
ADR 0065 still selects no executable study population or Binding.

The inspected active Python sources contain arm shuffling in the older
advisory pool runner, but no prospective account/lane allocation helper.
Select a pure planning helper for complete cycles over explicitly declared
account/lane pairs. Each batch contains one slot per arm on distinct resources;
each world/cycle gives every arm one slot on every pair. Shuffle resource and
arm order, cycle rotations, global batch order and within-batch launch order
using an explicit seed. This is a restricted cyclic allocation procedure,
not sampling uniformly from all possible balanced schedules.

This helper is an available planning procedure, not adoption of a study design.
A study must freeze its allocation and analysis together. Declare at least as
many distinct account/lane pairs as arms; reject insufficient resources for
this procedure rather than serialize arms while calling the batch parallel.
This refusal does not establish that the study is infeasible. Complete cycles
imply an episode multiple; do not silently increase a requested sample size.

Alternatives: manual assignment can satisfy the requirement but currently has
no executable invariant check; unconstrained per-slot randomization permits
complete arm/account confounding by chance; a general scheduling optimizer
would introduce capacity and design policies that remain unresolved. Select
bounded complete cycles with explicit limitations and no execution integration.

## Authorization before implementation

Authorize new `src/caplab/execution_allocation.py`,
`scripts/execution_allocation.py`, `tests/test_execution_allocation.py`,
`docs/product/contracts/execution-allocation-v1.md`, and this record. Use only
new synthetic planning metadata in tests and private `/tmp/caplab-execution-allocation-*`
artifacts. Run focused checks and the required full suite, then commit locally.
Retain the inspected Plane requirements and relevant source hashes as planning
provenance. Do not copy historical research evidence or run old campaign tools.

The input names worlds, arms, account/lane aliases, seed and complete-cycle
count. It reads no credentials, account configuration, world content or model
output. Bound emitted slots to 10,000 and CLI input to 1 MiB. Reject malformed
metadata, duplicate account/lane declarations, unknown fields and JSON
ambiguities. Preserve input objects and all existing runtime behavior.

The report labels proposed slots and declared-metadata-only provenance. It
establishes no sealed assignment, observed identity, genuine concurrency,
capacity, account equivalence, service isolation, blinding, quality or readiness.
No native/model call, spend, live ledger/store access, credential handling,
tracker write, message, deployment, push, study freeze, historical evidence
processing or human judgment. Preserve unrelated `docs/designs/`, worktrees
and services. Stop on a contract conflict or unexplained check failure.
Authorization expires at the verified local commit.

Verify exact per-world/cycle arm-resource counts, one occurrence of each arm
per batch, no within-batch account/lane collisions, launch-order permutations,
determinism and input-order invariance, seed-sensitive assignments, invalid
and oversized input refusal, and CLI JSON boundaries. These are combinatorial
planning checks; no statistical power or real-world balance claim follows.

## Execution and bounded verification

The first test required complete per-world/cycle arm-resource counts and
collision-free batches. After the helper existed, a two-resource/three-arm
case demonstrated that cyclic indexing alone silently reuses an account in a
batch. An explicit capacity-shape refusal now prevents that output. The next
tests exposed accepted invalid metadata and duplicate account/lane identities;
the validated input boundary rejects those before allocation. The final CLI
test first failed because no entry point existed, then passed with the bounded
UTF-8/strict-JSON reader and stdout-only report.

Six focused tests pass. They cover 108 synthetic seed/arm/resource combinations,
the full two-world/two-cycle example, borrowed-input preservation, input-order
invariance, seed-sensitive schedules and malformed input. The implementation
separates input validation/canonicalization from allocation; the focused checks
passed again after that behavior-preserving separation.

The private probe executes the exact documented CLI example and independently
counts its nine arm/account pairs. A deliberately confounded control retains
the same nine slots but covers only three pairs. This illustrates the defect
that total episode counts alone cannot detect. A 10,000-slot boundary plan
passes exact count checks, while 10,004 slots are refused. These are synthetic
planning observations, not native execution or statistical validation.

Artifacts are `/tmp/caplab-execution-allocation-`: `probe.py`,
`probe-result.json`, `example-input.json`, `example-report.json`, red/green
and focused logs, and exact Plane item/state/requirement snapshots. The runtime
uses no provider, scheduler, database or service. The report cannot establish
actual account independence, simultaneous launches or usable study samples.

## Doctrine and claim limits

The release retrieval gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-06e30d08d53dff98` was reassembled once with four typed
evidence records. Final packet `pkt-74aadce9ed24b38f`, content SHA-256
`74aadce9ed24b38f706777de1202a3dc3bbd65b5218bfc23ca133891777836aa`,
uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
Activated concepts, conflicts, authority constraints and prohibitions remained
unchanged after reassembly.

Applied repository-contract precedence, evidence before intervention, bounded
authority, structured cleanup and preservation of existing behavior. The
AI-failure-mode pass focused on duplicate resource declarations, boolean
integers, accidental mutation, seeded cosmetic reordering that leaves arm
assignments unchanged, and confusing a generated plan with verified execution.
Validation and canonicalization are separate from the allocation procedure;
the CLI retains ownership of its bounded file read.

The final 24 unmet obligations are nonmaterial to this bounded claim. Twenty-one
concern performance objectives, profiles, resource measurements and empirical
optimization comparisons: this work changes no execution concurrency and
claims no capacity, latency or memory improvement. Three concern expanded
toolchain/CI/formatter inventories: the helper uses the existing Python
standard library and introduces no dependency, language-version or tooling
change. Current-interpreter execution, public API/CLI tests and Ruff F supply
the scoped conformance checks. No cross-platform or cross-version equivalence
is claimed. The cyclic allocation's combinatorial balance follows the selected
contract and direct counts; Doctrine supplies no statistical validity judgment.

## Final verification and custody

The first full suite passed 1,332 tests in 178.270 seconds with four skips.
Because input validation was separated from allocation during that run, the
full suite was repeated on the final source bytes: 1,332 tests in 190.355
seconds, four skips, exit zero. The final log is
`/tmp/caplab-execution-allocation-make-check-final.log`. Ruff F and diff checks
passed. No runtime, test or contract edits followed the final run.

The final private manifest is
`/tmp/caplab-execution-allocation-verification.json`, SHA-256
`f674ce99be1bf25e872b28f412938cf81382733c0d5e536e960adb7fc2b6660b`.
It covers 30 artifacts, eight unchanged governing/adjacent source files checked
against their commit, and four new runtime/test/contract hashes. All typed
evidence provenance hashes matched. Five doctrine citations classified as valid
packet citations. Ten scratch packet/evidence/citation files were embedded
byte-for-byte, verified, then removed by exact path. Synthetic probe inputs,
reports, scripts, regression logs and planning snapshots remain retained.

The captured complete Plane list and state map still show 12 open items among
86, with CAPLAB-84 In Progress. No tracker field changed, and the reserved
preregistration remains absent. The local implementation is available for a
later selected allocation; no current study allocation, native run, model
measurement, independent acceptance or roadmap completion is claimed.
