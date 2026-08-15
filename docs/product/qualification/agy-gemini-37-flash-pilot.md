# Native-AGY Gemini 3.7 Flash pilot

This repository-development pilot compares three separate native agent-system
subjects: Gemini 3.7 Flash through AGY 1.1.13 at low, medium, and high effort.
It runs two matched clean/mutant integer-minimum cases per subject. The result
tests the adapter, structured response discipline, clean-control behavior,
defect detection, and exact defect anchoring on this synthetic population.

Run the tool from a CAPLAB checkout with Python 3.12, the project dependencies
installed in `.venv`, AGY 1.1.13 installed at the registered byte identity, and
an active owner sign-in. `WORKSPACE` must not exist. The tool has five stages:

```bash
PYTHONPATH=src .venv/bin/python tools/caplab_revbench_agy_pilot.py prepare WORKSPACE
PYTHONPATH=src .venv/bin/python tools/caplab_revbench_agy_pilot.py authorize WORKSPACE \
  --authorized-by OWNER --source AUTHORITY-SOURCE --valid-for-seconds 3600
PYTHONPATH=src .venv/bin/python tools/caplab_revbench_agy_pilot.py execute WORKSPACE
PYTHONPATH=src .venv/bin/python tools/caplab_revbench_agy_pilot.py score WORKSPACE
PYTHONPATH=src .venv/bin/python tools/caplab_revbench_agy_pilot.py inspect WORKSPACE
```

`prepare` performs no model call. It requires the exact registered AGY binary
and verifies the model, plugin, configuration, and skill surfaces. `authorize`
records the caller's explicit authority and exact twelve-call budget. `execute`
records an exclusive durable intent before every sequential call and never
retries. `score` is offline and keeps each effort binding separate.
`inspect` reports the retained stage state and metrics without a model call.

Expected failures use exit status 2 and one stable error line. For example,
`error: agy_runtime_surface_drift` means the model, plugin, configuration, or
skill surface changed after preparation. Preserve the workspace and prepare a
new plan; do not rerun an already claimed attempt.

The retained `observation.json` is an engineering pilot observation, not a
CAPLAB Measurement. AGY's signed-in global session, dynamic host runtime,
telemetry, skills, conversation persistence, and provider delivery semantics
are not sealed by this tool. The two-case synthetic population does not assess
broad coding, tool use, repository navigation, long context, multimodal work,
performance, cost, qualification, or acceptance. The exact authority and
reopening conditions are in [ADR 0064](../../decisions/adr-0064-bounded-agy-gemini37-revbench-pilot.md).
