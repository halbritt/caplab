# The GLM triplet: harness presence moves catch; harness choice does not

- Date: 2026-08-23. Completes the three-mounting design: one model
  (GLM-5.3, max effort) measured bare-lane, claude-code-harness, and
  opencode-harness on the identical seed-20260819 cases. oc-glm ran 69/69
  usable (opencode's arg transport measures the 4.4 MB case).

## The harness-quality contrast (both agentic)

| | oc-glm | cc-glm |
|---|---|---|
| catch (shared 57) | 0.719 | 0.719 |
| discordance | 5–5, p = 1.000 | |
| structural | 20/33 | 20/33 |
| semantic | 21/24 | 21/24 |
| false alarms | 17 | 10 (p = 0.065) |
| discrimination | +0.421 | +0.541 |

Detection is indistinguishable — identical catch, identical splits, no
directional discordance. The Principal's pre-registered concern ("if
oc-GLM differentiates from cc-GLM, I am going to have questions") is
answered: it does not, on any detection axis. The marginal difference is
temperament — oc-glm refuses more sound work (plumbing suspects: opencode
sends no effort pin where cc pins max; different Z.ai API surface;
different scaffolding) — and temperament, per the production-review study,
is exactly the axis mountings and configs shift.

## The mounting contrast (agentic vs lane), second GLM pair

oc-glm vs glm-lane: 14–6 harness-side, p = 0.115; catch 0.714 vs 0.571.
Same direction and size as the cc pair (13–5, p = 0.096), individually
short of significance both times (the two pairs share the lane arm, so
they do not pool). The established mounting result remains the gemini
16–0; GLM's two pairs support it directionally at a smaller effect.

## Standing summary of the mounting design

- Harness **presence**: moves catch (+14 to +28 points across three
  same-model pairs; established at p<0.0001 once, directional twice).
- Harness **choice** (claude-code vs opencode): moves nothing on
  detection; small marginal effect on refusal temperament.
- Lane band: four models, catch 0.536–0.571, structural 41–44%.
