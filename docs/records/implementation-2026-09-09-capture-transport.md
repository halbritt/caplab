# Own restricted routing throughout a capture

Baseline `435175e`. The prior goal turn made progress by committing the
destination installer. A current Plane read reports 86 items, 12 open, with
CAPLAB-84 In Progress. Its representative repair requirement remains unmet.
The native diagnostic still verifies a loopback-only network. The installer
can enforce exact destinations but attaches no transport. The earlier private
routed controls demonstrated normal slirp shutdown only after closing its
exit pipe, and retained a timeout when the probe merely wrote to that pipe.

Under ADR 0026, select a CAPLAB-owned context manager that installs the policy
before attaching slirp, waits for observed readiness, retains command and
policy linkage, and owns exit-descriptor closure and captured termination on
both normal and exceptional body exit. Reuse the existing bounded process
recorder and quarantine. Pin the target namespace descriptors and compare
them with the installer observation. Keep host-loopback access, built-in DNS,
IPv6 and the slirp API socket disabled. Use fixed tap0 and slirp's default IPv4
network. Caller owns endpoint authority, namespace exclusivity, authenticated
peer lifetime, private custody and the enclosing workload deadline.

Authorize `src/caplab/capture_network_transport.py`, its versioned contract,
`tests/test_capture_network_transport.py`, minimal parameterization of the
existing network handoff fixture in `tests/test_capture_network_policy.py`,
this record, and private verification under `/tmp/caplab-transport-*`. These
are a feature and its integration controls, not an adjacent refactor. Preserve
the existing offline native profile and every prior raw experiment. Do not
change native invocation/selection or renew a native attempt allowance.

The transport capture is bounded by a positive finite caller lifetime of at
most 300 seconds, with readiness limited to five seconds and output to 128 KiB.
Exceptions must close the owned exit writer and join the capture while its
borrowed descriptors remain open. A timeout, incomplete stream, helper error
or changed tool must not be reported as normal shutdown. A body exception
must remain a failure even when helper cleanup succeeds. Readiness is an
observation, not a promise that the helper remains alive through the body;
normal context completion requires the terminal helper checks too.

Standing integration tests may launch fresh outer Bubblewrap user/network/PID
namespaces with only loopback and no external route. In that owned namespace,
bring up loopback and assign 198.18.0.1 and 100.64.0.1, each solely for fixed
synthetic TCP sentinels. The inner workload uses the actual authenticated mount
handoff and drops all capabilities before it waits for release. Slirp egress
must remain in the disconnected outer namespace. Bound each outer capture to
30 seconds and the inner capture to its existing 15 seconds. Owned setup may
use SYS_ADMIN, NET_ADMIN, SETPCAP and NET_BIND_SERVICE; expose the existing
null and tun devices only to the trusted outer fixture. Tests may omit tun to
induce actual helper startup failure and raise a fixed body exception to
exercise cleanup. A short transport lifetime may exercise actual timeout.
All test listeners, process captures and descriptors must be joined/closed.

No external connection, DNS query, native/model call, credentials, spend, host
firewall or service change, historical evidence import/rewrite, tracker write,
message, push, deployment or independent acceptance. Preserve `docs/designs/`.
Stop on unexpected host effects, namespace ambiguity, lost failure evidence,
unbounded cleanup or unexplained regressions. Run focused and full checks,
review source and evidence, and commit locally; this scope expires at that
verified commit. Routing plus policy is still not a provider-ready native
profile or a representative repair measurement.

