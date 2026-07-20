---
id: adr-0032
artifact_type: architecture-decision-record
title: Initial synthetic evaluation baseline and gate policy
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Initial synthetic evaluation baseline and gate policy

## Context

CAPLAB-42 requires a deterministic snapshot gate whose baseline cannot change
automatically. ADR 0029 authorizes model-free implementation and fresh
synthetic fixtures but excludes historical BOOKS baselines and results.

The available choices were to leave the gate without an approved baseline, to
copy the historical BOOKS baseline, or to select a new baseline derived only
from CAPLAB's fresh synthetic replay. No baseline would leave regression
behavior unexercised. Copying the historical baseline would cross the custody
boundary in ADR 0029.

## Decision

Select
[`synthetic-replay-baseline-v1.json`](../product/evaluation/synthetic-replay-baseline-v1.json)
as the initial CAPLAB evaluation baseline. Its canonical SHA-256 is
`de0ffb12951579e7d2a9a012c303a32f5eefdfab40599c879c2ab6873b073fb9`.
It contains one scenario derived from the fresh synthetic CAPLAB-41 fixture,
not a historical result.

Select
[`synthetic-replay-policy-v1.json`](../product/evaluation/synthetic-replay-policy-v1.json)
as its policy. The policy binds that exact baseline, requires one
`authority-preservation` scenario, sets both exact score floors to `1/1`, and
allows no drop from the baseline. With one safety-contract scenario, any
failure must stop the gate.

The baseline and policy are product decisions, not registered model evidence,
verification, or CAPLAB acceptance. The evaluation package exposes no writer
or automatic update command for either artifact.

## Reopening conditions

Reopen this decision before changing the baseline bytes, policy identity,
required coverage, score floors, or tolerated regression. A future expansion
must use fresh or separately admitted CAPLAB evidence and preserve the old
artifact's custody; it must not overwrite this version.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate selected the smallest fresh
  synthetic baseline that exercises the CAPLAB-42 gate without admitting
  historical evidence.
