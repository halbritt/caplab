---
id: adr-0037
artifact_type: architecture-decision-record
title: CAPLAB-8 live preference-study authorization
status: withdrawn
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
expires_at: 2026-07-22T23:59:59Z
supersedes: []
superseded_by: adr-0039
affected_contexts:
  - agent-capability-lab
  - caplab-preference-001
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-8 live preference-study authorization

## Context

ADR 0030 selected and preregistered `caplab-preference-001`. ADR 0033
authorized its model-free implementation, and CAPLAB-7 qualified the frozen
instrument at commit `d79b2c4`. CAPLAB-8 is now unblocked. ADR 0026 delegates
CAPLAB decision and bounded execution-authorization authority to the primary
agent and directs it not to return ordinary decisions to the repository owner.

The clean execution baseline is commit
`3a852eb4f4e8a4573a37e44e59f2edda4f409fee`. The instrument file SHA-256 is
`36f3dfd13ab5128d9ef687a4bab6d3c2b1a1275cecdbb80676f0cb895b5fa020`,
and its design SHA-256 is
`b61f109be67031614b0830d49922280be594d015aa405bdd741a795f08dabe45`.

Read-only preflight observed Harbor `0.18.0`, Terminus `2.0.0`, installed
Terminus source SHA-256
`c6b72b8c6289809b2ff3a3009b8f118fa1edb1da205f48d0b56c6938a49cb12f`,
and an available OpenRouter credential by variable name without reading its
value. The live OpenRouter catalog on `2026-07-20T17:08:47Z` listed exact IDs
`anthropic/claude-fable-5` and `openai/gpt-5.6-terra`.

## Decision and authorization

Authorize one live CAPLAB-8 campaign through `2026-07-22T23:59:59Z` with the
following exact subject tuples:

| Alias | Provider route | Harness | Effort | Turn and completion ceiling |
|---|---|---|---|---|
| `fable` | `openrouter/anthropic/claude-fable-5` | Terminus 2 `2.0.0` under Harbor `0.18.0` | provider default, explicitly passed as `default` | 8 turns, at most 1,024 completion tokens per turn and 8,192 total |
| `gpt` | `openrouter/openai/gpt-5.6-terra` | Terminus 2 `2.0.0` under Harbor `0.18.0` | provider default, explicitly passed as `default` | 8 turns, at most 1,024 completion tokens per turn and 8,192 total |

Both subjects receive the frozen byte-identical subject instruction, a fresh
task-local memory, the same six synthetic task contracts, a 45-minute trial
timeout, JSON parser, disabled summarization, task-local terminal tools, and a
Docker task environment with `network_mode = "no-network"`. Provider requests
originate from the host-side harness; the task environment receives no network
or credential surface.

Run the 12 primary trials in the instrument's frozen order. At most one
byte-identical replacement may follow an infrastructure failure, with no more
than four replacements campaign-wide. A refusal, incorrect tool use, partial
result, or invalid subject artifact is not replaced. The campaign ceiling is
16 trials, 131,072 completion tokens, 12 wall-clock hours, and USD 50.00. The
lower cost ceiling does not amend the preregistered USD 100 design maximum.

Before the first provider request, the executor must commit and push:

- a content-addressed live manifest binding this decision, subjects, task
  order, instruction, harness controls, limits, storage roots, and stop rules;
- a test-first runner that performs a no-call dry-run, refuses manifest or
  instrument drift, creates no-network task images, disables Harbor retries,
  enforces one primary or authorized replacement at a time, and preserves
  every input and attempt identity; and
- regression tests proving command parity, cumulative token and cost stops,
  failure classification, blind-packet identity exclusion, and reveal refusal
  before dispositions are frozen.

The raw Harbor custody root is
`/home/halbritt/.local/share/caplab/campaigns/caplab-preference-001-2026-07-20`.
The repository may retain content-addressed normalized captures, blind packets,
dispositions, execution records, and results under the CAPLAB-owned study and
record paths. Raw provider and harness logs remain in the custody root and are
represented in the repository by an exact preservation manifest. No raw log is
published merely because it exists.

## Blinded delegated disposition

