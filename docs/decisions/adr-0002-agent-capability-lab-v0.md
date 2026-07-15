---
id: adr-0002
artifact_type: architecture-decision-record
title: Agent Capability Lab v0 product boundary
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership
created: 2026-07-14
decided_at: 2026-07-15
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans: []
related_receipts: []
---

# Agent Capability Lab v0 product boundary

Status interpretation: the repository owner selected this architectural
boundary on 2026-07-15 after reviewing the integrated CAPLAB-1 interview
answers. The decision establishes CAPLAB's product and claim boundary. It grants
no implementation, inference, retention, model-call, export, training, routing,
deployment, verification, or acceptance authority.

## Decision question and scope

Should this repository establish Agent Capability Lab as a behavioral
capability measurement and model-development platform, using one complete
checkout-retries vertical slice as v0 and reserving broader preference,
Striatum, and fine-tuning uses for evidence-earned later milestones?

This decision governs the product boundary, claim ladder, analytical
identities, scoped systems of record, target-system relationship, human
authority, and v0 acceptance boundary. It does not select implementation
schemas, service topology, retention durations, paid studies, datasets,
training runs, or scheduler policy.

## Observations and evidence

**Observation:** The repository already operates behavioral judgment studies
that bind model configuration, instructions and knowledge, task-world variants,
and instruments. Recorded rewards are mechanically graded; semantic
interpretations may require separate human adjudication. **Evidence:**
[`docs/agent-judgment/README.md`](../agent-judgment/README.md) and
[`checkout-retries-pair-report.md`](../../doctrine/evaluations/robustness/harbor/tasks/checkout-retries-pair-report.md).

**Observation:** Current repository contracts prohibit silent promotion among
observations, inferences, recommendations, decisions, authorization, execution,
verification, and acceptance. **Evidence:**
[`ubiquitous_language.md`](../../ubiquitous_language.md).

**Observation:** The first CAPLAB charter promoted itself to `decided`, made
governance the product, and treated model configuration and trial conditions as
one subject identity. The repository owner rejected that interpretation and
selected recommended answers across a 14-question interview covering mission,
preference, fine-tuning, identity, construct validity, claim promotion,
Striatum placement, training eligibility, evidence storage, Postgres, human
authority, and v0 scope. The owner selected the integrated record on 2026-07-15
by replying `YES` to the explicit selection question. **Evidence:** local Plane
work item `CAPLAB-1`, its review comments, and the owner's direct instruction in
the decision conversation. Plane records coordination; this ADR is the durable
decision record.

## Inferences, rivals, assumptions, and uncertainty

**Inference:** A common trial and provenance spine can support preference,
capability, placement, and training decisions only if those outputs remain
separate claims with separate owners and evidence gates.

**Inference:** The full trial envelope must be content-addressed, while model,
agent configuration, administration, trial context, sealed assignment, attempt,
and analysis population remain separately addressable. Otherwise a treatment or
host change silently creates an incomparable subject and prevents valid
replication or generalization.

Rivals and uncertainty:

- independent study reports would avoid platform work but leave identity and
  claim promotion inconsistent;
- a governance registry would preserve lineage but not deliver the measurement
  product the owner identified as intended;
- a global score would be simpler but would erase pass, task, treatment, cost,
  and uncertainty boundaries;
- delivering every downstream use in v0 would test several new constructs and
  storage contracts at once;
- existing checkout-retries evidence may prove insufficient for a capability
  profile, in which case v0 must report the broader claim as unavailable rather
  than manufacture one.

## Recommendation and alternatives

**Recommendation:** Select the boundary in
[`spec-agent-capability-lab`](../product/specs/spec-agent-capability-lab.md):

- behavioral capability measurement is the product;
- preference is distinct from capability;
- capability cards begin study-local and generalization requires replication;
- Striatum receives pass-specific placement evidence rather than a global model
  ranking;
- training-grade lineage is built now while actual fine-tuning remains gated on
  multiple validated task families and a genuinely held-out evaluation family;
- local S3, system Postgres, Git, and Plane serve distinct record roles; and
- one exactly identified historical checkout-retries experiment, registered as
  Study 001 without pooling adjacent experiments, is the sole v0 vertical
  slice.

