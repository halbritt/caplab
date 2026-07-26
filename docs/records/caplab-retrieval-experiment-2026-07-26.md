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
| embedding over lesson text (title + claim + decision_rule) | 0 / 10 |
| embedding over lesson + `common_failure_modes` + `why_it_matters` | **3 / 10** |
| **repository signals supplied to existing nomination** | **3 / 3** (separate run) |

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

Embeddings are a partial improvement (0/10 → 3/10) and not the main lever.
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

## Locators

- Corpus: 227 concepts, `doctrine/concepts/*.yaml`, pinned release at
  `~/.local/share/pincite/release`.
- Baseline exhibit and raw packets: `caplab-82-recall-exhibit-2026-07-25.*`.
- Worlds and captures: campaign custody
  `~/.local/share/caplab/campaigns/advisory-selection-001-shakedown-2026-07-26/`.
