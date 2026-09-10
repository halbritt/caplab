# Check restricted provider TLS routing before authenticated repairs

Baseline `933a280`. The preceding resource observer is committed and verified
with synthetic successful and failed processes. Live Plane readback retains
86 items and 12 open, including CAPLAB-80/84/85. The installed native diagnostic
currently uses a disconnected supervisor and fixed responses. Provider-connected
repair execution still requires a verified serving path and separately selected
credential administration; another fixed-response success cannot supply it.

Under ADR 0026 and the continuing owner goal, authorize a bounded connectivity
experiment using the existing parent-owned routing implementation. This is a
transport prerequisite, with no native harness launch, authentication, model
request, study execution or representative repair claim.

Authorize one IPv4 resolver lookup for `chatgpt.com`, bounded to five seconds
and 16 KiB of output. The earlier installed-native endpoint observation in
`verification-2026-09-09-native-auth-401.md` names that hostname. Retain only
sorted unique global IPv4 addresses and lookup timing. Freeze the numerically
smallest returned address, TCP port 443, hostname and public system CA bundle
hash before launch. Stop if no global IPv4 address is returned. No resolver
fallback, alternate address or automatic retry is authorized.

Then authorize one owned transient user unit and one fresh Bubblewrap workload
namespace using `parent-user/v1`. The trusted supervisor keeps its existing
network solely so the existing slirp helper can relay the approved destination;
the workload has a distinct network namespace, zero capabilities, no-new-privs,
no DNS, no host loopback route and the exact installed destination policy before
release. Do not change host interfaces, routes, rules, services or sysctls.

The workload may make one TLS connection to the pinned address with SNI and
certificate verification for `chatgpt.com`, using the read-only public CA
bundle. Send no HTTP request, application payload, cookie, token or other
credential. Record the certificate hash, verified hostname selection, TLS
version and cipher, peer address and connection timing. A successful handshake
proves only connectivity and certificate verification in this configuration.

After policy installation, attempt three negative TCP connections: pinned
address port 80, slirp host address `10.0.2.2:443`, and tailnet-range address
`100.64.0.1:443`. Each has a 0.5-second timeout and sends no application data.
Require all to time out; unexpected success or a different failure stops the
control. Do not probe further destinations or weaken the policy after failure.

Use the existing authenticated mount-handoff control and production routing
collector/inspector. Retain a private copy of the control helper with only the
explicit read-only CA mount added; pin its source, original source, production
modules, setup helper, tools and CA bytes. The synthetic workload sees read-only
`/usr`, its private proc/dev surfaces, five bounded writable tmpfs mounts and
the control socket. No operator home, private configuration, credential file or
historical world is mounted or read.

The unit is limited to 40 seconds, 256 MiB memory, zero swap and 64 tasks.
Workload capture has 15 seconds and 10 KiB combined stream output; routing has
20 seconds and its existing 128 KiB stream ceiling; TLS has five seconds. The
outer command has 45 seconds and 128 KiB combined output. All owned descriptors,
processes and the unit must be closed/joined/removed. Preserve partial captures
and errors. No retry is authorized by a failed attempt or lost observation.

Retain private probe, selection, source pins, raw results and inspection under
`/tmp/caplab-provider-tls-*`. Verify policy/readiness/terminal linkage, peer
identity, TLS and negative controls, source stability and owned cleanup. Commit
and push this result record after verification. This authority expires after
the one lookup, one unit and bounded verification. Preserve all prior custody,
`docs/designs/`, other worktrees and services. No tracker write, external message,
credential operation, reviewer ranking or independent acceptance is authorized.

## First launch: setup refusal before handoff

The one resolver call returned `104.18.32.47` and `172.64.155.209`; the frozen
selection is `104.18.32.47:443` with hostname `chatgpt.com`. CA bundle SHA-256 is
`6602a85a36afc2e51c66a0df5ae3d383c5b7c2fed93339ccef7d37e01faf09e8`.
Destination-policy identity is
`995e7aef6c7a9b88e3afd76d86ff99db758550f3ea30e2517f2ce8efa76645c0`.

The first workload exited 127 with `setpriv: apply bounding set: Operation not
permitted`; the supervisor subsequently timed out waiting for mount handoff.
The control copied an outer `setpriv --bounding-set=-all` prefix from tests
whose supervisor was already privileged inside its own user namespace. Here
the host supervisor is unprivileged and cannot change that bounding set.
No workload namespace, policy, routing helper, TLS or negative connection was
reached. The owned unit `caplab-provider-tls-eebe2e6f6597442c9b3b860d9fde869d.service`
is not found/inactive and its cgroup is absent. Original capture and source
bytes remain at `/tmp/caplab-provider-tls-control` and the first script paths.

Under ADR 0026, authorize one setup-corrected unit at
`/tmp/caplab-provider-tls-corrected-control`. Remove only the host-side `setpriv`
prefix from a separately retained worker copy. Bubblewrap still creates the
fresh user/network/PID/mount namespaces, and the existing trusted setup still
establishes the non-root workload and drops all five capability sets before
handoff. Production routing must independently verify those same zero-capability
and namespace-ownership conditions before releasing the peer. The corrected
launch grants no new workload privilege or host rule-changing authority.

