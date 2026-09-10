# Capture bounded cgroup resource observations

Baseline `77675b6`. The preceding installed-native diagnostic completed its
fixed tool exchange and full retained inspection, while preserving a transport
closure error. CAPLAB-84 remains incomplete: its current contract also requires
representative repairs, runtime resource usage, incremental capture overhead,
redaction effort and usable/missing capture observations. Live Plane readback
at `/tmp/caplab-post-native-roadmap.json` has 86 items, 12 open. No tracker write
or state change is selected here.

The current resource snapshot records limits/current usage and failure events,
but not CPU usage or peak memory. Retained-file accounting explicitly leaves
runtime peak and incremental capture overhead unavailable. Under ADR 0026 and
the continuing owner goal, select a separate bounded cgroup resource observer
and an explicit prospective capture option. This is measurement instrumentation;
it is not a performance optimization or evidence of reduced observer cost.

Authorize a new `caplab.capture_resources` module, its tests, and integration
in scripted diagnostic preparation/CLI, runner and retained inspection. Add
this record and a contract. The optional `resource_profile="cgroup-usage/v1"`
is supported only with `codex-scripted-routed/v2`; preparation v5 must bind both
selections. Omitted selection retains current preparation formats and capture
behavior. Preserve native launch identity, requests, routing, runtime/resource
ceilings, source/input pins, quarantine, one-shot consumption and cleanup.

The observer reads a caller-owned non-root domain cgroup at pinned identity.
Retain bounded raw CPU counters, memory.current, memory.peak, cgroup events and
read intervals before launch and after workload stop, before cgroup removal.
Keep counter deltas, lifetime/accounted peak, point observations and elapsed
observation interval distinct. Reads are not an atomic snapshot. Do not reset
counters, move processes, change limits or infer isolated observer overhead.
Kernel errors or unsupported fields propagate; missing observations are not
zero usage. Guard and seal new metadata before reporting it. Retained inspection
must validate schemas, raw/parsed agreement, units, identity, timing and
nondecreasing counters against independent capture anchors.

Authorize fresh synthetic cgroups/processes in owned transient user units under
`/tmp/caplab-resource-observation-*` and test temporary roots. Each test unit is
bounded to 30 seconds, 128 MiB memory, zero swap and 32 tasks; the child may
allocate at most 32 MiB and run at most five seconds. Stop/remove only the owned
unit/cgroups; preserve unrelated runtime and `docs/designs/`. No installed-native
execution, model/provider call, real authentication, spending, historical
custody effect, tracker write, external message, study or scoring is authorized.
Run focused real-cgroup and semantic refusal controls, full checks, then commit
and publish. This implementation authority expires at that verified commit.

## Execution and verification

Implemented the bounded read-only observer, retained interval verification and
the optional v5 preparation path. Scripted inspection requires two independently
hashed files and the observed child identity, then checks that the resource
read intervals enclose process capture. Default preparation and inspection
shapes remain available. The [resource contract](../product/contracts/cgroup-resource-observation-v1.md)
defines the units, accounting boundary, failure behavior and unavailable claims.

The new API and preparation controls first failed because the module and
keyword did not exist. The first real-kernel control then failed on the valid
`core_sched.force_idle_usec` key in `cpu.stat`. Allowing dots in bounded keyed
counter names fixed that refusal; the required usage/user/system counters and
duplicate-key checks remain. Focused checks passed all 18 tests in 2.449 seconds.
They exercise real cgroup accounting, nonzero usage after a failed child,
peak retention after exit, file-hash/identity/timing disagreement, duplicate
JSON keys, raw/parsed disagreement and preparation profile relabeling.

Fresh retained controls in `/tmp/caplab-resource-observation-control` use seven
source pins, kernel `6.8.0-138-generic`, a touched 24 MiB allocation and at least
0.08 seconds of process CPU work. Both owned transient units finished and were
removed; their cgroup directories are absent. The raw results are:

| Child exit | CPU usage delta, microseconds | Accounted peak, bytes | Ending current, bytes |
| --- | ---: | ---: | ---: |
| 0 | 106067 | 29433856 | 4096 |
| 7 | 102427 | 29429760 | 4096 |

These are two synthetic observations, with no performance comparison or
representative-population inference. The resource reader and preparation are
exercised, as is standalone anchored inspection; a complete installed-native
run with the new option has not been performed. The previous attempt remains
unchanged and has no reconstructed resource observations.

## Selection and preservation

Keeping only current/limit snapshots leaves the demonstrated peak-after-exit
gap. Reading a process after exit cannot recover its cgroup lifetime peak.
Adding this option supplies explicit bounded observations while preserving
older preparation identities. A polling profiler or paired overhead experiment
would introduce a different collection protocol and is deferred. This change
does not optimize execution or establish the observer's incremental cost.

The implementation adds one module and no dependency, background service,
thread or persistent scheduler. Its descriptor ownership uses the existing
context-managed capture reader. Counter, decode and filesystem errors propagate;
an incomplete pair stays unavailable. Existing writer stop, routing closure,
fixture join, quarantine and one-shot custody owners remain responsible for
cleanup. Reverting this commit or omitting the new option is the rollback route;
retained v5 records must keep their matching source version.

Per-edit classification: the module and runner/inspection integration add
resource instrumentation; preparation/CLI and their tests add a distinct
prospective selection; contracts and this record state the new behavior and
verification limits. No structural refactoring, dependency migration, historical
custody change or tracker state change is included. CAPLAB-84 remains open for
representative repairs and capture cost, redaction and missingness evaluation.

## Final checks and advisory evidence

`CAPLAB_TEST_WEBSOCKETS_ROOT=/tmp/caplab-native-transport-deps/websockets make check`
exited zero: 1,489 tests ran in 218.373 seconds, with four skips. The complete
output is `/tmp/caplab-resource-observation-full-suite.log`. Scoped Ruff F checks
and `git diff --check` passed; CLI prepare help includes the new resource option.
The full suite ran after the final Python changes. Later edits only documented
the result and retained private verification/advisory artifacts.

The validated Pincite release gate passed with release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
Initial packet `pkt-e390e23e1bf70d52` identified 70 obligations. Five inspected
typed evidence records produced final packet `pkt-6195cbcc1eba53e1`, content
SHA-256 `6195cbcc1eba53e1a2e80e9a9204613bc5f9028e2ccf122c3f89c3e02b8127f4`.

Metric semantics, bounded reads, ownership, missingness and runtime sanity
controls materially constrain this implementation. Causal observer overhead
is still unknown, so the conclusion is limited to collection mechanics and
retained consistency. Nine unmet obligations are individually classified in
`/tmp/caplab-resource-observation-obligations.json`: four broader toolchain/CI
claims, a performance target, cache/warmup control, variance, overhead/data-loss
calibration and representative non-ASCII input. None supports a broader claim
here. The schema-validated decision receipt and citation classifications for
both served packets remain under the same private prefix. No acceptance,
reviewer ranking or study result is recorded.

The verification manifest is `/tmp/caplab-resource-observation-verification.json`,
SHA-256 `8069f7dce44c7b1275bc82cdb8918f732e31b37108a839e74df1a039bbf1fe24`.
It pins 49 private artifacts and nine source/contract files. Readback also
verified all 184 private artifacts of routed native attempt 3 and all 92 private
artifacts of the preceding parent-routed profile implementation against their
original manifests. `docs/designs/` remains outside this change.
