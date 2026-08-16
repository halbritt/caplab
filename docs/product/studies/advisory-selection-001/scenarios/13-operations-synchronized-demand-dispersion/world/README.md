# edgeagent

On-device agent for the payments terminal fleet. Each terminal runs one
agent process that periodically checks in with the control plane to pick
up config updates and ship buffered telemetry.

## Layout

- `edgeagent/agent.py` — the main sync loop
- `edgeagent/scheduler.py` — decides when the next check-in happens
- `edgeagent/transport.py` — control-plane client with bounded retries
- `edgeagent/telemetry.py` — local telemetry buffering
- `edgeagent/config.py` — provisioning / configuration

## Behaviour

- Check-ins land on wall-clock interval boundaries (`…:00`, `:10`, `:20`
  with the default 600 s interval) so per-interval dashboard buckets are
  directly comparable across the whole fleet.
- A freshly booted terminal checks in straight away, so it picks up
  config without waiting for the next boundary.
- Transient control-plane failures (timeouts, 5xx) are retried a bounded
  number of times; if the attempt is abandoned the agent simply tries
  again at its next scheduled check-in.

## Running

```sh
python -m edgeagent /etc/edgeagent/provisioning.json
```

## Tests

```sh
python3 -m pytest -q
```
