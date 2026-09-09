# Verify guarded capture around a native error response

## Decision and authorization

At baseline `71419f8`, fabricated producers verify quarantine through process,
task, selected native and full-mount capture. Installed-native diagnostics
exercise error routing but do not adopt those guards. The mount handoff helper
also seals peer metadata without a policy. Under ADR 0026 and the continuing
improvement request, select a bounded integration diagnostic before any real
credential administration or representative repair attempt.

Authorize an optional `quarantine_factory` on `receive_mount` in
`scripts/probe_cgroup_resource_limits.py`, checking the handoff receipt and
planned paths before publication or child release. Preserve default behavior,
descriptor ownership, source checks and the before-snapshot handshake. Add
focused verification and run the relevant existing tests and full suite.

Authorize creating one private probe and verifier under
`/tmp/caplab-native-quarantine-*`. The new probe may derive source from
`/tmp/caplab-response-auth-http11-probe.py`, recorded by source commit `f1d0253`
in `docs/records/verification-2026-09-09-native-response-auth-routing.md`.
Preserve that original path and its content hash; do not execute, overwrite,
relabel or copy its old experimental outputs. Reuse current CAPLAB capture,
preparation, handoff, mount retention and integrity-checking components.

Permit exactly two new installed Codex diagnostic launches, sequentially, using
the currently inventoried installation at
`/home/halbritt/.npm-global/lib/node_modules/@openai/codex`. Enforce the native
contract for `codex-terra-max`, model `gpt-5.6-terra`, effort `max`, and the
canonical maximal-capture invocation. Freeze source/installation hashes and
the complete plan before launch. The diagnostic prompt is: "Authentication
diagnostic only. Reply READY without using tools or changing files."

Only the previously characterized local `chatgpt_base_url`, `openai_base_url`,
update-check disabling and local refresh-URL override may augment that plan.
These are explicitly named diagnostic configuration changes, not comparative
study subjects. Both cases use newly fabricated external-token auth caches,
with an empty refresh token, delivered via a sealed descriptor to a read-only
mount. No real credential, operator config/home, external network interface,
successful model response or provider service is permitted.

The first case receives a fixed local HTTP/1.1 401 error. Only if its guarded
capture completes and integrity checks pass may the second receive a 401 error
whose message is a newly fabricated forbidden value supplied through the
read-only fixture input. The purpose is to observe whether the native output
echoes that value and, if so, whether capture refuses it before retention.
Failure to echo is an inconclusive stimulus, not successful quarantine proof.

Each case uses an isolated Bubblewrap network namespace containing only
loopback. The trusted bootstrap may bring loopback up with CAP_NET_ADMIN, then
drop effective/permitted/inheritable capabilities and set NoNewPrivs before
launching native code. Use five 64-MiB writable tmpfs mounts, read-only system,
harness, fixture-input and control-socket mounts, and usable null/urandom
devices. Receive and verify all five descriptors before releasing native
execution. Bound local requests to 64 and each body to 1 MiB; native execution
to 20 seconds, captured child execution to 30 seconds and 300,000 stream bytes.
The owned systemd unit is bounded to 100 seconds, 512 MiB, zero swap and 128
tasks; each case uses a child cgroup with 256 MiB and 64 tasks. Bound task,
native and full-mount capture to the existing declared allowances. Quiesce the
child before after/native/full-mount collection and clean up only owned groups.

Use the same exact-value factory for process, task, native, handoff and retained
mount outputs and the probe's own JSON publications. It owns only fabricated
values; do not infer real-credential policy from it. Guarded refusal may leave
safe prefixes and earlier component receipts. Record missing completion
receipts explicitly; never retry into the same root, return redacted substitutes
or claim a complete aggregate after a guard error. Inspect all retained output
for forbidden raw values and verify exact independent custody on the safe case.

Allow local synthetic helper checks without installed-native launches. Stop
the native sequence on unexplained failure, changed source/installation,
unexpected network, quota/timeout, or failed safe-case verification. Preserve
all attempt and failure custody. Do not renew these two launch allowances
implicitly. Authorization expires at the verified local commit or after a
failed native sequence. No provider/model spend, real credential read/refresh,
historical evidence processing beyond the named source derivation, tracker
write, outbound message, independent acceptance or roadmap completion.
Preserve unrelated files, worktrees and services.

