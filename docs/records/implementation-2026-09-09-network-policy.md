# Install a frozen destination policy before capture release

Baseline `ef44a81`. Under ADR 0026, the primary agent selects a CAPLAB-owned
destination-policy installer, exercised through `receive_mount`'s existing
authenticated peer callback. That callback runs after owner, cgroup and mount
checks and before the starting inventory is sealed or the child acknowledged.
The existing offline native profile remains unchanged. This is one required
part of the prospective routed profile, not completed provider integration.

Authorize `src/caplab/capture_network_policy.py`, a matching contract, focused
tests and isolated fixture helpers, this record and private verification under
`/tmp/caplab-network-policy-*`. The configuration names at most 64 exact IPv4
unicast/TCP address-port pairs, with a content hash and no execution authority.
Reject hostnames, CIDRs, malformed addresses/ports and unknown fields. Canonical
ordering must not change identity; duplicate endpoints must be refused. The
caller selects and authorizes endpoints; this module cannot identify providers
or establish that a globally routable address belongs to one.

The installer must validate configuration before opening the peer or creating
custody. Pin the authenticated peer's user and network namespace descriptors,
require both to differ from the supervisor, and require zero workload
capabilities and no-new-privs. Enter only those pinned namespaces using bounded
captured commands. Require an empty initial nft ruleset, install a fixed inet
output chain with default drop and exact destination rules, and verify the
entire resulting ruleset before returning evidence to the handoff. Do not add
an unrestricted established-connection exception: earlier sockets must not
bypass destination restrictions. No DNS lookup, route or interface attachment.
Record binary/configuration hashes, namespace identity and all command receipts.
Never flush an existing table or retry into existing custody after failure.

Tests may create fresh Bubblewrap user/network namespaces with fixed local
Python producers and synthetic loopback listeners. They may configure loopback
inside their own namespace before dropping all capabilities. A pair of allowed
ports supports the synthetic local request and reply directions; a third port
is forbidden. Exercise actual nft enforcement and withheld release on failure
through the shared handoff. Bound each fixture to 15 seconds and command
captures to five seconds/128 KiB. Use only owned sockets, descriptors and
processes; capture timeout terminates owned process groups. Namespace teardown
removes its rules. No host networking/firewall changes, external connection,
native/model call, credentials, spend, historical evidence effect, tracker
write, message, push or independent acceptance. Preserve `docs/designs/`.

Run focused tests and the required full suite, review failure propagation and
source/receipt claims, and commit locally. Stop on unexpected host effects,
namespace ambiguity, failure to withhold release, or unexplained regressions.
The authorization expires at the verified commit. Later transport attachment,
resolver selection, IPv6 and native/provider integration need their own checks.

