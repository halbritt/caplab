# Deploy the tuned local Qwen review backend

This deployment keeps the trained model as a llama.cpp LoRA over the existing
compact Qwen3.6-35B-A3B base. The endpoint alias and Striatum backend identity
are `qwen3.6-ft` / `local-qwen-ft`. The server keeps the old model alias as a
transition-compatible secondary alias, but the untuned `local-qwen`
declaration is retained disabled so its historical ledger evidence remains
attributable.

## Install

Create a stable model path that points at the hash-verified recovered artifact:

```bash
mkdir -p /home/halbritt/models/Qwen3.6-35B-A3B-Striatum-FT
ln -s \
  /home/halbritt/.local/state/runpod-jobrunner/runs/run-20260802T122647-fd862d28930d/receipts/artifacts/artifacts/final/adapter-f32.gguf \
  /home/halbritt/models/Qwen3.6-35B-A3B-Striatum-FT/adapter-f32.gguf
```

Install `llama-27b.override.conf` as the service override only while holding the
proximal GPU-fleet lease. Apply gpu-fleet migration
`015_proximal_tuned_qwen.sql` during the same leased transition. Install
`backend.yaml` and the `striatum-backend-local-qwen-ft` command through the
striatum-next repository checks before enabling normal scheduling.

## Verify

Require all of these before releasing the lease:

- `/health` returns `ok`;
- `/v1/models` exposes `qwen3.6-ft`;
- one bounded completion succeeds through `striatum-openai-lane`;
- the local-qwen-ft live backend-conformance smoke submits a sealed review;
- gpu-fleet graduates the exact `qwen3.6-ft` slot to `routable`; and
- the old `local-qwen` declaration remains disabled.

## Roll back

Restore the prior systemd override, restart the service under a lease, and add
a new append-only gpu-fleet migration restoring `qwen3.6-35b-a3b`. Disable
`local-qwen-ft` and re-enable `local-qwen` with new declaration versions. Never
rewrite an applied fleet migration or existing ledger history.
