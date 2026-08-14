# CAPLAB qualification contract v1

This contract pins the shared boundary for `caplab.qualification`,
`caplab.revbench`, and future artifact consumers. Implementations reject
unknown fields and unsupported normative schema versions. JSON bytes use
CAPLAB canonical JSON: UTF-8, NFC strings, lexically sorted object keys, no
insignificant whitespace, and no binary floating-point values.

The network-independent
[`qualification-schema-catalog-v1.json`](qualification-schema-catalog-v1.json)
pins each public schema ID to a sibling file and SHA-256. Validators load that
catalog and register local bytes by schema ID; they never fetch
`https://caplab.local/`.

## Public operations

The generic module exposes these operations through Python and the batch CLI:

```text
record_measurement(measurement) -> immutable measurement
apply_policy(measurement | null, policy, binding | null, generated_at,
             supersedes) -> claim
read_history(binding_id, capability) -> claims and graph heads
export_claims(binding_id, capability) -> deterministic export artifact
```

The operator surface is:

```text
caplab qualification measure --input MEASUREMENT --ledger LEDGER
caplab qualification register --input OBJECT --kind KIND --schema SCHEMA \
  [--media-type MEDIA_TYPE] --ledger LEDGER
caplab qualification apply (--measurement MEASUREMENT | --binding BINDING) \
  --policy POLICY [--supersedes CLAIM_ID ...] --ledger LEDGER
caplab qualification history --binding BINDING_ID \
  --capability NAME --capability-version VERSION --ledger LEDGER
caplab qualification export --binding BINDING_ID \
  --capability NAME --capability-version VERSION --ledger LEDGER --output FILE

caplab revbench prepare --spec SPEC --ledger LEDGER --output MANIFEST \
  [--reference-output MANIFEST_REF]
caplab revbench execute --manifest MANIFEST \
  --execution-authorization-ref AUTHORIZATION_REF --ledger LEDGER \
  --output REVIEWS
caplab revbench score --manifest MANIFEST --reviews REVIEWS --ledger LEDGER \
  --output MEASUREMENT
```

`revbench execute` is the authorization-gated CAPLAB benchmark-execution
boundary. Version 1 prepares blinded inputs and invokes only a registered
static local fixture under sealed limits and containment. It refuses live
native-provider authority because the native launcher bundle and durable
streaming-custody seam are not implemented. `revbench score` is the separate
offline derivation; it performs no provider call. All three revbench commands
use the qualification ledger as their registration-aware resolver. Object
bytes without a matching retained registration record are refused.

`qualification register` preserves arbitrary bytes without JSON re-encoding
when `--media-type` is not `application/json`. Historical custody registration
is disabled until a typed admission-authorization path exists; supplying
`--custody` fails closed rather than creating an ungrounded provenance claim.

Stdout and durable documents are canonical JSON. Expected contract failures
return 2. A valid negative or insufficient qualification is successful and
returns 0. Read-only integrity reports may return 3 when their document has
`ok: false`.

## Binding: `caplab-binding/1`

The exact keys are:

```text
schema_version, binding_id, model, provider_or_path, harness,
reasoning_effort, configuration
```

The sections are:

```yaml
model: {model_id, revision, weights_ref, weights_unavailable_reason}
provider_or_path: {kind, identifier, revision, resolution, observed_at,
                   route_ref}
harness: {harness_id, harness_version, executable_ref,
          executable_unavailable_reason, command_ref, version_probe_ref}
configuration: {inference_ref, instructions_ref, knowledge_ref, tools_ref,
                permissions_ref, sandbox_ref, runtime_ref}
```

`weights_ref` and `executable_ref` may be null only when the named provider or
harness does not expose those bytes, in which case the matching unavailable
reason is mandatory. Every nonnull reference follows the registered
evidence-reference contract. The observed route and contract reference remains
mandatory. `resolution` is `immutable` or
`observed-route`; policy may reject the latter. `observed_at` is null for an
immutable route and a UTC timestamp for an observed route. `route_ref`
identifies the resolved route contract, not the nominal alias.

