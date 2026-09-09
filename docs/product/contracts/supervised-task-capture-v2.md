# Supervised task capture, version 2

`caplab.supervised_task_capture.SupervisedTaskCapture` records task state across
a caller-owned namespace lifetime. It complements the
[host-path wrapper](task-attempt-capture-v1.md), which remains v1. The recorder
does not launch, release, stop or wait for a workload. Its single caller owns
authorization, exact command execution, blocked setup, authenticated descriptor
handoff, task quiescence and process cleanup.

Construct it with `command`, and keyword arguments `task_root`,
`namespace_root`, `environment`, `output_dir`, `limits` and
`max_process_receipt_bytes`. `limits` is the existing `TaskCaptureLimits`.
The command and environment are copied and validated as explicit string inputs.
`task_root` is a resolved, existing host directory below `/`, used as the
declared launch working directory and preparation identity. It is not opened
for either inventory. `namespace_root` is a canonical absolute path below `/`
that identifies the task inside the namespace. Output must have a resolved
parent disjoint from the declared host task. Trusted stable host ancestry is
required; the recorder does not prove those paths' authority.

## Required lifecycle

1. Enter the context. It creates fresh private output and seals v2 `intent.json`
   before returning. The intent records command, host `cwd`, environment, limits,
   process-receipt allowance and `task_source` containing exactly
   `kind: directory-descriptor` and `namespace_root`.
2. The caller launches `capture_process` into `output_dir/process` using those
   declared command, host working directory, environment and process limits.
   A setup process creates the task namespace and blocks before task execution.
3. Receive its directory descriptor and independently expected device/inode.
   Call `capture_before(descriptor, expected_device=..., expected_inode=...)`.
   The method duplicates the borrowed descriptor, checks directory kind and
   identity, rejects overlap with output ancestry, and seals the before
   inventory. It returns that inventory's byte hash for the supervisor to retain.
4. Only after that succeeds does the caller release the workload. Wait for
   process capture and independently establish that every task writer stopped.
5. Call `finish(expected_process_sha256=...)` using an independently retained
   digest of `process/capture.json`. The recorder verifies the bounded process
   receipt and both streams, inventories the final task through its retained
   descriptor, then seals and returns v2 `attempt.json`.
6. Exit the context. The recorder closes its duplicate; the caller still owns
   the original descriptor and all process cleanup.

The caller must retain source and custody ownership throughout. The recorder
does not check that the original mount handoff was authenticated or that the
workload respected the blocked interval. An anchor computed from an untrusted
process receipt at finish time establishes only internal consistency. Neither
call order nor equal device/inode values establishes native execution identity.
The declared host-task agreement also does not prove that the namespace's
initial bytes match a frozen task input; that requires a separate content check.
The [anchored task-input API](task-input-v1.md) can create and verify those
bytes in the empty handed-off directory before `capture_before`. The caller
must seal its materialization result and connect the input and before-inventory
anchors before release; the recorder does not enforce that separate protocol.

Repeated or out-of-order calls are refused. A caught before/finish ordering
violation prevents further recording with that object. Exiting normally without
a completed finish raises `TaskCaptureError`. Exceptions preserve partial
custody and propagate; a failed recorder cannot be restarted. Existing output
directories are never reused. The recorder has no resume, retry or automatic
deletion path and emits no separate failure receipt. A known publication
exception cannot be overridden by observing a final filename afterward.

## Inventory and verification

V2 task inventories retain the existing exact file bytes, literal symlinks,
source stat observations, sorted paths and private payload objects. They add
`descriptor_identity` containing exactly `device` and `inode`, and use the
declared namespace path as `source_root`. Each scan checks its actual root
against that supplied identity. The duplicate pins the same directory through
both scans; its original host path may disappear between them.

Both scans share one task byte and entry allowance, including both root entries.
Before capture must leave room for the after root. Prefixes that fit remain
available after quota failure, but no final attempt is published. The existing
inventory stability checks remain in force. They do not make a live tree atomic
or bound blocked filesystem time. Inventory metadata, receipts and filesystem
allocation are additional storage. The positive integer process-receipt
allowance bounds the raw JSON read during finish; booleans are refused.

The [task verifier](task-capture-verification-v1.md) accepts matching v1 or v2
attempt/intent/inventory schemas. V2 requires exact source metadata, a canonical
namespace path, a positive process-receipt allowance, and equal before/after
descriptor identities matching their root stat observations. Device must be a
nonnegative integer and inode a positive integer, excluding booleans. It retains
the existing process, quota, hash and change-summary checks. V1 intents cannot
assert descriptor-source provenance. Verification opens no source task path.

V2 task inspection adds `task_source` with the namespace root, kind and observed
device/inode. Codex/Claude root linkage and byte accounting preserve this field
and require the declared task namespace to match the prepared invocation's
working directory, in addition to the existing host-task agreement. Captured
tool-pair inspection includes it in the verified `task_capture` result.
Existing v1 result shapes remain unchanged for valid inputs.

`capture_complete` still means process streams completed under their limits.
A failed process can have complete retained streams. Final task changes are
observations, and temporary writes between scans remain unobserved. No report
establishes native emission, handoff authenticity, exhaustive containment,
task correctness, study eligibility or acceptance. See the
[implementation and verification record](../../records/implementation-2026-09-08-supervised-task-capture.md).
