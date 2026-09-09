# Link a paused native entrypoint to a supervisor-owned exec trace

Baseline `b64bb3a`. Primary agent under ADR 0026 and the continuing CAPLAB goal.
The previous fixed native exchange completed, but its filtered trace omitted
successful exec calls and root linkage still reports no executed invocation
binding. The existing exec-trace contract requires an independently identified
PID, an expected invocation and trace custody unavailable to the workload.

## Decision and prospective authorization

Authorize this record and private implementation, synthetic control and capture
artifacts under `/tmp/caplab-native-exec-handoff-*`. Add a fixed Python exec
guard immediately before the native entrypoint. It connects through a separately
bound Unix sequenced-packet socket, sends only the local fixture port, waits for
release, closes that socket and execs the exact native command with its inherited
environment. No model or arbitrary command chooses the guard program.

The supervisor authenticates SO_PEERCRED, verifies the guard is a child of the
initial authenticated bootstrap, in its exact cgroup and user/PID/mount/network
namespaces, with the captured task directory as cwd and no controlling terminal
or retained privileges. Check the mounted installation root against the pinned
host installation. Reconstruct expected argv/environment independently from
the prepared plan and the bounded local port, and seal this pre-exec observation
before release. Retain source and namespace/cgroup/task/installation identities.

Place pinned strace in the supervisor cgroup outside the workload namespaces,
using numeric PIDs, `-f -v -xx -s 65536 -e trace=execve,execveat`, and a private
host trace path checked absent inside the workload. Limit the tracer file to
2 MiB with an 8-MiB hard ceiling; the existing bootstrap restores the native
8-MiB file limit. Remove the old inner filtered tracer to avoid competing ptrace
owners. This changes observation apparatus and adds a paused wrapper, not the
authorized native command or its workspace-write sandbox. Do not infer timing
or capacity equivalence to earlier probes.

First run fixed synthetic controls with an empty task, the existing bounded
tmpfs/procfs/device handoff and a fixed UTF-8 witness program. Require the
authenticated guard PID to match exactly one successful exec with expected
argv/environment in isolated host custody. Require wrong parent, malformed
port and wrong expected argv/environment to refuse release or verification,
with owned cleanup. Synthetic failure permits bounded diagnosis and correction,
not a native launch. Bind no host PTY tree or operator credentials.

After these controls pass, permit exactly one installed Codex 0.153.4 local
scripted exchange derived from `/tmp/caplab-native-basic-devices-probe.py`,
SHA-256 `13cc44a70b64cb2046865f57f9e7dd0d20cecfe58535ec2199aba8fb93b7e0b1`.
Preserve the exact fixed responses, command, model gpt-5.6-terra/max selection,
read-only fabricated auth, private loopback, device/procfs checks, five 64-MiB
tmpfs mounts, no core/swap, 256/512-MiB child/outer memory, 128/192 PID limits,
30/45/90/100-second time limits, stream/task/native/full-mount limits, and
request/body/POST bounds. Freeze derivation and all source/installation/tracer/
decoder pins before launch. Stop on first fixture error; no native retry.

Require the same fixed command, task and final-byte observations as the preceding
diagnostic, plus the authenticated entrypoint exec match. Preserve the strict
final-link refusal for recovery errors and all existing root-link ceilings.
An interpreted entrypoint does not attest its downstream executable chain or
provider/model identity. Inspect raw and hex-decoded exec arguments for configured
fabricated forbidden values before successful closeout; raw synthetic trace
custody may remain on refusal. No real-credential privacy claim follows.

Close every listener and descriptor, reap only owned processes, and verify exact
unit/cgroup cleanup on either outcome. Preserve failed control/native custody.
No repository runtime change, tracker write, message, push, historical research
evidence effect, study adoption or independent acceptance. Preserve unrelated
`docs/designs/`, worktrees and services. Commit the resulting record locally;
authorization expires there. Native execution awaits passing synthetic preflight.

Selecting a PID from matching syscall text alone does not satisfy independent
identification. Tracing inside the workload does not protect trace custody.
Disabling the native sandbox or dropping expected environment comparison would
weaken the required evidence. The paused guard supplies the missing process
identity while reusing the existing exact exec inspector.

## Synthetic verification and native preflight

Three real isolated controls passed: the authenticated guard's exact exec
matched, while a wrong parent and out-of-range port prevented release. Wrong
expected command and environment independently refused exec verification.
The successful control retained its exact UTF-8 witness; both rejected controls
exited without running it. No installed native agent executed in these controls.
The existing exec inspector's six tests passed, as did Ruff F for the support,
derivation and derived probe. Control receipts are retained under
`/tmp/caplab-native-exec-handoff-controls/`.

Derivation initially refused before writing a probe: the script-hash suffix
occurs in both selection and intent, rather than once. The corrected derivation
adds the support hash to both records. The original derivation and failure
description remain private artifacts. No native allowance was consumed.

The current native policy builder produces exactly the prior prepared plan.
Executing only the original bootstrap's four construction assignments confirms
the independent expected-command/environment constructor. All 13 runtime
source pins, the full native installation, fixed decoder and tracer match.
The derived probe's SHA-256 is
`4534752317d62774f648ee0178ee8609926e36efa06fc35545abda005dad66a9`;
support SHA-256 is
`db594fc7df96bc38d64eb834203cfd6005f5986d620f13e1831c34563bf0b58f`.
Preflight is `/tmp/caplab-native-exec-handoff-preflight.json`. The initial
Doctrine packet `pkt-eb7e9322c4391ccc` was read; repository authority governs
the bounded experiment and broader integration claims remain withheld.

