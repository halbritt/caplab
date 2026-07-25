---
id: adr-0060
artifact_type: architecture-decision-record
title: Advisory-selection-001 bounded shakedown authorization
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026-and-direct-repository-owner-execution-delegation
created: 2026-07-25
decided_at: 2026-07-25
expires_at: 2026-08-08T23:59:59Z
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-advisory-selection-001
related_specs:
  - spec-agent-capability-lab
related_plans:
  - Plane CAPLAB-44
---

# Advisory-selection-001 bounded shakedown authorization

## Authority

The repository owner delegated decision authority and authorized execution on
2026-07-25, directing the delegate to proceed autonomously. ADR 0026 requires
that, before a material effect, the delegate still record the exact target,
permitted effects, expiry, preservation boundary, verification, cleanup, and
stop conditions. This record supplies them. The owner's grant enables this
authorization; it does not substitute for it.

## What this does and does not authorize

This authorizes a **shakedown** — instrument validation — for the study mapped
at Plane CAPLAB-44. It does **not** authorize the study.

Shakedown episodes never enter any analysis. The three scenarios it consumes
are **excluded from the study population permanently**. No result, capability
inference, training-eligibility decision, export, or acceptance follows from it.
The preregistration, capability card, and selection ADR remain unwritten and
unauthorized; a separate authorization is required before the first study
episode.

## Why a shakedown is the correct first effect

Three quantities gate the preregistration and none can be established without
model calls:

1. **The repair-vs-review cost multiplier.** All per-episode cost estimates
   rest on 16 archived *review* episodes (104k input tokens, 3.6k output,
   1.4 min each). The 3–10× repair multiplier is an assumption and is the
   dominant error term in every projection.
2. **Headroom.** CAPLAB-81 requires each scenario cite a `common_failure_modes`
   entry, which *asserts* the doctrine-conformant move is not the agent's
   default. The `None` arm measures the spontaneous rate directly.
3. **Instrument viability.** Whether capture, redaction, and coding survive a
   real repair transcript is untested. CAPLAB-77 measures coder agreement on
   *review* transcripts and declares the transfer assumption; repair
   transcripts are the population actually being scored.

## Exact target

Three purpose-built synthetic scenarios, authored under CAPLAB-81 and
**declared consumed**. Four arms per CAPLAB-82 as amended: `retrieval`,
`injection`, `sham`, `none`. `k = 8` per arm.

Outcome is coded identically in all four arms as the fraction of that
scenario's frozen binary codes satisfied. Codes are frozen before any episode.

## Ceilings

| ceiling | value |
|---|---|
| Primary episodes | 96 (3 scenarios × 4 arms × 8) |
| Infrastructure replacements | 24 |
| Total episodes, hard stop | **120** |
| Wall-clock | 8 hours |
| Subject | one pinned native agent system, one snapshot |
| Spend route | existing authenticated subscription capacity |

Stop before any call that would meet or exceed a ceiling.

## Permitted effects

Render the three scenario worlds; run Pincite retrieval offline with
`PINCITE_TRACE_DIR` and `PINCITE_TRACE_SESSION` unset; assemble the four arm
packets; make the bounded native subject calls; capture native event streams
and final task trees; redact packets from transcripts before coding; code
episodes mechanically and by agent; record cost, duration, spontaneous rate,
and coder agreement; write CAPLAB-owned records; commit and push; update Plane.

## Preservation boundary

No writes to `halbritt/pincite`. No entry in the ADR 0019 served-doctrine
record — experimental retrievals are trace-disabled. No modification of any
registered evidence, including the review-dissent raw custody read for the
CAPLAB-78 observation. No held-out or study-population scenario is authored,
rendered, or inspected under this authorization.

## Verification

Report against each ceiling; per-episode attestation derived from the response
stream per turn, not from request configuration (CAPLAB-51 as amended),
including model, harness version, account, corpus/doctrine/retriever identity,
and packet content hash; mechanical confirmation that no coded artifact
contains packet text.

## Stop conditions

Any episode whose stream shows a model other than the pinned one; any coded
artifact failing redaction verification; per-episode tuple drift; replacement
count exceeding 24; total episodes reaching 120; wall-clock exceeding 8 hours;
any write attempted outside the preservation boundary.

## Cleanup

Scenario worlds and captures retained as append-only custody under
`~/.local/share/caplab/campaigns/`. Consumed scenarios recorded by identity so
they cannot re-enter the population.

## Sizing context

At the four-arm design and 80% power, the full study requires 110 episodes per
scenario at MDE 0.40 — 880 at eight scenarios, 1,760 at sixteen. This shakedown
is 120 episodes, roughly 7% of the smaller figure, and is what converts those
projections from assumption to measurement.

## Status history

- `2026-07-25` — `authorized` — recorded by the ADR 0026 delegate under the
  owner's execution delegation. Authorization is not execution, verification,
  inference, or acceptance.
