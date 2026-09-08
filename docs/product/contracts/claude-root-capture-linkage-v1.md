# Claude root capture linkage, version 1

Status: implemented read-only session field comparison. See the
[decision and verification](../../records/implementation-2026-09-08-claude-root-capture-linkage.md).

`caplab.claude_capture_link.link_claude_root(policy_path, task_custody,
collection_custody, *, expected_attempt_sha256, expected_collection_sha256,
max_receipt_bytes, max_identity_bytes)` compares the configured Claude session
UUID with retained stdout and a retained root transcript. The caller supplies
independently retained hashes of task `attempt.json` and native `collection.json`,
an authorized inspection scope, quiescent custody and trusted stable host parents.
The function writes nothing and launches no process.

## Retained evidence

The existing [task](task-capture-verification-v1.md) and
[native collection](native-collection-verification-v1.md) verifiers check both
referenced bundles first. A joint bounded pass rereads seven hash-linked receipts:
collection, collection intent, preparation, invocation, task attempt, task intent
and process capture. The canonical invocation must name `claude-code`. The
preparation's recorded task source must equal the task intent's cwd; neither
original source path is opened. Matching paths are metadata consistency, not
proof of a shared physical execution.

The reader selects exactly one inventory entry below `session_search_root/`
whose basename equals the configured UUID plus `.jsonl`. It must be a regular
file directly beneath one project directory. Duplicate exact candidates anywhere
in the session tree, a nested candidate, a selected symlink, and missing exact
names fail. No glob, substring match, project-directory encoding guess or search
of native homes supplies a substitute. The project directory is not independently
attested as the task's project. Other retained files remain unparsed.

The retained stdout and selected transcript object are reread with exact size,
SHA-256 and descriptor/path stability checks. The pure
`claude_root_session_fields(stdout, transcript, *, session_id)` callable handles
these already-bounded bytes. Both inputs must end in LF and contain nonempty
UTF-8 JSONL object records with nonblank string types. Duplicate keys, non-finite
numbers, blank records and partial final records fail. Splitting is on LF only;
Unicode separators inside text are preserved. Text is never searched for IDs.

Stdout uses the existing native session observation rules: nonblank
`parent_tool_use_id` scopes supported message types away from the root; invalid
scope values or conflicting root IDs fail. Exactly one `system/init` must appear
first and carry the configured `session_id`. All explicit root IDs must agree;
root user, assistant and result records must carry that ID. A terminal result
is not required for session agreement.

For persisted records, the official reader identifies `sessionId`, `uuid`,
`isSidechain`, `isMeta` and `teamName`. User/assistant messages outside sidechain,
meta and team scopes supply root evidence. See the pinned
[official reader](https://github.com/anthropics/claude-agent-sdk-python/blob/f1315c69a74db1c15fed2e5974918495d90b7d57/src/claude_agent_sdk/_internal/sessions.py#L1023)
and its [fixture builder](https://github.com/anthropics/claude-agent-sdk-python/blob/f1315c69a74db1c15fed2e5974918495d90b7d57/tests/test_sessions.py#L645).
CAPLAB requires present boolean flags to be actual booleans; team scope is absent,
null or a nonblank string. Every provided persisted session ID must be nonblank,
and every root-scoped ID must equal the configured ID, including metadata records.
Every user/assistant record needs a nonblank UUID. At least one root message must
carry the configured ID. Non-root messages cannot satisfy that requirement.

This is a strict field-comparison subset, not the SDK's transcript reconstruction
algorithm or a full native-format validator. It does not follow `parentUuid`,
choose a conversation branch, prove unique message UUIDs, validate message bodies
or silently discard malformed lines. Native compatibility remains unverified
until a separately authorized capture exercises the installed CLI.

## Bounds, report and failure

Both allowances are positive integers excluding booleans. Each initial bundle
verification and the joint metadata reread has its own `max_receipt_bytes`
allowance. The initial verifiers retain their anchored payload limits; the
additional stdout and transcript bytes share `max_identity_bytes` before
accumulation. The pure parser expects its caller to bound supplied bytes. Reads
use chunks no larger than 65,536 bytes; parsed memory is proportional to bounded
input. Blocked filesystem I/O has no wall-time guarantee. The separate trusted
policy file is outside custody allowances.

The `caplab.claude-root-capture-link/v1` report records both independent anchors,
configured tuple/profile/invocation identity, stdout and transcript hashes, the
logical transcript locator, session ID and observation counts, receipt/identity
byte counts and the task verifier's process outcome. It omits raw prompts,
commands, message bodies and source host paths. `root_id_agrees` and
`recorded_task_root_agrees` are true. `reported_tuple_agrees` and
`native_capture_complete` remain null. `executed_invocation_bound`,
`conversation_chain_verified` and `child_linkage_verified` remain false.

Non-root observations and `other_session_files` are counts, not verified child
lineage. Model, effort, CLI version, account, provider, genuine native emission,
containment, task success and eligibility are not attested. A nonzero or timed-out
process can retain matching IDs; its outcome remains visible. The task process
may be an outer command that this reader cannot bind to the frozen invocation.
No admission, qualification, replay or human judgment follows from the report.

Invalid, missing, ambiguous or contradictory evidence raises
`CaptureVerificationError`; filesystem errors propagate. There is no recovery,
retry, write or fallback. Known capture failures remain controlling. Verification
and rereads are not an atomic multi-file snapshot. Selected identity objects are
rechecked; other payloads changing after their initial check violate the caller's
quiescence requirement.
