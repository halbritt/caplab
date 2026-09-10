# Quarantine native exec traces before retention

## Observation and selected scope

At source commit `f602d15f5bba07eb3a0acc996e5711ccdb229a13`, the scripted
native runner passes a retained `safe-exec.trace` path directly to strace.
The final directory scan checks raw bytes after persistence. The selected
`-xx` trace format encodes argv and environment strings, so an exact plaintext
guard alone does not identify credential text in those strings. Prior private
diagnostics used synthetic credentials and separately checked decoded trace
strings; those checks do not establish a pre-retention guard for a real attempt.

The primary agent selects a sealed anonymous trace buffer and a guarded copy
into retained custody. Check raw bytes and every decoded hexadecimal string
before creating a durable trace. Preserve source descriptor identity in a
separate retention link, rather than asserting that the copied file is the
original tracer inode. Preserve existing file-backed observations and their
inspectors. The buffered profile must be selected explicitly and linked through
preparation, execution and inspection before it supports an actual attempt.

## Prospective authorization

Authority is the continuing owner goal and ADR 0026. Authorize implementation,
tests, contracts, retained verification and commit/push for this trace path.
Local tests may run bounded Python/strace producers with fabricated strings,
anonymous descriptors and temporary private directories. No real credential
read, credential delivery, installed native agent, provider request, historical
evidence rewrite, tracker mutation or external notification is authorized by
this record. The tracker read on this turn returned HTTP 403; repository
contracts remain available and the saved tracker response is only a prior
observation.

The trace owner must bound the producer's file size and process lifetime, stop
writers before sealing, close the anonymous descriptor on all exits and refuse
publication on quarantine, malformed encoding, truncation or custody failure.
Anonymous buffering is not a memory-erasure or swap-encryption guarantee.
Production adoption still requires zero-swap resource controls and the other
capture/identity/authorization gates. Historical traces, failed outcomes and
unrelated `docs/designs/` remain unchanged. This scope expires at the verified
commit; further actual native execution requires its own exact authorization.

Verification will exercise real strace output, safe byte preservation, encoded
secret refusal before durable writes, malformed/limited traces, immutable
source sealing, descriptor cleanup, copied-trace provenance and explicit
profile selection. Passing these checks does not establish provider integration,
representative repair, capture completeness or study eligibility.

## Component execution and prospective native control

The initial test failed because no buffered trace API existed. A real strace
producer now writes only to the supervisor's anonymous buffer; safe bytes are
sealed and copied unchanged. A fabricated non-ASCII credential in actual exec
argv is absent as plaintext in the raw hex trace, but decoded quarantine refuses
it before creating any output file. Malformed, abbreviated, incomplete and
at-limit inputs are refused. Existing output survives a refused replacement,
and descriptors close on normal and exceptional exits.

A separate real isolated-process control identifies the outside tracer and
anonymous output descriptor before release, then links its retained copy after
termination. Changed source identity, digest, quarantine flag or seals are
refused. Twenty-seven focused tests passed. A read-only inspection of the prior
v6 native diagnostic produced a byte-identical report under the current code.

Prepare one fresh native control at `/tmp/caplab-buffered-native-attempt-1`.
The resulting v7 preparation has SHA-256
`ea07600ce2074720911ccc769294c230383b94fe392d6b124a2fd35f50e6f1b3`.
After the full required check passes, the primary agent authorizes exactly one
execution of that preparation and retention/inspection of its resulting capture.
This is a new prospective authorization under ADR 0026; it does not broaden the
earlier component-only scope or renew a prior attempt.

The subject is the pinned installed Codex CLI, `gpt-5.6-terra`, effort `max`,
with routed/v2, cgroup-usage/v1, supervisor-poll/v1 and sealed-buffer/v1.
The fixed scripted responses and fabricated authentication remain selected;
the outer network is disconnected. Reuse only the already prepared diagnostic
task at `/tmp/caplab-routed-native-task-input`, input SHA-256
`626a261b34f11df899c7228baecf6de6559e92fb15b6d671db29e1940172a529`.
Its existing bytes remain immutable; the workload may add only the diagnostic
witness in its materialized copy. This has no repair-study population or model
response interpretation and creates no new world exposure for a reviewer study.

