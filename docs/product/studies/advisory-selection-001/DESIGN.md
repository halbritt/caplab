# advisory-selection-001 — two-part design

## Slate

20 concepts drawn at random from the 227-concept corpus
(`random.seed(20260729)`, `random.sample`) — see
[`concept-slate-20.md`](concept-slate-20.md). Random rather than chosen, so the
slate is representative of the corpus and not of what looks testable.

One scenario per concept, 20 in total, each built so that concept's lesson is
the correct approach.

## Part 1 — retrieval (zero model calls)

**Does the scenario yield its own concept on retrieval?**

Run each scenario's `TASK.md` through the pinned Pincite release and record
whether the target concept appears in the served packet. Deterministic,
offline, trace disabled; no model calls and no served-doctrine record touched.

Two conditions this measurement depends on:

- **Task text authored blind** to the concept's `retrieval_terms` and `routing`
  fields, or the measurement is circular.
- **Scored on the variable slots only.** Six always-load concepts appear in
  every packet regardless of query; scoring against the whole packet makes any
  of them a trivial hit. Two of the 20 are always-load and are excluded from
  part 1 — **18 eligible**.

Result is a hit/miss stratification over the slate, and a recall figure for
Pincite on fresh, naturally-worded tasks. Prior measurement on ten ad-hoc
queries was **0/10**; this slate is a better instrument for the same question
because it is randomly drawn.

## Part 2 — behaviour (model calls)

For each scenario, does serving the concept change what the agent does?

Part 1 stratifies part 2: scenarios where retrieval hits test the product
end-to-end; scenarios where it misses test whether the concept helps *when
delivered*, which retrieval currently cannot do. That separation is what
distinguishes "the corpus is inert" from "routing is broken" — the two have
opposite remedies.

Arms and power are not frozen. Nothing proceeds to part 2 before a scenario's
headroom is **measured**.

## What is already known and constrains this

| finding | consequence |
|---|---|
| Retrieval served the target 0/10 on naturally-worded tasks | expect a low part-1 hit rate; that is a result, not a failure |
| Repository signals recovered 3/3 blind, and 5/11→7/11 on real commits | part 1 should record signal-augmented retrieval as a second condition |
| Vector search reached 0–3/10 across five configurations | not a substitute for routing |
| 2 of 3 prior scenarios were at ceiling or floor | headroom must be measured before admission |
| 12-rung ladder did not order performance monotonically | capability may be the wrong axis; do not assume a frontier |
