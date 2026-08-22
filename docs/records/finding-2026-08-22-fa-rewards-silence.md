# Finding — the binary false-alarm metric rewards silence

- Date: 2026-08-22. Raised by the striatum-side handoff (task 3); the
  Principal and its author suspected the measure rather than the model.
- Subject: `or-gemini-3-7-flash-high` reports FA 0.036 against 0.13–0.35
  for every other subject on the identical cases.

## Confirmed: the advantage is emission style, not judgment

Findings emitted per arm, breadth cases, seed 20260819:

| subject | ctrl mean | ctrl zero-finding | mutant mean | mutant zero-finding |
|---|---|---|---|---|
| or-gemini (lane) | **0.04** | **96%** | 0.59 | **45%** |
| agy-flash-high | 0.25 | 82% | 0.98 | 16% |
| agy-flash-medium | 0.25 | 84% | 0.84 | 26% |
| deepseek (lane) | 0.57 | 61% | 1.18 | 30% |
| sol-high | 0.60 | 75% | 1.39 | 2% |
| cc-glm (harness) | 0.79 | 56% | 1.28 | 16% |
| glm (lane) | 1.23 | 36% | 1.79 | 14% |

or-gemini is nearly mute everywhere: 96% of its controls and 45% of its
mutant refusals carry zero findings. A binary refused/cleared metric
scores that silence as judgment. Symmetrically, the chattiest subjects
(glm-lane 1.23 findings per control, deepseek 0.57) buy their catches
with refusals everywhere and wear the FA cost. FA comparisons across
emission styles are confounded; between like-styled subjects they remain
meaningful.

## The emission-robust reading exists and is already on every claim

Anchored detection requires naming the planted defect's anchor:

| subject | catch | anchored |
|---|---|---|
| sol-high | 0.965 | 0.772 |
| agy-flash-high | 0.842 | 0.719 |
| cc-glm | 0.719 | 0.614 |
| agy-flash-medium | 0.719 | 0.596 |
| glm (lane) | 0.571 | 0.554 |
| or-gemini (lane) | 0.554 | 0.500 |
| deepseek (lane) | 0.571 | **0.321** |

Deepseek's gap (0.571 → 0.321) is the scattergun exposed: half its catches
never cite the defect. or-gemini's catches mostly do (0.500/0.554) — its
distortion is confined to the FA axis. Sol's high-FA reading survives:
it names what it catches (0.772) while refusing controls it examines.

## Disposition

- Read **anchored detection first** for any cross-emission-style
  comparison; catch and FA rank only like-styled subjects.
- The leaderboard's comparability note now says so.
- A finding-count metric ("mean findings per control") is worth adding to
  the claim vector in a future instrument revision; the raw data already
  survives in every row.
