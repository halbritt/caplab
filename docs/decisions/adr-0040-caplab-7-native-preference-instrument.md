---
id: adr-0040
artifact_type: architecture-decision-record
title: CAPLAB-7 native preference instrument qualification
status: decided
decision_owner: primary-agent
decision_authority: adr-0026-and-adr-0039
created: 2026-07-20
decided_at: 2026-07-20
supersedes:
  - adr-0033
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-preference-001-native-r1
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-7 native preference instrument qualification

## Context

ADR 0039 withdrew the shared Terminus design and returned CAPLAB-7 to
instrument work. The correction must retain the intended agent systems:
Claude Fable 5 at max effort through Claude Code, and GPT-5.6 Terra at max
reasoning effort through Codex CLI. No proxy attempt may influence the
corrected design or qualify as study evidence.

The six synthetic task contracts remain usable model-free inputs. They were
created by CAPLAB, no historical evidence was admitted into them, and the
correction changes only the behavior-bearing subject configuration, native
capture requirements, execution order, and reveal map. The four quarantined
proxy outputs were not opened or used during this correction.

## Decision

Accept `caplab-preference-001-native-r1` as the corrected model-free
instrument. It binds:

- `claude-fable-5-max` as `(claude-code, claude-fable-5, max)`;
- `codex-terra-max` as `(codex, gpt-5.6-terra, max)`;
- the exact native commands and version probes derived from the Striatum
  backend tuple declarations cited by ADR 0039;
- a fresh 12-slot execution order and reveal map;
- the six existing task contracts through file SHA-256
  `36f3dfd13ab5128d9ef687a4bab6d3c2b1a1275cecdbb80676f0cb895b5fa020`,
  projected to task instruction and task bytes only; and
- native event stream, final tree, last message, exit status, and runtime
  version as required capture surfaces.

The content-addressed instrument is
[`native-instrument.json`](../product/studies/preference-001/native-instrument.json),
file SHA-256
`f54be9b15feba7865b3fa31686d43557da82731c9d38eede82d4294d20e9a25b`
and design SHA-256
`a66911de20af5ebfbcfdd8ffecbd19f5bf8b5cb2a757083c1e42df4b22eeaef0`.
Its loader projects out the old instrument's proxy harness, subjects, order,
and reveal map. Rendered tasks carry the corrected instrument seal.

## Authorization boundary

This decision qualifies a model-free instrument and closes the corrective
CAPLAB-7 implementation slice. It authorizes zero model calls and zero spend.
It does not authorize CAPLAB-8, delegated dispositions, reveal, inference,
placement guidance, export, training, independent verification, or CAPLAB
acceptance.

The native command records intentionally require external containment for
live execution. CAPLAB-8 must implement and test that containment, freeze the
observed Claude Code and Codex CLI versions, and receive a new exact live
authorization before preparing an attempt. Native-harness unavailability
blocks the affected subject and does not reopen the proxy route.

## Verification

The public model-free interface verifies the policy and task-bank digests,
native tuple commands, zero-call budget, task-only projection, fresh task
rendering, corrected seal, 12 unique subject-task slots, balanced reveal map,
and refusal of a proxy substitution even when the changed instrument is
resealed. The complete repository gate passed with 186 tests, four live
integration tests skipped by their standing environment gates.

## Doctrine receipt

This decision reuses the directly applicable ADR 0039 Pincite packet
`pkt-90fb4230c045430d`, packet-file SHA-256
`cf6f0791f57c4c4b6cd4803fc4fa6554c6bd1ffc42bdabe97192680a8452990b`,
and packet-content SHA-256
`90fb4230c045430deb13d06b5bd10b377c79fc60eddc150fa61a01f8466fd020`.
The packet is advisory. ADRs 0026 and 0039 supply decision authority.

## Reopening conditions

Reopen before changing either tuple, task-bank identity, order, reveal map,
surface contract, capture requirement, zero-call boundary, or downstream claim
ceiling. A live campaign requires a separate authorization even if every
model-free check passes.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate qualified the corrected
  native-agent-system preference instrument under ADR 0039.
