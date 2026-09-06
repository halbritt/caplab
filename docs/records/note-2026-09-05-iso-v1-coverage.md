# iso-v1 review cohort: what is on it, what is not, and the Artificial Analysis top ten

- Date: 2026-09-05. Answer to the Principal's coverage question. The iso-v1
  cohort (`caplab-advisory · synthetic-contract · seed 20260819 · iso-v1`) is
  the only review cohort whose numbers compare today.

## On the cohort (7, plus one running)

`agy-gemini-3-8-flash-high`, `claude-fable-5-1-high`, `agy-gemini-3-7-flash-high`,
`or-gemini-3-7-flash-high`, `cc-glm-5-3-max`, `oc-glm-5-3`, `cc-glm-5-3-flash-high`.
`codex-sol-high` is sweeping now (launched 2026-09-05, 2 lanes).

## Measured on the same seed before isolation, never under it

The pre-isolation seed-20260819 cohort had twelve subjects. Five have no
isolation measurement: `agy-gemini-3-7-flash-medium` (+0.58 pre-iso),
`oc-deepseek-v4-flash` (+0.38), `glm-5-3-max` lane (+0.37), `or-ox-alpha`
(+0.34), `oc-deepseek-v4-pro` (+0.29), `deepseek-v4-flash` lane (+0.23).
Isolation moved catch by up to ~25 points on the pairs that were
re-measured, so none of these numbers sits beside the standing table.

## Never on the 20260819 draw at all

`claude-harm-fable-5-high` (+0.66 on seed 20260817, the fleet's declared
frontier reviewer until 2026-08-22), `codex-harm-sol-high` (+0.26 on the
clean 20260823 change-set draw), `claude-sonnet-5-high` (+0.14, dispatch
0815), `agy-gemini-3-7-flash-low`, and every tuple from the 2026-08 tuner
sweep (all claude-opus-5 / opus-4.8 / sonnet-5 efforts, codex-luna /
sol / terra efforts, kimi-k3, glm, local-qwen).

## Against the Artificial Analysis Intelligence Index top ten (read 2026-09-05)

| AA rank | model (effort) | index | fleet binding | on iso-v1? |
|---|---|---|---|---|
| 1 | Claude Fable 5.1 (max) | 57 | `claude-fable-5-1-high` only — max is above the sweep cap | **yes, at high** (+0.57) |
| 2, 3, 7, 10 | GPT-6 Astra (max / xhigh / high / medium) | 55–52 | **none** — no declaration exists on the fleet | no |
| 4, 6 | Claude Opus 5 (max / xhigh) | 54, 53 | `claude-opus-5-high` (+0.42, tuner seed 0807 only); max/xhigh above the cap | no |
| 5 | Claude Fable 5.1 (xhigh) | 54* | above the cap | no |
| 8 | Claude Fable 5 | 53 | `claude-fable-5-high` (+0.57, tuner 0807), `claude-harm-fable-5-high` (+0.66, seed 0817) | no |
| 9 | Muse Spark 1.3 (Meta, max) | 53 | **none** | no |
| 11 | Claude Opus 5 (high) | 52 | `claude-opus-5-high` | no |
| 14 | GPT-5.6 Sol (max) | 51 | `codex-sol-high` (max above the cap) | running, at high |
| 15 | Grok 4.6 (SpaceXAI, high) | 51 | **none** | no |

(* preliminary on the AA page.)

Reading: of the five model families in the AA top ten, the iso-v1 cohort
holds **one** (Fable 5.1, at high rather than max). Two families have
bindings on the fleet that were never measured under isolation — **Opus 5**
and **Fable 5** — and both could be swept today on the claude accounts
(`claude-opus-5-high` on the primary account, `claude-harm-fable-5-high` on
the harm account) at the same cost as the fable 5.1 run (~4 hours across
two session windows). Two families have no binding at all: **GPT-6 Astra**
(whether the codex CLI serves it is untested) and **Muse Spark 1.3**. The AA
index is a model-scoped prior on a different construct; this table says
what is unmeasured, not what would measure well.

## Owed

- Sweeps under iso-v1 for `claude-opus-5-high` and `claude-harm-fable-5-high`
  (bindings exist; supervised — shared claude windows).
- A probe of the codex CLI for a GPT-6 Astra model id before any declaration.
- The five pre-isolation seed-20260819 subjects, if the Principal wants the
  full twelve on one footing (the GLM lane and the two deepseek tuples are
  cheap; oc-deepseek-pro is not).
