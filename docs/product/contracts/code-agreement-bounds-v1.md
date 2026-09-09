# Optional simultaneous agreement bounds

Status: implemented diagnostic, not a study-selected interval method or gate.
[Decision and verification](../../records/implementation-2026-09-08-agreement-bounds.md).

`scripts/code_agreement.py judgments.json --iid-confidence 0.95` adds conservative
uncertainty bounds to an explicitly supplied agreement population. The confidence
value is required for this mode; 0.95 here is an example, not a selected study
parameter. The input remains
[`caplab-code-agreement-input/1`](code-agreement-report-v1.md). No input is changed.

The mode requires independently and identically distributed complete episode
pairs within each world/code, with sample size and inclusion not selected from
the observed labels. The program cannot verify those assumptions. Multiple
actions from one episode are not independent slots; neither are clustered
episodes simply because their IDs differ. Use a different, justified analysis
for those designs. Dependence between codes or worlds does not invalidate the
union bound, provided the within-row sampling assumptions hold.

Bounds describe the population represented by complete pairs. Missing and
explicitly unavailable judgments remain in the embedded descriptive report;
they cannot support claims about unobserved episodes. Informative missingness,
adaptive stopping and repeated looks require separate treatment. A report does
not account for other reports, confidence levels tried, or separately analysed
harnesses. Freeze the comparison family and analysis before viewing outcomes;
do not claim a single simultaneous level by juxtaposing separately generated
reports.

## Output and interpretation

The new schema is `caplab-code-agreement-bounds-report/1`. It contains:

- `method`: `hoeffding-three-proportions-union-bound/1`;
- `confidence` and `family_size`, counting all declared world/code rows;
- `agreement`, the unchanged descriptive report, including undefined point estimates;
- `bounds`, one row per declared world/code; and
- the original input SHA-256 at the CLI boundary and explicit interpretation limits.

Each bounds row names its complete-pair count, `epsilon`, and `[lower, upper]`
intervals for `observed_agreement`, `chance_agreement` and `kappa`.
`coder_positive_rates` contains two such intervals in the embedded report's
`coder_ids` order. These are population-proportion bounds, not additional
point estimates. No complete pairs yields null intervals and epsilon with
`bounds_unavailable_reason: "no-complete-pairs"`.

The kappa interval applies only when population kappa is defined.
`undefined_population_kappa_not_excluded` is true when the conservative region
also permits both coders to always give the same constant label, or when there
are no complete pairs. It does not diagnose the population as degenerate. An
undefined observed kappa remains null in `agreement`; an interval does not turn
it into a passing statistic. A tiny perfectly agreeing sample can give the full
`[-1, 1]` range, and constant agreement retains the undefined warning.

Confidence is a finite number strictly between zero and one. Invalid input or
confidence exits 2 with no report. Successful reporting exits 0 even with no
usable bounds. `--iid-confidence` and `--reference` are mutually exclusive:
these are agreement bounds, not accuracy bounds. Without either option, the
original agreement CLI output is unchanged; reference mode is unchanged.

## Derivation and numerical behavior

For one row with n complete pairs, let o be the agreement probability and a,b
the two positive-label probabilities. Each observed rate averages a bounded
indicator. Hoeffding's one-sided bound is `exp(-2*n*t*t)`; applying it to both
tails gives `2*exp(-2*n*t*t)`.
[Hoeffding (1963), Theorem 1, equation 2.3, page 15](https://www.cs.rpi.edu/academics/courses/spring06/random/hoefding.pdf).

For m declared rows and error budget alpha = 1 − confidence, use
`epsilon = sqrt(log(6*m/alpha)/(2*n))`. The union bound across three two-sided
rate bounds in each row gives simultaneous coverage at least the requested
confidence under the stated sampling model. Empty rows consume their share
without producing a bound. This allocation does not require independence among
the three rates or among rows.

Clip each rate interval to [0,1]. Chance agreement is
`e = a*b + (1-a)*(1-b)`. It is bilinear, so its minimum and maximum over the
rectangle of marginal-rate bounds occur at corners. The rectangle can include
infeasible combinations; retaining them makes the result more conservative.

For e < 1, `kappa = (o-e)/(1-e)` increases with o and decreases with e for
o ≤ 1. Thus the lower bound uses o's lower and e's upper endpoints; the upper
bound uses o's upper and e's lower endpoints. Intersect with [-1,1]. If e's
upper endpoint is 1, retain lower bound -1 and the undefined-population warning.
This extension from the concentration bound to kappa is CAPLAB's derivation,
not a kappa interval stated in Hoeffding's paper.

The implementation evaluates logarithm and square root in double precision,
rounds the radius upward by one representable value, then uses exact rational
arithmetic for rates, corners and transformations. JSON endpoints round outward
from those rationals. This reduces endpoint cancellation; it is not a formal
machine-verified bound on the platform's logarithm/square-root implementation.
The method can be substantially wider than other justified methods. It assumes
neither a normal approximation for kappa nor a bootstrap distribution.

## Reproducible example

Use the two-slot JSON example in the
[agreement guide](code-agreement-report-v1.md), then run:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 scripts/code_agreement.py judgments.json --iid-confidence 0.95
```

That example has one complete pair and one unavailable coder judgment. It
reports one incomplete pair, an undefined point kappa and bounds [-1,1] with
the undefined-population warning. No threshold or acceptance is inferred.
CAPLAB-71 still owns the study's confidence level, multiplicity family, sampling
unit and chosen uncertainty method. CAPLAB-65's accuracy/roster requirements,
CAPLAB-66's blinding validation and CAPLAB-77's actual repair coding evidence
remain separate prerequisites.
