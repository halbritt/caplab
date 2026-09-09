# Trace native code-mode dispatch before another diagnostic

Baseline `3eab46e`. Primary agent under the continuing CAPLAB objective and
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

Authorize bounded inspection of the installed Codex 0.153.4 binary and its
published source at tag `rust-v0.153.4`, plus this record and private artifacts
under `/tmp/caplab-native-dispatch-*`. Resolve and retain the source commit,
original URL/path and content hash. Fetch at most eight relevant source files,
at most 2 MiB each, to trace response parsing, output-item dispatch and code-mode
execution. Preserve installed source and predecessor probes/custody. Published
source is implementation evidence, not proof of byte-equivalent installed code.
No native task launch is authorized until an evidence-grounded prospective
amendment names the precise diagnostic change and verification criteria.

The preceding native attempt retained a custom call but returned no tool output,
made no task change and produced no final message, despite exit zero. Distinguish
parsing, retention, dispatch, execution and native completion. Do not change
model, harness, effort or native configuration to compensate for an unverified
fixture assumption. No real credentials, provider/model spend, historical
research effects, tracker writes, messages, push or other worktree changes.
Preserve unrelated `docs/designs/` and services. Authority expires at local commit.

## Source observation and tracing authorization

Tag `rust-v0.153.4` resolved to commit
`3d2ee51ca2d5db578f328aa75e20aa22c0197c9a`. Seven source files and bounded
GitHub directory listings are retained in `/tmp/caplab-native-dispatch-source/`.
An attempted `core/src/codex.rs` fetch returned 404; current tag source uses
`core/src/session/turn.rs`. The installed binary contains the older codex module
path, so tag source cannot be treated as exact installed-build attestation.

The published router maps a custom call with namespace/name/input/call ID to a
tool call. `stream_events_utils::handle_output_item_done` logs and retains it,
sets follow-up and queues a tool future. The published turn loop drains those
futures after response completion. Its custom-call schema requires no channel
or recipient field. These sources therefore do not justify guessing extra
response metadata. The observed retention-without-result remains unexplained.

Authorize exactly one new private diagnostic derived from the unchanged
code-mode probe under `/tmp/caplab-native-dispatch-*`, unit
`caplab-native-dispatch-<32 hex>.service`. Change only the native environment's
RUST_LOG filter to
`codex_core::stream_events_utils=trace,codex_core::tools::router=trace,codex_core::tools::code_mode=trace,codex_core::codex=debug`.
Do not enable HTTP/auth wire logging. Keep the exact scripted responses, fixed
JavaScript and command, native/model/effort, task input, fabricated auth and
all previous isolation, memory/task/stream/file/entry/deadline/cleanup bounds.
The diagnostic goal is an observed dispatch trace, not presumed successful
execution. If the exchange is incomplete, preserve and verify failure custody;
do not relabel a zero native exit or a trace statement as tool execution.

Freeze source/installation/library and exact response hashes before launch.
Check the derived bootstrap differs only in the logging environment; retain
native stderr and native log files through existing quarantine and byte limits.
Stop on guard refusal, quota, first fixture error, deadline or native exit.
Accept no more than two response POSTs. Verify actual tool/task effects and
source/install/library/capture integrity, exact unit removal and cgroup absence.
This consumes one new diagnostic allowance; no second launch under this scope.
No configuration or response-semantic repair is authorized by this amendment.

The derivation check confirms the bootstrap differs only in the RUST_LOG value;
all scripted-response code is unchanged from the previously preflighted probe.
Source and decoder pins matched; Ruff F passed. Final probe hash:
`1f248ecdc86908dc1b5c6e135dbedaf7e8c2d4bf15766aed817e46a9a485d4d3`.
Proceed with the single tracing diagnostic.

## Traced failure and PID-capacity experiment

The tracing run used
`caplab-native-dispatch-673c4e39ae2041798fd4817ad9575251.service`.
Native stderr directly records `handle_output_item_done` dispatching the fixed
exec call, followed by `code-mode host exited with status signal: 5 (SIGTRAP)`.
The rollout contains the exact call and a matching custom-call error output.
Native return code is zero, but no task write/final message/second POST exists.
The wrapper fails its completion requirement. The child cgroup's pids.events
max counter increased from zero to one under pids.max 64; memory max/oom/oom_kill
counters stayed zero. The current host reports 12 CPUs and 12 allowed CPUs.
This supports PID exhaustion as a candidate cause, without proving causality.

The verifier initially inherited an assertion that no custom output existed;
this run instead retained the explicit error output. The verifier was corrected
to require that exact error, preserving the failed observation and unchanged
native source. Process/task/native/mount integrity, root/pair parsing and
source/install/library pins passed. Full-mount custody has 3,429,291 bytes in
138 entries; 116 retained files contain no raw configured synthetic forbidden
values. The exact unit and cgroup are absent. Source and verification:
`/tmp/caplab-native-dispatch-failure-verification.json`.

