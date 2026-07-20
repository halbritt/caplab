---
id: caplab-p11-eligibility-decision-proposal-2026-07-20
artifact_type: decision-proposal
assertion_type: recommendation
checkpoint: CAPLAB-29/P11
decision_owner: repository-owner
status: awaiting-decision
---

# CAPLAB P11 training eligibility decision proposal

## Decision requested

The repository owner must select one disposition for candidate manifest
`0eeed6348f87d03143ad44c4b9d5440140957c33f32b70e456d80d493aad4a73`.
This proposal records no eligibility decision or export authority.

The available dispositions are:

1. **`no-example-eligible` — recommended on current evidence.** Select no
   candidate. CAPLAB-30/P12 remains unavailable, and the v0 export criterion is
   recorded as unmet.
2. **`defer-for-human-review`.** Name a reviewer and scope a privacy, license,
   quality, provenance, leakage, and family-safe-split review. This does not
   make any candidate eligible or authorize export.
3. **`select-exact-candidates-and-authorize-one-export`.** Name exact candidate
   IDs and record the completed review findings, destination, maximum size,
   retention, expiry, purge owner and trigger, and stop conditions. Without all
   of those fields, selection and export remain unavailable.

## Evidence for the decision

P10 derived 20 content-addressed candidates with complete mechanical
assignment-attempt-outcome and eleven-kind evidence lineage. There are zero
mechanical exclusions, and all candidates share the protected
`checkout-retries-study-001` split group. Each candidate is explicitly
`derived-not-eligible`.

Every candidate records human disposition as `not-recorded`, eligibility
effect as `unavailable`, and leakage review as
`unavailable-pending-human-eligibility`. The manifest contains no completed
privacy or license review and grants no destination or retention authority.
Those absences are why `no-example-eligible` is the conservative current
decision. A later campaign may reopen eligibility after the missing human
reviews; this proposal does not infer that every candidate is permanently
ineligible.

## Excluded authority

Neither `no-example-eligible` nor `defer-for-human-review` authorizes P12. Even
an exact selection authorizes only the one export scope recorded by the owner;
it does not authorize model calls, training, deployment, publication, a later
export, independent verification, or CAPLAB acceptance.
