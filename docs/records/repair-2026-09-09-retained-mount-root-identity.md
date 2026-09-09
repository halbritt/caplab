# Identify retained mount roots by path rather than sort position

Baseline: `6b65601`. Decision mechanism: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md) and the
continuing CAPLAB improvement goal.

## Authorization

Authorize reproducing and repairing root-entry selection in
`scripts/probe_cgroup_resource_limits.py` functions `retain_mount` and
`verify_retention`, adding focused tests under `tests/`, and this record.
Use newly constructed model-free local directory fixtures and private artifacts
under `/tmp/caplab-mount-root-*`; run focused and required repository checks.
Preserve sorted inventory serialization, schemas, retained bytes, quotas,
descriptor ownership, existing process/resource controls, and historical
custody. Do not launch a resource-pressure probe, namespace, native harness,
model or provider process; no operator credentials, tracker mutations,
historical evidence changes, messages, push, or unrelated code changes.
Preserve `docs/designs/`, other worktrees and services. Retain failed evidence
and propagate exceptions. Commit only the bounded repair, tests and record;
authorization expires at commit.

## Observations and selected repair

The current retained-mount writer sorts inventory entries by path, then reads
`entries[0]['source_stat']` as the root identity. Its verifier repeats that
assumption after validating the retained inventory. A legal filename beginning
with `!` sorts before `.`. The wrong entry can therefore cause rejection of a
correct directory identity or comparison against a child object's identity.

The shared `_Inventory.visit` appends the root before descending. The supervised
task recorder reads that unsorted construction list, where the first entry
is the root, before serializing it in sorted order. Its use of index zero has
a different invariant and is not changed here. The retained-mount functions
operate on the sorted representation and must select the exact `.` path.
The generic inventory verifier already requires a unique directory root and
valid payloads; the repair must preserve those checks.

Select the unique `.` entry explicitly in each affected function. Do not
change sorting, ban valid names, weaken descriptor identity checks, or create
a new inventory framework. Leaving the functions unchanged would retain the
identified integration defect. Changing only the writer would leave a later
custody read susceptible to the same confusion.

Verify normal and punctuation-prefixed names, rejection when a child identity
is substituted for the root identity, re-verification after source directories
are removed, and both public helper paths. Tests construct fresh retained
fixtures; they do not copy historical resource-probe evidence or claim new
resource/containment observations. The full suite must remain green before
commit. This repair supports CAPLAB-84 capture integration; it does not satisfy
representative repair measurements or authentication prerequisites.

## Reproduction and causal repair

Before the source change, five new tests produced two assertion failures and
five subcase errors in 0.277 seconds. The normal filename case passed;
`!first`, a leading-space filename and `#metadata` caused the writer to reject
the correct root. Independently constructed, valid retained inventories also
failed verification when a child sorted first. Both writer and verifier
accepted a substituted child identity, so the two negative tests failed to
raise the expected error. The original output is retained in
`/tmp/caplab-mount-root-red.log`.

These cases distinguish sort-position confusion from descriptor closure,
source mutation, or retained-byte corruption: the positive controls use open
root descriptors and retained payload validation, while the negative controls
change the expected identity to that of the first child. Both public helpers
compare the wrong source-stat entry before repair. No resource-limit or
provider behavior is involved.

The repair changes exactly two source expressions, selecting the unique entry
whose path is `.` in each function. Unpacking preserves refusal of an absent
or non-unique root rather than silently falling back to another entry. The
writer's construction invariant and the verifier's existing root-directory,
uniqueness, payload-hash, combined-budget and marker checks remain unchanged.
No inventory byte ordering or receipt schema changes.

All five focused tests then passed in 0.442 seconds, including independent
verifier inputs and a writer-to-verifier round trip over all five named mount
surfaces after removing their source directories. The fixtures are ordinary
local directories labeled with the probe's mount names, not newly executed
namespace or resource-pressure probes. The descriptor remains caller-owned
and valid after writer success or failure. Ruff's undefined-name/unused-import
checks passed for the source and tests. Full-suite verification is recorded
separately below when complete.

## Advisory provenance and scope review

The validated Pincite release gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
Initial packet `pkt-7f45d32d7d7233fa` identified the obligations. One typed
evidence pass retained authority, repository contracts, source structure and
actual before/after focused test results. The final packet
`pkt-c88423b77cced858` has content SHA-256
`c88423b77cced858d03a01a42f43f4eaa77286b83c9e94d3e2a06f85673c9ce7`.

All six remaining obligations concern whether a new architectural boundary is
earned. They are individually retained as nonmaterial because this repair
introduces no boundary, module, data owner or topology. Citation closure uses
`debugging-causal-repair`, `implementation-risk-driven-tests`,
`universal-explicit-invariants`, and `universal-repository-contract-precedence`:
repair the observed first divergence, test both rejection and false acceptance,
preserve exact root identity, and retain the repository's custody rules.
Generic guidance neither authorizes historical effects nor changes acceptance
criteria. The source/test review found no fallback success, swallowed errors,
new dependencies or unrelated refactoring.

A fresh read of work-instance Plane showed 12 open roadmap items, including
CAPLAB-84 In Progress and CAPLAB-80 Ready. The read-only snapshots are
`/tmp/caplab-roadmap-20260909-6b65601.json` and
`/tmp/caplab-roadmap-states-20260909-6b65601.json`. No tracker state changed.
This repair improves the correctness of a capture prerequisite; it supplies
no new reviewer comparison, independent adjudication, native authentication,
resource-pressure measurement or study acceptance.

## Final verification and retained custody

The required `make check` completed successfully: 1,252 tests in 153.394
seconds, with four skips. The log is
`/tmp/caplab-mount-root-make-check.log`. The final source diff contains only
the two root-selection replacements. No source changed after that run.
Local record links and whitespace checks passed. Pincite release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` was rechecked, and all four
structured citations classified as valid packet citations.

Private manifest `/tmp/caplab-mount-root-verification.json`, SHA-256
`ac46016c6b9fd8a12fc7c793dfbb9a3e19f3ce5067fdc3ce541956cd2ffc8c55`,
retains 16 artifact identities and final source/test hashes. Eleven advisory
scratch files were embedded byte-for-byte, rechecked and removed. Test logs
and current roadmap snapshots remain available. No historical experiment
artifacts were changed or read as new measurement evidence.
