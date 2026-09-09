# Observe native resource failures with a bounded filtered trace

Baseline `5fbe4a9`. Primary agent under the continuing CAPLAB goal and
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
The preceding broad syscall trace exhausted its own 2-MiB file allowance before
the scripted response. Authorize a new private diagnostic scope under
`/tmp/caplab-native-failure-trace-*` and this record. Preserve every predecessor
run, installed native source, repository runtime, unrelated `docs/designs/`,
worktrees and services. No provider/model spend, real credentials, research
evidence effects, tracker write, outbound message or push.

Select a strace observer that prints only failed process/create/exec, write,
file-sync/truncation, memory-map/protection and prlimit64 syscalls. Retain fatal
signal delivery and exit status, with process command names. Render write,
pwrite64 and writev arguments raw, without their payload bytes. Do not trace
reads, network payloads, environment values or unrelated processes. Successful
syscalls are intentionally unavailable; no complete execution provenance claim
may follow from this observer. This is a diagnostic observation change.

First run two bounded synthetic controls, with ignored and default SIGXFSZ,
each preceded by 32,768 successful writes to /dev/null. Give each tracer the
same 2-MiB file allowance; reduce only its synthetic child's file cap to 64 bytes.
Require the ignored-signal control to retain EFBIG and delivered SIGXFSZ, and
the default control to retain delivered SIGXFSZ and termination. Each trace must
remain under 64 KiB with no synthetic write payload in retained trace bytes.
Freeze the exact tracer command, source hash and installation/decoder pins.
A failed preflight authorizes correction of this observer and another synthetic
control, but no native launch until the criteria are met.

After a passing preflight, authorize exactly one native diagnostic derived from
the PID128 probe with only this tracer prefix added. Unit name:
`caplab-native-failure-trace-<32 hex>.service`. Preserve native Codex 0.153.4,
gpt-5.6-terra/max configuration, the exact fixed custom-call/SSE response bytes,
fabricated auth, isolated loopback-only namespace, read-only installation,
128 child/192 outer tasks, 256/512-MiB memory, no swap, 2-MiB per-file limit,
64-MiB writable tmpfs mounts, 30-second native/45-second capture/90-second unit
limits and all preceding stream/request/entry/retention/quarantine/cleanup bounds.
Require direct observed failure events for diagnosis. Actual tool output, witness
file, final message and two-response completion are required for task success.
On either outcome, verify full retained custody, installed source/decoder/tracer
pins and exact owned unit/cgroup removal. Do not infer native status solely from
the tracer return code. No automatic second native launch. Any resource repair
requires a separate prospective amendment grounded in this run's evidence.
Authority expires at local commit.

## Preflight and launch

Both synthetic controls passed. The ignored-signal trace is 279 bytes and records
EFBIG, delivered SIGXFSZ and child exit 23. The default trace is 296 bytes and
records EFBIG, delivered SIGXFSZ and signal termination. Each followed 32,768
successful writes, retained no write payload and stayed below the 64-KiB bound.
A Ruff F unused-import finding in the preflight driver was removed; its embedded
writer and executed controls remain unchanged. Evidence:
`/tmp/caplab-native-failure-trace-preflight.json`.

The derived bootstrap differs only by the selected tracer prefix. Source,
decoder and tracer hashes match. Native probe SHA-256:
`45842937c475d3f9634ec605d1762a46c02575427d3cade45f14da0d67fc3ebc`.
Proceed with the single authorized native diagnostic. Fixture-start command
metadata still names the underlying command; the derivation and launch bootstrap
retain the actual tracing prefix. Trace status must be read with that distinction.

## Observed file-limit failure and bounded repair diagnostic

The filtered run used
`caplab-native-failure-trace-bcc17ef69e034c3486fd36e3f8ff6dc0.service`.
Its 90,476-byte trace directly records a `sqlx-sqlite-wor` thread's pwrite64
at offset `0x200000` returning EFBIG, followed by delivered SIGXFSZ and termination
of process `14<codex>` by that signal. The JavaScript launcher `7<MainThread>`
subsequently exited zero. The wrapped return code therefore obscures a native
binary failure. The fixed tool call reached dispatch but produced no task write,
tool output, final message or second response POST. The trace remains below its
file limit and ends normally. No PID/memory limit event or OOM occurred.

Verified failure custody: 3,510,467 full-mount bytes in 139 entries, 117 files
scanned without the six raw synthetic forbidden values. Source/installation/
decoder/tracer hashes match; the exact unit and cgroup are absent. Evidence:
`/tmp/caplab-native-failure-trace-failure-verification.json`. This directly
establishes a file-limit failure for this diagnostic, not the only possible
obstacle to native completion. The trace's raw fd does not identify the pathname;
the earlier exact-size WAL remains supporting, non-identical evidence.

Under ADR 0026 authorize exactly one new diagnostic under
`/tmp/caplab-native-file-capacity-*`, unit
`caplab-native-file-capacity-<32 hex>.service`. Derive it from the filtered probe
by changing only the inherited RLIMIT_FSIZE from 2 MiB to 8 MiB and the owned
artifact/unit prefix. Keep the filtered observer, native configuration, fixed
response bytes, tool command, fabricated auth and all other previous limits.
In particular, 40-MiB total full-mount retention, 8-MiB selected-native retention,
64-MiB mounts, 256/512-MiB memory, 128/192 tasks and all time/stream/request limits
remain unchanged. A retention refusal must remain a failure, not trigger a
larger capture budget. The new per-file bound is a diagnostic resource change,
not adoption of a study Binding or a production capacity policy.

