# CAPLAB-41 evaluation replay implementation record

## Scope and authority

ADR 0029 authorizes CAPLAB-41 through `2026-08-03T23:59:59Z` for a
model-free, local, CAPLAB-native implementation. The permitted effects are
limited to `src/caplab/evaluation/**`, `tests/test_evaluation*.py`,
`tests/fixtures/evaluation/**`, required records, and their indexes and gates.

The authorization excludes model calls, external runtime mutation, historical
evidence admission, source-history mutation, dataset export, training, and an
independent verdict. Plane work item CAPLAB-41 is the planning projection.

## Baseline observations

- Active CAPLAB had no evaluation replay package before this execution.
- ADR 0029 selected reusable behavior from BOOKS-4 through BOOKS-6 while
  preserving the historical implementations as design evidence only.
- The repository gate at predecessor commit
  `c119ea929c2a07cf1eb09c2a98f8b64f5e811ebc` passed 105 tests with four
  authorized live integration skips.

## Executed effects

The execution added one public model-free operation,
`replay_synthetic_fixture`, and one recursively immutable result type. The
operation:

- verifies an exact manifest and fixture schema;
- binds manifest, fixture, request, and response content identities;
- requires fresh synthetic provenance and an immutable synthetic model name;
- refuses symlinks, undeclared files, path traversal, external locators,
  endpoints, credentials, host paths, and mutable references;
- checks the caller's execution mode before classification; and
- separates model outcomes, model failures, infrastructure failures, and
  not-evaluated outcomes.

Unknown and contradictory response states fail closed as infrastructure
failures. They are not score eligible and cannot supply model evidence.
Contract violations raise `EvaluationContractError` and are never rewritten as
model behavior.

The execution also added one fresh synthetic fixture. It contains no live
capture, credential, endpoint, host path, mutable source reference, or
historical output. No model or network call occurred, and no external state was
changed.

## Historical design provenance

| Work item | Source commit | Source path | Git blob | Translated behavior |
|---|---|---|---|---|
| BOOKS-4 | `3abb7509fe410a46ec2c9cf8e0ef054154d4aa8b` | `doctrine/tools/check_evaluation_fixtures.py` | `cf1c6de4e17295392fc131376483bb983d0b49fd` | manifested fixture identity and hygiene |
| BOOKS-5 | `4a89c600488a4fb5f69f3ac7f6ec76f218ce7c31` | `doctrine/tools/evaluation_outcomes.py` | `4d7caa6195322efae415834e16f3d1118ad25c00` | model/infrastructure outcome separation |
| BOOKS-6 | `f860157b5485ae4fafb4fcc4a298b5a668b952d6` | `doctrine/tools/evaluation_mode.py` | `e294e6b09949141a284269162d08d22cb29b9f76` | caller/fixture mode agreement |

The commits, paths, and blobs are custody locators. Their bytes and results
were not admitted into CAPLAB, and `history/ethogram/` was not edited.

## Doctrine receipt

Implementation used Pincite packet `pkt-7e4f53e45c8bb683`, packet-file SHA-256
`9830cd7053ff7eb0cc2531498445ad70bb3954a7d00702d337a9a9235fb55537`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from the validated release home.

The implementation follows the packet's explicit failure-policy,
risk-driven-test, test-first-feedback, and mutable-ownership guidance. The
concurrency obligations are not applicable: replay is synchronous, creates no
worker, wait, lock, retry loop, or external resource, and returns no mutable
object graph.

## Verification

Verification criteria are:

- the fresh manifested fixture replays through the public package interface;
- content identity and caller/fixture mode are enforced;
- hygiene rejects every excluded dependency class;
- unknown, contradictory, and infrastructure states cannot become model
  evidence;
- declared model failures remain score eligible but cannot masquerade as
  completed model evidence; and
- the complete repository gate passes.

Observed verification results:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest
  tests.test_evaluation -v`: 22 passed;
- `make check`: 127 passed, including the 22 replay-boundary tests, with four
  authorized live integration skips;
- `git diff --check`: passed with no output; and
- the repository contract's local Markdown-link test passed as part of the
  complete gate.

The three task-local `/tmp/caplab-41-*` files and generated Python bytecode
caches were removed after their identities and results were recorded.

The executed artifact SHA-256 identities are:

| Artifact | SHA-256 |
|---|---|
| `src/caplab/evaluation/replay.py` | `f49286fe3aec236f5823a74acc781447b8ddb3e48b01a69e179e44f1e0b8b8e8` |
| `src/caplab/evaluation/__init__.py` | `4b03985cfab54c62a6f60ba746126e66923769448896a3bf778f8a1fb2039e60` |
| `tests/test_evaluation.py` | `4a1d99fd3e1e2a349a0efb2474c5bde2cf7aa1b915ac6c3ea71c5bee0f596549` |
| `tests/fixtures/evaluation/replay/constraint-continuity-pass.json` | `0d7cba22ee0cc37b71366fc7eac9aa060bee25d4441709e1b5aca511b5b452b4` |
| `tests/fixtures/evaluation/replay/manifest.json` | `c30c179d6d1b2aa5b575557a4e0365b3bc70e422b61874c720318acc3c56ecc9` |

These are executor observations and technical verification, not independent
verification or CAPLAB acceptance.
