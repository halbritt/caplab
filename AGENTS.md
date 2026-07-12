# Agent instructions

Before interpreting source material, writing doctrine, constructing prompts, reviewing evidence, or recording decisions in this repository, read and follow [ubiquitous_language.md](ubiquitous_language.md).

Use its terms precisely. In particular:

- label observations, inferences, recommendations, and decisions when their distinction matters;
- preserve the evidence and provenance supporting observations;
- state uncertainty and credible rivals for inferences;
- do not treat a recommendation as a decision or authorization;
- keep decisions, authorization, execution, verification, and acceptance distinct;
- never silently promote one assertion type into another.

These meanings apply throughout the repository, including generated corpus artifacts and agent-produced analysis. More specific instructions may add constraints, but they must not redefine the ubiquitous language.

## Fast orientation

Start with `git status --short --branch` and `git log -1 --oneline`. This is a
shared checkout: preserve unrelated dirty paths and keep edits, validation, and
commits inside the requested slice.

Read the smallest start-here surface for the lane:

| Lane | Start here |
|---|---|
| Book conversion and generated corpus | `README.md`, then `docs/adding-books.md` |
| Doctrine library or retrieval | `doctrine/README.md`, then `doctrine/OPERATIONALIZATION.md` |
| Product specifications and plans | `docs/product/README.md`, then the selected spec and plan |
| Agent-judgment evaluations | `docs/agent-judgment/README.md`, then `doctrine/evaluations/robustness/README.md` |
| Harbor tasks and live runs | `doctrine/evaluations/robustness/harbor/README.md` |

For the `checkout-retries-v2`/`checkout-retries-m1` pair, read
`doctrine/evaluations/robustness/harbor/tasks/checkout-retries-pair-report.md`,
the two identical `instruction.md` files, both verifier `tests/test.sh` files,
and `tasks/scripts/check-pair-hygiene.sh`. Do not inventory `sources/`,
`books/`, or the full doctrine graph unless the lane requires them.
For the current compact-verification follow-on, continue with
`doctrine/evaluations/robustness/harbor/tasks/checkout-retries-activation-report.md`
and its referenced order, condition, skill, and stage-counter artifacts.

The pair's baked corpus is manifest-pinned to the source commit recorded in
its `environment/corpus/PROJECTION.md`. A `bake-surface --check` against a
newer checkout can correctly report `stale_surface`; that is not authorization
to re-pin an existing experiment. Validate against the recorded source or make
a new surface version under explicit experiment scope.

Checked-in experiment reports contain aggregates; raw Harbor jobs and
trajectories are scratch state outside the repository. When auditing a
behavioral claim, use structured `agent/trajectory.json` tool calls and
`verifier/detail.json`. An `<available_skills>` prompt entry is not evidence
that `SKILL.md` was read, and a command printed while reading a file is not an
executed command. If the raw records are unavailable, label the aggregate as
not independently verified.

Before relying on doctrine for execution-guiding advice, run
`PYTHONDONTWRITEBYTECODE=1 make doctrine-check`. If it fails because the shared
checkout has unrelated or stale generated state, do not rebuild that state
outside the authorized slice; report the failure and continue with
repository-only evidence when the task permits. Use `make check` as the full
repository gate for code or generated-artifact changes.
