# Enforce the selected identity on scripted native requests

Baseline `c1a2abd`. The previous turn made implementation and native-integration
progress. The current CAPLAB-79 contract requires configured identity, native
observations and provider evidence to remain distinct, and explicit off-pin
identity to stop continuation. The scripted endpoint currently validates shape
and lineage but accepts any request model/reasoning fields. Its inspector also
does not compare those raw fields against the selected invocation.

Under ADR 0026, select a request-boundary consistency check for the fixed
diagnostic. Require exact model, reasoning effort and requested summary detail
on every response request, including warmup and continuation. Derive expectation
from the selected invocation's model/effort and the existing detailed-summary
configuration. Retain the raw request first; refuse missing, malformed or
off-pin identity before child observation, response construction or sending.
Preserve already completed responses if a later request fails. The fixture
cannot authenticate an actual provider, and this check must not claim it does.

Authorize changes to the existing scripted fixture/payload/bootstrap/inspector,
their protocol and handshake tests, the diagnostic contract and this record.
Use newly constructed local socket fixtures with fabricated request metadata;
add no native execution, model call, spend, dependency or general serving API.
Preserve the current payload, handshake, deadlines, containment, quarantine and
transport-error semantics. Update existing test requests with explicit valid
identity so their original failure paths remain exercised. Test absent/wrong/
malformed identity, both generated turns and warmup, borrowed expectation
mutation, raw failure retention, and refusal before child acknowledgement.
Run focused and full checks and commit locally after verification.

Read-only comparison may verify the three exact retained request artifacts from
`/tmp/caplab-scripted-capture-native/run/safe-retained/4`, anchored by the
`c1a2abd` result SHA-256
`397126d0a9410699993c2efb57cc07572da5a201666a474ff64e111a843303ba`.
Their request hashes are
`1bcb1c3232cf5c176eb01c40c784b0b15610f24a2a2b8aecea359eb853d7dd7d`,
`ea91f8fdf05475f19640a2b990365d00c205faedf0217282022a9844d6f58246` and
`5f4c6129134b6a755029d60d56f5bed311774923007f0c0c6a23b65b9bdece53`.
They visibly name the selected model, max effort and detailed summary. This
authorizes a new bounded consistency observation with explicit source/result
lineage, not historical result replacement, registration or proof that the new
online gate executed during the old run. Keep all originals unchanged.

Private verification and advisory artifacts use `/tmp/caplab-wire-identity-*`.
No tracker writes, messages, push, unrelated worktree/service changes or old
attempt reuse. Stop on source drift, unclear failure ordering or unexplained
regressions. The scope expires at its verified local commit. Full capture,
containment, representative repair measurements and roadmap completion remain
separate requirements; this repair closes one demonstrated identity gap.

## Repair and controls

The new negative control sent the valid fixed tool request with a different
model. At the baseline it received a scripted response, failing the expected
connection refusal. The repaired endpoint copies a required three-field
expectation at construction, checks each raw request after retention and basic
protocol validation, and records only the matching model/effort/summary fields.
The bootstrap derives model and effort from its selected plan. The offline
inspector compares the anchored raw request fields and recorded observation
against that same selected plan and the fixed detailed-summary configuration.
The pure checker resides with the existing payload helpers so offline
inspection does not acquire a websockets dependency. Capsule imports use its
explicitly mounted files; host imports use the repository package.

All 25 protocol/handshake test methods pass, including 44 malformed/off-pin
combinations across initial generation, warmup, continuation after warmup and
tool result. A separate missing-listener control confirms identity refusal
precedes any child-observation connection. The wrong request remains in raw
custody with no corresponding response file. Later failures preserve earlier
responses and stop further generation. Expectation mutation after construction
does not change the selected fields; invalid expectation maps are refused.
Additional reasoning metadata remains in raw bytes and does not become an
unsupported full-configuration claim. Existing close-error and deadline
controls still exercise their original failure paths with valid identities.

