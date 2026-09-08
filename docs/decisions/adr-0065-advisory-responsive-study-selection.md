---
id: adr-0065
artifact_type: architecture-decision-record
title: Advisory-responsive approach selection study
status: decided
execution_authorized: false
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-09-08
decided_at: 2026-09-08
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans:
  - Plane CAPLAB-44
---

# Advisory-responsive approach selection study

## Decision

Under [CAPLAB ADR 0026](adr-0026-caplab-blanket-decision-authority.md), select
`advisory-selection-001` as a foundational study of whether **real Pincite
retrieval changes observable agent conduct on purpose-built synthetic tasks**.
Follow the owner's later CAPLAB-44 redraw: the primary comparison is real
retrieval versus no packet, with a sham-packet condition to examine effects
of receiving context. The intervention includes the frozen query procedure,
nomination, budget and assembly pipeline. Forced target-concept injection
does not represent that pipeline's performance.

Select the construct and requirements in version 0.1.0 of the
[advisory-responsive approach selection card](../product/capability-cards/caplab-advisory-selection-001-advisory-responsive-approach-selection.md).
This decision selects a question and claim boundary; it does not accept a
complete executable design or frozen preregistration. The reserved path
`docs/product/studies/caplab-advisory-selection-001-preregistration.md` remains
unwritten pending CAPLAB-74's population, instrument, parameters and feasibility.

CAPLAB-57's named use is to decide whether a behavioral effect warrants a
subsequent quality study. Change is not itself better judgment. This study
cannot justify reviewer ordering, deployment, or a Pincite routing investment
without the separate evidence those claims need.

This selection is distinct from the August advisory binding campaign in
[`adr-0064-advisory-selection-campaign.md`](adr-0064-advisory-selection-campaign.md),
which concerns `review.defect_discrimination/1`. Similar filenames do not
identify the same construct or transfer execution authority.

## Alternatives and evidence matrix

| Option | Question it can address | Disposition and evidence |
|---|---|---|
| Real retrieval / context sham / no packet on authored worlds | Whether the actual retrieval pipeline changes conduct | Selected by the later owner redraw in CAPLAB-44; query inputs and valid context controls still need freezing |
| Forced concept substitution into an actual-served baseline | Incremental effect conditional on engineered content exposure | Earlier design; cannot replace retrieval versus none. A separately justified diagnostic arm may study it |
| Historical ranking-miss defect commits | Conditional effects on that constrained, label-dependent population | Superseded as destination substrate by the synthetic redraw; no historical rows admitted here |
| Retrieval recall alone | Whether a nominated target was served | Useful diagnostic; cannot establish behavioral response or quality |
| Immediate quality/ranking study | Whether advice or a reviewer improves real work | Requires independent correctness outcomes and a different claim/analysis contract |
| Defer selection | Avoid a premature executable commitment | Unnecessary: select the owner question while leaving instrument and execution unauthorized |

The [CAPLAB-72 receipt](../records/decision-2026-09-08-caplab-72-selection.md)
retains the current map snapshot and CAPLAB-57 owner comment as planning
provenance. Those records are not admitted experimental observations.

## Construct and claim boundary

