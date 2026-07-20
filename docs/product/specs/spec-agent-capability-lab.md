---
id: spec-agent-capability-lab
artifact_type: product-spec
title: Agent Capability Lab v0 charter
status: decided
owner: repository-maintainers
created: 2026-07-14
updated: 2026-07-15
supersedes: []
superseded_by: null
decision_owner: repository-owner
decision_authority: repository-ownership
decision_record: adr-0002
related_plans:
  - plan-agent-capability-lab-v0
---

# Agent Capability Lab v0 charter

Status interpretation: the repository owner selected this product boundary on
2026-07-15 after reviewing the integrated CAPLAB-1 interview answers. The
decision establishes the CAPLAB product contract. It authorizes no study, model
call, evidence retention, dataset export, training run, routing change,
deployment, or implementation, and records no verification or acceptance.

The governing architectural decision is
[`adr-0002-agent-capability-lab-v0`](../../decisions/adr-0002-agent-capability-lab-v0.md).

## Decision question and scope

Should this repository establish Agent Capability Lab (CAPLAB) as a behavioral
capability measurement and model-development platform for software agents, with
one complete checkout-retries vertical slice as v0?

CAPLAB would measure engineering judgment and other behaviors defined by
study-specific capability cards as separate constructs rather than infer them
from whether an agent produced a passing patch. Its evidence would support three
downstream purposes:

1. characterize a named evaluator's preference between agent configurations on
   a defined population of complex tasks and test preregistered candidate
   explanations for that preference;
2. qualify configurations for placement against externally owned Striatum pass
   requirements and scheduler-policy objectives; and
3. produce governed, training-eligible examples for later open-model
   fine-tuning.

Fine-tuning is an intended product use, not part of the v0 execution scope. An
actual fine-tuning run remains unavailable until CAPLAB has multiple validated
task families and a genuinely held-out evaluation family. Provenance, privacy,
and authority controls constrain CAPLAB; they are not the product's primary
purpose.

## Observations and evidence

**Observation:** The source repository already had a behavioral evaluation
surface that records what an agent reads, verifies, changes, and declines, with
verifier-owned observations and human adjudication where semantics require it.
**Evidence:** `halbritt/books` paths `docs/agent-judgment/README.md` and
`doctrine/evaluations/robustness/README.md`, as identified by the imported
record in [`source provenance`](../../source-provenance.md).

**Observation:** Checked-in checkout-retries records document one completed
clean/lying-contract and knowledge-surface study with bounded rewards, and
separately preregister a compact-verification treatment. **Evidence:**
`halbritt/books` paths
`doctrine/evaluations/robustness/harbor/tasks/checkout-retries-pair-report.md`,
`doctrine/evaluations/robustness/harbor/tasks/checkout-retries-activation-report.md`,
and `docs/agent-judgment/running-evaluations.md`. These are external source
locators, not CAPLAB evidence registration.

**Observation:** Repository language separates observations, inferences,
recommendations, decisions, authorization, execution, verification, and
acceptance. **Evidence:** CAPLAB's
[`ubiquitous language`](../../domain/ubiquitous-language.md), derived from the
selected assertion contract during repository separation.

**Observation:** CAPLAB-1 was previously marked Done from an agent-authored
charter that treated provenance and governance as the product and collapsed
subject identity with experimental conditions. The owner rejected that
interpretation and answered the replacement design branches interactively on
2026-07-14. CAPLAB-1 records the reopened review and the owner's 2026-07-15
selection of the integrated proposal. **Evidence:** local Plane work item
`CAPLAB-1`, its review comments, and the owner's explicit reply to the selection
question. Plane is coordination evidence, not product or decision authority.

## Inferences, assumptions, rivals, and uncertainty

**Inference:** The existing experiments can seed a general capability platform,
but only if CAPLAB preserves their historical scope and adds explicit identities
for what was configured, manipulated, observed, and generalized. A single
content-addressed trial envelope is necessary for provenance but is too coarse
to serve as every analytical identity.

