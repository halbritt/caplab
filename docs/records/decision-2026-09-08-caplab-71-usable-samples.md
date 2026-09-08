# Count usable observations separately from scheduled slots

Date: 2026-09-08. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `7d33cb2`.

## Authorization before execution

Create `docs/product/contracts/usable-sample-budget-v1.md`, link it from the
product README and the prospective behavioral code-authoring procedure, and
complete this record. Use the read-only CAPLAB-52/62 decision comments and
CAPLAB-71 description as planning provenance. Verify new illustrative
arithmetic in a retained local `/tmp/caplab-71-*` script and report using exact
rational binomial sums and independently checked normal-approximation inputs.
No historical model outputs or live store contents may be read or changed.

After verification, append progress and parameter obligations to CAPLAB-71's
description, preserving its open state and original text. Re-read before
updating; stop on concurrent change. No comments or messages are authorized.
Preserve closed historical tickets and their completion metadata. Remove only
this task's doctrine scratch after recording its receipt; retain the arithmetic
and tracker receipts. Authorization expires at commit.

No new sample-size value, MDE, power target, missingness allowance or budget is
adopted for a study. No runtime, scoring, frozen study, admission, model call,
human-time commitment, ranking or placement changes are authorized. Preserve
`docs/designs/`. This is prospective accounting discipline, not a claim that
the current study meets its power or causal-identification requirements.

## Observation and selected correction

CAPLAB-62 comment `3f92fd39-3cd1-4e09-94af-7c94129c3ef4` already corrects the
earlier use of 1.96 alone as an 80%-power multiplier. Preserve that correction.
It derives usable counts T=50, P=50, C=100, then schedules 59,59,118 with a
working no-attempt rate of 0.15. Its subsequent SE=0.0651 and detectable
effect=0.182 check uses all scheduled counts as usable. That extra precision
is conditional on complete usable observations; it is not produced by the
missingness allowance itself.

Select separate fields for required usable counts, scheduled slots, observed
usable counts, and the interpretation of every loss-rate value. An expected
retention probability, a deterministic bound and an observed stop ceiling are
different assumptions. A global loss ceiling does not ensure each arm's
required count or allocation. Power accounting must use the frozen usable
analysis unit and preserve within-episode covariance.

Use an exact binomial example only to demonstrate that expectation-based
inflation is not a probability of attaining the required sample. Independent
constant retention is an illustrative assumption, not a measured model of
CAPLAB failure or refusal. More slots alone cannot repair outcome-dependent
missingness, shared failures, failed blinding or lack of identification.

Leaving the arithmetic unqualified lets capacity planning masquerade as
statistical information. Selecting a new budget now would require unresolved
population, Binding, costs and analysis choices. Adding another general power
library would not resolve those choices. The selected contract corrects the
denominator and records the assumptions without authorizing more execution.

## Implementation and verification

Added the prospective [usable-sample accounting contract](../product/contracts/usable-sample-budget-v1.md)
and linked it from the product index and code-authoring denominator section.
It requires the analysis unit, per-world/arm count targets, actual usable
counts, loss-rate interpretation, covariance assumptions, and precommitted
shortfall disposition. Expected retention and sample-attainment assurance
remain distinct from conditional statistical power. No runtime gate or
numerical study parameter is implemented or adopted.

