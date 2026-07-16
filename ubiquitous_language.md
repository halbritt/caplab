# Ubiquitous language

This file defines the canonical vocabulary for CAPLAB evaluations, studies,
reviews, plans, and decision records. Pincite-owned corpus and doctrine terms
retain the meanings and provenance of the pinned Pincite release.

The central rule is simple: label the kind of claim being made, and never silently promote one kind into another.

## Core terms

### Observation

An **observation** is a directly inspectable fact supported by identified evidence. It reports what was found without adding a causal explanation.

An observation should state:

- the fact observed;
- the evidence, method, or locator that supports it;
- the relevant time or version when the fact may change;
- any material limits in what was inspected.

An observation is not an inference merely because it is surprising, and it does not create authority to act.

Preferred form:

> **Observation:** `<fact>`. **Evidence:** `<source, locator, or method>`.

### Inference

An **inference** is an interpretation or causal explanation drawn from one or more observations. It may fit the evidence without being the only possible explanation.

An inference should state:

- the observations on which it depends;
- plausible rival explanations;
- contradictory or missing evidence;
- confidence or a condition that would falsify it when useful.

An inference does not become an observation through repetition. It also does not select a response or grant permission.

Preferred form:

> **Inference:** `<explanation>`, based on `<observations>`. **Rivals or uncertainty:** `<alternatives or missing evidence>`.

### Recommendation

A **recommendation** is a preferred response, ranked against alternatives under stated evidence and assumptions. It advises a decision owner but does not bind that owner or authorize action.

A recommendation should state:

- the response proposed;
- the decision rule or reasons for preferring it;
- meaningful alternatives, including no action when relevant;
- costs, risks, reversibility, and missing evidence;
- the conditions under which another response would be better.

Preferred form:

> **Recommendation:** `<preferred response>`. **Alternatives:** `<other responses>`. **Tradeoffs and conditions:** `<costs, risks, and assumptions>`.

### Decision

A **decision** is the recorded selection of an option by an identified decision owner or delegated mechanism within a defined scope. It resolves a question for that scope until it is superseded or its stated conditions no longer hold.

A decision should state:

- the question resolved and option selected;
- the decision owner;
- the source and scope of the owner's authority;
- the observations, inferences, and recommendation considered;
- the rationale, constraints, and conditions that would reopen it.

A decision is not execution, proof of effect, or acceptance. A decision includes authorization only when the decision owner explicitly has and exercises authority to authorize the action.

Preferred form:

> **Decision:** `<selected option>`. **Owner and authority:** `<owner, source, and scope>`. **Rationale and reopening conditions:** `<basis and conditions>`.

## Related terms

### Evidence

Material that can support or contradict an observation or inference. Evidence should retain provenance sufficient for another reader or agent to inspect it. Evidence can improve confidence; it cannot create authority.

### Assumption

A proposition treated as true for the purpose of analysis or action without direct confirmation. Assumptions must be visible when changing one could change the inference, recommendation, or decision.

### Hypothesis or diagnosis

A testable causal inference explaining a set of observations. A diagnosis is a hypothesis that has survived proportionate attempts to disconfirm it; it remains distinct from the underlying observations.

### Proposal

A concrete prospective artifact or change offered for consideration. A proposal may embody a recommendation, but it is not authoritative state until selected and authorized.

### Selection

The act of choosing among alternatives. The durable record of that selection is the decision.

### Authorization

Permission granted by the actual owner or an explicitly delegated mechanism to perform an action within a stated scope. Access, capability, evidence, recommendation, and selection do not independently confer authorization.

### Execution

The act of carrying out an authorized decision. Execution should remain within the authorized scope and preserve a record of what changed.

### Verification

Evidence that an executed action met stated technical criteria or produced its intended effect. Verification does not redefine the criteria and does not itself constitute acceptance.

### Acceptance

The judgment by an authorized owner or mechanism that the verified outcome is sufficient. An implementer cannot silently accept their own work unless that authority was explicitly delegated.

## Repository domain terms

These terms name artifacts and review stages specific to this repository. The
DDD discovery entrypoint at
[`docs/domain/UBIQUITOUS_LANGUAGE.md`](docs/domain/UBIQUITOUS_LANGUAGE.md)
points here rather than maintaining a second glossary.

### Pincite release

A **Pincite release** is the exact external corpus, doctrine, schemas,
retrieval index, and executable identified by `pincite-dependency.json`.
CAPLAB may consume it only after the dependency gate verifies its tag, commit,
corpus ID, and doctrine ID.

### Pincite source, corpus, and concept record

**Pincite source**, **corpus**, and **concept record** refer to artifacts owned
and defined by the pinned Pincite release. CAPLAB preserves their identifiers
and locators as provenance; it does not become their authority by evaluating
them.

### Formulation

A **formulation** preserves a source-attributed contribution and its exact
locator in the doctrine graph. Several formulations may support, refine, or
contest one concept record without being collapsed into one source claim.

### Evidence obligation

An **evidence obligation** names information required before a doctrine-backed
claim or recommendation can be made at its proposed scope. A routing signal
may reveal an obligation but cannot satisfy it.

### Evidence packet