**Inference:** Human preference, behavioral capability, Striatum placement, and
training eligibility can share trial evidence without becoming the same claim.
Each needs its own construct, owner, promotion rule, and output record.

Assumptions and uncertainty:

- checkout-retries can be registered without changing historical outcomes or
  retroactively applying new retention rules;
- the locally scoped S3-compatible store and system Postgres can receive
  dedicated CAPLAB namespaces and credentials during implementation;
- later task families will be independently designed strongly enough to test
  cross-task generalization rather than template recognition;
- an opaque provider alias may not identify immutable model weights, so claims
  about such a subject remain scoped to the observed provider route and time.

Credible alternatives are a study archive without a platform contract, a
governance-only registry, or an immediate system spanning every downstream use.
The first two cannot support the intended decisions; the last introduces too
many untested contracts before one complete vertical slice exists.

## Recommendation and alternatives

**Recommendation:** Select CAPLAB as the measurement platform described here
and deliver v0 as one complete scientific vertical slice using checkout-retries
Study 001. Require each broader claim and downstream use to earn its own
evidence and authorization.

`Study 001` will identify one exact historical checkout-retries experiment, not
the task family or a pool of its experiments. Before implementation, its
registration must bind the selected preregistration, result record, task and
world identities, and a verified preserved-input manifest. The repository owner
or a delegate named in a durable authority record must make that selection in a
separate Git-recorded Study 001 registration decision; the implementation plan
must link it and cannot infer the selection from available files. Other
checkout-retries experiments retain separate identities. Until that binding is
selected and recorded, Study 001 recomputation is unavailable.

Alternatives:

1. **No platform.** Keep experiments as independent reports. This avoids new
   infrastructure but leaves identity, generalization, placement, and training
   lineage inconsistent.
2. **Governance registry only.** Preserve manifests and decision boundaries
   without treating measurement as the product. This is the rejected prior
   interpretation.
3. **All downstream uses in v0.** Include preference studies, broad Striatum
   qualification, and model training before accepting v0. This delays feedback
   and couples several unresolved constructs.
4. **Global leaderboard.** Rank models with one aggregate. This is incompatible
   with role-conditioned measurement and the evidence needed for scientific
   generalization.

## Product contract

### Users and decisions served

- researchers and evaluation authors defining behavioral constructs and trials;
- named evaluators examining task-conditioned model preference;
- adjudicators making human-owned semantic judgments;
- Striatum policy owners evaluating configuration placement against governing
  pass requirements; and
- model developers producing and evaluating governed fine-tuning data.

CAPLAB may inform these decisions. It does not inherit their authority.

### Preference is not capability

A preference profile records a named evaluator's blinded, task-conditioned
judgments over paired outputs. It identifies the task population, comparison
dimensions, presentation and randomization method, and uncertainty. CAPLAB may
compare a preference profile with a behavioral capability profile, but it may
not translate preference into a global claim that one model is better. A claim
about what drives a preference must separately preregister its hypothesis,
credible rivals, evidence, and promotion rule. Correlation with a capability
profile is not a causal explanation.

### Capability cards

Capabilities begin as versioned, study-specific capability cards. A card names:

- the construct and intended task population;
- observable behaviors and verifier-owned endpoints;
- positive, negative, clean, and manipulation controls;
- credible rivals, confounders, and falsifiers;
- mechanical and human-owned judgments;
- scoring and exclusion rules; and
- evidence required for replication and generalization.

A shared capability taxonomy may be promoted only after multiple task families
support a stable meaning. CAPLAB does not begin with a universal capability
list.

### Claim ladder

Within each promotion path, the gates are cumulative: every broader claim
inherits the validity, instrument, missingness, scope, and uncertainty
requirements of its narrower source claims. Preference, placement, and training
eligibility are separate paths rather than automatic promotions from the
capability ladder. A broader claim cannot substitute new evidence for a
prerequisite.