The read-only prior-capture check reverified its independently anchored full
capture manifest and the three request hashes. All three match the selected
model, max effort and detailed summary. The resulting new observation says
`new_gate_executed_in_historical_run=false` and preserves the old result. The
new inspector requires per-request observations absent from the old run;
original claims remain tied to the original pinned inspector.

Leaving the endpoint unchanged allows contradictory native wire configuration
to receive scripted responses. Checking only after the run would retain the
contradiction but allow subsequent fixture actions; checking only the command
or rollout observes different surfaces. Select both immediate refusal and
later raw-byte verification. Keep one small pure predicate shared by these two
consumers, without new protocol abstraction, source discovery or serving API.
This is an explicit semantic repair, not a behavior-preserving refactor.

## Full-suite failure investigation

The first full suite ran 1,439 tests with four skips and one failure in the
unchanged real child-handshake control: its launcher closed the control channel
before sending the expected completion byte. The surrounding assertion hid the
already retained per-case launcher stderr. Before any native attempt, extend
this scope to expose that bounded diagnostic in test failures and investigate
the same fixed local control. Any repair must preserve authentication refusal,
freeze/thaw, descriptor restoration and owned cleanup criteria. No native-agent
retry or looser production handshake is authorized by this investigation.

An unforced isolated recheck passed. The production helper checks SO_PEERCRED
before reading the request, so its wrong-peer refusal can close the socket
before the sender writes. A deterministic control waits for socket readability
after connection in that case, forcing the early-close schedule. It reproduced
the same outer missing-completion failure and exposed `BrokenPipeError` in the
launcher. The original run did not retain that inner diagnostic in its public
log, so its exact inner exception remains unavailable.

The test client now interprets BrokenPipeError during send, like connection
reset during receive, as an empty acknowledgement. It still requires the exact
supervisor-side peer refusal, rejects empty acknowledgement in the success
case, checks thaw and descriptors, reaps children and removes owned resources.
The forced early-close case passes. No production handshake predicate, timeout
or error behavior changed. The failure diagnostic remains in the standing test
so later failures retain their per-case cause.

## Conditional one-attempt integration authorization

After the final full suite completes successfully and current source pins match
preparation, authorize exactly one new offline installed-native diagnostic under
ADR 0026 at `/tmp/caplab-wire-identity-native`. Its preparation SHA-256 is
`9aa8ab28f22ae3b420580a77c2782e854f848e04978fadcdf50e316b38a0bd31`.
The subject remains Codex 0.153.4 / `codex-terra-max` / `gpt-5.6-terra` / max,
with the fixed scripted tool exchange, fabricated readonly auth and existing
loopback-only unshared capsule. Model inference, provider access, real tokens,
paid calls and replacement attempts remain unauthorized.

Preserve native/capture/unit/outer 30/45/90/100-second limits, 256/512 MiB
workload/unit memory, zero swap, 128/192 tasks and all prepared byte/entry caps.
Use the repository's exclusive consumption receipt before launch and owned
`caplab-scripted-native-<uuid>.service` cleanup. Freeze implementation, tests,
this authorization, inspection criteria, preparation and verification logs
before execution. Failure consumes the allowance.

The new frozen inspector must verify exact request configuration on all three
requests if the native client emits its observed warmup, or both generated
requests if it does not; all previous kernel/trace, tool/final, raw protocol,
custody, quarantine, resource and cleanup criteria remain required. Either
clean closure or the already classified sole missing-close-frame error may
support bounded observations, but that error must retain bootstrap exit 1 and
a failed native-attempt result. No other failure is cleared. Stop on source
drift, unknown identity, containment/quarantine failure or incomplete cleanup.
No historical capture, independent acceptance, study eligibility or roadmap
completion follows. This allowance expires on consumption or local commit.

## Native verification

