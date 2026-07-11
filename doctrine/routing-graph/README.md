# Routing adjacency projection

`links.yaml` is generated from Concept Record `routing.related_concepts` by
`../tools/sync_concepts_to_graph.py`. It records only that two concepts are
eligible for co-retrieval under some route.

Every link has `semantic: false`. A routing link does not claim that either
concept requires, enables, refines, corroborates, or otherwise supports the
other, and it must never cite source formulations as evidence for such a
relationship. Evidence-backed engineering relationships remain exclusively in
`../graph/edges.yaml`.
