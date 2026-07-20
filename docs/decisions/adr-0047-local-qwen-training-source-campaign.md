---
id: adr-0047
artifact_type: architecture-decision-record
title: Local-Qwen review training-source campaign authorization
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - review-dissent-001
  - governed-training-data
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Local-Qwen review training-source campaign authorization

## Context

CAPLAB-14 requires a validated contrastive training export. Study 001 remains
`no-example-eligible` under ADR 0024. CAPLAB-13 produced zero schema-valid
reviews. CAPLAB-8 produced valid blind preferences, but its Claude Code and
Codex subscription outputs are not eligible for competing-model development:
the current Anthropic Consumer Terms section 3.2 and OpenAI Terms of Use
prohibit that use. Ownership language does not erase the use restriction.

The existing Striatum local-Qwen backend declares the native tuple
`striatum-openai-lane` v1 plus `qwen3.6-35b-a3b`. It is already serving on the
loopback endpoint and is a review-only, E0 backend. The frozen review-dissent
instrument has two development task families and two separately sealed
held-out families. Its prior proprietary campaign exposed an elicitation bug,
not a task or oracle defect.

## Decision and authorization

Authorize exactly the eight development calls in
[`local-training-instrument.json`](../product/studies/review-dissent-001/local-training-instrument.json).
The prompt presents every public task file in one immutable JSON payload and
states the exact `critical|noncritical` severity enum. The subject must respond
through the Striatum-declared native harness with exactly one review object.

Permitted effects are limited to sequential loopback inference and additive
raw custody beneath the exact manifest root. Each response, parse status,
mechanical score, duration, command, harness version, model file hash, and
manifest identity must be recorded before the next call.

No call may start while the llama server reports an active or deferred request.
This authorization may not restart, stop, reconfigure, or replace the server;
open held-out content; send proprietary output to the local model; use a proxy
harness; make a paid call; retry a subject outcome; or mutate Striatum.

## Result and export boundary

Schema-valid rows may be mechanically graded because the complete presented
file set is recorded; no human label is required for the frozen oracle. Invalid
or infrastructure rows remain excluded. A result may recommend an internal
SFT/preference export using local-model output and deterministic reference
reviews only. The export requires ADR 0048 after the complete campaign is
sealed and may not contain Claude or OpenAI output.

Development world `RD-D01` is the training family and `RD-D02` is the
development family. Held-out worlds `RD-H01` and `RD-H02` remain unopened and
reserved for CAPLAB-16. Family identities may not cross those splits.

## Terms and data lifecycle

The terms review was performed on 2026-07-20 against the current official
Anthropic Consumer Terms and OpenAI Terms of Use. It is a conservative product
eligibility decision, not legal advice. Qwen output remains internal and may be
used only for this CAPLAB development purpose. Inputs are synthetic and the
campaign must scan exported text for credentials, personal data, host paths,
and non-synthetic third-party material before eligibility.

Raw custody is retained through the CAPLAB-17 disposition. Purge or external
publication requires separate exact authority. The campaign stops on server
busy state, tuple or model drift, response write failure, held-out access,
credential discovery, or any limit breach.

## Advisory doctrine

Pincite packet `pkt-aec71995c3f2cb2d`, packet-file SHA-256
`ef0984f5d9123c97ec1a7e4271654c3cfe1d560d5a1253b46ef9491d983f08a7`,
and packet-content SHA-256
`aec71995c3f2cb2d3a49c23eaa1d93637caecf906a481d5739f03b3491493734`
supplied advisory guidance. The exact manifest, source hashes, decision owner,
limits, data classification, retention, stop conditions, tests, and separate
export gate discharge its authority, evidence, privacy, and lifecycle
obligations.

## Verification and reopening

Model-free tests must prove oracle exclusion from prompts, complete task-file
presentation, exact JSON/schema refusal, deterministic grading, local-only
source enforcement, and family-safe splits before the first call. Technical
verification after execution remains distinct from result disposition.

Reopen before changing any subject tuple, task byte, prompt, order, call count,
replacement rule, timeout, endpoint, split, output use, retention, or held-out
boundary.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized eight bounded
  local-Qwen native-harness development reviews with no server mutation.
