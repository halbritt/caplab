# Codex final-message linkage, version 1

`caplab.codex_capture_link.link_codex_final_message(policy_path, task_custody,
collection_custody, *, expected_attempt_sha256, expected_collection_sha256,
max_receipt_bytes, max_identity_bytes)` checks the final-file consistency
requirement in CAPLAB-79. See the
[decision and verification](../../records/implementation-2026-09-08-codex-final-message-linkage.md).

The function first performs the existing [Codex root linkage](codex-root-capture-linkage-v1.md)
with both independently retained anchors and its full custody/tuple checks.
That API and its incomplete-process behavior are unchanged. It then rereads
the anchored collection, task attempt and process receipt under a separate
combined `max_receipt_bytes` allowance. Retained stdout and the selected
`final_message` object are reread with stable descriptor/path and exact
size/hash checks. The final object must be the selected regular file; a
similarly named task artifact or nested filename cannot substitute for it.

The existing `final_codex_message` selector requires an unambiguous initial
thread, one started turn, one final completed turn, final LF, no recognized
failure event and a completed agent message with a unique item ID. It selects
the last completed agent message inside that turn, preserving its zero-based
event index and item ID. Malformed later messages cannot fall back to an earlier
answer. The selected thread must agree with the retained root rollout.

Encode the selected message text as UTF-8 and compare it exactly to the retained
file bytes. No stripping, newline addition/removal, Unicode normalization or
decoding repair is allowed. Empty bytes match only an explicitly completed empty
agent message, never absence of a message. Invalid Unicode encoding fails.

The official writer at Codex tag `rust-v0.153.4`, commit
`3d2ee51ca2d5db578f328aa75e20aa22c0197c9a`, writes the supplied string directly.
Its JSONL processor normally selects an agent message and also permits a plan-only
fallback. That fallback does not supply an agent-message event, so this API
withholds agreement when no such event exists. It does not infer the plan text.
See the [writer](https://github.com/openai/codex/blob/3d2ee51ca2d5db578f328aa75e20aa22c0197c9a/codex-rs/exec/src/event_processor.rs#L38)
and [JSONL processor](https://github.com/openai/codex/blob/3d2ee51ca2d5db578f328aa75e20aa22c0197c9a/codex-rs/exec/src/event_processor_with_jsonl_output.rs#L380).
Source inspection does not establish behavior of a particular captured process.

The unique stdout, rollout and final-file bytes share `max_identity_bytes`.
Stdout is read again for comparison; the allowance is not total I/O across all
passes. Existing root-link receipt budgets still apply, plus the separate
three-receipt comparison allowance. Parsing and UTF-8 encoding allocate memory
proportional to bounded input. The original policy remains a separate trusted
input. No blocked-filesystem wall-time guarantee is introduced.

The `caplab.codex-final-message-link/v1` report embeds the unchanged root-link
report and adds `final_message_agrees: true`, logical final-file locator, raw
hash and byte count, selected message ID/index, total identity bytes and comparison
receipt bytes. It omits message text. Process completion, return code and termination
remain in the root report. A completed event stream can match a file even if the
outer process exits nonzero or times out afterwards; agreement never clears that
outcome. Native completeness, child linkage and executed-invocation binding
retain their existing unverified values. No score, qualification or acceptance
is supplied.

The caller supplies authorized inspection, quiescent custody and trusted stable
parents. This is not an atomic multi-file snapshot. Referenced selected bytes are
rechecked after root verification; other payloads retain the existing quiescence
requirement. Missing, contradictory, malformed, oversized or changed evidence
raises `CaptureVerificationError`; filesystem errors propagate. There is no
write, native process, original-source search, retry, admission or fallback.
