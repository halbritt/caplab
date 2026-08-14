# Assumptions {#el:assumptions}

## Materialized inputs unavailable in this execution lane {#el:inputs-unavailable}

- The prompt's stated working directory (`.../workspaces/bbfb05.../work`) and the
  materialized inputs it references (`inputs/00-base-pin`, `inputs/01-base`,
  `inputs/02-work-graph`) were **not present** in this environment; the actual
  working directory was empty. I therefore reviewed against the fully inlined
  change-set body, the inlined `review-work-graph-context`, the inlined
  environment excerpts, and the **sealed mechanical context** in the pass header
  (which already reports `base_materialization_succeeded`,
  `materialized_base_matches_derived`, `result_derivation_succeeded`,
  `derived_result_matches_declared`, and `packet_element_matches_declared` all
  true). I did not independently recompute any content hash; the mechanical
  layer's hash equalities were taken as given, per the review context note.

## Live checkout used as a proxy for base-state facts {#el:base-proxy}

- To verify structural facts the change-set depends on but that live outside the
  inlined diff, I cross-referenced the live checkout at
  `/home/halbritt/git/striatum-next` as a proxy for the anchored base
  (`a0354e59…`). This established, and I assumed carries to the actual base:
  - the base catalog holds exactly **12 passes** and no `subject-assembly.yaml`
    (so this packet yields 13 and the README's "thirteen" is correct);
  - `catalog/passes/build.yaml` is **contract_version 3** and is not modified by
    this packet (matching `TestSubjectAssemblyDoesNotBranchBuild`);
  - `productCatalog` is a package-level `const` in
    `internal/driver/catalog_overlay_test.go` (outside this packet's write
    scope), so the new test file's references resolve;
  - none of the new test's functions/helpers (`TestCatalogReadmePassCountIsCurrent`,
    `producersOf`, `containsWord`, `spelledCounts`, etc.) collide with existing
    `driver_test` declarations;
  - `internal/driver/catalog.go`'s `ProducerOf` body is byte-identical to base
    (the change-set's edit is comment-only);
  - `schema/pass.schema.json` is a Phase-0 placeholder (`additionalProperties:
    true`) with no Go test validating pass files against it.
- The `code` acceptance check (which runs these guards at verification) is the
  mechanical backstop for any base-count drift; my review judged coherence given
  the declared base, and the self-checking `TestCatalogReadmePassCountIsCurrent`
  guard would catch a genuine count mismatch at that gate rather than in review.