The primary agent may exercise the repository owner's explicitly delegated
CAPLAB judgment authority from ADR 0026. It must apply the frozen comparison
criteria to pair aliases before identity reveal, record criterion-level
dispositions, rationale, uncertainty, and the delegation source, and freeze
all six dispositions before opening the reveal map. This is a delegated owner
judgment record, not an independent verdict or a claim that an unobserved human
interaction occurred.

Prior knowledge of the preregistered reveal map is a residual blinding risk and
must be reported. The packet itself must contain no subject, provider, harness,
model, seal, or operational identity. Any identity clue in task material,
capture, packet, filename, or adjudication surface stops preference inference.

## Excluded effects

This authorization permits no adaptive task, endpoint, model, effort, order,
sample, criterion, or budget change after the first request; no informal
replacement; no omitted attempt; no additional model or adjudicator call; no
historical-evidence admission; no second-study call; no capability or causal
generalization; no dataset export; no training; no Striatum policy mutation;
no independent verification; and no CAPLAB acceptance.

## Preservation and stop conditions

Stop before the first request if the committed manifest, runner dry-run,
complete repository gate, credential presence, exact provider catalog
identity, Docker availability, task no-network policy, artifact capture, or
token/cost accounting cannot be proven.

After the first request, preserve the attempt and stop the affected trial or
campaign on:

- task, subject, instruction, harness, order, reveal-map, or limit drift;
- task-network access, credential exposure, differential subject surface, or
  an output above 8,192 completion tokens;
- a total at or above USD 50.00, 131,072 completion tokens, 16 trials, or 12
  wall-clock hours;
- a second infrastructure failure for one slot, a fifth replacement, more
  than one invalid pair, an unaccounted attempt, or a blinding breach;
- missing raw-custody bytes, hash mismatch, capture-shape mismatch, or inability
  to distinguish provider, harness, capture, task-image, and subject outcomes;
  or
- any effect outside this authorization.

Do not replace, erase, or reinterpret the stopped attempt. A failure consumes
only the replacement or stop allowance named here; it does not authorize an
expanded retry.

## Verification, cleanup, and closure

Technical verification must cover exact manifest and input identity, all
attempt and raw-custody hashes, frozen order, subject-surface parity, token and
cost accounting, replacement accounting, task preservation, mechanical
constraint grading, packet blinding, frozen delegated dispositions before
reveal, result recomputation, complete repository gate, diff hygiene, pushed
commits, and a clean synchronized checkout. Provider invoices or reported
costs remain observations, not implicit zero.

CAPLAB-8 may close when its technical criteria and delegated dispositions are
recorded. That closure is not independent verification, broad capability
inference, training eligibility, routing authority, or CAPLAB acceptance.

## Doctrine receipt

This authorization used Pincite packet `pkt-fd13177d2d5b2db7`, packet-file
SHA-256
`c8d167e3f54b53d3f334e947e785a2c89d18792b701a97a9eac28c3b89c62314`,
packet-content SHA-256
`fd13177d2d5b2db7cd2736a856055bfa53ec2441747e0c1a28f7c6fec3f4b1a7`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from validated release commit
`65bc86d2555223279e3c0c6cf16be00cce116883`.

The packet is advisory. Its authority, repository-precedence, preservation,
behavioral-data fitness, evidence, and stop guidance supports the bounded
authorization. Obligations about historical repository sampling and generic
refactoring economics are nonmaterial: this campaign uses fresh synthetic task
images under an accepted study contract and does not infer from repository
history or perform a refactor. ADR 0026, not Doctrine, supplies authority.

## Reopening conditions

Reopen before changing any subject, provider route, effort, harness, task,
instruction, order, sample, timeout, token or cost ceiling, network policy,
replacement rule, raw-custody root, criterion, delegation source, claim scope,
expiry, or excluded effect.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized one exact
  live preference campaign after the model-free instrument and live harness
  preflight exposed and bounded token and task-network behavior.
- `2026-07-20` — `withdrawn` — ADR 0039 established that OpenRouter plus
  Terminus exercised proxy configurations rather than the native Claude Code
  and Codex agent systems. Four preserved attempts are quarantined and no
  further call is authorized.
