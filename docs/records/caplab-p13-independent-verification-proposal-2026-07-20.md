---
id: caplab-p13-independent-verification-proposal-2026-07-20
artifact_type: verification-proposal
assertion_type: recommendation
work_item: CAPLAB-33
status: awaiting-owner-authorization-and-independent-executor
prepared_by: primary-agent
prepared_at: 2026-07-20
candidate_baseline: 4ac9f976fbc8fa58205bbcbf8ba24d58769a7176
---

# CAPLAB-33 independent verification proposal

## Status and authority boundary

This record recommends an exact P13 campaign. It is not authorization,
execution, verification, or acceptance. The preparer implemented or executed
parts of P7 through P11 and therefore cannot supply P13's required independent
verdict.

Before any verifier access or live command, the repository owner must name a
fresh independent executor and authorize the exact source commits, evidence
root, read-only access effects, expiry, cleanup, and stop conditions. The
authorization must say whether the executor may create and later remove a
separately named, least-privilege verifier identity. Existing P7 access remains
disabled and is not authority to reopen it.

Doctrine packet `pkt-caab38337e2cf60e` informed the evidence and authority
separation in this proposal. It was assembled from the validated Pincite
release at commit `65bc86d2555223279e3c0c6cf16be00cce116883`; the packet JSON
has SHA-256
`f0133532f3b2757197f0da4452b2870db468ad713d42a03835e8adb4a7234dc0`.
Doctrine is advisory and grants no CAPLAB authority.

## Recommended frozen scope

The owner authorization should bind all of the following before the executor
starts:

- the final clean CAPLAB commit containing this proposal, with
  `4ac9f976fbc8fa58205bbcbf8ba24d58769a7176` as the product-and-decision
  baseline;
- Proximal desired state
  `1b79aa07cc4e44e8fc828449f882c6b62008edb6` and the installed host-file
  identities it governs;
- P6 admission manifest
  `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`;
- P7 observation manifest
  `68845b0ce21fe30e21b5e46f988c624bef85b6eaf3d02319f24c8e7992e7c6d1`,
  normalized-result SHA-256
  `6c4deff865354c78835741bcbbead517828e207db16452469872dfb363dbaab8`,
  and sealed evidence-manifest SHA-256
  `42b57e7c7dc38786f32267e6e2f63031cc56e335e592688470d47dcee2ac94e6`;
- P8 profile manifest
  `641965dc30fd0dbfca81d56bb05282b01e8e079285ab605c12672e92f3971ef0`,
  P10 candidate manifest
  `0eeed6348f87d03143ad44c4b9d5440140957c33f32b70e456d80d493aad4a73`,
  and their sealed evidence-manifest SHA-256
  `89ea1e396eb8023e1430569edcc740642461b8fd7933f97bded61a93e018b016`;
- ADR 0023's `refuse` disposition and ADR 0024's
  `no-example-eligible` disposition; and
- a new root-owned mode-0700 verification evidence root, exact campaign
  identity, UTC expiry, and cleanup owner. The P7 and P8/P10 execution roots
  remain immutable inputs rather than the verifier's output directory.

The campaign excludes evidence admission, historical rewriting, object or
database repair, purge, export, model calls, training, publication, routing,
deployment, product changes, and owner acceptance. Any newly discovered need
for one of those effects requires a separate proposal and authorization.

## Independent procedure

### 1. Establish independence and source custody

The verifier records its identity and confirms it did not implement or execute
the bound P7 through P11 work. It creates a clean isolated worktree at the
authorized CAPLAB commit and records the commit, branch state, submodule state,
Python version, environment, command versions, UTC time, and source inventory.
It independently compares the plan, ADRs, execution records, installed source,
and both sealed execution manifests with their frozen identities.

The verifier runs `make check` without bytecode writes. A passing suite is one
evidence layer, not proof of the integrated result.

### 2. Replay the model-free derivation

Using independent copies read from the sealed evidence roots, the verifier:

1. validates the selected Git inputs and the P6 registration document by byte
   identity, internal content identity, cardinality, and relational links;
2. runs the P6 read-only source and registration verification paths when the
   exact separately authorized verifier access is available;
3. recomputes Study 001 twice from the frozen registration, requires canonical
   byte-identical outputs, and checks the historical comparison and observation
   manifest independently;
4. regenerates the P8 profile twice and requires the bound profile identity,
   `pending-human-inference` immutable status, and unavailable broader claims;
5. regenerates the P10 candidate manifest twice and requires 20
   `derived-not-eligible` candidates, zero exclusions, complete lineage, and
   the single `checkout-retries-study-001` split group; and
6. verifies ADR 0023 and ADR 0024 as separate human decisions. It must not
   rewrite the immutable P8 or P10 output to embed either disposition.

If live P6/P7 reads are not separately authorized, the verifier may complete
the sealed-artifact and hermetic layers but must report the live replay layer
as `NOT VERIFIED`; it may not infer access authority from the installed
controller or prior campaigns.

