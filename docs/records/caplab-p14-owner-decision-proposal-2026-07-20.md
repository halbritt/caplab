---
id: caplab-p14-owner-decision-proposal-2026-07-20
artifact_type: decision-proposal
assertion_type: recommendation
work_item: CAPLAB-34
status: selected-by-adr-0027
prepared_by: primary-agent
prepared_at: 2026-07-20
verification_record: caplab-p13-independent-verification-2026-07-20
disposition_record: adr-0027
---

# CAPLAB-34 owner decision proposal

## Decision required

CAPLAB-33 has an independent technical `FAIL`; the CAPLAB v0 criteria are
`UNMET`. Under the accepted plan, P14 may record `revision` or `rejection`.
Acceptance and conditional acceptance are unavailable.

This proposal was prepared before the owner clarified the blanket delegation
recorded by ADR 0026. ADR 0027 now selects the recommended `revision`
disposition. This record remains the recommendation; it is not repair authority,
retry authority, or acceptance.

## Evidence reviewed

Independent verifier `/root/p13_independent_verifier` recorded:

- P6 source reconstruction, P8/P10 deterministic replay, failure fixtures,
  recovery evidence, claim refusal, split enforcement, and bounded non-export
  checks passed;
- the complete 105-test repository gate passed with four explicitly gated
  integration skips;
- the one live P7 replay did not start because the installed controller refused
  `enable` when it found the retained prior campaign state;
- trapped aggregate disablement then failed because that state named an
  already-absent Garage key and remained `disable_incomplete`;
- external observations found effective access closure and no protected-state
  drift; and
- ADR 0024's `no-example-eligible` decision left the required export criterion
  unmet.

The independent record is
[`caplab-p13-independent-verification-2026-07-20`](caplab-p13-independent-verification-2026-07-20.md).
Its root evidence manifest has SHA-256
`08e5139f12c0874d73d947b449549480ad84308c5fd3a89cab6e6eea03b9bbef`
and independently verifies.

Doctrine packet `pkt-a9ae74cd0a59d3c3` informed the alternatives and authority
boundary. It was assembled from validated Pincite release commit
`65bc86d2555223279e3c0c6cf16be00cce116883`; its JSON SHA-256 is
`7198a10f112e23737db33cabb2a8f4b297bc3d9f689bac8f07ebc361b51f42e7`.
Its authority ceiling is `recommend`; CAPLAB's plan, decisions, and independent
verification record govern this proposal.

## Options

### 1. `revision` — recommended

Record that the current CAPLAB v0 slice is not acceptable and requires
revision. Preserve the completed study registration, observation, refusal,
no-eligibility decision, independent failure record, and all sealed evidence.

Revision leaves two distinct decisions for later authority:

1. repair the P7 controller's terminal-state contract so a retained state with
   an already-absent key can be externally reconciled without weakening
   fail-closed enablement, then authorize a fresh independent P13 campaign; and
2. either retain `no-example-eligible` and revise the next product/version
   contract so export is not an acceptance criterion, or complete the named
   privacy, license, quality, provenance, leakage, and family-safe-split reviews
   needed to reopen P11 and consider one exact export.

Neither follow-up is authorized by selecting `revision`. Each needs its own
proposal, preservation boundary, tests, verification, and owner authorization.

This option fits the evidence because the registered study and deterministic
derivations passed independent checks, protected state did not drift, and the
technical failure has a bounded controller lifecycle surface. It does not
pretend the current slice passed.

### 2. `rejection`

Record that the current CAPLAB v0 slice is rejected and close the current
acceptance campaign. Preserve all decisions and evidence as historical CAPLAB
records. Rejection grants no deletion, purge, publication, export, model, or
training authority.

Choose this if the owner does not want another controller correction and
independent verification campaign, or does not want to revisit the v0 product
contract or eligibility decision. The controller's retained
`disable_incomplete` state remains an observed operational residue; rejection
does not authorize changing or deleting it.

### Unavailable dispositions

`acceptance` and `conditional-acceptance` are unavailable because mandatory
technical verification failed and the export criterion is unmet. Relabeling
the stopped P13 campaign, relying only on effective external closure, or
waiving the export criterion inside P14 would rewrite frozen criteria and is
not an option under the current plan.

## Recommendation and consequences

**Recommendation:** `revision`.

If selected, CAPLAB-34 closes the current v0 acceptance review with a revision
decision. It does not return CAPLAB-33 to In Progress, authorize a controller
change, authorize a retry, reopen P11, or make P12 available. New work must be
projected only after its governing decision and authorization are durable.

If `rejection` is selected instead, the current v0 acceptance campaign closes
without follow-on execution authority.

## Remaining doctrine obligations

The grounded packet still lists co-change, version-history, and generic
no-change/preservation procedure obligations. They are nonmaterial to this
bounded recommendation: no architecture boundary or repair design is selected
here, the independent runtime failure directly identifies the decision front,
and either P14 disposition preserves the current evidence. Those obligations
become material if a controller repair or product-contract revision is later
proposed.

## Owner response

The owner may select exactly one current disposition:

- `revision` (recommended); or
- `rejection`.

Any different disposition requires reopening the accepted P14 contract before
the decision is recorded.
