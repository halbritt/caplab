# Canonical Doctrine Graph

This graph is a repository-native semantic projection of the mined corpus. It is
stored as plain YAML so humans can review diffs and agents can retrieve bounded
subgraphs without specialized graph infrastructure.

## Files

- `index.yaml`: graph version, file manifest, node kinds, relation vocabulary,
  and retrieval rules;
- `nodes.yaml`: canonical engineering concepts and operational constructs;
- `formulations.yaml`: source-specific paraphrases with exact chapter/heading
  locators and their relationship to a canonical node;
- `edges.yaml`: typed relationships between nodes, each with formulation-level
  provenance;
- `views.yaml`: curated entry nodes for roles, tasks, and common decisions.

`../tools/sync_concepts_to_graph.py --write` adds any missing Concept Record,
typed source-support projection, and routing-composition edge while retaining
curated graph material. `--check` is the release gate for a missing projection.

## Canonicalization rules

1. Merge source formulations only when they govern the same operational decision
   with compatible applicability and evidence rules.
2. Preserve a formulation separately when it adds a condition, proof obligation,
   mechanism, or counterexample; link it as `refinement`, not silent consensus.
3. Preserve genuine disagreement with `in-tension-with` or `contradicts` edges and
   a `conflict_ref`. State whether the difference is contextual, terminological,
   historical, methodological, or substantive.
4. Do not make a source's terminology the canonical label merely because the
   source is prominent. Choose stable role- and language-neutral names when the
   operational rule is broader.
5. Do not generalize a language-specific mechanism into a universal node without
   independent language-neutral support. Link it with `specializes`.
6. Every node and edge must cite at least one source formulation. Pure task-policy
   rules can remain in the doctrinal library but are excluded from the corpus
   graph until a chapter supports them.

## Provenance relations

- `direct_support`: the source chapter explicitly advances the canonical rule.
- `corroboration`: the source independently supports the same rule or result.
- `refinement`: the source adds operational conditions, mechanics, limitations,
  or a narrower specialization.
- `derived_inference`: the canonical rule follows from source evidence but is not
  stated directly; the inference and alternatives must be recorded.
- `terminology_variant`: the source names substantially the same operational idea
  differently.
- `historical_precursor`: the source offers an older formulation whose assumptions
  or technology differ materially.
- `tension`: the source supports a competing position preserved in the conflict
  registry.

## Edge interpretation

Edges are directional unless their relation is documented as symmetric in
`index.yaml`. An edge states an operational claim, not mere topical similarity.
For example, `characterization-surfaces --enables--> safe-structural-change`
means that captured behavior creates feedback required for a bounded change; it
does not mean the two concepts simply co-occur in a chapter.

Every edge carries `provenance`, a list of formulation IDs. A synthesized edge
may combine formulations from several sources, but its confidence and derivation
must remain explicit. Unsupported convenience edges are invalid.

## Retrieval

Use `views.yaml` for common entry points. Traverse only relations relevant to the
decision and respect the linked Concept Record's routing metadata. Conflict
edges require loading their `conflict_ref`; a retriever must not pick one side
without evaluating the recorded evidence conditions.
