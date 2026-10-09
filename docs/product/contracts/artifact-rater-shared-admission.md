# Artifact-rater shared admission

The installed `caplab-artifact-rater` command and
`python -m caplab.artifact_rater_cli` expose the original select, select-all, run
and evaluate operations. The checkout script remains an entry point. Only `run`
with `--shared-admission CONFIG` enrolls native launches. Select/evaluate do not
launch or enroll anything. Native launch control is Caplab-owned under
[ADR0073](../../decisions/adr-0073-artifact-rater-shared-admission.md).

## Enrollment

Create a new owner-controlled output directory, then use
`python -m caplab.runtime.native_admission domain --custody OUTPUT` to obtain its
real custody-domain ID. Prepare one
[shared SDK enrollment/2](native-calibration-shared-admission.md) with that domain,
`caller_id: caplab`, an explicit native administration binding ID, one designated
home, SDK source pin and catalog release/overlay/policy pins. Choose an enabled
catalog entry with the exact Codex model/effort and a tuple admitted by Caplab's
closed native-agent-systems policy. No account ID, release or numeric limit is
automatically invented. The binding ID labels this administration; it does not
create a qualified `bnd-` Binding.

Its `credential_profile_sha256` hashes canonical JSON (Caplab's
`canonical_json`) of the following complete operator declaration:

```json
{"schema_version":"caplab-artifact-rater-declared-profile/1","profile_id":"SELECTED_PROFILE","host":"SELECTED_HOST","account_id":"SELECTED_ACCOUNT","config_home":null,"native_home":"/ABSOLUTE/NATIVE_HOME"}
```

Replace placeholders with the actual selection. Preserve its exact config_home
value; when non-null it must equal NATIVE_HOME/.codex. The home must already have
an existing `.codex` directory. Do not create or print credentials. This is a
pinned local/operator account-domain assertion, not provider authentication.
Conservative shared aggregation is valid. Quota observations still need actual
account applicability and remain independent veto evidence.

CONFIG is a closed object with these fields; SHA256 values are bare hex:

| Key | Meaning |
| --- | --- |
| schema_version | `caplab-artifact-rater-shared-admission/1` |
| manifest_sha256 | SHA256 of the exact rater manifest file bytes |
| output_root | Absolute new custody output root |
| model, effort | Exact native tuple and CLI run arguments |
| expires_at | Aware ISO8601 execution expiry; original authority must select it |
| native_home | Absolute actual HOME; CODEX_HOME is HOME/.codex |
| codex_executable, codex_sha256 | Absolute actual native executable and byte pin |
| native_policy_path, native_policy_sha256 | Absolute closed Caplab policy and raw file pin |
| enrollment_path, enrollment_sha256 | Absolute SDK enrollment and raw file pin |

The existing policy is canonically pinned, even if raw formatting differs.
Artifact command validation names its precise native long-option argv variant;
it does not loosen Revbench/catalog general command equality. Existing disabled
entries or absent closed-policy tuples cannot launch. Future compatible native
selection/authorization is Caplab work, not a Quartermaster approval gate.
The adapter forwards the original prompt bytes after its one-byte gate and
records their hash. It shares the host network and retains native filesystem
reads. Output and the declared Codex home are writable; shared-launch custody is
read-only inside the namespace. The outer environment is PATH/LANG only; HOME,
CODEX_HOME and native executable PATH are explicitly assigned inside. Other
inherited environment settings are excluded. This administration must be named
in any future Binding/qualification.

## Use and recovery

```sh
caplab-artifact-rater admission-describe --manifest MANIFEST --output-root OUTPUT --model MODEL --effort EFFORT --shared-admission CONFIG
caplab-artifact-rater run --manifest MANIFEST --output-root OUTPUT --model MODEL --effort EFFORT --shared-admission CONFIG --workers 4 --timeout 900
caplab-artifact-rater admission-reconcile --manifest MANIFEST --output-root OUTPUT --model MODEL --effort EFFORT --shared-admission CONFIG
```

Describe retains enrollment evidence but does not reserve resources or launch.
Reconcile may append authentic SDK reconciliation proposals; it does not launch.
Run assigns `helper:codex-version` once, then `trial:SLOT:attempt-NNN` per original
attempt. SDK concurrency and launch resources are reserved together before
possible creation. The earlier of execution expiry and the original attempt
wall timeout governs; it must fit fixed windows without extending authority.
Positive creation counts one outer, including later exec failure. Positive
noncreation returns the unused closed right. Uncertain creation or closure stays
held. Neither an error nor a consumed permit is proof of zero launches.

Restart with the exact original release, configuration and manifest. Native
intent/completion/outputs, including prompt identity, are immutable. Missing
publication projects retained output into the same attempt. Changed bytes refuse;
missing or uncertain native outcome refuses replay. An already recorded failed
attempt follows existing rater retry numbering; each new attempt needs admission.
Published judgments continue to require genuine event/message/rollout derivation;
this adapter creates none of those observations. For a cleanup or SDK error,
retain its original exception and sidecars, run reconciliation with the original
pinned release, and resolve the actual missing evidence. Deleting custody, using
another output root to replay an old assignment, or inventing a death receipt
is not recovery. Active predecessors keep their original release/runtime pins.

The core supervision and post-monitor pidfd observation are reused from native
calibration. The public constructor requires a source-pinned SDK with interval,
reconcile and bounded-busy support. No additional SDK capability was needed for
this slice. Unenrolled runs retain the original subprocess behavior. Other helper,
advisory/sweep/review-gate and Revbench paths remain separately enrolled or
residual; this contract makes no universal producer or scientific-success claim.
