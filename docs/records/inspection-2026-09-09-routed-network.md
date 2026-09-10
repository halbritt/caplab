# Test routed filtering without an external network

Baseline `cdbb898`. The local loopback filter passed, but it did not exercise
a network transport. Under ADR 0026, the primary agent selects a bounded
slirp4netns routing experiment before any provider integration. The installed
version is 1.2.1 with libslirp 4.7.0. Its matching
[manual](https://github.com/rootless-containers/slirp4netns/blob/v1.2.1/slirp4netns.1.md)
documents readiness/exit descriptors and host-loopback/DNS restrictions; its
[source](https://github.com/rootless-containers/slirp4netns/blob/v1.2.1/main.c)
shows a helper entering the target namespace to configure a TAP. These are
upstream interface evidence, not observations of CAPLAB execution.

Authorize new private source, retained upstream references, controls and
receipts under `/tmp/caplab-routed-network-*` and this record. Launch at most
one outer Bubblewrap namespace, one inner network namespace and one
slirp4netns instance. The outer namespace must differ from the host in user,
network and PID identity and have only loopback and no default route before
setup. All sentinel addresses belong only to its loopback interface:
198.18.0.1 (permitted service and forbidden second port), 100.64.0.1
(forbidden internal service), 198.18.0.53 (local UDP control on port 53),
and 127.0.0.1 (host-loopback sentinel). Use ephemeral TCP ports and synthetic
one-byte replies. A private resolver file names only 198.18.0.53.

The inner namespace must differ from the outer network namespace before TAP
setup. Slirp may configure only that namespace's tap0, using its default
10.0.2.0/24 network and default route. Its egress stays in the disconnected
outer namespace. Enable its sandbox, seccomp, disable-host-loopback and
disable-dns options. Require readiness before traffic; record actual namespace
identities, interfaces, routes, process configuration and policy readbacks.
The private probe may bind the existing null and tun devices into the outer
namespace and use CAP_SYS_ADMIN, CAP_NET_ADMIN, CAP_NET_RAW and CAP_SETPCAP
there for setup. This trusted probe's filesystem projection is not a native
workload containment profile.

Before filtering, require replies from both ports at 198.18.0.1, the internal
sentinel and the direct UDP control. Require the gateway-host and built-in DNS
paths to fail while the outer sentinels are live. Then install an inet output
policy allowing established/related traffic and only the selected IPv4/TCP
destination/port; deny everything else. Repeat traffic with all workload
capabilities dropped and no-new-privs set. Require the selected destination
to work; require other tested destinations to fail, rule mutation and raw
sockets to be denied, and unchanged policy apart from observed counters.

Bound the outer capture to 80 seconds, child and slirp captures to 35 seconds,
individual commands to five seconds and connects/receives to one second.
Limit each process capture to 128 KiB. Setup/readiness waits are bounded and
check the actual capture future for early failure. Stop on an unexplained
setup/control failure, namespace mismatch, output limit, unexpected route or
cleanup failure. Signal slirp through its owned exit descriptor, stop the
child through its private control file, join all owned captures/listeners,
and retain terminal receipts. No replacement launch follows failure.

No external interface, external DNS, provider request, native harness/model
call, credentials, spend, host firewall/sysctl/service change, historical
research effect, tracker update, message, push or study acceptance. Preserve
`docs/designs/` and all previous probes. This scope expires at the bounded
experiment's evidence commit. Native integration, hostile-workload escape
resistance, provider compatibility and representative repair measurements
remain separate requirements. A controlled transport tunnel remains an
alternative if isolated routing cannot satisfy the required restrictions.

Before any launch, amend the slirp allowance to two sequential instances in
the same inner namespace. The first keeps host-loopback and built-in DNS
enabled and must demonstrate all six sentinel paths. Stop it through its exit
descriptor and require terminal cleanup before starting the second with both
restrictions enabled. The second must preserve the four direct baselines and
deny the two special paths before nft filtering. This omission control prevents
an unreachable sentinel or invalid UDP probe from masquerading as enforcement.
No other namespace, limit or replacement allowance changes. Two instances
mean two declared control conditions, not retry after failure.

Source review before launch found that `create_sandbox` in upstream
`sandbox.c` explicitly retains CAP_NET_BIND_SERVICE via capset. Add that
capability to the outer setup allowance so the requested sandbox can perform
its documented transition; the restricted workload still drops every
capability. The retained source names this requirement. No host capability
or executable attribute changes.

## Resolver setup failure and correction

The outer launch at `/tmp/caplab-routed-network-run` exited 1 before executing
the Python probe. Bubblewrap reported `Can't create file at /etc/resolv.conf:
No such file or directory`. No inner namespace, sentinel or slirp process ran.
This is a filesystem setup failure, not routing evidence. Preserve the original
probe, preflight and complete 72-byte stderr.

Under ADR 0026, authorize exactly one corrected outer launch at
`/tmp/caplab-routed-network-corrected-run`, with a new probe file
`/tmp/caplab-routed-network-corrected.py`. Replace only resolver projection:
create a private `etc` directory containing the synthetic `resolv.conf` and
bind that directory read-only at `/etc`. This avoids the host resolver symlink
and removes the probe's access to other host `/etc` files. Keep the original
traffic controls, namespace/capability checks, two sequential slirp conditions,
capture limits, stop and cleanup criteria. No further replacement is granted.

## Exit descriptor failure and correction

The corrected resolver projection allowed the inner namespace and first slirp
condition to run. All six routed sentinel paths replied. The probe then wrote
to the exit pipe and waited five seconds, but slirp did not terminate. The
child stopped on the owner's stop file; slirp reached its 35-second capture
deadline and was killed, retaining incomplete streams and return code -9.
The outer command exited 1 with its full traceback. No second slirp condition
or nft filter was executed.

The upstream
[poll loop](https://github.com/rootless-containers/slirp4netns/blob/v1.2.1/slirp4netns.c)
registers only G_IO_HUP for the exit descriptor. Writing data does not satisfy
that event. This is a probe lifecycle defect; the passing routed baseline
does not establish normal shutdown or restricted routing. Retain all sources
and failed-run receipts unchanged.

Under ADR 0026, authorize one final run at
`/tmp/caplab-routed-network-final-run`, using
`/tmp/caplab-routed-network-final.py`. Change only exit signaling from writing
a byte to closing the owned write end, removing it from subsequent cleanup
to prevent double close. The read descriptor borrowed by capture remains
open until capture returns. Repeat both declared control conditions in fresh
namespaces, under the same limits and criteria. Require normal first-instance
termination before starting the second. No further run, external connection,
native execution or weaker outcome is authorized by this correction.

## Observed result

The final run exited zero with complete outer streams in 4.699 seconds. Result
`/tmp/caplab-routed-network-final-run/result.json` has SHA-256
`8e6f01356bac42d54e9e1f221008fa4bbe0fe3c9fe8e06082e3576790d4fd7ec`.
The omission condition reached all six sentinel paths. After normal shutdown
and restart with both slirp restrictions, the four direct paths still replied
and the gateway-host and built-in DNS paths failed. After nft policy installation,
the child with zero capabilities and no-new-privs reached only the selected
address and port. Wrong-port, internal-address and gateway TCP connections timed
out; the direct and built-in DNS UDP sends returned EPERM. Raw socket creation
and policy mutation were also denied.

All rules remained unchanged after the restricted controls. The drop counter
increased from zero to nine packets totaling 570 bytes. Every outer sentinel
still replied after the child finished. Both slirp instances recorded an
exit-descriptor event and normal return with complete streams; the first had
finished before the second started. The child and outer command also returned
zero. The private listeners were joined and closed. This demonstrates normal
cleanup for the final run; the earlier forced termination remains a failure.

A separate read-only inspection verified 27 process receipts across all three
runs, including the retained prefixes from the slirp timeout. It checked stream
lengths/hashes, current files against each run's nine preflight source/binary
pins, namespace differences, baseline and restricted outcomes, unchanged policy,
sequential slirp termination and raw-result linkage. Inspection is retained at
`/tmp/caplab-routed-network-inspection.json`, SHA-256
`ec34d1acf9fdee1842f6186d4ca1535264592a1a605e59553284db657231120a`.
The timeout receipt's incomplete-stream flag is preserved; hash agreement does
not make that capture complete.

## Decision after the experiment

The mechanism can carry the exercised local IPv4/TCP and UDP traffic while
enforcing the named restrictions. Select a prospective native-capture network
profile as the next implementation step. It must install and verify destination
policy before native release, pin transport configuration and binaries, keep
resolver authority outside the workload, and own readiness, exit-descriptor
closure and failure cleanup. Preserve the existing offline profile and its
loopback-only checks. The new profile must have its own verification contract;
this probe's broad read-only filesystem projection cannot become its default.

No provider transport or native launch is authorized by this selection. Real
endpoint/address handling, IPv6, surviving connections, namespace escape paths,
failure/cancellation cleanup and integration with the existing capture handoff
still need bounded verification before a provider-connected attempt. The
sentinels are synthetic local services, not external hosts or provider replicas.
CAPLAB-84 remains open for representative repair measurements.

## Advisory and checks

Doctrine's release gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-8fd44b79d0bc07b2` was reassembled with four evidence
records. Final packet `pkt-f5436a45ce059479`, SHA-256
`f5436a45ce059479cfd9dd9d44648e3cff545d1eeb06bd43dfe29a3274b7f87f`,
uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, and retriever `retriever-ec995ecdd083b2c8`.
One evidence declaration was narrowed before final assembly: known capture
limits do not establish instrumentation overhead. Both assemblies are retained.

Applied repository precedence, evidence before intervention, bounded authority
and structured cleanup. All four concept citations classified as valid in all
three packets. The decision receipt's two local evidence locators classified
as foreign to the Doctrine corpus; they remain CAPLAB evidence, with their
own hashes. An initial checker incorrectly expected those locators to be
doctrine citations. The corrected check preserves their classification and
checks the four output concept citations separately.

The 38 missing obligations are individually retained with scope-relative
classification and reasons in the private obligation disposition. They are
nonmaterial to this local observation: performance, observer cost, compatibility
matrices, general text handling, maintainability and complete fault/cancellation
coverage are not claimed. Complete lifecycle and containment checks become
material before native integration. The packet's performance and structural
design conflicts do not warrant optimization or refactoring in this probe;
the next integration must preserve the tested restrictions and failure records.

Ruff F checks passed for the executed private probes. Documentation was checked
against the retained commands, upstream sources and actual control outputs.
No production runtime or standing test file changed, so the full suite was
not rerun. All raw runs and private sources remain intact, including the
72-byte setup error and incomplete timeout streams. The decision receipt
records next-step selection separately from execution and study acceptance.

The private verification manifest is
`/tmp/caplab-routed-network-verification.json`, SHA-256
`e77bc075bd71afd6558392c37c8d175a6e18f8560c07bc8ebfe3b48e56ee6501`.
All 143 artifact hashes and 15 evidence provenance references were checked.
The record is snapshotted at advisory and manifest time; the final repository
commit supplies its final version. All execution allowances in this record
expire at that commit. The unused second slirp condition from the failed
lifecycle run cannot be resumed as a separate attempt.
