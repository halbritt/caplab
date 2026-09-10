# Cgroup resource observations, version 1

The scripted native diagnostic accepts `--resource-profile cgroup-usage/v1`
with `--launch-profile codex-scripted-routed/v2`. This creates preparation v5,
which binds both selections. Omission retains the existing preparation and
capture behavior. Preparation grants no execution authority.

`caplab.capture_resources.read_cgroup_resources()` reads the caller-owned,
non-root domain cgroup before process capture and after workload shutdown,
before removal. The runner guards and seals `safe-resource-before.json` and
`safe-resource-after.json`. Each observation retains the cgroup path, device
and inode, kernel release, monotonic start and finish, bounded raw fields and
their parsed values. Required files are `cgroup.type`, `cpu.stat`,
`memory.current`, `memory.peak` and `cgroup.events`; each read is limited to
16,384 bytes. The reader closes its descriptors and performs no writes.

The selected [Linux cgroup v2 counters](https://docs.kernel.org/admin-guide/cgroup-v2.html)
have these meanings in the report:

| Field | Meaning and boundary |
| --- | --- |
| `cpu_delta_usec` | Differences in cumulative usage, user and system CPU time, in microseconds, for the selected cgroup and descendants. |
| `accounted_memory_peak_bytes` | Ending accounted lifetime peak for the cgroup and descendants, in bytes. This is neither peak subtraction nor native-process RSS. |
| Before and after memory current | Separate point observations in bytes; ending current usage can fall after a process exits while its peak remains. |
| `observation_interval_ns` | Minimum and maximum elapsed time between points within the two sequential read intervals. This is not CPU time or incremental capture overhead. |

The caller must preserve cgroup identity and lifetime in one running kernel,
and exclude outside migrations, deletion/replacement and counter resets. Reads
are sequential, not atomic. They do not establish equality between total CPU
and separately read components, or an instantaneous relationship between
memory current and peak. Helpers and other charges in the selected cgroup are
included; parent supervisor, fixture and routing costs outside it are excluded.
The observer itself runs outside the measured child cgroup.

`verify_cgroup_resource_interval()` requires an independently supplied cgroup
identity, exact observation schemas, raw/parsed agreement, matching kernel
release, ordered intervals and nondecreasing CPU counters and memory peak.
It reports retained consistency; it does not authenticate kernel origin.
Scripted inspection additionally verifies the two file hashes from its already
verified capture manifest, matches the observed child identity, and requires
the observations to enclose the captured process interval.

Unsupported or unreadable required fields stop observation. Missing evidence
is never zero usage. A process exit failure can still have usable resource
observations. Earlier setup, read or quarantine failures can leave an incomplete
pair, which cannot produce a verified interval. Standalone resource inspection
does not require process success; full native inspection retains its existing
completion criteria.

These records set `study_eligible` and `native_process_only_usage` to false and
`incremental_capture_overhead_seconds` to null. Synthetic successful and failed
process controls verify accounting mechanics. They do not measure representative
repair cost, observer overhead or reviewer capability. The optional profile
requires a fresh prospective preparation and authorization before an installed
native attempt; historical attempts receive no reconstructed observations.