The fixed native/capture/unit/outer ceilings remain 30/75/120/130 seconds,
with 256/512 MiB workload/unit memory, zero swap, 128/192 tasks and the prepared
capture byte limits. Verify all implementation/runtime/harness/input pins before
consumption. No retry or allowance refund is authorized. On failure preserve
the spent receipt and safe partial artifacts, close the buffer, stop the owned
unit/workload and remove only owned transient runtime resources. Verify the
retention link, tracer custody, exact native/tool/task/final observations and
owned cleanup. Preserve any transport failure as a separate failed outcome.
No real credential read/delivery, provider call, historical evidence mutation,
model-generated review, qualification or human-owned judgment is authorized.

## Native result and final verification

The full required check passed: 1,505 tests in 214.555 seconds, four skipped,
with `CAPLAB_TEST_WEBSOCKETS_ROOT=/tmp/caplab-native-transport-deps/websockets make check`.
The later test-only dependency-skip annotations also passed all 13 focused
trace/provenance tests in 0.581 seconds. Runtime sources were unchanged between
preparation, the full check and native execution. Scoped Ruff F checks, selected
file formatting and `git diff --check` passed.

The one native allowance was consumed. Result SHA-256 is
`f6d886cf35d6d15ad3ed92ce2d81cef2a16270e7dee73055bce895018ee86329`;
inspection SHA-256 is
`70767b06d613e1db94bfd795d66dec69d9488724aa25abcfe27b97ca7b8f22d0`.
The inspection is `/tmp/caplab-trace-quarantine-native-inspection.json`.
It verified the new custody link for 1,515,632 unchanged trace bytes and 5,102
decoded strings, with all four required seals. The anonymous source and retained
file have distinct identities, as required. Exact native request, tool, task,
final-message and normal shutdown observations remain available.

The overall attempt is still failed: the existing
`ConnectionClosedError: no close frame received or sent` is preserved. Successful
trace retention does not convert that transport outcome into success. There was
no real credential read/delivery or actual provider request. The source/runtime
pins, process receipt hashes and owned cleanup were independently rechecked;
the owned unit is unloaded and its workload cgroup is absent. The verification
result is `/tmp/caplab-trace-quarantine-verification.json`.

The live CAPLAB-84 read succeeded on the default work tracker instance after the
personal-instance 403. Its current description matches the repository's
representative-repair requirement. No tracker write occurred.

The owner then canceled the continuing goal and instructed the agent to land
work in progress. This record closes the buffered-trace implementation only.
Provider integration, the transport failure and representative repair/reviewer
measurements remain unfinished; no further goal execution is selected here.

## Retained advisory and verification identities

Final packet `pkt-0a23df64054c61a1` has content SHA-256
`0a23df64054c61a14f9e8f7924ee273cbad767f9f2be7a81c6915cb50ee07164`, corpus
`corpus-2026-07-12-a11702cc9217`, retriever
`retriever-ec995ecdd083b2c8`. Four evidence records and the decision receipt
passed schema validation; both packets have citation classifications. Nineteen
missing obligations concern unclaimed performance/overhead measurements or
wider interpreter/toolchain qualification and remain classified nonmaterial
with exact rationales in `/tmp/caplab-trace-quarantine-obligations.json`.
The decision receipt is `/tmp/caplab-trace-quarantine-decision-receipt.json`.

Private manifest `/tmp/caplab-trace-quarantine-verification-manifest.json`
has SHA-256 `749d64bc6a4bcd4e26dc35db20c54b78223d54750f607b0c4349ed12e39b6695`. It anchors 37
private artifacts, the native result locator and 172 implementation/8 runtime
pins. Historical custody remains unchanged.
