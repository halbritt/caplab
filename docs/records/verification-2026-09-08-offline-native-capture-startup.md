# Exercise native capture startup without credentials or network

Date: 2026-09-08. Baseline: `d849a0e`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `scripts/probe_native_capture_startup.py` and this record. Reuse the
existing resource probe's authenticated five-mount handoff and cgroup cleanup,
the supervised task recorder and descriptor native collector. Permit one
supporting change in `scripts/probe_cgroup_resource_limits.py`: an optional
trusted peer-inspection callback before before-capture and workload release,
retaining its returned observations in the handoff receipt. Preserve the
existing default path. Do not modify runtime components or frozen policies.
This diagnostic advances CAPLAB-84/85's
native startup compatibility evidence; it is not a study episode, repair
measurement, harness selection, or model-quality comparison.

Authorize exactly one generated `caplab-native-startup-<uuid>.service` with
512 MiB memory, no swap, 128 tasks and a 75-second lifetime. Inside it, run
one startup invocation per native harness, sequentially, under a distinct
owned child cgroup limited to 256 MiB, no swap, group OOM and 64 tasks.
Each invocation has a 20-second wall limit and 200,000 combined stream bytes;
the outer service capture has an 85-second limit and 200,000 stream bytes.
No retries are authorized. Preserve failures and stop before another unit.

Use only installed Codex package
`/home/halbritt/.npm-global/lib/node_modules/@openai/codex` and installed Claude
executable `/home/halbritt/.local/share/claude/versions/2.1.265`, mounted
read-only with `/usr`, the existing minimal device files, and a private handoff
socket. Hash these sources before and after, bounded by 1 GiB and 10,000
entries per harness. Reject source symlinks that escape the declared package.
Record package/executable content identities and the current policy/profile
invocations before launch; these are not complete system-runtime Bindings.

Run canonical `codex-terra-max` and `claude-fable-5-max` capture invocations
with the exact synthetic prompt: `Startup diagnostic only. Reply with the
single word READY. Do not change files or use tools.` Use a fresh canonical
Claude session UUID recorded in the sealed plan. There is no advice arm or
quality scoring, and this authored startup prompt is excluded from study
task populations. The source task is empty. Before capture verifies the empty
private `/work` tree while execution is blocked.

Unshare all namespaces including networking. Require the peer's network
namespace to differ from the supervisor's and its interface inventory to
contain only loopback before release. Mount no credential, configuration,
home directory, account session or history from the host. The inner environment
is the canonical prepared profile; the outer environment is the existing
fixed launcher allowlist. Native code may attempt offline initialization or
fail for missing credentials, blocked networking, unsupported arguments or
resource limits. No remote authentication or inference is authorized.

Retain five private 64-MiB tmpfs descriptors. Seal before-task custody before
release and finish/collect only after the owned child cgroup is empty; kill
only that child's remaining processes if bounded process capture leaves any.
Allow 1 MiB/1,000 entries for combined task inventories, 8 MiB/1,000 entries
for selected native outputs and 40 MiB/2,000 entries combined for five full
mount inventories. Keep absent native outputs and incomplete streams explicit.
Do not assert model observation, executed-invocation attestation, native
capture completeness, account compatibility or eligibility from startup.

Keep new inputs, custody, logs, source/authorization hashes and verification
under `/tmp/caplab-native-startup-*`. Close owned descriptors, remove only
the generated child cgroups, stop only the generated unit, and verify that
unit and its parent cgroup are absent. Preserve raw failed custody, all
historical evidence, `docs/designs/`, other worktrees and unrelated services.
Permit focused static/offline checks and `make check`, consolidate advisory
scratch before deleting only its named files, and commit only the three named
files locally. No tracker mutation,
external message, push, study admission, ranking
or independent acceptance. Authorization expires at commit or a need for
wider execution effects.

## Decision and current scope