The final full suite passed 1,439 tests in 165.636 seconds with four existing
skips. Ruff F and diff checks passed. The conditional gate therefore permitted
the one native integration. Its 170-record frozen release has SHA-256
`95c71aefff449bd0f69d8181c326ac64604d3beeba0bb07bac82c6e8e14735ce`;
all records and input/runtime manifests still matched after execution.

The attempt was consumed exactly once. Its result has SHA-256
`e119660e7c3be488184d799e0523271ce7534f5e463ab35946388a2b23d22c36`.
The pinned inspector returned `verified-observation` with
`request_configuration_verified=true`; output SHA-256 is
`c898a107e6a3427c1c52330bd977b4f5976d5aee6c970c98e82ce187b58ae9ce`.
All three requests, including warmup, explicitly named `gpt-5.6-terra`,
`max` effort and `detailed` summary. The new online observations agree with
the retained raw requests and selected configuration. The actual capsule
also verified the individually mounted fixture/payload import path.

The previous kernel/source/tracer/child-execution, tool/final, raw protocol,
custody, quarantine and resource checks passed. The freeze interval was
230.089069 ms and the handshake 244.623799 ms for this diagnostic only.
The trace retained 1,422,201 bytes and writable mounts 1,322,311 bytes across
131 entries. The selected quarantine checked 121 files and 4,955 decoded
trace strings. The owned unit
`caplab-scripted-native-bbaa281f2c814a5ab4ef87e9ca0423dc.service` and cgroup
were removed. No producer or inspector source changed after release.

The fixture again retained `ConnectionClosedError: no close frame received or
sent`. Native shutdown was normal, but bootstrap exit 1 and the CLI's failed
attempt result remain unchanged. No replacement ran. Request consistency is
not provider authentication, full capture, serving parity or reviewer quality;
all corresponding qualification/study claim limits remain in force.

## Advisory and final custody

The validated Doctrine release is commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, Doctrine `doctrine-f6bbb5196a3f8bf9`
and retriever `retriever-ec995ecdd083b2c8`. The two evidence passes yield final
packet `pkt-032d48671c75d3a4`, content SHA-256
`032d48671c75d3a4507bbfbdfa9963cc83fd03b378e8a79f85cf085ccca0ab81`.
The intermediate packet was read in full; its final diff changes only packet
identity and the discharged obligations. Four initial and six final used
concepts were classified as valid packet citations. Advisory ceiling is
execute; repository delegation supplies actual authority.

All 19 remaining obligations are retained. Fourteen concern deduplication,
async UI, symbolic configuration references and relevance ranking, none changed
by this repair. Three concern paging/monitoring, which it does not introduce.
The general latent-risk inventory obligation exceeds this bounded change's
claim; no exhaustive audit is asserted. Those 18 are nonmaterial here.
Eval-versus-serving parity remains material to representative measurement, so
that broader conclusion is withheld. Exact native request observations support
the narrower request-configuration consistency claim.

The refactor-now conflict is resolved by repairing the demonstrated boundary
and its existing consumers without reorganizing adjacent capture modules.
The upfront-versus-feedback conflict is resolved by preserving the refusal and
custody criteria, then reproducing the request defect and the early-close
control failure before fixing them. A socket reset or broken pipe is not a
successful acknowledgement; it is accepted only as refusal in a case where
the supervisor separately establishes the specified rejection.

The private manifest `/tmp/caplab-wire-identity-verification.json` seals the
original failures, controls, source/release pins, native result, separately
anchored historical consistency observation and advisory provenance. Original
captures and results remain intact. Only verified advisory scratch embedded in
the manifest may be removed. Verify all current implementation/test hashes
before committing this scope locally; no push or tracker write. The preparation
scope expires at commit and the single native allowance remains consumed.
The overall goal and representative repair shakedown remain active.

The sealed manifest SHA-256 is
`2221eea4081a6f81909bf983cfdd58e9bc9744682a61083aacdc101f12e8f9d1`:
167 artifacts, 164 current source pins and 17 embedded advisory scratch files.
Each hash was checked before removing only the 17 embedded scratch files.
