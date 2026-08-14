# Build task: merge `striatum-tuner` into `caplab` and establish the binding-qualification boundary for Quartermaster

## Goal

Consolidate `striatum-tuner` and `caplab` into a single capability-measurement system, with **caplab as the surviving authority**.

This is not primarily a repository-cleanup exercise. It is an architectural correction.

`striatum-tuner` grew around the idea of learning backend suitability from downstream Striatum outcomes. That signal is contaminated: downstream fate is affected by the implementation, subsequent agents, retries, task difficulty, selection effects, and by the review itself. It is useful as observational metadata but is not independently authorized truth and therefore cannot be the foundation for capability qualification.

`caplab` is the proper home for capability measurement.

The resulting system must move toward this architecture:

```text
                    slow evidence loop

     independently authorized corpora / experiments
                         |
                         v
                       caplab
        measure bindings against explicit protocols
                         |
                         v
        qualification claims + evidence bundles
                         |
                         v
                    Quartermaster
            runtime capability registry
                         |
                         v
                 Dispatch / callers
```

The immediate task is to make the **caplab side of this boundary real and coherent**.

Do not build Quartermaster in this task.

Do build the artifact/schema that Quartermaster will eventually consume.

---

## 1. Execution model: fan out aggressively

This task is explicitly intended for a high-parallelism agent harness.

**Do not approach it as one agent reading both repositories serially and then implementing everything itself.**

Fan out immediately.

The coordinator owns:

- architectural invariants;
- decomposition;
- dependency ordering;
- merge decisions;
- integration;
- final verification.

Sub-agents own bounded investigations and implementation slices.

Prefer parallel discovery and parallel implementation wherever work does not have a true data dependency.

A useful initial fan-out is:

```text
                         coordinator
                              |
       ┌──────────────────────┼────────────────────────┐
       │                      │                        │
       v                      v                        v
 caplab archaeology     tuner archaeology       revbench analysis
       │                      │                        │
       ├──────────────┬───────┴───────────┬────────────┤
       │              │                   │            │
       v              v                   v            v
 binding model   provenance model   qualification   test/migration
    review            review          schema review     review
```

Do not limit fan-out to these exact roles if additional independent work is visible.

Spawn additional agents when a task can be made:

- independently inspectable;
- bounded by files/directories/interfaces;
- reviewable from its output;
- mergeable without hidden shared state.

Avoid spawning agents for trivial work whose coordination cost exceeds the work itself.

---

## 2. Parallelism rules

Use the following rules throughout the task.

### Fan out before deciding

For architecture-sensitive questions, prefer two or more independent analyses before committing.

Examples:

- canonical binding identity;
- qualification-claim schema;
- migration strategy;
- provenance representation;
- treatment of tuner history;
- compatibility boundary.

Have agents inspect independently, then synthesize.

Do not allow the first plausible proposal to become architecture merely because it arrived first.

### Parallelize repository archaeology

At minimum, inspect `caplab`, `striatum-tuner`, and `revbench` concurrently.

Each archaeology agent should report:

```text
purpose as implemented
current authority boundaries
core data models
CLI/API surface
persistent state
tests
useful reusable code
incorrect assumptions
integration dependencies
likely extraction/migration units
```

The coordinator should synthesize these reports before committing to destructive migration.

### Parallelize implementation by ownership boundary

Once schemas and ownership are pinned, divide implementation into independent slices where possible.

Likely slices include:

```text
binding identity + serialization

experiment / measurement model

revbench migration

qualification policy

qualification claim schema + export

tuner historical-data migration

compatibility adapter

boundary/conformance tests

documentation
```

Do not serialize these unnecessarily.

Where one slice depends on a schema, pin the schema first and let all consumers implement against it concurrently.

### Pin interfaces early

Parallelism works only if shared boundaries stop moving.

The coordinator should establish the minimum stable contracts early:

1. binding identity;
2. measurement record shape;
3. qualification-policy interface;
4. qualification-claim schema;
5. evidence/provenance reference shape.

Once pinned, treat them as integration contracts.

Do not let sub-agents independently invent incompatible variants.

Changes to a pinned contract require coordinator approval and explicit propagation.

### Agents do not silently redesign neighboring layers

