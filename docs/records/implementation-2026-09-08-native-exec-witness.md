# Verify native execution with supervisor-owned trace custody

Date: 2026-09-08. Baseline: `9b2bff2`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Initial bounded investigation authorization

The continuing goal and CAPLAB-84 require an exact native execution link.
Current Codex/Claude root linkers explicitly leave `executed_invocation_bound`
false. Authorize this record and one fixed local feasibility probe under
`/tmp/caplab-exec-witness-*`: supervisor-side `/usr/bin/strace` tracing
`execve` and `execveat` across a fresh Bubblewrap namespace running a fixed
Python sentinel. Use explicit PATH/LANG only, no network, no credentials,
read-only `/usr`, a private 1-MiB task tmpfs and an otherwise read-only root.
The trace stays in the supervisor's private host directory, which is not
mounted into the workload. The sentinel reports its namespace IDs and whether
that host trace path can be reached, then exits. It executes no native harness
and imports no historical evidence.

Bound the probe to five seconds and 100,000 combined stream bytes, with a
1-MiB trace file limit, five CPU seconds, 256-MiB address space and disabled
core files. Record argv/environment, tool hashes, trace bytes and hashes,
process result and source. Clean only its owned process group; preserve its
new partial custody on failure. No service, cgroup, account, model call,
historical campaign, tracker write, external message or push is authorized.
This allowance ends after that one probe. Any further execution or source
implementation requires a prospective amendment here.

## Observation and investigation decision

Live Plane still has the same 12 open roadmap items, including the current
CAPLAB-84 integration and representative-measurement requirements. Reads are
retained at `/tmp/caplab-roadmap-{current,states}-9b2bff2.json`. Existing native
startup source records the prepared plan and authenticates a blocked mount
handoff; neither alone proves that the requested `execve` succeeded.

