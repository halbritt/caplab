# Planner ranking: Council disposition and what changed

- Date: 2026-09-04. The Principal handed CAPLAB the Council synthesis
  `~/council-artifacts/caplab/synthesis-2026-09-04-planner-ranking.md`
  (sha256 `c618e402c39520f4…`; scribe fable; members agy, sol, deepseek,
  glm; qwen-chair failed both turns) as the disposition of
  `planner-evaluation-v1.md`. This record says what the synthesis decided,
  what was done in response the same day, and what remains the Principal's.

## The disposition, in one paragraph

The design's diagnosis and hygiene are right; the ranking it proposes
answers the wrong question. Striatum must absorb weekly model churn, any
frontier planner is probably adequate, and the failure worth paying to
detect is a defective or regressed backend. So: **park the pairwise
tournament** (L1 and its 5,376-call run), keep its assets, and replace it
with a per-binding **admission gate** (pass/fail, mechanical where possible),
**operational routing** among admitted bindings in Quartermaster, and
**production canaries** with a per-producer first-pass floor. Keep judge
spend on review and Arm 2, where mechanical ground truth separates bindings.
Un-park L1 only if production telemetry shows planner-attributable variation
between admitted bindings — and then as a projection for a prefer list,
never a placement gate.

## Defects the Council found, and the author's position

All accepted. Corrections are marked inline in the design (`status: parked`)
and listed in its §12.

1. **The calibration proved the wrong thing.** 714 calls showed judges detect
   gross injected defects against an intact control. L1 asks judges to order
   two intact, admissible graphs. No clean-vs-clean measurement exists.
2. **Size neutrality was overstated.** In every size probe the larger-or-
   smaller graph was also the defective one; 68/68 is defect detection with
   size varying. `prefers_larger_share` 0.457 is the probe mix (16/35), not a
   measurement. H4 belongs first.
3. **The jury did not deliver two families per pair.** With codex down,
   Gemini 3.7 Flash was the only judge eligible for every pair, and
   Claude-vs-GLM pairs (6 of 28) had Gemini alone.
4. **H1 was underpowered as written** (ρ ≥ 0.6 with interval excluding 0
   needs ρ ≈ 0.74 at n=8; four L2 tasks is ~20 packets per planner).
5. **Transport and rubric v2 are prerequisites**, not sequence items (21/180
   pairs dropped; GLM 5/13 on the class whose registry index the judge never
   saw).
6. **The system design narrated the proposal in the present tense.** Fixed.
7. **The construct is a composite no production lane performs**, which
   bounds placement validity — already on the claims, restated.

## Done today

- `doc/designs/caplab-system-design.md` §4.3 rewritten: the planning
  construct is described as the gate it is; the three-layer ranking as
  proposed and parked; what exists in code named.
- `docs/product/designs/planner-evaluation-v1.md`: `status: parked`,
  disposition banner, three inline corrections, §12 disposition.
- `docs/product/designs/planning-admission-gate-v1.md` (**proposed**): Probe
  A tree-mounted finishability on a fixed 12-task draw (floor ≥ 10/12
  proposed); Probe B the nine audited operators as **reviewer** probes under
  a `plan-review-v1` contract (36 pairs, catch/FA with Wilson, floors
  proposed); Probe C optional 5-task execution canary on one fixed executor;
  Probe D optional single-judge sanity pass. Admission is a Principal
  decision on the claims; all admitted bindings are equivalent for planning.
- `scripts/planning_production_fate.py`: the §3.3 covariate table from a
  ledger dump. First run, on 373,371 events, below.
- The review sweeps that were running closed: fable 5.1 69/69 and GLM-flash
  69/69, claims `qc-6504bb1fb3728992` and `qc-ca04644b2e37dd52`
  (`report-2026-09-03-review-sweeps-fable-glm.md`). Judge spend on review,
  as the Council asked.

## The production fate table (covariate, not a claim)

Per producer of accepted implementation plans, the fate of the packets
under the same pass prefix. Attribution is by prefix to the latest accepted
plan before the packet's gate fired; scheduler-routed, different tasks per
producer, different builders per packet. `unattributed` is packets whose
pass had no accepted plan on record before they were checked.

| producer | plans | accepted | finishability p/f | plan-review p/f | acceptance p/f | packets | first-pass | checks/packet | packet-review fail | quarantines |
|---|---|---|---|---|---|---|---|---|---|---|
| `codex-sol-high` | 159 | 55 | 123/37 | 109/1 | 57/9 | 88 | **0.94** | 8.97 | 0.04 | 0 |
| `codex-terra-max` | 103 | 42 | 46/24 | 66/14 | 43/34 | 142 | 0.77 | 21.85 | 0.24 | 0 |
| `claude-harm-opus-5-high` | 67 | 7 | 9/25 | 7/34 | 7/2 | 31 | 0.81 | 71.74 | 0.10 | 0 |
| `claude-code` (generic era) | 53 | 2 | 0/0 | 19/30 | 15/10 | 14 | 0.64 | 14.50 | 0.72 | 0 |
| `claude-opus-5-high` | 3 | 2 | 2/0 | 2/0 | 2/0 | 8 | 1.00 | 1.50 | 0.00 | 0 |
| `unattributed` | — | — | — | — | — | 134 | 0.75 | 4.04 | 0.34 | 0 |

Read with care. `checks/packet` counts every `packet-checks` result on a
packet, including re-evaluations that are not rebuilds, so it is churn, not
rework; a rebuild-only count is owed. `claude-harm-opus-5-high` planned 67
times and had 7 plans accepted (finishability 9/25, review 7/34): most of
its plans never reached packets, so its packet numbers describe a small,
survivor-selected set. Sol's 0.94 first-pass on 88 packets and 109/1 on
plan review is the one strong signal here, and it matches the Tier B read
of 2026-08-23. None of this is a qualification basis; it is what the
Council's canary would be watching, and it is what would un-park L1 if
producers ever diverged on it after randomized routing.

## Still the Principal's

1. Specify the admission gate on the card (or not), with floors.
2. Authorize `plan-review-v1` and one Probe B run on the eight board
   bindings to set floors on evidence.
3. Whether to spend ~450 judge calls on the clean-pair diagnostic over the
   stored graphs, to retire the tournament on data. Optional; nothing
   depends on it.
4. Hand the canary (shadow slice, exploration share, first-pass floor) to
   striatum as a request; CAPLAB supplies the fate harvest.
5. `codex-sol-high` is back (PROBE-OK); its return to any jury is a
   decision, not a default.