A sub-agent may identify a boundary problem.

It should report it.

It should **not** independently solve it by introducing:

- Quartermaster behavior;
- Dispatch behavior;
- runtime fleet state;
- another service;
- another registry;
- a workflow engine.

The coordinator owns architectural expansion.

### Integrate continuously

Do not wait for every branch of work to finish before integrating anything.

Use waves:

```text
Wave 1:
  archaeology + schema proposals

Wave 2:
  pin contracts

Wave 3:
  parallel implementation

Wave 4:
  integration + migration

Wave 5:
  adversarial review + conformance tests

Wave 6:
  cleanup + documentation
```

Merge low-risk, contract-conforming work as it becomes ready.

Keep the integration branch continuously runnable where practical.

---

## 3. Architectural ownership

The final ownership model is:

### caplab owns

- benchmark/evaluation corpora;
- experiment definitions;
- test protocols;
- synthetic defect injection;
- mechanical oracles;
- human-adjudicated preference/outcome data;
- benchmark execution;
- measurements;
- qualification criteria;
- qualification decisions;
- evidence bundles;
- qualification history;
- provenance for all of the above.

Caplab answers:

> **What has this exact binding been measured to be capable of, under what protocol, and what evidence supports the claim?**

### Quartermaster will own

Not part of this implementation, but design toward this interface.

Quartermaster will own:

- current binding inventory;
- current capability registry;
- active/inactive state;
- capability → eligible-binding queries;
- imported qualification claims;
- references back to caplab evidence.

Quartermaster will answer:

> **Which currently available bindings are qualified to satisfy this capability requirement?**

Caplab must **not** become the runtime capability registry.

Do not add runtime fleet state, quota state, provider health, current model availability, or dispatch policy to caplab.

### Dispatch is out of scope

Dispatch is the Inference Control Plane and will eventually:

```text
caller capability request
        ↓
Dispatch
        ↓
Quartermaster.resolve(...)
        ↓
eligible bindings
        ↓
Dispatch selects according to live cost/capacity/latency/quota state
        ↓
invoke
```

None of those runtime selection semantics belong here.

---

## 4. Merge direction

`caplab` survives.

`striatum-tuner` is absorbed into caplab.

Do **not** create a third abstraction or compatibility daemon between them merely to avoid making a decision.

Preserve useful code, datasets, protocols, historical measurements, and concepts from `striatum-tuner`, but relocate/reframe them according to the authority model above.

The desired end state is conceptually:

```text
caplab/
    experiments/
    corpora/
    protocols/
    qualification/
    evidence/
    ...
```

Exact internal organization must be derived from repository reality.

Do not cargo-cult this directory tree if the existing code suggests a cleaner organization.

---

## 5. Preserve the useful lesson from `striatum-tuner`

The important correction is epistemic.

Downstream Striatum fate is **not qualification ground truth**.

Do not silently discard existing fate/outcome data; it may remain valuable as a covariate or research signal.

It must not authorize capability claims.

Allowed:

```text
input
binding output
independent oracle result
downstream fate
```

where `downstream fate` is metadata for later analysis.

Not allowed:

```text
downstream artifact succeeded
therefore reviewer was correct
therefore binding is qualified
```

Capability qualification must derive from an independently authorized target.

---

## 6. Fold `revbench` into caplab

`revbench` becomes a named **caplab methodology/experiment family**, not another standalone product.

Its essential structure is:

```text
known artifact
    ↓
mechanically inject known defect
    ↓
binding performs review
    ↓
independent oracle knows planted truth
    ↓
measure whether binding detected it
```

This solves the central defect in fate-based tuning: the target exists independently of the binding being measured.

Preserve `revbench` as useful vocabulary, e.g.:

```text
caplab revbench ...
```

or the closest idiomatic equivalent for the actual CLI.

Do not create a new repo for it.

Assign revbench migration to its own sub-agent where practical.

That agent should not redesign the general caplab qualification model; it implements revbench against the contracts pinned by the coordinator.

---

## 7. Two initial sources of authorized truth

Support at least these two qualification-data classes.

### A. Mechanically authorized experiments

Examples:

- planted defects;
- known-invalid transformations;
- deterministic oracle checks;
- controlled mutations.

