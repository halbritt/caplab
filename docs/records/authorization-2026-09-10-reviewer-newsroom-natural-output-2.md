# Preserve a public identity field name while guarding its value

Under ADR 0026, authorize a versioned correction for the observed source
preflight failure and one new preparation in `newsroom-natural-output-2`.
Attempt 1 launched no model: its guard rejected six original source files
because ordinary `user_id` parameters matched a credential claim key.
Preserve its entire preparation, failure and diagnostic custody unchanged.

The observed collision is the key `user_id` directly beneath
`https://api.openai.com/auth` in the token claims. The actual identity value
remains private. OpenAI's original Codex
[`token_data.rs`](https://github.com/openai/codex/blob/main/codex-rs/login/src/token_data.rs)
declares that key and
uses it as the fallback for `chatgpt_user_id`. It is a public protocol field
name, not a private identifier merely because it occurs in this credential.

Authorize `credential-private-text/v4`, retaining v1-v3 unchanged. In v4 only,
recognize this exact key occurrence when its value is a nonempty string.
Continue guarding its value, every token/segment, identity, private claim and
equal text at any private occurrence. Unknown paths, malformed shapes and
custom keys remain guarded. Test that ordinary source survives while private
values and collisions at private occurrences do not. Do not add a global
allowlist or weaken the stream matcher.

After focused tests pass, copy the first preparation's hash-checked original
task trees, diff, dependencies, hidden assessment obligations and successful
test-readiness evidence into the new custody. Do not rerun or relabel its
readiness observations. Freeze new runner, authorization, guard and support
hashes. The sole administrative change is v4 field classification; the task,
prompt, outcome obligations, original Python environment, native tuple,
fifteen-minute budget and opaque-reasoning projection remain the same.

Authorize one new outer native review, subject to all source, isolation,
capture, expiry and no-ranking boundaries in the
[first authorization](authorization-2026-09-10-reviewer-newsroom-natural-output.md).
The first attempt's unconsumed model allowance does not authorize replay of
its frozen plan. One version-only preflight is allowed. Expiry remains
2026-09-11T00:00:00Z or consumption. Stop on any remaining guard rejection;
retain every failure and continue independent work. This correction permits
reviewing ordinary source without changing that source or admitting a case.
