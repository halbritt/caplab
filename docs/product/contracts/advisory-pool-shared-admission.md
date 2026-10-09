# Opt-in advisory pool shared admission

This is a prospective administration under ADR0068. Existing unenrolled calls
keep their previous subprocess path. New pool runs can reserve a shared account
pool's concurrency and finite guarded outer-launch budget through the deployed
Quartermaster SDK. Provider percentages remain separate veto observations.
ADR0069 adds interrupted case recovery. ADR0072 adds the explicit-byte release
gate for future administrations; the block-writer barrier alone is insufficient.

Use an owner-controlled, durable, nonrollback output directory, disjoint from
the model-visible case workspaces. Do not copy it to restart an assignment in a
fresh domain. Initialize its public custody identity without acquiring rights:

```sh
mkdir -m 700 /absolute/new-pool-run
caplab advisory admission-domain --out /absolute/new-pool-run
```

Prepare the existing `caplab-shared-admission-enrollment/2` document with the
explicit SDK executable/source-tree pins, one designated home, pinned policy,
catalog release and overlay, mutable observations path, selected catalog entry,
caller, prospective Binding identity and the returned custody domain. For this
adapter `credential_profile_sha256` hashes the canonical UTF-8 JSON (sorted
keys, compact separators, no newline) below:

```json
{"schema_version":"caplab-pool-configured-profile/1","profile_id":"EXACT_CATALOG_PROFILE","host":"EXACT_CATALOG_HOST","account_id":"EXACT_CATALOG_ACCOUNT","config_home":"EXACT_NATIVE_HOME"}
```

`config_home` may be null when the catalog says null. This is public configured
profile metadata, not credentials or authenticated provider identity. Its
account/profile/home and the actual native command must match the catalog. Do
not supply a convenient account label for an unrelated native profile. Actual
credential-to-account authentication/qualification remains separately evidenced.
This adapter admits only tuples in the canonical native-agent-systems contract;
a missing current tuple needs a Caplab-owned contract disposition, not a proxy.

Create a configuration with exactly these fields:

```json
{"schema_version":"caplab-pool-shared-admission/1","enrollment_path":"/absolute/enrollment.json","enrollment_sha256":"RAW_FILE_SHA256","declaration_sha256":"NATIVE_DECLARATION_DIGEST","valid_until":"UTC_ADMINISTRATION_EXPIRY_Z","native_policy_path":"/absolute/canonical-native-agent-systems.json"}
```

The declaration digest is `caplab.advisory.run_spec.declaration_digest` of the
parsed YAML, preserving YAML types. The policy is verified against Caplab's
canonical contract digest. Supply a finite original administration expiry that
fits the selected SDK windows; do not move it to make admission pass.

```sh
caplab advisory pool-run --backend EXACT_ENTRY \
  --backends-root /absolute/declarations --registry /absolute/substrates.jsonl \
  --out /absolute/new-pool-run --seed 7 --shared-admission /absolute/pool-config.json
caplab advisory admission-reconcile --backend EXACT_ENTRY \
  --backends-root /absolute/declarations --out /absolute/new-pool-run \
  --shared-admission /absolute/pool-config.json
```

Python callers pass `shared_admission_config` to `run_pool`. Lower-level native
callers use `PoolAdmission.read`, then `invoke(..., admission=controller,
launch_key=exact_assignment)`. `measure_case` needs its frozen
`assignment_prefix` and carries arm/replicate identities itself. The new native
administration needs Bubblewrap and PIDFD support; `CAPLAB_NO_SANDBOX` cannot
bypass enrollment. Recovery uses `recovery=True`, including after expiry, and
never reserves, prepares, invokes or treats a numeric PID's absence as death.

Each assignment gets an exclusive directory before any shared operation. A
prepare commit with lost reply cannot create a second child. A positively
closed pre-Popen right can reconcile an unused permit. Actual Popen success is
retained before observer/SDK work; child-side exec failure counts one. An
uncertain constructor/exec boundary keeps a possible launch outstanding. Native
completion plus death of the held namespace-init descriptor is required for
tree settlement. Output preimage drift refuses reconciliation. Missing closure
keeps concurrency held even when the outer monitor exited.