| Claim | Minimum scope and evidence |
|---|---|
| Trial observation | One valid attempt under one sealed trial envelope. |
| Study-local estimate or association | A preregistered controlled study with a valid instrument, frozen analysis, and reported missingness and failures. |
| Causal treatment effect | A controlled contrast with randomized assignment, including randomization within blocks when blocking is used, treatment-fidelity evidence, and no unresolved differential instrument failure. A nonrandomized design requires a separate recorded identification decision, exchangeability assumptions, and falsification checks. |
| Task-family capability inference | Replication with the governing capability card's controls, rivals, and population stated. |
| Cross-task capability inference | At least two independently designed task families, including held-out confirmation. |
| Preference profile | Blinded judgments from a named evaluator over a declared task population; never an automatic capability promotion. |
| Preference-driver inference | A preregistered candidate explanation with declared rivals and repeated evidence across the intended task population. A causal driver claim additionally meets the causal-treatment gate. |
| Striatum placement recommendation | A qualifying capability profile compared with a governing external pass profile and explicit policy objective. |
| Training eligibility decision | A named human decision selecting identified examples under provenance, privacy, license, quality, and split rules. Export remains separately authorized. |

No CAPLAB result automatically creates a universal model ranking, safety claim,
routing decision, training authorization, deployment decision, verification, or
acceptance.

## Architecture and artifact contracts

### Layered identity

CAPLAB uses several identities rather than one overloaded subject tuple:

| Identity | Contents |
|---|---|
| Model identity | Immutable checkpoint and hash when available; otherwise the observed provider route, declared version or alias, response metadata, and observation time. |
| Agent configuration | Model identity, reasoning effort and sampling, harness/runtime/adapter versions, and tool surface. |
| Administration | Instruction and knowledge surfaces, role/pass package, and experimental treatment. |
| Trial context | Task and world identities, instrument and verifier versions, environment and hardware, budgets, randomization block, and relevant endpoint configuration. |
| Trial assignment | One sealed preregistered slot binding its condition, block, sequence position, planned denominator, and replacement or consumed-slot rules. |
| Attempt | One execution linked to a trial assignment and binding timestamps, interaction boundary, failure classification, replacement disposition, and preserved outputs. A slot may have zero, one, or multiple attempts only as its frozen rules permit. |
| Analysis key | The fields held fixed, manipulated, blocked, randomized, treated as nuisance, and included in the intended population of inference. |

The complete trial envelope is content-addressed. Changing a
behavior-relevant field changes that envelope, but does not silently redefine
which model, configuration, treatment, task family, or population an analysis
compares.

For agentic model comparisons, the default evaluated unit is the native agent
system defined by ADR 0039. The native harness is a behavior-bearing component
of the agent configuration, especially for models tuned for agentic workflows
in that harness. CAPLAB must not replace Claude Code and Codex CLI with a
shared proxy harness and then describe the result as a comparison of the
native systems. Common controls apply to task, authority, budgets, capture,
and scoring; irreducible native-harness differences remain part of the
treatment and must be reported.

### Scoped systems of record

CAPLAB uses one authoritative system of record per kind of state:

- **Local S3-compatible object storage:** authoritative bytes for immutable,
  content-addressed attempt bundles, derived datasets, and preservation
  manifests. Final human disposition records and the outcome records that link
  them to validated observations are content-addressed here and bound into
  result and dataset manifests. CAPLAB uses a dedicated bucket and credentials
  with recorded access, retention, and purge state.
- **System Postgres:** transactional system of record for live study metadata,
  registered identities, attempts, artifact locators, lineage, permissions,
  adjudication workflow state and pointers, and operational state transitions.
  Mutable workflow rows do not replace frozen adjudication artifacts. SQLite is
  not a second supported operational backend; it may be used only for
  disposable prototypes or explicitly non-authoritative offline exports.
