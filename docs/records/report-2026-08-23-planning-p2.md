# Planning P2: the corpus exists and the pipeline closes

- Date: 2026-08-23. Phases P1–P2 of `planning-constructs-v1.md`.
- **P1 (striatum agent):** `striatum-plan-oracle 1` (`03f0cc3`), verified
  against the contract end-to-end — stdin and `-graph`, degradation
  statuses, verdicts never in exit codes, full JSON on a real production
  graph with `-registry` and `-tree`.
- **P2 (this record):** `caplab.advisory.planning_corpus` — harvest,
  retention, contract, extraction, normalization, oracle scoring.

## The corpus

All **338 of 338** bound implementation-planning dispatches survive on the
exchange — zero reaped. Task registry: `advisory/planning-tasks.jsonl`
(dispatch, step, production backend and outcome, input hashes); every
input body retained in the advisory CAS (573 MB total store after
dedup — the shared base trees collapse). 160 tasks fit an inline prompt
(≤180 KB); the other 178 carry full base trees and need the
spill-to-workspace transport — planning is tool-hungry, as the card
predicted, so the mounting axis is built into the corpus itself.

## Instrument facts the smoke test established

1. Modern ledger artifact bodies are CAS pointers (zstd objects in the
   exchange CAS); the harvester reads them natively.
2. The planning contract (`plan-v1`, PLAN ONLY preamble) must carry the
   exact work-graph skeleton: the parser rejects unknown fields, and the
   real schema has sharp edges (`derived_from` is a string; the plan pin
   demands a 64-char hash). Two prompt iterations were caught by the
   oracle itself — the instrument debugging its own contract.
3. The plan pin (identity/version_seq/content_hash) is driver bookkeeping
   a subject cannot know: `normalize_graph` stamps it harness-side,
   passes the subject's index/packets through untouched, and the
   normalization is recorded on every scored document.
4. End-to-end verdict on one live task (gemini-3.7-flash, vertex lane,
   sandboxed): parse/index/legality all pass, 6/6 acceptance checks
   resolve — and the produced plan is a pure depth-6 chain,
   depth×width 6, maximal ancestor-cascade cost. The first data point is
   already the construct's point.

## Next (P2b)

The qualification sweep: a fixed task draw (seeded, class-balanced by
step kind), each candidate tuple planning each task once, oracle verdicts
aggregated into `planning.finishability/1` claims with the oracle binary
sha256 pinned. Spill transport for the 178 large tasks; lane subjects
measurable on the 160 inline tasks with the limitation named.
