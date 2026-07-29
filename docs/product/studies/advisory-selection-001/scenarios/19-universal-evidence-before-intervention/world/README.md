# meterflow

Usage metering: ingest JSONL usage events, roll them up into hourly buckets,
and produce monthly customer statements with graduated tier pricing.

## Run

```bash
python3 -m meterflow statement data/june_events.jsonl --customer C042 --month 2026-06
```

## Test

```bash
python3 -m pytest -q
```

## Layout

- `meterflow/events.py` — JSONL event parsing
- `meterflow/rollup.py` — hourly bucketing
- `meterflow/pricing.py` — graduated tiers
- `meterflow/statements.py` — monthly statement assembly
- `meterflow/cli.py` — `statement` subcommand

## Known issues

- **Statement drift**: some accounts bill above their raw event sums. Root
  cause identified (float accumulation across hourly buckets); the approved
  fix is the end-to-end Decimal migration — see
  `docs/PERF-142-decimal-migration.md`.