### 3. Test failure and recovery boundaries

The verifier inspects the relevant assertions and independently exercises the
valid, invalid, missing, altered, tampered, ambiguous, duplicate, interrupted,
and identity-substitution fixtures. It records which oracle covers each case
instead of using a coverage percentage as the verdict.

Database, Garage, and independent-copy recovery are checked against the frozen
P5 execution and independent verification records, their sealed evidence, and
the isolated synthetic recovery tests. This campaign does not repeat a live
repair, restore, or purge. If the existing retained evidence cannot establish
a required recovery criterion, the verifier reports that criterion as
`NOT VERIFIED`; a fresh operational recovery rehearsal needs its own authority.

### 4. Verify claim and split refusal

The verifier independently attempts to promote the P7 observation into
task-family, cross-task, model-wide, preference, mechanism, safety, universal
ranking, or placement claims. Every promotion must fail closed. It also
attempts to divide candidates from the same task family or scenario lineage
across splits; the single protected split group must prevent that separation.

ADR 0023 is then checked as a refusal record, not used as a substitute for the
mechanical claim-ceiling tests.

### 5. Verify bounded non-export

ADR 0024 authorized no destination and selected no eligible examples. The
verifier records the exact CAPLAB-controlled surfaces inspected for a P12
dataset bundle, manifest, dataset dependency, export command, or export
authorization. At minimum those surfaces are the bound Git tree, retained P7
and P8/P10 evidence roots, CAPLAB database namespace, Garage bucket,
independent-copy namespace, and configured CAPLAB runtime paths.

The finding must be stated as bounded to those named surfaces and observation
time. A clean search does not prove that no unrelated system contains copied
bytes. The required CAPLAB result is:

- no authorized or materialized P12 export observed in the named surfaces;
- P12 not run; and
- the CAPLAB v0 export criterion `UNMET` by decision, regardless of whether all
  technical non-export checks pass.

### 6. Close access and seal the record

Any separately authorized verifier login, key, credential, process, session,
ACL, or temporary worktree is removed before the verdict. The verifier proves
the disabled state through external observations, rechecks the protected
database and object inventories, scans retained evidence for credentials, and
seals every report, command output, receipt, and derived artifact in one
`SHA256SUMS` manifest.

Cleanup success is reported separately from verification success. A cleanup
failure forces a stop and a failed access-closure criterion even when earlier
checks passed.

## Required verdict structure

The independent record must contain a criterion ledger with `PASS`, `FAIL`,
`NOT VERIFIED`, or `UNMET BY DECISION` for each of these groups:

1. verifier independence, frozen authority, and source custody;
2. repository and hermetic fixture gates;
3. selected-input and P6 registration identity;
4. P7 recomputation and historical match;
5. P8 profile and claim ceiling;
6. P10 candidate lineage and family-safe split;
7. P5 database, Garage, and independent-copy recovery evidence;
8. ADR 0023 inference refusal;
9. ADR 0024 eligibility decision and bounded non-export observation;
10. access closure, preservation, and evidence sealing; and
11. residual failures and unverifiable claims.

The record reports two conclusions separately:

- `technical_verification: PASS` only when every mandatory technical criterion
  is `PASS`; otherwise `technical_verification: FAIL`; and
- `caplab_v0_criteria: UNMET`, because the required export criterion was not
  satisfied.

Even a technical `PASS` cannot accept CAPLAB v0, authorize P14 acceptance, or
change the P9/P11 decisions. Under the current plan, P14 may record revision or
rejection after reviewing this independent record.

## Stop conditions

The verifier stops without repair or reinterpretation when any of the following
occurs:

- the verifier is not named, independent, or explicitly authorized for the
  exact campaign;
- a bound commit, document, installed file, manifest, input, or object identity
  drifts or cannot be independently read;
- an operation would write historical evidence, mutate a protected store,
  repair a discrepancy, enable access outside the named identity and expiry,
  or exercise an excluded effect;
- a command exposes a credential or sensitive evidence outside the root-owned
  evidence boundary;
- a replay differs, an expected refusal succeeds, an assertion lacks an
  observable oracle, or the inspected non-export surfaces cannot be named;
- cleanup or disabled-state verification fails; or
- the executor cannot state what changed, what remains invariant, or whether
  the next action is authorized.

The verifier retains the failure evidence, disables authorized access if safe,
records the residual state, and returns `FAIL` or `NOT VERIFIED`. It does not
repair the failed condition inside P13.

## Owner decision required

Recommended next action: explicitly delegate CAPLAB-33 to a fresh independent
executor and authorize this frozen procedure, including the exact final CAPLAB
commit, verifier identity, evidence root, read-only host-access effects, expiry,
and cleanup. Until then CAPLAB-33 is ready for authorization but not execution;
CAPLAB-34 remains blocked.