The exact calculation is retained in
`/tmp/caplab-71-usable-samples-check.py` with results in
`/tmp/caplab-71-usable-samples-result.json`. Verification used Python standard
library rational arithmetic and `statistics.NormalDist`, without a new dependency
or model call. Exact binomial sums were separately checked against repeated
Bernoulli convolution; the variance expression was separately checked by
expanding all four mean coefficients and the paired-control covariance term.
The binomial formula was checked against
[NIST](https://itl.nist.gov/div898/handbook/eda/section3/eda366i.htm).

The required usable counts give SE bound 0.070711 and normal planning detectable
effect 0.198102. All scheduled slots usable gives 0.065094 and 0.182368.
Concentrating 34 losses in P gives 59,25,118 usable observations: total loss
14.41% but detectable effect 0.211106 and a failed P target. Under the explicitly
illustrative independent 85% retention model, joint target attainment is
0.21998181375604586. That last result is neither measured retention nor actual
campaign power. A hard per-cell loss bound has different implications and is
not refuted by this stochastic illustration.

`/tmp/caplab-71-usable-samples-verification.json` records the independent
arithmetic agreement, 24 resolved local links at the initial verification, and
SHA-256 identities of the three product documents. No runtime or test source
changed, so the prior 897-test check is not rerun or presented as verification
of these statistical claims. The exact arithmetic and document checks are the
verification for this change. Statistical assumptions, real retention,
blinding, accuracy, costs, and the campaign's final sample requirements remain
unverified here. There is no independent acceptance verdict.

Read-only planning provenance retained locally:

| Source snapshot | SHA-256 |
|---|---|
| `/tmp/caplab-52-power-comments.json` | `2b54b13c5c8d7e2723c04ad8e9be4a4acd946b7ba69296adf68ea2679334f986` |
| `/tmp/caplab-62-power-comments.json` | `e15f9d7ceac4a1eb47df4d8d585cf6cf46832906f1e7743d41bb30be80492860` |
| `/tmp/caplab-71-retention-current.json` | `85a987f19bc986712b39b6f0221f24b2b67d984efa12b8f8a8d6df086ff16f7f` |

These are decision-comment/description snapshots, not an import or admission
of historical study evidence. CAPLAB-62's closed record and original comment
remain unchanged. The earlier CAPLAB-52 formula is superseded planning context,
not the formula used for this correction.

## Doctrine receipt

The validated release gate passed before retrieval. Release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`; corpus
`corpus-2026-07-12-a11702cc9217`; doctrine `doctrine-f6bbb5196a3f8bf9`;
retriever `retriever-ec995ecdd083b2c8`.

Final evidence-backed packet: `pkt-55dd80b0be58b973`, SHA-256
`55dd80b0be58b973e63eb12f8b927af56372bbef66ba3f7e89b376d5b78c08b9`.
One evidence-gathering pass supplied six typed records: explicit authority,
domain distinctions, static document structure, recorded planning history,
observed synthetic arithmetic, and repository contracts.

Applied `universal-repository-contract-precedence` to preserve the existing
attempt and pooling contracts; `universal-evidence-before-intervention` to
limit the correction to reproduced arithmetic; `universal-explicit-invariants`
to separate usable units from capacity; and
`agent-conduct-authority-bounded-action` to leave actual parameter adoption and
execution outside this effect. The packet supplies engineering guidance, not
statistical authority or permission to run a campaign.

All remaining obligations are nonmaterial to this prospective document claim;
they remain requirements to examine if later implementing a durable execution
or accounting system. The single Plane projection edit uses a before/read-back
check and no automatic retry after an unknown outcome, not a claimed atomic
transaction or distributed idempotence guarantee.

| Remaining obligation group | Exact unmet requirements | Classification and reason |
|---|---|---|
| `data-consistency-model-selection` | application scenario and forbidden observations; datastore consistency and isolation guarantees; datastore guarantee; forbidden observation or invariant; latency and availability consequences under partition or failure | Nonmaterial: no datastore or consistency model is selected or implemented. |
| `data-end-to-end-request-idempotence` | atomic deduplication or uniqueness enforcement; atomic durable effect boundary; external-effect and retry behavior; identity generation and propagation path; retention period and collision semantics; stable intent identity | Nonmaterial: no operation-identity protocol is implemented; an uncertain tracker update stops for read-only reconciliation. |
| `data-system-of-record-derived-state` | derivation, rebuild, reconciliation, and consumer behavior during lag; measured read benefit plus write, storage, freshness, and consistency costs | Nonmaterial: no cache, index, or new derived runtime store is introduced; Plane remains a planning projection. |
| `data-transaction-guarantee-verification` | application invariants and anomaly analysis; concurrency and fault tests at the relied-upon boundary; datastore guarantee and configuration; explicit application invariants; vendor or protocol guarantee for the exact configuration | Nonmaterial: no transaction guarantee is claimed; no runtime storage boundary is changed. |

Citation classification returned four `valid-packet-citation` results. The
eleven explicitly named `/tmp/caplab-71-sample-doctrine-*` working files are
removed after retaining this receipt; arithmetic and tracker files remain.

## Tracker execution and disposition

Re-read CAPLAB-71 immediately before the append and compared the entire issue
data with the fresh baseline; no concurrent change was present. Read-back
matched the requested description append (with the API's outer HTML wrapper).
Only `description_html` and `updated_at` changed. State remains Backlog and
`completed_at` remains null; unrelated fields were preserved. No closed ticket,
comment, or message was written.

Receipts: `/tmp/caplab-71-before-sample-update.json`,
`/tmp/caplab-71-immediate-sample-update.json`,
`/tmp/caplab-71-sample-update.ndjson`,
`/tmp/caplab-71-sample-update-result.json`,
`/tmp/caplab-71-after-sample-update.json`, and
`/tmp/caplab-71-sample-update-verification.json`.

The bounded documentation correction is complete after final link/diff checks
and commit. CAPLAB-71 remains open for actual parameter selection and a complete
freeze; no campaign is ready merely because this accounting contract exists.
