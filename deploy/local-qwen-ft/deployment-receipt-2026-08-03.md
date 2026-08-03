# Local Qwen fine-tune deployment receipt — 2026-08-03

## Deployed identity

- Striatum backend: `local-qwen-ft` (review only, rank 8)
- llama.cpp model alias: `qwen3.6-ft`
- base GGUF: `/home/halbritt/models/Qwen3.6-35B-A3B-APEX-I-Compact.gguf`
- LoRA adapter: `/home/halbritt/models/Qwen3.6-35B-A3B-Striatum-FT/adapter-f32.gguf`
- adapter SHA-256: `807a2a59544fd9e78c8527cfb272778d9ecc7312c25e18bfa1fa7f41d1326715`
- runtime: `striatum-openai-lane 4`
- serving mode: request-level `chat_template_kwargs.enable_thinking=false`

The endpoint intentionally exposes only `qwen3.6-ft`. The historical untuned
`local-qwen` backend remains present but disabled, so old ledger attribution is
preserved without allowing endpoint discovery to collapse the two identities.

## Live verification

The cutover and verification ran under gpu-fleet leases on `proximal` slot 0.
The following gates passed:

1. llama.cpp loaded the compact base plus the hash-verified LoRA adapter.
2. `/health` returned `{"status":"ok"}`.
3. `/v1/models` returned the single id and alias `qwen3.6-ft`.
4. A no-thinking direct fleet canary returned `READY`.
5. gpu-fleet acquired the exact `qwen3.6-ft` capability lease.
6. Striatum backend conformance completed a detached `review` dispatch.
7. The required `review-ledger` output was present and sealed.
8. The supervisor reclaimed its cgroup residue and the wake hook fired.
9. The standing `whisper-stt` service was restored after the lease.

The successful sealed submission is retained at:

```text
/tmp/local-qwen-ft-backend-smoke-20260803-attempt2/spool-root/spool/submissions/
```

Its output content hash is
`8066331c2a5e7b0613b75bdcaa499adf96bf56f37b98ed0fc174adfe619e0960`;
its manifest seal digest is
`68162396accf45735cb05fb843f88256196d7522706142a0bb0cdb7c27bbf44c`.

## Robustness findings closed during cutover

- Hidden reasoning exhausted a deliberately tiny first canary. The shared
  OpenAI-compatible lane now has an opt-in `-disable-thinking` flag; generic
  backends retain their old request shape.
- A comma-separated compatibility alias made llama.cpp advertise the base
  identity as the single discovered model. The tuned service now exposes only
  `qwen3.6-ft`, which lets gpu-fleet verify the declared capability exactly.
- Interactive backend conformance initially lacked a delegated cgroup. The
  verified command runs inside `systemd-run --user --scope -p Delegate=yes`;
  production service units must supply equivalent delegation.

## Source revisions

- striatum-tuner: `4e64b6d`, `771ed9e` plus this receipt revision
- striatum-next: `deb3ee3`, `ed66466`
- gpu-fleet: `2de2007`

The pre-cutover systemd override is retained at
`/etc/systemd/system/llama-27b.service.d/override.pre-local-qwen-ft-20260803`
for an explicit rollback. The applied gpu-fleet migration is append-only and
must not be edited; rollback requires a new migration.
