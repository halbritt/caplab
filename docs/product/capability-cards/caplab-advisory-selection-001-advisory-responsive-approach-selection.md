---
card_id: advisory-responsive-approach-selection-v1
artifact_type: capability-card
schema_version: caplab-capability-card/1
card_version: 0.1.0
status: specified-prospective
execution_authorized: false
decision_owner: primary-agent
decision_authority: adr-0026
selection_record: docs/records/decision-2026-09-08-caplab-73-capability-card.md
---

# Advisory-responsive approach selection

This construct asks whether an agent incorporates advice that fits a task,
resists advice that does not fit, and preserves the quality of its work.
It can apply to doctrine, style guidance, or runbooks. Its first planned study
is `advisory-selection-001`; the study-specific filename preserves the reserved
path, while this card defines requirements that later studies must inherit.

This is a prospective measurement contract selected in the
[CAPLAB-73 decision](../../records/decision-2026-09-08-caplab-73-capability-card.md).
An adopting study must name this version and freeze its own instrument and
analysis. No study is preregistered, no evidence is admitted, and no Binding is
qualified by publishing this card. The checks below are requirements for
adoption and interpretation, not claims of implemented automatic enforcement.

## Construct and failure mode

**Advisory-responsive approach selection** has three constitutive clauses:

1. Incorporate served guidance when it bears on the task.
2. Decline to distort the work toward guidance that does not bear on the task.
3. Do so without the guidance's presence degrading the work.

Advice recommends an approach; its presence does not make that approach
appropriate or override task authority. Uptake of both fitting and misfit
advice is **suggestibility**. Repeating the guidance, naming its source, or
copying its vocabulary does not establish that the agent enacted its rule.
A correct alternative approach may exhibit none of the bearing codes.

The unit under measurement is an exact
[native agent system](../contracts/native-agent-systems.json) Binding within
a declared task population and administration. A model name alone is
insufficient. Pin harness/version, model and effort, instruction surfaces,
tools, permissions, relevant runtime and account/serving context. Record
assignment and observed identity separately. Unverified identity or a changed
Binding cannot be silently pooled into the named subject.

## Required comparisons

Every study claiming this construct must include an appropriate baseline,
bearing advice, and plausibly adjacent non-bearing advice. These are comparison
roles, not a proof that exactly three physical arms suffice. The study must
map each role to its actual serving operation and identify the estimand for
every contrast. A fourth arm needs its own purpose and denominator.

The non-bearing comparison is constitutive and cannot be dropped. For a
Pincite concept study, use the explicitly adopted
[adjacent-placebo selection rule](../contracts/adjacent-placebo-selection-v1.md)
and record semantic pairing validation. A random unrelated concept or a packet
borrowed from another task is not automatically a valid adjacent placebo.
Show that the placebo conduct is possible in this world and that following
it does not meet a bearing need. Absence of placebo conduct alone cannot
distinguish discrimination from an impossible behavior or an inert detector.

Freeze the actual baseline packet, dose, insertion/substitution operation,
token and tool budgets, and allowed authority. A baseline with existing advice
estimates an incremental effect under that advice; it does not estimate advice
versus none. Control differences in task, exposure, account, timing and capture
that could otherwise masquerade as advice effects. Record any residual
confounding and restrict the claim accordingly.

## Observables and instrument definition

Use frozen binary behavioral codes with explicit positive and negative rules.
A **B-code** detects the bearing guidance's conduct. A **P-code** detects the
non-bearing guidance's conduct; a true P-code is not a favorable quality score.
Apply both code families to all comparison roles using the same frozen rules.

Adopt the [behavioral code-authoring procedure](../contracts/behavior-code-authoring-v1.md):

- Derive B-codes from both the guidance's decision rule and a reference
  solution. Validate a materially different correct implementation, so exact
  patch matching cannot satisfy the measurement contract.
- Derive P-codes from the placebo rule. Validate parent/reference negatives
  and an explicit feasible positive witness; an always-false predicate fails.
- Specify boundary negatives, including words without actions and a reported
  check without evidence of its required completion. Prefer artifact
  observables when sufficient. Static diffs cannot establish action sequence.
- Freeze mechanical versus agent/human scoring, witness results, input
  boundaries and code weights before subject outputs. Missing or unreadable
  evidence is unavailable, never silently false.

Context used to define codes is not permission to expose references or arm
labels during application. Record author, validator, custodian and application
coder identities and prior exposure. Seal the codebook and interpretation
rules with a protected prior witness before scoring outputs. Validate the
redactor against direct and indirect treatment clues while preserving the
conduct needed for scoring. Removing exact packet text alone is insufficient.

Perform the preregistered dual-coding and per-code reliability gate before
unblinding. A failed or undefined required statistic stops that analysis;
do not drop the code after seeing results. Agreement, including perfect
agreement, does not establish accuracy or independence. Require a separately
justified accuracy anchor and record its authority and limitations. The
[agreement diagnostic](../contracts/code-agreement-report-v1.md) supplies
descriptive counts and statistics, not that anchor or a pass decision.

## Change, selectivity, and quality remain separate

For each world, let B and P be its frozen code-family scores. Let C denote
baseline, T bearing advice, and W non-bearing advice. Report arm-level B and P
scores, then both own-code contrasts:

```text
dB = mean(B_T) - mean(B_C)
dP = mean(P_W) - mean(P_C)
S  = dB - dP
```

