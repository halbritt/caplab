# Verify resource limits across writable fixture mounts

Date: 2026-09-08. Baseline: `0cd940e`. Primary-agent authority:
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Extend only `scripts/probe_cgroup_resource_limits.py` and this new record.
Preserve the existing fixed control, scratch-memory and caught-pids fixtures;
add fixed memory-pressure cases for `/tmp` and `/dev/shm`. Make the private
root, `/dev` directory and `/proc` read-only while preserving the declared
writable tmpfs mounts. Retain each namespace's mount table and verify the
expected writable mounts before fixture pressure. The control must exercise
writes in all three allowed mounts and refused writes outside them. Preserve
the existing descriptor handoff and retained `/scratch` marker after OOM.
This is a model-free diagnostic extension, not a native launcher or a complete
containment/eligibility gate.

Authorize at most three new sequential transient user units named
`caplab-resource-probe-<uuid>.service`, each with 128 MiB memory, zero swap,
64 tasks and 60 seconds. Only their own delegated fixture groups may be
created, configured, killed or removed. Each of the five trusted fixtures has
32 MiB memory, zero swap, group OOM handling, at most 16 tasks (eight for the
pids fixture), ten seconds and 200,000 combined stdout/stderr bytes. Each
memory fixture attempts at most 64 one-MiB writes in its named tmpfs; the pids
fixture attempts at most 32 short-lived children. No native harness, model,
credential or network use. Do not execute untrusted code or mount a writable
host directory into any fixture.

Keep raw commands, counters, mount tables, partial captures, source hashes and
verification under fresh private `/tmp/caplab-mount-coverage-*` paths. Outer
capture is bounded to 70 seconds and 200,000 bytes. Inventory retention remains
bounded to 40 MiB and 100 entries per fixture. Only `/scratch` payloads are
retained; temporary/shared-memory payloads are disposable and their absence
must remain an explicit limit. Preserve success and failed probe custody.
Verify independent kernel events after quiescence, all retained payloads after
service exit, and exact owned unit/cgroup cleanup. Run offline negative
expectation checks and `make check`; do not repeat a live run just because a
poll times out. Unsupported delegation, mount behavior or unavailable receipt
must fail the probe rather than adopt weaker requirements.

Preserve all runtime owners, standing tests, historical evidence, world files,
`docs/designs/`, sibling worktrees, unrelated services/cgroups/timers, tracker
state and model/spend restrictions. No study admission, scoring, ranking,
placement, native attempt, external message or push. This authorization supplies
no independent acceptance. Consolidate advisory provenance before deleting
only named advisory scratch, then commit these two files locally. Authorization
expires at commit; stop before wider required effects.

## Selected change and evidence

The preceding [storage inspection](inspection-2026-09-08-runtime-storage-bounds.md)
showed that a cap on one tmpfs left the private root writable. The existing
[resource probe](implementation-2026-09-08-resource-limit-probe.md) retained
kernel events and `/scratch` files after failure but did not exercise alternate
writable mounts. Leaving that probe unchanged would leave a concrete coverage
gap before native integration. The chosen change extends its fixed fixtures;
it adds no arbitrary-command runner or production resource policy.

The namespace now has three writable tmpfs mounts: `/scratch`, `/tmp` and
`/dev/shm`, each configured for 64 MiB. Its private root and proc mount are
read-only. Instead of the larger generated device tree, the fixed fixture has
only read-only binds for `/dev/null` and `/dev/urandom`; no native device or
terminal compatibility is claimed. The same 32-MiB, zero-swap fixture cgroup
covers each executed memory-pressure case.

Before acknowledging the descriptor handoff and allowing fixture execution,
the supervisor reads the peer's `/proc/<pid>/mountinfo`. It checks all rows,
requires exactly the three writable tmpfs mount paths and the named read-only
mounts, and refuses duplicate mount paths. The exact table and parsed rows
are retained with the peer and descriptor identity. This is a pre-execution
observation of the fixed trusted topology, not proof against later mount changes.

