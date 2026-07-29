# Scenario 12 — `operations-ephemeral-instance-design`

**Target concept:** `operations-ephemeral-instance-design` (operations)
**Concept title:** Treat instance identity, storage, and clock as ephemeral
**Retrieval-eligible:** yes

## Status

Not authored. Not admitted.

## Required artifacts

- [ ] `world/` — small, self-contained, buildable repository; tests green, defect latent
- [ ] `TASK.md` — the symptom, in consumer register
- [ ] `reference.md` — a solution exhibiting this concept's lesson
- [ ] `codes.json` — 2–4 binary codes, negative space stated, validated not to fire on `world/`
- [ ] `headroom.json` — **measured** unaided score, `none` arm, k >= 5

## Authoring constraint (part 1 depends on it)

`TASK.md` must be written **blind to this concept's `retrieval_terms` and
`routing` fields**. Author from the *situation* the doctrine addresses, in the
register a user or operator would use. Consulting the retrieval vocabulary
makes part 1 circular — it would measure whether Pincite retrieves words that
were fed to it.

## Admission

Admitted only when measured unaided competence lands in `[0.25, 0.75]`.
Ceiling and floor scenarios cannot show an effect: of the three prior
scenarios, one scored 0.94–1.00 unaided at every rung and another 0.00–0.22.
