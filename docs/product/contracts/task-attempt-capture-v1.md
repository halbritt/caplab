# Task state and process capture, version 1

Status: implemented prospective component. Native adapters and campaign
eligibility are not implemented by this interface. Decision and verification:
[implementation record](../../records/implementation-2026-09-08-task-attempt-capture.md).

`caplab.task_capture.capture_task_attempt(command, *, task_root, environment,
output_dir, limits)` retains the task tree before and after
[bounded process capture](bounded-process-capture-v1.md). `limits` is a
`TaskCaptureLimits(max_stream_bytes, max_task_bytes, max_task_entries,
timeout_seconds)` value. Every limit is explicit; integer limits must be
positive and the timeout positive and finite. Boolean limits are rejected.

The caller owns execution authorization, the exact native subject and source
binding, containment, campaign accounting, reserved storage, and trusted source
and custody parents. The task tree must be quiescent at each inventory boundary.
Only the explicitly supplied command and environment are used. Their copies,
the working directory and limits are sealed in private `intent.json` before
task capture or launch. The command/environment themselves must be authorized
capture inputs; this component does not redact them.

## Ordering and retained evidence

1. Create fresh private custody outside the task tree; refuse reuse.
2. Seal `intent.json` and `before/inventory.json` before starting the process.
3. Retain the process's bounded streams and `process/capture.json`.
4. After process-group cleanup, seal `after/inventory.json`.
5. Publish `attempt.json`, linking the three component receipts and intent by
   SHA-256 of their exact bytes, with the process result and observed changes.

Inventory schema `caplab.task-inventory/v1` records the source root, UTC scan
bounds, retained logical bytes and sorted entries. Each entry has a task-relative
path, permission/special mode bits, kind and source stat observations (device,
inode, mode, link count, size, modification time and change time). Root `.` is
included. Regular files retain exact bytes in numbered `object-*` files with
byte count and SHA-256; all regular-file paths are included, without Git or
basename exclusions. Multiple hard-linked paths retain separate copies and
count separately; their source inode observations remain visible.

Directories include empty directories. Symlinks retain their literal target as
base64-encoded filesystem bytes and are never followed, including dangling or
external links. Names use the host filesystem encoding with surrogate escape;
JSON escaping preserves non-UTF-8 names for round trips through `os.fsencode`.
Sockets, FIFOs and device nodes are unsupported and fail capture explicitly.
No permission or owner metadata from a task file is applied to custody files.
Custody directories use 0700 and files 0600.

The attempt schema is `caplab.task-attempt-capture/v1`. `changes` lists added,
deleted and modified paths; modifications name differences in kind, mode, byte
count, content hash or link target. Inode/time observations and custody object
names are excluded from that comparison. A rename appears as deletion/addition;
equal hashes can support further analysis but do not prove a rename operation.
No inference about every intermediate write or executed tool call is made.

## Limits, failures and completeness

`max_task_bytes` is a combined allowance across both inventories for regular
file bytes and literal link-target bytes. `max_task_entries` likewise counts
both inventories, including both root entries. The before allowance is not
reset for the after scan. Retained regular-file buffering uses chunks of at
most 65,536 bytes. A quota check may read one unretained byte to detect overflow;
regular-file prefixes already retained are kept. Inventory metadata, intent,
receipt bytes, filesystem allocation and source copies are additional storage.
These limits do not replace the full episode/campaign storage reservation.

Directory enumeration is bounded by the remaining entry allowance. Traversal
uses directory descriptors and refuses following links when opening files or
directories. File stat observations are checked before/after copying and
against the path; directory entries and stat observations are checked again
after traversal. Observed changes, unavailable paths or read errors stop capture.
These checks do not make a live filesystem atomic: changes outside the checked
interval, escaped writers and changes before observation still require external
quiescence/containment. Trusted parents must remain stable throughout capture.

The timeout bounds the process polling window, not the inventory scans or
blocked filesystem operations. Stream timeout/overflow still allows a final
task inventory, but `capture_complete` is false. A nonzero process exit can
have complete capture; task success and test success must use the actual exit
status and retained output. Capture completeness is not native identity,
instruction compliance, blinding, qualification or campaign eligibility.

Inventory, launch, storage and publication exceptions propagate. There is no
final attempt receipt on these failures; partial component custody remains and
must not be treated as a completed eligible attempt or an unused assignment.
`TaskCaptureError` records `failure.json` (`caplab.task-capture-failure/v1`)
with its phase, exact reason, intent byte hash and truncation flag before
propagating. Task byte/entry limits set that flag true; source-change and
unsupported-object errors set it false. A failure receipt is not a completed
attempt. Filesystem errors can prevent this record and still propagate.
After a process-capture exception, the wrapper does not attempt a final scan.
Component receipts do not override a failed parent attempt. Pending JSON files
are unsealed; receipt publication syncs file and directory state using the
shared capture publisher. Later consumers must reverify component and object
hashes before interpretation; the [read-only integrity verifier](task-capture-verification-v1.md)
implements that check against an independently retained attempt digest.

For a task created inside a blocked namespace, use the separate
[supervised v2 recorder](supervised-task-capture-v2.md). It seals intent before
supervisor launch, then inventories an identified directory descriptor before
work is released and after writers stop. It preserves v1's byte/entry accounting
while making the namespace source and external supervisor responsibilities explicit.
The wrapper is not an admission or replay API.

CAPLAB-84 still requires native session/child linkage, diagnostics, exact binding
enforcement, campaign stops and representative capture-cost measurements.
CAPLAB-66 still owns blinding feasibility. No historical budget or campaign
manifest is renewed by this component.
