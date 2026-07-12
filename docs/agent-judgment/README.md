# The agent judgment harness

This documentation set covers the evaluation system built on the Doctrine
Robustness Laboratory's Harbor surface: behavioral measurement of engineering
judgment for any combination of model, agent harness, and knowledge surface.
It measures what an agent *does* — what it reads, what it verifies, when it
declines — rather than what it says it would do.

- [Running evaluations](running-evaluations.md) — commands and operational
  practice for every existing evaluation type.
- [Extending the harness](extending.md) — authoring new judgment tasks,
  knowledge-surface experiments, and the path to fine-tuning.

## What exists

| Component | Location | Purpose |
|---|---|---|
| Doctrine-skill A/B harness | `doctrine/tools/evaluate_doctrine_skill.py` | Sealed control/treatment receipt evaluation of the installed doctrine skill; mechanical grading with hard authority failures and over-refusal detection |
| Harbor adapter | `doctrine/evaluations/robustness/harbor/` | Renders receipt cases as matched Harbor task pairs whose separate verifier grades only the transferred `decision-receipt/2` |
| Curated judgment tasks | `doctrine/evaluations/robustness/harbor/tasks/` | Hand-authored world-tasks with graded reward bands (`checkout-retries`, and the `checkout-retries-v2`/`-m1` clean–mutant pair) |
| Knowledge-surface baking | `evaluate_doctrine_skill.py bake-surface` | Manifest-pinned, sealed knowledge surfaces (doctrine projection or any directory) baked identically into task environments |
| Pair hygiene gate | `tasks/scripts/check-pair-hygiene.sh` | Enforces the single-hunk causal invariant, pristine-verifier sync, metadata uniformity, and forbidden-string scoping |
| Experiment records | `tasks/checkout-retries-pair-report.md` | Pre-registered predictions, fixed parameters, classification rules, and results |

## Design commitments

1. **Behavioral oracles, harm-ordered.** Rewards grade behavior classes, not
   implementations, and shipping harm always scores below doing nothing
   (`checkout-retries-m1`: folklore retry 0.2 < silent no-op 0.3 <
   evidence-based decline 0.8–1.0). A subject that refuses everything cannot
   score well: matched clean tasks penalize over-refusal.
2. **The verifier trusts nothing the agent can write.** Graded components
   ship pristine inside the verifier (`tests/pristine/`), probe counts fail
   closed, and every band boundary was adversarially reviewed and
   regression-probed before the first experimental trial.
3. **One causal variable per comparison.** Clean/mutant pairs differ by one
   hunk (hygiene-enforced); skill arms differ only by skill injection; the
   knowledge surface is baked identically everywhere so retrieval behavior is
   measured, not assumed.
4. **Mechanical grading is observation, not acceptance.** Judgment-bearing
   artifacts (`DECISION.md` texts, receipt human-criteria) are dumped
   verbatim for human review through the adjudication surfaces and are never
   keyword-matched or model-judged for reward.
5. **Retention is explicit.** Trajectories and raw job records stay in
   session scratch space; the repository carries aggregates, hashes, and
   pre-registered records.

## Findings to date (2026-07-12)

- **Receipt A/B (authority-withdrawal):** five live arms across three model
  families all abstained on an adequately evidenced clean case; skill
  injection monotonically reduced hard failures without converting
  abstention into a recommendation. Whether that is over-refusal, oracle
  dogmatism, or instruction anchoring is queued for human adjudication.
- **checkout-retries v1:** saturated at the frontier — four models earned
  1.0 via the documented idempotency-key path; the reward gradient separates
  agents from no-ops but not frontier models from each other. One harness
  (opencode) failed as an integration artifact, graded separately from model
  judgment.
- **v2/m1 pair:** pre-registered experiment; see the report for predictions
  and results.
