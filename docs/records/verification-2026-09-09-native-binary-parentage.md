# Verify the native binary's relationship to its authenticated launcher

Baseline `ae8b5b0`. Primary agent under ADR 0026 and the continuing CAPLAB goal.

## Decision and prospective authorization

The preceding native trace verifies the authenticated launcher exec but omits
its child creation. The committed process-creation reader now verifies explicit
PID-namespace translation and ordinary parentage in real synthetic kernel
controls. Select one fresh installed-native diagnostic with combined exec and
creation tracing. Verify the binary's exact argv/environment separately from
the launcher and compare the creation relationship using the same protected
trace. Do not infer the relationship from adjacent records or source code.

Authorize this record and private artifacts under
`/tmp/caplab-native-binary-link-*`. Derive from the retained native launch
adoption probe/support, preserving original paths and hashes. Change owned
artifact/unit paths and host strace options only, plus pre-release supervisor
observations of process-leader identity and the mounted launcher, Node and
native binary file identities. Add `--decode-pids=pidns` and
`clone,clone3,fork,vfork` to the existing exec syscall selection. Preserve exact
bootstrap/guard bytes, native installation, prompt, fixed responses, effective
launch configuration, fabricated auth, quarantine, namespaces, devices, procfs,
descriptor handling and all previous resource limits. Pin current Node bytes
separately without claiming that earlier diagnostics pinned them.

Derive the expected native binary command from the fixed installed wrapper:
the selected binary path plus unchanged command arguments after argv[0]. The
child environment adds the inspected managed-package root and package-manager
marker; no arbitrary environment override is authorized. Compare this
construction with the prior retained diagnostic before the new launch. Seal
preflight source/installation identities and expected construction, then consume
exactly one native attempt in a fresh root and owned unit. No automatic retry.

Use only the isolated local two-response scripted fixture and fabricated,
sealed read-only credentials. No actual credentials, external endpoint,
provider inference, model spend, historical research copy/admission/rewrite/
purge, tracker write, message, push or independent acceptance is authorized.
Preserve unrelated `docs/designs/`, worktrees, services and prior evidence.
Run focused shared checks and inspect private source before launching.

Retain 30/45/90/100-second native/capture/unit/outer limits; 256/512 MiB child/
unit memory, zero swap, 128/192 PIDs; 300,000-byte native streams, 1 MiB/1,000
task entries, 8 MiB/1,000 native-output entries, 40 MiB/2,000 retained-mount
entries, 2 MiB trace, 8 MiB native files and no cores. Keep five 64 MiB tmpfs
mounts, the closed six-device profile, 1 MiB wire/decoded HTTP body allowance,
32 requests and two response POSTs. Stop on source drift, timeout, unsupported
trace semantics, quarantine, any unexplained verification or cleanup failure.
Keep partial custody and diagnose without another native attempt. Stop only
the owned unit and verify it and its cgroup are absent.

Afterward verify intent/selection/configuration/guard/trace anchors, protected
tracer custody, authenticated launcher exec, exact selected binary exec,
translated parentage, pre-release mounted-file identities, captured task/runtime
source links, tool witness, final bytes, resources, known-value scans and cleanup.
Keep the strict final-message linker's existing treatment of transport errors.
Parentage and pathname/source consistency do not independently prove every
binary mapping, cwd, descendant or output writer. Full Binding, capture
completeness, provider capability and study eligibility remain unestablished.
Commit the verified record locally; authorization expires at that commit.

No change preserves the missing parentage evidence. Changing the native
workload or relaxing the root linker at the same time would obscure the
relationship under test. This run changes the observation apparatus only;
it makes no timing, capacity or untraced-behavior equivalence claim.

## Preflight and release decision

The derived probe and guard retain exact bootstrap/guard bytes. The canonical
policy plan and complete native installation manifest match the prior diagnostic.
The expected binary command/environment also match its independently anchored
native exec at PID 3586007, line 8. A separate internal sandbox invocation of
the same binary exists, so the new verifier selects by full argv/environment
and requires exactly one match; pathname or adjacency alone cannot select it.

Seventeen current repository source pins are recorded. The explained change
from the earlier diagnostic is `exec_trace.py` plus the new process-creation
reader at `ae8b5b0`. Node is now separately pinned at SHA-256
`bc17c508ffeed0ec622934f9b7fa72f8e78da65350e63c3eceb56fa688aa5e12`.
The launcher and native binary hashes still match the installed manifest.

All 15 shared trace tests pass. Five derived synthetic guard controls pass with
the combined trace and new mounted-file observations: the successful fixed Python
execution waits for both seals; wrong parent, invalid port and either injected
seal failure prevent release. No installed native binary executes in these
controls. The fixed control mounts expose the same read-only installation
identities needed for the pre-release checks.

Proceed with the single authorized native attempt using probe SHA-256
`6141ca5e0389a4b0dafa8cfb9905938007d5d2d4fe77552467316af49b396b97`
and support SHA-256
`b221b96846a1f7fe965311bedf9ea74c19879ad30bec4a9993e780e7c193d416`.
Preflight, derivation, controls and logs are retained under the private prefix.
The next launch consumes the allowance on either success or failure.

## Failed native attempt and preserved observations

The allowance was consumed by unit
`caplab-native-binary-link-9505dabb5cad45c996439e9a3385987d.service`.
The attempt failed: the fixed bootstrap reports `native_timed_out: true` and
native return code -9 at the 30-second deadline. The native launcher and selected
binary have terminal SIGKILL records. Bootstrap and outer service return 1.
The supervisor withheld `observations.json` and its success report. The unit
is not found and its cgroup is absent. No retry occurred.

