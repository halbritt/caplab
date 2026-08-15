# Binding qualification

CAPLAB is the authority for capability evidence, Measurements, qualification
policies, and qualification Claims. It answers a deliberately slow question:

> What has this exact agent-system Binding been measured to do, under which
> protocol and population, and what registered evidence supports the Claim?

The design absorbs the useful measurement lesson from `striatum-tuner` without
adopting its downstream-fate labels as truth. A later implementation outcome is
affected by the task, selection, retries, implementers, reviewers, and the
review itself. It can be retained as an observational covariate, but it cannot
authorize a capability decision.

## Authoritative path

```text
exact native Binding
        |
        v
CAPLAB experiment + protocol + corpus
        |
        v
independently authorized Measurement
        |
        v
versioned qualification policy
        |
        v
append-only Claim + evidence references
        |
        v
deterministic Quartermaster export
```

A **Binding** identifies the complete behavior-bearing subject: model revision
or weights, provider or resolved path, native harness and executable/version
probe, reasoning effort, inference settings, instructions, knowledge, tools,
permissions, sandbox, and relevant runtime configuration. A change to any of
these fields produces a different Binding. A generic model name is not a
Binding, and a proxy cannot stand in for a native harness unless an explicit
owner decision authorizes that exact subject.

A **Measurement** is an immutable observation for one Binding, capability
distribution, experiment, protocol, and corpus. It records sample flow,
rational metrics, evidence bases, case-selection lineage, evidence references,
covariates, and provenance. It contains no threshold or qualification status.

A **qualification policy** is a separately identified, versioned rule. It
checks applicability, evidence kinds, completeness, rational thresholds, and a
time-bounded authorization. Applying a policy produces an immutable **Claim**.
`qualified` and `unqualified` are decisions; `advisory` and `unmeasured` expose
insufficient authority or evidence without pretending that evaluation failed.

A qualified Claim means only that the exact Binding earned the named
capability, role, domain, and distribution under the cited Measurement and
policy during the Claim's validity interval. It does not mean that the model is
generally capable, best, currently reachable, enabled, affordable, within
quota, healthy, or suitable for a different harness, effort, population, or
protocol. A negative decision is also not a provider failure.

Claims are append-only. A new Claim may supersede older Claims, but does not
mutate them. Multiple unsuperseded heads remain visible because CAPLAB does not
choose which one a runtime should activate. The local JSONL ledger publishes
each logical append as one atomically replaced, file-and-directory-fsynced
stream image, so a failed write cannot expose a partial record. An exact retry
after an uncertain directory sync re-syncs the stream and object directories
before reporting idempotent success.

## Independent truth and the fate firewall

Version 1 admits two possible decision-grounding basis kinds:

- a registered deterministic or mechanical oracle; and
- a registered human-authorized judgment with an explicit delegation record.

Model judgments can support advisory observations. Downstream fate is stored,
if admitted, only as the `downstream_fate` covariate. Policy predicates cannot
read covariates. Decision metrics must name registered truth,
metric-derivation, and case-selection lineage, and a case selection conditioned
on downstream fate or model judgment cannot issue a decision over the original
population.

`caplab.revbench` is the first active experiment family at this boundary. It
prepares bounded known-defect/control pairs and scores registered captures
with a deterministic oracle. Its v1 executor supports a sealed static local
fixture and one bounded live-native profile: Codex CLI 0.147.0 with GPT-5.6
Terra at maximum effort on the configured direct OpenAI Responses route.
Subject-visible inputs are blinded to the arm and planted answer.

Live execution requires an exact registered clean-source apparatus receipt,
time-bounded authorization, and a separately owned nonrollback custody-domain
identity. It runs from the documented `/usr/bin/python3 -I -S -B` source
entrypoint, uses the packaged launcher/containment bundle, mounts a validated
credential through an anonymous read-only memfd, and streams raw output through
durable one-shot custody before registration. The credential profile is an
operator-declared mismatch guard, not provider-authenticated identity. The
one-shot guarantee covers one outer containment launch within an intact
custody root; it does not prove provider delivery or prevent Codex-internal
retries. Exact-scalar quarantine does not claim to detect encoded or fractured
secret leakage. The full operational and evidence limits are in the contract.

The offline scorer performs no provider call and does not consult historical
fate. Its output is a Measurement. The live configured route is
nonobservational and advisory-only under qualification v1; a separate policy
application remains required to produce any Claim. Implementation, live
execution, and green checks do not accept a qualification.

The source migration and its conservative A–E classification are recorded in
[`history/striatum-tuner/`](../../../history/striatum-tuner/README.md).

## Quartermaster boundary

`caplab qualification export` emits a deterministic
`caplab-qualification-export/1` document containing selected Claims and the
schema identities needed by an independent consumer. The public schema catalog
pins local schemas by SHA-256; consumers do not fetch the schema IDs as URLs.

Quartermaster will eventually ingest this artifact and own the runtime mapping
from capabilities to available Bindings. CAPLAB does not own enabled state,
reachability, health, capacity, quota, cost, preference, placement, or Dispatch
selection. No Quartermaster database, runtime registry, compatibility daemon,
or fleet service is implemented here.

The normative shapes, CLI operations, validation rules, and status semantics
are in the
[`CAPLAB qualification contract v1`](../contracts/caplab-qualification-contract-v1.md).
The decision and reopening conditions are in
[`ADR 0062`](../../decisions/adr-0062-binding-qualification-boundary.md). The
consumer obligations and exact next slice are in the
[`Quartermaster ingestion handoff`](quartermaster-handoff-v1.md).
