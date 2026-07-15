# Product specifications and implementation plans

This directory is the repository-native home for proposals that turn the
corpus and doctrine into products, research instruments, or runtime
capabilities. These documents are repository-specific. They are not
source-derived doctrine and must not be cited as corpus evidence.

Product documents follow the assertion and authority meanings in
[`ubiquitous_language.md`](../../ubiquitous_language.md):

- a polished specification is still a proposal until a decision owner selects
  it;
- a selected specification does not authorize implementation;
- a ready implementation plan does not authorize execution;
- execution, verification, and acceptance remain separately recorded states.

Architectural selections live in the repository's
[`docs/decisions/`](../decisions/README.md) index. A product document may link
an ADR; it does not become one.

## Layout

```text
docs/product/
  README.md
  capability-cards/
    README.md
  templates/
    product-spec.md
    implementation-plan.md
  specs/
  plans/
```

Use a product specification when a capability introduces a new user-visible or
agent-visible contract, several components, a new evaluation claim, or a
material governance boundary. Use an implementation plan when delivery requires
several dependency-ordered checkpoints or explicit preservation and stop
conditions. Small, local documentation changes do not require either artifact.

## Stable identity

Canonical filenames equal the document ID plus `.md`. IDs are descriptive and
do not contain dates, model names, or lifecycle states:

- `spec-<capability>`
- `plan-<capability>-<campaign>`

Dates and authorship belong in metadata. Keep superseded documents at their
canonical path and link their replacement instead of moving or rewriting
history.

## Lifecycle

Specification states:

- `draft`: incomplete and not ready for selection;
- `proposed`: reviewable proposal, not selected and not authorized;
- `decided`: selected by an identified decision owner with an authority source
  and durable decision record; implementation is still not authorized;
- `superseded`: replaced by a reciprocally linked specification;
- `withdrawn`: no longer proposed or governing, with a recorded reason.

Implementation-plan states:

- `draft`: incomplete;
- `proposed`: complete enough for review, but its source design may still be
  undecided;
- `ready`: execution-ready after the source design is selected, explicitly not
  authorization;
- `authorized`: a named owner has granted a bounded execution scope through a
  durable authorization record;
- `executed`: the authorized change has been carried out and linked; this does
  not claim verification or acceptance;
- `superseded`: replaced by a reciprocally linked plan;
- `withdrawn`: no longer proposed or active, with a recorded reason.

Blockers, verification results, and acceptance do not become overloaded plan
states. Record them in the plan's status log and dedicated records.

## Index

| ID | Type | Title | Status | Steward | Source or parent | Updated |
|---|---|---|---|---|---|---|
| [`caplab-study-001-explicit-verification-elicited-harm-avoidance`](capability-cards/caplab-study-001-explicit-verification-elicited-harm-avoidance.md) | capability card | Study 001: explicit-verification-elicited harm avoidance | selected by ADR 0006 | repository maintainers | ADRs 0004 and 0006 | 2026-07-15 |
| [`spec-agent-capability-lab`](specs/spec-agent-capability-lab.md) | product specification | Agent Capability Lab v0 charter | decided | repository maintainers | ADR 0002 | 2026-07-15 |
| [`plan-agent-capability-lab-v0`](plans/plan-agent-capability-lab-v0.md) | implementation plan | Agent Capability Lab v0 | proposed | repository maintainers | `spec-agent-capability-lab`; ADR 0002 | 2026-07-15 |
| [`spec-doctrine-robustness-laboratory`](specs/spec-doctrine-robustness-laboratory.md) | product specification | Doctrine Robustness Laboratory | decided | repository maintainers | corpus operationalization gap | 2026-07-12 |
| [`plan-doctrine-robustness-laboratory-pilot`](plans/plan-doctrine-robustness-laboratory-pilot.md) | implementation plan | Doctrine Robustness Laboratory pilot | authorized | repository maintainers | `spec-doctrine-robustness-laboratory` | 2026-07-12 |

## Maintenance rules

- Every plan links its source specification and, once one exists, its governing
  ADR. Without that decision, the plan remains unselected and
  unauthorized.
- A specification lists its active plans.
- Supersession links are reciprocal.
- Evidence uses exact repository paths, revisions, commands, incidents, or
  receipts. Doctrine links may explain a recommendation but cannot select it.
- `owner` means document stewardship. It is not a substitute for decision,
  authorization, verification, or acceptance ownership.
- Generated indexes may summarize metadata, but tools must not rewrite
  substantive prose.

Start new artifacts from the files under [`templates/`](templates/). Start an
architectural selection from the
[`ADR template`](../decisions/adr-template.md).