The first real handoff reached namespace entry but nft returned EPERM. The
existing non-root UID mapping loses effective/permitted capabilities across
exec without an ambient capability. Preserve that workload mapping. Authorize
a fixed Python 3.12 helper to enter only the pinned user/network namespaces,
reduce all capability sets to CAP_NET_ADMIN, set no-new-privs, record its
pre-exec state, close namespace descriptors and execute the fixed nft binary.
It runs as a separate bounded capture; the workload retains zero capabilities.
The Linux [setns](https://man7.org/linux/man-pages/man2/setns.2.html) and
[capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html) manuals
describe the relevant namespace and exec transitions. Retain the failed
nsenter diagnostic under the private prefix. No UID/GID mapping, executable
attribute or host privilege is changed.

## Implementation and observations

The [versioned contract](../product/contracts/capture-network-policy-v1.md)
defines three public operations: build the exact destination selection, compare
a complete ruleset, and install it in an authenticated blocked peer. The
installer owns namespace descriptors, bounded helper captures and fresh output;
the caller owns endpoint authority, peer lifetime and exclusive namespace use.
This is a new feature. Existing native entrypoints and the offline capture
profile are unchanged. No-change would leave the tested filtering mechanism
outside CAPLAB's capture handoff; copying the private probe into each caller
would duplicate command, privilege and readback policy. Select one module at
the existing callback, without a new transport abstraction or CLI option.

The initial nsenter attempt failed with nft EPERM. Its raw command capture,
policy and preflight binary hashes remain in
`/tmp/caplab-network-policy-install-diagnostic`; that early capture did not
record complete command intent, so it is not an immutable snapshot of the
original implementation. The fixed helper then passed with the original
non-root UID mapping. Commands now have separate sealed argv/environment and
borrowed-descriptor records, whose byte hashes are returned with capture hashes.

The first quarantine refusal test exposed an unchecked temporary policy path.
The installer now checks both pending and final receipt paths before writing.
The corrected integration exercises actual kernel filtering: both local ports
reply before installation; afterward the selected port still replies while
new and already-open forbidden connections time out. The producer prints a
release marker immediately after acknowledgment, independently of those later
traffic checks. Existing nft policy, quarantined pending policy path and a
peer retaining privileges each prevent that marker and final installation
receipt. Privileged-peer refusal occurs before custody creation. Six mutations
of actual readback cover changed defaults, extra table, missing rule, extra
accept, malformed counter and wrong destination port.

Final focused log `/tmp/caplab-network-policy-focused-final-source.log` reports
five tests passing in 2.070 seconds. The preceding full suite passed 1,455 tests
with four skips in 178.137 seconds, but its run preceded the final release-marker
and command-custody edits. It is retained as an intermediate check, not the
final-source verification gate.

The final-source `make check`, with the existing retained WebSocket test
dependency selected by `CAPLAB_TEST_WEBSOCKETS_ROOT`, exited zero: 1,455 tests,
four skips, 175.144 seconds. Log:
`/tmp/caplab-network-policy-make-check-final.log`. Runtime and test hashes in
`/tmp/caplab-network-policy-final-source.sha256` still match after completion.
The installed environment was Python 3.12.3, nftables 1.0.9 and Bubblewrap 0.9.0;
`pyproject.toml` requires Python >=3.12. No other platform was exercised.

A separate retained final-source handoff under
`/tmp/caplab-network-policy-private-final` exited zero with complete streams.
Its `verification.json` checks all four process receipts against stream byte
lengths and hashes, command/receipt hashes against the installation record,
and runtime/test source identity before and after. The supervisor's user,
network, mount and PID namespace identities and descriptor population remained
equal. The parent did not join the helper's namespaces. This verifies the
observed local fixture and its retained links, not the absence of every possible
host effect or an independent hostile-workload containment verdict.

## Advisory review and remaining evidence

The Pincite retrieval gate passed at release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-4cdaa8e37c13062b` and two evidence passes
`pkt-a655446bd11419c1` and `pkt-c61884e539e15fb7` were inspected. The final
packet's content hash is
`c61884e539e15fb708fc26e16fe3c3fd00fd778410d1cc1833c58c974baa4b03`, with corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9` and
retriever `retriever-ec995ecdd083b2c8`. Six typed evidence records retain exact
authority, contract, source, tests, runtime and environment observations.

Applied concepts are authority-bounded action, repository-contract precedence,
structured cleanup, evidence before intervention, local reasoning and behavior
preservation. Their source locators remain in each packet's provenance links;
all six structured citations classify as valid for each of the three packets.
The decision receipt and all 20 unmet obligations, each classified nonmaterial
with its rationale, remain under `/tmp/caplab-network-policy-`. Thirteen concern
performance objectives, representative populations, metrics and overhead; four
concern CI, tooling or version matrices; one concerns representative non-ASCII
data; two concern a measured no-change assessment. This feature makes no such
claims. Its scope is the installed environment, a closed address/port format,
actual local enforcement and release refusal. Native/provider integration,
representative repairs and their capture costs remain material future work.

For the module-size conflict, keep the privilege and policy lifecycle together
behind one installer; the pure builder and readback comparison expose separately
useful operations. Reuse the existing handoff and process recorder. No adjacent
refactor or performance specialization is selected. Namespace/custody ownership
and refusal ordering are fixed now; routing and native integration remain
separate behavior changes with their own controls.

Test Guard checked actual infrastructure, independent traffic outcomes and the
immediate acknowledgment marker. AI Failure Modes review checked propagated
exceptions, real helper execution, bounded external inputs and owned resource
cleanup. Docs Guard compared public signatures, receipt fields, limits and
failure behavior with source and retained results. No fallback reports an
installation after a failed command or mismatched readback.

The final local Markdown-link check, Ruff F check, format check and source-pin
recheck passed. `/tmp/caplab-network-policy-verification.json` inventories the
retained private artifacts and four final implementation files. The current
source snapshot is separate from the failed early helper diagnostic; no later
source is attributed to that earlier execution. Packets, typed evidence,
classifications and raw failures are preserved as private provenance. The
receipt's two local evidence locators are classified as foreign to the doctrine
packet, separately from its six valid doctrine concept citations.

The local commit expires this scoped authorization. It does not enable a
routed native profile, register study evidence, produce a model-generated
repair, qualify a reviewer, change Plane, or constitute independent acceptance.
