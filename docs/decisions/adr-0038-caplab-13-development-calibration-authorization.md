---
id: adr-0038
artifact_type: architecture-decision-record
title: CAPLAB-13 development calibration authorization
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
expires_at: 2026-08-03T23:59:59Z
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-review-dissent-001
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-13 development calibration authorization

## Context

ADR 0034 selects `caplab-review-dissent-001`, and ADR 0036 authorizes and
qualifies its model-free instrument. CAPLAB-13 requires an exact live boundary
before a provider request. ADR 0026 delegates the required product, execution,
and bounded-budget decisions to the primary agent without another owner
interaction.

The clean authorization baseline is commit
`c794b0a36e8c7f0b5c0bc28a55d2b1c5df38c01c`. The public provider catalog was
observed at `2026-07-20T17:40:07Z`.

## Decision and authorization

Authorize one development-only calibration campaign through
`2026-08-03T23:59:59Z` with these exact subject tuples:

| Subject | Provider route | Prompt USD/token | Completion USD/token |
|---|---|---:|---:|
| `fable` | `openrouter/anthropic/claude-fable-5` | `0.00001` | `0.00005` |
| `gpt` | `openrouter/openai/gpt-5.6-terra` | `0.0000025` | `0.000015` |

Both use Harbor `0.18.0`, Terminus `2.0.0` source SHA-256
`c6b72b8c6289809b2ff3a3009b8f118fa1edb1da205f48d0b56c6938a49cb12f`,
the JSON parser, provider-default reasoning with no literal override, eight
turns, at most 1,024 completion tokens per turn and 8,192 per trial, no
summarization, fresh memory, task-local tools, a 45-minute task limit, a
no-network task container, one sequential trial, no harness retry, disabled
harness verification, and `/app` as the only captured artifact.

The 16 primary slots are frozen in this order:

1. `r03:gpt`
2. `r04:fable`
3. `r07:fable`
4. `r08:gpt`
5. `r02:gpt`
6. `r01:fable`
7. `r06:fable`
8. `r05:gpt`
9. `r04:gpt`
10. `r03:fable`
11. `r08:fable`
12. `r07:gpt`
13. `r01:gpt`
14. `r02:fable`
15. `r05:fable`
16. `r06:gpt`

Each subject therefore receives every development cell exactly once. The
campaign may use at most four same-slot replacements, only after a preserved
provider, harness, capture, task-image, or verifier infrastructure failure.
A subject refusal, invalid review, partial review, or wrong review consumes
its primary slot and is never replaced.

The ceilings are 20 total trials, 163,840 completion tokens, 12 elapsed hours,
and USD 25.00. Stop before a call that would meet or exceed the dollar ceiling.
The raw custody root is
`/home/halbritt/.local/share/caplab/campaigns/caplab-review-dissent-001-development-2026-07-20`.

Permitted effects are the 16 development primary calls and bounded
infrastructure replacements; exact public catalog and credential-presence
preflights; deterministic rendering; raw append-only custody; trace-owned read
observations; review capture and mechanical grading; blinded qualitative
packets; delegated qualitative dispositions that name ADR 0026; scoped
calibration analysis; CAPLAB-owned source, tests, decisions, product records,
and campaign artifacts; repository checks, commits, and pushes; and Plane
projection updates for CAPLAB-13.

## Excluded effects

Do not open, render, inspect, execute, or otherwise consume `heldout.json` or a
held-out oracle. The live path must load development content and only the
held-out aggregate seal already present in `instrument.json`.

This authorization permits no historical evidence admission or rewrite, no
production evidence promotion, no dataset export, no training, no Striatum
policy change, no lane-fit decision, and no independent verification or
acceptance. It does not authorize changing either subject identity, the task
population, the factorial factors, the frozen order, or the equal surface.
Provider credit purchase, payment-method use, account billing changes, and
credential mutation are outside this campaign even though trial spend within
the funded balance is authorized.

## Preservation and stop conditions

Every launch, completion, provider result, trajectory, artifact tree,
observation, normalized capture, mechanical result, blinded packet,
qualitative disposition, and analysis must be content identified. Preserve
post-interaction failures and partial artifacts. Derive accounting only from
sealed raw custody, never from a caller-supplied ledger.

Stop before another call on:

- an unclassified prior attempt or a next-slot mismatch;
- a missing exact provider identity, price drift, harness drift, credential,
  Docker runtime, or funded provider balance;
- a held-out read or attempted held-out path access;
- task, oracle, instruction, manifest, order, surface, or custody drift;
- any target mutation, hidden-oracle access, differential capture, or
  treatment leak;
- a missing measured token or cost value other than a zero-token rejected
  provider request, which records zero cost;
- a second infrastructure failure for one slot;
- the fourth replacement already consumed; or
- any call, token, time, or dollar ceiling breach.

## Verification and result boundary

Before the first call, prove the exact manifest, development artifact,
held-out aggregate seal, frozen order, provider catalog entries and prices,
harness source, Docker runtime, task template, credential presence without
reading its value, sequential command, no-network container, and all ceilings.
Regression tests must prove the live loader never opens held-out content and
that replacement, custody, capture, preservation, grading, blinding, and
budget failures close safely.

The final result is calibration evidence only. Report all 16 primary slots,
all infrastructure attempts, mechanical bands by subject, truth, cue, and
world, and qualitative dispositions separately. Missing and invalid subject
outcomes remain in denominators. No result may claim general review skill,
production fitness, or acceptance.

## Doctrine receipt

The authorization used Pincite packet `pkt-eb754819440d5612`, packet-file
SHA-256 `05da913f8126021f318119b26d322711a277383f2f63ad9d4f292455cbfa399f`,
packet-content SHA-256
`eb754819440d5612ac79946615e1c70e312f1034a34736f1b64fce2d4e689ffd`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from the validated release home.

The packet is advisory. ADR 0026 and the repository contracts supply the
authority; the packet informed the explicit failure policy, append-only
custody, sequential simplicity, preservation boundary, and verification gate.

## Reopening conditions

Reopen before changing a subject tuple, provider route, task population,
factorial factor, order, surface, budget, replacement rule, custody root,
development-only boundary, claim ceiling, or qualitative authority.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized one exact,
  bounded, development-only CAPLAB-13 calibration campaign.
