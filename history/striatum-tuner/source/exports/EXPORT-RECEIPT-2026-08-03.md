# Corpus export receipt — 2026-08-03

**Principal export direction (verbatim, 2026-08-03):** "make a pastebin to the
analysis, export the corpus and define the predicate"

This receipt records the explicit Principal direction that
`catalog/target-states/judgments-become-a-corpus.yaml` (striatum-next) requires
before any judgment-bearing corpus leaves this box ("local-first, no export
without explicit direction"). The direction was given in the operator session
that produced `docs/DRIVER_TUNING_FEASIBILITY_2026-08-03.md`, in response to
that analysis naming the export ruling as a Principal-only decision.

## What is exported

`corpus-driver-v2-2026-08-03.tar.zst` — the driver-role transcript corpus
(corpus v2, built by `extract_driver.py` at commit 563df7b):

- `corpus-driver/sessions.jsonl` — 6,100 transcript files indexed; 675 driver
  sessions (40 claude / 42 claude-harm / 593 codex)
- `corpus-driver/events.jsonl` — ~530k normalized events from driver sessions
- `corpus-driver/striatum_calls.jsonl` — 18,063 striatum CLI invocations
  (10,484 modern-dialect + 7,579 legacy-dialect), including resolve
  `--disposition`/`--note` adjudication text
- `corpus-driver/stats.json` — extraction summary

SHA-256 hashes: `SHA256SUMS` (bundle + members). Bundle size: 130,240,322 bytes.

## Sensitivity note

The corpus contains Principal adjudication notes, operator reasoning, and
transcript excerpts from all three agent harnesses. It is licensed by the
direction above for **training use** (the driver-tuning arc of the analysis
doc — e.g. upload under a hash-pinned runpod-jobrunner manifest for a tuning
job). It is not licensed for publication or any third-party sharing beyond the
training infrastructure.

## Scope going forward

The same direction covers the future pass-produced adjudication corpus named by
`judgments-become-a-corpus@1` (dossier-shaped training pairs), which supersedes
this transcript-grain corpus for decision-grain training when delivered. Each
actual off-box upload should still land in a job manifest (hash-pinned, like
`jobs/qwen35b_moe/`) so the export trail stays receipt-shaped.
