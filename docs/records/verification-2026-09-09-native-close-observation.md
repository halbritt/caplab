# Observe native shutdown after the completed fixed exchange

Baseline `0ebc177`. Primary agent under ADR 0026 and the continuing CAPLAB goal.
The prior turn made progress: it preserved the first native WebSocket exchange
and identified fixture-triggered termination before the final-message file.

## Decision and prospective preparation

Select a diagnostic-only close policy to distinguish premature supervisor
termination from failure of the native process to finish. Preserve the original
failed attempt and all source artifacts. Derive new private artifacts under
`/tmp/caplab-native-close-*`; preserve native configuration, installation,
ordinary trace, guard, containment, quarantine, fixed payloads and all limits.
No public runtime or study policy changes are selected.

An abnormal WebSocket closure remains in the fixture's errors. Permit it to
avoid immediate supervisor termination only when it has neither received nor
sent a WebSocket close frame, both generated fixed responses have completed
all sends and raw retention, and no other error exists. Record its exact error
index and bounded closure observation. A later additional error must restore
immediate termination. This is a narrowly classified observation delay, not
suppression, successful transport classification, or an extended deadline.
Keep the existing 30-second native and 45/90/100-second capture/unit/outer bounds.

Authorize this record, private source derivation and real-loopback controls.
First reproduce the missing policy through a socket abort after both complete
responses. Then implement the classification and test early closure, malformed
frames or messages, incomplete response retention, additional errors and open
connection timeout. Test the actual bootstrap loop's use of this predicate.
No native attempt is authorized in this preparation section. Freeze a separate
one-attempt authorization after controls and source checks pass.

Preserve every native stdout event, strict final-file linkage and the original
failure-free success verifier. The new diagnostic may observe normal native
exit and final-file custody while still reporting the fixture's transport error.
Do not classify that as the previously required failure-free attempt. No model
inference, real credentials, historical evidence effect, tracker write, push,
external message or independent acceptance. Preserve unrelated docs/designs,
worktrees and services. Stop on unexplained controls or source drift. This
preparation authorization expires at the local record commit.

## Preparation results and one-attempt authorization

The first socket-abort test reproduced the absent stop policy. After adding
explicit deferred-close metadata and a stop_required predicate, it passed with
the original close error retained. The actual bootstrap-worker test then failed
because it still stopped on any error. Its loop now uses stop_required and
publishes the deferred-close observation; the same test passes and confirms
that a subsequent forbidden response POST immediately restores the stop.

All 18 fixture methods pass, including five new shutdown methods. They cover
abort before either response, explicit protocol-error close, malformed JSON and
unmasked frames after both responses, final-event file collision, open-socket
deadline, retained error identity and the actual worker's response to additional
errors. The derived six-device isolated startup control passes readonly import,
health, capability drop, thread/listener cleanup and owned-unit removal.

The native probe differs only in the fixture module path, fixture-worker stop
predicate and deferred-close summary field. Its guard, command/environment,
fixed payload, native polling loop, cleanup and failure-free assertion remain
unchanged. The 17 source pins and installed harness still match; the existing
five guard controls and 58 focused public tests are reused from their verified
unchanged sources and sealed prior manifest. No public code changed. The
prospective observation auditor requires native zero exit, exact protocol/tool/
final bytes, strict final-file linkage, exact launch and direct parentage,
quarantine/resource/custody checks and owned cleanup while retaining the sole
classified transport error. It does not emit a failure-free success result.

Primary agent under ADR 0026 authorizes exactly one invocation through
`/tmp/caplab-native-close-launch.py` with fresh root
`/tmp/caplab-native-close-run`. Consume its exclusive allowance receipt before
launch and pin this authorization, fixture, probe, verifier, controls and
installation/source records in release-preflight.json. The subject remains
installed Codex CLI 0.153.4, gpt-5.6-terra/max, codex-terra-max, through the
native-agent-systems.json canonical builder and codex-scripted-local/v1 profile.
Only fabricated readonly authentication and fixed local responses are available.

Preserve ordinary unfiltered exec/process tracing, all isolated namespaces,
isolated procfs, six explicitly bound devices and five 64-MiB writable tmpfs
mounts. Preserve 30/45/90/100-second native/capture/unit/outer limits,
256/512-MiB child/unit memory, zero swap, 128/192 task limits, 300,000-byte native
streams, 1-MiB/1,000-entry task capture, 8-MiB/1,000-entry native collection,
40-MiB/2,000-entry mount capture, 2-MiB trace, 8-MiB native file limit and no cores.
All prior value quarantine and authenticated seal-before-release checks apply.

On any timeout, extra protocol error, quarantine, source drift or verification
failure, preserve the result and stop further native execution. A retained
classified close error is expected to leave the unchanged bootstrap success
assertion false even if the native process exits normally; audit that outcome
separately without relabeling the original attempt. Stop and verify removal of
only the exact owned unit/cgroup. No retry, real provider execution, credential
read, historical effect, tracker write, push, message, independent acceptance,
full Binding or study eligibility is authorized. Scope expires with this single
attempt and the verified local record commit.

## Execution and verified outcome

The single allowance was consumed. Installed native Node launcher and Codex
binary both exited zero. The retained fixture error is unchanged:
`ConnectionClosedError: no close frame received or sent`. It is identified as
the sole deferred error after both complete generated responses. No later error
triggered the stop predicate, and the 30-second native deadline was not reached.
The unchanged bootstrap success assertion still failed, leaving outer diagnostic
exit one and no original success observation. This is the expected separation
between observing normal native completion and claiming a failure-free fixture.

