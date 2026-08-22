# The harness is worth 28 points of catch — same model, same cases

- Date: 2026-08-22
- Pair: `or-gemini-3-7-flash-high` (one-shot lane, no tools, OpenRouter →
  google-vertex/global, revision `-20260813` at mint) versus
  `agy-gemini-3-7-flash-high` (agy agentic harness, workspace + shell).
  Same model name, same `high` effort, same 69-case seed-20260819 set.
  The fleet's first same-model harness pair.
- Lane run: 68/69 usable (one 4.4 MB change set exceeds the 1M window on a
  transport with no spill path — structurally unmeasurable on a bare lane,
  honestly discarded), no aborts, ~$1.20 total.

## Result

| | lane (no tools) | harness (tools) |
|---|---|---|
| catch (shared 56) | 0.554 | 0.839 |
| discordance | **0** cases lane-only | **16** cases harness-only |
| sign test | p < 0.0001 | |
| structural split | 14/32 (44%) | ~69% |
| semantic split | 17/24 (71%) | ~87% |
| false alarms (shared) | 2 | 9 (p = 0.039) |

Every one of the 16 discordant cases was caught by the harness and missed
by the lane. Zero ran the other way. The mounting — workspace, shell, the
ability to enumerate and compute over the artifact instead of reading a
prompt — is worth ~28 points of catch on the identical model.

**And the false-alarm axis separated for the first time in the campaign's
history** (p = 0.039): the harness refuses more sound work than the lane.
Tools buy detection on both arms — some of it correct, some of it
over-zealous. Every prior contrast compared like-mounted subjects, which
is exactly why this axis never moved before.

## What this reframes

1. **Lane-measured Bindings were never measuring the model alone.** The
   historical bare-lane rows (glm-5.2, deepseek, kimi, local-qwen) carry a
   mounting penalty of unknown size; their structural blindness is at
   least partly affordance, not capability. The deepseek and GLM re-runs
   in flight will quantify whether *any* lane subject escapes it.
2. **Not all of the deficit is the lane.** The lane's structural 44%
   against fable-5-high's 13/33 *with* tools shows mounting is neither
   necessary nor sufficient — the model still matters.
3. **Caveat, standing:** identical model name across surfaces does not
   prove identical weights. OpenRouter served `-20260813`; the Ultra-plan
   build is unknown; sampling defaults differ. "Harness effect" here means
   the whole mounting, serving stack included. The cc-glm-5-3-max vs
   glm-5-3-max pair (in flight) repeats the design on a second family.

## Bookkeeping

Claim derived and ledgered (68 pairs, seed 20260819 — the cohort's fourth
subject). Contrast:
`advisory/comparisons/or-gemini-vs-agy-gemini-high-20260819.json`. The
lane's discordant cells enter the promotion gate at one sweep. Follow-ups
noted: stdin transport needs a loud capacity refusal (arg mode has one);
the supervisor should not re-release deterministic transport failures.