`version_probe_ref` resolves to canonical
`{command_ref, exit_code, stdout_ref, stderr_ref}` captured before the attempt.
Each configuration reference identifies the complete canonical configuration
document for that surface. `binding_id` is `bnd-` plus the
SHA-256 of the complete canonical document with only `binding_id` removed.

Any change to model revision or weights, provider or proxy path, native harness
or wrapper, effort, inference configuration, instructions, knowledge, tools,
permissions, sandbox, or relevant runtime creates a different Binding.
Protocol and corpus are measurement identities. Exact rendered administration
that can change behavior is represented by the Binding's instruction and
configuration hashes as well as by its governing protocol.

## Evidence reference

Every evidence pointer has exact keys:

```text
kind, schema, media_type, sha256, byte_count, locator, registration_ref,
custody
```

`locator` is the canonical CAPLAB object key derived from `sha256`.
`registration_ref` identifies the CAPLAB admission or registration record that
verified the bytes. `custody` is null for CAPLAB-native material or has exact
keys `repository`, `commit`, `path`, and `source_sha256`; its path is a
normalized repository-relative path with no `.` or `..` segment. A bare
mutable path, host path, or URL is not an immutable reference. A syntactically
valid reference is not proof of registration: claim issue resolves each
registration reference and verifies the recorded digest and byte count.

## Measurement: `caplab-measurement/1`

The exact keys are:

```text
schema_version, measurement_id, observed_at, binding, capability,
experiment, protocol, corpus, evidence_basis, disposition, sample_flow,
metrics, evidence, covariates, provenance
```

`capability` has `name`, `version`, `role`, `domain`, `distribution`, and
`card_ref`. Claims never extrapolate beyond this identity. `experiment` has
`family` and `version`. Protocol and corpus are evidence references.

Each evidence basis has exact keys `basis_id`, `kind`, `role`, `evidence_ref`,
and `authorization_ref`. Roles are `truth`, `case-selection`, and
`metric-derivation`. Version 1 kinds are `mechanical-oracle`,
`human-authorized`, and `model-judgment`. The first two may qualify when the
policy permits them. `model-judgment` remains distinguishable and cannot issue
a version 1 qualified or unqualified decision.

`basis_id` is `basis-` plus the canonical SHA-256 of the other four fields.
Both reference fields use the evidence-reference contract; the authorization
reference names the decision or delegated mechanism that permits this basis to
support the stated capability and distribution.

`disposition` is `complete`, `incomplete`, `invalid`, or
`infrastructure-failure`. `sample_flow` contains `planned`, `attempted`,
`usable`, `excluded`, `missing`, `subject_failures`, and
`infrastructure_failures`. The counts form a partition:
`attempted + missing == planned` and
`usable + excluded + subject_failures + infrastructure_failures == attempted`.
Every metric has exact keys `value`, `basis_ids`, and `case_selection_ref`.
`value` is a rational `{numerator, denominator}` with a positive denominator;
`basis_ids` names all truth and derivation bases that contributed to it; and
`case_selection_ref` resolves to a `caplab-case-selection-manifest/1` document
that declares every selection and exclusion input. A decision metric must have
complete lineage through permitted independent bases. A selection manifest
conditioned on downstream fate or model judgment is advisory-only unless the
capability distribution explicitly names that selected population.

`caplab-case-selection-manifest/1` has exact keys `schema_version`,
`selection_id`, `population_ref`, `included_case_refs`, `excluded_case_refs`,
`selection_inputs`, `exclusion_inputs`, `conditioned_on`, and
`authorization_ref`. The ID is `selection-` plus the canonical SHA-256 of all
other fields; case and input lists are sorted
registered references. `conditioned_on` uses the closed vocabulary
`downstream_fate`, `model_judgment`, `human_judgment`, `provider_verdict`,
`scheduler_choice`, `admission`, `backend_rank`, `task_difficulty`, and
`attempt_outcome`. A decision over the declared source population requires that
list to be empty.

