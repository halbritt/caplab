# Retrieval experiment: nomination vs embeddings vs signals — 2026-07-26

Observations with locators. Zero model calls beyond a local embedder
(`nomic-embed-text` via ollama, 768-dim). Pincite trace disabled throughout;
no served-doctrine record touched. CAPLAB reports; Pincite adjudicates its own
routing policy.

## Question

Ten task descriptions were authored in consumer register, blind to every
target concept's `retrieval_terms`. Each has a known correct concept. How well
does each retrieval method find it, at a packet size of 14?

## Results

| method | recall@14 |
|---|---|
| current nomination, question only | **0 / 10** |
| vector: lesson text only | 0 / 10 |
| vector: lesson + `common_failure_modes` + `why_it_matters` | 2–3 / 10 |
| vector: same, with `search_query:`/`search_document:` prefixes | 2 / 10 |
| vector: per-field chunks + prefixes, max-pooled | 1 / 10 |
| **repository signals supplied to existing nomination** | **3 / 3** (separate run) |

**Do not rank the vector variants against each other.** At n = 10 queries a
one- or two-hit difference is sampling variation. Two runs of the closest-
equivalent configuration returned 3/10 and 2/10. The supported statement is
that *every* vector configuration tried lands in the 0–3/10 band at packet
size, and none approaches usable.

Applying nomic's documented asymmetric prefixes and per-field chunking — both
expected to help — did **not** improve recall. That is evidence the ceiling is
in the task, not in the retrieval recipe.

Adding source code to the embedded query, on the three built worlds:

| world | target | rank, query only | rank, query + code |
|---|---|---|---|
| SC-01 | `implementation-duplication-as-evidence` | 219 | **217** |
| SC-02 | `implementation-representation-fit` | 33 | **20** |
| SC-03 | `implementation-explicit-failure-policy` | 31 | **10** |

## The finding

**Retrieval difficulty tracks whether the concept names a topic or a structural
property.**

- **Topical concepts** — error handling, memory, concurrency — have lexical and
  semantic traces in both the symptom and the code. Embeddings reach them:
  SC-03 improved 31 → 10 once the code was included, because the code contains
  `except Exception: pass`.
- **Structural concepts** — duplication, coupling, layering — have no topical
  trace. SC-01's code contains three copies of one timeout constant, and the
  target concept is *about duplication*, yet it ranks 217 of 227 with the code
  supplied. **The code does not talk about duplication; it exhibits it.**
  Similarity search cannot see a property that is never mentioned.

This also explains why some queries are unroutable in principle. S01 reads
"staging still times out after 30 seconds even though we raised the limit to
120." Nothing in that sentence indicates duplication. A human expert could not
route it either. The routing information does not exist in the query.

## Implication

Vector search is at best a marginal improvement over nomination (0/10 → 2–3/10,
within noise of each other) and is not the main lever.
The measured winner is **supplying repository signals to the nomination
machinery that already exists** — 3/3, using Pincite's own
`activate_for_repository_signals` axis, with the packet staying at 14 concepts
because the existing budget displaced lower-ranked members automatically.

The gap is that nothing currently *computes* those signals; a caller must
already know to supply "coordinated edits" or "materialization". That points at
a signal-extraction step over the repository and task — structural analysis for
structural concepts, lexical or semantic for topical ones — feeding the routing
axis that already works, rather than replacing nomination with similarity
search.

A hybrid is the natural shape: embeddings for topical concepts, computed
structural signals for the rest.

## Limits

One embedding model was tested (`nomic-embed-text`, 768-dim), because it is
what is installed locally. A larger or code-aware embedder could plausibly
improve the topical concepts and the 2/10 figure may be understated. It would
not be expected to change S01 or S06: no similarity function retrieves a
property the text never mentions.

Consistent across all five vector configurations: S01 ranked 215/217/221/219
and S06 ranked 203/195/213 out of 227. That stability, not the small
differences between variants, is the load-bearing observation.

## Locators

- Corpus: 227 concepts, `doctrine/concepts/*.yaml`, pinned release at
  `~/.local/share/pincite/release`.
- Baseline exhibit and raw packets: `caplab-82-recall-exhibit-2026-07-25.*`.
- Worlds and captures: campaign custody
  `~/.local/share/caplab/campaigns/advisory-selection-001-shakedown-2026-07-26/`.
