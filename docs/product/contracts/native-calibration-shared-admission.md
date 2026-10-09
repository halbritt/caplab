# Native calibration shared admission v1

ADR0071 adds opt-in administration to preference and review-dissent native
Python/CLI runners. Native manifest authorization, expiry, source pins,
instruments, task-only containment, order, replacements, limits, observation
and model-identity rules still apply. Expired historical campaigns are not
resumed. New source needs a fresh compatible authorized manifest.

Create an owner-controlled campaign custody parent (mode 0700), then:

```sh
python -m caplab.runtime.native_admission domain --custody /absolute/campaign-custody
```

This creates native identity only. Prepare three
`caplab-shared-admission-enrollment/2` files using
[the enrollment contract](../../shared-admission.md), one for each `fable`,
`gpt` and `platform`. Every mapping selects the same SDK executable/source-tree,
home, policy and catalog release; account/profile selections may differ. Caller
is `caplab`; use the returned custody domain and exact raw file pins.
Subject `binding_id` is the native instrument's `tuple_id`, an assertion rather
than a newly qualified Binding. The platform entry declares its finite charged
domain without claiming a native model run. Subject model, native harness ID
and effort must match the selected enabled catalog tuple.

`credential_profile_sha256` hashes canonical UTF-8 JSON (sorted keys, compact
separators, no newline) with exactly these fields:

```json
{"schema_version":"caplab-native-declared-profile/1","profile_id":"EXACT_PROFILE","host":"EXACT_HOST","account_id":"EXACT_ACCOUNT","config_home":null,"native_config_home":"/absolute/native/config-home"}
```

Use the catalog's actual `config_home`, including null. `native_config_home`
records the existing native runner's host config path for Claude Code/Codex;
use null for `platform`. No credential bytes are read by the adapter. This is
an operator-declared finite domain, not physical provider authentication.
Conservative aggregation through catalog `quota_pool_ids` remains possible;
provider veto observations need actual account applicability. Policy's
canonical JSON identity and enrollment's raw file `policy_sha256` (hex without
`sha256:`) have different digest domains; do not confuse them.

The configuration contains exactly:

```json
{"schema_version":"caplab-native-shared-admission/1","family":"preference","manifest_sha256":"EXACT_MANIFEST_DIGEST","subjects":[{"subject_id":"fable","native_config_home":"/absolute/claude/config","enrollment_path":"/absolute/fable.json","enrollment_sha256":"RAW_FILE_SHA256_HEX"},{"subject_id":"gpt","native_config_home":"/absolute/codex/config","enrollment_path":"/absolute/gpt.json","enrollment_sha256":"RAW_FILE_SHA256_HEX"},{"subject_id":"platform","native_config_home":null,"enrollment_path":"/absolute/platform.json","enrollment_sha256":"RAW_FILE_SHA256_HEX"}]}
```

Use `review-dissent` for that family. All three mappings are required.

```sh
python -m caplab.preference.native_live --manifest /absolute/manifest.json \
  --instrument /absolute/native-instrument.json --source-root /absolute/source-checkout \
  --shared-admission /absolute/enrollment.json admission-describe
python -m caplab.preference.native_live --manifest /absolute/manifest.json \
  --instrument /absolute/native-instrument.json --source-root /absolute/source-checkout \
  --shared-admission /absolute/enrollment.json run --slot-index 0 --attempt-kind primary
python -m caplab.preference.native_live --manifest /absolute/manifest.json \
  --instrument /absolute/native-instrument.json --source-root /absolute/source-checkout \
  --shared-admission /absolute/enrollment.json admission-reconcile
```

The review runner uses `caplab.review_dissent.native_live` with the same global
options. Installed modules use `--source-root` to resolve source assets: the
declared source must also byte-match the loaded runner/runtime. Describe
retains native enrollment metadata but reserves/launches nothing. Reconcile
validates retained custody before SDK effects; it never reserves, prepares or
launches. These two commands can load expired manifests for housekeeping;
execution still refuses expiry.

Python callers pass `shared_admission=configuration_path` to
`execute_native_trial` or `execute_native_review_trial`. Standalone preflight
uses `load_native_admission(path, manifest, family=...)`, passing the controller
to `preflight_native_runtime(..., shared_admission=controller)`.
All five preflights (two version, platform version, two auth checks) participate,
followed by one separately governed trial. Per-trial preflights have distinct
primary/replacement keys. Repeating standalone preflight reads retained
observations, rather than making a new freshness probe. Native auth checks keep
their campaign meaning; they are not a universal account-authentication gate.

Each helper/trial owns an immutable assignment under campaign
`shared-launches/assignments`. Quartermaster owns all numeric accounting.
Native evidence pins loaded adapter/custody/containment sources and the startup
gate/interpreter. A fresh permit precedes possible creation. Actual same-boot
UTC/monotonic brackets and held PID1 observation precede release. An isolated
Python startup gate consumes one explicit release byte, then execs the original
command with EOF stdin. Supervisor EOF cannot release the application. This
is a stage of the same outer launch, not a provider proxy or another harness.

Positive Popen return counts once, including later exec failure. Constructor
exceptions are unresolved. Authentic completion wholly before Popen can close
an unused right. Real namespace-init death and native completion are needed
for settlement; missing clocks/witnesses/completion stays held. Outer exit or
expiry alone is not a tree oracle. Application timeout includes admission;
output retains the native captured-byte contract. SDK errors propagate rather
than becoming fabricated measurements. Cleanup failures annotate the primary
error. A valid native outcome may coexist with an unresolved SDK hold.

Restart validates launch, shared completion and raw output preimages, then can
finish interrupted native publication without another helper, child or charge.
A prepared attempt without shared custody refuses with
`native_prepared_attempt_unresolved_no_retry`; an incomplete outcome refuses
with `native_outcome_unresolved_no_retry`. Deleting assignments or resetting
keys to evade these states is not recovery. Existing unenrolled behavior remains.

This slice does not enroll artifact-raters, retrieval Cairn/database/git/search
helpers, other advisory/sweep paths, historical campaigns or uninstrumented
clients. Private local-process controls establish adapter mechanics, not native
model qualification, scientific acceptance or universal producer coverage.