An evidence basis authorization reference resolves to
`caplab-evidence-basis-authorization/1`. Its exact keys are `schema_version`,
`authorization_id`, `authority_source_ref`, `authorized_by`,
`delegate_or_mechanism`, `binding_ids`, `capability`, `experiment`,
`protocol_ref`, `corpus_ref`, `case_selection_ref`, `method_ref`, `basis_kind`,
`basis_role`, `valid_from`, and `valid_until`. The ID is content-derived from
all other fields as `basis-auth-` plus its canonical SHA-256. Binding IDs are
sorted and nonempty; capability includes its
card; and every reference is registered. Together the Binding, capability,
experiment, protocol, corpus, case selection, and method form the exact
evidence scope. The authorization must match the enclosing evidence basis kind
and role, the Measurement, and its observation time. It cannot broaden the
separately declared case-selection population or authorize a qualification
status.

`evidence` has one `bundle_ref` and a sorted `run_refs` list. `covariates` may
contain downstream fate and other observational metadata. Policy predicates
cannot address `covariates`. `provenance` has `caplab_version`,
`caplab_commit`, optional `caplab_package_sha256`, and sorted `source_refs`.
Newly produced Measurements and Claims include the package digest as a
separate field; it never substitutes for the source commit.

The exact subordinate shapes are:

```yaml
evidence: {bundle_ref, run_refs}
covariates:
  - {name, value, evidence_ref}
provenance: {caplab_version, caplab_commit, caplab_package_sha256, source_refs}
```

The reserved covariate name for migrated tuner outcomes is
`downstream_fate`. Its value is observational text; neither its name nor value
is present in the policy document supplied to the evaluator.

`measurement_id` is `meas-` plus the SHA-256 of the canonical document without
`measurement_id`. A measurement is an observation and contains no policy,
threshold, or qualification status.

## Policy: `caplab-qualification-policy/1`

The exact keys are:

```text
schema_version, policy_id, name, version, capability, applies_to,
requirements, criteria, outcomes, authority, provenance
```

`applies_to` pins experiment family/version, protocol SHA-256, corpus SHA-256,
and permitted Binding resolutions. `requirements` pins minimum usable samples,
maximum missing and infrastructure-failure ratios, and permitted evidence-basis
kinds. Policy validation refuses `model-judgment`, downstream fate, admission,
scheduler choice, provider verdict, or any covariate as a decision-authorizing
basis.

The exact subordinate shapes are:

```yaml
capability: {name, version, role, domain, distribution, card_ref}
applies_to:
  experiment: {family, version}
  protocol_sha256: ...
  corpus_sha256: ...
  binding_resolutions: [immutable | observed-route, ...]
requirements:
  minimum_usable: ...
  maximum_missing_rate: {numerator, denominator}
  maximum_infrastructure_failure_rate: {numerator, denominator}
  basis_kinds: [mechanical-oracle | human-authorized, ...]
criteria:
  - {metric, operator, threshold: {numerator, denominator}}
outcomes:
  met: qualified
  not_met: unqualified
  insufficient: advisory
  no_measurement: unmeasured
authority: null | caplab-qualification-authorization/1
provenance: {caplab_version, caplab_commit, source_refs}
```

All lists with set semantics are sorted and duplicate-free. Each source
reference uses the evidence-reference contract.

`caplab-qualification-authorization/1` has exact keys `schema_version`,
`authorization_id`, `authority_source_ref`, `authorized_by`,
`delegate_or_mechanism`, `binding_ids`, `capability`, `policy`,
`permitted_statuses`, `valid_from`, and `valid_until`. It names exact Binding
IDs, the complete capability including card reference, the policy name,
version, and authority-free semantic SHA-256, and any permitted decision
statuses. The semantic digest prevents two different policy bodies from
sharing one name/version authorization. Its ID is content-derived from all
other fields. Claim issue resolves its authority source and refuses
out-of-scope, expired, not-yet-valid, status-mismatched, or policy-body-
mismatched authorization.