Before timeout, the fixed command completed with exit zero, its 26-byte UTF-8
witness was retained, and the exact 40-byte final response and turn.completed
event were emitted. Both scripted response POSTs completed with status 200.
Fixture errors, auth changes, refresh, quarantine, memory max/OOM and PID max
counters are absent; final child PID count is zero. The trace is 1,779,842 bytes,
below its 2 MiB bound. Completion output does not establish normal native exit.
The trace lacks sufficient timing/cleanup detail to attribute the timeout to
tracing overhead, native shutdown or another cause. No performance conclusion
or limit increase is selected.

The anchored launcher and Node exec checks still pass for authenticated process
leader 3643245. The raw trace has a clone return at line 20 naming child 11 in
the workload namespace, host PID 3643254. Line 21 contains the expected native
binary exec with exact argv/environment. A separate invocation at line 2210
has different argv/environment and is not the selected invocation. These are
raw scoped observations, not a passing binary-parentage verification.

Both the public binary exec check and process-creation check refuse with
`missing or abbreviated clone flags`. The offending native thread-creation
records contain `CLONE_THREAD` plus `0x400000`; they are not abbreviated. The
closed parser accepts named flag tokens but rejects that numeric token, including
in creation records unrelated to the selected parent edge. The installed Linux
header identifies 0x00400000 as `CLONE_DETACHED`; the installed clone manual
calls it historical and usually ignored, with exceptions. This source context
supports a subsequent explicit parser repair investigation, not bypassing the
current refusal or treating all numeric flags as safe.

The combined trace SHA-256 is
`3bffe6a7154149140c8e194ff3c4d3e785841d6e094b8b5945ab502ae0a814af`.
Source, Node and native installation pins still agree. The guard's mounted
launcher/Node/binary identities agree with their pinned source files; configuration
sealing and recorded tracer consistency pass. The first diagnostic inspector
stopped at the public parser refusal and retained that failure. A separate
failure auditor records the raw observations and both public refusals without
changing the parser, original trace or verification criteria.

## Post-failure custody inspection

`/tmp/caplab-native-binary-link-failure-audit.py` verifies retained task,
collection and mount receipts with explicitly post-failure caller anchors.
These anchors are not an original supervisor success report. Its first local
view omitted symlink target bytes from the aggregate; the existing custody
checker refused. The corrected auditor includes those bytes, and the first
source/log remain retained. No captured bundle was changed.

Verified retained mounts contain 918,416 bytes across 128 entries. The auditor
checks 110 files and 6,327 decoded hexadecimal trace strings against configured
forbidden synthetic values without a match. Task/root linkage and tool pairing
remain available with process return 1. Exact witness and final bytes agree,
but the strict final-message linker still refuses the retained transport-error
events. Capture integrity, final-file agreement and native process success remain
separate. Binary parentage is unverified, full capture completeness is unknown,
and study eligibility is false.

The next material work is to reconcile the observed numeric clone flag with
explicit syscall semantics and repair the verifier with regression and kernel
evidence. Normal native shutdown also remains unresolved. This failed run must
not be retried under its consumed allowance or promoted after a parser repair.

## Advisory review and remaining obligations

The release retrieval gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial `pkt-36b1457b71f5bf33` and final Markdown packets were read. Five typed
records preserve authority, incident, source, controls and the failed native
observation. Final packet is `pkt-eadffbd26a22d3ab`, SHA-256
`eadffbd26a22d3abb9462a5b1ecba36d224254f6c97c3f5c7ddec1236cffd72a`.
Versions remain corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`, schema
`evidence-packet/3`.

All 25 missing obligations remain visible. Eighteen concern unchanged
deduplication (3), ingest populations (4), asynchronous UI (4), declarative
references (3) and ranking (4), and are nonmaterial to this diagnostic. Three
external-capability obligations and evaluation/serving parity remain material
to broader integration and study readiness; those claims are withheld. Three
monitoring obligations are nonmaterial because no service or paging policy
changed. Applied guidance is repository-contract precedence, evidence before
intervention, separating semantic and structural work, preservation of the
fixed workload, and authority-bounded action. The performance routes in the
initial packet do not authorize a performance claim from this one failed run.

## Repository verification and disposition

No repository runtime or test source changed. The last full check remains
1,368 tests with four skips at `ae8b5b0`. This turn reran all 15 trace tests and
five synthetic guard controls, and observed one failed installed-native attempt.
Ruff F passes for the live probe/support, controls, intended verifier and final
failure auditor. These checks do not override the failed native outcome.
Current Plane snapshots are retained as planning provenance; no item was changed.

## Final custody

Manifest `/tmp/caplab-native-binary-link-verification.json`, SHA-256
`59235207f65690b7fb2701e3258d38c22d311f13415aeab547d9ca37f3b426a3`,
retains 194 artifacts, 17 repository source identities, four additional
inspected sources and 11 embedded advisory scratch files removed after exact
verification. Artifact, source, typed-evidence provenance and embedded-byte
checks pass. Five citation observations classify as valid packet citations.
The previous diagnostic's anchors remain unchanged, and this run's unit and
cgroup were checked absent again.

This record preserves a failed diagnostic and actionable parser evidence.
The native allowance is exhausted; the local commit closes its authorization.
No repository runtime change, model spend, tracker write, push, historical
research effect or independent acceptance occurred. The broader CAPLAB goal
remains active.
