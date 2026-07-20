---
id: caplab-10-lane-fit-verification-2026-07-20
artifact_type: verification-record
title: CAPLAB-10 first Striatum lane-fit verification
status: pass
created: 2026-07-20
decision_record: adr-0046
verifier: primary-agent
independence: not-independent
---

# CAPLAB-10 first Striatum lane-fit verification

## Verdict

**PASS** for the CAPLAB-10 comparison and disposition criteria. This is
technical verification, not independent verification or Striatum acceptance.

## Verified evidence

- Both accepted profile files are bound by exact SHA-256 and source commit.
- Every comparison is traced to an accepted profile, registered subject tuple,
  admitted study result, and named human disposition where one exists.
- The report covers evidence strength, uncertainty, coverage, failure,
  latency, tokens, and common-cost unavailability.
- Human-only capability inference remains refused or unavailable; the report
  does not synthesize a human disposition.
- No tuple meets either profile floor, so both the qualifying set and Pareto
  set are empty rather than padded with an ineligible candidate.
- The result is a recommendation only. No Striatum lane, scheduler, gate,
  workflow, backend declaration, or dispatch policy was mutated.

## Boundary

CAPLAB-10's comparison, recommendation, delegated acceptance, and technical
verification are complete. A later qualifying campaign requires a new CAPLAB
decision, and any placement change remains owned by Striatum.