These should be plentiful, reproducible, cheap, and suitable for automated campaigns.

`revbench` belongs here.

### B. Human-authorized observations

Examples:

- owner adjudications;
- explicit A/B preference decisions;
- manually labeled correct/incorrect review outcomes;
- curated capability examples.

These are sparse and expensive but authoritative.

Preserve provenance identifying the human authorization without hard-coding any one person's identity into the data model.

---

## 8. Capability claims must be binding-specific

Do not qualify abstract model names.

The measured subject is an **exact binding**.

A binding may include at least:

```text
model
provider or serving path
harness
reasoning effort
relevant inference configuration
prompt/protocol version where it materially affects measured capability
```

A change that could invalidate the measurement must produce a distinct binding or qualification identity.

Examples:

```text
gemini-X / Gemini CLI / medium

gemini-X / Gemini CLI / high

same model / OpenRouter provider A / high

same model / direct API / high

local model / serving stack Z
```

These are potentially different capability-bearing objects.

Do not collapse them merely because the nominal model string is identical.

Have at least one independent sub-agent adversarially review the proposed binding identity for stale-qualification hazards before pinning it.

---

## 9. Capability claims are role/domain qualified

Do not produce a single global statement such as:

```text
binding A is good
```

The system needs claims shaped more like:

```text
binding A:
    review.correctness: qualified
    review.spec_conformance: qualified
    review.security: unmeasured
    ui.mobile_critique: weak
    synthesis: qualified
```

A measurement establishes capability only over the distribution actually tested.

A high `revbench` score over mechanically injected correctness defects does not imply competence in:

- security review;
- UI aesthetics;
- synthesis;
- architecture;
- unrelated coding tasks.

Represent this explicitly.

---

## 10. Define a stable qualification-claim artifact

Create a versioned, machine-readable schema intended to be consumed later by Quartermaster.

Quartermaster must not need to understand caplab internals.

The exact schema is yours to design, but it must express at least:

```yaml
schema_version: ...

claim_id: ...
generated_at: ...

binding:
  id: ...
  model: ...
  provider_or_path: ...
  harness: ...
  reasoning_effort: ...
  configuration: ...

capability:
  name: review.correctness
  version: ...

qualification:
  status: qualified | unqualified | advisory | unmeasured
  threshold_version: ...

measurement:
  experiment: revbench
  experiment_version: ...
  corpus: ...
  corpus_hash: ...
  sample_count: ...
  metrics: ...

evidence:
  bundle_ref: ...
  run_refs: ...

provenance:
  caplab_version: ...
  protocol_hash: ...
```

Do not blindly implement this exact YAML if a better representation follows from the existing code.

The contract matters more than the spelling.

Requirements:

- deterministic serialization where practical;
- explicit schema version;
- immutable evidence references;
- binding identity sufficient to prevent accidental reuse of stale qualification;
- protocol/corpus identity;
- qualification status;
- enough metrics for humans to inspect why the status was granted;
- provenance sufficient to reproduce or audit the claim.

Assign schema design and schema adversarial review to different agents.

The schema author should not be its only reviewer.

---

## 11. Qualification claims are append/supersede, not mutable truth

Do not model qualification as a mutable Boolean attached to a backend.

A claim is evidence-backed historical state.

A later experiment may supersede it.

Desired conceptual model:

```text
claim A
  binding X
  capability Y
  qualified
  evidence E1

claim B
  supersedes A
  binding X
  capability Y
  unqualified
  evidence E2
```

Quartermaster will later decide which current claim is active for runtime use.

Caplab preserves evidence history.

---

## 12. Qualification policy

Separate:

```text
measurement
```

from:

```text
qualification policy
```

For example:

```text
score = 0.81
n = 800
```

is measurement.

```text
score >= threshold under protocol V3 → qualified
```

is qualification policy.

Both belong in caplab, but they must remain distinguishable.

Do not bury qualification thresholds inside experiment implementation code.

Version policy changes.

A binding may need requalification when:

- the experiment changes;
- the corpus materially changes;
- the qualification threshold changes;
- the binding changes;
- the inference protocol changes materially.

---

## 13. Keep capability validation honest

Avoid the following failure modes.