The evaluator receives a projection containing only Binding, capability,
experiment, protocol/corpus identities, disposition, sample flow, metrics, and
evidence-basis kinds. Covariates and raw metadata are not present in that
projection. It recomputes every rational comparison with exact integer
arithmetic; a producer-supplied criterion result is never trusted.

Criteria use only `metric_at_least` and `metric_at_most`, each with an exact
rational threshold. All criteria form a conjunction. New predicate semantics
require a new policy schema version.

`outcomes` is fixed to `qualified`, `unqualified`, `advisory`, and
`unmeasured`. Without an exact valid authorization for the resulting status, a
policy can emit only `advisory` or `unmeasured`. Version 1 decision claims also
require an `immutable` Binding with nonnull model-weights and harness-executable
references; an `observed-route` or unknown-byte Binding is advisory-only.
`policy_id` is `pol-` plus the SHA-256 of the canonical document without
`policy_id`.

Status semantics are:

- `unmeasured`: no eligible complete measurement;
- `advisory`: observations exist but identity, basis, coverage, or authority is
  insufficient;
- `unqualified`: authorized eligible evidence is sufficient and any criterion
  fails;
- `qualified`: authorized eligible evidence is sufficient and every criterion
  passes.

## Claim and history

The public claim schema is
[`qualification-claim-v1.schema.json`](qualification-claim-v1.schema.json).
Its exact top-level keys are:

```text
schema_version, claim_id, generated_at, assertion_type, binding,
capability, qualification, measurement, evidence, provenance, supersedes
```

The claim embeds the complete public Binding so a consumer does not join
against CAPLAB storage. It carries inspection metrics and evidence references,
not raw private evidence. Its Measurement summary includes the immutable
Measurement, protocol, corpus, policy, capability-card, evidence-basis, and
case-selection references. `claim_id` is `claim-` plus the SHA-256 of the
canonical claim basis excluding `claim_id` and `generated_at`; idempotent issue
keeps the first ledger-recorded `generated_at`. The CLI does not accept a
caller-selected issuance time. A test clock is injectable only through the
in-process composition root.

Claim construction accepts either a Measurement or an explicit full Binding.
The Binding argument is required when the Measurement is null, which is the
only path that can issue `unmeasured`. When a Measurement is supplied, its
embedded Binding is authoritative; an optional separately supplied Binding
must match it exactly. The CLI exposes this as a mutually exclusive
`--measurement` or `--binding` input.

`qualified` and `unqualified` use assertion type `decision`; `advisory` and
`unmeasured` use `recommendation`. Superseded claims remain byte-for-byte
present. `supersedes` may name only existing claims with the same Binding and
capability identity, and the graph must remain acyclic. History reports every
head and whether the series is ambiguous; it does not choose a current claim.

A decision claim additionally requires a complete Measurement, at least one
`mechanical-oracle` or `human-authorized` truth, case-selection, and
metric-derivation bases permitted by the Policy,
nonempty registered bundle and run evidence, a nonnull matching measurement
digest, a resolvable decision reference, sufficient sample flow, and a
criterion list recomputed from the exact Measurement. `model-judgment` cannot
appear among a decision claim's basis kinds. A claim cannot supersede itself.

The local reference implementation receives a ledger directory, not a database
connection. It contains canonical `measurements.jsonl`, `policies.jsonl`, and
`claims.jsonl`.
Append operations refuse symlinks, take one directory-scoped exclusive lock,
and validate the complete existing stream. An append constructs the complete
next stream image in an exclusive, no-follow temporary file in the ledger
directory, flushes and `fsync`s that file, atomically replaces the stream, and
then `fsync`s the directory before reporting success. A reader therefore sees
either the prior complete image or the next complete image, never a partial
record. A failure before replacement leaves the prior image unchanged. A
directory-`fsync` failure after replacement reports failure even though the
complete next image is visible; an exact retry re-`fsync`s the ledger directory
before it reports idempotent success. Object and namespace-directory replays
likewise re-`fsync` their owning directories before the corresponding
registration can succeed. Filesystem errors are returned as
qualification-ledger errors. An existing ID with different bytes is a
conflict. Readers perform no repair.

