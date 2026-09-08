# Observe enforced resource limits in a delegated probe

Date: 2026-09-08. Baseline: `33e82a5`. Primary-agent authorization under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `scripts/probe_cgroup_resource_limits.py` and this record. Implement a fixed,
model-free substrate diagnostic, not a native launcher. It may create at most
three uniquely named `caplab-resource-probe-<uuid>.service` transient user units
during development/verification, sequentially. Each unit must have a 128-MiB
memory limit, zero swap allowance, 64-task limit and 30-second runtime limit.
Use only the user manager, never sudo or a system unit. Retain bounded stdout,
stderr, commands, kernel counter snapshots and reports in fresh private roots
under `/tmp/caplab-resource-probe-*`.

Within each unit, create only its own delegated supervisor and fixture cgroups.
Enable memory and pids controllers only in that delegated unit. Move only its
own supervisor and newly created fixture processes. Set per-fixture memory to
32 MiB, swap to zero, group OOM handling to one and tasks to at most 16. Run
fixed trusted Bubblewrap fixtures: ordinary success; at most 64 one-MiB writes
to a private tmpfs; and at most 32 attempts to spawn short-lived children with
an eight-task limit. No host path is writable from the fixture namespace.
Record independent kernel counters before and after; do not infer complete
capture from a zero exit or absence of a particular counter.

Terminate and remove only owned fixture cgroups and exact generated unit names.
Retain all reports and partial/error output. If delegation, controller files or
unit properties are unavailable, stop that probe and report the limitation;
never run a fixture without its checked limits. Bound each fixture to ten
seconds and combined streams to 200,000 bytes. Bound outer service capture to
40 seconds and 200,000 bytes. Inspect official kernel and installed systemd
documentation, run focused checks and the repository suite, consolidate advisory
evidence, clean exact named advisory scratch and commit locally. Authorization
expires at commit.

Preserve unrelated services, cgroups, timers, processes, runtime/capture owners,
tests, development worlds, historical evidence, `docs/designs/` and worktrees.
No native harness/model calls, credentials, study admission, campaign budget,
ranking, placement, tracker mutation, external message or push. This diagnostic
does not select a production resource policy or establish capture completeness.
Stop before any required broader effect or unsupported guarantee.

## Intended verification

The control should terminate normally without new memory-OOM or task-limit
events. A tmpfs writer should encounter the fixture's cgroup memory bound while
the supervisor survives and retains the kernel observations. A process-limit
fixture should be able to catch fork failure and exit zero while the independent
`pids.events` counter still records the limit. All owned fixture cgroups must be
empty before removal and the transient unit must be gone after cleanup.

These checks test resource enforcement and observation. They do not turn cgroup
memory into a logical-file quota, detect every filesystem error, retain tmpfs
artifacts after OOM, or validate a native Binding. The prior storage findings
remain in force.

## Implementation

The script accepts a fresh absolute output root and creates one UUID-named user
service. The service manager places the supervisor in its own subgroup using
`DelegateSubgroup=supervisor`; installed systemd 255 documents that facility.
The supervisor verifies its membership and the enclosing memory, swap and task
limits before configuring sibling fixture groups. All direct cgroup mutations
are under that generated delegated service. No sibling unit is selected.

Each fixture group is fresh, configured and read back before launch. A trusted
helper joins its own process to that group before executing Bubblewrap. The
supervisor stays outside the fixture group and retains kernel observations in
host custody that is not mounted in the fixture namespace. `OOMPolicy=continue`
lets the supervisor observe a fixture-group OOM; `memory.oom.group=1` applies
inside the fixture group. The service retains its separate outer resource and
runtime ceilings. The code never runs an arbitrary caller-supplied command.

The script retains before/after raw `memory.events`, `pids.events` and
`cgroup.events`, plus limits and current usage. It distinguishes natural
quiescence from cleanup, kills only residual processes in its own fixture group,
and requires the group to be empty before removal. The outer owner stops only
the exact generated service if needed and verifies that the unit and cgroup are
gone. A failed check leaves prior intents, streams and observations intact.
Missing delegation or a differing limit refuses the fixture launch.

The memory controller records boundary and OOM events independently of the
process's text output; the pids controller records task-limit events. Those
counters have different meanings. A memory `max` increment can involve reclaim
and is not itself proof of a failed write; an OOM count is not a logical-byte
count. The probe retains raw keys rather than turning these counters into a
capability score. [Linux cgroup v2 documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)

## Observed run

The authorized invocation was:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 scripts/probe_cgroup_resource_limits.py \
  --output-root /tmp/caplab-resource-probe-first
