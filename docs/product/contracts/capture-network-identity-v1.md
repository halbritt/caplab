# Capture network namespace identity, version 1

`open_capture_network_namespaces(peer_pid, profile=...)` is a read-only context
manager in `caplab.capture_network_identity`. Its caller must authenticate the
peer, own the target namespace authority and keep the peer blocked for the
descriptor lease. Access to a PID or namespace does not provide that authority.
The reader opens descriptors and reads kernel metadata; it does not enter a
namespace, install policy, start a routing helper or authorize execution.

The two closed profiles are:

| Profile | Required ownership |
| --- | --- |
| `workload-user/v1` | The network's owning user namespace is the workload's user namespace. |
| `parent-user/v1` | The network owner is the distinct, immediate parent of the workload's user namespace. |

The network owner comes from `NS_GET_USERNS` on the opened network descriptor.
The parent profile compares it with `NS_GET_PARENT` on the opened workload user
descriptor. Device/inode pairs identify the opened namespace objects. The
network, workload user and network-owner user namespaces must differ from their
corresponding supervisor namespaces. A grandparent owner is not admitted as an
immediate parent.

Both profiles require all five workload capability sets to be zero and
`NoNewPrivs=1`. The parent profile additionally requires a single internal
UID/GID 1000 mapping to the observer's current UID/GID, and all four proc status
UID/GID values must equal those observer credentials. Proc mapping coordinates
are those of the observer; they are not labeled as coordinates in the workload's
immediate parent. The reader makes no claim that UID/GID zero is mapped in the
owner namespace or that a particular helper can run there. Those are separate
configuration and execution checks.

The yielded `CaptureNetworkNamespaces` contains `user_fd` for the network owner,
`network_fd` for the peer network, and an owned `observation` snapshot with schema
`caplab.capture-network-identity/v1`. The snapshot records the selected profile,
peer PID, supervisor identities, workload user identity and optional parent,
network and owner identities, mapping observer credentials, UID/GID maps and
capability fields. It always has `study_eligible=false`. It is an observation,
not independent acceptance, continuous liveness or proof of hostile containment.

Descriptors are non-inheritable and borrowed only until context exit. An owned
exit stack closes the proc, workload, network, owner and optional parent
descriptors on normal exit, refusal or caller exception. A helper may receive
the two yielded descriptors only through an explicit caller-owned handoff.
The observation mapping belongs to the caller; changing it cannot change the
opened kernel objects. Guard and anchor it before persisting or using it as
retained verification evidence.

Status reads are bounded to 16,384 bytes and each ID-map read to 4,096 bytes.
Invalid arguments, profiles, relationships, privileges and selected mappings
raise the repository's `CaptureVerificationError` (a `ValueError`). Kernel,
descriptor and ASCII decoding failures propagate; no fallback owner is chosen.
Unsupported kernels or inaccessible namespace ancestry therefore fail closed.

This contract adds no routing-profile or native-launch behavior. Existing routed
capture still uses its selected mapped-root configuration. A later integration
must explicitly bind this ownership profile to preparation, helper execution
and retained inspection. The successful synthetic topology control is not a
completed native capture or representative repair measurement.
