---
id: spec-capability
artifact_type: product-spec
title: Capability title
status: draft
owner: repository-maintainers
created: YYYY-MM-DD
updated: YYYY-MM-DD
supersedes: []
superseded_by: null
decision_owner: null
decision_authority: null
decision_record: null
related_plans: []
---

# Capability title

Status interpretation: this document is a draft proposal. It does not record a
decision or authorize implementation.

## Decision question and scope

State the question this specification asks an identified owner to resolve and
the repository/product surface in scope.

## Observations and evidence

Record inspectable current-state facts with paths, revisions, commands, or
other evidence. Keep observations distinct from explanations.

## Inferences, assumptions, rivals, and uncertainty

Explain what the observations may mean, credible alternatives, and evidence
that could change the conclusion.

## Recommendation and alternatives

Describe the proposed capability, meaningful alternatives including no change,
costs, risks, reversibility, and the conditions favoring each option.

## Product contract

Define users, use cases, inputs, outputs, observable behavior, refusal behavior,
and the boundary between this product and adjacent systems.

## Architecture and artifact contracts

Describe components, data flow, stable identities, provenance, versioning, and
repository layout. Prefer existing contracts over parallel models.

## Constraints, invariants, and preservation boundaries

Name properties that implementation must preserve, including authority,
privacy, compatibility, deterministic behavior, and human-owned records.

## Failure modes and operational response

Describe invalid inputs, safe failure, diagnostics, recovery, and escalation.

## Verification and acceptance criteria

State what can be checked deterministically, what requires human adjudication,
and who can accept the result. Avoid uncalibrated numeric thresholds.

## Rollout, reversal, and reopening

Describe the smallest viable slice, rollback or disable path, and evidence that
would reopen the design.

## Security, privacy, and retention

State what repository or model data may be captured, where it may be retained,
and what must be redacted or kept outside version control.

## Unresolved questions

List decisions or evidence gaps that block selection or implementation.

## Decision and authorization record

Record a decision only after the named owner selects an option. Record
implementation authorization separately; do not infer either from document
status. Link `decision_record` to a repository
[ADR](../../decisions/README.md) when the selection is architectural.
