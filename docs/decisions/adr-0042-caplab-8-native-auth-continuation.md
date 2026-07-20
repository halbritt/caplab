---
id: adr-0042
artifact_type: architecture-decision-record
title: CAPLAB-8 native authentication containment continuation
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026-adr-0039-and-adr-0040
created: 2026-07-20
decided_at: 2026-07-20
supersedes:
  - adr-0041
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-preference-001-native-r2
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-8 native authentication containment continuation

## Context

ADR 0041 authorized native campaign r1. Claude Code completed slot zero. Codex
CLI reached its native provider at slot one but received HTTP 401 because the
contained Striatum configuration exposed an `auth.json` symlink whose target
was outside the namespace. Version preflight did not detect the missing target.
The two attempts and exact stop are preserved in the
[`r1 stop record`](../records/caplab-8-native-r1-stop-2026-07-20.md).

Exposing the whole home directory would defeat the containment boundary. The
correction instead projects only the selected Codex harness module, its exact
configuration and model cache, and the native ChatGPT credential file into an
otherwise fresh `CODEX_HOME`. The task tree still cannot see any other home or
repository path. Preflight now requires both exact versions and authenticated
native identities inside the same namespace: Claude `claude.ai`, first-party,
Max subscription; Codex `Logged in using ChatGPT`.

## Decision

Stop r1 without using its authorized replacement. Authorize a fresh campaign,
`caplab-preference-001-native-r2-2026-07-20`, from slot zero under
[`native-live-manifest-r2.json`](../product/studies/preference-001/native-live-manifest-r2.json),
manifest SHA-256
`c6c6eb3e8b9801cc52150edb5fe1b609e2d1724ffc846268421f4330536526b9`.
It retains ADR 0040's instrument, tuples, task bytes, order, reveal map, limits,
capture contract, and claim ceiling. It changes only:

- containment profile to `caplab-native-task-bwrap-v2`;
- containment source SHA-256 to
  `1f0010fcd5c876e23b65514a2c4fbbdcbd9ff19eaf6c124fdfd5109b3791ef93`;
- authenticated no-inference preflight for both native harnesses; and
- campaign identity and raw custody root.

The authorization begins at `2026-07-20T21:55:00Z`, expires at
`2026-08-03T23:59:59Z`, and carries the same 12-primary, four-replacement,
16-total, 45-minute-per-trial, and 12-hour campaign ceilings as ADR 0041.

## Boundaries and stop conditions

All ADR 0041 execution, custody, replacement, verification, and acceptance
boundaries remain in force. R1 attempts cannot be mixed into r2 scoring or
used to skip r2 slots. An authentication identity mismatch stops before a
model call. A model call may start only after exact version and authentication
preflight succeeds inside its actual namespace.

The projected credential is a native harness dependency, not task evidence.
It may be read and ordinarily refreshed by Codex CLI; its content must never
enter repository records, console output, task files, observations, or model
prompts. OpenRouter and all other proxy substitutions remain forbidden.

## Verification

Contained no-inference preflight now observes Claude Code `2.1.215`, Codex CLI
`0.144.6`, bubblewrap `0.9.0`, Claude first-party Max authentication, and Codex
ChatGPT authentication. Tests preserve cross-harness mount separation: Claude
receives no Codex configuration or credential path, and Codex receives no
Claude configuration path.

## Doctrine receipt

This continuation reuses Pincite packet `pkt-90fb4230c045430d`, packet-file
SHA-256
`cf6f0791f57c4c4b6cd4803fc4fa6554c6bd1ffc42bdabe97192680a8452990b`,
and packet-content SHA-256
`90fb4230c045430deb13d06b5bd10b377c79fc60eddc150fa61a01f8466fd020`.
The packet is advisory; ADRs 0026, 0039, and 0040 supply authority and product
constraints.

## Reopening conditions

Reopen under every ADR 0041 condition and before changing the projected native
authentication identity or credential path. A failed authenticated preflight
does not authorize a call or proxy fallback.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate stopped r1, preserved
  its two attempts, and authorized r2 after authenticated contained preflight
  passed without a model call.
