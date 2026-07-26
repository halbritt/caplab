# Retrieval re-baseline and blind signal extraction — 2026-07-26

Observations with locators. Zero model calls. Pincite trace disabled; no
served-doctrine record touched. CAPLAB reports; Pincite adjudicates its own
routing policy and gate state.

## Method

The 11 ranking-miss rows from the 2026-07-22 retro-replay carry ground-truthed
pairs: commit subject → the concept that should have served. Each subject was
replayed against the **current** pinned release
(`corpus-2026-07-12-a11702cc9217`) with `--role coding-agent
--task defect-repair`, question only. Then again with repository signals
produced by `scripts/pincite-signal-extract`, which analyses the parent tree
**blind to the target concept**.

## Result

| condition | target served |
|---|---|
| recorded 2026-07-22 | **0 / 11** |
| current corpus, question only | **5 / 11** |
| current corpus + blind extracted signals | **7 / 11** |

Per row:

| repo | commit | target | Q-only | Q+signals |
|---|---|---|---|---|
| engram | `7327b56e24` | representation-fit | miss | miss |
| engram | `adac16507a` | readiness | **HIT** | **miss** |
| engram | `23f495f28e` | small-verified-steps | miss | miss |
| engram | `307f554e31` | legacy-seams | miss | miss |
| engram | `3c8f8b9b3a` | explicit-failure-policy | HIT | HIT |
| engram | `7432494fa8` | duplication-as-evidence | miss | **HIT** |
| engram | `00e3e27ddd` | anticorruption-layer | miss | miss |
| engram | `44dd3e391b` | duplication-as-evidence | miss | **HIT** |
| engram | `7c33304ad8` | explicit-failure-policy | HIT | HIT |
| engram | `c71c75cddf` | metric-semantics | HIT | HIT |
| pincite | `47fd011f27` | duplication-as-evidence | HIT | HIT |

## Finding 1 — the known-miss gate is stale

Five of eleven rows recorded as ranking-misses now serve their target on
question text alone. The corpus changed after the replay (PINCITE-44 batch
admissions, 2026-07-23) and the replay was not re-run. The replay rows do not
record `corpus_version`, so the drift is not diffable from the artifact —
recording it would make future staleness detectable.

## Finding 2 — signal extraction is not monotonic

`adac16507a` went **HIT → miss** when signals were added. Signals compete for
the same 5000-unit retrieval budget, so supplying more can **displace** a
concept that was already being served. Net movement was 5 → 7: two recoveries,
one regression.

**Any signal-extraction work must be scored on net recall, never on recoveries
alone.** A extractor that recovers three targets while displacing three others
is worthless, and recovery counts alone would report it as a success.

## Finding 3 — four rows resist both

`representation-fit`, `small-verified-steps`, `legacy-seams`,
`anticorruption-layer`. These are the structural-property concepts identified
in the companion record: properties code exhibits rather than mentions. The
current extractor's structural detectors (repeated literals, whole-result
materialisation, broad exception handlers) do not cover them.

## Bound on the value of any of this

Owner-supplied (not admitted evidence): a titration across GPT-5.6 model and
effort tuples, **statically injecting correct doctrine with no retrieval**,
found no behavioural difference for highly capable tuples and a difference
below some point. That is the ceiling for retrieval work: perfect retrieval
cannot exceed perfect injection, and perfect injection is worth zero above the
capability frontier.

Retrieval repair therefore pays only within the band where injection pays.
Locating Striatum's actual placement tuples against that frontier is the
cheaper prior question.

## Locators

- `scripts/pincite-signal-extract` — the blind extractor used here.
- Ranking-miss pairs: `halbritt/pincite`
  `docs/audits/retro-replay-judgments-2026-07-22.jsonl`.
- Companion record: `caplab-retrieval-experiment-2026-07-26.md`.