## Pre-execution checks

Three synthetic handoff tests passed in 0.299 seconds; twenty adjacent capture
tests passed in 6.287 seconds. The initial helper test exposed an incorrect
normal exit from an unfinished recorder. The probe now lets guard exceptions
cross the recorder context before classifying them, preserving cleanup and
missing receipts. Ruff and diff checks passed. The full suite is running.

The fixed probe is `/tmp/caplab-native-quarantine-probe.py`, SHA-256
`c7b5a264cd34d32bc91e939d182f7c6f117a8a3ec2ac9a1e149ef8945b7c3280`. Its source derivation records the original
`/tmp/caplab-response-auth-http11-probe.py` with SHA-256
`51c28c1d43ea69b14004a3dea32728359d7216cbc672d5fff0ecfba84e89bd4c`. The new source compiles, and the bootstrap's
capability drop and descriptor handshake precede its sole native launch call.

The validated Doctrine release gate is unchanged from the preceding capture
record. Initial packet `pkt-74ad54763074d88a` and first typed pass
`pkt-fa0383609e4b4911` support this scoped implementation. The 21 remaining
obligations concern performance objectives, metrics and representative baselines
(14), full toolchain/platform conformance (5), and workload/task-size profiling
for concurrency optimization (2). All are nonmaterial here: no performance,
platform qualification or concurrency improvement is claimed. Existing bounded
threads remain responsible for blocking I/O and handshake progress.

The exact native plan and installation inventory will be sealed in the fresh
`/tmp/caplab-native-quarantine-run/selection.json` before any native launch.
Only the two cases in this authorization may run.

## Execution and independent verification

Both authorized cases ran in
`caplab-native-quarantine-ae2b0a4fc30543c1ab1f8057412963cf.service`.
The private capture root is `/tmp/caplab-native-quarantine-run/`. The sealed
installation inventory matched before and after execution and during a later
independent verification. All frozen CAPLAB source/test hashes also matched.

| Case | Native/process observation | Capture result |
| --- | --- | --- |
| Ordinary local 401 | The native child returned 1; the diagnostic wrapper returned 0. The fixture recorded 56 requests, including 39 response-path 401s bearing the fabricated access token, no refresh request, no fixture error and no native timeout. | Process, task, selected native files and all five writable mounts completed their capture paths. Independent integrity/linkage/accounting checks passed. Full-mount retention contained 3,381,587 bytes in 136 entries. |
| Local 401 with forbidden message | Process quarantine raised the expected refusal. The native terminal outcome is unavailable after capture terminated the process path; do not infer a completed native failure from the first case. | No process or task completion receipt was published. Guarded selected-native and full-mount collection retained safe partial diagnostic state afterward: 2,778,953 full-mount bytes in 122 entries. Those component receipts do not complete the aggregate attempt. |

The echo case retained 706 stdout bytes and zero stderr bytes; these are safe
prefixes, not complete-stream byte counts. The gate does not record which of
six configured values matched. Attribution of that refusal to the changed
error message is therefore an inference from the paired stimulus, not a
direct per-value observation. The probe establishes native-path quarantine
and incomplete-capture handling without preserving the rejected raw value.
Per-value diagnostic attribution would need separately scoped instrumentation;
it must not be fabricated from the absence of retained secret bytes.

`/tmp/caplab-native-quarantine-verify.py` independently rechecks the safe task,
native and full-mount receipts; the echo native/full-mount component receipts;
the missing echo process/task receipts; the exact shared allowances and totals;
installation/source hashes; and every retained filename and file's raw bytes.
Its result, `/tmp/caplab-native-quarantine-independent.json`, covers 213 retained
files and finds none of the six configured raw values. This does not cover
transformed secrets, other values, original fixture inputs or memory erasure.

The unit's cleanup receipt and a subsequent live `systemctl --user show` both
report `not-found`; its delegated cgroup is absent. The stop command returned 5
because the completed collected unit was already unloaded; the separate live
read and absent cgroup establish cleanup. No other service was stopped.

