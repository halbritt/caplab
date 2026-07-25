# CAPLAB-82 exhibit — targeted retrieval recall on authored scenarios, 2026-07-25

Observation with an evidence locator. No inference about Pincite's nomination
policy is recorded here, and no Pincite artifact was modified.

## Method

Ten scenarios authored in consumer register, each targeting one corpus concept
and citing the `common_failure_modes` entry it is built to elicit (CAPLAB-81).
Task text was authored **blind to every target concept's `retrieval_terms` and
`routing` fields**, so the measurement is not circular.

Each was run through the pinned release binary
`~/.local/share/pincite/release/doctrine/bin/pincite` with `--render none`,
supplying question, role, task-family and language only.
`PINCITE_TRACE_DIR` and `PINCITE_TRACE_SESSION` were unset, per the
`scripts/retro-replay` determinism contract — these are synthetic experimental
retrievals and must not enter the ADR-0019 served-doctrine record.

**Zero model calls. Zero spend.**

Inputs: [`caplab-82-scenarios-2026-07-25.tsv`](caplab-82-scenarios-2026-07-25.tsv).
Raw packets: [`caplab-82-recall-exhibit-2026-07-25.jsonl`](caplab-82-recall-exhibit-2026-07-25.jsonl).

## Result

| measure | result |
|---|---|
| exact target concept served | **0 / 10** |
| near-equivalent served | 1 / 10 (S07 → `python-representation-fit`) |
| distinct activated sets | **4** across 10 scenarios |
| always-load core | **6 concepts present in all 10 packets** |
| scenarios where question text moved the packet | **1** (S07) |

Always-load core observed: `agent-conduct-authority-bounded-action`,
`universal-evidence-before-intervention`, `universal-no-change-option`,
`universal-preserve-behavior-by-default`,
`universal-repository-contract-precedence`,
`universal-separate-semantic-structural-change`.

Variable slots track `(role, task-family, language)`: five scenarios received
byte-identical Python lens blocks, three identical refactoring blocks, one the
performance block.

## Measurement correction this run forced

A naive score reported 2/10, because two scenarios targeted
`universal-no-change-option` — which is always loaded. **Recall must be scored
against the packet's variable slots only**, and a scenario whose target sits in
the always-load core is ineligible: retrieval cannot fail to serve it, so it
carries no information.

## Relation to the retro-replay

The retro-replay reported 12.5% defect-priced recall and caveated it as "a
lower bound tied to minimal-context queries — a single-sentence subject is a
weaker query than a real retrieval (question + signals + observed evidence)."

These tasks are naturally-worded and materially richer than commit subjects,
and targeted recall did not improve. **The caveat is removed for question-text
richness.** It survives for retrieval supplied with signals and observed
evidence, which this run did not exercise.

## Boundary

CAPLAB reports; Pincite adjudicates its own nomination policy, known-miss gate,
and lever priority (CAPLAB-53 authority split). Routed to Pincite as a finding
via CAPLAB-83.
