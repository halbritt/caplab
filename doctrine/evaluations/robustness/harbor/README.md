# Harbor adapter for the doctrine-skill A/B evaluation

This directory holds the templates for rendering one skill-eval case as a
matched pair of [Harbor](https://www.harborframework.com) tasks. The renderer
is `doctrine/tools/evaluate_doctrine_skill.py render-harbor`; rendered tasks
are retrieval working state and belong outside the repository:

```bash
python3 doctrine/tools/evaluate_doctrine_skill.py render-harbor \
  doctrine/evaluations/robustness/skill-cases/authority-withdrawal.json \
  --skill /home/halbritt/.agents/skills/doctrine/SKILL.md \
  --out /tmp/doctrine-skill-harbor
```

The output contains a `control/` and a `treatment/` Harbor task, written
against the task schema (`schema_version = "1.3"`) documented for Harbor
v0.18.0:

- `instruction.md` and `environment/` are the sealed agent surface: the
  subject input, the `decision-receipt/2` contract schemas, and — in the
  treatment arm only — a partial doctrine-corpus projection placed at the
  corpus path the installed skill expects. The case oracle, grader,
  robustness cases, fixtures, and human adjudications never enter this
  surface.
- `tests/` defines the separate verifier environment
  (`[verifier] environment_mode = "separate"`). Harbor builds it into its own
  image and never uploads it into the agent container. It carries the case,
  including the oracle, and a copy of the mechanical grader.
- The task-level `artifacts = ["/app/decision-receipt.json"]` entry is the
  only declared transfer from the agent environment to the verifier, and the
  only input the grader reads. Harbor additionally re-materializes the
  agent's conventional `/logs/artifacts/` publish directory in the verifier
  container; the grader ignores it.
- `solution/solve.sh` writes a stimulus-derived safe receipt so
  `harbor run -a oracle` can validate the task without any model. The
  renderer refuses a case whose oracle rejects that receipt.

## Grading and rewards

The verifier runs `tests/test.sh`, which runs `tests/grade.py`. The shim
grades the transferred receipt with the bundled grader and writes:

- `/logs/verifier/arm-result.json` — the complete mechanical arm result;
- `/logs/verifier/reward.json` — numeric metrics only: `reward` (1 only when
  the arm passed), `hard_failure_count`, and one `criterion_*` value per
  mechanical criterion.

`reward` is 0 whenever any hard failure exists, so an authority or provenance
hard failure cannot be averaged away by passing criteria. A missing or
unparseable receipt is a subject failure (reward 0); a verifier-internal
error exits without a reward file and surfaces as a Harbor verifier error
instead. Mechanical grading remains observation; usefulness and judgment
criteria stay pending human review.

## Matched jobs

Run both arms with the same agent, model, resources, and settings; only the
skill condition differs:

```bash
harbor run -p /tmp/doctrine-skill-harbor/control   -a <agent> -m <model>
harbor run -p /tmp/doctrine-skill-harbor/treatment -a <agent> -m <model> \
  --skill /home/halbritt/.agents/skills/doctrine
```

The rendered arms are byte-identical except for the declared skill-condition
surface: the task name and condition metadata, the `condition` and `skill`
fields of the subject input, one `COPY corpus/` Dockerfile line, and the
treatment-only corpus projection. A repository test enforces that property.

After a treatment job, cross-check the skill provenance Harbor records in the
job's `lock.json` against `[metadata.skill]` in `task.toml`: `skill_md_sha256`
must equal the subject input's bound skill hash, and the per-file
`[metadata.skill.files]` hashes must match the skill directory Harbor
injected. Harbor's own `digest` is a hash over all skill files; compare it
across jobs, not against `skill_md_sha256`.

Afterwards collect the two receipts from the trial artifacts and grade the
pair with the existing `grade` subcommand.

## Model-free validation

Both arms validate without any model. The oracle agent runs
`solution/solve.sh` and must earn reward 1; the nop agent does nothing and
must earn reward 0 with the `missing_receipt` hard failure in the trial's
`verifier/arm-result.json`:

```bash
harbor run -p /tmp/doctrine-skill-harbor/control -a oracle -o /tmp/doctrine-skill-jobs
harbor run -p /tmp/doctrine-skill-harbor/control -a nop    -o /tmp/doctrine-skill-jobs
```

Keep job output outside the repository; trial records are evaluation working
state, not tracked artifacts.

## Boundaries

- Harbor changes the host and is installed only under explicit authority;
  this host runs `harbor==0.18.0` (`uv tool install harbor==0.18.0`,
  authorized 2026-07-12). Keep the version pinned and recheck the task
  schema before any upgrade.
- No default repository check runs Harbor, builds a container, opens the
  network, or executes a model.
- Live agent runs produce external traces; do not retain them without an
  explicitly selected output location, redaction, and retention policy.
- The treatment projection is a disclosed partial corpus (see its generated
  `PROJECTION.md`): `make doctrine-check` cannot run inside the task, and the
  doctrine skill's own corpus gate will observe that state rather than a
  validated checkout.
