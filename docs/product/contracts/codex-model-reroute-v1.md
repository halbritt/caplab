# Codex model-reroute evidence, version 1

Status: implemented semantic repair. See the
[authorization and verification record](../../records/repair-2026-09-08-codex-model-reroute.md).

The official Codex JSONL processor at commit
[`3d2ee51ca2d5db578f328aa75e20aa22c0197c9a`](https://github.com/openai/codex/blob/3d2ee51ca2d5db578f328aa75e20aa22c0197c9a/codex-rs/exec/src/event_processor_with_jsonl_output.rs)
maps `ModelRerouted` to an `item.completed` event with an `error` item and a
message beginning exactly `model rerouted: `. The formatter includes model
names and a reason in text; CAPLAB does not parse those names into model identity.
This source establishes a supported marker, not an observation of a live reroute.

`caplab.codex_events.is_codex_model_reroute` recognizes that exact envelope and
prefix. A missing item ID does not remove the explicit reroute evidence. Ordinary
warnings, other event/item types, quoted agent text and tool output do not match.
The detector does not search nested payloads or guess future native formats.
`require_no_codex_model_reroutes` parses a supplied stream and raises
`CodexEventError` when this marker occurs. It does not establish completion or
positive model identity when the marker is absent.

| Consumer | Effect of the explicit marker |
|---|---|
| Artifact judgment derivation | Raises `CalibrationError`, even when the final judgment and sidecar agree. |
| Ladder attempt classification | Returns infrastructure disposition, even with a passing pin and task writes. The ladder remains closed to execution. |
| Revbench response derivation | Raises `CodexJSONLTransportError("codex_jsonl_model_reroute")` before response-schema interpretation. Existing execution handling assigns infrastructure failure and registers no derived response. |
| Review model assessment for the `codex` harness | Returns `model-mismatch` with reason `native-model-reroute`; the existing scoring and continuation gates withhold credit and further preparation. |

The review assessment retains an optional `reroutes` list in its existing
`caplab.review-dissent.native-model-identity/v1` result. Each observation contains
the one-based JSONL `line`, raw `item_id` (null when absent), raw `message` and
`source: "item.completed.error"`. Repeated markers remain separate locators;
their number is not a count of independent model actions. The configured subject
is preserved; CAPLAB does not assign the response to a model named in the message.
A malformed stream still follows the existing invalid-trace path. An otherwise
valid Codex stream without this marker remains `model-unverified`.

Completion, root linkage and final-file byte agreement remain separate facts.
`require_completed_codex_turn`, `final_codex_message`, `link_codex_root` and
`link_codex_final_message` keep their existing contracts. A rerouted turn may
complete and produce a matching final file. Neither fact removes the reroute or
establishes configured-subject attribution, execution binding or capture
completeness. Existing non-reroute and Claude assessment behavior is preserved.

Verification uses new synthetic streams and temporary custody. This repair does
not invoke a native harness, rewrite historical assessments, reseal campaigns,
change policy or capture options, or qualify a reviewer for selection.
