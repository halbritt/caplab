# Restricted capture routing, version 1

`caplab.capture_network_transport.capture_routed_network(plan, *,
expected_policy_sha256, peer_pid, output_dir, timeout_seconds,
quarantine_factory=None)` is a context manager. It installs an anchored
[destination policy](capture-network-policy-v1.md), starts a fixed slirp4netns
helper, yields a readiness observation and checks captured helper termination
when the context exits. It enables no native CLI option and grants no execution
or study authority.

The caller owns endpoint selection/authorization, authenticated peer lifetime,
exclusive use of its fresh network namespace, stable private custody, and the
enclosing workload's deadline. Hold the peer blocked until the context yields.
Keep the context open throughout the workload, then destroy the owned namespace
after helper cleanup. If entry or exit fails, withhold release or stop the owned
workload as appropriate. No policy removal, custody reuse, automatic retry or
provider request occurs in this module.

The plan is rebuilt and its independent hash checked before opening procfs or
creating custody. Peer PID must be a positive integer. The lifetime must be a
finite number greater than zero and at most 300 seconds; booleans are refused.
The output must be a fresh resolved absolute path with caller-owned ancestry.
The namespace descriptors are pinned from the peer's proc directory, and both
must differ from the supervisor's namespaces. Policy installation requires
all five workload capability sets to be zero and no-new-privs set. Its namespace
observations must match the transport's pinned descriptors.

The policy is installed and its full readback verified **before** slirp starts.
The routing helper enters only the pinned user namespace, checks its identity,
selects mapped UID/GID zero, sets no-new-privs and removes capabilities except
SETPCAP, SYS_ADMIN, NET_ADMIN and NET_BIND_SERVICE. Inheritable and ambient sets
are zero. It checks and records this pre-exec state, closes the user descriptor,
then executes the fixed slirp binary. It keeps the supervisor's network
namespace as egress; slirp's TAP setup child enters the descriptor-selected
workload network namespace. No PID-based namespace fallback is used.

This profile requires an inner UID/GID zero mapping. The installed slirp 1.2.1
sandbox's path-mode startup does not use its explicit user-namespace path in
the parent phase; the fixed helper supplies the selected namespace before exec.
The original native diagnostic's nonzero mapping is a different configuration
and remains unchanged. Any future native adoption must freeze that mapping
and the routing configuration as part of its exact Binding.

Fixed slirp options configure `tap0`, enable its sandbox and seccomp, and disable
host-loopback and built-in DNS access. IPv6 and the API socket are not enabled.
The IPv4 network is slirp's default 10.0.2.0/24. The caller supplies a compatible
trusted helper filesystem, including `/dev/net/tun`, `/etc`, `/run` and `/tmp`;
the workload does not need the tun device. Python and slirp bytes are hashed
before and after the operation; helper source and exact argv/environment are
recorded. These hashes identify observed tools, not an independent allowlist
or a complete dependency/Binding inventory.

Each helper capture retains at most 128 KiB of combined stdout/stderr and runs
for at most the selected lifetime. Readiness waits at most five seconds or that
lifetime, whichever is shorter, while checking for early capture completion.
The expected readiness byte is `1`. The yielded
`caplab.capture-routing-readiness/v1` document has `ready_signal_observed: true`,
its observation time, namespace identities, plan and command hashes, and
`study_eligible: false`. `ready.json` is sealed before yield.

Readiness is not continuous liveness, verified route topology, successful
workload execution or proof that a later caller releases the workload. The
helper can fail while the body runs. A caller must not accept the body result
until context exit has checked the terminal capture. The body must have its own
deadline; the context manager does not interrupt arbitrary caller code.

On normal return or an exception, the context closes its exit-pipe writer
(slirp observes HUP), then joins the captured process before closing borrowed
namespace/pipe descriptors. The join allows the selected capture lifetime plus
five seconds. The shared process recorder stops its owned process group at its
deadline; a helper ignoring HUP can therefore delay cleanup until that deadline.
The trusted quarantine factory must itself have bounded execution, as required
by the shared process-capture contract. This is not a hard bound on arbitrary
user-supplied Python code or filesystem stalls.

When a terminal process receipt is available, `terminal.json` records schema
`caplab.capture-routing-terminal/v1`, command/readiness/capture hashes,
`normal_shutdown`, `body_completed`, `tools_agree` and `study_eligible: false`.
`normal_shutdown` requires exit zero and complete streams. A body exception
keeps `body_completed` false and propagates even if the helper exits normally.
An incomplete capture, helper error or tool drift raises on context exit.
Cleanup failure can be chained to an earlier body/entry error; it must be
treated as failure. Startup failure may have a null readiness hash. Quarantine
or storage failure may leave raw prefixes without a terminal receipt; absence
does not mean normal cleanup or zero retained cost.

Fresh custody contains `policy/`, sealed `command.json`, `process/`, and only
the readiness and terminal records actually reached. Plan/command metadata,
pending/final receipt paths and captured streams pass through the caller's
trusted quarantine factory. Return values are newly built caller-owned
documents; their sealed byte hashes identify the originally retained versions.
The mutable input plan is validated and copied before helper work begins.

The standing test runs the actual mount handoff and this context manager in
disconnected outer namespaces. It checks selected TCP traffic, forbidden port
and internal address, readiness/release ordering and normal exit. It also
exercises a missing tun device, an exception after readiness, a real helper
timeout and quarantined command metadata. Original offline policy tests retain
their nonzero UID/GID mapping. These controls do not establish provider
compatibility, hostile namespace escape resistance, full native capture,
representative repair quality or reviewer qualification.