Under ADR 0026, authorize one separate PID-capacity diagnostic derived from the
unchanged tracing probe, under `/tmp/caplab-native-pid-capacity-*` and unit
`caplab-native-pid-capacity-<32 hex>.service`. Change only child pids.max from
64 to 128 and outer TasksMax from 128 to 192, including their verification
expectations. Preserve the same 256-MiB child/512-MiB outer memory, no swap,
12-CPU visibility, native configuration, tracing filter, response bytes,
prompt, tool command and every other preceding namespace/device/mount/time/
stream/file/entry/request/cleanup limit. This changes the diagnostic resource
administration and is not an equivalent study Binding or a representative
capacity estimate. Do not alter model identity or infer model capability.

Before launch, verify exact derivation differences, original source/library
pins and unchanged bootstrap/response bytes. Require normal native completion,
the two-response exchange, actual witness file, tool output and final linkage
for success. Inspect PID/memory event deltas on either outcome. A successful
result supports the bounded capacity hypothesis; a failure remains evidence
and does not justify unlimited resources. Preserve all partial capture and
verify exact owned cleanup. Exactly one launch; no automatic further attempt.

The PID derivation check passed: only the two PID limits, their expected values
and owned artifact/unit prefix differ. Bootstrap and response bytes are exact;
source/library pins and Ruff F passed. Probe hash:
`7d150985959fbf984811717979af925de10131f9cbd6f3c27cacd69ad9cd2add`.
Proceed with the single capacity diagnostic.

## Capacity observation and bounded syscall trace

The 128-task child run recorded no PID-limit event and no memory limit/OOM event.
The fixed call reached native dispatch, but still produced no task write, final
message or second POST. Its native process exited zero. The SIGTRAP error is
absent from this run's selected trace; that absence alone does not prove host
health. No successful execution is claimed. A retained native state WAL in the
preceding capture is exactly 2,097,152 bytes, equal to the inherited per-file
RLIMIT_FSIZE. This is a second candidate boundary, not a diagnosis.

Authorize one separate observational derivative of the 128-task probe under
`/tmp/caplab-native-syscall-*`, unit `caplab-native-syscall-<32 hex>.service`.
Prefix only the owned native command with installed `/usr/bin/strace`, following
its descendants and writing `/episode/native-syscalls.log`. Trace process,
signal, openat, ftruncate, fsync/fdatasync, mmap/mprotect, prlimit64 and
write/pwrite64/writev syscalls. For all write-family syscalls use raw argument
rendering, retaining pointer/length/results instead of payload contents. Do
not trace reads, network payloads, environment values or unrelated processes.
Keep all earlier limits, including 128 child/192 outer tasks, 2-MiB file size,
256/512-MiB memory and 30-second native deadline. Freeze strace's file hash.
This changes diagnostic observation and scheduling; it is not study execution.

Verify the derived command and unchanged fixture bytes before one launch.
Retain and inspect the trace through the existing guarded full-mount collection,
including failure and truncation. Require actual return/error events to identify
the observed termination; no disappearance-only inference. Verify retained
custody/source/install/library/strace and exact owned unit/cgroup cleanup.
No resource or response repair is authorized by this tracing scope. No further
native launch under this record after the trace.

The syscall derivation and source/decoder/tracer pins were rechecked before
launch. Ruff F passed. A bounded synthetic strace preflight accepted the exact
selectors and rendered the write syscall as raw pointers/length/result, without
its payload bytes; exec arguments remain visible by design. Preflight evidence:
`/tmp/caplab-native-syscall-preflight.json`. Final native probe hash:
`440a86ba399786ee46ed5a7c1ea01ae3b53d5a2e4b91a011d0dbe3f8e942237c`.
Proceed with the single syscall diagnostic. The fixture-start command field
names the underlying native command; the frozen bootstrap and derivation name
the actual tracer prefix and must be used to interpret execution.

## Outcomes and next diagnostic boundary

The capacity run used
`caplab-native-pid-capacity-75c462cfa45d40c3bb8b4b01bc35fe63.service`.
Its custody verification passed: 3,419,991 full-mount bytes, 138 entries and
116 scanned files. Source/installation/decoder pins match. The exact unit and
cgroup are absent. No PID/memory limit event occurred. The unchanged response
hash is `72698e6a71eb5bc812f107160c8880ed656292a77571d3a485877a2592ba1d11`.
Verification: `/tmp/caplab-native-pid-capacity-failure-verification.json`.

The syscall run used
`caplab-native-syscall-7628d111c5b449fd9cd5a81b95622fcd.service`.
Its directly owned subprocess is strace, so the fixture's inherited field
`native_return_code: -25` reports tracer SIGXFSZ, not a separately observed
native terminal status. The bootstrap subsequently cleans up the owned process
group. The log is exactly 2,097,152 bytes and ends mid-line before the first
response POST. It contains no native EFBIG, delivered SIGXFSZ, or code-mode-host
execution event. Signal-handler registration is not signal delivery. The
combined observations identify an instrumentation failure; they do not diagnose
the preceding native execution failure.