## Quartermaster-facing export

The public export schema is
[`qualification-export-v1.schema.json`](qualification-export-v1.schema.json).
An export contains one explicitly selected Binding/capability series, every
claim in that series, the public schema hashes, and producer provenance. Claims
are sorted by claim ID; their own `supersedes` fields are the only graph-edge
source. `export_id` is `export-` plus the SHA-256 of the complete canonical
document with only `export_id` removed.

Exports never contain a mutable `current` flag, raw evidence bytes, host paths,
credentials, runtime inventory, enabled state, reachability, provider health,
quota, price, preference, placement, or Dispatch policy. A consumer may verify
and preserve claims; it must make its own active-claim and runtime decisions.

JSON Schema validation establishes shape, not truth. CAPLAB and conforming
consumers also recompute every Binding, Measurement, Policy, Claim, and Export
ID; require canonical ordering; match every content locator to its digest;
verify schema digests against the supplied schema bytes; enforce sample-flow
equations and valid rate bounds; recompute each policy criterion; require every
claim to match the selected Binding and capability; reject duplicate claim
IDs, dangling/cross-scope/self supersession and cycles; and resolve qualifying
evidence and authority references. Failure of any semantic check rejects the
artifact.

## Revbench v1

Revbench is CAPLAB's first mechanically authorized experiment family. It has
three separate effects: deterministic preparation, authorization-gated native
execution, and offline scoring. A green execution or score is verification,
not qualification or acceptance; applying a separate policy is still
required to create a Claim.

### Preparation

`caplab-revbench-spec/1` has exact keys `schema_version`, `binding`,
`capability`, `protocol`, `corpus`, `native_system_contract_ref`,
`case_selection_ref`, `basis_authorization_refs`, `cases`, and `provenance`.
Each basis authorization is independently delegated for its exact Binding,
capability, experiment, protocol, corpus, selection, method, kind, role, and
time interval.

Version 1 cases have exact keys `case_id`, `control`, `mutation`, `oracle`, and
`defect_anchor`. The only initial mutation is `replace-json-value/1`; it names
a JSON Pointer and replacement integer. The only initial oracle is
`json-integer-minimum/1`; it names the same pointer and an inclusive minimum.
Preparation independently proves that the control satisfies the invariant and
the mutant violates it.

`caplab-revbench-manifest/1` adds `experiment_id`, `family`, and
`family_version`, replaces each source case with the exact control and mutant
content, hashes both arms, and records a sealed `assignment_order`. The
manifest embeds the complete Binding and the registered native-agent-systems
contract. Preparation rejects hidden selection or exclusion inputs; version 1
therefore cannot conceal downstream-fate selection behind an empty
`conditioned_on` declaration.

Preparation accepts only the repository-owned synthetic fixture namespace in
version 1. Its Binding is exactly:

```text
provider identifier: caplab-local-fixture
provider/model revision: revbench-static-fixture-v1
model: caplab/revbench-static-fixture
harness: caplab-revbench-static-fixture
harness version: fake-native 1
effort: fixed
```

Its native-system document has exact top-level keys `schema`, `policy`,
`decision_authority`, `source_observation`, `systems`,
`forbidden_proxy_markers`, and `exceptions`. `policy` is
`caplab-revbench-local-fixture-v1`, `decision_authority` is `adr-0062`, and
`source_observation` is exactly
`{"contract":"caplab-revbench-local-fixture/1"}`. The one system entry pins
the absolute executable path, required command prefix, exact version command,
harness version, version exit code, and SHA-256 digests of version stdout and
stderr. The executable must be a real, executable, nonsymlink file whose bytes
equal its registered `executable_ref`. The complete mandatory proxy-marker set
is `openrouter`, `harbor`, and `terminus`; a caller cannot weaken it.

