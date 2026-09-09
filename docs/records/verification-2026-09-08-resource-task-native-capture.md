# Retain task and native-format evidence after resource failure

Date: 2026-09-08. Baseline: `2dee28b`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Extend only `scripts/probe_cgroup_resource_limits.py` and this record. Connect
the existing fixed resource fixtures to `SupervisedTaskCapture`, descriptor
native collection, byte accounting and tool-pair inspection. Add private
64-MiB `/work` and `/episode` tmpfs mounts to the three existing writable
mounts. Authenticate all five descriptors against the blocked peer's mount
table, ownership and exact fixture cgroup. Seal the before task inventory
before acknowledging release; finish and collect only after that cgroup is
empty. Retain all five mount inventories under the existing combined 40-MiB,
100-entry allowance, with separate 10,000-byte/100-entry task and
100,000-byte/100-entry native collection allowances. Each process retains at
most 200,000 combined stream bytes and runs for at most ten seconds.

Use authored Codex-format session records and one small task file, with a
started tool item before resource pressure and a completed item/final message
only after successful work. No Codex or Claude executable, model, credential,
network or historical capture is involved. The five modes remain control,
memory, pids, tmp-memory and shm-memory. Require resource counters, exact task
bytes, retained session/diagnostic bytes, and missing final output after OOM;
do not infer native completeness or workload correctness from stream EOF.

Authorize one new generated `caplab-resource-probe-<uuid>.service`, bounded
at 128 MiB, no swap, 64 tasks and 60 seconds. Its five sequential child
cgroups keep the existing 32-MiB/no-swap, group-OOM and 8/16-task limits.
The outer capture is limited to 70 seconds and 200,000 stream bytes. Stop
only that exact unit, close owned descriptors, kill only its owned child
cgroups when needed, remove those groups, and verify the unit and parent
cgroup are absent. Stop before any additional live unit unless a new scoped
authorization is recorded. Preserve failed raw results without retries.

Permit local static/focused offline checks and `make check`; retain new
synthetic custody, source hashes, authorization and verification under
`/tmp/caplab-resource-capture-*`. Consolidate advisory packets before deleting
only their named scratch files. Preserve existing evidence, `docs/designs/`,
sibling worktrees, unrelated runtime state and pending human questions. No
Plane write, external message, push, study admission, ranking or independent
acceptance. Commit only the named files locally; authorization expires at
commit. Stop on ambiguous ownership or unsupported source-lifetime claims.

## Decision and scope

Leaving the components separate would preserve their individual tests but
would not establish that the before-capture barrier and native retention work
with an OOM-killed writer. Extend the existing fixed probe to exercise this
connection, rather than adding a second resource supervisor. These are new
synthetic fixtures, not a native repair attempt or capability measurement.
Native Binding, actual invocation evidence, general frozen-task copying,
representative repair/coding and independent judgments remain outstanding.

## Preparation failure and replacement authorization

The first unit, `caplab-resource-probe-b1d7798aa510486d94b0ef60e9a3c93a.service`,
failed before workload launch. A local retention-loop variable named `digest`
shadowed the new hash helper, raising `UnboundLocalError` during preparation.
The local variable is renamed `inventory_hash`. Raw output and prepared
synthetic inputs remain at `/tmp/caplab-resource-capture-run/`; outer log is
`/tmp/caplab-resource-capture-live.log`. Cleanup recorded `LoadState=not-found`.

Authorize one replacement generated unit under exactly the limits, fixture
set, effects and cleanup above, using fresh custody
`/tmp/caplab-resource-capture-run-fixed/`. This replaces the consumed first
execution allowance; it does not permit further live retries. Keep both runs
and their source snapshots. This authorization also expires at commit.

## Verification

The replacement unit,
`caplab-resource-probe-a5886c59138e405abf29bf4fe19d6a51.service`, completed
all five fixtures. Custody is `/tmp/caplab-resource-capture-run-fixed/` and
the outer log is `/tmp/caplab-resource-capture-live-fixed.log`.

| Mode | Process exit | OOM-kill counter increase | Task-limit counter increase | Retained mount bytes | Tool item |
| --- | ---: | ---: | ---: | ---: | --- |
| control | 0 | 0 | 0 | 471 | paired |
| memory | -9 | 4 | 0 | 25,608,528 | request without result |
| pids | 0 | 0 | 2 | 465 | paired |
| tmp-memory | -9 | 4 | 0 | 25,633,104 | request without result |
| shm-memory | -9 | 4 | 0 | 25,641,296 | request without result |