- **Git:** standalone CAPLAB Git owns governing specifications, code identities,
  admitted manifests, normalized results, and durable decision, verification,
  and acceptance records. Before P6, the source repository remains authoritative
  for selected historical preregistrations, results, and content identities.
- **Plane:** planning projection and collaboration surface. It may link to
  authoritative records but cannot create evidence or decision authority.
  Public Plane surfaces receive only sanitized summaries and links.

Every inference-bearing result must bind a frozen manifest in S3 or Git so the
claim does not depend on mutable Postgres state. Database rows and object
locators must carry enough content identity to detect drift or substitution.

### Training-data lineage

CAPLAB preserves this lineage without performing v0 fine-tuning:

```text
trial/capture -> validated observation -> outcome record
              -> human disposition when required -> derived example
              -> label and reward provenance -> eligibility decision
              -> authorized export -> authorized training
              -> trained checkpoint -> held-out family evaluation
```

Authorized retention may preserve every attempt for audit. Only examples
derived from evidence-valid observations and carrying any required human
disposition are training-eligible. Eligible data may include successful behavior
and informative failures. Provider or infrastructure failures, compromised
verifiers, ambiguous judgments, and leaked evaluation cases are excluded.
Dataset splits keep task families and scenario templates together so held-out
evaluation remains unseen. CAPLAB may prepare an authorized eligible export in
v0, but no actual fine-tuning run is eligible for authorization until multiple
task families are validated and a genuinely held-out evaluation family has been
reserved.

## Constraints, invariants, and preservation boundaries

- Historical studies retain their recorded tasks, treatments, results,
  corrections, failures, stopping rules, and claim scope.
- Registration cannot rewrite a historical outcome or retroactively authorize
  retention.
- Mechanical grading remains an observation; semantic judgment remains human
  unless a governing construct defines a deterministic oracle.
- A mutable or unverifiable provider alias supports only provider-route-local
  claims.
- CAPLAB cannot populate a human-owned judgment, decision, verification, or
  acceptance record under that human's identity.
- Target systems retain their own semantics and authority. For Striatum, model
  choice remains scheduler policy, a lane remains an execution context, and the
  Principal retains acceptance authority.
- Passing repository, instrument, or statistical checks does not promote the
  resulting assertion or grant downstream authority.

## Striatum placement contract

CAPLAB compares an agent configuration, under a specified administration and
declared trial population, with an externally governing pass profile and lane
requirement. The administration binds the tested instruction, knowledge,
role/pass package, and treatment surfaces. Changing one narrows or invalidates
the placement evidence unless separate evidence supports that generalization. A
placement report first applies the profile's quality, safety, and independence
floors. Among qualifying envelopes, it reports the cost, latency, and capacity
frontier. CAPLAB names one preferred envelope only when the target scheduler
policy supplies an explicit utility rule. The report is a recommendation;
Striatum owns placement selection, execution, verification, and acceptance.

## Authorization and human ownership

CAPLAB may automatically:

- verify manifest, capture, and instrument integrity;
- classify outcomes whose oracle is mechanical and preregistered; and
- compute frozen preregistered statistics.

A named human owns each semantic judgment, construct interpretation, capability
or preference inference, training-eligibility decision, and study conclusion.
Automation may prepare observations, estimates, or recommendations but cannot
record a human-owned assertion under that human's identity. The repository
owner controls privacy and retention exceptions, paid-inference authorization,
dataset-export authorization, and training authorization unless authority is
explicitly delegated in a durable record. Plane access and technical capability
do not delegate those powers.

Paid inference requires a separate authorization fixing subject configurations,
sample and order, maximum spend or local compute, output handling, replacement
and stopping rules, and authorization expiry. Dataset export and training are
separate authorizations.

## Failure modes and operational response

CAPLAB fails closed when an identity, artifact hash, provenance edge, required
human judgment, authorization, or instrument invariant is missing. It records
provider, capacity, harness, capture, verifier, adjudication, and subject
outcomes as distinct states.

