# advisory-selection-001 — study artifacts

Construct: **advisory-responsive approach selection** (CAPLAB-58).
Map: Plane CAPLAB-44.

[ADR 0065](../../../decisions/adr-0065-advisory-responsive-study-selection.md)
selects the owner's real-retrieval-versus-none question and distinguishes it
from forced-injection diagnostics. The selection is complete; the executable
design, preregistration and admission are not. It does not authorize a campaign.

The completed pre-study agent-system ladder is recorded in
[`LADDER-RESULT.md`](LADDER-RESULT.md). Its result does not preregister or admit
the destination study described below.

The completed campaign's legacy launcher now refuses every new attempt before
creating custody or starting a process. Reopening it requires a new
authorization and an exact, sealed native-provider launcher/runtime bundle;
the historical runner's ambient host environment is not such a bundle.

The [prospective capability card](../../capability-cards/caplab-advisory-selection-001-advisory-responsive-approach-selection.md)
now specifies the construct and claim requirements. It must be explicitly
adopted by a future study and does not amend this study's existing artifacts.
**The preregistration does not exist yet.** Its reserved path remains
`docs/product/studies/caplab-advisory-selection-001-preregistration.md`.
CAPLAB-44's destination is not complete.

The [prospective admission contract](../../contracts/advisory-study-admission-v1.md)
specifies source classes, permitted use, construction provenance and custody
verification. It admits no current scenario and does not generalize the
existing Study 001 admission command.

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
  file mtime, which races across parallel lanes. The shared reader requires
  complete turn contexts with a consistent model/effort tuple and session/CLI
  metadata throughout the supplied capture. Settings alone cannot attest a
  turn; a transient change remains a failure even if later restored. This
  checks the captured bytes, not provider identity or capture completeness.
  See the [reader repair record](../../../records/repair-2026-09-08-rollout-attestation.md).
  Callers must preserve the captured bytes before attesting them and must
  reject custody failures or conflicting existing copies. See the
  [custody repair record](../../../records/repair-2026-09-08-attestation-custody.md).
  Native stdout and stderr stay byte-exact, including partial timeout output;
  timeout facts are separate attempt metadata. See the
  [timeout capture repair](../../../records/repair-2026-09-08-native-timeout-capture.md).
  Usable attempts also require one unambiguous native thread and turn with a
  final completion event and no failure evidence. A valid answer file alone
  cannot satisfy this [completion gate](../../../records/repair-2026-09-08-native-completion.md).
  Artifact judgments are derived from the final captured agent message; the
  separate answer file must agree. Each new judgment retains the selected
  event, item, and hashes in its
  [derivation record](../../../records/repair-2026-09-08-rater-message-derivation.md).
  New attempt records describe validation; `accepted.json` marks publication
  and names the supporting record hash. Interrupted publication resumes from
  custody under the [publication contract](../../../records/repair-2026-09-08-rater-publication.md).
  Calibration evaluation and cached reuse verify published identity and raw
  evidence before using a judgment. New CLI results retain input hashes;
  supported legacy receipts are checked read-only under the
  [evaluation contract](../../../records/repair-2026-09-08-calibration-evidence-read.md).
- **Scope is scored.** Agents edit tests to ratify their own fix; one titration
  episode added a test asserting that logging is correct failure handling.

## Open, before anything is frozen

- The scenario set is the binding constraint, not the design. Prior work had
  one informative scenario out of three.
- The 12-rung ladder did **not** order performance monotonically, and the
  Claude-versus-GPT family gap exceeded every within-ladder difference. Whether
  capability is the right axis is unresolved.