Bubblewrap's `--remount-ro` is nonrecursive, so the writable child mounts remain
separate checks. The installed help and the version-matched
[Bubblewrap 0.9.0 source](https://raw.githubusercontent.com/containers/bubblewrap/v0.9.0/bubblewrap.c)
agree on that option. Kernel documentation includes tmpfs/shared-memory data in
memory accounting and distinguishes memory pressure, OOM and killed-process
counters. It also identifies allocations that need not raise an OOM event;
absence of such an event cannot establish complete capture.
[Linux cgroup v2 documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)

## Executed verification

Two of the three authorized units were used. The first probe's control failed
because creating nonexistent `/proc/other` raised `ENOENT`; that operation
cannot establish read-only enforcement. The other three refused writes and
all three memory-pressure cases had already run. The failed probe, its exact
source snapshot and all five retained inventories remain under
`/tmp/caplab-mount-coverage-first*`. Its generated unit and cgroup were removed.
The control was corrected to open the existing `/proc/self/comm` entry; its
failure must be `EROFS`, matching the other read-only checks.

The final probe exited 0 on Linux `6.8.0-138-generic`, Bubblewrap `0.9.0`,
systemd `255.4-1ubuntu8.17` and Python `3.12.3`. Raw custody is
`/tmp/caplab-mount-coverage-final/`; unit
`caplab-resource-probe-96b72da2196440ada3724c77d921dca4.service`.

| Fixed fixture | Outcome | Independently retained event delta |
| --- | --- | --- |
| Control | Exit 0; writes succeed in all three declared tmpfs mounts; `/other`, `/dev/other`, `/usr/other`, `/proc/self/comm` each refuse with `EROFS` | Memory OOM and pids max zero |
| Scratch writes | Signal 9 | Memory max 18, oom 1, oom_kill 4, oom_group_kill 1 |
| Caught task limit | Exit 0 after caught fork failure and child cleanup | Pids max 2 |
| Temporary-directory writes | Signal 9 | Memory max 18, oom 1, oom_kill 4, oom_group_kill 1 |
| Shared-memory-directory writes | Signal 9 | Memory max 18, oom 1, oom_kill 4, oom_group_kill 1 |

Each process had complete retained stdout/stderr and an empty fixture cgroup
before collection. The supervisor retained the `/scratch` marker in all five
cases and the scratch writer's partial payload, verified again after service
exit. Temporary/shared-memory pressure payloads were not retained. Their
surviving `/scratch` markers verify the existing handoff under those failures;
they do not constitute complete runtime-output custody.

The final v3 observation/verification records name five fixtures. Previous v2
records and authorizations remain historical evidence, unchanged. Both exact
probe script hashes match their retained execution intents. Kernel event counts
are observations for these runs, not fixed expected counts; verification
requires the relevant positive delta rather than the number 18 or 4.

Ten offline negative cases were refused: writable private root, unknown writable
mount, absent `/tmp`, a writable non-tmpfs filesystem, stacked mount paths,
empty mount table, absent read-only `/usr`, missing OOM-kill evidence for each
new memory case, and a modified parsed mount summary. Those checks use retained
real mount tables and counters with explicit mutations; they do not fake
successful native execution. Script and output are
`/tmp/caplab-mount-coverage-offline.py` and
`/tmp/caplab-mount-coverage-offline.json`.

Both unit-state reads reported `not-found`, and both delegated cgroup paths
were absent. Exact-name stop commands returned 5 because collection had already
removed the units; the separate state reads verified cleanup. The probe keeps
those outcomes rather than treating an attempted stop as proof of removal.

## Interpretation and remaining integration

These observations extend the resource probe from one writable mount to three
and exercise refusal outside the declared paths. They support continuing toward
a native launcher with a read-only root, explicit writable surfaces and retained
kernel evidence. They do not establish a universal allocation-failure detector,
inode/logical-byte bounds, native compatibility, adversarial isolation, provider
routing, account/model identity, complete capture, or representative costs.

The host, same-user custody parents, supervisor and fixture source remain
trusted. Mount topology is inspected before execution; the fixed fixtures do
not attempt namespace escape or mount reconfiguration. A production adapter
still needs task/runtime preparation, initial/final inventories, the selected
native invocation and authentication, output retention for every required
surface, and separately frozen budgets and stop policy. These diagnostic
numbers are not campaign budgets. No roadmap item is closed, and no study
observation or independent correctness judgment is created.

## Suite and advisory closure

`make check` exited 0: 1,205 tests, four skips, 151.876 seconds. The complete
log is `/tmp/caplab-mount-coverage-make-check.log`. The standing suite does not
launch this resource probe; the two separately authorized real executions and
ten negative checks supply its direct verification. No standing test or runtime
owner changed. The documentation guard checked signatures, flags, paths,
versions, counters, retained-output scope and cleanup against source and receipts.

The validated Pincite release is `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
Final packet `pkt-c726018e9fef5569` has content SHA-256
`c726018e9fef5569dc22bd982907c8d9f16051224fb52207cce0ba7049c2b5c8`.
Its execute ceiling is advisory; the exact authorization above governs effects.
Applied repository-contract precedence, evidence before intervention,
authority-bounded action and structured cleanup. The implementation extends a
trusted diagnostic rather than adopting a new native sandbox policy.

Fourteen missing generic obligations remain nonmaterial to this bounded claim:
CI/build/version matrices and formatter/checker configuration are unchanged;
this is a new fixture extension rather than a production-defect repair;
fixed ASCII mount names add no general text-decoding claim; no code-coverage
percentage or independent adequacy claim is made; no quantified intervention
cost, future architecture choice, comprehensive latent-risk audit, formal
leave-code-alone/preservation export or exhaustive repository-contract audit
is asserted. Each obligation and its individual rationale are retained in
`/tmp/caplab-mount-coverage-verification.json`.

That verification artifact consolidates both advisory packets, five typed
evidence records and citation classification before the eleven named advisory
scratch files are removed. It pins both raw probe trees, the failed and final
script identities, offline checks, source metadata, authorization, observations,
completed record and full-suite log. All failed and successful probe custody
remains private and available. No historical evidence was processed or changed.
This local commit consumes the authorization; no push, tracker change, study
readiness or independent acceptance is recorded. The CAPLAB goal remains active.
