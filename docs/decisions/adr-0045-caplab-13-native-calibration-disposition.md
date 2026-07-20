---
id: adr-0045
artifact_type: architecture-decision-record
title: CAPLAB-13 native calibration normalization and disposition
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026-adr-0044
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-review-dissent-001
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-13 native calibration normalization and disposition

## Context

ADR 0044's exact native campaign completed 16 primary slots with no
infrastructure failure and no replacement. Every native harness returned a
review artifact, but every artifact failed the frozen review schema. The
instrument asked for a `severity` field without telling the native subject
that the only accepted values were `critical` and `noncritical`. Both native
harnesses instead emitted ordinary labels such as `high`, `medium`, `low`, or
`major`.

Execution is complete, but it does not itself authorize normalized captures or
a calibration disposition. The model-free normalization source has SHA-256
`3db22ce3040a04abd5dd1269195adf8c6d9c4ccadeb2b8fb733686f567fd35ac`.
The repository gate passes 206 tests with four authorized integration skips.

## Decision

Authorize one exact normalization of the 16 sealed native primary attempts.
The normalizer may write identity-bearing captures beneath raw custody at
`normalization/captures`, a capture manifest, and one repository result at
`docs/product/studies/review-dissent-001/campaign-development-native-r1-2026-07-20/result.json`.

Every row must retain its original subject, tuple, cell, truth, cue, world,
status, observed severity vocabulary, review hash, observation hash, capture
hash, preservation result, and mechanical score. Invalid reviews remain
invalid and score-ineligible. No parser repair, severity remapping, semantic
rescue, replay, replacement, or post-hoc model comparison is permitted.

Because there is no schema-valid review, no qualitative disposition is
recorded. Each row must say that qualitative disposition is unavailable due to
the mechanically invalid review schema. The exact calibration conclusion is
`instrument-not-calibrated`; model comparison is `not-estimable`.

## Preservation and boundary

Raw streams, task trees, review artifacts, launch/completion/observation
records, and the held-out seal remain unchanged. `heldout.json` remains
unopened. Stop on any incomplete attempt ledger, digest mismatch, duplicate or
missing subject-cell row, changed task tree, capture overwrite, unexpected
replacement, or result-root collision.

This disposition is development calibration evidence only. It does not rank
the native systems, establish review capability, authorize a corrected rerun,
open the held-out split, support lane-fit or training use, supply independent
verification, or accept CAPLAB.

## Doctrine receipt

This decision reuses Pincite packet `pkt-eb754819440d5612`, packet-file
SHA-256
`05da913f8126021f318119b26d322711a277383f2f63ad9d4f292455cbfa399f`,
and packet-content SHA-256
`eb754819440d5612ac79946615e1c70e312f1034a34736f1b64fce2d4e689ffd`.
The packet is advisory; ADR 0026 and ADR 0044 supply authority.

## Reopening conditions

Reopen before changing normalization source, input custody, schema-validity
rule, severity treatment, denominator, conclusion, comparison status, output
roots, held-out boundary, or claim ceiling.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized exact
  normalization and the fail-closed instrument disposition after all 16 native
  primary slots completed.
