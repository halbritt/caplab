# Test network-namespace filtering before provider integration

Baseline `887865d`. The previous goal turn linked prepared task inputs to
native capture and verified one installed-native diagnostic. It still uses
fixed local responses. The older provider-connected preference runner uses
`--share-net`; its historical authorizations do not transfer to a new repair
shakedown. Current capture inspection expects loopback-only networking.

Under ADR 0026, select a bounded local capability experiment before choosing
the provider-connected transport. Test whether the current kernel permits a
new owner-controlled user/network namespace to install and verify an nftables
output policy, and whether a workload with all capabilities dropped remains
subject to that policy. This is an implementation prerequisite, not a provider
request, native subject attempt, containment acceptance or study measurement.

Authorize a private probe and observations under `/tmp/caplab-egress-preflight-*`
and this repository record. The probe may launch at most two fresh isolated
user/network namespaces: first with `unshare --user --map-root-user --net`,
and, only if namespace creation itself is unsupported, one with Bubblewrap.
Before any rule or interface change, require both user and network namespace
identities to differ from the host's recorded identities. Change only the new
namespace: bring up loopback, create an `inet caplab_probe` table and output
chain, and use two fresh loopback TCP listeners to exercise allowed/denied
connections. No external interface, route, DNS lookup or internet connection.

Bound each namespace to 20 seconds, each subprocess to five seconds, loopback
connects to one second, and captured output to 64 KiB per process. Record exact
commands, binary hashes/versions, namespace identities, policy readback, control
outcomes and errors. Require both listener ports to work before filtering;
after filtering require only the selected port to work. Drop bounding,
effective, permitted, inheritable and ambient capabilities and set no-new-privs
before the restricted workload. Test that it cannot alter the namespace rules
or open a raw socket, while ordinary permitted TCP remains usable.

The process owner closes only its sockets and waits for its child processes;
namespace destruction removes its temporary interfaces/rules. Do not change
host firewall rules, host interfaces, sysctls, installed software, capabilities
on executables, or persistent services. Do not read credentials, historical
worlds/captures or private account configuration. No model call, native launch,
provider access, spend, evidence admission, tracker write, external message,
push or independent acceptance. Preserve `docs/designs/` and all other lanes.

Stop on namespace identity ambiguity, unexpected host effect, missing baseline
connectivity, an allowed/denied mismatch, privileged restricted workload, or
unexplained cleanup failure. A local success only supports this observed
kernel/filter mechanism. Native/provider compatibility, DNS/address changes,
IPv6, NAT, namespace escape resistance and the full capture integration still
need their own checks. Failure does not authorize sharing the host network.

Alternatives are retaining offline-only capture, a separately controlled
transport tunnel that preserves the native harness, or a namespace with
outbound filtering. Inspect the local mechanism before adding a transport
implementation. This authorization expires after the bounded experiment and
its local evidence commit.

## Setup observations and one corrected namespace

The first launch exited 1 before running the probe: `unshare` could not write
`/proc/self/uid_map` (`Operation not permitted`). The authorized Bubblewrap
fallback created distinct user and network namespaces with the requested
capability mask `0x3100` and no-new-privs. It then failed before executing even
the loopback command: `capture_process` could not open `/dev/null` through the
read-only root projection. No filtering policy was installed and neither result
tests filter enforcement. Preserve both failed launches and their source bytes.

Under ADR 0026, authorize one additional setup-corrected namespace at
`/tmp/caplab-egress-preflight-final-run`, using a new wrapper
`/tmp/caplab-egress-preflight-final.py`. Keep the original probe and all criteria
unchanged. Add only an explicit `/dev/null` device bind, as the existing capture
fixtures require, so the process recorder can open its null stdin. It names
the host's null character device; no disk-backed host path becomes writable.
Keep the 20-second namespace bound, five-second control bounds, all output
limits, namespace checks and cleanup. This is one correction of a demonstrated
setup defect, with both prior launches retained; it grants no external network,
native execution, further replacement or weaker filter criterion.

## Result and next disposition

The Bubblewrap launch with the explicit null-device bind exited zero in 2.863
seconds, with complete streams and empty stderr. Its result at
`/tmp/caplab-egress-preflight-final-run/result.json` has SHA-256
`8a8305acf4efdd9b4b89a612b992e9cb5e06344cacb94a835e252e01c7698ee0`.
Both TCP listeners replied before filtering. After filtering, port 36287
continued to reply and port 57849 timed out. The restricted child repeated
those outcomes with all five capability sets zero and no-new-privs set.
Its raw-socket request and attempt to flush the output chain were denied.
Readback after those controls retained the same rules; only the drop counter
changed, from zero to two packets totaling 120 bytes.

