# opsdigest

Small tool that keeps the home fleet honest. Each host runs its checks
from cron and reports results with `opsdigest record`; every morning at
06:00 the monitor box runs `opsdigest send`, which renders a digest of
the last 24 hours and drops it in the outbox that gets posted to the
on-call channel (set `OPSDIGEST_WEBHOOK_URL` to also post directly).

## Layout

- `opsdigest/events.py` — the check-event model (JSON per line on disk)
- `opsdigest/eventlog.py` — append-only JSONL event log, the system of record
- `opsdigest/digest.py` — renders the morning digest text
- `opsdigest/notify.py` — outbox / webhook delivery
- `opsdigest/cli.py` — `record`, `send`, `prune` subcommands
- `scripts/simulate_night.py` — recreate a realistic night of traffic
  locally (writes into `demo/`, which is generated and disposable)

## Usage

```bash
# on each host, from cron:
python -m opsdigest.cli record --log /var/lib/opsdigest/events.jsonl \
    --host web-01 --check heartbeat --status ok

# on the monitor box, mornings:
python -m opsdigest.cli send --log /var/lib/opsdigest/events.jsonl \
    --outbox /var/lib/opsdigest/outbox

# retention, weekly:
python -m opsdigest.cli prune --log /var/lib/opsdigest/events.jsonl --keep-days 90
```

## Tests

```bash
python3 -m pytest -q
```