The live roadmap read at `/tmp/caplab-roadmap-current-d849a0e.json` still has
twelve open items. The preceding resource probe verifies authored producers,
not actual native command startup. Existing version probes execute only
`--version`. Exercise the already constructed capture commands under the
resource and custody path now, keeping all model-serving surfaces unavailable.
Another authored producer would not detect native argument-parser, runtime
initialization or persisted-output differences. A networked repair attempt
would require the still incomplete serving/account and study gates.

## Initial observation and bounded diagnostic extension

Unit `caplab-native-startup-848e3786fb914ccabe39e75d283676f1.service`
completed its two startup captures. Codex reached native thread initialization
and timed out on offline DNS retries after 20 seconds; its task was unchanged,
streams were incomplete and the final message was missing. Claude exited 134
with a Bun runtime abort before any stdout/session content, with no observed
cgroup OOM kill. Both owned child groups and the unit were removed. Raw custody
is `/tmp/caplab-native-startup-run/`; the executed source files were preserved
against the sealed launch hashes before further editing.

Authorize one additional generated unit at fresh
`/tmp/caplab-native-startup-trace/`, with the same outer/child resource limits,
filesystem, empty task, prompt, environment, credential exclusion and network
checks. Run only the same Claude source and canonical capture invocation once,
under installed `/usr/bin/strace`, recording file/process/signal syscalls with
256-character strings to `/scratch/trace.log`. This read-only instrumentation
is an explicitly different diagnostic configuration, not a study subject or a
substitute harness. Hash the strace executable before and after. Permit a fixed
`--trace-claude` option in the new diagnostic script; no arbitrary trace command
or harness override. Retain its raw trace through the existing mount inventory
allowance. Do not open or send the runtime's crash-report URL.

The purpose is to identify an inspectable startup dependency or failure path;
do not attribute the abort to a missing device, memory limit or CLI argument
without evidence. This extension permits no uninstrumented retry, model call,
new mount, credential, network sharing or source modification. It expires when
this single diagnostic finishes or the accompanying commit is made.

## Device failure and repair authorization

The traced Claude unit,
`caplab-native-startup-5467309332204da38058ee75abb84206.service`, retained
a 7,489-byte trace. It records successful `execve` of `/toolbin/claude`, then
`openat(..., "/dev/urandom", O_RDONLY) = -1 EACCES` immediately before
SIGABRT. The authenticated mount table shows `nodev` on both device mounts.
The files have host mode 0666. Bubblewrap's local help identifies `--dev-bind`
as the binding mode that allows device access. This supports a concrete
mount-policy defect, distinct from the other missing optional system files
listed in the trace. The traced unit and its owned groups were removed.

Authorize changing the two device mounts in both named probe scripts from
`--ro-bind` to `--dev-bind` followed by an explicit `--remount-ro` for each
device. Keep only `/dev/null` and `/dev/urandom`; do not mount host `/dev`
wholesale, add credentials, share networking, or make any filesystem mount
writable beyond the existing five tmpfs mounts. Before release in the native
diagnostic, check both device types/identities through the peer's root, read
one byte from urandom, and verify null reads/writes discard data. Retain only
the access results and identities, not random bytes. Preserve the earlier
executed scripts and traces against their launch hashes.

Authorize one corrected, uninstrumented two-harness native unit at
`/tmp/caplab-native-startup-fixed/` under the initial native limits, and one
five-mode resource-probe unit at `/tmp/caplab-native-startup-resource-fixed/`
under that probe's existing 128-MiB/64-task/60-second outer and 32-MiB/8-or-16
task child limits. No other retries. The resource probe retains its 70-second
outer and ten-second child capture limits and existing byte allowances.
Verify the corrected mount flags/access, resource fixtures, native outcomes,
retained custody and exact unit/cgroup removal. Run the final static and full
checks after these source changes. This repair/verification allowance expires
at the accompanying local commit or a need for wider effects.

