# Frozen native child observation v1

`caplab.native_child_process.observe_frozen_native_child(cgroup_path, *, evidence)`
observes exactly one matching direct child in a frozen, owned leaf cgroup.
`FrozenNativeChildEvidence` contains `parent_pid`, `parent_proc_descriptor`,
`expected_executable`, `expected_executable_sha256`, `max_executable_bytes`, and
`max_processes`.

The caller authenticates the paused parent, opens its actual `/proc/<pid>`
directory before release, and keeps that borrowed descriptor open through this
call. An open proc directory remains associated with that process incarnation;
it does not redirect to a new process reusing the PID. The reader also compares
its device/inode with the current kernel directory. See the
[kernel procfs contract](https://www.kernel.org/doc/html/latest/filesystems/proc.html).

The caller owns the cgroup, source quiescence, freeze/thaw transitions and absence
of external migrations, fatal signals or namespace changes. The supervisor must
remain outside the workload group. This is not an atomic snapshot against a
hostile cgroup administrator. The reader performs no writes, process control,
sleep, retry, publication or evidence admission. Owned file descriptors close
on every exit; the parent descriptor remains borrowed and open.

## Required kernel and file evidence

The cgroup path must be resolved and strictly beneath `/sys/fs/cgroup`. The
reader requires `cgroup.type=domain`, `cgroup.events` reporting `frozen=1`, and
`cgroup.stat` reporting zero descendants. Merely requesting a freeze is
insufficient; external migration and fatal signals remain possible even after
freezing. See the [cgroup v2 contract](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html).

The reader enumerates `cgroup.procs` with unique positive process IDs and the
supplied process allowance. The authenticated parent must be present, the
supervisor absent. Every enumerated candidate must be a process leader and
report the exact selected unified cgroup membership through kernel procfs.
It selects exactly one process with `PPid` equal to the authenticated parent
whose `/proc/<pid>/exe` matches the selected host file's stable identity.
Zero or multiple matches refuse; a matching grandchild is not a direct child.

The selected executable must be a resolved regular file. Its bytes are hashed
against the independent supplied SHA-256 using the existing stable file reader.
The source descriptor stays open throughout observation. Matching uses device,
inode and the remaining stable metadata in the shared `_identity` contract,
not pathname spelling or just equal file contents. An identical copy on another
inode cannot stand in for the selected executable object. The `/proc/.../exe`
magic link is intentionally followed; other descriptor opens use no-follow.

The frozen population, leaf/domain state, parent and child membership, selected
executable and source/cgroup identities are checked again before returning.
There is no fallback to a partial task-children list. That interface can omit
live children when other children exit, as documented in
[proc_tid_children(5)](https://man7.org/linux/man-pages/man5/proc_tid_children.5.html).

## Bounds, errors and result

The executable allowance is a positive integer of at most 1 GiB, read in bounded
chunks without accumulating binary contents. The process allowance is an integer
from 1 through 128. Each kernel pseudo-file read is limited to 65,536 bytes.
Parent PID and descriptor reject booleans and invalid numeric ranges. Existing
hash validation applies. Invalid evidence/predicates raise `ValueError`
(normally `CaptureVerificationError`); filesystem errors propagate as `OSError`
subclasses. Unsupported or disappearing kernel objects never produce success.
There is no wall-time guarantee for kernel/filesystem operations.

`caplab.frozen-native-child-observation/v1` contains parent/child PIDs and proc
directory identities, child Pid/Tgid/PPid, cgroup identity and observed process
population, selected executable path/bytes/hash/device/inode, and the observation's
monotonic start/end times in nanoseconds. Those timestamps bracket this read;
they do not measure the full freeze interval or representative capture overhead.
The record contains no command line, environment, credentials or trace text.

`live_child_executable_observed` is true. Continuous image residence, trace
linkage, task success, Binding completeness and study eligibility remain false;
native capture completeness remains null. This observation identifies the image
seen during the frozen interval, not every image the PID executed. It does not
authenticate its own retained JSON bytes. The caller must independently seal
and anchor the observation before using its PID with the
[child execution linker](native-child-execution-v1.md) and a separately prepared
command/environment. No historical child can be observed after it has exited.

Public native startup does not yet use this observer. Adoption must explicitly
select and record the pause, preserve source and observation custody, and measure
its effects on native execution and capture before claiming representative results.
