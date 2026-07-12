# Extending the judgment harness

## Authoring new judgment tasks

The band-design rules that survived adversarial review, stated as
requirements:

1. **Grade behavior classes, not implementations.** A band names an
   observable outcome (duplicate charges, a decline artifact, an exact-once
   ledger), so unforeseen-but-sound solutions land correctly. Name the
   solution classes you expect in the verifier's comments; let the checks
   define the class.
2. **Order bands by harm.** Confident harm scores below inaction; inaction
   scores below evidenced action or evidenced declining. Matched clean tasks
   keep declining from becoming a universal strategy.
3. **Ship pristine copies of everything graded.** The verifier builds graded
   components from `tests/pristine/`, never from the agent-writable tree —
   otherwise "fix the mock" defeats the task's premise.
4. **Fail closed.** An unreadable probe is a floor reward, never a skipped
   gate. Every external read gets a timeout; stacks get readiness checks and
   dynamically chosen ports.
5. **No signposting, including side channels.** Instructions identical
   across a pair except declared surfaces; forbidden-string scans over
   agent-visible authored files; uniform file metadata (Docker `COPY`
   preserves the mtime/mode that would otherwise beacon the mutated file).
6. **One hunk per mutation**, enforced by a hygiene script, so a judgment
   delta has exactly one cause.
7. **Validate with reference solutions for every band** on every verifier —
   the matrix must match the design table cell-for-cell — plus oracle/nop
   runs in real containers, before any experimental trial.
8. **Pre-register.** Fixed parameters, predictions, and classification rules
   are committed before the first run; results are appended, never
   retrofitted.

Seed material: the gold queue's parked scenario-construction candidates
(`doctrine/evaluations/gold/`) each name one axis on which judgment should be
challenged; future tasks should cite the candidate id they instantiate.
Receipt-shaped cases belong in `skill-eval-case.schema.json`; world-tasks
currently live under `harbor/tasks/` — a versioned schema extension for
behavioral cases should go through `docs/product/` rather than a sibling
format.

## Knowledge-surface experiments

`bake-surface` makes the information available to an agent an experimental
variable:

```bash
python3 doctrine/tools/evaluate_doctrine_skill.py bake-surface \
  --task <task-dir> [--task <task-dir> ...] \
  --name memory --mount /agent/memory --source <directory>
```

Any directory — a doctrine projection, an agent memory store, reference
documentation — becomes a sealed, manifest-pinned surface materialized
identically across every listed task. Symlinks are rejected, oracle-marker
content refuses to bake, identity excludes the floating provenance files,
and a drifted source fails `--check` instead of silently rebaselining. The
behavioral question "did the agent consult the surface?" is answered by
fingerprints in the world (the gateway access log pattern), and "did the
skill retrieve the right doctrine?" by packet inspection — both recorded as
observations, never as reward by themselves in clean tasks.

This is the intended instrument for memory experiments: bake a memory
directory into both arms, vary one memory entry (single-hunk discipline),
and measure whether behavior tracks the changed memory.

## Composing with the robustness laboratory

The lab's axis corrupts the world or the doctrine; the skill A/B toggles the
agent's protocol. They compose into a 2×2 whose most informative cell is
skill-on × corrupted: does doctrine-equipped judgment detect a corrupted
input, or does an authoritative-looking packet make the agent confidently
wrong? The `checkout-retries-v2`/`-m1` pair instantiates this with a
world-level mutation; packet-level mutations should reuse the operator
registry (`doctrine/evaluations/robustness/operators.yaml`) so a mutation
applies to a scenario without rewriting it.

## From evaluation to training

The harness extends to fine-tuning for judgment, in escalating order of
investment:

1. **Rejection-sampling SFT.** Run wide matrices on the local subject, keep
   only top-band trajectories (`terminus-2` exports them; m1 declines are
   the valuable examples), and tune a small model on the kept set. Cheapest,
   and works today.
2. **Reward-based RL.** The verifiers already emit numeric, harm-ordered
   rewards in Harbor's format; the Harbor cookbook ships RL integrations
   (harbor-rl, tinker-rl, gepa), and terminus-2 has a Tinker backend.
3. **Guard rails that become load-bearing under optimization.** Training
   inverts the threat model: every verifier exploit becomes gradient bait,
   so pristine-component grading and fail-closed probes are the training
   substrate, not optional hardening. Two tasks overfit immediately — build
   task families from the gold-queue seeds and hold out families when
   comparing checkpoints. Human-adjudicated dimensions must never be proxied
   by a mechanical stand-in inside a reward function.

The concrete target this points at: a judgment-tuned driver for
`striatum-next` (`~/git/striatum-next/`), whose escalation discipline — act
within authority, decline with evidence, never resolve your own escalations
— is exactly what the m1 band structure rewards. The doctrine skill already
carries a striatum-next routing reference; a model tuned on top-band
trajectories from these tasks is a candidate for that seat, gated by the
same human adjudication that gates everything else here.
