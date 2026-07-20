---
id: caplab-p8-p10-execution-2026-07-20
artifact_type: execution-record
assertion_type: observation
campaign: caplab-backlog-drain-stage-a
authorization: adr-0016-and-owner-drain-instruction
executor: primary-agent
executed_at: 2026-07-20
status: complete
---

# CAPLAB P8 and P10 deterministic execution

## Authority and inputs

The repository owner's standing instruction is to work the Plane backlog until
it is drained. ADR 0016 names CAPLAB-26/P8 and CAPLAB-28/P10 as deterministic,
model-free consumers of P7 and reserves their later human decisions. After P7
completed, the executor ran only those two deterministic boundaries.

Both executions consumed P7 observation manifest
`68845b0ce21fe30e21b5e46f988c624bef85b6eaf3d02319f24c8e7992e7c6d1`.
P10 also consumed P6 admission manifest
`d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`.
P8 consumed the selected capability card and ADR 0006 bytes with SHA-256
`8c910c50923340d3586e82ac29fee4614eb72bfefd2347180803e1792b08fad5`
and `7d14f4e4c9efffd297512be6b1a00cccb16f309119667ee6663afb316e5ff713`.

The commands used the installed package from CAPLAB source
`bf6de2b24ac61e82107208cdc609c7e534c6eaaa`. The current repository was clean
at `cf6f1c19c4b49d4deafa94755dbe63e124ba6c4e` before execution.

## P8 observation

The profile command ran twice and emitted byte-identical canonical documents.
The file SHA-256 is
`2c637d554fef3cc8fa0863d7fc922df0452025f0441d813643809269dd639c0e`;
the content-addressed profile manifest is
`641965dc30fd0dbfca81d56bb05282b01e8e079285ab605c12672e92f3971ef0`.

The output is a `caplab-capability-profile-proposal/1` proposal with status
`pending-human-inference`. It binds the selected card, selection record, P6
admission, P7 recomputation, normalized result, exact population, missingness,
failure classifications, clean guard, and credible rivals. Its human inference
gate is pending. Task-family capability, cross-task capability, model-wide
capability, universal ranking, preference, mechanism, safety, Striatum
placement, training eligibility, technical verification, and acceptance are
all `unavailable`.

## P10 observation

The candidate command ran twice and emitted byte-identical canonical
documents. The file SHA-256 is
`a1aa5c63dddccd19853c1b560e619ae269b92185669d88c71766030ac316d4fa`;
the content-addressed candidate manifest is
`0eeed6348f87d03143ad44c4b9d5440140957c33f32b70e456d80d493aad4a73`.

The output is a `caplab-training-candidate-manifest/1` candidate manifest with
status `eligibility-unavailable`. It contains 20 candidates and zero
exclusions. Every candidate is `derived-not-eligible`, records the exact
assignment-attempt-outcome and eleven-kind evidence lineage, and belongs to
the one `checkout-retries-study-001` split group. Leakage review remains
`unavailable-pending-human-eligibility`. Eligibility, export, model calls, and
training remain unavailable.

## Verification and custody

Both output identities were recomputed from their canonical bodies. The
complete 105-test repository gate passed after execution. P7 access remained
disabled with no credential, key, session, or reader process.

The root-owned execution evidence remains at
`/var/tmp/caplab-p8-p10-execution-2026-07-20`. Its 23-entry `SHA256SUMS` has
SHA-256
`89ea1e396eb8023e1430569edcc740642461b8fd7933f97bded61a93e018b016`
and verifies. It contains the registered P6 document, P7 observation, P8
proposal, P10 candidate manifest, replay outputs, source hashes, test output,
and boundary checks. It contains no credential or provider secret.

## Result and next gates

**Execution result:** CAPLAB-26/P8 and CAPLAB-28/P10 are complete. The outputs
are inputs to human-owned CAPLAB-27/P9 and CAPLAB-29/P11; they do not satisfy
those decisions. P12 export, P13 independent verification, and P14 acceptance
remain unavailable until their dependencies and authority gates are met.