A non-local Binding must reference canonical bytes equal to
[`native-agent-systems.json`](native-agent-systems.json), and preparation then
fails closed because live native-provider preparation is not implemented in
version 1. Thus neither a caller-authored provider policy nor a local fixture
can label synthetic bytes as Codex, Claude Code, or another live subject. A
future provider implementation must add sealed launcher dependencies and
version evidence before this preparation refusal can be removed.

The control is known sound only for the declared integer-minimum invariant.
The bounded distribution is `json-integer-minimum/1`; it does not imply
general review correctness, security review, architecture judgment, or any
other distribution.

### Execution authorization and exact runtime

`caplab-revbench-execution-authorization/1` has exact keys
`schema_version`, `authorization_id`, `authority_source_ref`, `authorized_by`,
`delegate_or_mechanism`, `experiment_id`, `manifest_ref`, `binding_id`,
`native_system_contract_ref`, `command_ref`, `version_probe_ref`,
`effect_class`, `limits`, `valid_from`, and `valid_until`. Its ID is
`revbench-execution-auth-` plus the canonical SHA-256 of every other field.
The authority source is a registered `caplab-authorization-delegation/1` for
the `revbench-execution` effect and the same complete scope and interval.

`effect_class` is `local-fixture` or `live-native-provider`. The latter is
reserved and rejected by v1 preparation and execution. A future live run would
require both an implemented sealed provider adapter and its own registered
`live-native-provider` authorization.

`limits` has exact keys `max_version_probe_processes`,
`max_native_review_processes`, `timeout_seconds_per_process`,
`total_wall_seconds`, `max_stdout_bytes_per_process`, and
`max_stderr_bytes_per_process`. The two process counts equal twice the sealed
case count in the zero-retry v1 protocol. Time and stream limits are bounded by
the public schema and are enforced by the runner.

CAPLAB execution supports one fail-closed configuration profile:

- `runtime_ref` resolves to `caplab-revbench-execution-runtime/1` and pins the
  absolute executable path, `static-elf` format, empty environment-key list,
  temporary empty working directory, `not-required` network mode,
  canonical-JSON stdin, and single-JSON stdout;
- `inference_ref` binds the exact native command;
- `instructions_ref` binds the fixed blinded-review instruction;
- `knowledge_ref` and `tools_ref` must explicitly disable those surfaces;
- `permissions_ref` pins the environment allowlist, read-only root/private
  working-directory mode, and network mode; and
- `sandbox_ref` pins the absolute Bubblewrap adapter and its registered bytes,
  a read-only root, private writable working directory, and the same network
  mode.

The v1 executor accepts only `local-fixture` authority. It refuses
`live-native-provider` authority until CAPLAB has a separately pinned native
harness bundle, provider-specific tool-disable contract, and durable streaming
custody adapter. The authorization schema reserves that effect class without
claiming an implementation.

CAPLAB resolves and compares both executable and sandbox-adapter bytes before
execution. `executable_ref` cannot be null on this path, and the executable
must be a self-contained static ELF file. For every process CAPLAB writes a
private snapshot of the already verified executable and rechecks the sealed
Bubblewrap adapter bytes immediately before launch. It then runs the exact
command under `shell=False` in a new process group and Bubblewrap namespace.
The namespace has an empty root, no host filesystem mounts, no
network, no environment values, a private working directory, and only the
sealed executable plus minimal virtual `/proc` and `/dev` trees. The
`knowledge_ref` and `tools_ref` records describe absent subject integrations;
they do not rename ordinary runtime syscalls as agent tools. Stdin is written
non-blockingly so a child that does not read cannot escape the process
deadline. A timeout or byte limit terminates the process group and retains the
captured prefix.

### Blinding and attempt records