**Advisory-responsive approach selection** means incorporating guidance that
bears on the task, resisting distortion by guidance that does not bear, and
preserving work quality. Anti-suggestibility is constitutive: uptake of both
fitting and misfit advice cannot establish this capability. The term is added
to [CAPLAB's ubiquitous language](../domain/ubiquitous-language.md).

A positive behavioral response alone leaves selectivity and non-degradation
unestablished. A null estimate with wide uncertainty does not establish absence
of an effect or inert doctrine. A frozen meaningful-effect and uncertainty rule
must govern any decision to stop pursuing quality.

Preregistration must reconcile these comparison roles:

- **Real retrieval versus none:** estimate the effect of assignment to the
  specified retrieval procedure on frozen behavioral observables. Record target
  recall alongside behavior. Do not restrict the primary denominator to episodes
  where retrieval succeeded: that selects on an observed consequence of the
  intervention. Missing targets inform exposure diagnosis, not a unique causal
  attribution of a null result to routing.
- **Context sham:** freeze its source, dose, presentation and purpose. A packet
  borrowed from another world is not automatically inert or non-bearing here.
  Matching packet length alone does not establish a valid context control.
- **Adjacent non-bearing advice:** a full anti-suggestibility claim needs the
  card's validated comparison, feasible placebo conduct and semantic pairing
  judgment. A context sham cannot substitute without meeting those requirements.
  Any additional condition needs a frozen purpose and denominator.
- **Forced injection, if retained:** its treatment packet is a
  **CAPLAB-constructed stimulus, not a Pincite output**. Retain the original
  retrieval packet and exact construction lineage. Do not describe its effect
  as real-retrieval performance or inherit the old injection primary contrast.

Illustrative distinction: no-packet conduct 0.20, real-retrieval conduct 0.20,
and forced-injection conduct 0.80 give a retrieval effect of 0.00 and a forced
exposure effect versus none of 0.60. Calling the latter a retrieval benefit
would answer the wrong question. These are synthetic values, not study results.

An unchanged packet produced by the pinned real retrieval procedure remains a
Pincite output. CAPLAB owns assignment, stimulus construction, measurement and
claims; Pincite owns its corpus and retrieval policy. Neither a study finding
nor a shared ADR ordinal transfers decisions between products.

Use exact native agent-system Bindings under
[ADR 0039](adr-0039-native-agent-system-subject-identity.md), distinguishing
assignment, administration and observed identity. CAPLAB-63 must select the
single native harness after its capture prerequisites pass. This decision
selects no model, version, account, proxy exception or sampling default.
Repeated trials do not establish cross-harness or cross-population generality.

## Evidence classes, permitted use and custody effects

The [restricted admission contract](../product/contracts/advisory-study-admission-v1.md)
governs the future dossier. This selection authorizes **no evidence copy or
registration**, and designates no existing directory as admitted custody.
A later authorization must bind exact source commit/path/hash/length, assertion
class, permitted use, exposure, destination custody domain, independent copy,
verification, recovery and expiry. A glob or latest artifact cannot fill a
missing identity.

| Class/material | Prospective permitted use | Effect of this decision |
|---|---|---|
| Deterministic retrieval output | Observed output of a pinned procedure; target labels remain separate inferences | No replay or admission |
| Historical judgments or defect commits | Judgments may nominate candidates; source bytes alone do not establish truth | No import, registration, relabeling or purge; real-commit branch not selected |
| Authored task/world/reference/oracle | Constructed artifacts with derivation and separate validity witnesses | No construction, existing-scenario admission or seal |
| Code, pairing or accuracy judgments | Named inference/decision class with author, exposure and delegation | No owner judgment or human-time commitment |
| Native captures and derived scores | Capture observations and separately reproducible derivations | No call, capture processing, scoring or qualification |
| Selection/governance records | Decision/authorization provenance within their scope | This ADR and its glossary/index links are recorded; no experimental evidence created |

Future admission must preserve successful and failed candidate provenance under
its authorized retention rules. Existing shakedown/ladder artifacts do not
become study evidence through selection. New episode IDs cannot make a
previously observed world unobserved.

## Authority and next boundary

**Zero model calls and zero spend. Execution is not authorized.** This decision
does not reopen a campaign, admit evidence, freeze a study, accept a result,
or change ranking/placement. The
[confirmed review-instrument disposition](../records/report-2026-09-07-review-instrument-disposition.md)
continues to govern review spend and claims.

Authority comes from CAPLAB's ADR 0026, the blanket primary-agent delegation.
Pincite's distinct `docs/decisions/adr-0026-rubric-provisional-admission.md`
governs provisional concept admission in Pincite. It supplies no CAPLAB
decision authority or evidence-admission permission.

CAPLAB-74 still needs an exact population and native Binding; valid code/oracle
and pairing witnesses; coder roster and independent accuracy anchor; complete
capture and blinding validation; arm/query mapping, randomization, missingness
and usable-sample accounting; protected freeze/custody records; and justified
parameters, costs and feasibility. Use the selected
[code-authoring](../product/contracts/behavior-code-authoring-v1.md),
[pairing](../product/contracts/adjacent-placebo-selection-v1.md),
[coverage](../product/contracts/shakedown-coverage-v1.md), and
[sample-accounting](../product/contracts/usable-sample-budget-v1.md) contracts.
Missing requirements mean not ready. `Infeasible-as-designed` needs a
demonstrated constraint conflict, not merely an unfinished table.

Instrument construction requires a separate bounded authorization; live
execution requires a later exact authorization after its gates pass. This
selection does not bypass Principal-owned human-time or pairing judgments.
Agreement does not substitute for accuracy, nor code conformance for work
quality. CAPLAB-44 remains incomplete after this ADR is written.

Reopen if the owner changes the question, retrieval and forced exposure cannot
be kept distinct, valid controls cannot support the intended claims, or
feasibility requires a materially different population or primary comparison.
Record the change before adopting a new instrument; preserve old results.

## Doctrine receipt

Evidence-backed packet `pkt-50604e2d058a5f6e`, content SHA-256
`50604e2d058a5f6ea9163158a62a52ea3b32302fccfffc8520139a8fcadd81a4`,
was retrieved from validated release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`: corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`. Applied repository precedence,
evidence before intervention, explicit invariants and bounded authority. The
[decision receipt](../records/decision-2026-09-08-caplab-72-selection.md)
retains the complete obligation disposition and citation verification.

Pincite guidance informs this design decision, creating an **epistemic**
dependence that is disclosed. At this selection boundary it enters no subject,
coder, oracle or score computation: no measurement execution is authorized.
It is not an observed arm-varying measurement exposure. This does not prove
that a future instrument is free of such exposure or design bias. Actual
input/context inventories and arm-invariance arguments need verification before
launch; do not suppress the receipt to make independence appear stronger.

## Status history

- `2026-09-08` — `decided` — ADR 0026 delegate selected the owner's later
  real-retrieval question and canonical construct; executable design,
  preregistration, admission and execution remain unapproved.