Full-mount custody contains 5,220,292 bytes in 139 entries. All 117 retained files
were scanned for the six configured raw synthetic forbidden values; none were
found. This exact-value check does not establish protection against arbitrary
encodings. Process/task/native/mount integrity checks passed; the selected
rollout contains only session metadata and a task-start event. Root linkage
correctly refuses its missing tuple attestation. The verifier's initial inherited
assumption of a linkable rollout failed; it was replaced with a requirement for
that exact refusal. Empty stdout tool-pair parsing does not repair root linkage.
No final message, task write, fixture error, PID-limit event, memory-limit event
or OOM was observed. Source/installation/decoder/tracer pins match, and the exact
unit and cgroup are absent. Verification:
`/tmp/caplab-native-syscall-failure-verification.json`.

The syscall prefix retained 4,784 mmap and 4,726 openat records among its startup
traffic. A future diagnostic should first demonstrate that a narrower failure/
signal trace retains a synthetic file-limit failure within this same byte budget.
That is a candidate observation change, not permission for another launch here.
No fourth native launch is authorized by this record. The 2-MiB native WAL remains
a candidate boundary, and the original SIGTRAP cause remains unproven. Leave
response semantics, native configuration and CAPLAB runtime unchanged.

Alternatives considered: guessing custom-call metadata is unsupported by the
observed dispatcher and published schema; removing all resource limits would
lose the bounded failure question; repeating the broad trace would reproduce
its observer limit. Preserving the failures and preflighting a smaller observer
has a concrete evidence basis. This record establishes dispatch and failed
resource diagnostics only, with no study capacity, model capability, successful
authentication, provider execution, reviewer qualification or roadmap closure.

## Advisory closeout and remaining obligations

The release retrieval gate was rechecked successfully at release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
The initial packet was `pkt-f3cbda931613cb03`. Five typed evidence records and
one reassembly produced `pkt-3d5f98382d62c10e`, content hash
`3d5f98382d62c10e4761e474db3e14f4afa8eb2fd3d8257d0b1a9cd6f569b8c0`.
Both Markdown packets were read. The question's initial premise, retention
without dispatch, was contradicted by the logging run; dispatch is now observed,
while the termination cause remains unresolved. The original packet wording is
preserved rather than rewritten to imply a successful original diagnosis.

All 32 final missing obligations remain visible in the archived packet:

- Eighteen concern deduplication keys (3), ingestion populations (4), async UI
  state (4), declarative reference validation (3), and relevance selection (4).
  They are nonmaterial here: no such product behavior was changed or certified.
- Four external-capability obligations are material to a working integration
  claim, which is withheld. Installed-native failure observations and a
  synthetic endpoint do not establish a working provider integration. This
  verification is explicitly limited to the observed diagnostic and its custody.
- Four authoritative-gate obligations are material to a production readiness
  claim, which is withheld. Actual receipt/source bytes and process outcomes
  were inspected for these runs; no evaluation/serving parity or complete
  production gate inventory is established.
- Three symptom-monitoring obligations are nonmaterial: no service monitoring
  or paging policy was changed or assessed.
- Three no-change obligations about future plans, intervention cost and its
  general decision procedure are nonmaterial to preserving these observed
  failures. No architectural recommendation or lasting resource policy is
  selected; the prospective trace candidate requires its own preflight and scope.

The selected guidance was repository-contract precedence, evidence before
intervention, separate semantic and structural change, default preservation,
and authority-bounded action. Source observations and executed checks establish
the findings; advisory retrieval does not establish native causality or accept
any study result. AI-failure-mode review focused on mistaking tracer status for
native status, treating handler registration as signal delivery, and inheriting
verification expectations from later-stage captures. The synthetic preflight
missed trace volume; preserve that limitation instead of declaring the observer
adequate. No CAPLAB runtime or test source changed, so no full-suite rerun is
warranted for this record-only commit. The private verifier and derivation Ruff F
checks passed.

Packet identities are corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8` and schema
`evidence-packet/3`. Citation consumption recorded all five selected concepts.

## Final custody

Private manifest `/tmp/caplab-native-dispatch-verification.json`, SHA-256
`ba71d352161bd65290e1df84a58a3e7b54d758f167ca0aa5072136435bd7a69d`,
anchors 390 artifacts and 13 unchanged repository source records. It includes
all three run custodies, source/derivation/preflight/failure verifiers, the seven
pinned published source files, and byte-for-byte archives of eleven retrieval
scratch files. Each archive was verified before those exact scratch paths were
removed. Native failure artifacts and predecessor evidence remain retained.
All three native allowances are consumed. No provider/model spend, real
credential use, tracker write, outbound message, push or historical-research
evidence effect occurred. Preserve unrelated `docs/designs/` and worktrees.
