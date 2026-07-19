---
id: plan-capability-campaign
artifact_type: implementation-plan
title: Capability campaign
status: draft
owner: repository-maintainers
created: YYYY-MM-DD
updated: YYYY-MM-DD
supersedes: []
superseded_by: null
source_artifacts: []
source_decision: null
baseline: null
authorization_record: null
authorized_scope: []
change_types: []
---

# Capability campaign

Status interpretation: this document is a draft implementation proposal. It
does not select the source specification or authorize execution.

## Objective and authority boundary

Name the outcome, source decision, decision owner, authorization status, and
the highest action level currently granted. When `source_decision` is
architectural, link the governing repository
[ADR](../../decisions/README.md).

## Current-state evidence and assumptions

Anchor the plan to a revision, dirty paths, relevant contracts, verification
baseline, and assumptions that must be rechecked before execution.

## Scope, non-goals, and change classification

List allowed, adjacent read-only, and forbidden paths. Classify feature,
repair, refactoring, architecture, migration, optimization, cleanup, generated,
and documentation work separately.

## Preservation boundaries

Inventory behavior, data, interfaces, provenance, authority, privacy, and
human-owned artifacts that each checkpoint must preserve.

## Dependency map

Show checkpoint order and work that can proceed independently.

## Checkpoints

| ID | Purpose | Depends on | Write scope | Output | Verification | Rollback |
|---|---|---|---|---|---|---|
| P0 |  |  |  |  |  |  |

For every checkpoint, state preconditions, exact work, evidence, acceptance
criteria, stop conditions, and the next safe action.

## Verification plan

Separate deterministic structural checks, hermetic tests, optional external
witnesses, human adjudication, and final acceptance.

## Risks and mitigations

Record the causal failure mode, early signal, mitigation, residual risk, and
owner rather than a generic severity list.

## Stop, escalation, and rollback conditions

Define when to stop, who owns the blocked decision, the last known-good state,
and what can be retained safely.

## Deferred work

List adjacent work that is deliberately excluded and the evidence that would
earn a later campaign.

## Execution, verification, and acceptance records

Link resulting changes and execution records only after work occurs. Link
verification and acceptance separately.

## Status log

Append dated entries without rewriting earlier state.