The installed slirp4netns 1.2.1
[manual](https://github.com/rootless-containers/slirp4netns/blob/v1.2.1/slirp4netns.1.md)
documents readiness, namespace paths and sandbox restrictions. The earlier
retained [routing record](inspection-2026-09-09-routed-network.md) supplies
the observed exit-pipe failure and correction. They guide this implementation;
neither authorizes replay of those historical runs.

The first nested fixture could not write its inner UID mapping; preserving the
outer caller's UID then exposed Bubblewrap's refusal of inherited capabilities.
Drop all inherited capability sets before launching the inner Bubblewrap.
Retain the outer cgroup namespace's view so the existing exact membership
check can identify the fixture group. These changes affect the trusted test
launcher, not the production handoff's authentication checks.

With that setup, the policy installed and slirp obtained its TAP descriptor,
but its sandbox failed at `setegid(0)`. The initial diagnosis was that the
inner user namespace mapped only the caller's nonzero ID. Under ADR 0026,
select an explicit inner UID/GID
zero mapping for the routed synthetic fixture. It maps to the same outer owner
and still drops all workload capabilities before the handoff. Preserve the
original nonzero mapping in the existing policy-only fixture and native CLI.
This is a real constraint on the prospective routed native profile; future
integration must freeze and verify its mapping as part of the Binding, rather
than claiming this fixture validates the existing native configuration.

The zero-mapped fixture still failed at the same call, contradicting that
diagnosis as a sufficient explanation. The matching upstream
[parent path](https://github.com/rootless-containers/slirp4netns/blob/v1.2.1/main.c)
passes only `target_pid` to sandbox namespace entry, ignoring the explicit
namespace paths in this phase. With path mode there is no target PID. Preserve
descriptor pinning; do not switch to an unpinned PID lookup or disable sandbox.
Authorize a fixed Python helper to enter only the pinned target user namespace,
select its mapped UID/GID zero, reduce capabilities to SYS_ADMIN, NET_ADMIN and
NET_BIND_SERVICE, set no-new-privs, record its pre-exec state and execute the
fixed slirp binary. Its network namespace remains the caller's egress namespace;
slirp's TAP setup child enters the pinned target network namespace. The parent
is already mapped root when slirp builds its sandbox. Record Python/helper
hashes as well as slirp identity. No host UID mapping or capability is changed.

The helper reached sandbox creation but slirp then refused its own bounding-set
drop without SETPCAP. Its matching
[sandbox source](https://github.com/rootless-containers/slirp4netns/blob/v1.2.1/sandbox.c)
performs that operation before retaining only NET_BIND_SERVICE. Add SETPCAP to
the fixed helper's temporary capability allowance so slirp can complete its
documented reduction. Keep all other capabilities removed, no-new-privs set,
the final sandbox enabled and the workload's zero-capability requirement.

## Implementation and observed controls

The [routing contract](../product/contracts/capture-network-transport-v1.md)
defines one context manager. It keeps policy installation, pinned descriptors,
readiness and helper cleanup together. Removing that module would return the
same lifecycle obligations to every capture caller. Leaving only private
probes would not integrate the accepted containment requirement. An unpinned
PID fallback and disabling sandbox were rejected; actual native adoption is
deferred until its mapping, provider endpoints and complete capture profile
are frozen and verified.

The transport module and test are new. The existing policy test helper gains
parameters for the real installer, selected plan/producer, launch privilege
drop and explicit inner mapping; its original tests and default behavior remain
unchanged. Production policy installation, process capture and mount handoff
are reused without modification. The outer test projection mounts `/usr`, this
repository and cgroup information read-only, supplies private `/etc` and `/run`,
and binds only its own output writable. It preserves the caller's cgroup view
while isolating user, network and PID namespaces. No host network is attached.

The red test failed on the missing transport module. The setup and helper
failures described above remain in `/tmp/caplab-transport-*` with raw captures
and command records where reached. The earliest fixture failures did not retain
complete immutable test-source snapshots; do not attribute later fixture source
to those runs. Later diagnostics record source hashes and exact helper argv.

The combined focused run passed eight tests in 9.094 seconds. Its only subsequent
test change retained the already-checked initial outer interfaces/routes in
the result. The final-source full suite is a separate verification gate.

Five separate retained controls under `/tmp/caplab-transport-private-final`
exercise normal completion, missing tun, body exception, transport timeout and
command quarantine. Their verifier checks 29 process receipts against actual
stream lengths/hashes, policy readback against the exact selected destination,
command/readiness/terminal linkage and policy completion before helper start.
It preserves incomplete timeout streams. Twelve source/tool pins agree before
and after, as do the supervisor's user/network/PID namespace identities and
descriptor population. Each outer fixture records only loopback and no routes
before its local address setup; all three local sentinels reply before handoff.

Normal capture permits only the selected service among the three tested TCP
targets and closes slirp normally. Missing tun leaves no readiness or release
marker and records failed helper termination. A fixed body exception after
readiness withholds release, closes the helper normally and remains the reported
error. A real two-second helper timeout leaves an incomplete process capture
and a failed terminal check even though the synthetic body had completed.
Quarantined command metadata refuses before helper creation and leaves no
terminal receipt. These are distinct observations; none is relabeled as native
task success or reviewer capability.

The retained verification report is
`/tmp/caplab-transport-private-final/verification.json`, SHA-256
`a809916eaf56d14b5bc130fa4cb06de114aa7c804c678155b5a6626538f42bd3`.
It is a local inspection of fixed controls, not independent containment
acceptance, provider compatibility or representative repair evidence.

## Final checks and advisory record

The final-source full suite exited zero: 1,458 tests, four skips, 185.691 seconds.
Log `/tmp/caplab-transport-make-check-final.log` used the existing retained
WebSocket test dependency through `CAPLAB_TEST_WEBSOCKETS_ROOT`. All three
runtime/test source hashes in `/tmp/caplab-transport-final-source.sha256`
still match after completion. Python 3.12.3, slirp4netns 1.2.1 with libslirp
4.7.0 and libseccomp 2.5.5, Bubblewrap 0.9.0 and nftables 1.0.9 were observed.
No other version/platform or representative repair workload was tested.

The validated Pincite release gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Release commit is `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Initial packet
`pkt-472b17ffd59d0cb2` was reassembled with six typed observations into
`pkt-5ed37c59ae8f400b`, content hash
`5ed37c59ae8f400ba006efb0238e7d3cbfcddf991be0f343527498ebf0a82a33`.
Corpus is `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.

Applied resource-lifecycle ownership, repository precedence, structured cleanup,
evidence before intervention, runtime validation and bounded authority. The
packets retain each concept's source locators. All six output concept citations
classify as valid in both packets. The decision receipt's two local evidence
locators classify separately as foreign to the doctrine corpus. The receipt
passes the release schema and records selection without independent acceptance.

Eleven remaining obligations are individually retained with nonmaterial
classification and reasons in `/tmp/caplab-transport-obligations.json`: four
concern CI/tool/version matrices, three concern static-checker or annotation
claims, one concerns retention/contention measurement for reused resources,
one concerns representative non-ASCII data and two concern a measured no-change
assessment. No such claims are made. Each call owns fresh resources; runtime
validation and local lifecycle controls establish the bounded behavior here.
Representative capture costs and full native containment remain future work.

Keep the lifecycle in one module rather than splitting it by line count or
adding a generic transport interface. Runtime checks enforce externally supplied
values; annotations do not establish their validity. Existing native consumers
and their offline verification remain protected. This addresses the packet's
module-size, static/runtime, uniformity and staged-design conflicts without an
adjacent refactor or unsupported performance claim.

Test Guard checked real kernel/process/handoff execution, distinct error
outcomes, receipt linkage and immediate release markers. AI Failure Modes review
checked failure propagation, bounded ownership and actual helper execution.
Docs Guard compared signatures, limits, fields and restrictions to current
source and retained results. The contract states that readiness is not continuous
liveness and that caller code owns the body's deadline. No mock fallback,
timeout relabeling or claim of native success was introduced.

Ruff F, formatting, whitespace and local Markdown-link checks accompany the
commit. `/tmp/caplab-transport-verification.json` inventories private artifacts
and the five final changed files; packets, evidence, classifications, raw
failures and final-source snapshots remain private provenance. This local
commit expires the named execution scope. Plane remains unchanged and CAPLAB-84
remains open. No provider/native attempt, study admission, qualification or
independent acceptance occurred.