Each case retained five mount inventories after its cgroup became empty.
The before task inventory contains `item` with exact bytes `old`; the after
inventory contains `changed` and the authored mount marker. The two task
inventories total 33 retained bytes. Native collection preserves the authored
session records and binary diagnostic bytes. Only the control and pids cases
have final messages. All three OOM cases explicitly retain `final_message`
as missing and a started tool item without a result. Stream capture reached
EOF in all cases, including exit -9; this does not imply native completeness.

The handoff identity and before-inventory hash are written before release.
Resource-exit observations are written before after-capture and native
collection, so a later capture exception leaves those observations available.
The task and native receipts are checked against the same handed-off mount
identities and process receipt. Original synthetic host task/preparation
directories are removed before derived capture verification. After the
service exits and received descriptors close, the outer verifier reproduces
all five reports from retained custody. The exact unit was already unloaded
when cleanup attempted to stop it (`stop` exit 5, `LoadState=not-found`);
the recorded delegated cgroup is absent.

The offline driver `/tmp/caplab-resource-capture-offline.py` repeats these
checks and retains thirteen refusals at
`/tmp/caplab-resource-capture-offline/report.json`: final-message linkage for
each of the three OOM cases; wrong attempt, collection and handoff anchors;
a changed pre-release inventory anchor; a changed resource/process receipt;
modified task bytes; a missing native payload; a changed handoff source
identity; a missing runtime mount inventory; and an altered combined byte
total. Corruption cases use separate copies of the new synthetic custody.
No additional user unit or resource workload was launched for these checks.

This extends the fixed probe's observations and verification receipts to v5.
Its native-format producer remains authored Python. The native linker reports
`executed_invocation_bound=false` and `native_capture_complete=null` even when
the authored model/effort fields agree. Pressure was applied to scratch,
temporary and shared-memory mounts; this run does not establish every task or
runtime allocation/inode failure path, adversarial containment, supervisor
crash recovery, native compatibility, or a complete live-attempt launcher.
CAPLAB-84 remains incomplete, and these results supply no reviewer ranking or
independent acceptance.

`make check` passed 1,227 tests in 165.067 seconds with four skips; log
`/tmp/caplab-resource-capture-make-check.log`. The probe's five live fixtures
and thirteen offline refusals are separate from that test count. Ruff's F
checks passed, embedded Python programs parsed, the document link resolved,
and `git diff --check` passed. No probe source changed after the successful
live run or full suite. Both executed source versions match their retained
intent hashes; both generated cgroup paths were rechecked as absent.

The successful observations SHA-256 is
`b7d6a42ec35b97624931e8232ae40ec717d4ababf2f1ffc75195c02e4a1f081a`;
its verification receipt SHA-256 is
`94491f8378f3dfcc447f0734a37372afe61ae264a104491e9b2f856dd3016b00`.
The offline report SHA-256 is
`b7e57c8a13be82b13a2ed3f2921ae1d2dca5af9baf001e1ab90abd1ab536b72c`.

## Advisory provenance

Pincite's release gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Packet `pkt-fc41a5e035403437` has content SHA-256
`fc41a5e03540343767228da7080caa138b066a52663bac04680f66dec3f9392f`;
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.

Four served concepts informed the work: repository-contract precedence,
evidence before intervention, preservation of existing behavior, and action
within recorded authority. Citation classification marked all four valid.
The packet's 35 remaining obligations are classified individually as
nonmaterial with rationale in retained provenance. They concern personal-data
lifecycle, caches, performance objectives, heap/profile interpretation and
performance metric definitions. This change uses new synthetic bytes, adds no
cache or performance claim, and retains the existing fixed resource-counter
method. It does not recommend production limits from these observations.

Consolidated provenance is `/tmp/caplab-resource-capture-verification.json`,
SHA-256 `b8dc10a0dbf0331a7adecabfaaa287d8b1aad6e8bec08d39fe28515c2a5df60f`.
It contains 364 artifact hashes, complete advisory packet/evidence/citation
bytes, the individual obligation classifications, verification totals and
both cgroup absence checks. Eleven named advisory scratch files were removed
after consolidation. Raw fixture custody and failed execution output remain.
The accompanying local commit consumes both execution authorizations. No
model call, tracker write, external message, push or independent acceptance
occurred.
