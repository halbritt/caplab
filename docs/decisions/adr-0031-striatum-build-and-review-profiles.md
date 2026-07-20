---
id: adr-0031
artifact_type: architecture-decision-record
title: Striatum build and fresh-review capability profiles
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - striatum-placement
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Striatum build and fresh-review capability profiles

## Context

CAPLAB-9 asks for two contrasting Striatum pass profiles. Current Striatum does
not define a product-level “pass family.” Its active contracts define workflow
jobs, including stored `build` and `review` job types, plus lane, principal,
gate, driver, scheduler, and backend boundaries.

CAPLAB therefore treats “pass profile” as a CAPLAB evidence profile for one
current Striatum job context. It does not add a Striatum job type or alter a
Striatum gate.

## Decision

The ADR 0026 delegate accepts these profiles:

1. [`striatum-build-v1`](../product/striatum-pass-profiles/striatum-build-v1.md)
   for an agent executing an authorized `build` job; and
2. [`striatum-fresh-review-v1`](../product/striatum-pass-profiles/striatum-fresh-review-v1.md)
   for an independent agent executing a `review` job with fresh context.

They are selected because the contexts assign opposite value to several
identical behaviors. Editing in-scope source is necessary in a build job and
disqualifying in a review-only job. Retaining author context can help a build
and invalidates a fresh review. A justified refusal can be a useful review
finding while an unwarranted refusal leaves an authorized build incomplete.

The profiles constrain later CAPLAB evidence gathering and lane-fit
recommendations. Striatum retains authority over workflows, placement,
scheduling, capabilities, gates, and runtime acceptance.

## Current source custody

The profiles were derived from the clean Striatum repository at
`87ed89099477da7ba39252fe77c541e90928a8ef` and these content identities:

| Source | Git blob | Use |
|---|---|---|
| `docs/reference/spec.md` | `94b446a18d6cb94292543ba384ae48353b4e572a` | workflow, review, authority, adapter, and completion contracts |
| `docs/reference/ubiquitous-language.md` | `96bc763f407117f9374ec4b769d0888d0726e6ad` | principal, lane, gate, driver, scheduler, backend, and provenance vocabulary |
| `go/pkg/workflowauthoring/workflow.go` | `0f3289f02ea8fce2c02978ee91e8489ca65efedf` | current build/review validation paths |
| `go/pkg/mutations/run.go` | `feb5eae410a65ec1ef278acb0c821f1db037a716` | job-type projection and run preparation |
| `go/pkg/mutations/review.go` | `d77daec1a7481fd3c81c4ad3b272f414ffebc55e` | review verdict mutation boundary |

These are downstream requirement locators, not copied Striatum authority.
CAPLAB does not modify or vendor them.

## Evidence and alternatives

The no-change alternative leaves CAPLAB-10 without frozen lane-fit inputs. A
single generic profile collapses behaviors that have opposite value in build
and fresh-review contexts. More than two profiles adds breadth before the first
two have evidence. The selected pair is the smallest contrast that preserves
current Striatum semantics.

Pincite packet `pkt-9165b553e244b739` supplied advisory guidance. Its captured
SHA-256 is
`0ff7d9f9a857609ca0ff9180f9d80cc561e9a398da5c10aa02c69c7cbae06140`.
The packet's task-authority, accepted-contract, current-runtime, and bounded-
decision obligations were supplied. History-mining and architecture-boundary
obligations were nonmaterial because this decision changes no Striatum source,
runtime, ownership, or architecture. The exact source and preservation
locators above discharge the applicable contract and reversal concerns.

## Acceptance and reopening

The primary agent accepts both profile contracts under ADR 0026. This is
profile acceptance, not model selection, Striatum placement, profile
verification, or acceptance by a Striatum policy owner.

Reopen either profile when its source commit changes a cited contract, measured
cost or latency makes a bound unrealistic, Striatum replaces either job type,
or a lane-fit campaign exposes behavior whose value the profile cannot classify.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate accepted the build and
  fresh-review profiles as CAPLAB evidence contracts.
