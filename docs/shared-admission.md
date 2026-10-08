# Opt-in shared admission for live Revbench

This candidate guards Caplab's existing one-shot live Codex Revbench custody.
Both assigned `version-probe` helpers and `native-review` processes participate.
It does not construct a Binding, substitute a harness, authorize an experiment,
or qualify a measurement. Unenrolled execution keeps its existing behavior.
Local fixtures, advisory `pool_runner`, retrieval, preference and review-dissent
runners remain unenrolled. Other native harness adapters are outside this slice.

## Enrollment and use

Use a Quartermaster SDK reporting interval-v1, response protocol v2 and incident
reconciliation through `quartermaster admission capabilities`. The deployed
`/home/halbritt/.local/bin/quartermaster` reports source tree
`sha256:af3621e6ddd0062cbc46ec5e37bb3c31f8321dd88a4024a8495055aac6bfa247`
at this candidate's verification. It supports policies 1/2 and reducers 1–3.
The adapter sends explicit request-v2 profile/host selection, including under
policy 1; policy 2's `request-max-slots` reader accepts this slice's one slot.
Caplab owns its implementation, native operation and rollout choices.

Create the shared home/policy/catalog through Quartermaster's documented public
interfaces. The same governed pool must have one designated home across enrolled
consumers. The selected account must declare its actual shared `quota_pool_ids`;
Caplab does not infer them from provider percentages. Policy must enroll the
`caplab` namespace/caller, permit the selected account/route, and provide both
finite guarded-launch budgets and concurrency. Numeric test policy is synthetic,
not a suggested production cap. Observation refresh is a separate local import
operation; Caplab never collects provider data.

Enrollment is an explicit JSON object with exactly these fields:

| Field | Required value |
| --- | --- |
| `schema_version` | `caplab-shared-admission-enrollment/2` |
| `sdk_source_tree_sha256` | Exact prefixed digest from `admission capabilities`; checked before each operation |
| `cli`, `cli_sha256` | Absolute Quartermaster CLI path and raw executable SHA256 |
| `home`, `home_id` | Absolute shared home and the policy's designated home identity |
| `release_path`, `release_sha256` | Absolute retained catalog release path and raw file SHA256 |
| `overlay_path`, `overlay_sha256` | Absolute Caplab overlay path and raw file SHA256 |
| `policy_path`, `policy_sha256` | Absolute shared admission policy path and raw file SHA256 |
| `observations_path` | Absolute local quota-observation array file; intentionally refreshable |
| `entry` | Exact enabled projected entry key from `caplab catalog` discovery |
| `caller_id` | Caller enrolled in the shared policy's `caplab` namespace |
| `custody_domain_id` | Actual existing `FilesystemLiveExecutionRuntime.custody_domain_id` |
| `binding_id` | Existing native manifest's Binding identity |
| `credential_profile_sha256` | Raw SHA256 of the Binding runtime's resolved `credential_profile_ref` bytes |

All values are nonempty strings. File/profile SHA256 values are unprefixed hex;
`sdk_source_tree_sha256` includes `sha256:`. Version 1's original 17-field
configuration remains readable for historical recovery and has no source-tree
pin; version 2 adds precisely that field. New enrollment should use version 2.
An incompatible SDK refuses before a native process claim. Capabilities identify
local source bytes, not authenticated installation or provider identity.
The selected catalog tuple/profile is checked against the complete existing
Binding/native-system contract, including native harness/model/effort/config.
The native credential profile bytes are pinned separately. These declarations
are not authenticated provider account identity: Caplab's owner must establish
the catalog-account/actual-credential join before installed enrollment. Neither
Caplab nor Quartermaster can manufacture that identity from quota observations.

Use the existing source-only live `execute` invocation and add
`--shared-admission /absolute/enrollment.json`. That option is intentionally absent
from the ordinary local-fixture CLI. Python callers import
`SharedAdmissionEnrollment` from `caplab.revbench.shared_admission`, read the
configuration with `SharedAdmissionEnrollment.read(path)`, then pass it as the
`shared_admission` keyword to the existing `caplab.revbench.execute` API.
Native authorization, custody root/domain, apparatus receipt, trial assignment
and credential custody remain required. The CLI is control-plane tooling;
its invocations are not measured outer harness creations. It runs outside the
contained harness with an empty environment and no credential arguments.

The enrollment is retained before any native process claim. Resumed executions
must supply the identical enrollment. An old unenrolled execution intent cannot
be enrolled after claim; omitting the option cannot disable retained enrollment.
Changing any pinned input refuses. The CLI executable digest alone does not
pin its interpreter/libraries; version 2 additionally checks the SDK source-tree
identity. Installation provenance remains a separate deployment concern. New Caplab source requires a fresh
prospective clean apparatus receipt/native authorization, not an active run's pins.
This source candidate adds supervisor observations and control-plane calls; it
is not a claim that an existing authorized apparatus already includes them.

## Creation, closure and recovery

Each assigned process requests one concurrency slot and a finite bound of one
outer creation using its authorization-independent native effect identity.
Quartermaster's charge reader may impose a larger concurrency charge; Caplab
does not override it. The native custody claim remains one-shot. Only a fresh
retained Quartermaster `prepared` response permits crossing `Popen`. Reserve or
prepare latency consumes the original native deadlines, and host-closure checks
remain immediately before launch. Replayed/lost responses grant no launch right.

Successful `Popen` counts one outer child even when contained exec subsequently
fails. `Popen` OSError leaves possible creation unresolved; native `not-invoked`
is preserved but is not translated into proof of zero children. A completion
produced entirely before `Popen`, together with the consumed native right, can
truthfully retire a permit as `not_created` and return unused capacity. A crash
between a permit and a receipt retains uncertainty. No blanket timeout/expiry
release is added.