Alternatives are no platform, a governance-only registry, all downstream uses
in v0, or a global leaderboard. The specification records their tradeoffs.

## Decision, owner, authority, and rationale

**Decision:** The repository owner selected the recommended boundary in
[`spec-agent-capability-lab`](../product/specs/spec-agent-capability-lab.md).
CAPLAB is a behavioral capability measurement and model-development platform;
checkout-retries Study 001 is its sole v0 vertical slice under the exact-binding
gate recorded in the specification.

**Owner and authority:** repository owner under repository ownership. The owner
made the selection on 2026-07-15 by replying `YES` to the explicit integrated
selection question after the 14-question CAPLAB-1 interview and independent
review.

**Rationale:** this is the smallest complete measurement platform that supports
later preference, placement, and training decisions without promoting one kind
of evidence into another. Its claim ladder and separate downstream authorities
keep broader uses unavailable until their evidence gates are met.

## Authorization and execution scope

The owner's 2026-07-15 reply authorizes recording this selection in the ADR,
specification, indexes, and CAPLAB-1, then closing CAPLAB-1. No product
implementation is authorized.

Future authorization must separately name paths and systems, database and
object-store scope, migrations, preservation and rollback, verification,
model-call or compute ceilings, retention, dataset export, training, and stop
conditions as applicable.

## Consequences and preservation boundaries

This decision:

- CAPLAB becomes the umbrella; Doctrine Robustness and checkout-retries remain
  study families rather than defining the platform;
- studies must declare layered identities, experimental factors, populations,
  sealed trial assignments, and promotion gates;
- human preference and behavioral capability remain independently inspectable;
- placement reports cannot alter Striatum scheduler policy;
- fine-tuning examples require content-addressed human disposition records,
  evidence lineage, and family-safe splits;
- Postgres is the only operational database, S3 preserves evidence bytes, Git
  preserves frozen research and governing records, and Plane remains a
  projection; and
- historical experiment results and retention policies remain unchanged.

The costs are new schemas, storage operations, migration and recovery checks,
human adjudication workflow, and ongoing construct-validity review.

## Verification and fitness criteria

The decision record is internally conformant when:

- this ADR and the product specification agree on status and scope;
- all internal links resolve;
- repository documentation and doctrine checks pass; and
- the owner's dated selection, scope, and authority are recorded without
  creating implementation authorization.

These checks verify the decision record. They do not create the decision or
accept an implementation.

After separately authorized implementation, v0 fitness requires a model-free,
recomputable Study 001 path through Postgres metadata, S3 evidence, frozen Git
records, one bounded capability profile, one authorized training-eligible
export, explicit unavailability of unsupported broader claims, and independent
verification before owner acceptance. Before implementation, Study 001 must be
bound to one existing preregistration, result record, task and world identity,
and verified preserved-input manifest. This decision does not choose that
experiment. Before implementation authorization, the repository owner or a
delegate named in a durable authority record must record a separate Study 001
registration decision binding those artifacts by content identity, and the
implementation plan must link that decision rather than infer the selection
from available files.

## Acceptance owner and outcome

The repository owner is the acceptance owner. Outcome pending. Passing checks
does not select this decision or accept an implementation.

## Reopening and supersession conditions

Reopen when identity layers omit a material confounder, claim gates
misstate actual scientific practice, preference and capability cannot remain
separate, target-system placement requires authority CAPLAB cannot own, data
governance proves insufficient, the storage design is disproportionate, or
fine-tuning requires a different evidence lineage.

Supersession requires a new ADR and reciprocal links. A changed product
specification cannot silently rewrite this decision.

## Related artifacts

- Product specification:
  [`spec-agent-capability-lab`](../product/specs/spec-agent-capability-lab.md)
- Planning projection: local Plane work item `CAPLAB-1`

## Status history

- `2026-07-14` — `proposed` — integrated proposal written from the owner
  interview; final owner selection pending.
- `2026-07-15` — `decided` — repository owner selected the integrated CAPLAB v0
  product boundary; implementation remains unauthorized.
