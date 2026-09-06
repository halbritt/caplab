# Label revalidation for tree-v1 (plan §4, step 3)

- Date: 2026-09-06. Tool: `scripts/tree_v1_revalidate.py` (no model calls,
  no ledger writes). Output: `advisory/pool-runs/tree-v1-revalidation-20260906/`
  (`revalidation.jsonl` one row per record, `base-classes.json` one entry per
  draw case, `judgment-items.json`).
- Scope: every control adjudication whose basis rests on the out-of-contract
  rule — 47 of 71 records (the finding record counted 36 by a narrower regex;
  this pass matches "out-of-set", "not scorable" and "single-document set" as
  well). Each is re-derived against the base production actually pinned, per
  the §2.3 amendment.

## Base classes on the seed-20260819 draw (69 cases)

| class | n | how the base is obtained |
|---|---|---|
| `whole-tree` | 33 | 26 repo-doc via `git archive` at the registered commit; 5 anchored-era change sets via the run's `materialized_base` object; 2 change sets via their body's `git-tree` anchor commit |
| `none-by-design` | 18 | exchange prose: production pinned the artifact alone |
| `partial-product-tree` | 8 | the change set's declared product object (0–17 files) |
| `lost` | 10 | the declared base object is absent from the store or does not decode |

## Outcomes (47 records)

| outcome | n | meaning |
|---|---|---|
| `resolved-valid` | 24 | references resolve in the pinned tree and name what the artifact says, or the label rests on in-set grounds that a base cannot move |
| `reference-not-required` | 16 | `none-by-design`: the reference lies outside the pinned set; unverifiable by contract, not a finding |
| `evidence-unavailable` | 5 | `partial` or `lost` base; the allegation depends on files the reviewer's base did not hold — the pair is scorable for in-set operators only |
| `principal-re-examination` | 2 | whole tree now available; see below |

**No label flips mechanically.** Every declared file hash checked in the
repo-doc trees matches (6 of 6: `training-experiment.json`, `corpus.json`,
`general-coding-controls.json`, three `training-execution-q*.json`). Every
ADR, decision, RFC and markdown link the repo-doc controls cite resolves at
the registered commit, with three residues listed below. Sol's "not
reachable" allegations against repo-doc controls were false against the
tree the artifact belongs to; the sound labels stand, now on
`resolved-valid` rather than on out-of-contract.

**Consequence for §7.** Because no label changed, no corrected `iso-v1`
claim is re-emitted. The `iso-v1` claims stand as originally computed; their
provisional banner is about the environment, not the labels.

## For the Principal

Five items, none of which changes a label unless the Principal says so.

1. **`qs-43f3d7e27dec1a64`** (change set, whole tree via git anchor) —
   *defective*, oracle-settled 2026-08-23 on in-set grounds (CHANGELOG claims
   a v2 anchor the envelope lacks; "proves" guards grep comment tokens). My
   in-set detector missed the wording; the grounds are in-set. Recommend:
   **re-affirm defective**.
2. **`qs-641d18fb33495aba`** (change set, whole tree via `materialized_base`)
   — *defective*, oracle-settled 2026-08-23: the production path returns
   before the provenance write the docs describe. That was read from the
   change set's own files; the whole tree is now available and does not
   contradict it. Recommend: **re-affirm defective**.
3. **`qs-41241900113d9862`** (repo-doc, `first-compile.md`) — *sound*.
   Residue: `rfcs/0031` in a command example (`striatum request rfcs/0031
   --target design-accepted`) does not exist in the tree. It is an
   illustrative argument in a tutorial, not a claim that the RFC exists.
   Recommend: **reference-not-required**.
4. **`qs-e7003896d6e7ab48`** (repo-doc, ADR 0056) — *sound*. Residue:
   `training-started.json` does not exist in the tree; the ADR names it as
   the marker that *would be* written when training starts, and training
   never started. Recommend: **reference-not-required**.
5. **`qs-961371a1d0b19095`** (repo-doc, P13 verification record) — *sound*.
   Residue: `recomputation.json`, `registration.json` under
   `/var/tmp/...` execution roots named as verified outputs; they were never
   repository files. Recommend: **reference-not-required**.

Also re-examined, with new evidence, the whole-tree Principal rulings:

- **`qs-907a07dad63ec02e`** (ruled defective 2026-09-05): the materialized
  base carries `src/semantic_closure/admission/admission.go`, where
  `contextMatches := candidate.Evidence.Context.Matches(candidate.RunContext)`
  and the refusal text is "submitted context does not equal the sealed
  producing-run context". The check compares the submitted context to the
  run's; the record shows them unequal beside `pass`. The ruling is
  confirmed by the code it was made without.
- **`qs-faaba3e49977ce66`** (ruled sound) and **`qs-af9054a1808cceba`**
  (ruled defective), both whole tree: nothing in this pass bears on the
  contract questions they turned on. Recommend: re-affirm as ruled.

## What step 3 leaves

The 16 `none-by-design` records keep the out-of-contract justification, now
grounded in production fidelity (plan §2.3 amendment). The 5
`evidence-unavailable` records mark pairs whose base-dependent operators are
unscorable under `tree-v1`; the pairs stay scorable for in-set operators.
Step 4 (Stage B containment and the probe set) does not depend on the five
rulings above; step 6 (dry run) does.