- An invalid or incomplete attempt remains in the audit record but cannot be
  silently replaced or treated as subject behavior.
- A missing or mismatched S3 object invalidates dependent recomputation until
  repaired or explicitly excluded.
- A database-to-manifest mismatch blocks claim publication.
- A public-projection redaction failure blocks publication; it does not move
  raw evidence to Plane.
- A failed claim-promotion gate leaves the narrower claim intact and the broader
  claim unavailable.

## V0 product slice

V0 is complete only when CAPLAB can:

1. register one exactly identified historical checkout-retries experiment as
   Study 001 without rewriting its history or pooling adjacent experiments;
2. represent layered identities, sealed trial assignments, and one governing
   capability card;
3. store operational metadata in Postgres and immutable evidence in the
   dedicated S3-compatible store;
4. recompute one frozen study result from preserved inputs;
5. emit a bounded capability profile and an authorized training-eligible export;
6. show unsupported cross-task and Striatum placement claims as unavailable;
   and
7. preserve verification evidence for each step and obtain owner acceptance of
   the integrated slice.

Blinded preference measurement and multi-family Striatum qualification are
later milestones. Actual fine-tuning is also later and remains gated on multiple
validated task families plus a genuinely held-out evaluation family. The v0
contracts must leave those paths open without pretending they have been
validated.

## Verification and acceptance criteria

This selected specification's decision record is mechanically conformant when
metadata validates, internal links resolve, repository documentation checks
pass, and the ADR and product index agree on lifecycle state. Those checks
verify the record; the owner's selection created the decision.

After separately authorized implementation, v0 requires:

- byte and hash verification from registered Study 001 inputs through its
  recomputed result;
- database and object-store integrity and recovery tests;
- model-free fixtures for valid, invalid, missing, tampered, and ambiguous
  records;
- an independent check of claim-scope and training-split enforcement; and
- final acceptance by the repository owner after reviewing the verified slice.

## Rollout, reversal, and reopening

The smallest rollout is Study 001 registration and model-free replay. No new
model call is required to establish the storage, identity, lineage, and claim
contracts. Each later paid study, export, training run, or scheduler-policy
change is separately authorized.

Before any production consumer exists, reversal means withdrawing this
specification, preserving historical experiment records, and deleting only
CAPLAB-owned projections or newly created state under an authorized retention
and migration plan.

Reopen the charter if:

- a material confounder cannot be represented by the layered identities;
- preference and capability cannot remain separate in actual studies;
- cross-task evidence contradicts the capability-card model;
- target-system placement needs authority or semantics CAPLAB cannot lawfully
  own;
- privacy, licensing, backup, recovery, audit, or retention controls prove
  insufficient;
- Postgres or S3 operation makes the vertical slice disproportionate; or
- fine-tuning requires a materially different evidence or lineage contract.

## Unresolved implementation questions

This product decision did not itself select the exact frozen checkout-retries
experiment or capability card. ADR 0004 subsequently selected the exact C9
experiment, and ADR 0006 selected the exact version 0.1.0 Study 001 capability
card. The Postgres schema, object-store bucket name, retention implementation,
service interface, deployment topology, runtime serialization, and migration
sequence remain unresolved. The implementation plan links the downstream
selections and cannot infer the remaining answers from available files. Those
questions require current runtime evidence and separately authorized work.

## Decision and authorization record

**Decision:** The repository owner selected the integrated CAPLAB v0 product
boundary on 2026-07-15. **Owner and authority:** repository owner under
repository ownership. **Decision record:**
[`adr-0002-agent-capability-lab-v0`](../../decisions/adr-0002-agent-capability-lab-v0.md).

The owner's reply authorized recording this selection and closing CAPLAB-1. It
did not authorize CAPLAB implementation, Study 001 selection, model calls,
storage changes, evidence retention, dataset export, training, routing, or
deployment. Each requires a separate bounded decision or authorization as
specified above.
