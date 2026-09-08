# Usable observations and scheduled slots, version 1

Status: prospective accounting contract selected under the
[CAPLAB-71 decision](../../records/decision-2026-09-08-caplab-71-usable-samples.md).
An adopting study must freeze its own values and assumptions. The numbers below
reproduce a planning example; they are not a new study budget or launch authority.

## Define the count before calculating precision

The analyst must distinguish these quantities for every required world and arm:

| Quantity | Meaning |
|---|---|
| Required usable observations | Complete analysis units needed by the frozen precision or power calculation |
| Scheduled slots | Assigned capacity, including the stated allowance for unusable observations |
| Observed usable observations | Units that actually meet the frozen observation and analysis rules |
| Loss allowance | Its denominator, covered failure classes, scope, and interpretation: expected rate, deterministic bound, or observed stop ceiling |
| Attainment assurance | If claimed, the probability of reaching all required usable counts under an explicitly stated retention model |

State the estimand, analysis unit, allocation, world weighting, code aggregation,
covariance assumptions, effect size, error rate, power or interval target, and
approximation used. Codes from one episode are not independent episodes. Two
scores from one control episode retain their joint covariance. Counts usable
for one contrast need not be usable for a different contrast or a pooled score.

Preserve the
[attempt and unavailable-code rules](behavior-code-authoring-v1.md#6-preserve-attempt-denominators-and-interpretation-limits).
Assigned slots, launches, attempts, infrastructure failures, capture failures,
no-attempts, and usable analysis units need separate accounting. Do not count a
partially observed episode as a complete joint control observation or silently
fill unavailable values with zero. A planned loss allowance is not permission
to replace no-attempts until compliant conduct appears.

## Give each loss-rate statement its actual meaning

Inflating a usable target `k` to `ceil(k / (1-r))` scheduled slots has different
implications under different assumptions:

- **Expected retention:** if each slot has usable probability `1-r`, the
  expected usable count reaches `k`. That expectation is not assurance that the
  realized count reaches `k`. A probability claim needs a joint retention model;
  common outages and outcome-dependent refusal can invalidate independence.
- **Deterministic bound:** if no more than fraction `r` of slots can be unusable
  in each required cell, the corresponding inflation ensures its count target
  subject to that bound and the frozen definition of usable. State the evidence
  for the bound; choosing a ceiling does not establish it as a property of the
  system.
- **Observed stop ceiling:** if exceeding the per-cell ceiling stops the study,
  inflation can ensure the count target conditional on passing that ceiling.
  It does not establish how likely the study is to pass. Report stopped studies
  and their consumed slots; do not omit them from execution accounting.

For an integer loss count, apply the ceiling to the exact observed fraction,
not a rounded display percentage. A global ceiling does not imply the same
ceiling in every arm or world. Freeze the scope of each ceiling explicitly.

If attainment assurance is needed for capacity planning, specify the event
being assured (all required cells, not just an average cell), desired probability,
retention assumptions, dependence treatment, and calculation. Keep that
assurance separate from statistical power conditional on the analysis sample.
Neither a count target nor an assurance value is adopted by this contract.

## Reconcile the historical planning example

CAPLAB-62 comment `3f92fd39-3cd1-4e09-94af-7c94129c3ef4` corrected the earlier
1.96-only power calculation. It used the normal planning multiplier
`z(0.975) + z(0.80) = 2.801585`, a 0.20 target effect, and usable counts
T=50, P=50, C=100. It then inflated scheduled slots to 59,59,118 for a working
loss allowance of 0.15. Preserve those historical statements as provenance;
this prospective clarification does not rewrite them or adopt their parameters.

For its particular summary
`theta = ((mean(B_T)-mean(B_C)) + (mean(P_P)-mean(P_C))) / 2`,
assume independent episodes and arms, complete paired control scores, and
episode fractions in [0,1]. Their variances are at most 1/4; the maximum
within-control covariance is 1/4. Thus a conservative variance bound is
`1/(16*n_T) + 1/(16*n_P) + 1/(4*n_C)` using **usable** counts. This is a
within-world planning calculation, not a model for arbitrary cross-world
clustering, a finite-sample power guarantee, or permission to pool theta.
The [pooling gates](behavior-code-authoring-v1.md#7-check-difficulty-before-pooling)
remain separate requirements.

| Usable T, P, C | Variance bound | SE bound | Normal planning detectable effect |
|---|---|---|---|
| 50, 50, 100 | 1/200 | 0.070711 | 0.198102 |
| 59, 59, 118: every scheduled slot usable | 1/236 | 0.065094 | 0.182368 |
| 59, 25, 118: losses concentrated in P | 67/11800 | 0.075352 | 0.211106 |

The historical SE of about 0.0651 and detectable effect of about 0.182 apply
to the second row. Loss compensation alone does not supply that extra precision.
The third row loses 34/236 slots (14.41%), below a global 15% ceiling, but
fails the P usable-count target and exceeds the planned 0.20 detectable effect.
The example shows why total retention alone cannot verify the allocation.

For a separate **illustrative** capacity calculation, suppose all scheduled
slots independently produce usable observations with constant probability
0.85. Exact binomial sums give these attainment probabilities:

| Arm | Required usable | Scheduled | Expected usable | Probability of reaching target |
|---|---|---|---|---|
| T | 50 | 59 | 50.15 | 0.609130 |
| P | 50 | 59 | 50.15 | 0.609130 |
| C | 100 | 118 | 100.30 | 0.592881 |

With independence across arms as well, the probability of reaching all three
targets is `0.6091295054^2 * 0.5928809624 = 0.2199818138`, about 22%.
These are CAPLAB arithmetic illustrations using the
[NIST binomial mass and cumulative formulas](https://itl.nist.gov/div898/handbook/eda/section3/eda366i.htm).
They are not measured CAPLAB retention probabilities, a forecast of an actual
campaign, or the campaign's unconditional statistical power. In particular,
the calculation does not apply if 15% is a hard bound instead of a stochastic
mean, and some samples below these individual targets can have other valid
precision properties under an explicitly specified analysis.

## Freeze the shortfall disposition before execution

CAPLAB-71 must record the quantities above with the applicable Binding and
population before an adopting campaign launches. Name the maximum scheduled
capacity and the handling of each missingness class, count shortfall, allocation
deviation, and breached ceiling. Infrastructure replacement, if authorized,
needs its own bounded rule and retained slot lineage. Any adaptive collection
or stopping rule must be part of the statistical design; it cannot be improvised
after seeing outcomes or arm differences.

After collection, report planned and observed counts side by side. Verify the
frozen count and analysis conditions before claiming the planned precision or
power. A shortfall is a reported deviation with the frozen disposition, not a
license to label scheduled slots as observations. If a different analysis is
authorized, identify the amendment and its limits; do not backdate planning
claims or report post hoc observed power as evidence of a successful design.

More slots cannot by themselves repair outcome-dependent missingness, failed
blinding, a weak accuracy anchor, invalid code definitions, or causal selection
bias. Those failures remain visible even when numerical count targets pass.
This contract defines review obligations; it does not implement a runtime gate,
establish study readiness, or qualify a reviewer.
