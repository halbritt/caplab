# Parent-owned capture routing, version 1

The explicit `namespace_profile="parent-user/v1"` option on
`install_capture_network_policy` and `capture_routed_network` routes a non-root
workload through its network's owning parent user namespace. It addresses the
synthetic case where mapped-root execution prevents a nested sandbox from
writing its UID map, while the installed routing helper requires mapped root.
The caller must select this profile before collection. Neither a successful
topology control nor this API option changes a native launch profile.

The default `workload-user/v1` preserves the existing
[policy](capture-network-policy-v1.md),
[transport](capture-network-transport-v1.md) and
[inspection](capture-network-verification-v1.md) v1 formats and behavior. Its
historical collection path does not acquire the new kernel ownership lease.
Unsupported profile values are refused before peer access or custody creation.

## Collection and caller responsibilities

The caller owns authorization for fresh namespaces, authenticated peer identity,
its blocked lifetime, stable private custody and the enclosing deadline. Keep
the peer blocked until routing readiness, and stop the workload before closing
the routing context. A failure requires withholding release or stopping the
owned workload and preserving partial custody. No automatic retry is provided.

For the parent profile, policy installation and transport each acquire the
[kernel ownership lease](capture-network-identity-v1.md). The network owner must
be the distinct immediate parent of the workload user namespace. Neither user
namespace nor the network may overlap the supervisor's corresponding namespace.
The workload must have all five capability sets zero and `NoNewPrivs=1`, with
internal UID/GID 1000 mapped singly to the observer's UID/GID. All four observed
proc status UID/GID values must agree with that mapping. The policy observation
must equal the transport observation before routing starts.

Both helpers receive the checked network owner's user descriptor and the
workload network descriptor. Helper source, arguments, executable observations,
capability restrictions, destination rules, readback, stream limits, readiness
and shutdown criteria retain the existing contracts. The routing helper still
requires UID/GID zero in the owner namespace; the workload's mapping does not
establish that helper precondition. A caller must supply a compatible owner and
helper filesystem. Setup privileges used to create the topology are separate
from the zero-capability workload state required at handoff.

## Retained records

Parent collection emits these closed formats:

| Artifact | Schema or additional fields |
| --- | --- |
| `policy/preflight.json` | `caplab.capture-network-preflight/v2`; v1 fields plus `namespace_profile`, full `network_identity` and `workload_credentials`. |
| `policy/installation.json` | `caplab.capture-network-installation/v2`; the same additions to the v1 installation fields. |
| `identity.json` | `caplab.capture-network-identity/v1`; identical to the linked policy snapshot. |
| `command.json` | Existing exact command fields plus `namespace_profile` and `network_identity_sha256`. |
| `ready.json` | `caplab.capture-routing-readiness/v2`; v1 fields plus that profile and identity hash. |
| `terminal.json` | `caplab.capture-routing-terminal/v2`; v1 fields plus that profile and identity hash. |

`workload_credentials` has exactly `uid` and `gid`, each a list of four decimal
strings observed from proc status. The identity snapshot's mapping coordinates
are those of its recorded observer. The original identity schema does not
contain these raw credential fields, so policy retains them separately. The
identity file is guarded and sealed after successful policy installation and
before helper launch. Each later routing record links its byte hash. Existing
command, policy, readiness, process and terminal hashes remain required.

All newly retained metadata passes the existing quarantine boundary. An error
may leave only the records reached; absent readiness or terminal custody is
not evidence of successful execution or zero cost. Descriptor ownership and
helper cleanup cover normal return, refusal, body exception and timeout.

## Independent inspection

Call `verify_capture_routing(...,
expected_namespace_profile="parent-user/v1")` with the existing independent
policy, readiness, terminal and authenticated peer anchors. The CLI equivalent
is `scripts/inspect_capture_routing.py --namespace-profile parent-user/v1`
with all existing required options. Default inspection refuses parent records;
parent inspection refuses legacy records. The inspector does not infer profile
selection from captured data.

`verify_network_identity_observation(observation, expected_profile=...,
expected_peer_pid=...)` checks the exact retained identity schema, namespace
relationships, strict integer IDs and mapping ranges, observer credentials,
capabilities and `study_eligible=false`. It returns an owned copy or raises
`ValueError`. It performs no kernel reads or namespace operations. The parent
routing inspector additionally checks credential status, all snapshot copies,
policy namespace agreement and identity hashes through command, readiness and
terminal records. Existing command, policy/readback, captured stream and
lifecycle checks still apply. A successful report uses
`caplab.capture-routing-inspection/v2` and includes the selected profile,
identity hash and snapshot alongside the v1 report fields.

Rehashing a contradictory owner, parent, mapping, privilege or credential record
does not make it valid. Consistent retained records are still not independent
proof that their kernel observations occurred. Trusted collection, independent
anchors and peer lifetime remain essential. Inspection is read-only and bounded
by the existing custody reader; it does not certify continuous containment,
provider compatibility, native execution, representative repairs or reviewer
capability. Both study eligibility and native containment verification remain
false in the report.