S describes selectivity on these code scales. It is non-monotonic in raw
uptake: equal positive dB and dP give S = 0, not high capability with a caveat.
Do not substitute uptake alone, or a favorable S alone, for the three clauses.
Inspect cross-code effects, such as loss of B conduct under W, alongside
separately measured work quality; own-code contrasts can miss that harm.

An adopting foundational study may make behavioral change its primary. Its
candidate pooled estimand `theta = (dB + dP) / 2` answers a different question:
did serving guidance increase its own conduct? A suggestible subject can have
a large theta. The code-authoring procedure's comparability and uncertainty
gates must pass before theta is reported. Always retain dB and dP separately.
Declaring S secondary or descriptive does not waive evidence needed for a
later capability claim.

Measure work quality independently of code conformance. For repairs this may
include correctness under a frozen acceptance oracle and scope violations.
For review it requires independently grounded defects and sound controls,
anchored findings, and false-alarm observations. A guidance-shaped answer or
agreement with another model is not the quality oracle. Quality may remain
outside a premise-only study; that study then leaves clause 3 unestablished.
Do not filter attempts by correctness merely to improve the behavioral score.

Report assigned slots, exposures, completed captures, attempts, usable code
judgments, and exclusions by arm/world with reason counts. Preserve unavailable
outcomes and the fixed replacement rule. Equal attempt rates do not establish
equal composition; attempt-conditioned differences require their stated
selection assumptions or sensitivity analysis for a causal interpretation.
Multiple codes from one episode are not independent replications. Preserve
within-episode covariance, world sampling and frozen weights in uncertainty
estimates. Neither a common [0,1] range nor repeated trials alone justifies
cross-world or cross-Binding generalization.

## Claim and promotion gates

The study owner freezes meaningful effect and harm tolerances, uncertainty
method, multiplicity handling, sample sizes, analysis population, and stopping
rules before outputs exist. This card sets no numerical pass threshold.
Missing choices prevent a favorable capability claim; they are not defaults
to zero tolerance or to a conventional significance threshold.

| Claim level | Evidence required | If unavailable or contradicted |
| --- | --- | --- |
| Behavioral observation | Valid identity, capture, codebook, scoring and custody; arm denominators and uncertainty | Report the missing/invalid evidence without a capability score |
| Advice changed conduct | Identified comparison and meaningful own-code effect under frozen inference rules | Report bounded estimates; a wide interval is inconclusive, not no effect |
| Advisory-responsive approach selection | Evidence of fitting uptake, bounded misfit distortion and non-degradation, each meeting its frozen uncertainty criterion | State which clause is unsupported or contradicted; no favorable full-construct claim |
| Capability profile contribution | Accepted exact-scope measurements, all construct gates, sampling/exposure limits, and a separately authorized qualification policy | Keep descriptive evidence separate from profile promotion |
| Reviewer selection or deployment value | Separate criterion evidence on representative review work, independent outcomes, costs and harms, plus authorized selection policy | No reviewer ordering or placement inference from this card |

For a favorable full-construct claim, the interval for fitting uptake must
support the frozen meaningful benefit, and misfit distortion and quality harm
must each stay within their frozen acceptable bounds. A non-significant harm
test is insufficient: uncertainty must exclude unacceptable harm under the
declared rule. High spontaneous conduct may leave no measurable uptake
headroom; that is a limitation of this instrument for that subject, not proof
that the subject lacks capability.

No one-dimensional leaderboard score is defined. Show per-world effects,
intervals, denominators, quality outcomes and unresolved gates first. Any
permitted pooled summary must retain those components and state its population.
Authoring or tuning scenarios against observed output limits the generalization
claim even when remaining evaluation episodes have not been observed.

These arithmetic examples are synthetic, not accepted measurements:

| dB | dP | S | theta | Interpretation before uncertainty/quality gates |
| --- | --- | --- | --- | --- |
| 0.60 | 0.60 | 0.00 | 0.60 | Strong own-code change; no selective lift |
| -0.10 | -0.50 | 0.40 | -0.30 | Positive difference without fitting uptake |
| 0.40 | 0.00 | 0.40 | 0.20 | Candidate selective lift; quality and other gates still required |
| 0.00 | 0.00 | 0.00 | 0.00 | Point estimates alone cannot distinguish no effect from inadequate precision or headroom |

The theta column illustrates arithmetic only; no example supplies the frozen
comparability or uncertainty evidence needed to publish a pooled estimate.

## Study handoff and limits

The card carries the construct, non-bearing comparison requirement, code and
blinding discipline, non-monotonic selectivity rule, and claim boundaries.
Each preregistration carries the actual world population, exact Binding,
serving/dose mapping, corpus and packet identities, admission/sealing procedure,
coder roster/accuracy anchor, parameter table, execution schedule and budget,
custody manifest, analysis and reporting rules. A later study of a runbook or
style guide inherits the card requirements but selects its own operationalization.

CAPLAB-65, 66, 70, 71, 72, 74 and the shakedown/custody work remain separate
deliverables. Completing this draft does not establish their completion.
This card cannot establish cross-harness portability, a general model ranking,
Pincite routing policy, or production reviewer value. The confirmed
[review-instrument disposition](../../records/report-2026-09-07-review-instrument-disposition.md)
continues to govern reviewer ranking and model spend; this card changes none
of those permissions.