Proceed with the single authorized installed-native diagnostic. The next launch
consumes its allowance; failure permits inspection and closeout, not retry.

## Observed native execution

The one run completed under unit
`caplab-native-exec-handoff-014370edb7be41d4ade9a7cc3c9dddb1.service`.
The supervisor authenticated guard PID 3464336, parent 3464334, before release.
Its parent, cgroup, namespaces, task-directory identity, installation mount,
zero capabilities, NoNewPrivs and absence of a controlling terminal passed the
live checks. The actual tracer remained in supervisor namespaces and cgroup;
its open trace descriptor matched the private host file, unavailable inside
the workload.

The existing exec inspector identifies exactly one successful `/toolbin/codex`
exec for that independently authenticated PID, at trace line 5, with exactly
the reconstructed argv and environment. The host trace is 1,648,830 bytes,
SHA-256 `5aa70e5d6f6fe69f5196f50a67e3a076ceb119fe9a0e36fea387b517b6f342fc`.
It remains below the 2-MiB ceiling. The pre-release observation hash is
`241cda8a4303d6e2a06bbcd0277611a86bc71ebca22665167a5a8a8de6b1a2d5`.
The authenticated PID later exits zero. This establishes this native
entrypoint's invocation agreement; it does not attest the interpreted
entrypoint's downstream executable chain or provider/model identity.

The native stdout has one completed command pair with exit zero and the exact
UTF-8 witness. Retained rollout output agrees, and `capture-witness.txt` contains
the same 26 bytes. The completed message and final file agree on the fixed
40-byte final text. Both scripted response POSTs returned 200 after bounded
zstd decoding. The stream ends with turn.completed; native return is zero,
without timeout, fixture error or auth refresh. Fabricated auth is unchanged.

Task, native collection and all five retained-mount custody checks pass.
Retained mounts contain 918,046 bytes and 122 entries. Child PID-limit and
memory max/OOM/kill counters remain zero, final PID count is zero, and no forced
post-capture group kill or quarantine refusal occurred. All 110 retained files
were checked for configured raw forbidden values; 6,327 hexadecimal strings
from the host trace were also decoded and checked, with no configured forbidden
value found. This does not establish privacy for real credentials.

The first post-execution verifier run passed. All source, support, installation,
decoder and tracer hashes still match. The owned unit reports not-found and
its cgroup is absent. The native allowance is consumed. Verification source
and result are `/tmp/caplab-native-exec-handoff-verify.py` and
`/tmp/caplab-native-exec-handoff-result-verification.json`.

## Remaining measurement boundaries

Four WebSocket retry errors and one fallback error item remain in the stream.
The strict final linker still refuses with `retained stdout lacks an unambiguous
completed agent message`, caused by `native event stream reports error`.
The verifier requires that refusal and checks exact final bytes separately.
No failed criterion or retained event was changed.

The reusable exec inspector deliberately leaves its own trace-provenance and
binding-completeness flags false; the private caller records its authenticated
process and tracer-custody evidence separately. Public root linkage still
reports `executed_invocation_bound: false`, and native capture completeness is
unknown. The next integration work must carry authenticated entrypoint evidence
into a reusable capture contract while preserving downstream-chain limits.
Final-byte identity and failure-free-turn eligibility also remain distinct
predicates. Representative repair measurements, study readiness and independent
acceptance are not established by this local scripted diagnostic.

## Advisory and final verification

The Doctrine retrieval gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`
at release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Five typed evidence
records produced final packet `pkt-b5de9e0008b4b2dd`, SHA-256
`b5de9e0008b4b2ddbcf626739130d73c20ec06351ebf5b57bb7663e8e65014cc`.
Both initial and final Markdown packets were read. Versions are corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, schema `evidence-packet/3`.

All 25 remaining obligations are retained. Eighteen concern unchanged
deduplication (3), ingest populations (4), asynchronous UI (4), declarative
references (3) and ranking (4); they are nonmaterial to this fixed exec
diagnostic and those product paths are not certified here. Three external
capability obligations and one evaluation/serving-parity obligation are
material to broader provider integration and study readiness; those claims
remain withheld. Three monitoring obligations are nonmaterial because no
service or paging policy changed.

Applied guidance is repository-contract precedence, evidence before
intervention, separation of semantic and structural work, default-behavior
preservation and authority-bounded action. The private verifier's cgroup
comparison was simplified to the one observed snapshot shape; it passed again
without repeating native execution. Ruff F passed. No repository runtime or
test source changed, so the preceding full-suite result of 1,343 tests with
four skips remains applicable. The six exec-inspector tests and the new real
controls directly cover the mechanism used here. These checks supply technical
verification, not independent acceptance or reviewer capability evidence.

## Final custody

Private manifest `/tmp/caplab-native-exec-handoff-verification.json`, SHA-256
`b7519b0210884d7b1c6634cb30f1796a37ac50fe95c3d9826d364eed1d28cac5`,
retains 162 artifact hashes, 13 preflight source identities, three additional
inspected-source identities and 11 embedded advisory scratch files. Artifact,
source, evidence-provenance and embedded-byte hashes passed before the exact
scratch files were removed. Five citation observations classified as valid
packet citations. A fresh read confirmed the exact owned unit and cgroup were
absent before sealing.

One native allowance was consumed. No real credentials, external model spend,
tracker writes, messages, pushes or historical research evidence effects
occurred. This record-only local commit closes this diagnostic authorization;
the continuing CAPLAB goal and representative repair shakedown remain open.