### Endogenous labels

Do not infer truth from outcomes the tested binding helped cause.

### Same-distribution overclaiming

Do not extrapolate from one experiment family to unrelated capabilities.

### Model-name collapse

Do not assume different harness/provider/reasoning configurations are equivalent.

### Stale qualification

Do not leave a capability claim silently valid after the measured binding changes.

### Circular judging

Where a model judge is involved, clearly distinguish model-judged evidence from mechanically or human-authorized truth.

### Hidden provenance

Every qualification must trace to an experiment/protocol/corpus.

Have an adversarial-review agent specifically search for ways the proposed implementation could accidentally violate these rules.

---

## 14. Integrate useful `striatum-tuner` history

Inspect `striatum-tuner` before deleting or rewriting anything.

Classify existing functionality into:

```text
A. valid capability measurement

B. useful observational/covariate data

C. reusable infrastructure

D. obsolete fate-derived qualification logic

E. unclear — preserve until understood
```

Migrate A–C.

Preserve D only where required for historical reproducibility or comparison, and clearly mark it non-authoritative.

Do not delete historical data simply because the original interpretation was wrong.

An incorrect metric can still be useful research evidence.

This classification should be performed independently by at least two agents if the repository is nontrivial; reconcile disagreements before destructive migration.

---

## 15. Keep compatibility only where useful

If current Striatum code depends on `striatum-tuner`, provide the minimum migration seam necessary to avoid blocking unrelated work.

Prefer:

```text
old interface
    ↓
thin compatibility adapter
    ↓
new caplab implementation
```

over maintaining two independent authorities.

Compatibility code must be visibly temporary and documented with a removal condition.

Do not let compatibility requirements distort the new caplab data model.

---

## 16. Striatum integration direction

Striatum is currently developing capability-aware placement.

Do not make Striatum permanently understand how qualification was established.

It should eventually require something like:

```text
capability: review.correctness
qualification: qualified
```

rather than:

```text
revbench_score > X
```

or:

```text
backend_rank = ...
```

or:

```text
Gemini-X is reviewer tier 2
```

If today's implementation requires an intermediate generated artifact or local adapter, keep that boundary evidence-oriented so Quartermaster can replace it later.

The long-term path is:

```text
caplab
    ↓ qualification claims
Quartermaster
    ↓ capability → bindings
Dispatch
    ↓ execution
striatum
```

Do not implement runtime Quartermaster behavior inside Striatum as a convenience.

---

## 17. Quartermaster-facing output

Provide a straightforward export operation suitable for future ingestion.

Conceptually:

```text
caplab qualification export ...
```

which yields one or more versioned qualification claims.

It must be possible for a future Quartermaster importer to:

1. validate schema;
2. verify binding identity;
3. read capability name/version;
4. determine qualification status;
5. preserve evidence references;
6. import without understanding caplab's database or experiment internals.

Do **not** couple caplab directly to a Quartermaster database.

The boundary is an artifact/schema.

A separate sub-agent should build or review a small fake/fixture consumer that proves Quartermaster-style ingestion is possible without importing caplab internals.

Do not implement Quartermaster itself.

---

## 18. No runtime registry in caplab

This is a hard boundary.

Caplab may know that a binding was tested.

It must not become authoritative for whether that binding is currently:

- enabled;
- installed;
- reachable;
- administratively disabled;
- preferred;
- available under quota;
- healthy;
- economically desirable.

A binding may be:

```text
qualified in caplab
```

while:

```text
absent from Quartermaster
```

or:

```text
present but disabled in Quartermaster
```

Likewise a new binding may exist operationally before it has any caplab qualification.

That distinction is intentional.

---

## 19. CLI/API surface

Inspect the existing CLI conventions and preserve them where sensible.

The resulting tool should support the conceptual operations:

```text
run an experiment

run revbench

inspect results

apply qualification policy

inspect binding qualification history

export qualification claims
```

Do not add a daemon or workflow engine unless one already exists and is essential.

Prefer a CLI plus durable artifacts.

---

## 20. Data/provenance requirements

For every measurement run preserve enough information to answer:

