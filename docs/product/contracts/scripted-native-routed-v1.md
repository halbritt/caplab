# Scripted native routed diagnostic, version 1

The [scripted native CLI](scripted-native-capture-v1.md) accepts
`prepare ... --launch-profile codex-scripted-routed/v1`. Its default remains
`codex-scripted-local/v1`. Both use the same fixed supplied tool/response
exchange, fabricated authentication, native policy and pinned Codex source
profile. Neither invokes a provider or measures model-generated work.

Routed preparation uses `caplab.scripted-native-preparation/v3`, adding
`launch_profile` and `task_input` (an anchored input selection or null). Versions
1 and 2 remain the offline formats. A v3 preparation cannot relabel itself as
the offline profile. It pins the existing Python/node/strace/Bubblewrap tools
plus slirp4netns, nft, ip and setpriv. Source, runtime and optional task inputs
are reverified before the existing one-shot consumption path. The same separate
authorization format binds the exact preparation hash; preparation creates no
execution permission and a failed attempt is not refunded.

The routed worker enters a fresh outer user/network/PID namespace before
launching the workload. It preserves the supervisor UID mapping and mounts
the declared repository, native installation, fixture dependency and selected
task-input custody read-only.
Only its owned custody tree and delegated unit cgroup are bound writable.
It records the parent and outer namespace identities, confirms only loopback
and no routes, then assigns `198.18.0.1/32` to that outer loopback. The four ip
commands have captured argv, streams and completion, bounded to five seconds
and 128 KiB each. No host interface, address or route is changed. The outer
namespace has a synthetic resolver file; it does not select a DNS destination.

The supervisor owns the scripted fixture in a joined thread, listening only on
`198.18.0.1` and one selected ephemeral TCP port. It seals the resulting exact
destination policy before releasing the workload. The fixture has the existing
protocol limits and request-identity checks. Its protocol files are retained
under `safe-fixture-requests`, guarded before persistence; its joined summary
is sealed separately as `safe-fixture.json`. A startup or thread failure
propagates. The owner requests stop on body exit and allows eight seconds for
join, covering the fixture's bounded observation handshake and socket close.
The owned service remains the final process-level lifetime boundary.

The inner Bubblewrap workload maps UID/GID zero and requests NET_ADMIN and
SETPCAP for raising loopback and dropping its bounding set. The
bootstrap clears all five capability sets and sets no-new-privs before the
authenticated mount handoff. The policy installer independently reads those
fields while the peer is blocked. The native launcher and child execution
remain subject to the existing authenticated exec handoff, source preparation,
outside trace and frozen-child observation checks. These configured and
observed components do not amount to independent hostile-escape acceptance.

The handoff installs the exact IPv4/TCP policy, attaches restricted slirp and
includes the [routing readiness record](capture-network-transport-v1.md) before
task materialization and release. Host-loopback forwarding, built-in DNS,
IPv6 and the slirp API remain disabled. The native base/refresh URLs use the
fixed outer fixture address and selected port; no generic endpoint override
is added. Routing closes after workload writers stop and before final fixture
summary collection. Failed or incomplete routing cannot become a completed
routing observation.

The first admitted request triggers the existing Unix child-observation
handshake from the supervisor fixture process, authenticated with SO_PEERCRED.
The workload remains separately authenticated by its mount/exec handoffs.
The request hash, freeze/thaw interval, observed child executable and eventual
native trace are still linked. TCP is not a native-process authentication
mechanism. The fixture's protocol source is outside the workload cgroup and
cannot be described as a workload-local observation.

The routed mount handoff has a 25-second deadline, process capture 75 seconds,
owned systemd unit 120 seconds and outer capture 130 seconds. The native body
remains 30 seconds, native identity/observation handshakes five seconds, and
routing helper 45 seconds. Existing memory, task, stream, file and inventory
limits remain. These are termination ceilings, not measured costs or a promise
that every scheduling path succeeds. The offline profile retains its original
limits.

Inspection joins the native bootstrap summary and the separately retained
fixture summary without rewriting either. A fixture error keeps the attempt
failed even when the native bootstrap exits normally. Its timing is bounded by
fixture completion rather than by the earlier native polling clock. It checks
the prepared profile, exact outer command, selected destination, native port,
outer-to-handoff namespace link, and protocol files against the anchored capture
manifest. Shared custody inspection requires explicit routing evidence; the
terminal hash comes from that manifest and readiness from the verified handoff.
The [retained routing inspector](capture-network-verification-v1.md) checks
policy, command, stream and lifecycle consistency. Offline inspection refuses
an unexpected routed handoff.

Routed execution and inspection remain diagnostics. Complete native capture,
provider compatibility, representative repairs, incremental observer cost,
blinding, coding reliability, model quality and qualification require separate
evidence. Existing historical attempts and preparation files are not migrated
or replayed by this feature.