The handoff's three new tests use actual Bubblewrap descriptors. Safe non-ASCII
peer metadata round-trips before release. Forbidden peer metadata or a forbidden
receipt name prevents handoff publication and release, leaves no final task
receipt, and returns descriptor counts to baseline. The synthetic omission
control at `/tmp/caplab-native-quarantine-handoff-omission.py` disables only the
handoff factory: both negative tests then detect the missing refusal while the
safe case still passes. The two failures in its retained log are intentional
control observations, not failures of the implemented helper.

`make check` passed: 1,300 tests in 170.152 seconds, with four skips. The new
handoff tests ran without skips. Ruff and `git diff --check` passed. No source
or test change followed that full run. The earlier fixture-lifecycle error and
the omission-control log remain retained alongside successful check logs.

The two native launch allowances are consumed. No real credentials, external
provider, successful model response or model spend occurred. Neither the
supervisor's attempt record nor its self-reported child command is an
independent host exec trace, provider authentication or full native identity
attestation. The local endpoint overrides remain diagnostic configuration;
this is not an eligible comparative subject or representative repair capture.

CAPLAB-84 still requires a selected administration and integrated supervisor
for representative repair work, followed by separately authorized measurements
of legibility, resource use, blinding and coding reliability. The current
diagnostic confirms that real native failure output can pass through guarded
custody or be refused without inventing a completed attempt. It does not close
that roadmap item or authorize a subsequent native run.

## Advisory provenance and limits

The release gate verified fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Two typed evidence passes retain
authority, local contracts, current source, synthetic checks and the scoped
native observations. Final packet `pkt-589e9ff1256a9bd8`, retriever
`retriever-ec995ecdd083b2c8`, has content hash
`589e9ff1256a9bd8d45460de14dc910c26552ea749c720e6e4511c647f5bd160`.

The 21 unmet obligations remain nonmaterial to the bounded capture claim:

| Group | Unmet requirements | Reason |
| --- | --- | --- |
| Performance objective (5) | Workload/operation; inspection authority/objective owner; environment/distribution/scale/concurrency/population; metric/target; tradeoff owner | No performance objective is selected. |
| Metric semantics (5) | Instrumentation access; definition/configuration; overhead/data-loss limits; runtime sanity check; unit/window/population/sampling | Retained-byte counts describe these files; they do not estimate representative cost or overhead. |
| Representative baseline (4) | Measured-workload correctness; exact benchmark/environment versions; resource/cache state; repeated measurements/variance | The two error cases are diagnostic, with no performance comparison or repair-population extrapolation. |
| Toolchain conformance (5) | CI/build matrix; formatter/static configuration; Python/dependency matrix; formatter/linter/type-checker configuration; complete toolchain inspection | No platform or toolchain change/qualification is claimed. Local interpreter, source and executed checks bound verification. |
| Concurrency profiling (2) | Task-size distribution; workload profile | Existing bounded I/O threads are reused; no concurrency optimization is selected. |

Six applied concepts have valid packet citations: authority-bounded action,
repository-contract precedence, structured cleanup, text/bytes boundaries,
evidence before intervention and preservation by default. They support guarding
the current handoff publisher, allowing errors to cross resource-owning contexts,
preserving raw safe bytes and requiring the first control before the second
native case. They do not supply study authority or independent acceptance.

## Retained provenance and local completion

The private manifest `/tmp/caplab-native-quarantine-verification.json` has
SHA-256 `e058c83a88940698dea46a41b6c4755f21aa0fc6a9280973a54cc5eec0163a42`.
It retains 30 supporting artifact entries, the hashes of 213 capture files,
frozen source hashes, suite results and the consumed two-launch count. Thirteen
temporary advisory files were embedded byte-for-byte and checked before those
exact scratch paths were removed. The native capture root, source-derived
probe, independent verifier, original authorization snapshot, source derivation,
success/failure/control logs and read-only ticket snapshots remain private.

Commit the handoff helper, its three tests and this record. Preserve unrelated
`docs/designs/`, the detached worktree and all historical capture roots. The
local handoff change and two diagnostic observations are verified within the
limits above; the active improvement goal remains incomplete.