```text
What exact binding ran?

Against what exact corpus?

Under what exact protocol?

With what exact inference configuration?

What target/oracle authorized correctness?

What raw outputs were produced?

What metrics were derived?

What qualification policy was applied?

What software version performed the experiment?
```

Content hashes should be used for immutable corpora/protocol/evidence where practical.

A qualification claim without reproducible provenance is not a qualification claim.

---

## 21. Testing strategy

Testing is itself parallel work.

Assign independent agents to:

- unit/schema tests;
- migration tests;
- adversarial boundary tests;
- end-to-end qualification tests.

At minimum, prove the following.

### Known defect corpus

Run a small deterministic `revbench` corpus where expected detections are known.

Verify measurement output.

### Fate contamination test

Demonstrate that downstream fate can be stored but cannot independently produce a qualified claim.

### Binding identity test

Changing a qualification-relevant binding dimension must prevent accidental reuse of the old claim.

Examples:

```text
reasoning effort changes
harness changes
provider changes
protocol changes
```

### Qualification threshold test

Same measurement + different versioned threshold should produce appropriately different qualification results without mutating historical measurements.

### Export conformance

Exported claims validate against the published schema.

### Supersession/history

New evidence can supersede an old claim without deleting or rewriting historical evidence.

### Compatibility path

If a temporary `striatum-tuner` adapter remains, prove it delegates to the new authority rather than maintaining parallel state.

### Fake Quartermaster consumer

A minimal independent consumer can ingest exported claims using only the public schema.

---

## 22. Adversarial review wave

Before declaring completion, fan out a dedicated review wave.

Use separate agents to inspect the integrated result from at least these perspectives:

### Epistemic review

Look for contaminated labels, circular qualification, overclaiming, and unverifiable evidence.

### Boundary review

Look for runtime registry semantics, Dispatch semantics, fleet state, or orchestration leaking into caplab.

### Migration review

Look for lost historical data, duplicated authority, and compatibility paths that accidentally became permanent.

### Schema review

Look for stale-binding hazards, underspecified provenance, mutable truth, and Quartermaster coupling.

### Operational review

Run the actual CLI and end-to-end qualification flow from a clean checkout.

Do not let the implementation agents self-certify these properties without independent review.

Reconcile findings centrally.

---

## 23. Documentation

Write or update architecture documentation explaining:

1. why `striatum-tuner` was absorbed;
2. why downstream fate is not qualification truth;
3. caplab's authority boundary;
4. what a binding is;
5. what a capability-qualified claim means;
6. what it does **not** mean;
7. the difference between measurement and qualification;
8. why Quartermaster, not caplab, will own the runtime capability registry;
9. the export boundary toward Quartermaster;
10. where `revbench` now lives.

Do not present the old tuner model as foolish; document the empirical reason it was superseded.

---

## 24. Migration outcome

At completion, the system must satisfy:

```text
striatum-tuner
    no longer exists as an independent capability authority

revbench
    exists as a caplab experiment/methodology

caplab
    is the sole authority for capability evidence and qualification claims

Quartermaster boundary
    is represented by a stable exported qualification-claim schema

runtime capability registry
    is NOT implemented in caplab

downstream fate
    may be preserved as metadata
    but cannot authorize qualification

bindings
    are qualified per capability using independently authorized evidence
```

---

## 25. Parallel build plan

Use this as the default execution shape unless repository reality reveals a stronger dependency structure.

### Wave 1 — fan-out archaeology

Run concurrently:

```text
Agent A: caplab architecture and data-model inventory

Agent B: striatum-tuner architecture, history, and dependency inventory

Agent C: revbench methodology and implementation inventory

Agent D: current Striatum capability-placement integration surface

Agent E: provenance/evidence review

Agent F: existing test/fixture/corpus inventory
```

Each produces a concise written report.

Coordinator synthesizes.

### Wave 2 — fan-out contract proposals

Run concurrently:

```text
Agent A: canonical binding identity proposal

Agent B: measurement/evidence model proposal

Agent C: qualification policy model proposal

Agent D: Quartermaster-facing claim schema proposal

Agent E: migration strategy proposal

Agent F: adversarial critique of likely authority-boundary failures
```

Coordinator reconciles and **pins contracts**.

Do not proceed with broad implementation until the shared contracts are coherent.