Freeze exact derivation/source/decoder/tracer hashes before launch. Require the
actual witness bytes, linked tool output, two-response completion and final
message, as well as capture integrity, for task success. Inspect the native
trace for EFBIG and fatal signals on either outcome. Preserve partial evidence
and exact owned cleanup on failure. No automatic retry or third native attempt
under this record. Leave native/provider source and repository runtime untouched.

The capacity derivation passed: only the per-file limit and owned prefix differ;
all scripted-response code and other bootstrap bytes are unchanged. Decoder and
tracer pins match and Ruff F passed. Probe SHA-256:
`09cb8cee7c7785c5b841bd30ce5bc0237f9330be205d8cfeabf6f38e4ab1ac30`.
Proceed with the single file-capacity diagnostic.

## File-capacity outcome

The capacity run used
`caplab-native-file-capacity-a889fc9b4a3b47a9961e2d08286b0492.service`.
The unchanged fixed custom call produced a native custom-call output and a
second response POST. Its command result is exit 1 with
`bwrap: setting up uid map: Read-only file system`. The task inventory remains
empty. This is evidence of a nested sandbox setup failure, not successful task
execution. The outer namespace's /proc was deliberately remounted read-only;
a future containment design must support the native sandbox's UID-map setup
without disabling that sandbox or exposing host process state.

The fixed fixture correctly refused the missing witness text on the second
POST, recorded one AssertionError, and stopped the owned process group. The
wrapped return code -9 is cleanup after that fixture error, not an independently
observed natural native exit. The fixture provided no successful final response.
The 92,951-byte trace contains no EFBIG or delivered SIGXFSZ. No PID/memory limit
or OOM event occurred. This supports the bounded per-file-capacity repair while
revealing another execution obstacle; it establishes no representative capacity.

Failure custody verified: 3,600,688 full-mount bytes in 141 entries, 118 retained
files scanned without the six raw synthetic forbidden values. This is exact-value
protection only. Source/installation/decoder/tracer pins match, root linkage is
available, and the exact unit and cgroup are absent. No tool-pair group in the
stdout projection records this nested command; the exact result is preserved in
the retained rollout's custom-call output. Evidence:
`/tmp/caplab-native-file-capacity-failure-verification.json`.

Both native allowances are consumed. Select source inspection and a synthetic
nested-sandbox control as the next work, before any further native attempt.
Removing the native sandbox or changing fixture success criteria would change
the subject or conceal the failure; neither is selected. No third native attempt
is authorized here. The 8-MiB file allowance remains a private diagnostic choice,
not a CAPLAB runtime or study default.

## Advisory and verification closeout

Doctrine retrieval used the validated release at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`; its gate verified source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
The initial packet was `pkt-54f10093dc455d54`. Five typed records and one
reassembly produced `pkt-f360b7d1c6b111cd`, content hash
`f360b7d1c6b111cd764a463782750396883c956043f7e546ad5fe85b526f8f63`.
Both Markdown packets were read. Versions: corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, schema `evidence-packet/3`.

The 32 final missing obligations remain in the archived packet:

- Eighteen concern deduplication keys (3), ingestion populations (4), async UI
  states (4), declarative reference validation (3) and relevance selection (4).
  They are nonmaterial to these private diagnostics; no such product behavior
  was changed or certified.
- Four external-capability obligations are material to a working provider
  integration claim, which is withheld. Verification is limited to the installed
  native harness, fabricated endpoint, observed failures and retained custody.
- Four authoritative-gate obligations are material to production readiness,
  which is withheld. These runs inspect actual trace/output/receipt bytes but
  do not establish evaluation/serving parity or a complete production gate inventory.
- Three symptom-monitoring obligations are nonmaterial because no service
  monitoring or paging policy changed.
- Three no-change obligations about future plans, intervention cost and general
  decision procedure are nonmaterial to these bounded failure observations.
  The diagnostic resource change follows direct EFBIG/SIGXFSZ evidence; no
  lasting resource or architecture policy is selected.

The applied guidance is repository-contract precedence, evidence before
intervention, separate semantic and structural changes, default preservation
and authority-bounded action. Doctrine supplies no independent acceptance or
measurement result. AI-failure-mode review checked wrapper/native exit confusion,
trace observer overhead, omitted successful syscalls, native error output versus
successful command execution, and preservation of fixture refusal. No swallowed
failure, success fallback, model score or reviewer qualification is introduced.
Ruff F passed for the private derivations, probes and verifiers. Repository
runtime/tests are unchanged; a full-suite rerun would not verify this diagnostic.

Alternatives remain explicit: repeating the broad trace would repeat its
storage failure; removing all resource limits would erase the bounded question;
disabling Codex's sandbox would change the subject. The next diagnostic must
instead establish a compatible isolated procfs arrangement with synthetic
controls and its own prospective scope. No successful native task, independent
acceptance, study result or roadmap closure is claimed here.

Private custody manifest `/tmp/caplab-native-failure-trace-verification.json`,
SHA-256 `b51071d75c20bcc3d1d5814ea561a33246a861c7a88ff32783e09831c5788b96`,
anchors 262 artifacts and 13 unchanged source records. Eleven retrieval scratch
files, including both packets, five typed records and citation observations/
results, were archived byte-for-byte and verified before exact-path removal.
All five cited concepts were classified as valid packet citations. Native and
synthetic source/capture/failure artifacts remain retained. Both owned units and
cgroups were verified absent. No provider/model spend, real credential use,
historical-research evidence effect, tracker write, message or push occurred.