Root wait and complete streams alone do not establish tree closure. Bubblewrap
0.9.0 reports the initial application exit independently of the namespace init's
lifetime ([source](https://github.com/containers/bubblewrap/blob/v0.9.0/bubblewrap.c)).
For enrolled processes the existing supervisor inspects only its owned outer
process's direct children, identifies the actual child namespace PID1, and opens
a reuse-safe Linux pidfd. Boot identity, start ticks, parent and namespace IDs
are retained. Settlement additionally requires observed init death, durable native completion/root wait, the pinned
PID-namespace/death-on-parent plan, and a
proved end timestamp. PID namespace init death closes that namespace's process
population ([Linux contract](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)).
No daemon, helper launch, persistent PID registry, additional privilege, new
harness argv or new native measurement schema is introduced. Missing `/proc`
access, pidfd support, a fast unobserved init or missing native completion
retains capacity. Output truncation remains a native measurement failure; it
does not defeat an independently observed positive namespace/tree closure. Namespace inspection is bounded by the original native time budget.

Command `--now` uses full-resolution host UTC; native measurement timestamps
keep their existing one-second schema. Birth evidence separately samples host
UTC, monotonic nanoseconds and boot ID immediately around `Popen`. It retains the
closed possible-time interval, not a midpoint or an invented event instant.
End evidence brackets the same held init pidfd's last positive liveness and its
positive death observation. If the descriptor was acquired but no positive
liveness sample was recorded, the retained outer-process precreation sample
can supply the lower bound: the recorded namespace init must be a child of
that exact positively created outer process. The closure sidecar retains
`lower_bound_basis` to distinguish these cases. Both bounds still require the
same boot and ordered UTC/monotonic clocks. This fallback cannot prove death
without the held init descriptor and does not repair an unobserved init or an
already retained closure with unknown time.
The final observation waits at most 50 ms, bounded
by the original native deadline; monitor reap remains insufficient evidence.
Reversed UTC/monotonic or changed-boot brackets retain unknown time. These are
trusted host-clock observations, not hardware clock qualification.

Fixed windows with fractional cutoffs and rolling windows are supported through
SDK interval accounting. The SDK conservatively counts each creation once in
every applicable window and ages rolling consumption from the latest possible
birth. On a fresh execution the fixed-window deadline fit is checked before any
process claim; retained recovery preserves the original deadline. The native
supervisor still refuses at zero remaining authority. Neither interval upper
bounds nor shared latency extend that authority. A positive birth whose bracket
may violate validity is counted and retained; it is not permission to launch late.

Before `Popen`, a control-plane failure completes the consumed native right as
not invoked and retains a separate full-resolution observation of that closure.
Recovery inspects the existing exact admission/attempt, never prepares again.
A possibly committed permit plus this positive prechild completion may record
`not_created`; a crash with no completion remains held. `clock_order`, bounded
`admission_busy`, invalid replies and uncertain transports remain visible through
raw transport/control-fault sidecars and a returned shared `hold` when recovery
cannot finish. Custody conflicts and pin changes still propagate as errors.
Transient failures of the per-operation SDK capability probe (transport error,
timeout, nonzero exit, oversized reply or invalid JSON) use that same recoverable
control-fault path. A valid reply declaring incompatible capabilities or a
changed pinned SDK identity remains a hard error. Before creation the native
right closes without launching; after creation capture continues and recovery
reuses retained evidence. A failed probe never supplies launch permission.
After `Popen`, lost creation replies do not abort native capture: the already
retained birth preimage is retried on the same attempt after native completion.
Positive tree/right closure uses ordinary settlement first. SDK incident
reconciliation can then close custody with unknown positive birth or a retained
validity violation, freeing slots/unused allocation atomically while retaining
one debit or timing hold and the incident. No unresolved child is retired by it.

Immutable additive sidecars stay in existing private native custody, outside
measurement/qualification documents. They retain actual command inputs/replies,
allocation/permit receipts, possible-creation facts and closure witnesses.
`SharedAdmissionEnrollment.reconcile_session(session)` reconciles only retained
claimed processes, including sealed executions; it never acquires a right or
spawns. Normal sealed execution recovery invokes it too. A lost allocation receipt
can be recovered from the designated home's exact request/holder/namespace record.
Positive retained closure can finish settlement after restart; a lost pidfd with
no durable positive closure cannot be reconstructed as death and remains held.
Shared status is available through Quartermaster's public `admission status`.
Native completion and qualification are separate from shared settlement.

## Local verification and remaining enrollment

Run Caplab's existing `make test` preservation suite. The additional real shared
CLI/custody/process controls are enabled with `CAPLAB_TEST_SHARED_QM` set to an
absolute SharedAdmissionLedger-capable CLI path. Without it those integration
controls explicitly skip; standalone Linux pidfd/namespace controls still run.
Tests use synthetic catalog/account/policy/observation inputs and owned local
processes, never provider/model calls. They exercise exec failure, prechild refusal,
unknown creation/time, same-key recovery, quota change, shared other-namespace
capacity, actual tree closure, sealed recovery and immutable enrollment.
Host namespace refusal is an explicit unavailable qualification result.

Advisory `pool_runner.invoke` still creates children through its existing
`subprocess.run` path without this Revbench custody protocol. Local-fixture
Revbench, retrieval, preference and review-dissent also retain their native paths.
`scripts/caplab-ladder-subject.py` and `scripts/caplab-artifact-rater.py` also
invoke Codex directly and are unenrolled. These paths require separate
producer/custody integration before claiming
full Caplab enrollment. This candidate neither blocks those paths nor claims
full shared-catalog/admission goal completion, deployment, qualification or
acceptance from local tests.