```

It ran on Linux `6.8.0-138-generic`, systemd `255.4-1ubuntu8.17` and Python
`3.12.3`. The script and executable identities are retained in the verification
manifest. Unit:
`caplab-resource-probe-6b237d711248403bb57ef6831bfcc546.service`.

| Fixture | Process outcome | Independent retained event delta |
| --- | --- | --- |
| Control | Exit 0; complete streams; no remaining fixture processes | Memory OOM and pids max both zero |
| Tmpfs memory pressure | Signal 9; supervisor survives; no remaining fixture processes | `memory.events`: max 20, oom 1, oom_kill 4, oom_group_kill 1 |
| Caught task-limit failure | Fixture catches errno 11 after five children, cleans them up, then exits 0 | `pids.events`: max 2 |

The task-limit counter is not a one-to-one count of the script's caught
exceptions. The observation is that the independent counter remains positive
despite successful process exit and cleanup. Likewise, memory usage had fallen
to 204,800 bytes after the OOM, but its event counters remained available before
group removal. This avoids the prior probe's reliance on final free space.

All three expectation checks passed. The three fixture cgroups were empty
before cleanup and removed afterward. The transient service was already
collected when the exact-name stop ran (exit 5, unit not loaded); the independent
state read returned `not-found`, and its cgroup path was absent. The script
treats the verified absence as cleanup success and retains both command results.
This first run consumed one of the three authorized development units.

Raw capture, commands, snapshots and cleanup evidence remain under
`/tmp/caplab-resource-probe-first/`, with console output at
`/tmp/caplab-resource-probe-first.log`. No tmpfs task payload was copied as study
evidence, and no native agent was involved.

## Scope of the result

This supplies a reusable local substrate probe and a concrete mechanism for
observing the exercised resource failures outside the failing process. It does
not implement a native capture runner or turn resource-limit events into an
automated study disposition. The script's fixture ceilings are diagnostic
parameters, not measured native resource requirements or an execution budget.

Cgroup memory includes process and filesystem memory accounting; it is not a
logical-file, inode or disk-space quota. The probe does not establish that every
allocation failure produces one of these events, that all storage paths are
covered, or that sparse files are bounded. It does not preserve runtime artifacts
after namespace destruction, authenticate native identity, or prove complete
capture from absent counters. Those remaining storage/custody requirements need
integration under a separately frozen launcher configuration.

The supervisor, fixture, system runtime and same-user parent directories are
trusted for this diagnostic. This is not adversarial qualification against a
host actor that can replace those sources or alter delegated limits. Group
membership before exec also does not establish that all earlier process memory
was charged to the fixture. Keep the captured configuration and observation
scope explicit when using the result for later design.

## Final checks

The repository suite passed **1,163 tests, four skipped, 160.856 seconds**.
Its log is `/tmp/caplab-resource-probe-make-check.log`. Review then tightened
the probe's expectation check to require complete, exited process capture for
all three fixtures. This affects the new standalone diagnostic, not a path
exercised by the repository suite. The final script was verified directly by a
second complete execution under `/tmp/caplab-resource-probe-final/`, unit
`caplab-resource-probe-a6647959e0de457ba2bac04828afce4e.service`. Its memory event
deltas were max 18, oom 1, oom_kill 4 and oom_group_kill 1; its pids max delta
was 2. All three final expectations and cleanup checks passed. Two authorized
units were used; neither remains active.

Six deliberately invalid report variants were rejected: incomplete streams
for each fixture, missing OOM-kill evidence, missing pids-limit evidence and
residual processes. The first offline report-check invocation lacked
`PYTHONPATH=src` and failed on import before running a check. The corrected
invocation followed CAPLAB's Makefile environment. The consulted environment
skill is scoped to another repository; it did not override CAPLAB's runner.
The one bytecode file created by that failed import was removed by exact path.
`/tmp/caplab-resource-probe-focused.json` retains the checked cases.

The final script hash matches the second run's sealed intent. The six protected
capture/source/record files remain byte-identical to `33e82a5`. Raw observations
from the first run are preserved with their original script hash, not relabeled
as final-script execution. No standing test or existing runtime owner changed.

## Advisory disposition and closure

The validated Pincite retrieval-state gate passed for release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet:
`pkt-7199658e0567b6b3`, content SHA-256
`7199658e0567b6b3bd319bff8f17e38b2cd00abc8d79545c3a6328f6d4f34d3d`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`.

Applied repository-contract precedence to the no-native-execution boundary,
evidence before intervention to the independent kernel observations,
structured cleanup to exact owned cgroups/units, and the no-change option to
preserving existing native runtime owners. Four concept citations are retained
in the consolidated classification receipt. Doctrine supplies engineering
guidance, not kernel facts or CAPLAB product authority.

Ten unmet obligations remain nonmaterial:

| Concept | Unmet requirements | Scope reason |
| --- | --- | --- |
| architecture-interaction-synchrony | latency and availability budget; load shape and capacity mismatch | No production response, load or availability design is chosen; the fixed local diagnostic has explicit bounded deadlines. |
| implementation-repository-language-conformance | CI and build matrix; formatter and static-tool configuration | No toolchain change or cross-platform claim; actual local execution and the existing suite supply the stated checks. |
| python-repository-shaped-idiom | Python and dependency version matrix; formatter linter and type-checker configuration | No dependency, formatter or supported-version matrix is changed. |
| python-runtime-static-boundary | annotation maintenance cost; checker and trust-boundary evidence; configured checker and Python version | No checker or annotation policy is selected; fixed trusted inputs and explicit runtime checks define this probe boundary. |
| python-text-bytes-boundary | representative non-ASCII data | The diagnostic uses ASCII kernel counters and fixed fixture text; it changes no native text decoding or normalization. |

`/tmp/caplab-resource-probe-verification.json` consolidates source identities,
both retained runs, final focused checks, the suite log, typed evidence,
citation classification and exact scratch cleanup. The first executed script
is retained at `/tmp/caplab-resource-probe-first-script-source.py`: reversing
only the final two-line guard addition reproduces its original sealed script
hash. Its reconstruction method remains explicit; it is not relabeled as a
new execution.

Eleven named advisory scratch files are removed after consolidation. Source
snapshots, both process-capture trees, all logs and reports remain. The final
local commit contains only the new diagnostic script and this record. No unit
or cgroup is left running, no roadmap item is closed, and no independent
acceptance is claimed. Authorization expires at commit; the CAPLAB goal remains
active.
