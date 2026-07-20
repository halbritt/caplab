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

## Historical design provenance

This is a CAPLAB-native implementation under ADR 0029. The following historical
BOOKS artifacts informed its contracts:

| Behavior | Source commit | Source path | Git blob |
|---|---|---|---|
| fixture manifest and hygiene | `3abb7509fe410a46ec2c9cf8e0ef054154d4aa8b` | `doctrine/tools/check_evaluation_fixtures.py` | `cf1c6de4e17295392fc131376483bb983d0b49fd` |
| model/infrastructure outcome boundary | `4a89c600488a4fb5f69f3ac7f6ec76f218ce7c31` | `doctrine/tools/evaluation_outcomes.py` | `4d7caa6195322efae415834e16f3d1118ad25c00` |
| caller/fixture mode agreement | `f860157b5485ae4fafb4fcc4a298b5a668b952d6` | `doctrine/tools/evaluation_mode.py` | `e294e6b09949141a284269162d08d22cb29b9f76` |

Those locators are design evidence, not registered CAPLAB evidence. No
historical fixture, model output, run result, score, baseline, or judgment was
copied or admitted. The fixture under `tests/fixtures/evaluation/replay/` was
written fresh for CAPLAB.
