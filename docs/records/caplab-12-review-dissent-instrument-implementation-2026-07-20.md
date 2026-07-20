# CAPLAB-12 review-dissent instrument implementation record

## Scope and authority

ADR 0036 authorized one model-free CAPLAB-12 implementation campaign from
baseline commit `2193307f5c83cdc0b619655eb36cd4fd4c2554ad`. Plane work item
CAPLAB-12 is the planning projection. The campaign authorized no subject,
provider, or live harness call; spend; credential access; historical evidence
admission; human disposition; study result; inference; export; training;
Striatum policy change; independent verification; or acceptance.

## Executed effects

The execution froze separate content-addressed development and held-out
artifacts. Each split contains two worlds and eight cells. Every world is a
complete target-truth by author-cue factorial with a byte-equal clean/defect
pair differing on one semantic line and a byte-equal author-cue pair. The
instrument design SHA-256 is
`2038bacc25c6b95ce2420e0c273829922b6f5eeb2230658229a10bb04b521767`.

The CAPLAB-owned package:

- validates schema, content digests, split identities, cell counts, complete
  factorials, causal-pair hygiene, required-evidence availability, and the
  exact zero-call budget;
- gives calibration only the development content and held-out aggregate seal,
  while reserving the two-split loader for this model-free qualification;
- deterministically renders neutral task images without the hidden oracle;
- captures only explicit canned attempts, hashes target state before and
  after, and preserves infrastructure failures outside mechanical scoring;
- reaches the frozen `1.0`, `0.7`, `0.4`, `0.2`, and `0.0` bands with reference
  fixtures, including the cautious-clean anti-refusal control; and
- creates blind packets with no subject, provider, treatment, truth,
  mechanical score, or prefilled human disposition.

The two-subject development estimate is 16 primary calls plus at most four
infrastructure replacements, for a maximum of 20 calls and 163,840 completion
tokens. Paid cost remains unavailable until exact subjects and routes are
frozen. The instrument authorizes zero calls and zero spend. There is no live
runner or provider adapter in the package.

## Doctrine receipt

Implementation review used Pincite packet `pkt-d85ec1bbe5d82cb1`, packet-file
SHA-256
`015a64e91e9ed64a623ce9955e6eae6f31b5d731733efc70ccbf5bb699b4cf69`,
packet-content SHA-256
`d85ec1bbe5d82cb127c5071389e40c9eef2b9d99bff0be68aa671195c7c1369a`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from validated release commit
`65bc86d2555223279e3c0c6cf16be00cce116883`.

The packet's repository-precedence, runtime-validation, explicit-invariant,
observable-outcome, preservation, and authority-separation guidance was
material. Remaining obligations about type-checker maintenance history,
test-suite false-positive history, out-of-process and database dependency
classification, performance of substitutes, and generic no-change economics
were nonmaterial to the narrower model-free contract: this repository has no
configured type checker, the package has no out-of-process dependency or
managed database, the sole read interception proves the held-out non-read
contract, no historical suite-reliability claim is made, and ADRs 0034 and
0036 had already selected and authorized implementation. The packet's
authority ceiling was recommendation; ADR 0036, not Doctrine, authorized the
effects.

## Verification

Test-first qualification observed:

- the initial focused test failed because `caplab.review_dissent` did not yet
  exist;
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest
  tests.test_review_dissent -v`: 13 passed;
- the calibration non-read test intercepts `Path.read_bytes`, the actual
  artifact access surface, and fails if `heldout.json` is opened;
- every world, cell, harm band, infrastructure status, preservation outcome,
  blind packet, manifest refusal, and exact estimate passed;
- `make check`: 165 passed with four authorized live integration skips; and
- `git diff --check`: passed with no output.

Artifact SHA-256 identities before this record was added:

| Artifact | SHA-256 |
|---|---|
| `src/caplab/review_dissent/instrument.py` | `297b53f9e39e21e9fc0be77f6340f775cbb7e350da81e574005d61c2d1b6090b` |
| `src/caplab/review_dissent/__init__.py` | `57c1203a4cddfe1d2e8facc158c1ae87592e8388e6e5c9b8d3983bfc13772269` |
| `src/caplab/review_dissent/README.md` | `06fb5ecfb47437f461a450912b8387c3daed9cc93f35fe58951c26037730e104` |
| `tests/test_review_dissent.py` | `eff83e3d5efa736c5d6662606310fb5029daf6e7ff38fba0e1795cafe702849e` |
| `docs/product/studies/review-dissent-001/instrument.json` | `7cd5c06934a0a5dadb85bb7d86b6195b3a298f58b5d9c3880d7773dec953f394` |
| `docs/product/studies/review-dissent-001/development.json` | `3de5a877d003f568b680a72ddbd2659ba69e4a391ecebbb3cc35ee24aae77419` |
| `docs/product/studies/review-dissent-001/heldout.json` | `ec7ef0160e878608094f190b7af5bb3c20e4183e7621cdb5d9d1464fb5fe2834` |
| `docs/product/studies/review-dissent-001/live-estimate.json` | `c0b4dfa1a3d648f1b30a1c7616a9b802e40723371be18c102ae8e341d9f29d1f` |
| `docs/product/studies/caplab-review-dissent-001-preregistration.md` | `6d8813942a746c2fad14a95fdc6aa5a8072e32f05398228b243989d556d72043` |

Temporary rendered task images were removed by their test contexts. The
Doctrine packet and typed evidence records under `/tmp` are removed after
their identities are recorded. These are executor observations and technical
verification, not live study execution, independent verification, human
judgment, inference, or CAPLAB acceptance.