The pool namespace additionally masks its custody directory. Its environment
stamp is `tree-v1-held-pid1-explicit-gate-v1` (or
`iso-v1-held-pid1-explicit-gate-v1`), preserving the base
materialization rules while separating this administration from old cohorts.

The pool output includes shared accounting status and custody path separately
from the native review result. A model response can succeed while accounting
stays held. The held-PID1 environment must be cohorted separately from prior
`tree-v1`/`iso-v1` measurements. It does not establish study completion,
qualification, authenticated account joins or universal producer coverage.

This first integration does not enroll `supervise_sweep.py` probes or its
failed-row release/retry behavior, review-gate probes, the older advisory
executor, native preference/review-dissent, retrieval or artifact-rater. Those
callers must explicitly carry genuine assigned helper/root/retry custody and
their native authority. Do not use a new random assignment key to replay a lost
launch. A new explicitly assigned administration/attempt retains its own native
retry/qualification rules; the shared ledger does not choose them.

The installed public command requires the declared PyYAML 6 runtime dependency.
The source-native equivalent is `PYTHONPATH=src python3 -m caplab.advisory`.

`caplab advisory admission-describe` takes the same backend, declaration root,
output and configuration options as `admission-reconcile`. It exposes the
version-pinned native holder/launch-path mapping to the declared account and
catalog `quota_pool_ids`, profile/home, shared home and policy. Python callers
use `PoolAdmission.describe()`. Neither interface reserves or launches. This
configured/operator evidence can support finite declared-domain enrollment;
provider-authenticated physical identity is not a universal prerequisite.
Possibly aliased profiles may be conservatively joined by the owner's catalog
to shared pools, preserving the SDK's all-pool atomic enforcement. Do not change
account joins in the consumer or advertise local assertions as authentication.
Provider-window observations remain separate and apply only to their supported
accounts; an unknown applicability/value cannot be converted into launch capacity.

Enrolled `measure_case`/`pool-run` resumption now recovers an already assigned
arm/replicate. It validates the exact retained intent, completion and output
hashes and rebuilds the row without another child or shared charge. An assigned
outcome without complete output becomes an unusable attempt with
`recovery_basis=assigned-output-unavailable`; that is not proof of native closure
or a retry right. Completed captures use `recovery_basis=retained-completion`.
Direct `invoke` still refuses replay unless the caller explicitly selects
`recover_assigned=True`. An expired enrollment can recover existing assignments;
new assignments must meet the original deadline. Instrument source/run-spec
pins continue to reject changed administrations.

New completion records retain optional integer `elapsed_milliseconds`,
`timed_out` and `outputs_complete` fields. Historical v1 completions remain
readable without rewriting; absent historical elapsed duration projects as
null. Failure output is not promoted into a complete scored response. Cleanup
uncertainty is retained separately in `cleanup_errors`, while the original
exception reaches the caller with secondary failure notes.

Controlled startup refusal uses an owned process-group SIGKILL before monitor
reap, plus positively observed PID1 death when available. No-witness accounting
remains held. The pinned existing retrieval exec gate is mounted read-only at `/dev/caplab-launch-gate.py`
in the sandbox's existing private `/dev` mount
and invoked with the pinned system interpreter. Only after all readiness and
deadline checks does the supervisor send one release byte followed by the
original stdin payload. Arg-mode applications keep their original argv and
receive EOF after the gate byte. EOF before that byte exits the gate instead of
execing the native command, including after supervisor SIGTERM/SIGKILL. This
changes startup administration, not the native command/model/effort. Gate EOF
is not namespace closure evidence; missing completion/witness still holds.

Future enrollment receipts identify `pool-held-pid1-explicit-gate-v1`. Assigned
intent pins exact gate/interpreter bytes. Original `pool-held-pid1-v1` receipts
remain loadable with `recovery=True` for describe/reconciliation only; `run`
refuses those legacy administrations even when their expiry is still valid.
Opening the same custody under the new administration refuses receipt conflict.
Use a separately declared prospective administration, never delete or relabel
old custody. Existing completed-arm replay and source/run-spec pins remain.
This feature does not itself authorize an unenrolled benchmark or claim native
model qualification.

Startup refusal attempts bounded raw-stream capture after abort/reap without a
release byte. Preserved stderr/exit facts remain unscored incomplete output and
never establish namespace closure. Secondary errors annotate the primary one.
