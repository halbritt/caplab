# tree-v1 coverage report: where each case's base actually is

- Date: 2026-09-06. Plan `tree-v1` rev 2, step 2 deliverable (§3, §8). No
  model calls. Every number below was computed against the ledger dump, the
  graph store objects, the CAS and the two git repositories on this host.
- **The plan's factual premise in §1/§2.3 does not hold and this report
  stops at the step-2 gate for a ruling.** The graph store holds no
  "repository snapshot object current at a seq": its `product-artifact`
  objects are per-pass product trees of 1–105 files (2 of 123 contain
  `go.mod`). Whole-repository bases exist only where striatum expanded a
  git anchor into a bundle, and those bundles are what the ledger's
  `materialized_base` pins name.

## What a production reviewer actually saw

From 8,220 `review` runs in the ledger: 6,053 carry four input pins
(change set, product-artifact as `base`, `materialized_base`, and one
more) — the anchored-base era; 1,919 carry **one** pin, the reviewed
artifact alone. Every prose review (designs, plans, proposals) is one-pin.
Production reviewers of prose are **world-blind**: they never received a
repository tree. Sol cleared 16 of 18 prose controls before isolation by
reading the live checkout — the wrong universe — not by any affordance
production gives.

Where a `materialized_base` pin exists its object is present (400/400
sampled) and is a whole tree: 976 of 1,086 files of one sampled base match
striatum-next commit `629fb7a1…` exactly, the remainder being the product
overlay — the "anchored-expanded" composition the ledger names.

## The seed-20260819 draw, case by case

| class | n | exact base available | source | what production gave the reviewer |
|---|---|---|---|---|
| repo-doc (`v1`) | 26 | **26** | `git archive` at the registered commit (all 26 resolve; 64/65 markdown links resolve in that tree) | n/a — CAPLAB corpus, not production artifacts |
| change set, anchored era | 5 | **5** | the run's `materialized_base` object (whole tree, 977–1,121 files, `go.mod` present) | that same tree |
| change set, git-anchor body | 2 | **2** | `git archive` at the body's `anchor.commit` (both resolve) | reviewer got the change set only (1 pin) |
| change set, `base.content_hash` / `observed_product` present | 9 | partial only | a product object of 0–17 files, plus ancestors where declared | change set only (1 pin) |
| change set, base object missing | 9 | **none** | the declared base hash resolves to no object in the store | change set only (1 pin) |
| exchange prose (`v1`) | 18 | **none exists** | no tree was ever pinned; `RQ-` references resolve to compilation requests 19/19; the one escalation reference does not resolve | the artifact alone (1 pin) |

Whole-repository exact bases: **33 of 69**. Partial product bases: 9.
No base: 27 (9 change sets with lost objects; 18 prose that never had one).

## What this means for the plan

1. **§2.3 `product-head-at-seq` cannot be built as specified.** There is no
   repository snapshot series in the graph store. For anchored-era change
   sets the exact base is the run's `materialized_base` pin; for git-anchor
   bodies it is `git archive`; for older change sets it is the declared
   product object, which is partial; for prose it does not exist.
2. **`unscorable_missing_base` as written removes 27 of 69 cases**, all 18
   prose among them. The prose class would be empty, not underpowered.
3. **The prose question is not "which tree" but "any tree".** Production
   never gave a prose reviewer a tree. `iso-v1` was, for prose, the
   production-faithful environment; `tree-v1` with a repository tree would
   give prose reviewers *more* than production does. Sol's 16 prose refusals
   under isolation were refusals of exactly the situation production puts a
   reviewer in.
4. **The ledger re-derivation (§4) changes shape.** For the 18 prose and 9
   lost-base change sets, "reference resolvable against the exact base" has
   no base to resolve against; the §4 outcome for those is
   `evidence-unavailable` or `reference-unresolvable-anywhere` by
   construction, and the plan says neither auto-sound nor auto-defective.

## Options for the Principal

- **A. Production-faithful bases.** Each case gets what production gave its
  reviewer: whole tree for the 7 anchored/git-anchor change sets; the
  declared partial product tree for the 9 with objects; nothing for the 18
  prose and 9 lost-base change sets, plus recoverable exchange objects
  (`RQ-` compilation requests) under `evidence/`. Every case stays
  scorable; `base_source` on the row says which; the contract tells the
  reviewer exactly what was and was not pinned, so "not reachable" is a
  legitimate finding only for a named object outside the pinned set.
  Measures the production affordance. Sol's prose refusals would then be
  judged against the same one-pin universe production gives it.
- **B. Plan as written.** Exact whole-tree bases only (33 cases); the other
  36 unscorable. Measures a cleaner construct on half the draw, with no
  prose class.
- **C. A for change sets, plus a repository tree for prose from
  `git-at-time` on scored rows.** Gives prose reviewers a tree production
  never gave them, approximately dated. The plan forbids this on scored
  rows and I do not recommend it: it measures an affordance no production
  lane has.
- **D. Redraw.** A new seed over the anchored-era change sets (the class
  with exact whole-tree bases: 6,053 production reviews to draw from) and
  the repo-doc corpus, dropping prose from the review instrument until
  striatum pins a base for prose reviews. Loses comparability with the
  20260819 draw entirely; gains an instrument whose every case has an exact
  base.

Recommendation: **A**, with D noted as the shape of the next draw. A keeps
the 69 cases, gives every scored row an honest `base_source`, and turns the
prose class into a measurement of what production reviewers face rather than
of an environment that does not exist.

## Owed before step 3 under any option

- The `exchange-objects` materializer for `RQ-` references (compilation
  requests are in the ledger; receipts are `artifact_admitted` records by
  identity). Escalation 2646 resolves nowhere.
- The contract paragraph (§2.7) rewritten to state, per case, what is
  pinned: "a whole tree", "the product tree the change set declares", or
  "no tree was pinned for this artifact".

Step 3 (label re-derivation) is blocked on the option chosen: under A, the
36 no-tree and partial-tree cases keep their environment-invariant labels
and their reference-resolution labels are re-derived against `evidence/`
only; under B they are simply unscorable.

## Ruling (Principal, council #57, 2026-09-06)

Option A, with conditions, now written into plan §2.3 as an amendment:
`tree-v1` proceeds **production-faithful**. `base_source` is one of
`whole-tree`, `partial-product-tree`, `none-by-design` (prose: production
pinned nothing), or `lost` (change sets whose production base is
unrecoverable). `none-by-design` is an exact statement of the pinned set:
references outside it are unverifiable and not findings, and a binding that
refuses them is measured as a false alarm. `lost` pairs are scorable only
for in-set operators. Exchange objects that resolve go under `evidence/`.
Contrasts are reported per base class as well as pooled, and
reference-resolution cells are pre-registered per class. In §4, a reference
outside a `none-by-design` pinned set is `reference-not-required`. Two
follow-ons: a striatum finding (production prose reviews are world-blind —
`finding-2026-09-06-prose-reviews-world-blind.md`), and the next review seed
is drawn from the 6,053 anchored-era reviews plus the repo-doc corpus, as the
successor to 20260819.
