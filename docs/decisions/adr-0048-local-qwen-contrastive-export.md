---
id: adr-0048
artifact_type: architecture-decision-record
title: Local-Qwen contrastive training export authorization
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026-and-adr-0047
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

# Local-Qwen contrastive training export authorization

## Completed source campaign

ADR 0047's exact eight-call campaign completed with seven schema-valid local
Qwen rows, one subject-invalid truncated response, and zero harness failures.
Six valid rows scored `1.0`; one clean row scored `0.2` after inventing critical
findings. The invalid response remains in raw custody and is not eligible.

The raw result semantic SHA-256 is
`df92d36f8986ffcd957cfd7cb0ce848f20089c1878664f1fbfb2bd8039b7d38f`
and its file SHA-256 is
`67e7ab18a9d9ac558f638145472b52301380ba9273bebe518e3d4f1cee8aa412`.
The complete raw custody tree inventory hashes to
`fc20e0fa6d9e15cc7a14ec00de38e31275b792515542b5612b8c01e5efdfa4bd`.
Held-out content remained unopened.

## Decision and authorization

Authorize one deterministic internal training export to
`docs/product/training/caplab-review-dissent-local-qwen-r1/`. Its expected
semantic corpus SHA-256 is
`303a55e6594528ab520d9fbc92d306cd942d4d6a76c68ef314797aa0c84cf1e5`.

The export contains all seven valid local-open-model rows: three `RD-D01`
training rows and four `RD-D02` development rows. `RD-H01` and `RD-H02` are
recorded only as sealed test-family identities; their bytes and rows are not
exported before CAPLAB-16 evaluation.

Each row binds the source study, tuple, task family, treatment, observable
mechanical outcome, oracle type, non-human mechanical label authority, prompt,
chosen response, optional rejected response, source-row hash, split, and
record hash. Perfect local responses support SFT-style chosen records. The
`0.2` clean review forms one preference record with the deterministic frozen
reference review chosen and the local false-positive review rejected.

## Exclusions and license boundary

The export must reject:

- the truncated local response;
- every CAPLAB-13 schema-invalid proprietary response;
- every CAPLAB-8 Claude or OpenAI response and blind preference;
- all ADR 0024 Study 001 candidates;
- provider, harness, capture, verifier, or provenance failures; and
- any row containing a credential, personal datum, host path, or non-synthetic
  third-party content.

The local model repository identifies the exact Qwen APEX quant as Apache-2.0.
CAPLAB-authored synthetic task inputs and deterministic reference reviews are
restricted to this internal export; external publication is not authorized.
The source and output license review is recorded in the dataset card.

## Preservation, verification, and stop conditions

The export is additive and may not mutate raw custody, source study bytes, or
held-out content. Stop on any source digest mismatch, family crossing, row
count other than seven, proprietary source, secret/privacy scan finding,
semantic corpus hash drift, or unresolved license identity.

After materialization, technical verification must independently recompute
every source-row and record hash, the family split, exclusions, secret/privacy
scan, corpus identity, and repository checks. This authorization is not
training authorization, checkpoint deployment, held-out access, Striatum
policy mutation, or CAPLAB acceptance.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized one exact
  seven-row local-only contrastive export after the sealed campaign completed.