An **evidence packet** is a content-addressed Pincite selection of doctrine,
conflicts, procedures, provenance, supplied evidence, and remaining evidence
obligations for one question. It is retrieved guidance, not a CAPLAB finding,
decision, or authorization.

### Decision receipt

A **decision receipt** is a typed record of evidence and assertion lineage for
one decision question. It may supply an ADR, specification, plan, review, or
handoff. It does not become a decision merely because it is structurally valid.

### Screening

**Screening** is a machine judgment used to prioritize later review. A
screening verdict is an observation of model output, not verification of the
screened claim and not a human judgment.

### Pre-review

A **pre-review** is an advisory model-authored inspection of a screening flag
or pending evaluation candidate. It may record observations, an inference, and
a recommended disposition or repair. It is not a human audit, human
disposition, decision, verification, or acceptance, and it must not be copied
into a human-owned record without an actual human judgment.

**Frontier second opinion**, **frontier pre-pass**, and **gold pre-pass** are
pre-review variants. Their narrower names may remain in schemas and historical
records, but prose should identify them as pre-review when the distinction from
human adjudication matters.

### Human audit

A **human audit** is a human-authored finding about a screening record or
citation after the named reviewer inspects its evidence. It does not modify
doctrine by itself.

### Human disposition

A **human disposition** is a human-authored resolution of a calibration
candidate. It records the verdict, evidence reviewed, rationale, and residual
uncertainty. Machine output may inform it but cannot populate it under a human
identity.

### Adjudication bench

The **adjudication bench** is the interface that presents screening,
pre-review, source evidence, human audits, and human dispositions without
collapsing those records into one authority level.

### Study

A **study** is a versioned CAPLAB measurement design binding a question,
subject identity, task world, conditions, instruments, outcomes, analysis
population, and promotion gates. Adjacent experiments are not silently pooled
into one study.

### Capability card

A **capability card** is a bounded reviewer-facing interpretation of one
selected study. It preserves observations, uncertainty, rivals, exclusions,
and claim scope. It is not a global model ranking or an authorization for
deployment, placement, export, or training.

### Bounded context

A **bounded context** is a deliberately selected boundary within which a model
and its language have a consistent meaning and an identified owner. A
directory, service, database, process, or team is evidence to inspect, not
proof of a bounded context.

### Context map

A **context map** records bounded contexts and the semantic and integration
relationships between them. Candidate boundaries stay labeled as candidates
until a decision owner selects them through an ADR.

### Domain event

A **domain event** is a past-tense fact that matters to a named domain model
inside a bounded context. A log line, queue message, webhook, or state change
is not a domain event solely because it happened.

### Product specification

A **product specification** describes a proposed or selected observable
capability and its contract. Its lifecycle state does not silently authorize
implementation.

### Implementation plan

An **implementation plan** orders proposed or authorized execution checkpoints
and preservation boundaries. Readiness is not authorization, and execution is
not verification or acceptance.

### Architecture decision record

An **architecture decision record** (**ADR**) preserves one architectural
selection, its owner and authority, evidence, alternatives, rationale,
consequences, and reopening conditions. In this repository an ADR with status
`decided` records selection; it does not imply implementation authorization,
verification, or acceptance.

## Assertion flow

The usual progression is:

```text
evidence -> observation -> inference or diagnosis -> recommendation
         -> proposal -> selection and decision -> authorization
         -> execution -> verification -> acceptance
```

Not every activity requires every stage, and stages may be revisited when new evidence appears. Skipping a stage must not change the meaning of the remaining terms.

## Prohibited promotions

Do not treat:

- access or technical capability as authorization;
- an observation as a diagnosis;
- correlation, a smell, or a repeated claim as a proven inference;
- an inference as the only possible explanation without testing rivals;
- a recommendation or proposal as a decision;
- a decision as authorization unless the owner explicitly exercises that authority;
- execution as evidence that the intended effect occurred;
- passing technical checks as acceptance;
- acceptance as proof that no residual or future risk exists.

## Illustrative example

The following statements describe one situation at different assertion levels. They are illustrative, not claims about the current repository state.

> **Observation:** The repository check exits with a nonzero status and identifies a stale corpus index. **Evidence:** the recorded command, exit status, and diagnostic output.
>
> **Inference:** The index may not have been regenerated after a source change. A manual edit or an incorrect source hash is a rival explanation.
>
> **Recommendation:** Compare source hashes and inspect for manual edits before regenerating the affected index. Prefer no regeneration if the existing output contains unexpected edits.
>
> **Decision:** The repository owner selects regeneration only for outputs whose source changed and whose integrity check finds no manual edits. The owner records the authorized scope separately.
>
> **Verification:** A second run produces no meaningful diff and the repository check passes.
>
> **Acceptance:** The designated owner judges the verified corpus sufficient for downstream use.

## Decision-record fields

A decision record should preserve enough context to reconstruct the progression without conflating its stages:

- question and scope;
- observations and evidence locators;
- inferences, rivals, and uncertainty;
- recommendation, alternatives, and tradeoffs;
- decision, owner, and authority source;
- authorization and execution scope;
- verification criteria and results;
- acceptance authority, outcome, and residual risk.

When a compact machine-readable label is needed, use the lowercase singular terms defined here: `observation`, `inference`, `recommendation`, `decision`, `authorization`, `execution`, `verification`, and `acceptance`.