Copy only the named synthetic selection and CA-mount control helper from the
first root into the new root; explicitly retain their equal byte hashes. Reuse
the exact frozen provider address, hostname, CA hash and policy without a new
DNS lookup. Preserve every prior criterion, deadline, negative control, capture
bound, source pin and cleanup requirement. This authorizes one additional
unit, not an automatic retry policy. Stop after its result; further effects
need a new decision. No native execution, HTTP request or credential use.

## Corrected control and retained verification

The corrected unit completed with exit zero in 2.467 seconds. Its captured
client completed TLS 1.3 with `TLS_AES_256_GCM_SHA384`, using CA verification
and hostname checking for `chatgpt.com` at `104.18.32.47:443`. The peer
certificate was 921 bytes with SHA-256
`ad91a26bd918766c2a03145563b5f833a9a7c999dce33e4869eae291dcfb57dc`.
The connection interval was 19,075,286 nanoseconds; it is one observed interval,
not a provider-latency estimate. All three negative TCP controls timed out.
The client sent no HTTP request or application payload.

Production retained routing inspection passed with `parent-user/v1`. The
network owner is the distinct immediate parent of the workload user namespace;
all five workload capability sets are zero and no-new-privs is set. UID/GID
maps are `[[1000, 1000, 1]]` in supervisor coordinates. Network identity SHA-256
is `4ac93f9026783b363886457fd310397683144548f9e5750021cac7b82c57c9bf`.
The authenticated handoff's readiness document agrees with the retained
policy, command and terminal links. Readiness preceded TLS; the helper exited
normally after the workload. Supervisor namespace and descriptor observations
were unchanged across the control.

Unit `caplab-provider-tls-2cdbf512839045d898e59aa8f2150c3e.service` is
not found/inactive and its cgroup is absent. The independent read-only script
`/tmp/caplab-provider-tls-verify.py` rechecked both controls' source pins,
consumption/selection/authorization hashes, retained stream sizes/hashes,
handoff and routing links, TLS/negative observations and current owned cleanup.
It also confirmed that the private handoff helper differs from repository
source only by the fixed read-only CA mount. Both control selections have
identical bytes. No second resolver call or alternate destination was used.

## Meaning for the repair shakedown

The existing routing mechanism can carry certificate-verified TLS to the named
native-provider hostname from the exercised isolated workload. The host-side
prefix failure identified an assumption specific to the disconnected test
supervisor, and the corrected experiment preserved the zero-privilege workload
boundary. No runtime code or standing test was changed.

This removes one transport uncertainty before provider integration. It does
not establish HTTP/WebSocket compatibility, authentication or refresh behavior,
available model/account capacity, DNS-change handling, IPv6, continuous hostile
containment, native tool execution or representative repair quality. No proxy
or replacement harness is selected. A future native provider profile must
freeze its exact endpoint/CA/address selection, administration, capture and
resources and receive its own bounded authorization.

Keep the current fixed-response profiles unchanged. The next implementation
must separate provider administration from the scripted fixture and derive
native endpoint selection from a prospective provider configuration. Credential
delivery must preserve the existing private input and output-quarantine
boundaries; this result grants no credential read or delivery. CAPLAB-80/84/85
and the wider goal remain incomplete.

## Advisory and verification custody

The read-only verification checked five process receipts from the failed
control and eight from the corrected control, with 222 source/tool/selection
pins in each. Corrected result SHA-256 is
`faae0510426090160ab774e45b3da9d6f314ba6f25053542773bd129caa347c0`.
Private results and verification remain under `/tmp/caplab-provider-tls-*`.

The validated Pincite release remains commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
Initial packet `pkt-4138a7b5e4a4f83f` identified 73 obligations. Four inspected
typed records produced final packet `pkt-d104e1bda9fa011e`, content SHA-256
`d104e1bda9fa011e1fef3f0df77a721f3523fa7a52d0653292e4fa88c88afadc`.
Applied bounded authority, repository precedence, evidence before intervention,
preserved behavior and structured cleanup to this existing-API experiment.

Nineteen remaining obligations are individually classified in
`/tmp/caplab-provider-tls-obligations.json`: six production-object ownership,
four code-structure/local-reasoning, four broader toolchain/CI, three static
annotation/checker and two representative text/codec obligations. No production
API, object model, refactoring, type system or text codec is changed or
qualified here. Those omissions do not support broader conclusions. The
schema-validated decision receipt and citation classifications for both served
packets remain under the same private prefix.

Documentation verification compared the stated selection, hashes, exact
failure, timing, source delta, observed privileges and cleanup against retained
bytes. `git diff --check` passed. The full suite was not rerun: only this result
record changes the repository, and the unchanged production sources already
passed the preceding 1,489-test run with four skips. That suite is not evidence
of public-provider connectivity; the new bounded control supplies that narrower
observation. No independent acceptance is recorded.

The final manifest is `/tmp/caplab-provider-tls-verification-manifest.json`,
SHA-256 `db11c55ee2d43d2053bd0a615173eeaf7d88f6b92a282a8c4594aee6d2f6293c`.
It pins 107 private artifacts, including both controls and their pre-execution
source selections. Readback also verified the preceding resource-observation
manifest's 49 private artifacts and nine source/contract pins unchanged.
The final record remains outside its own manifest to avoid a circular hash.
