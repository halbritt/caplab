# Native tool-pair report, version 1

Status: development reporting surface. See the
[implementation record](../../records/implementation-2026-09-08-native-tool-pairs.md).
Native emission and representative coding compatibility remain unverified.

`caplab.native_tool_pairs.build_native_tool_pair_report(content, *, format,
expected_sha256, expected_root_id, max_bytes)` inspects caller-owned immutable
bytes. It requires a positive integer byte limit, a matching lowercase SHA-256,
nonempty strict UTF-8 JSONL ending in LF, and the expected initial root ID.
Empty lines, ambiguous JSON keys, malformed supported records, and conflicting
root IDs fail with `ValueError`. CRLF records retain their exact bytes. The hash
must come from independent custody; computing it from an untrusted file at
inspection time does not establish origin or execution linkage.

## Observed units and scope

| Format | Association | Boundary |
| --- | --- | --- |
| `codex-exec-jsonl` | `item.started`, `item.updated`, `item.completed`, by item ID | Command execution, file change, MCP call and web-search item lifecycles; this is not a generic tool-call count. |
| `claude-stream-jsonl` | Complete assistant `tool_use` and user `tool_result` blocks, by native tool ID | Session ID and parent-tool ID also belong to the key. Results from a child scope cannot satisfy a root request. |

The first event must be the matching Codex `thread.started` or Claude root
`system/init`. Reinitialization is refused. Every Claude event must carry a
nonempty session ID; events without a parent-tool scope must use the expected
root session. This strict supported profile may reject other native variants;
rejection is not a finding about the harness's capability.

Claude partial `content_block_start/tool_use` records are kept as `partials`,
separate from the completed request. Other streaming records remain explicitly
unclassified. A partial-input stop does not establish execution completion.
Unknown events, item types and content blocks retain line/pointer references.
Known non-tool content is identified in the event index without reproducing
its text. No event is silently removed from that index.

Groups contain source references for requests, updates, partial starts and
results, plus observed kinds/tool names. Status is one of:

- `paired`: exactly one supported request and result, in that record order.
- `request_without_result` or `result_without_request`: one side is absent.
- `partial_or_update_only`: no completed request or result was observed.
- `ambiguous`: repeated requests/results, conflicting kind/name, or result
  order inconsistent with the request. All references remain available.

Duplicates are retained even when identical; they are not silently collapsed
as retransmissions. Missing counterparts can reflect native surface semantics
or incomplete evidence, and are not automatically execution failures. File
changes emitted only as completed items remain result-only observations.
Counts describe these groups within one supplied surface, not comparable
actions or harness quality across formats.

## Provenance and interpretation

The report identifies the entire source by hash and length. Each event index
entry records its 1-based line, 0-based byte offset, exact length including line
terminator, hash, type and classifications. Group pointers are JSON pointers
within that line's object. Input/output bodies and commands are not copied
into the report; follow its references in restricted raw custody when needed.
IDs and tool names can still be private. Keep reports restricted accordingly.

Selected native outcome fields remain observations: Codex `status` and
`exit_code`, or Claude `is_error`, with missing values null. `outcome_records`
locates turn outcomes/errors or session results; it does not assert that an
error event is terminal. Explicit Claude compaction boundaries are located
separately. Absence of such markers does not prove absence of compaction.

Native completion prose and successful session termination do not close an
unmatched call or override a reported tool error. A pair establishes only ID
and ordering agreement. The report always leaves `native_execution_linked`
false, `capture_complete` null and `work_correctness` null. It does not establish
test passage, task correctness, child ancestry, version/model identity,
representative legibility, blinding, study eligibility or acceptance. It
neither combines stdout with persisted transcripts nor replaces their existing
independent bundle and session verification.

## CLI

Use a previously retained source digest and root identity:

```sh
umask 077
python3 scripts/native_tool_pairs.py /path/to/native.stdout \
  --format claude-stream-jsonl --expected-sha256 "$RETAINED_STDOUT_SHA256" \
  --expected-root-id "$RETAINED_SESSION_ID" --max-bytes 16777216 > report.json
```

The CLI reads at most the requested limit plus one byte, rejects oversize
inputs, and emits JSON to stdout only after successful validation. Filesystem
errors propagate; it never rewrites the source. It performs no discovery or
automatic hash adoption. Caller-owned paths and custody must remain stable.
