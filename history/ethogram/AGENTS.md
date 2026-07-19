# Agent instructions

Before constructing prompts, reviewing evidence, interpreting evaluation
results, or recording decisions in this repository, read and follow
[`ubiquitous_language.md`](ubiquitous_language.md).

Use its terms precisely. In particular:

- label observations, inferences, recommendations, and decisions when their distinction matters;
- preserve the evidence and provenance supporting observations;
- state uncertainty and credible rivals for inferences;
- do not treat a recommendation as a decision or authorization;
- keep decisions, authorization, execution, verification, and acceptance distinct; and
- never silently promote one assertion type into another.

## Fast orientation

Start with `git status --short --branch` and `git log -1 --oneline`. This is a
shared checkout: preserve unrelated dirty paths and keep edits, validation, and
commits inside the requested slice.

Read the smallest start-here surface for the lane:

| Lane | Start here |
|---|---|
| Product specifications and plans | `docs/product/README.md`, then the selected spec and plan |
| Agent-judgment evaluations | `docs/agent-judgment/README.md`, then `doctrine/evaluations/robustness/README.md` |
| Harbor tasks and live runs | `doctrine/evaluations/robustness/harbor/README.md` |
| Study dashboard | `caplab/dashboard/README.md`, then the selected capability card |
| Pincite integration | `pincite-dependency.json`, then `caplab/pincite.py` |

For the `checkout-retries-v2`/`checkout-retries-m1` pair, read
`doctrine/evaluations/robustness/harbor/tasks/checkout-retries-pair-report.md`,
the two identical `instruction.md` files, both verifier `tests/test.sh` files,
and `tasks/scripts/check-pair-hygiene.sh`. For the compact-verification
follow-on, continue with
`doctrine/evaluations/robustness/harbor/tasks/checkout-retries-activation-report.md`
and its referenced order, condition, skill, and stage-counter artifacts.

The pair's baked corpus is manifest-pinned to the source commit recorded in its
`environment/corpus/PROJECTION.md`. A `bake-surface --check` against a newer
Pincite checkout can correctly report `stale_surface`; that is not
authorization to re-pin an existing experiment. Validate against the recorded
source or make a new surface version under explicit experiment scope.

Checked-in experiment reports contain aggregates; raw Harbor jobs and
trajectories are scratch state outside the repository. When auditing a
behavioral claim, use structured `agent/trajectory.json` tool calls and
`verifier/detail.json`. An `<available_skills>` prompt entry is not evidence
that `SKILL.md` was read, and a command printed while reading a file is not an
executed command. If raw records are unavailable, label the aggregate as not
independently verified.

Before relying on Pincite for execution-guiding advice, run:

```bash
PYTHONDONTWRITEBYTECODE=1 make pincite-check
```

Use `make test` for hermetic CAPLAB changes and `make check` as the full local
gate for code, generated evaluation artifacts, or Pincite integration changes.
Do not copy Pincite corpus, doctrine, retrieval, or conversion implementation
back into this repository to make a check pass.

## Branch hygiene

Do not leave unmerged code lying around. If a task uses a branch, merge its authorized work into the intended target branch before reporting completion. If merge authority is absent, report that as a blocker instead of treating the branch as finished. Clean up branches and associated worktrees after merge.
