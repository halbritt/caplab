# Opt-in nested-user-namespace procfs capture

The diagnostic mount handoff supports `nested_userns=True` for native sandboxes
that must write their own UID/GID maps and mount procfs in a nested PID namespace.
The flag is an explicit boolean. Existing callers retain read-only procfs and
unchanged receipt fields. This option does not select a study Binding or authorize
a native launch.

## Mount and release requirements

`mount_coverage` permits `/proc` as one additional writable mount only in this
mode. It must be procfs with `nosuid,nodev,noexec`, without covered subpaths.
The five existing writable roots remain bounded tmpfs; usable device exceptions
remain `/dev/null` and `/dev/urandom`. All other existing read-only and unexpected
mount checks remain in force. Procfs is a live kernel interface, not a sixth
retained artifact root.

Before `receive_mount` releases its paused peer, the supervisor reads the peer's
kernel namespace links and status. Its PID, user, mount and network namespaces
must differ from the supervisor's, and `/proc/1/ns/pid` as viewed through the
peer's root must name the peer's PID namespace. Effective, permitted, inheritable
and ambient capabilities must all be zero; `NoNewPrivs` must be 1. Missing,
unreadable or contradictory evidence prevents release and final handoff
publication through the existing cleanup path.

The handoff adds `mount_coverage.writable_procfs: ["/proc"]` and a
`nested_procfs` observation with schema `caplab.nested-procfs/v1`, the paired
namespace identities, procfs PID-1 namespace and privilege status. Quarantine
checks cover these fields before publication. `inspect_custody` recomputes the
mount constraints and validates these recorded predicates. This verifies the
record's consistency and custody; it does not recreate a live namespace after
exit or prove future runtime safety.

## Protection and limits

This mode relies on user/PID namespace isolation, Linux permissions, dropped
capabilities and NoNewPrivs. It does not claim read-only kernel-control mounts.
Self controls such as UID/GID maps remain usable. `ns_last_pid` refers to the
calling task's current PID namespace. The checked synthetic control denied
write-open for 1,213 other enumerated kernel-control files and never wrote a
kernel-control value. That observation is bounded to its kernel and environment.

Read-only submounts covering nonempty procfs directories can prevent a nested
procfs mount under Linux's user-namespace mount restrictions. Disabling the native
sandbox to avoid that restriction would change the evaluation subject and is not
part of this interface.

Mountinfo and namespace observations are required together. Topology parsing
alone does not prove PID isolation. A zero process return code, a successful
handoff or passing custody checks does not prove successful native task execution.
Resource limits, full-mount retention, process cleanup and native success criteria
remain caller-owned contracts.

Sources: [Linux procfs mount restrictions](https://www.kernel.org/doc/html/latest/filesystems/proc.html#mount-restrictions),
[ns_last_pid](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html#ns-last-pid),
and [Bubblewrap 0.9.0 procfs setup](https://github.com/containers/bubblewrap/blob/v0.9.0/bubblewrap.c).
