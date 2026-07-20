---
id: adr-0039
artifact_type: architecture-decision-record
title: Native agent system is the comparative subject
status: active
decision_owner: repository-owner
decision_authority: repository-owner-directive-2026-07-20
created: 2026-07-20
decided_at: 2026-07-20
supersedes:
  - adr-0030-shared-harness-clause
  - adr-0033-shared-harness-clause
  - adr-0037
  - adr-0038
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-preference-001
  - caplab-review-dissent-001
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Native agent system is the comparative subject

## Context

The repository owner directly corrected the CAPLAB execution design: the
native harness is an important component under test because these models are
fine-tuned for agentic workflows within their native harnesses. A model route
behind OpenRouter and Terminus is therefore not a substitute for the same
model identity exercised through Claude Code or Codex CLI.

This was a propagation failure, not a newly discovered preference. CAPLAB
already defined agent configuration as model, reasoning effort,
harness/runtime/adapter, and tool surface. Earlier Study 001 review work also
required the harness/model/effort tuple to be visible. Despite that, ADRs 0030,
0033, 0037, and 0038 treated a common Terminus harness as a fairness control.
The later records encoded the opposite of the established subject identity.

The current `striatum-next` backend declarations are a useful downstream
reference because much CAPLAB testing is intended to inform Striatum. At
Striatum commit `9178e74314ed3d65328b60cec0650471cc15e6b3`, the executable
backend identity is explicitly a `(harness, model, effort)` tuple:

| Tuple | Native harness | Model | Effort | Native invocation |
|---|---|---|---|---|
| `claude-fable-5-max` | `claude-code` | `claude-fable-5` | `max` | `claude -p --model claude-fable-5 --effort max ...` |
| `codex-terra-max` | `codex` | `gpt-5.6-terra` | `max` | `codex exec -m gpt-5.6-terra -c model_reasoning_effort=max ...` |

Striatum supplies observed runtime requirements, not CAPLAB product authority.
CAPLAB owns this decision and its study contracts.

## Decision

For comparative evaluation of agentic models, the CAPLAB subject is the
**native agent system**: model identity, native harness, harness version,
effort and configuration, instruction and knowledge surfaces, tools,
permissions, sandbox, and relevant runtime. The harness is behavior-bearing
treatment, not a nuisance variable to normalize away.

CAPLAB must use each model through its native harness when that native agent
system is the named subject. It may equalize task bytes, requested effect,
authority, starting state, wall-clock and output budgets, available capability
classes, capture, grading, blinding, and analysis where those controls remain
meaningful. It must document irreducible harness differences as part of the
treatment. It must not claim fairness by forcing both models through one proxy
harness.

OpenRouter, Harbor/Terminus, a generic SDK, or another proxy adapter constitutes
a different agent configuration. Such a configuration may be studied only
when it is explicitly named as the subject, or when a later repository-owner
decision expressly authorizes a specific proxy exception and the resulting
claim is limited to that proxy configuration. Convenience, availability,
price, shared surface, or a delegated budget decision cannot create an
exception.

The machine-readable mapping and pre-execution validator live in
[`native-agent-systems.json`](../product/contracts/native-agent-systems.json)
and `caplab.subject_identity`. A live manifest must carry a recognized tuple,
native command, and native version probe. Unknown tuples, changed harnesses,
proxy markers, and implicit exceptions fail closed before an attempt is
prepared.

## Corrective effects

- ADR 0030 remains the historical hypothesis-selection record, but its
  same-harness reopening clause is superseded. The hypothesis must be
  redesigned around native agent systems before execution.
- ADR 0033 and its Terminus-bound preference instrument are superseded. Their
  model-free implementation is not a qualified live instrument.
- ADR 0037 is withdrawn. Its four OpenRouter/Terminus attempts are quarantined
  from inference, adjudication, capability profiling, export, and training.
  Their raw custody remains unchanged and preserved.
- ADR 0038 is withdrawn before its first call. Its runner and manifest are not
  executable authorization.
- No future CAPLAB authorization may reinstate either proxy path merely by
  changing a status field: the executable native-system validator still
  rejects the subject configuration.

The quarantine record is
[`caplab-8-openrouter-attempt-quarantine-2026-07-20`](../records/caplab-8-openrouter-attempt-quarantine-2026-07-20.md).
This correction does not cancel either study or future work. CAPLAB-7/8 and
CAPLAB-13 return to redesign and execution under native tuples.

## Consequences

Comparisons now estimate behavior of the native agent systems that users and
Striatum actually employ. Harness-specific planning, tool use, context
management, retries, and safety behavior remain observable. The comparison is
less superficially symmetric, but scientifically better identified.

Native-harness capacity or authentication failure blocks that subject; it
does not authorize substitution. Each study must freeze exact harness versions
and configuration, capture native transcripts and artifacts under the same
custody requirements, and state where native surfaces cannot be made
identical. Existing synthetic tasks and scoring logic may be reused only after
their instrument contracts are regenerated around the native tuples.

## Doctrine receipt

This correction used Pincite packet `pkt-90fb4230c045430d`, packet-file
SHA-256 `cf6f0791f57c4c4b6cd4803fc4fa6554c6bd1ffc42bdabe97192680a8452990b`,
packet-content SHA-256
`90fb4230c045430deb13d06b5bd10b377c79fc60eddc150fa61a01f8466fd020`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from validated release commit
`65bc86d2555223279e3c0c6cf16be00cce116883`.

The packet is advisory. The repository owner's direct correction supplies the
decision authority. The material guidance is implemented as a domain term,
an explicit supersession path, a machine contract, a cheapest-boundary
execution refusal, tests, and preservation of the invalid attempts as history.

## Reopening conditions

Reopen before changing the definition of a native agent system, the default
native-harness requirement, either adopted Striatum-derived tuple, the
exception authority, or the quarantine boundary. A new model or effort level
requires a new mapped tuple before live authorization; it does not require
reopening this invariant.

## Status history

- `2026-07-20` — `active` — the repository owner directly established the
  native harness as a behavior-bearing component under test and required the
  rule to live in the repository rather than memory alone.
