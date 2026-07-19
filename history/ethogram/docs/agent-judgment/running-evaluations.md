# Running judgment evaluations

Prerequisites: `harbor==0.18.0` (pinned; installed via `uv tool install`),
Docker, and — for host-side reference matrices — `go`, `python3`, and `curl`.
No default repository check runs Harbor, a container, a model, or the
network; everything below is invoked deliberately.

## Receipt evaluations (doctrine-skill A/B)

Render a skill-eval case as matched control/treatment Harbor tasks, run them,
and grade the pair. Commands, isolation contract, reward projection, and the
skill-provenance cross-check are documented in
[`doctrine/evaluations/robustness/harbor/README.md`](../../doctrine/evaluations/robustness/harbor/README.md).
The short form:

```bash
python3 doctrine/tools/evaluate_doctrine_skill.py render-harbor \
  doctrine/evaluations/robustness/skill-cases/authority-withdrawal.json \
  --skill "$HOME/.codex/skills/doctrine/SKILL.md" \
  --out /tmp/doctrine-skill-harbor

harbor run -p /tmp/doctrine-skill-harbor/control   -a <agent> -m <model>
harbor run -p /tmp/doctrine-skill-harbor/treatment -a <agent> -m <model> \
  --skill "$HOME/.codex/skills/doctrine"

python3 doctrine/tools/evaluate_doctrine_skill.py grade <case> \
  --control <receipt> --treatment <receipt> --out <result>
```

## World-task evaluations (curated tasks and pairs)

Validate any task without a model — the oracle must earn its top band and
the nop agent its floor:

```bash
harbor run -p doctrine/evaluations/robustness/harbor/tasks/checkout-retries-v2 -a oracle -o /tmp/jobs
harbor run -p doctrine/evaluations/robustness/harbor/tasks/checkout-retries-v2 -a nop    -o /tmp/jobs
```

Before running or editing the v2/m1 pair, bake the knowledge surface and run
the hygiene gate:

```bash
python3 doctrine/tools/evaluate_doctrine_skill.py bake-surface \
  --task doctrine/evaluations/robustness/harbor/tasks/checkout-retries-v2 \
  --task doctrine/evaluations/robustness/harbor/tasks/checkout-retries-m1 \
  --corpus-root "$PINCITE_RELEASE_HOME" \
  --check   # verify the pinned manifest; omit only when re-pinning is intended

bash doctrine/evaluations/robustness/harbor/tasks/scripts/check-pair-hygiene.sh
```

The manifest pins Pincite content identity to the validated release. Use a
clean Pincite worktree at the same pinned commit only when the installed
release is unavailable.

The reference-solution matrix must match each task's band table exactly
after any verifier change:

```bash
bash doctrine/evaluations/robustness/harbor/tasks/checkout-retries-refs/run-reference-matrix.sh
```

Verifiers accept `CHECKOUT_APP_DIR`, `CHECKOUT_VERIFIER_LOGS`,
`CHECKOUT_GATEWAY_PORT`, and `CHECKOUT_PORT` for host-side runs; without the
port overrides they pick free ports themselves.

## Live subjects

Local models run at zero cost through `terminus-2`, whose model calls
originate on the host:

```bash
OPENAI_API_KEY=sk-local-noauth harbor run -p <task> -a terminus-2 \
  -m openai/qwen3.6-35b-a3b --ak api_base=http://127.0.0.1:8081/v1 \
  --agent-timeout-multiplier 2 -o <jobs-dir> --job-name <name> -q -y
```

Hosted subjects go through OpenRouter (`-m openrouter/<vendor>/<model>` with
`OPENROUTER_API_KEY` in the host environment). OpenRouter reserves
`max_tokens × completion price` against remaining credits before each
request; terminus sends no cap by default, so for expensive models add
`--ak 'llm_kwargs={"max_tokens": 8192}'`. In-container coding harnesses
(codex, qwen-coder, opencode, claude-code) and their endpoint/auth wiring
are recorded in the adapter README; grade harness-integration failures
separately from model judgment — a reasoning-model reply a harness cannot
parse is not a judgment result.

## Records and retention

Job records, trajectories, receipts, and `DECISION.md` texts stay in session
scratch space. The repository carries: pre-registered experiment records
(fixed parameters, predictions, classification rules — committed before the
first trial), aggregates and band counts afterward, and content hashes for
every input. Judgment-bearing texts reach humans through the adjudication
surfaces as model-attributed material awaiting disposition, never as
auto-filled verdicts.

Derive stage counts from retained Harbor jobs with:

```bash
python3 doctrine/tools/summarize_harbor_trials.py \
  /tmp/jobs/job-* > /tmp/harbor-stage-summary.json
```

The counter currently accepts `terminus-2` jobs in Harbor's `ATIF-v1.7`
trajectory format. It reads realized skill injection from `lock.json`, direct
single-line commands from agent tool calls, and ledger/decision observations
from verifier-owned `detail.json`.
Prompt metadata, reasoning prose, terminal output, and commands printed by a
file read do not advance a stage. Each trial record includes SHA-256 hashes of
the four input artifacts.

The pair verifiers additionally emit a fully world-derived record under
`detail.json`'s `world` key, requiring no trajectory at all: the agent tree
diffed against the shipped `tests/app-manifest.json` (files added, removed,
modified; whether the gateway mock or the payment client changed) and
idempotency-key fingerprints parsed from the agent-phase gateway access log,
including `replay_probe_observed` — a deterministic "ran the falsifying
experiment" signal (two same-key charges observed). These fields are
informational in the current bands; regenerate manifests after any authored
app change with `tasks/scripts/regen-app-manifests.sh` (the hygiene gate
fails on stale manifests).