The installed strace manual documents unabbreviated environments with `-v`
and hexadecimal strings with `-xx`. The [strace project](https://strace.io/)
identifies ptrace as its execution observation mechanism. A trace inside a
workload-writable mount would itself be exposed to modification, so test
whether the tracer can remain outside the workload namespace and retain its
own output. This is a feasibility observation, not a selected study instrument
or an inference of provider identity, native completeness or task correctness.
No change leaves the execution link missing; implementing a new ptrace engine
before testing the installed tracer adds unearned complexity.

## Feasibility result and implementation authorization

The one sentinel probe exited zero with complete streams. Its 3,720-byte
supervisor-owned trace contains successful Bubblewrap and Python `execve`
records. The sentinel observed distinct mount/PID namespaces and could not
reach the host trace path. Custody is
`/tmp/caplab-exec-witness-feasibility/`. A post-run display command initially
used `stdout.bin`; reading the captured receipt supplied the actual
`native.stdout` locator. This display error did not relaunch the probe or
invalidate its already sealed zero-exit result.

Authorize adding `src/caplab/exec_trace.py`, `tests/test_exec_trace.py`,
`docs/product/contracts/exec-trace-v1.md` and an optional fixed
`--trace-exec` mode in `scripts/probe_native_capture_startup.py`. Preserve both
existing diagnostic modes, native policy, capture profiles, public root-link
results and historical custody. The new inspector reads an independently
anchored, bounded strace hex-format file and requires exactly one successful
`execve` of the expected executable by the independently supplied handoff PID,
with exact argv and environment. Unsupported, abbreviated, malformed,
ambiguous or incomplete selected-PID exec records are refused. It verifies an
execution observation; it does not authenticate arbitrary trace provenance,
establish provider identity or make a complete Binding.

The optional startup mode places the tracer in the supervisor cgroup outside
the workload namespace, before the existing cgroup-join/Bubblewrap command.
It retains the trace directly in private supervisor custody and links its
hash to the authenticated mount-handoff PID and prepared invocation. Record
the tracer binary hash before and after execution. The tracer has a 1-MiB
soft file limit and a 64-MiB hard limit; trusted setup raises the native
process's soft limit to 64 MiB before release. Preserve the existing child
memory, swap, process, time and mount limits and all cleanup ownership.
Tracing changes the observation apparatus and must be named in a future
Binding; no equivalence to untraced runtime cost is claimed.

After focused parser tests pass, authorize exactly one invocation of the new
fixed mode, containing one offline startup each for the existing
`codex-terra-max` and `claude-fable-5-max` profiles. Freeze each plan, prompt,
session identity, installed harness manifest, tracer and launch command before
release. Use the existing exact startup prompt, empty tasks, loopback-only
network and empty credential/configuration homes. These are diagnostics on
already exposed startup behavior, not repairs, treatment arms or replacements
for failed attempts. No model-serving endpoint or credential is exposed.
The existing bounds are 20 seconds and 200,000 stream bytes per native startup;
256-MiB child memory, no swap, 64 tasks; 512-MiB outer memory, no swap,
128 tasks, 75-second unit limit and 85-second outer capture. Preserve all five
64-MiB writable mounts and two usable device nodes. Retain selected native
surfaces and full mount inventories under existing quotas, plus each bounded
host trace. Stop on changed source, failed handoff/containment, quota failure
or unsupported trace evidence. Failed startup and partial custody remain
observations; there is no retry allowance.

Run focused tests, one retained fixed native probe and `make check`. New
synthetic trace bytes may be created for refusal tests; they are never native
evidence. Retain new observations and failures under
`/tmp/caplab-exec-witness-*`. Consolidate advisory scratch before removing only
its named files. No historical import/admission, tracker writes, messages,
push, model spend, ranking or independent acceptance. Preserve `docs/designs/`
and sibling worktrees. Commit only these five named files locally. This
authorization expires at that commit; wider effects need a new decision.

## Implementation and native observations

Added the bounded [execution-trace inspector](../product/contracts/exec-trace-v1.md)
and the optional supervisor-side trace mode. Six focused tests pass. They
exercise exact Unicode/quoted/newline argv, environment order and empty values,
cross-PID interleaving and resumed calls, failed execution, wrong identity and
invocation, duplicate success, abbreviation, malformed/duplicate environments,
unsupported records, incomplete calls, byte/hash limits and symlink refusal.
The descriptor count remains unchanged across refusals. These generated syscall
strings are parser tests, not native execution evidence.

The one authorized two-startup diagnostic completed under unit
`caplab-native-startup-646c1581dab14ca9a767645eb46ecb23.service`.
Both actual handoff PIDs have exactly one successful `/toolbin/<harness>`
execve matching the prepared argv and entire environment. The launch placed
the tracer in the supervisor; pre-release checks observed distinct
supervisor/task PID and mount namespaces, and neither peer could reach the
host trace path. Each trace stayed below the 1-MiB file limit. Task/native collection
and retained-mount verification succeeded after namespace exit.

| Native startup | Matching host PID / trace line | Trace bytes / SHA-256 | Subsequent process outcome |
|---|---|---|---|
| Codex, `codex-terra-max` | `1137497` / `4` | 364,663 / `99829a8e27c88a64b1c2ed15036de3f0cd2948ab31dabf8f3aa8e5b9bbcefa98` | Offline timeout, exit -9, incomplete streams, missing final message; 33,827 selected native bytes retained |
| Claude, `claude-fable-5-max` | `1142294` / `4` | 73,800 / `c8a6db82dc0ca78a8db01f183dd80d0d77eca1eae1f321a3b12467e5f33b8ba3` | Login failure, exit 1, complete streams; 31,536 selected native bytes retained |

Both empty tasks remained unchanged. No authentication or remote model call
occurred. The matched Codex entrypoint is the installed npm harness entrypoint;
this check does not independently attest its complete interpreter/worker
execution chain. Successful entrypoint execution is distinct from a successful
model response or complete native capture. Existing public root-link results
remain unchanged; the new trace result separately records execution agreement
while leaving provenance authentication to its caller.

Custody is `/tmp/caplab-exec-witness-native/`; raw outer run output is
`/tmp/caplab-exec-witness-native-run.log`. The native `observations.json` hash is
`4ac2f9a1b4871611d522fa42c59f323d2bb938c42f879bd9057e3a00755e69ae`;
`verification.json` hash is
`54100a8ba9ca9263b0f172f3a42d694d81240cc11f7ad98cace0c6b31d5925ac`.
The exact unit was already unloaded when cleanup called stop. Fresh readback
confirmed `LoadState=not-found` and absence of its delegated cgroup; the
closure is retained in `/tmp/caplab-exec-witness-closure.json`. No retries,
other service operations or historical evidence effects occurred.

## Advisory provenance and limits

The retrieval-state gate passed for the Pincite release at
`/home/halbritt/.local/share/pincite/release` at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
The question was how a supervisor-side execution trace outside the workload
namespace should verify prepared native argv and environment without
overstating native identity or completeness. Initial packet
`pkt-71d163b3e8e690ed` was followed by one typed-evidence pass for authority,
contracts, source and the sentinel probe. Final packet `pkt-19698b40b81e9bfd`
has content SHA-256
`19698b40b81e9bfda08b06c663c54ac905f6359585f24fd292e9fa4558351a2f`.

Applied repository precedence, evidence before intervention, structured cleanup
and bounded authority; their four citations passed packet classification.
The 28 remaining generic obligations are individually retained as nonmaterial:
ten concern Python/toolchain conformance without a language or dependency
migration; four concern external configuration without a configuration-service
or fleet-promotion change; fourteen concern performance objectives, metrics or
representative baselines without an optimization, cost estimate or untraced
equivalence claim. The actual trace format, resource bounds and runtime
observations are explicit. No material unresolved obligation was used to
support a stronger execution or measurement claim.

Reopen before supporting another trace format, exec mechanism, authenticated
environment, executable resolution rule or execution apparatus. Trace fidelity
and protection must be validated for the eventual repair workload. Current
successes do not establish complete containment, a complete Binding, provider
identity, repair quality, representative capture overhead, blinding, coding
accuracy, study admission or independent acceptance.

## Final verification and custody

`make check` passed 1,240 tests in 154.668 seconds with four skips; log
`/tmp/caplab-exec-witness-make-check.log`. The six focused parser tests passed
in 0.007 seconds, recorded in `/tmp/caplab-exec-witness-focused-final.log`.
Ruff `F` checks, Python syntax parsing of the three affected Python files,
the three relative document links and `git diff --check` passed. Documentation
was checked against the actual parser, launch mode and retained observations.

Private consolidated verification is
`/tmp/caplab-exec-witness-verification.json`, SHA-256
`2a460ba697b4e92176b87935c11b14661fa311e5dbc038fd94fc2cea1cba1982`.
It hashes 167 retained artifacts and the implementation/contract files, and
embeds the exact bytes/hashes of both advisory packets, four evidence records,
citation observations/classification and all 28 nonmaterial obligation
classifications. Only those eleven consolidated scratch files were removed
after byte verification. The native traces, sentinel, process receipts,
partial native startup outputs, logs, roadmap snapshots and closure remain.
The authority evidence record embeds the pre-implementation record's hash and
locator; this committed record preserves the authorization text and result.

The five-file local commit completes this bounded implementation and
verification. It does not complete CAPLAB-84 or the wider roadmap. No tracker
state or human-owned judgment changed, and unrelated `docs/designs/` remains
outside scope.
