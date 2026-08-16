# K3 content-channel probe — 2026-08-07

Two calls to `moonshotai/kimi-k3` via OpenRouter (provider: Together, both), same
fully-inline review prompt (dispatch `7ddfb972d4a7…`, the smallest eval example
with no spilled input bodies). Raw response bodies preserved verbatim — this is
the capture `eval.py` discards (it keeps only `message.content`).

| file | request | outcome |
|---|---|---|
| `k3-plain-response.json` | plain chat completion, max_tokens 32768, temp 0.6 (what `striatum-openai-lane` sends today) | `finish_reason: stop`, **content empty**, 9,787 reasoning tokens, $0.175, 73s |
| `k3-schema-response.json` | same + `response_format: json_schema` (the lane's `review-ledger` schema) + `provider: {require_parameters: true}` | **valid ledger in content** (5,172 chars, verdict `accept_with_findings`, 3 findings), 6,903 reasoning tokens, $0.124, 68s |

Mechanism, visible in `k3-plain-response.json` → `message.reasoning` tail: the
model completes the review in its reasoning channel, then says *"Now write the
files. … Create outputs/ dir, write review-ledger and ASSUMPTIONS.md. … Let me
write the files now."* — and stops. The rendered prompt's file-workspace
instructions (`outputs/ASSUMPTIONS.md`, "write every required output as a single
file", "your working directory is …") make K3 attempt tool-style action; a bare
chat completion has no tool channel, so it emits nothing in `content`. A trivial
prompt has no file instructions, which is why the earlier control probe answered
normally.

The schema-mode call is the fix `backends/glm/backend.yaml` already carries
(`-response-format review-ledger`) and the `kimi-k3` / `deepseek-v4-flash`
declarations omit.

Note: the schema-mode verdict (`accept_with_findings`) landed on the wrong side
of the reference (`needs_revision`, fate `revised`) — one sample at temp 0.6
proves the content channel, not review quality. The full fair benchmark decides
quality. Full analysis: `docs/audits/OPENROUTER_ADAPTER_INVESTIGATION_2026-08-07.md`.
