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
apply_policy(measurement | null, policy, generated_at, supersedes) -> claim
read_history(binding_id, capability) -> claims and graph heads
export_claims(binding_id, capability) -> deterministic export artifact
```

The operator surface is:

```text
caplab qualification measure --input MEASUREMENT --ledger LEDGER
caplab qualification apply --measurement MEASUREMENT --policy POLICY \
  [--supersedes CLAIM_ID ...] --ledger LEDGER
caplab qualification history --binding BINDING_ID \
  --capability NAME --capability-version VERSION --ledger LEDGER
caplab qualification export --binding BINDING_ID \
  --capability NAME --capability-version VERSION --ledger LEDGER --output FILE

caplab revbench prepare --spec SPEC --output MANIFEST
caplab revbench run --manifest MANIFEST --reviews REVIEWS --output MEASUREMENT
```

`revbench run` is an offline derivation over captured native-harness reviews;
it performs no provider call. Harness execution remains an upstream evidence
capture effect and must be separately authorized.

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
`authorization_ref`. The ID is content-derived; case and input lists are sorted
registered references. `conditioned_on` uses a closed vocabulary that includes
`downstream_fate` and `model_judgment`. A decision over the declared source
population requires that list to be empty.

An evidence basis authorization reference resolves to
`caplab-evidence-basis-authorization/1`, which names the authority source,
capability/card, basis kind and role, evidence scope, valid interval, and
delegate or deterministic mechanism. It cannot broaden the separately declared
case-selection population.

`evidence` has one `bundle_ref` and a sorted `run_refs` list. `covariates` may
contain downstream fate and other observational metadata. Policy predicates
cannot address `covariates`. `provenance` has `caplab_version`,
`caplab_commit`, and sorted `source_refs`.

The exact subordinate shapes are:

```yaml
evidence: {bundle_ref, run_refs}
covariates:
  - {name, value, evidence_ref}
provenance: {caplab_version, caplab_commit, source_refs}
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
IDs, the complete capability including card reference, policy name/version,
and any permitted decision statuses. Its ID is content-derived from all other
fields. Claim issue resolves its authority source and refuses out-of-scope,
expired, not-yet-valid, or status-mismatched authorization.

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
validate the complete existing stream, append one newline-terminated record,
flush, and `fsync` before reporting success. An exact content replay is
idempotent; an existing ID with different bytes is a conflict. Readers perform
no repair.

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

`caplab-revbench-spec/1` has exact keys `schema_version`, `binding`,
`capability`, `protocol`, `corpus`, `case_selection_ref`,
`basis_authorization_refs`, `cases`, and `provenance`.
`basis_authorization_refs` has exact keys `truth`, `case_selection`, and
`metric_derivation`, each resolving to a scoped
`caplab-evidence-basis-authorization/1` record. Version 1 cases
are canonical JSON artifacts and have exact keys `case_id`, `control`,
`mutation`, `oracle`, and `defect_anchor`. The one initial mutation operator is
`replace-json-value/1`; it names a JSON Pointer and replacement value. The one
initial oracle is `json-integer-minimum/1`; it names the same pointer and an
inclusive integer minimum. Preparation requires a control integer at or above
the minimum and a replacement integer below it.

The control is known sound only for this declared invariant. Revbench v1 may
support the bounded distribution `json-integer-minimum/1`; it does not turn a
single passing predicate into a claim about general review correctness.

`caplab-revbench-manifest/1` has exact keys `schema_version`, `experiment_id`,
`family`, `family_version`, `binding`, `capability`, `protocol`, `corpus`,
`case_selection_ref`, `basis_authorization_refs`, `cases`, and `provenance`. It
pins each known control, mechanically transformed
mutant, independently recomputed oracle result, exact Binding, assignment
order, and expected JSON-Pointer defect anchor. Each arm stores canonical
artifact content and its SHA-256. Preparation fails unless the clean control
passes its oracle and the mutant fails exactly the planted invariant.

`caplab-revbench-reviews/1` has exact keys `schema_version`, `experiment_id`,
`observed_at`, and `attempts`. Each attempt has exact keys `case_id`, `arm`,
`binding_id`, `observed_binding`, `attempt_ref`, `attestation_ref`, `prompt_ref`,
`disposition`, `verdict`, `anchors`, and `output_ref`. `attempt_ref` identifies
the complete registered attempt envelope. `observed_binding` is a complete Binding derived
from the registered native-attempt attestation, not a caller label. Arms are
`control` and `mutant`; dispositions are `complete`, `subject-failure`, and
`infrastructure-failure`; verdicts are `clean`, `defect`, and `invalid`.
Anchors are sorted JSON Pointers. The output is an immutable evidence reference.

A captured review is usable only when its declared Binding matches the
manifest and its observed Binding recomputes to that exact ID. The scorer
resolves and verifies the native-attempt attestation, prompt, and output before
using the arm. Detection requires a conforming verdict and the exact defect anchor;
a generic refusal is not catch credit. Revbench reports catch rate,
false-alarm rate, discrimination, anchor-hit rate, and conformance separately.
There must be exactly one control and one mutant attempt per case. An invalid,
missing, or infrastructure-failed arm excludes its pair and remains visible in
sample flow; it cannot improve any score. Discrimination is
`(caught mutants - false-alarm controls) / usable pairs`, so its numerator may
be negative.

Legacy tuner summaries and fate-selected controls are not imported as
Measurements by default. They remain `legacy_nonqualifying` observations until
an authorized audit establishes independent truth, exact Binding, complete
provenance, and independent case-selection lineage for an individual run. A
fate-conditioned sample may at most support a claim whose distribution is
explicitly narrowed to that selected population; it cannot be generalized.
