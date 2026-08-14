# Ubiquitous language

These terms govern CAPLAB code, studies, records, dashboards, and planning.
Never silently promote one assertion type into another.

## Assertion types

**Observation** is a directly inspectable fact with an evidence locator,
method, and relevant version or time. It adds no causal explanation and grants
no authority.

**Inference** interprets observations. It names credible rivals, missing or
contradictory evidence, and uncertainty. Repetition does not turn an inference
into an observation.

**Recommendation** ranks a response against meaningful alternatives and their
tradeoffs. It advises; it does not select or authorize.

**Decision** records an option selected by a named owner or delegated mechanism
within a defined scope. It names the source of authority and reopening
conditions. It is not execution, verification, or acceptance.

**Authorization** is permission from the actual owner or an explicitly
delegated mechanism to perform named effects within a stated scope and time.
Access, capability, evidence, and selection do not create authorization.

**Execution** carries out an authorized decision and records the effects.

**Verification** supplies evidence that execution met frozen technical
criteria. It does not change those criteria or accept the outcome.

**Acceptance** is the authorized judgment that a verified outcome is
sufficient. Passing checks is not acceptance.

The ordinary progression is:

```text
evidence -> observation -> inference -> recommendation -> proposal
         -> selection and decision -> authorization -> execution
         -> verification -> acceptance
```

## CAPLAB terms

**Capability card** is a versioned measurement contract for one construct and
population. It names observables, controls, rivals, exclusions, scoring,
missingness, human judgments, and promotion gates.

**Binding** is the content-identified, behavior-bearing configuration of one
native agent system under measurement. It includes the exact model, serving
path, harness, effort, administration, tool and permission surfaces, sandbox,
and relevant runtime; a material change creates a different binding.

**Measurement** is an immutable observation about one binding and capability
under an exact experiment, protocol, corpus, and evidence basis. A measurement
contains no qualification decision.

**Qualification policy** is a versioned decision rule that interprets eligible
measurements for one bounded capability. Its thresholds, permitted evidence
bases, missingness rules, and decision authority remain separate from the
experiment that produced the measurements.

**Qualification claim** is an append-only recommendation or decision about one
exact binding and bounded capability under one qualification policy. It may
supersede prior claims in the same scope, but it is not runtime availability,
selection, verification, or acceptance.

**Revbench** is the CAPLAB experiment family that measures review behavior by
applying a mechanically verified defect to a known control and comparing the
binding's responses to the independently known truth.

**Downstream fate** is an observation about what happened after an artifact or
review entered another system. It is a covariate, not an independent evidence
basis for a qualification claim.

**Study** is one preregistered empirical question with a frozen population,
design, instrument, analysis, and missingness contract. A task family or pool
of adjacent experiments is not automatically one study.

**Model identity**, **agent configuration**, **administration**, and **trial
context** are separate identities. A treatment, prompt, tool, task, world,
instrument, or runtime change must not silently redefine the model.

**Native agent system** is the behavior-bearing evaluation subject for an
agentic model: model identity plus its native harness and harness version,
effort and configuration, instruction and knowledge surfaces, tools,
permissions, sandbox, and relevant runtime. The harness is part of the subject
under test. Running the same model route through a proxy or common adapter
creates a different agent configuration; it does not control away the native
harness. Comparative studies equalize task, authority, budgets, capture, and
scoring where meaningful while preserving and naming native-harness
differences. See ADR 0039.

**Trial assignment** is a sealed preregistered slot binding condition, block,
sequence, denominator, and replacement rules.

**Attempt** is one execution linked to a trial assignment, including its
interaction boundary, timestamps, failure class, disposition, and preserved
outputs.

**Registered evidence** is immutable content whose bytes, locator, custody,
and metadata have passed an authorized admission path. Availability or a hash
in a source repository is not CAPLAB registration.

**Capability profile** is a bounded presentation of accepted observations and
inferences under a capability card. It is not a global model ranking.

**Projection** is regenerable review or planning state. Dashboards and Plane
are projections; they cannot create evidence, decisions, authorization,
verification, or acceptance.

**Review dissent** is an evidence-backed non-clearing review verdict that
contradicts a favorable author cue because the frozen acceptance contract is
not met. It is not contrarianism: the same reviewer must accept clean controls
and must not invent blockers when the available evidence supports clearing.
