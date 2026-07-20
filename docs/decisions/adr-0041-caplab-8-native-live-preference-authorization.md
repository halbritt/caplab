---
id: adr-0041
artifact_type: architecture-decision-record
title: CAPLAB-8 native live preference campaign authorization
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026-adr-0039-and-adr-0040
created: 2026-07-20
decided_at: 2026-07-20
supersedes:
  - adr-0037
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-preference-001-native-r1
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-8 native live preference campaign authorization

## Context

ADR 0039 withdrew the OpenRouter and Terminus campaign because it replaced
the behavior-bearing native harnesses. ADR 0040 qualified a corrected
instrument using Claude Fable 5 at max effort through Claude Code and GPT-5.6
Terra at max reasoning effort through Codex CLI. No quarantined proxy output
was opened, scored, or used to construct this authorization.

The live boundary now uses the same external bubblewrap isolation profile for
both subjects while mounting only the selected subject's native harness,
configuration, and task tree. Codex retains its native `workspace-write`
sandbox. Harness-specific planning, context management, output management,
and tool behavior remain part of the treatment.

## Decision

Authorize the exact campaign
`caplab-preference-001-native-r1-2026-07-20` under
[`native-live-manifest.json`](../product/studies/preference-001/native-live-manifest.json),
manifest SHA-256
`a1891ec8cb324bf89765f5e3f851efabca27978fc67dd8250f1c2cbdaf6ba942`.
The manifest binds:

- instrument file SHA-256
  `004fb6eb7b7ab5fd22f50087732fa160fbc54f090066d80966e7c038b0c03e6a`
  and design SHA-256
  `cc03ce18856433fdfff6fccab0874f6bf144c80f02c3987294f5bc60d75b1bc7`;
- Claude Code `2.1.215`, Codex CLI `0.144.6`, and bubblewrap `0.9.0`;
- containment source SHA-256
  `f8bed2d71efd225be068e3cfabd024115a813c25a68489ce935596a1ee5e0655`;
- the fresh 12-slot order and reveal map from ADR 0040;
- at most 12 primary trials, four infrastructure-only replacements, 16 total
  trials, 45 minutes per trial, and 12 campaign wall-clock hours; and
- raw custody at
  `/home/halbritt/.local/share/caplab/campaigns/caplab-preference-001-native-r1-2026-07-20`.

The authorization begins at `2026-07-20T21:45:00Z` and expires at
`2026-08-03T23:59:59Z`. It permits authenticated subscription-backed native
model calls and the native harness's ordinary authentication-state updates.
It authorizes no OpenRouter, Harbor, Terminus, generic SDK, historical-evidence
mutation, repository mutation outside raw custody, reveal, adjudication,
inference, export, training use, independent verdict, or CAPLAB acceptance.

## Execution and custody

Every call must pass exact version preflight, render a fresh task tree, and
seal its launch before the native harness starts. The attempt captures native
JSONL, stderr, exit and timeout state, exposed usage, final task tree, and the
final-message hash. Launch, completion, observation, output, and task-tree
digests form one lineage.

The next call may begin only after the preceding attempt has a sealed
observation and the ledger derives the next allowed slot. Primary trials follow
the frozen order. Only infrastructure failure permits one replacement for the
same slot. A second infrastructure failure for that slot, exhausted replacement
or trial capacity, wall-clock exhaustion, version drift, custody ambiguity,
containment drift, expiry, or a proxy marker stops execution. A stopped or
invalid campaign remains evidence about execution state, not a completed study.

## Verification and acceptance boundary

Model-free tests cover proxy refusal, exact source binding, cross-harness
namespace separation, ordered accounting, replacement stops, both native JSONL
formats, exclusive custody, full completion-to-observation lineage, and refusal
to advance past incomplete custody. Live preflight observed all three bound
runtime versions without a model prompt.

This decision authorizes execution and recording only. Mechanical scoring,
blind packet construction, delegated dispositions, reveal, analysis,
independent verification, and acceptance require their existing distinct
boundaries. Successful calls do not by themselves close CAPLAB-8.

## Doctrine receipt

This authorization reuses Pincite packet `pkt-90fb4230c045430d`, packet-file
SHA-256
`cf6f0791f57c4c4b6cd4803fc4fa6554c6bd1ffc42bdabe97192680a8452990b`,
and packet-content SHA-256
`90fb4230c045430deb13d06b5bd10b377c79fc60eddc150fa61a01f8466fd020`.
The packet is advisory. ADR 0026 supplies delegated decision authority; ADR
0039 supplies the native-subject invariant; ADR 0040 supplies the qualified
instrument.

## Reopening conditions

Reopen before changing a subject tuple, native harness, effort, command,
runtime version, containment source, task-bank identity, order, reveal map,
limit, custody root, expiry, replacement rule, capture surface, or claim
ceiling. Runtime unavailability does not authorize a proxy substitution.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized the exact
  native live campaign after content-addressed containment, ordered custody,
  failure accounting, native output capture, and exact version preflight
  passed their model-free gates.
