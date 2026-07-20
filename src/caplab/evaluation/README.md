# CAPLAB evaluation replay

`replay_synthetic_fixture` is CAPLAB's model-free boundary for deterministic
evaluation fixtures. It accepts a content-addressed fixture only when the
manifest, fixture schema, synthetic provenance, request and response hashes,
model identity, and caller-selected execution mode agree.

The boundary refuses symlinks, unmanifested sidecars, path traversal, external
locators, endpoints, credentials, host paths, and mutable model references.
Contract violations raise `EvaluationContractError`; they are not converted
into model outcomes.

Response classification is deliberately narrower than fixture validation:

| Fixture response | Outcome class | Score eligible | Model evidence |
|---|---|---:|---:|
| completed output with no error | `model-outcome` | yes | yes |
| declared refusal or invalid output | `model-failure` | yes | no |
| declared not run | `not-evaluated` | no | no |
| infrastructure, unknown, or contradictory state | `infrastructure-failure` | no | no |

Returned output is recursively immutable. Replay has no model, network,
credential, database, or mutable external-runtime dependency.

## Snapshot gate

`build_evaluation_snapshot` aggregates already-replayed scenarios into a
canonical inventory of scenario IDs, fixture identities, outcome classes,
declared kinds, coverage counts, and exact rational scores.
`compare_evaluation_snapshots` validates the candidate, approved baseline, and
policy before comparison. It refuses:

- a policy that does not bind the supplied baseline;
- corpus drift;
- removed scenarios or substituted kind and fixture identities;
- coverage shrinkage or run errors; and
- absolute-floor or approved-baseline score failures.

The active baseline and policy are under
[`docs/product/evaluation/`](../../../docs/product/evaluation/README.md). The
package has no baseline writer or update command.

`record_gate_observation` appends a content-derived observation only for a
failed gate. `record_defect_inference` requires evidence and credible rivals;
`record_defect_disposition` requires a named decision owner and authority.
Every related event binds the original observation digest. Ledger appends use
one exclusive file lock, flush and `fsync` the file, and `fsync` a newly
created directory entry. Loading refuses malformed, out-of-order related,
unlinked, duplicate, tampered, or symlinked state; it never repairs state
implicitly.

## Historical design provenance

This is a CAPLAB-native implementation under ADR 0029. The following historical
BOOKS artifacts informed its contracts:

| Behavior | Source commit | Source path | Git blob |
|---|---|---|---|
| fixture manifest and hygiene | `3abb7509fe410a46ec2c9cf8e0ef054154d4aa8b` | `doctrine/tools/check_evaluation_fixtures.py` | `cf1c6de4e17295392fc131376483bb983d0b49fd` |
| model/infrastructure outcome boundary | `4a89c600488a4fb5f69f3ac7f6ec76f218ce7c31` | `doctrine/tools/evaluation_outcomes.py` | `4d7caa6195322efae415834e16f3d1118ad25c00` |
| caller/fixture mode agreement | `f860157b5485ae4fafb4fcc4a298b5a668b952d6` | `doctrine/tools/evaluation_mode.py` | `e294e6b09949141a284269162d08d22cb29b9f76` |
| snapshot comparison | `759e4015bfa6e369c3e4d9f04253631c257c0c52` | `doctrine/tools/evaluation_regression_gate.py` | `32fe25244510e732be785d14e6bd560d464c6976` |
| typed append-only defect events | `f860157b5485ae4fafb4fcc4a298b5a668b952d6` | `doctrine/tools/evaluation_defect_ledger.py` | `3a0df18664a31bc84082b24721abc7a03a07c37f` |

Those locators are design evidence, not registered CAPLAB evidence. No
historical fixture, model output, run result, score, baseline, or judgment was
copied or admitted. The fixture under `tests/fixtures/evaluation/replay/` was
written fresh for CAPLAB.
