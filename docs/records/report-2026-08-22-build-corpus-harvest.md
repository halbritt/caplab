# The build construct exists: 3,089 mechanically-labelled attempts harvested

- Date: 2026-08-22. Task 1 of the striatum-side handoff (`/tmp/caplab-next-three.md`).
- Construct: **`build.packet_delivery/1`** — CAPLAB's first build construct,
  defined in `caplab.advisory.build_corpus`. Metrics:
  `packet_checks_pass_rate` (mechanical format/compile/test label) and
  `delivery_rate` (runs closed `submitted`, deferrals excluded), each with
  Wilson CIs and `n_pairs`.
- Custody: **`striatum-production`** — a third custody class, registered in
  quartermaster's schema: evidence executed and labelled by striatum's own
  production loop, harvested and scored by CAPLAB. No judgment is in the
  labelling loop, which is what makes build harvestable where review needed
  Revbench to manufacture ground truth.
- Source: the striatum ledger (253,757 records; sha256 pinned on every
  claim; the >200k line guard is enforced in code because `ledger cat` can
  return empty under lock contention — observed twice during this harvest).

## The reconciliation, and what it reveals

The handoff counted 2,160 pass / 2,547 fail. The harvest reproduces it
exactly — and decomposes it: **2,163 pass / 926 builder failures / 1,621
tree-moved exclusions**. The handoff's fail count was 64% base churn:
`packet-checks` failures whose detail carries `tree moved: rebase-style
revision required`, meaning an operator commit moved the anchored base
under the in-flight build. Scored as builder failures they would have
roughly tripled every backend's apparent failure rate. They are excluded
and counted, never silently dropped; capacity deferrals likewise leave the
delivery denominator (the freeze-guard weeks made both exclusions large).

## Headline build ranking (floor n≥10; 20 ranked, 17 below floor)

| rank | Binding | checks-pass | n | delivery |
|---|---|---|---|---|
| 1 | agy-gemini-3-7-flash-high | 87.5% | 535 | 99.6% |
| 2 | codex-sol-high | 82.0% | 172 | 97.4% |
| 3 | agy-gemini-3-7-flash-medium | 78.5% | 195 | 99.4% |
| 4 | codex-sol-xhigh | 78.9% | 242 | 98.7% |
| 5 | codex-sol-medium | 72.7% | 44 | 100% |
| 6 | codex-sol-max | 77.0% | 579 | 92.3% |
| … | claude-harm-sonnet-5-high | **33.5%** | 400 | 86.7% |

37 claims ledgered and ingested; the draft build objective's placeholder
construct is replaced with the real definition (its own text invited
exactly that). Build and review constructs are deliberately separate:
flash-high leading both is a finding, not an assumption.

## Proposed quality-class floors (the flag back to striatum)

`minimum_quality: strong` currently gates adversarial review against a
threshold nobody has written down. CAPLAB's proposal, defined **per
instrument** on `review.defect_discrimination/1`, synthetic-contract
profile, n ≥ 40 pairs:

- **frontier**: discrimination ≥ 0.70 AND anchored_detection ≥ 0.70
- **strong**: discrimination ≥ 0.50 AND anchored_detection ≥ 0.55
- **baseline**: everything else
- CI guard: grant only when the conservative bound (Wilson 95% lower bound
  of catch minus Wilson 95% upper bound of FA) clears the floor − 0.10;
  a claim whose FA audit status is `contains-unaudited-refusals` on more
  than 20% of controls can hold a class but not newly earn one.

Fit against the measured cohort: sol-high (0.768/0.772) → frontier;
flash-high (0.681/0.719) → **strong on this instrument** — its declared
frontier class rests on the 20260815 dispatch-prompt measurement (0.773),
and cross-instrument classes should be re-based, not mixed; cc-glm
(0.541/0.614) → strong; flash-medium (0.576/0.596) → strong; every lane
tuple → baseline. Anchored detection is in the rule deliberately: the
2026-08-22 silence finding shows binary FA rewards muteness, and anchored
is the emission-robust axis. Adoption is striatum's; the floor is now
written down.
