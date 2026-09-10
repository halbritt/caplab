# Reproduce sampled pool-runner transport and validity behavior

Under ADR 0026 and the active reviewer-ranking goal, authorize private
development custody at
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/pool-transport-witness-1`.
Copy original tracked `src/caplab/` files, `pyproject.toml`, and
`docs/product/specs/spec-agent-capability-lab.md` from these CAPLAB revisions:

- Introduction: `9cb8d6561176e9d3d7b530eae3f40954744d1766`.
- Sampled base: `1517d426afbced67422a4097c0d5fd92d7200287`.
- Sampled repair: `c8f097a0934bfa380e7c9c5cda4f11ea4ac2b454`.

Pin source commit, tree, path, Git blob, content hash and exact membership.
Historical source must remain unchanged and read-only. Preserve the failed
attempt if preparation or execution fails; do not revise its frozen criteria.
This authorizes a private development copy only, not corpus admission,
registration, historical result relabeling or purging.

Run the original `invoke` and `run_pool` implementations against a new local
process fixture that records exactly what arrives through its declared
argument or stdin channel. For file-spilled bodies, the fixture reads the
named file and retains its bytes. The fixture is a deterministic transport
endpoint, never a native reviewer or proxy for a model. It supplies controlled
valid, absent, timed-out and invalid-verdict responses so the original
runtime's delivery, pair disposition and aggregate denominator can be tested.
Historical injection helpers may prepare two distinct bodies; their alleged
defect labels and scores are not ground truth for reviewer quality.

Freeze these nine conditions: direct argument prompts at 100,000 and 100,001
bytes; a 100,001-byte stdin prompt; healthy inline pair; healthy oversized
pair; empty control response; empty mutant response; timed-out mutant; and
parseable mutant object without a verdict. The latter challenges whether the
sampled repair's parseability gate establishes a valid response. Expected
delivery follows the declared channel; missing/invalid responses cannot
become subject judgments under the predating product specification and the
original prompt's response contract.

Use Python 3.12 and installed PyYAML, with executable and dependency hashes
pinned. Two executions per revision, each limited to 60 seconds; total
execution budget 360 seconds. Original subprocess timeout is 0.5 seconds for
the deliberate timeout condition and 5 seconds otherwise; the fixture sleeps
5 seconds for the timeout. Kill only owned process groups on outer timeout.
Do not call a provider, native agent, real pool, source registry or service.
Unshare networking, mount source and dependencies read-only, clear the home
and environment, and write only new private capture/workspace files. Retain
all endpoint receipts, full received prompts/bodies, original result rows,
summaries, process status and inventories. Stop on input/runtime drift,
fixture failure, unexpected effects or budget exhaustion. Expiry:
2026-09-11T00:00:00Z or consumption.
