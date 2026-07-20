# CAPLAB-7 preference instrument implementation record

## Scope and authority

ADR 0033 authorized one model-free CAPLAB-7 implementation campaign from
baseline commit `458ba63884f3948b79adba3b7b5b49cf03f18d64`. Plane work item
CAPLAB-7 is the planning projection. The campaign did not authorize a live
subject call, spend, credential access, human adjudication, identity reveal,
preference inference, evidence admission, export, training, or Striatum policy
change.

## Identity resolution observations

The freeze prerequisite was resolved from read-only, non-secret local state:

- the installed `harbor` executable reported version `0.18.0`;
- its installed `terminus-2` implementation returned version `2.0.0`; that
  source file had SHA-256
  `c6b72b8c6289809b2ff3a3009b8f118fa1edb1da205f48d0b56c6938a49cb12f`;
- clean Striatum Next commit
  `9178e74314ed3d65328b60cec0650471cc15e6b3` declared the model keys
  `claude-fable-5` and `gpt-5.6-terra` in
  `backends/observations/fleet-models.yaml`, Git blob
  `5a8285d056eb6dae64871539bf79d552645ab817`; and
- Harbor exposes both as caller-supplied model names to the same
  `terminus-2` interface. No compatibility substitution was needed.

These observations resolved instrument identifiers. They were not copied into
CAPLAB as model evidence and did not authorize a call. No credential-bearing
configuration was read.

## Executed effects

The execution froze one content-addressed instrument with:

- one byte-identical subject instruction;
- two subject identities sharing the same harness, task-local tools, disabled
  external network, fresh memory, 8,192-token ceiling, and 45-minute limit;
- the preregistered 12-position execution order and six-pair reveal map;
- six fresh synthetic task contracts, each with eight mandatory constraints
  over at least four surfaces;
- zero authorized calls and zero authorized spend; and
- the frozen replacement, invalid-pair, and blinding-breach stop rules.

The instrument design SHA-256 is
`b61f109be67031614b0830d49922280be594d015aa405bdd741a795f08dabe45`.
Each task has a separate contract digest inside the instrument.

The CAPLAB-owned package validates the complete design before use, renders a
new task repository without a process or network call, and content-seals the
instrument, task, subject, harness, model identifier, common surface, and
instruction into every canned capture. It refuses reused destinations,
symlinked destination ancestry, path traversal, live mode, changed design
identities, swapped captures, and identity-contaminated blind material.

Canned capture keeps mechanical satisfied/missed constraints separate from an
empty human disposition. Completed, partial, declined, invalid, and
infrastructure outcomes remain distinct. Only infrastructure outcomes may be
replaced; more than four replacements, more than one invalid pair, or a
blinding breach stops preference adjudication. Blind packets expose only pair
aliases, task material, mechanical results, diffs, handoffs, and an empty
fixed-choice adjudication form.

No model, provider, live harness, credential, network, subprocess, export,
training, or adjudication adapter exists in the package. The canned attempts
are qualification data, not study results or model evidence.

## Doctrine receipt

Implementation used Pincite packet `pkt-73dfad1f44591bd0`, packet-file SHA-256
`b126d3686f9976e2bc43a0cc9b2b4333de2996dc2cf5c5865749a19890dbf1da`,
packet-content SHA-256
`73dfad1f44591bd05f9685757709f0d88c2ad0f1cd8550f4a2bbcbff9ec61a17`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from the validated release home.

The implementation applies the packet's repository-precedence,
information-hiding, minimal coherent API, explicit failure, preservation, and
evidence-before-intervention guidance. The no-change option was rejected only
for the already-authorized, accepted CAPLAB-7 criteria. No opportunistic
refactor or unrelated interface was added.

## Verification

Test-first qualification observed:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest
  tests.test_preference_instrument -v`: 13 passed;
- all 12 canned subject positions across all six task shells rendered,
  captured, mechanically passed, and produced identity-clean pair packets;
- mutations to subject, harness surface, order, reveal map, ceiling, and task
  digest were refused;
- complete, partial, declined, invalid, and infrastructure classification,
  replacement accounting, stop rules, swapped-capture refusal, and recursive
  identity-leak refusal passed;
- `make check`: 152 passed with four authorized live integration skips; and
- `git diff --check`: passed with no output.

Artifact SHA-256 identities before this record was added:

| Artifact | SHA-256 |
|---|---|
| `src/caplab/preference/instrument.py` | `6184f754ef867243e1bfc2325cb79dbf0f1344a4bcb2f1210353eb8bb33c2556` |
| `src/caplab/preference/__init__.py` | `085996cfcf459fc5abe275ce649dbe5eafebfec397b11e50f17fac4fa506a55b` |
| `src/caplab/preference/README.md` | `eebbf119aa1ff5f4aa8412eb23ebd9d037015ae917a2794ce325107497e32593` |
| `tests/test_preference_instrument.py` | `a23f81e9d8158f18560520071c8bdafe8984d3d89a3b2e8ccfc7e33e903664c3` |
| `docs/product/studies/preference-001/instrument.json` | `36f3dfd13ab5128d9ef687a4bab6d3c2b1a1275cecdbb80676f0cb895b5fa020` |
| `docs/product/studies/caplab-preference-001-preregistration.md` | `05ce136a9d935834e570885a6baa9b625bff5bc2548d1d8ecc502d3a365b845e` |

The task-local temporary repositories were removed automatically. The
Doctrine packet under `/tmp` was removed after its identity was recorded.
These are executor observations and technical verification, not independent
verification, human adjudication, study execution, inference, or CAPLAB
acceptance.