The first repair did not clear `nodev`: the corrected resource probe passed
its older fixture assertions but its retained mount table still showed
`ro,nosuid,nodev` on both devices. The native pre-release check caught this and
refused `/dev/null` with `EACCES` before either native invocation was released.
Unit `caplab-native-startup-6c481f70723b40b79d3f1b24eb17202a.service`
was removed; its failed custody is `/tmp/caplab-native-startup-fixed/`.
The resource unit `caplab-resource-probe-588917f55ff04583937c34df6029e5cb.service`
was also removed. Its passing result does not verify device usability.

Authorize two model-free, five-second/8-KiB process captures under fresh
`/tmp/caplab-native-startup-device-check-*` roots. Execute only a fixed Python
device-access and mount-table probe in a no-network Bubblewrap namespace,
with read-only `/usr` and root, private temporary storage, and the same two
device nodes. Compare `--dev-bind` alone with `--dev-bind` followed by
`--remount-ro`. No native CLI, user unit, credential or host-directory write.
This isolates device mount semantics before selecting another native retry.

Both fixed Python checks completed. Adding the read-only remount produced
`ro,nosuid,nodev` and EACCES for both nodes; plain device binding produced
`rw,nosuid` without `nodev`, a zero-byte null read, a five-byte discarded
null write, and a one-byte urandom read. Random bytes were not retained.

Select plain device binding for exactly those two character devices. Amend
both probes' mount policy to distinguish these device mounts from the five
writable tmpfs storage mounts. Require device filesystem/type/identity and
actual access before release, in the shared handoff helper. Preserve the
helper's default legacy path and old read-only-device observation inspection;
new resource observations use v6. The root, `/usr` and `/proc` stay read-only.
This explicitly authorizes normal device I/O to the two named nodes, including
discard writes to null; it does not authorize any additional device or
writable host file/directory.

Authorize one final corrected two-harness native unit at
`/tmp/caplab-native-startup-devices/` and one final five-mode resource unit at
`/tmp/caplab-native-startup-resource-devices/`, under their respective limits
already stated. Keep earlier failures and successful model-free checks. No
other native or resource retry is permitted by this extension. The preceding
read-only-remount recommendation is withdrawn based on these observations.

## Final verification and interpretation

Final native unit `caplab-native-startup-ec2258b2b3034596a4eb60633306de2a.service`
and resource unit `caplab-resource-probe-dfb01b6dc2c845efa39a8c4d1c28cc48.service`
completed their capture/verification paths. Each handoff verifies that the two
devices have the expected character-device identities and are usable before
the workload is released. The root, system and proc mounts remain read-only;
the only writable storage mounts are the five declared tmpfs roots. The two
device mounts are listed separately in v6 resource observations.

| Final native startup | Exit / termination | Stream capture | Selected native bytes | All retained mount bytes | Missing selected locations |
| --- | --- | --- | ---: | ---: | --- |
| Codex | -9 / timeout | incomplete | 33,826 | 3,356,581 | final message |
| Claude | 1 / exited | complete | 31,535 | 247,323 | none |

Both task inventories remained empty. Neither native child recorded an OOM
kill or task-limit event. Codex reported thread initialization and offline DNS
failures before the 20-second timeout. Its persisted rollout reports CLI
`0.153.4`, configured model `gpt-5.6-terra` and effort `max`. Claude now passes
runtime initialization, reports CLI `2.1.265` and configured model
`claude-fable-5`, emits an authentication failure with `apiKeySource=none`,
and retains session/debug files. No credentials or network access were supplied.
The Bun abort stopped occurring after the controlled device-policy correction;
an authentication failure is the expected boundary for this diagnostic.