The separate read-only inspection at
`/tmp/caplab-egress-preflight-inspection.json` checked ten completed process
receipts across all three launches against their retained stream lengths and
hashes. It checked result/observation agreement, current binary/probe hashes
against their pre-launch pins, both namespace identities, capability fields,
baseline and filtered replies, and full policy equality after excluding the
counter values. The first two failures remain intact. The fallback's partial
loopback intent has no completed process receipt because process setup failed.

All recorded namespace commands are terminal. The successful probe joins its
two listener threads and closes their sockets before returning. A later scan
found no matching namespace among readable process entries; 1,068 namespace
links were permission-denied, so that scan cannot prove system-wide absence.
The wrapper observed unchanged host namespace identity. Host firewall contents
were not independently snapshotted: the limited no-host-rule-change conclusion
rests on the checked distinct namespaces before any rule command and the
reviewed command sequence. The read-only root projection used for this trusted
probe is not an approved filesystem profile for untrusted native workloads.

This establishes the exercised local IPv4/TCP filter mechanism. It does not
establish routed connectivity, provider compatibility, DNS policy, IPv6
behavior, resistance to namespace escape, or complete native containment.
No external interface or provider request was used. The existing runtime and
loopback-only capture contract remain unchanged.

Select a source-backed routing experiment as the next step, before integrating
a provider transport. It must distinguish permitted traffic from forbidden
host/internal destinations, verify configuration before releasing a workload,
and retain cleanup and missingness evidence. A separately scoped authorization
must name that experiment's interfaces, destinations and launch allowance.
The current result grants no additional launch. Sharing the host network is
not selected; a controlled transport tunnel remains an alternative if the
isolated routing mechanism cannot meet the required restrictions.

CAPLAB-84 still requires actual representative repairs and empirical capture,
redaction and resource measurements. This result resolves one implementation
uncertainty without supplying any reviewer capability or study outcome.

## Advisory and verification scope

Doctrine's release gate verified commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-715fe75718daf294` was reassembled with four typed records.
Final packet `pkt-3ba11e53fc9d99e1` has content SHA-256
`3ba11e53fc9d99e197b2d923c020a46c95831936c9b3a6e439beee9f2015fad7`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, and retriever `retriever-ec995ecdd083b2c8`.
The packet nominated no network-specific concept. Applied repository precedence
to the native contract, evidence before intervention to the local controls,
bounded authority to the three launches, and structured cleanup to owned
processes and listeners. All four citations classified as valid.

Forty-three missing obligations remain individually listed, classified and
explained in `/tmp/caplab-egress-preflight-obligation-disposition.json`. They
are nonmaterial to the narrow local observation: no runtime API, ownership
architecture, compatibility matrix, typing guarantee, text codec, performance
improvement or complete containment claim is made. In particular, untested
cancellation and fault cleanup cannot be inferred from the successful terminal
run. Those checks become material before selecting a reusable transport.
The packet's module, refactoring and style conflicts do not require a runtime
change for this experiment. Runtime observations support the filter claim;
static assertions cannot establish kernel behavior. Transport architecture
remains undecided pending the next experiment.

The documentation check compared the numeric outcomes, commands, source paths
and result fields against retained bytes and current source. It corrected the
rounded duration from 2.864 to 2.863 seconds. No runtime or standing test source
changed, so the full test suite was not rerun. The previous 1,450-test result
does not provide additional evidence for this filter experiment. All private
probes, failed launches, raw controls and advisory provenance remain retained.

The verified private manifest is
`/tmp/caplab-egress-preflight-verification.json`, SHA-256
`3bb8dd5964ed6f205862ee6e19656d185ed340ae53176e496d760b1ebe6b7258`.
It retains 64 artifact hashes, 14 checked advisory provenance references and
seven current source hashes verified against baseline `887865d`. Those source
hashes are explicitly post-run inspection, separate from the binaries and
probe scripts pinned by each launch. Versioned snapshots preserve this record
at advisory and manifest time without a circular final-record hash. This
authorization expires at the local evidence commit; all three launch
allowances are consumed.