### Wave 3 — parallel implementation

Once contracts are pinned, fan out:

```text
Agent A: binding + measurement primitives

Agent B: revbench migration into caplab

Agent C: qualification policy + claim generation

Agent D: qualification export + schema validation

Agent E: tuner data/history migration

Agent F: temporary compatibility path, if required

Agent G: provenance/evidence persistence

Agent H: test fixtures and known-defect corpora
```

Add or collapse agents according to actual code boundaries.

Implementation agents work against pinned contracts.

### Wave 4 — integration

Coordinator integrates continuously.

Resolve:

- API mismatches;
- duplicated concepts;
- incompatible persistence assumptions;
- migration edge cases;
- CLI consistency;
- historical-data preservation.

Do not solve integration failures by restoring duplicated authority.

### Wave 5 — parallel verification

Run independently:

```text
epistemic reviewer
boundary reviewer
schema reviewer
migration reviewer
operational end-to-end reviewer
```

Also run automated tests concurrently where possible.

Require evidence for acceptance.

### Wave 6 — final cleanup

Only after behavior and boundaries are proven:

- remove dead tuner authority code;
- mark temporary compatibility code;
- update documentation;
- normalize CLI help;
- produce migration notes;
- produce Quartermaster handoff notes.

Do not perform unrelated aesthetic refactors.

---

## 26. Dependency discipline

Do not serialize work merely because the task description is written linearly.

The true dependency graph is approximately:

```text
repo archaeology ─────────┐
                          ├──> contract pinning
schema proposals ─────────┘           |
                                      |
                    ┌─────────────────┼─────────────────┐
                    v                 v                 v
              revbench move     tuner migration    qualification
                    |                 |                 |
                    └──────────────┬──┴─────────────────┘
                                   v
                              integration
                                   |
                    ┌──────────────┼──────────────┐
                    v              v              v
                 tests          review          docs
```

Exploit that graph.

If two tasks do not depend on each other's output, they should normally execute concurrently.

---

## 27. Scope guard

Do not let this task turn into:

- Quartermaster implementation;
- Dispatch implementation;
- Striatum placement redesign;
- global model routing;
- quota management;
- provider selection;
- benchmark-framework rewrite for aesthetic cleanliness;
- database-platform migration;
- general experiment orchestration infrastructure.

The purpose is narrower:

> **Make caplab the trustworthy measurement and qualification authority, absorb the useful parts of striatum-tuner and revbench into it, and establish the durable evidence boundary through which Quartermaster will later learn which bindings have earned which capabilities.**

---

## 28. Coordinator instructions

The primary agent is a coordinator and integrator, not a lone implementer.

It must:

- fan out immediately;
- keep multiple independent investigations in flight;
- identify true dependencies rather than serializing by habit;
- pin shared contracts early;
- prevent sub-agents from expanding scope;
- integrate results continuously;
- send uncertain architectural questions to multiple agents independently;
- prefer evidence from repository inspection over assumptions;
- use independent adversarial reviewers before acceptance.

Do not ask the owner for implementation preferences that can be resolved from the architecture, repository evidence, or independent agent review.

Escalate only genuine architectural contradictions or decisions whose consequences cross the stated boundaries.

---

## 29. Completion report

At completion, report concisely:

- what moved from `striatum-tuner`;
- what was deleted;
- what remains temporarily compatible;
- where `revbench` now lives;
- the authoritative data path;
- binding identity definition;
- schemas introduced;
- qualification policy mechanism;
- historical data preserved;
- tests proving the authority boundary;
- results of adversarial review;
- any unresolved architectural conflicts;
- exact follow-on needed for Quartermaster ingestion.

Also provide the final flow:

```text
exact binding
    ↓
caplab experiment
    ↓
independently authorized measurement
    ↓
versioned qualification policy
    ↓
qualification claim
    ↓
immutable evidence reference
    ↓
Quartermaster-consumable export
```

The success criterion is not:

> the repositories were merged.

The success criterion is:

> **Capability qualification now has one trustworthy home, produces evidence-backed binding claims through a stable boundary, no longer derives authority from downstream fate, and the implementation was produced and independently challenged through deliberate parallel fan-out rather than one serial agent path.**