The prospective observation auditor ran unchanged and passed. It verifies the
release snapshot/receipt, source and installed harness pins, the same one
WebSocket/warmup/two-response protocol, exact retained raw message/event bytes,
fixed tool JavaScript and actual command output, the 26-byte UTF-8 task witness,
and the 40-byte final-message file. The unchanged strict final-message linker
now passes with zero native stream error events. Native collection has no
missing locations. No error was removed and no final bytes were synthesized.

Exact effective argv/environment, Node exec and selected native binary exec
agree. Direct native parentage now passes the unchanged public reader. Host
launcher PID 3904182 created binary PID 3904198 at trace line 20; the native exec
is line 21. Both selected terminal trace records are exit zero. No incomplete
clone or parentage-reader repair was needed for this execution. Root linkage
still reports executed_invocation_bound false, native capture completeness
unknown and study eligibility false; the narrower observations do not replace
those integration boundaries or prove independently observed cwd at every exec.

The native process was observed exited 20.079 seconds after spawn, 5.635 seconds
after abnormal socket closure. Final response transmission finished at 13.789
seconds. These observations answer the bounded diagnostic question: under this
close policy the installed harness can finish normally and write its final file
within the existing deadline. They do not establish a general timing target,
normal termination for every run, a performance improvement, or a comparison
that controls scheduling, cache or other runtime variation.

Task, native collection and all five retained-mount custody checks pass. Retained
mounts contain 1,322,313 bytes across 131 entries. The ordinary trace is 1,433,305
bytes, SHA-256
`5fb541c3f303104b85fa3acae10d0e4f2649aee3eb88e81ee2ff5d2ac8b58ab1`.
All 117 retained files and 4,755 decoded trace strings pass the configured
forbidden-value checks. No quarantine refusal, PID-limit event or memory
max/OOM/kill event occurred; final child PID count is zero. Configured unit and
observed child limits match the preserved bounds. Unit
`caplab-native-close-3a42bd3119ad47858f3868b4ded02a53.service`
and its recorded cgroup are absent. No additional native attempt was made.

The next product decision is how a capture report should keep native process
completion, final-message linkage, and fixture transport closure as separate
observations. The current transport error cannot be silently promoted to
failure-free protocol success. The verified execution/configuration/custody
components also still need integration into the public capture path before a
representative repair measurement or study claim. This record selects neither
a provider run nor independent acceptance of a Binding.

## Advisory and final checks

The Doctrine release gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet pkt-434d79adf8298fbf and five typed evidence groups produced
pkt-902b153dfa6232fc, SHA-256
`902b153dfa6232fc950e28763cdf47eb4425e174354ecc31f19d7ce781e94a2b`.
Both Markdown packets were read. Versions remain corpus-2026-07-12-a11702cc9217,
doctrine-f6bbb5196a3f8bf9, retriever-ec995ecdd083b2c8 and evidence-packet/3.

All 28 missing obligations remain visible. Eighteen concern unchanged record
identity/deduplication (3), ingest populations (4), asynchronous UI (4),
declarative references (3) and ranking (4); they are nonmaterial to the selected
private close-policy experiment. Three monitoring obligations are nonmaterial
because service monitoring and paging did not change. Three external-capability
and four authoritative-gate obligations remain material to full native capture
and study adoption, which are withheld. The scoped installed-native observation
does not establish provider operation, complete Binding or representative repair
performance. No timing optimization or statistical improvement is claimed.

Selected guidance is repository-contract precedence, evidence before
intervention, authority-bounded action, preservation by default and separating
semantic from structural changes. Leaving the prior immediate-stop policy
cannot answer whether native shutdown would complete after closure. Removing
errors, extending the deadline or accepting incomplete sends would change the
question and its protected criteria. The selected narrow deferral preserves
those criteria and produces the needed observation without such changes.

The eighteen fixture methods and isolated startup pass. The frozen prospective
observation auditor and separate limits/timing auditor pass; the original
failure-free assertion remains false as recorded. Existing guard/public-test
results were reused only after source and artifact hash checks. No public
runtime or test file changed, so the prior 1,374-test full-suite result with four
skips remains the applicable recorded check and was not rerun. Ruff F passes
for the new fixture, controls, probe, launcher, verifier and auditors. The
prior failed native attempt and its artifacts remain unchanged.

## Final custody

Manifest `/tmp/caplab-native-close-verification.json`, SHA-256
`35cc351ba0f3d6b960f8c6347cf9408ce20f857c45f0bbb38dd84a6c26c11f34`,
covers 158 artifacts, 20 unchanged repository sources and 60 private dependency
files. The preceding WebSocket manifest and all its artifacts still match their
original hashes. All five doctrine citations classify as valid; eleven scratch
packet/evidence/citation files were embedded, hash-verified and removed.

The release authorization snapshot, consumed one-attempt receipt and unchanged
prospective auditor are retained separately from this final record. This local
commit closes the scoped authorization. Native shutdown and exact final linkage
are verified for this one fixed diagnostic; the recorded transport error remains.
No independent acceptance, full capture, qualification or roadmap completion is
claimed. The full CAPLAB goal remains active.