The existing Codex and Claude root linkers verify agreement between captured
stdout and the corresponding persisted session files. Tool-pair inspection
can parse both retained startup streams. The linked report is
`/tmp/caplab-native-startup-linked.json`. These are observations about startup
and locally reported configuration. They do not verify provider-served model
identity, full invocation attestation, conversation/child completeness,
successful repair, representative resource costs or study eligibility.
Codex's truncated capture remains incomplete despite a valid root link.

The five final resource fixtures passed: control exited zero without resource
events, pids exited zero with two task-limit events, and each of the three
memory-pressure fixtures exited -9 with four OOM-kill counter increments.
Their five-mount retention and task/native captures reverified after service
exit. The separate offline driver retained seven refusals: a harness symlink
escape, an oversized source, a special source file, the supervisor's own network
namespace, an omitted device policy, a `nodev` device and a device mount with
the wrong filesystem. It also reverified the three earlier retained native
failure captures and the final resource run. Driver/report:
`/tmp/caplab-native-startup-offline.py` and
`/tmp/caplab-native-startup-offline/report.json`.

The first full suite passed 1,227 tests in 160.855 seconds with four skips,
before the device repair. The final suite passed 1,227 tests in 164.166 seconds
with four skips; log `/tmp/caplab-native-startup-make-check-final.log`.
Ruff F checks, Python parsing and `git diff --check` passed. The native and
resource diagnostics are separate from the unit-test count. No probe source
changed after the final live runs and final suite.

The final native observations SHA-256 is
`8b43451f04e95b3a3472ed6c41dcb194fdc537cc6a6c2b719935e0ea20201c7d`;
its verification receipt is
`b441c181ef2c079c8f32991e328a737a635b58bf95814065a4bca34ca161b037`.
Final resource observations SHA-256 is
`919a5143caf52a746cdeeaa3e2978288a9776039098dd2efe4d58f5eb298c2aa`;
its verification receipt is
`8353ba71014774220890862d59641c5c0f3f957381cd5e4387bd63efd629c4b7`.

CAPLAB-84 and CAPLAB-85 remain open. This work fixes an instrument startup
defect that could otherwise be mistaken for a native-harness failure. It does
not finish containment, account/serving configuration, complete Binding and
invocation evidence, representative repair measurements, blinding, coding
accuracy or independent reviewer judgments. No planning state or acceptance
was changed.

## Advisory provenance and closure

Pincite's release gate passed at
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Packet `pkt-0ca9d326dc2b0ce5`, content SHA-256
`0ca9d326dc2b0ce5725668d70cc33d15b93606fad55fc2bceaf1597511cb8f18`,
uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and retriever `retriever-ec995ecdd083b2c8`.
Repository-contract precedence, evidence before intervention, structured
cleanup and explicit failure policy informed the diagnostic. The later device
correction follows the retained native syscall and controlled mount-access
observations and the explicit authorization extensions above.

The 15 remaining packet obligations are individually retained as nonmaterial
with rationale: no toolchain/language migration, public runtime API change,
or new decoding/normalization policy is proposed. Existing byte-preserving
capture APIs and local Python/probe conventions remain in use. No doctrine
packet grants execution or acceptance authority.

Consolidated verification is `/tmp/caplab-native-startup-verification.json`,
SHA-256 `10f1a8d7a68ff1085a55272ce623b409a34af237dc201bc4bb96e96df8eb9c1e`.
It retains 761 artifact entries, complete advisory packet/evidence/citation
bytes and the individual obligation classifications. The deliberately oversized
sparse refusal fixture is recorded by size with an explicit unhashed-content
reason; other listed files have content hashes. Four citations were classified
valid. Eleven named advisory scratch files were deleted after consolidation.

All six generated units were rechecked as unloaded and their cgroup paths as
absent. There were five actual native launch invocations, including one traced
Claude invocation, one separate pre-release refusal, ten resource fixtures and
two model-free device variants. All native outputs remain in private custody.
The accompanying commit consumes the scoped execution allowances; no model
serving, tracker write, external message, crash-report submission, push or
independent acceptance occurred.
