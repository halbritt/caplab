# Prospectively seal the effective native launch

Baseline `9fabc76`. Decision mechanism: primary agent under the continuing
CAPLAB goal and [ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Observation, decision and authorization

The previous native diagnostic authenticated its entrypoint and retained exact
effective arguments and environment. Commits `881624e` and `9fabc76` supplied
reusable tracer observation and effective-configuration checks, but their joint
prospective use has not been observed. Select one new diagnostic that seals the
full configuration before releasing the authenticated exec guard. This is
integration verification, not a representative repair or capability measurement.

Authorize this record and private derivation, synthetic controls, preflight,
native capture, verification and advisory artifacts under
`/tmp/caplab-native-launch-adoption-*`. Derive from the retained
`/tmp/caplab-native-exec-handoff-probe.py` and support, retaining their original
paths and SHA-256 values. Change only private supervisor integration and owned
artifact/unit paths: use the committed effective-configuration builder and
tracer observer, seal the configuration before guard release, and anchor that
file and configuration hash in the authenticated guard observation. Keep the
bootstrap and guard bytes, native installation, fixed prompt, scripted responses,
effective argv/environment, model and effort, quarantine policy, namespaces,
devices, procfs, descriptors and resource limits unchanged.

Verify derivation and canonical policy before launch. Compare the original
bootstrap construction with the committed configuration builder. Pin current
repository sources and explain differences from the prior diagnostic baseline.
Run synthetic controls demonstrating successful release only after both seals,
and refusal before release on configuration/observation sealing failure or bad
peer identity. These controls execute fixed Python producers only and do not
represent the native agent. Then authorize exactly one installed-native attempt
in a fresh owned unit/root. The allowance is consumed on launch, with no retry.

Use only fabricated credentials, sealed read-only inputs and an isolated local
HTTP fixture with two fixed scripted responses. No real credentials, external
endpoint, provider inference, model spend, historical research copy/admission/
rewrite/purge, tracker write, message, push, independent acceptance or study
promotion is authorized. Preserve unrelated `docs/designs/`, worktrees and
services. No repository runtime or test-source changes are selected here.

Retain the prior limits: 30-second native child, 45-second capture, 90-second
unit and 100-second outer capture; 256/512 MiB child/unit memory, zero swap,
128/192 PIDs; 300,000-byte native streams; 1 MiB/1,000-entry task capture;
8 MiB/1,000-entry native collection; 40 MiB/2,000-entry full-mount retention;
2 MiB host exec trace, 8 MiB native file limit, no cores; five 64 MiB tmpfs
mounts and the closed six-device profile. HTTP retains its 1 MiB wire/decoded
bound, 32 requests and two response POSTs. Stop on source drift, failed
preflight, unexplained refusal, timeout, quarantine or cleanup failure. Retain
partial results and diagnose without another native attempt. Stop only the
owned unit and verify it and its cgroup are absent.

After execution verify independent plan/configuration/guard/trace anchors,
recorded tracer custody, exact authenticated exec arguments/environment,
pre-exec cwd and installation-mount identities, task witness, native rollout,
tool result, final bytes, quarantine scans and cleanup. Preserve transport
errors and the strict final-message linker's existing refusal. A pre-exec cwd
observation does not prove cwd at all later execs; installed mount identity does
not prove the complete executable chain. Keep Binding completeness, native
capture completeness and study eligibility unestablished. Commit the verified
record locally; authorization expires at that commit.

No change would retain only retrospective configuration compatibility. Changing
the workload or transport simultaneously would obscure whether the new capture
integration itself works. This bounded adoption preserves that baseline while
testing the actual pre-release path.

## Preflight and release decision

The derivation preserves exact bootstrap and guard bytes and reproduces the
original effective command/environment/cwd at ports 1, 43,210 and 65,535. The
installed native manifest and canonical policy plan match the prior diagnostic.
Sixteen current source pins match committed `9fabc76`; the startup supervisor is
an explained difference from the prior baseline, adding the shared tracer and
optional launch-configuration checks. Other previously pinned sources match.

The five synthetic controls passed: successful execution after configuration
then observation seals; wrong parent, invalid port, injected configuration-seal
failure and injected observation-seal failure each prevent release and return
exit 7 with no stdout or task witness. The positive control verifies real kernel
tracer custody after exit and exact UTF-8 witness bytes. Two altered invocation
checks refuse. All controls restore the supervisor's descriptor set. Their
configuration is explicitly synthetic and is not a native launch profile.

The eight configuration tests passed, and Ruff F passed for the new private
support, probe, controls and verifier. Source inspection corrected a verifier
field name from `network` to the actual handoff `peer_checks` before execution.
This is a verifier correction, not a native result or runtime change.

Preflight source is `/tmp/caplab-native-launch-adoption-derive.py`; its result
is `preflight.json` under the same prefix. Controls are `controls.py`,
`controls/verification.json` and `controls.log`. Proceed with exactly one native
attempt using probe SHA-256
`41ab44b40501122dcddf03e659322a487a2bc46718dfaf108dac127f6fbd54d1`
and support SHA-256
`26be561cc2dff4c091d842cf75ced91a90149c658586472809505cdbd579ef15`.
The next launch consumes the allowance, whether it succeeds or fails.

## Native observation and verification

The single attempt completed under unit
`caplab-native-launch-adoption-16000b2204e34d839cd904d3ba2c578b.service`.
The outer process terminated with exit zero. The owned unit is not found and
its cgroup is absent; no retry or second native attempt occurred.

The guard authenticated PID 3586000 and sealed the effective configuration
before its observation and release. Configuration identity is
`eaa6ae5d83782dfb95d866e3d0e466ec9bd3f8e82af820fc9ad69eac128a49d6`.
The observation file SHA-256 is
`4f611acdb071cfba3b586a2557ec98398d8195fcb5d95c56e6dbf2cf2576a9f6`.
Both the initial bootstrap and guarded native peer have the shared kernel
tracer observation. Their retained consistency checks pass against the same
protected trace inode. The guard's pre-exec task identity agrees with the
mount handoff and captured task source; the installed native mount identity
was checked while the guard was paused and the installation manifest agrees
before and after execution.

The 1,649,604-byte trace has SHA-256
`9a363150351842d01b2d15279d0b3d4ea7b1fa107c554d1d9d81c04414cedc0e`.
The effective-configuration inspector matches `/toolbin/codex` at line 5 for
the authenticated PID, with exact argv/environment and a terminal exit zero.
Independent wrong configuration hash and wrong PID controls refuse. The local
configuration remains distinct from the canonical invocation. The checker
continues to report `cwd_source_linked: false`: a paused guard cwd observation
and fixed guard code do not independently observe cwd at every native exec.
Recorded tracer consistency also retains `observation_origin_verified: false`;
the caller's authenticated protocol, source pins and protected custody supply
its origin evidence rather than the observation authenticating itself.

The fixed native tool exchange completed: one command pair reports exit zero,
the rollout contains the exact fixed JavaScript call and matching output, and
the captured task file contains `CAPLAB café tool witness` plus newline. Its
26 UTF-8 bytes match the tool output. The completed agent message and final file
match the 40-byte fixed final response. Two response POSTs used bounded zstd
request decoding and received the fixed 200 responses. The fixture reports no
error, timeout, refresh or changed auth input. PID/memory max and OOM counters
remain zero, final child PID count is zero, and no post-capture group kill was
needed.

Five transport-error events precede the successful tool call and remain in
custody. The strict final-message linker still refuses with `retained stdout
lacks an unambiguous completed agent message`, caused by `native event stream
reports error`. No event was removed and no gate was relaxed. Root linkage
still reports `executed_invocation_bound: false`; native capture completeness
is unknown and study eligibility remains false.

Full-mount retention contains 918,045 bytes across 122 entries. The verifier
checked 111 retained files and 6,327 decoded hexadecimal trace strings against
the configured forbidden synthetic values without a match. This is bounded
known-value checking, not a general privacy proof. Native verification is
`/tmp/caplab-native-launch-adoption-verify.py`, with `verify.log` and
`result-verification.json` under the same prefix.

The current Plane read still contains 86 items, 12 open. CAPLAB-84 remains In
Progress. This execution verifies prospective configuration/tracer adoption in
the private scripted diagnostic; it does not integrate the complete native
executable chain into the product root linker, establish representative repair
measurements, or settle reviewer capability. Those are remaining work.

## Advisory review and remaining obligations

The release retrieval gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-0d1ada73339c72ed` and both evidence-backed Markdown packets
were read. Five typed records preserve authority, the integration gap, inspected
source, synthetic controls and native observations. The second evidence pass
names the actual signal at each gate in `gates.json`; it records broader
verification as provisional. Final packet is `pkt-a32bf2b23aea4104`, SHA-256
`a32bf2b23aea410463933d0e3e33f1fefc1cbf121a6772f9c5d74cab0d01d4ff`.
Versions are corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`, schema
`evidence-packet/3`.

All 25 missing obligations remain visible. Eighteen concern unchanged
record deduplication (3), ingest populations (4), asynchronous UI (4),
declarative references (3) and ranking (4); these are nonmaterial to this
private diagnostic adoption and those systems are not certified here. Three
external-capability obligations and evaluation/serving parity remain material
to provider integration and study readiness, which are withheld. Three
monitoring obligations are nonmaterial because no service or paging policy
changed. Applied guidance is repository-contract precedence, evidence before
intervention, separation of semantic and structural work, preservation of
existing behavior and authority-bounded action.

## Repository verification

No repository runtime or test source changed. The preceding full `make check`
result at `9fabc76` remains 1,359 tests with four skips; this turn reran the eight
configuration tests and five new real synthetic controls, then verified the
single installed-native diagnostic. Ruff F and diff checks pass. This is
verification of the declared integration, not independent acceptance.

## Final custody and disposition

Manifest `/tmp/caplab-native-launch-adoption-verification.json`, SHA-256
`27f488dd26e5c8cd55a6f8643226b1d50d22e000d696245f1788765e9086875d`,
retains 191 artifacts, 16 source identities and 15 embedded advisory scratch
files removed after exact-byte verification. Source, artifact, typed-evidence
provenance and embedded-byte hashes pass. Five citation observations classify
as valid packet citations. The preceding diagnostic's manifest, guard and trace
anchors remain unchanged. The owned unit and cgroup were checked absent again.

The new prospective adoption is verified within the declared private scripted
scope. All execution allowance is consumed. No repository runtime change,
model spend, tracker write, push, historical research effect or independent
acceptance occurred. The local record commit closes this authorization and
leaves the broader CAPLAB goal active.
