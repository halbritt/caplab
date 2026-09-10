# Exact capture destination policy, version 1

`caplab.capture_network_policy.build_capture_network_policy(destinations)`
returns a prospective `caplab.capture-network-policy/v1` document. Each of
1–64 destination entries contains exactly `address` and `port`: a canonical
IPv4 literal and an integer TCP port from 1 through 65535. Hostnames, CIDRs,
IPv6, unspecified/multicast addresses, the limited broadcast address, duplicate
pairs, extra fields and boolean/nonnumeric ports are refused. The builder sorts
by address text and port, copies the entries and hashes all other result fields
as canonical JSON in `network_policy_sha256`. Input order does not affect it.

The closed profile is `exact-ipv4-tcp/v1`. Its `execution_authorized` and
`study_eligible` fields are false. Endpoint selection and authorization belong
to the caller. Private and loopback addresses can be explicitly selected for
isolated fixtures; this is not a public-provider address classifier. The policy
does not resolve names or attest ownership of any address.

`install_capture_network_policy(plan, *, expected_policy_sha256, peer_pid,
output_dir, quarantine_factory=None)` validates and rebuilds that exact
configuration before opening the peer or creating output. Extra fields,
modified profile/flags, and mismatched independent hashes fail. `output_dir`
must be a fresh resolved absolute path with caller-owned stable private ancestry.
The caller must authenticate the peer and hold it blocked for the entire call.
It owns the peer's namespaces and must exclude other policy writers; merely
having access to a namespace does not establish that ownership.

The installer opens the peer's proc directory and pins its user and network
namespace descriptors. Both must differ from the supervisor's namespaces.
All five workload capability sets must be zero and no-new-privs must be set.
The fixed Python 3.12 helper enters those descriptor-selected namespaces,
checks their identities, reduces its capabilities to CAP_NET_ADMIN, sets
no-new-privs, reports its state, closes the namespace descriptors and execs
the fixed nft binary. It preserves the workload's UID/GID mapping and never
changes the workload's capabilities. The helper enters neither its mount
namespace nor its PID namespace; executable and custody paths remain trusted
supervisor paths. Python and nft byte hashes are checked before and after the
operation, and the helper source hash is recorded. These are observed installed
inputs, not an independently selected tool allowlist or complete Binding.

The caller's namespace descriptors are borrowed by each captured helper and
remain open until its return. Each command is limited to five seconds and
128 KiB of combined stdout/stderr. The three commands read the initial ruleset,
install the policy and read back the complete ruleset. Any existing nft object
is refused before installation; no flush, replacement or retry occurs. Policy
JSON is sealed and passed through a read-only descriptor, without shell
interpolation. Quarantine applies to plan/metadata, both final and pending
receipt paths, and captured streams through the existing capture policy.

The installed table is `inet caplab_capture`, with an output filter chain at
priority zero and default drop. Each rule permits exactly one IPv4 destination
and TCP destination port. A final counter/drop rule records denied packets.
There is no general established/related exception: an earlier connection to a
forbidden endpoint must still be blocked. Outgoing IPv6 and UDP packets have
no permit rule. The synthetic loopback integration fixture explicitly permits
both its server port and client reply port because both directions traverse
output in one namespace. A remote TCP peer's reply traverses input instead.

`verify_capture_network_rules(plan, observed, *, expected_policy_sha256)`
rebuilds the anchored policy and compares the entire supplied nft JSON ruleset.
Only the leading nft metadata, valid object handles and nonnegative integer
counter values are excluded from equality. Additional tables/rules, missing
rules, changed defaults/destinations and malformed counters fail. This pure
comparison borrows its inputs; the caller owns bounded reading and trusted
collection of `observed`. The installer supplies its actual bounded readback.

Successful custody contains `preflight.json`, `policy.json`, the `initial`,
`install` and `readback` process captures and their `*-command.json` records,
and `installation.json`. Exact argv, environment and borrowed descriptor
numbers are sealed before each command starts. The returned
`caplab.capture-network-installation/v1` result records the peer and namespace
identities, its capability fields, configuration/tool/helper hashes, command
and receipt hashes, and raw readback hash. `rules_agree` is true, while
`workload_release_verified`, `transport_attached` and `study_eligible` are false.
This result does not prove that a caller subsequently released a workload.

The existing `receive_mount(..., inspect_peer=...)` callback can invoke this
installer after peer/cgroup/mount authentication and before before-capture and
handoff sealing. The isolated integration test exercises that actual callback,
permitted TCP traffic, rejection of new and previously established forbidden
connections, and withheld release on privileged-peer, existing-policy or
quarantine refusal.
The current native diagnostic CLI still selects its original offline profile;
no routed native execution is enabled by this module alone.

The installer creates no interface, route, transport, DNS configuration or
input-chain policy. It cannot attest inbound isolation, provider compatibility,
hostile namespace escape resistance, native task success or capture completeness.
It does not remove rules: its caller owns namespace destruction after success
or failure. Failure after installation can leave the policy and partial receipts;
the caller must withhold release and clean up its owned workload. Exceptions
propagate, and no final installation receipt is sealed on failure.
