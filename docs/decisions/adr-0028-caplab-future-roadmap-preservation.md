---
id: adr-0028
artifact_type: architecture-decision-record
title: Preserve the CAPLAB roadmap beyond v0
status: decided
decision_owner: repository-owner
decision_authority: repository-owner correction
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
---

# Preserve the CAPLAB roadmap beyond v0

## Owner correction

The repository owner corrected the interpretation of the v0 boundary:

> v0 was narrowed, that doesn't mean to cancel future work.

## Decision

The CAPLAB v0 boundary limits the current acceptance slice. It does not remove
later preference, Striatum, second-study, dataset, tuning, evaluation, or
scheduler-decision work from the CAPLAB roadmap.

CAPLAB-6 through CAPLAB-17 are restored to Plane Backlog. Their earlier
cancellation incorrectly treated deferral from v0 as cancellation of the
future roadmap.

## Existing cancellations that remain valid

This decision does not reopen:

- CAPLAB-2 through CAPLAB-5, whose broad pre-selection forms were replaced by
  the exact v0 Study 001 registration, subject, capability-card, and profile
  work;
- CAPLAB-30/P12, which remains unavailable under ADR 0024 because no example
  is training eligible and no export is authorized; or
- CAPLAB-31 and CAPLAB-32, whose incorrect dependency relations were replaced
  by CAPLAB-33 and CAPLAB-34.

## Authority and sequencing

Restoring a work item to Backlog is planning correction, not execution
authorization. Each item still follows its recorded dependencies. Material
effects require a separate durable authorization under ADR 0026, with the
exact scope, preservation boundary, verification, cleanup, and stop
conditions recorded before execution.

The completed P0-P14 v0 campaign remains closed with the ADR 0027 revision
disposition. Future roadmap work may produce later evidence or decisions, but
it cannot rewrite that campaign's observations, verification, or disposition.

## Status history

- `2026-07-20` — `decided` — the repository owner clarified that narrowing v0
  did not cancel future CAPLAB work; CAPLAB-6 through CAPLAB-17 were restored
  to Backlog.
