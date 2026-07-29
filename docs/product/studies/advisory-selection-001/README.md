# advisory-selection-001 — study artifacts

Construct: **advisory-responsive approach selection** (CAPLAB-58).
Map: Plane CAPLAB-44. Preregistration:
[`../caplab-advisory-selection-001-preregistration.md`](../caplab-advisory-selection-001-preregistration.md).
Capability card:
[`../../capability-cards/caplab-advisory-selection-001-advisory-responsive-approach-selection.md`](../../capability-cards/caplab-advisory-selection-001-advisory-responsive-approach-selection.md).

## Layout

| path | holds |
|---|---|
| `scenarios/` | one directory per scenario: world, `TASK.md`, target concept, reference solution, headroom evidence |
| `packets/` | rendered arm packets per scenario, content-addressed |
| `codes/` | frozen binary codes with negative space, one file per scenario |
| `campaigns/` | normalized per-campaign results. Raw append-only custody stays outside the repo at `~/.local/share/caplab/campaigns/` |

## Status

**Not preregistered.** No scenario is admitted. Nothing here is frozen.

The prior scenario set (three worlds, ADR-0060 shakedown and ADR-0061 titration)
is **consumed and excluded** — those scenarios were observed, and two of the
three proved uninformative.

## Admission bar for a scenario, derived from measurement

The titration measured unaided competence at every rung of a 12-rung
`gpt-5.6-{luna,terra,sol}` × `{low,medium,high,xhigh}` ladder. Two of three
scenarios could not have shown an effect if one existed:

| scenario | unaided score across all 12 rungs | verdict |
|---|---|---|
| SC-01 duplication | 0.94–1.00 | **ceiling** — solved unaided everywhere |
| SC-02 representation | 0.25–1.00 | usable headroom |
| SC-03 failure policy | 0.00–0.22 | **floor** — solved by nobody |

So a scenario is admitted only if its **unaided score is measured**, not
asserted, and lands away from both bounds. CAPLAB-81 permitted headroom to be
established by citing the target concept's `common_failure_modes`; that
catalogue records what practitioners get wrong, not what current models get
wrong, and it failed on first contact with data.

**Proposed bar:** measured unaided mean in `[0.25, 0.75]` on the intended
subject, `k >= 5`, before the scenario is admitted. The screening arm is
`none` only, so it costs one arm rather than four.

## Constraints carried forward from measurement

- **Codes are validated, not just written.** No predicate may fire on the
  parent tree. Three of seven did, flooring SC-03 and inflating SC-02, and the
  arm means reported from that run were artifacts. `scripts/caplab-scenario-coder.py`
  refuses to run unless validation passes.
- **Dispositions come from structured events.** Provider failure is
  infrastructure, never a behavioural non-attempt. Raw-text matching produced
  false positives from a `429` in a grep's line numbers and from the doctrine
  packet's own prose. See `scripts/caplab-classifier-fixtures.py`.
- **Attestation is per episode.** Codex's non-ephemeral rollout carries
  per-turn `model` and `reasoning_effort`; join it by `thread_id`, never by
  file mtime, which races across parallel lanes.
- **Scope is scored.** Agents edit tests to ratify their own fix; one titration
  episode added a test asserting that logging is correct failure handling.

## Open, before anything is frozen

- The scenario set is the binding constraint, not the design. Prior work had
  one informative scenario out of three.
- The 12-rung ladder did **not** order performance monotonically, and the
  Claude-versus-GPT family gap exceeded every within-ladder difference. Whether
  capability is the right axis is unresolved.
