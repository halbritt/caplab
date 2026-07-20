# CAPLAB-42 evaluation gate implementation record

## Scope and authority

ADR 0029 authorizes CAPLAB-42 through `2026-08-03T23:59:59Z` for a
model-free, local snapshot comparison and append-only defect ledger. ADR 0026
delegates the initial baseline decision; ADR 0032 records that decision.
Plane work item CAPLAB-42 remains a planning projection.

The authorization excludes model calls, external runtime mutation, historical
evidence admission, source-history mutation, dataset export, training, and an
independent verdict. The implementation stays within the active CAPLAB
evaluation, test, product-record, decision, and index surfaces authorized by
ADR 0029.

## Baseline observations

- CAPLAB-41 was complete at predecessor commit
  `e8f73ddc3e1beb572fc992d1c0fce49b05d370fa` and supplied one public,
  content-addressed synthetic replay path.
- Active CAPLAB had no snapshot comparison, approved evaluation baseline, or
  typed defect ledger.
- The relevant behavior existed only in the exact historical BOOKS-2 and
  BOOKS-6 custody locators below. ADR 0029 excluded their baselines, results,
  and defect records.

## Executed effects

The execution added a CAPLAB-native snapshot builder that binds corpus,
scenario, fixture, kind, outcome-class, score-eligibility, and model-evidence
identities. Counts and rates are recomputed from scenario records; inconsistent
aggregates are contract errors. Rates use exact integer ratios rather than
floating-point identities.

The comparison validates candidate, baseline, and policy before producing a
gate result. It refuses an unbound baseline, corpus drift, removed scenarios,
substituted fixture or kind identity, coverage shrinkage, run errors, absolute
floor failures, and regressions beyond the approved tolerance.

ADR 0032 selected one initial baseline derived only from CAPLAB's fresh
synthetic fixture. Its canonical SHA-256 is
`de0ffb12951579e7d2a9a012c303a32f5eefdfab40599c879c2ab6873b073fb9`.
The separately versioned policy has canonical SHA-256
`bf4ad6df0a2a0903afab90665bca9c13bd106e87eb3260d8b7dac7109d947e67`.
No API or command writes or updates either artifact.

The execution also added an append-only JSONL defect boundary:

- failed gate results create digest-bound observations;
- identical observation retries return the existing record;
- inferences require linked evidence, credible rivals, and an author;
- dispositions require a linked observation, decision owner, rationale, and
  authority; and
- loading validates every identity and relationship and refuses corruption
  without repair.

The writer uses one exclusive file lock, appends one canonical line, flushes
and `fsync`s the file, and `fsync`s the directory entry when creating a new
ledger. It refuses symlinked path components. Returned snapshots and records
are recursively immutable.

No model or network call occurred. No external runtime state changed. No
historical baseline, result, score, defect event, or judgment was copied or
admitted, and `history/ethogram/` was not edited.

## Historical design provenance

| Work item | Source commit | Source path | Git blob | Translated behavior |
|---|---|---|---|---|
| BOOKS-2 | `759e4015bfa6e369c3e4d9f04253631c257c0c52` | `doctrine/evaluations/regression-gate.schema.json` | `968cf14950c2f11a83e2e127e6ddd2173c413e3f` | score floor and baseline tolerance contract |
| BOOKS-2 | `759e4015bfa6e369c3e4d9f04253631c257c0c52` | `doctrine/evaluations/snapshot.schema.json` | `918c50abfd44e586cfb0532359650f473406919c` | snapshot inventory and coverage contract |
| BOOKS-2 | `759e4015bfa6e369c3e4d9f04253631c257c0c52` | `doctrine/tools/evaluation_regression_gate.py` | `32fe25244510e732be785d14e6bd560d464c6976` | deterministic comparison behavior |
| BOOKS-6 | `f860157b5485ae4fafb4fcc4a298b5a668b952d6` | `doctrine/evaluations/gate-defect-event.schema.json` | `13927b6d19d8d1a0338575741b68578815ec6f2d` | assertion-type separation |
| BOOKS-6 | `f860157b5485ae4fafb4fcc4a298b5a668b952d6` | `doctrine/tools/evaluation_defect_ledger.py` | `3a0df18664a31bc84082b24721abc7a03a07c37f` | append, identity, and linkage behavior |

These commits, paths, and blobs are custody locators. The implementation uses
CAPLAB vocabulary and fresh artifacts; it does not register the historical
bytes as CAPLAB evidence.

## Doctrine receipt

Implementation used Pincite packet `pkt-ef31b8b4820b778c`, packet-file SHA-256
`7b25d750509cd8280ca36449c24d641aba355e86b1c4bd2ef05dda64a463d343`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from the validated release home.

The implementation applies the packet's repository-contract, explicit
invariant, risk-driven test, test-first feedback, and designed-failure-mode
guidance. Performance-measurement obligations are not applicable because this
execution makes no performance claim. Concurrency is limited to one operating
system file lock with no nested acquisition, retry loop, worker, or fairness
policy. A failed or interrupted write is surfaced; retry is content-idempotent,
and corrupted state is preserved and refused rather than repaired.

## Verification

Frozen verification requires:

- exact replay-to-snapshot reproduction of the ADR 0032 baseline;
- pass against the separately bound policy;
- refusal of removals, substitutions, coverage shrinkage, run errors,
  absolute-floor failures, baseline regressions, and baseline identity drift;
- aggregate inconsistency refusal;
- idempotent digest-bound observation append;
- typed and linked inference and disposition records;
- missing-observation, tamper, and symlink refusal; and
- the complete repository gate.

Observed verification results:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest
  tests.test_evaluation_gate -v`: 12 passed;
- `make check`: 139 passed, including all replay and evaluation-gate tests,
  with four authorized live integration skips;
- `git diff --check`: passed with no output; and
- the repository contract's local Markdown-link test passed as part of the
  complete gate.

The executed artifact SHA-256 identities are:

| Artifact | SHA-256 |
|---|---|
| `src/caplab/evaluation/snapshot.py` | `b892716a249e05b57a7c9f0226dd159e41ab2a6525c9f0bc200f5b05a9f86b64` |
| `src/caplab/evaluation/defects.py` | `d1af04365acd457b559b2a32ff57964cf11f98fb46b085bead9d420abba19699` |
| `src/caplab/evaluation/__init__.py` | `e70e7dc0b0f354e669d6a676e010ac7aaa884b297077219d1f85fcf5e738d13a` |
| `tests/test_evaluation_gate.py` | `10ad8b0e476130044dfdad5d155e5a26a8e4ea917acd39a1b9234ea0a17395e9` |
| `docs/product/evaluation/synthetic-replay-baseline-v1.json` | `7fd616b4756a93c838a12683ed62422e33e25fd4984384b8e1ca83b9ad14d7da` |
| `docs/product/evaluation/synthetic-replay-policy-v1.json` | `c7ad69d2aab43270185625879ad1b878a2b51a016d287024fe4823d4c3eb5c48` |

The task-local `/tmp/caplab-42-*` files were removed after their identities and
results were recorded. These are executor observations and technical
verification, not independent verification or CAPLAB acceptance.
