---
id: adr-0043
artifact_type: architecture-decision-record
title: CAPLAB-8 native normalization and delegated blind disposition
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026-adr-0039-adr-0040-and-adr-0042
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-preference-001-native-r2
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-8 native normalization and delegated blind disposition

## Context

ADR 0042's r2 campaign completed all 12 primary native attempts. The execution
record binds a 115-file raw custody tree with SHA-256
`f990811b8204840351ec9123ab5fb1025fcd2e9f9764720ad709abf839d510a8`.
Execution does not itself authorize normalization, judgment, reveal, or a
result.

The corrected normalization boundary is implemented by
`caplab.preference.native_results`, source SHA-256
`f9640235d1fb8f8decb8f6f61c909d9ee4ee56f614627806b9099150d5b004e9`,
using native capture and blinding code in `caplab.preference.native`, source
SHA-256
`494257688cd03710c33cafda60ce687e4eed65701ba68293c5903705797de8fb`.
It uses the corrected instrument seal and never calls the withdrawn proxy
instrument's subject or harness identity.

## Decision

Authorize one normalization, delegated blind-disposition, reveal, and exact
descriptive-analysis campaign for
`caplab-preference-001-native-r2-2026-07-20`. The permitted effects are:

1. read the 12 sealed r2 native streams, observations, and final task trees;
2. write identity-bearing normalized captures beneath the existing raw
   custody root at `normalization/captures/` and seal their manifest;
3. write six identity-free packets and a packet manifest beneath
   `docs/product/studies/preference-001/native-campaign-r2-2026-07-20/`;
4. allow the primary agent, exercising the repository owner's blanket CAPLAB
   delegation through ADR 0026, to inspect only those six packets and record
   one blind `A|B|tie|unjudgeable` disposition per task with fixed reasons,
   rationale, and uncertainty;
5. freeze all six dispositions and packet hashes before any reveal; and
6. apply the frozen reveal map and recompute the exact preregistered counts and
   conclusion.

The judgments are decisions of the delegated primary-agent mechanism. They
must not be described as the repository owner's personal judgments. The
delegation scope is exactly the six CAPLAB-8 blind pair dispositions and does
not extend to independent verification or CAPLAB acceptance.

## Blinding and analysis contract

Before freeze, the adjudicator may inspect task instruction, outcome,
mechanical satisfied and missed constraints, final diff, and handoff for
aliases A and B. It may not inspect raw-custody paths, subject IDs, tuples,
commands, timestamps, token usage, reveal-map values, identity-bearing capture
paths, or proxy attempts. Any identity marker in a packet or decision stops
before freeze.

After all six decisions freeze, reveal computes for each valid pair:

- constraints satisfied by each subject;
- whether Fable has the strict constraint advantage; and
- whether the frozen preferred alias reveals to Fable.

The candidate explanation is inconclusive with fewer than five valid pairs.
With at least five, it meets the descriptive thresholds only if Fable has the
constraint advantage on at least four pairs and is blindly preferred on at
least four. Otherwise the hypothesis is disconfirmed. The claim ceiling is a
task-conditioned descriptive association on this synthetic population. No
causal mechanism, global model ranking, other-evaluator claim, routing rule,
training eligibility, or cross-harness generalization is authorized.

## Preservation and stop conditions

Raw streams, r1 custody, proxy quarantine, task trees, and observations remain
unchanged. New normalization files are additive and content-checked. Stop on
any campaign incompleteness, non-completed subject outcome, raw or normalized
digest mismatch, duplicate or missing pair, identity leak, incomplete
disposition set, changed reason vocabulary, invalid freeze, premature reveal,
or threshold drift. Do not repair a failed judgment gate by changing task,
packet, capture, reveal, or threshold bytes.

## Verification and acceptance boundary

Model-free tests cover corrected capture scoring and subject seals,
identity-free pair construction, rejection of an identity-bearing rationale,
complete freeze before reveal, capture/packet/freeze lineage, and exact
threshold recomputation. After execution, technical verification must recheck
all raw and normalized hashes, mechanical scores, packet blinding, frozen
decision bytes, reveal recomputation, repository tests, and checkout state.

This decision authorizes no independent verdict or CAPLAB acceptance. CAPLAB-8
may close after its technical criteria, delegated dispositions, result, and
verification record are complete; that closure remains distinct from broader
CAPLAB acceptance.

## Doctrine receipt

This decision reuses Pincite packet `pkt-90fb4230c045430d`, packet-file
SHA-256
`cf6f0791f57c4c4b6cd4803fc4fa6554c6bd1ffc42bdabe97192680a8452990b`,
and packet-content SHA-256
`90fb4230c045430deb13d06b5bd10b377c79fc60eddc150fa61a01f8466fd020`.
The packet is advisory. ADR 0026 supplies delegated decision authority; ADRs
0039, 0040, and 0042 supply subject, instrument, and execution authority.

## Reopening conditions

Reopen before changing the campaign, raw tree, normalization source, capture
schema, packet surface, evaluator mechanism, delegation source or scope,
reason vocabulary, freeze order, reveal map, thresholds, conclusion rule,
output roots, or claim ceiling.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized one exact
  native normalization and six blind delegated dispositions after the complete
  r2 custody tree and model-free normalization gates were verified.