The subject-visible `caplab-revbench-native-input/1` contains only
`schema_version`, the fixed instruction, the declared oracle requirement, the
artifact, and `response_schema_version`. It omits case ID, arm, assignment
index, mutation, oracle outcome, and defect anchor. Its canonical bytes are
the exact process stdin.

`caplab-revbench-prompt/1` is the internal assignment envelope. It contains
the experiment, case, arm, assignment index, Binding ID, protocol reference,
and registered blinded-input reference. The subject returns one
`caplab-revbench-native-response/1` object with `verdict` and sorted `anchors`.
A clean response has no anchors; a defect response has at least one. Invalid
bytes become a derived `invalid` output and never a subject-supplied valid
verdict.

A fresh version probe runs before every assigned attempt. Its registered
`caplab-native-version-observation/1` records the authorization, Binding,
expected probe, command, interval, complete or truncated raw streams, exit,
termination, and mechanically recomputed match result.

A successfully returned local-fixture execution registers, for every
assignment:

- exact stdin, stdout, and stderr bytes;
- `caplab-native-output/1`, which projects only the parsed raw stdout;
- `caplab-native-attempt-capture/1`, which records authorization, full Binding,
  command, version observation, streams, completeness, exit, invocation state,
  and termination;
- `caplab-native-attempt-attestation/1`, which binds the capture to the native
  system contract, execution authority, version observation, prompt, output,
  assignment, and full observed Binding; and
- `caplab-native-review-attempt/1`, the content-identified envelope whose
  projection is repeated in the execution record.

All record IDs are their named prefix plus the canonical SHA-256 after removing
only that ID field. Scoring resolves every reference and recomputes the IDs,
full Binding, blinded input, raw-output projection, assignment, intervals,
authority, version match, capture disposition, and envelope projection. A
caller cannot substitute a control prompt/output for a mutant attempt through
the supported API and receive catch credit.

`caplab-revbench-reviews/1` has exact keys `schema_version`, `execution_id`,
`experiment_id`, `execution_authorization_ref`, `started_at`, `observed_at`,
`status`, `stop_reason`, and `attempts`. Complete executions contain every
sealed assignment and have a null stop reason. Stopped executions retain every
completed attempt and may contain none when authority or total time expires
before the first process. Subject response failures are sealed and execution
continues. Version drift, process spawn/nonzero/timeout/stream-limit failures,
or authorization expiry are infrastructure failures and stop execution without
retry.

### Offline scoring and trust ceiling

`revbench score` accepts only a reconstructed execution record. A usable pair
has one conforming control and mutant attempt for the same case. Catch credit
requires a defect verdict with exactly the planted JSON-Pointer anchor. A
generic refusal, invalid response, or wrong anchor earns no catch credit.
Revbench reports reduced-rational catch rate, false-alarm rate,
discrimination, anchor-hit rate when at least one mutant defect call exists,
and conformance rate. Missing, invalid, subject-failed, and infrastructure-
failed arms remain visible in sample flow and cannot improve a metric.
Discrimination is `(caught mutants - false-alarm controls) / usable pairs`, so
its numerator may be negative.

The local append-only ledger is a registration-aware integrity and custody
boundary, not a cryptographic signer or protection against a malicious writer
with the same filesystem authority. A registration failure raises and cannot
produce a Measurement, but the local-fixture executor does not have a durable
preopened stream sink that can recover bytes after a process completes. That
missing seam is one reason live execution remains refused. The executor does
not claim hardware attestation, secret-value identity, or independent
acceptance. Descriptor-relative stream publication refuses a symlink at the
ledger root or stream entry, but still trusts the ledger path's ancestor
directories; an actor able to replace those ancestors or write the ledger
outside its lock remains outside this boundary.

Legacy tuner summaries and fate-selected controls are not imported as
Measurements by default. They remain `legacy_nonqualifying` observations until
an authorized audit establishes independent truth, exact Binding, complete
provenance, and independent case-selection lineage for an individual run.
