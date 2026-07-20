---
id: adr-0044
artifact_type: architecture-decision-record
title: CAPLAB-13 native development calibration authorization
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026-adr-0034-adr-0036-and-adr-0039
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

# CAPLAB-13 native development calibration authorization

## Context

ADR 0038 was withdrawn before its first call because it substituted
OpenRouter and Terminus for the behavior-bearing native harnesses. ADR 0039
requires native agent systems and explicitly preserved CAPLAB-13 as future
work. ADR 0026 delegates bounded CAPLAB product and execution decisions to the
primary agent without further owner interaction.

The corrected instrument retains the model-free-qualified development task
population, causal factors, oracles, blocked order, grading bands, held-out
seal, and claim ceiling from ADRs 0034 and 0036. It changes the treatment
identity and capture boundary to the native systems that Striatum declares:

| Subject | Native tuple | Harness | Model | Effort |
|---|---|---|---|---|
| `fable` | `claude-fable-5-max` | Claude Code `2.1.215` | `claude-fable-5` | maximum |
| `gpt` | `codex-terra-max` | Codex CLI `0.144.6` | `gpt-5.6-terra` | maximum |

The native instrument has semantic SHA-256
`7841f899c2dcf3f70453db0ee16d21388352f10dc769b3290c6f826709c76213`
and file SHA-256
`1e7747342ede592f5ddd6553233ea36c80282266251bf7e30feebb06edf6a242`.
The live manifest has semantic SHA-256
`b6d810ea4ee1ec55cb2f3d69646e18dc1fe34fd9d596cee940c162e367b10446`
and file SHA-256
`0499700c6f7db81ffb530fbe314e921844239bdb698141c34f637a6a9c29423b`.

## Decision and authorization

Authorize campaign
`caplab-review-dissent-001-development-native-r1-2026-07-20` through the
recorded expiry. It may execute the 16 development primary slots in the exact
preregistered order and at most four same-slot replacements. Replacement is
allowed only for a provider, harness, capture, task-image, or verifier
infrastructure failure. Refusal, invalid output, target mutation, partial
review, or wrong review is subject behavior, consumes its slot, and is never
replaced.

Each attempt must use a fresh native session inside the shared task-only
bubblewrap namespace. Only the selected harness, its authentication state, the
system toolchain, and the task tree are projected. The task tree is the only
writable study surface. Shared host networking exists only because each native
harness must reach its own provider endpoint. No repository, other home data,
historical evidence, hidden oracle, or held-out content is mounted.

The exact primary order remains:

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

The ceilings are 20 total trials, four replacements, 45 minutes per trial,
and 12 cumulative trial hours. Output is native-harness-managed and measured
when exposed. Both harnesses use existing authenticated subscription capacity;
no per-call price is observed, no credit purchase or payment change is
authorized, and capacity failure does not authorize proxy substitution.

## Permitted effects

The campaign may perform native authentication and version preflight without
inference, render development task images, make the bounded native subject
calls, capture native event streams and final task trees, derive conservative
read observations, mechanically grade reviews, create blind qualitative
packets, record primary-agent qualitative dispositions under ADR 0026, compute
development calibration aggregates, write CAPLAB-owned records and tests,
commit and push repository changes, and update CAPLAB-13 in Plane.

Raw append-only custody is
`/home/halbritt/.local/share/caplab/campaigns/caplab-review-dissent-001-development-native-r1-2026-07-20`.
Normalized repository artifacts are under
`docs/product/studies/review-dissent-001/campaign-development-native-r1-2026-07-20`.

## Excluded effects and stops

Do not open, render, inspect, or execute `heldout.json`; calibration receives
only its already recorded aggregate seal. Do not change the development
population, truth or cue factors, order, native tuple, effort, harness command,
capture rules, grading, or claim ceiling. Do not use OpenRouter, Harbor,
Terminus, a generic SDK, or another shared proxy.

Stop before another call on an unclassified prior attempt, order or digest
drift, held-out access, hidden-oracle exposure, task-treatment leakage,
containment drift, authentication or native-version mismatch, a second
infrastructure failure in one slot, replacement exhaustion, or a time/trial
ceiling. Target mutation remains a consumed subject outcome and prevents a
successful mechanical score; it does not justify altering the captured task.

## Verification and result boundary

Before the first call, model-free checks must prove native tuple validation,
development-only loading, exact order and ceilings, identical external
containment, infrastructure-only replacement, trace-owned read extraction,
target preservation, review validation, and sealed capture lineage. The
qualified source hashes are:

- native instrument and capture: `f67f6853ce43dea43b05c2fb07c504dfe0a2b9971e5f07f65ddf0e388d529ff1`;
- native live runner: `48bb5bf8ba282f186e29a35a65e1d6c39042d87d09a22e9322b0205cb8dbac4b`;
- shared frozen containment runtime: `1f0010fcd5c876e23b65514a2c4fbbdcbd9ff19eaf6c124fdfd5109b3791ef93`.

The pre-call repository gate passed 205 tests with four authorized integration
skips. The final result must report every primary and infrastructure attempt,
mechanical bands by subject, truth, cue, and world, and qualitative
dispositions separately. Missing and invalid outcomes remain in denominators.

This is development calibration only. It authorizes no held-out run,
independent verdict, broader review-skill claim, Striatum policy change,
lane-fit decision, evidence export, training, or CAPLAB acceptance.

## Doctrine receipt

This decision reuses Pincite packet `pkt-eb754819440d5612`, packet-file
SHA-256
`05da913f8126021f318119b26d322711a277383f2f63ad9d4f292455cbfa399f`,
and packet-content SHA-256
`eb754819440d5612ac79946615e1c70e312f1034a34736f1b64fce2d4e689ffd`
from the validated release home. The packet is advisory. ADR 0026 supplies
delegated authority; ADRs 0034, 0036, and 0039 supply the study, instrument,
and native-subject boundaries.

## Reopening conditions

Reopen before changing the campaign, subject tuple, harness version or
command, effort, population, factor, order, replacement rule, ceiling,
containment, custody root, evaluator mechanism, held-out boundary, grading, or
claim ceiling.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized one exact,
  bounded, development-only calibration through native Claude Code and Codex
  CLI harnesses after the model-free gate passed.
