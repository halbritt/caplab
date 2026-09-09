# Basic device profile for nested Bubblewrap

`usable_devices='bwrap-basic-v1'` selects a closed diagnostic profile in
`mount_coverage` and `receive_mount`. Literal `False` retains the default
read-only device topology. Literal `True` retains usable null and urandom and
the existing receipt fields. All other values are invalid; a profile is not an
arbitrary device list. This interface does not authorize native execution.

The named profile requires exactly these six writable devtmpfs device mounts
without `nodev`, in addition to the caller's existing writable tmpfs/procfs
allowances. It preserves all other mount, namespace and resource checks.

| Path | Character device | Live check |
|---|---|---|
| `/dev/null` | 1:3 | Empty read; five-byte write discarded |
| `/dev/zero` | 1:5 | One zero byte read |
| `/dev/full` | 1:7 | One zero byte read; write refused with ENOSPC |
| `/dev/random` | 1:8 | One-byte nonblocking read |
| `/dev/urandom` | 1:9 | One-byte nonblocking read |
| `/dev/tty` | 5:0 | Identity only; no supervisor terminal I/O |

Before checking devices, the supervisor reads the peer's kernel stat record
and requires its controlling-terminal number to be zero. Each device is pinned
by O_PATH with O_NOFOLLOW and checked through fstat before I/O. Non-terminal
I/O reopens the pinned descriptor through `/proc/self/fd`; no unverified device
path is opened for reading or writing. All owned descriptors close on success
and failure. No random byte values are retained. A nonblocking random read
that cannot complete refuses the handoff instead of weakening the check.

The mount observation adds `device_profile: 'bwrap-basic-v1'` and the six
`writable_devices` paths. Handoff `device_access` contains schema
`caplab.basic-device-observation/v1`, the profile, controlling-terminal number,
and ordered device records with major/minor numbers, read counts, zero-read
predicates and write outcomes. It is covered by the existing quarantine gate.
`verify_basic_devices` requires exact fields, values and scalar types;
`inspect_custody` validates it alongside the recorded mount profile. Missing or
contradictory observations refuse verification. This is recorded consistency
and byte custody, not a reconstruction of live devices after exit.

The profile supplies the standard devices required by Bubblewrap `--dev`.
It exposes no host PTY tree, terminal session, block device or whole host /dev.
It does not prove successful native work, complete native capture, production
capacity or study eligibility. The fixed device identities are Linux-specific.

Source: [Bubblewrap 0.9.0 device setup](https://github.com/containers/bubblewrap/blob/v0.9.0/bubblewrap.c#L1202).
