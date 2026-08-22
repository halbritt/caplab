# The second harness pair: same direction, weaker, not established

- Date: 2026-08-22
- Pair: `cc-glm-5-3-max` (claude-code harness via Z.ai, workspace + shell,
  arg transport) versus `glm-5-3-max` (one-shot lane, stdin). Same model,
  same max effort, same seed-20260819 cases. Second family in the
  harness-effect design after the gemini pair
  (`report-2026-08-22-harness-effect-gemini.md`).
- Harness run: **69/69 usable** — including the 4.4 MB change set every
  lane discards: arg-spill materializes it as a file the agentic subject
  reads. No aborts.

## Result

| | lane | harness |
|---|---|---|
| catch (shared 56) | 0.571 | 0.714 |
| discordance | 5 lane-only | 13 harness-only |
| sign test | p = 0.096 — **not established** | |
| breadth discrimination | +0.375 | **+0.544** |
| structural | 14/32 (44%) | 20/33 (61%) |
| semantic | 18/24 (75%) | 21/24 (88%) |
| false alarms | 11 (20%) | 10 (18%) — no FA effect (p = 1.0) |

Direction replicates; significance does not. Two honest readings, and the
record keeps both: mounting helps GLM less than it helps gemini (16–0
there), or n=56 cannot resolve a 13–5 split. The gemini pair remains the
established mounting result; this one is supporting, not confirming.

Unlike the gemini pair, the harness costs GLM nothing in false alarms —
the first pair's tools-buy-detection-on-both-arms pattern did not repeat.

## The lane floor is half affordance

Twelve breadth cases resist every lane-mounted subject (gemini, GLM,
deepseek). The GLM harness caught **6 of the 12**. Half the lane's hard
floor is affordance; the other half stayed uncaught even with tools —
casework for the corpus, and candidate targeted-reproduction cells.

## Placement note (Principal's, not CAPLAB's)

The glm-zai handoff framed this sweep as the held-out split that could make
`cc-glm-5-3-max` review-eligible. Its measured profile — catch 0.719 / FA
0.175 / discrimination 0.544, structural 61% — sits in the flash-medium
band on the same cases. Whether that earns a review class is a declaration
decision; the measurement is now on the ledger either way. Separately, the
`glm-5-3-max` disable rested on a mid-flight n=24 read; the completed run
(disc +0.375, not 0.042) is the evidence that decision should be re-taken
on, in whichever direction.

Artifacts: `advisory/comparisons/cc-glm-vs-glm-lane-20260819.json`; runs
under `advisory/pool-runs/sweep-{cc-,}glm-5-3-max-20260819/`.
