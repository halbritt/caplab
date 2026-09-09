# Bounded process streams, version 1

Status: implemented component; native campaign integration unverified.
Owner: CAPLAB. Decision and verification:
[implementation receipt](../../records/implementation-2026-09-08-bounded-process-capture.md).

This component implements the stdout/stderr part of
[CAPLAB-79's prospective capture design](../../records/decision-2026-09-08-caplab-79-capture-design.md).
It does not implement the entire episode recorder or authorize a launch.
Existing frozen native runners do not call it. CAPLAB-84 remains open.
The prospective [task-attempt wrapper](task-attempt-capture-v1.md) now calls it
between sealed task inventories; this does not establish native integration.

## Interface and owner responsibilities

`caplab.process_capture.capture_process(command, *, cwd, environment,
output_dir, max_stream_bytes, timeout_seconds, pass_fds=(), quarantine_factory=None)` launches one argument-vector
command, with stdin closed and an explicit environment. The caller must supply
an absolute working directory, a fresh absolute output directory under a
trusted resolved parent, a positive integer combined stream limit, and a
positive finite timeout. There are no inherited-environment, byte-budget,
working-directory, shell, or timeout defaults. Empty argument values are
permitted; the executable argument must be nonempty.

The function snapshots each input container before validating its entries;
both the argument tuple and environment dictionary are owned before creating
custody. Later changes to the caller's
containers cannot change what is launched. The caller must keep inputs stable
while those initial snapshots are made; this does not synchronize writers or
make arbitrary custom containers atomic. String entries are immutable, so
shallow snapshots suffice. No ambient environment is merged into the snapshot.

`pass_fds` optionally names extra POSIX descriptors that the launched program
may inherit, at their existing numbers. Its empty default passes none. The
sequence is snapshotted before setup; entries must be unique exact integers
greater than 2. Strings, bytes, non-sequence containers, booleans, standard
stream numbers and duplicates raise `ValueError`. Each descriptor is checked
with `fstat` before custody opens any files, so an already-closed number cannot
silently become a capture file; a closed descriptor raises `OSError`.
`Popen(close_fds=True, pass_fds=...)` excludes other extra descriptors even if
they are inheritable in the parent.

The descriptors remain borrowed. The caller keeps them open and their identities
stable until return; concurrent close/reassignment is outside this contract.
Capture does not read, hash, seek, duplicate, close or change the parent's
inheritable flags on them. A child shares their open-file-description state,
including offsets and access permissions; borrowing does not imply immutable
input. The input-descriptor contents are not added to capture metadata, but
without a quarantine factory, bytes emitted by the child enter raw stdout/stderr capture. This is
a transport facility, not credential validation, redaction, or authorization.
Callers own sealing/read-only delivery, closure before final subject exec,
and secret handling. See the [descriptor implementation record](../../records/implementation-2026-09-08-capture-input-descriptors.md).

## Optional output quarantine

`quarantine_factory` is a trusted callable, invoked once for stdout then once
for stderr before custody creation or launch. It returns distinct fresh gates
implementing `StreamQuarantine`: `feed(bytes) -> bytes`, `finish() -> bytes`,
`abandon()`, and a `quarantined` flag initially exactly `False`. The existing
Revbench `SealedCredential.stream_quarantine` method satisfies this interface;
the recorder imports no provider adapter and parses no credentials. Gate
construction and private data/buffering bounds belong to the caller. Factory
calls precede the capture deadline; this is not a sandbox for untrusted code.

The recorder checks methods, initial flag and distinct identity before launch.
It adopts each returned object's callable `abandon` even when another shape
check rejects it; a duplicate object is cleaned once. A rejected object without
a callable cleanup method cannot be cleaned by this interface. Factory and
gate exceptions propagate; their implementation must not disclose secrets in
exception messages. Type annotations do not validate gate policy.

During capture, `feed` withholds possible secret prefixes before the disk sink.
`finish` releases safe buffered bytes only at observed EOF. The flag must remain
exactly `False` before any returned bytes can be written. The received byte
allowance includes withheld overlap, so buffering does not extend the limit.
A gate cannot emit more bytes than its stream has received, and all emitted
values must be bytes. Before completion publication, each stream's emitted
length and SHA-256 must match its original received bytes. These checks reject
silent transformations, loss and reordering; they do not prove the supplied
gate recognizes the right secrets or validate intermediate emitted prefixes.

A secret match or invalid runtime flag raises `ProcessCaptureQuarantineError`
with `capture output quarantined`. Altered/non-byte/excess output uses
`quarantine changed raw stream`. Timeout or quota exhaustion in guarded mode
raises `guarded capture incomplete: timeout` or `guarded capture incomplete:
byte-limit`. The child group is terminated and reaped, pending gate data is
abandoned, and no final receipt is published. Safe prefixes already written
remain in private failure custody; no public receipt or automatic retry is
created. A missing receipt is unavailable capture, never zero-cost success.
Gate cleanup completes before receipt publication, including after normal
native failure. Successful guarded capture retains the unchanged v1 schema
and exact raw streams; nonzero native exit may still have complete streams.

The default `None` retains existing behavior, including incomplete receipts
for unguarded timeout or quota stops. The optional seam has no credential
policy identifier in v1; an adopting adapter must freeze the factory, private
policy source and its authority separately. A receipt alone does not prove a
quarantine was selected. Known-value matching does not detect transformed,
encoded, cross-stream fragmented or unknown secrets, or protect persisted
native files and task inventories. This is not coder blinding or full-surface
privacy acceptance. See the [implementation record](../../records/implementation-2026-09-09-process-output-quarantine.md).

## Remaining caller responsibilities

The caller owns execution authorization, exact subject/instrument identity,
command/configuration custody, task and account isolation, disk reservation,
and campaign accounting. It must put capture outside subject-writable mounts.
This helper does not make an arbitrary command safe to execute or substitute
for the native harness. It launches a new process session so cleanup can target
that process group without terminating sibling attempts.

The output directory is created with mode 0700; files use mode 0600 and
exclusive creation. An existing directory, including a symlink, prevents launch.
No resume or overwrite path exists. A failed attempt directory remains occupied;
a caller must not delete it and replay the same assignment as if it never ran.

## Stream and completion semantics

A synchronous selector loop drains both pipes into `native.stdout` and
`native.stderr`. Bytes are retained without decoding, normalization, or
line-oriented parsing. The read buffer is at most 65,536 bytes; short writes
are completed before the next read. This bounds payload buffering for this
component, not the Python process's total memory or other capture surfaces.

`max_stream_bytes` applies to stdout plus stderr, not independently to each.
At most one extra byte is read to distinguish an exactly full but complete
stream from overflow. The extra byte is not retained. On overflow, retain each
stream's prefix and terminate the launched process group. Scheduling determines
how the remaining shared allowance is distributed between ready pipes; do not
interpret cross-stream read order as native action order.

The receipt `capture.json`, schema `caplab.process-capture/v1`, records:

- `termination`: `exited`, `byte-limit`, or `timeout`;
- the leader's actual `return_code`, including negative signal codes;
- `streams_complete`, true only when both pipes reach EOF and the leader exits
  before the deadline without exceeding the limit;
- the configured allowance/deadline and retained combined byte count;
- each stream's path, byte count, SHA-256, EOF observation, and first/last
  nonempty-read monotonic receipt timestamps;
- host UTC start/finish times and monotonic start/finish timestamps.

Host read timestamps are not native execution timestamps. First/last receipt
bounds are not a per-event timeline. Empty streams have null read timestamps.
A quota-triggering read can include an unretained byte; these timestamps describe
reads, not only retained bytes. Native timestamps and tool causal links belong
to later parsing of preserved native surfaces.

`streams_complete` can be true with a nonzero exit code: all output was captured,
but the child failed. Conversely, an exited leader can have return code zero
and `streams_complete: false` if a descendant retains its pipes past the
deadline. EOF without leader exit also does not complete the attempt.
Callers must check termination, completeness **and** return code before any
native parsing or outcome interpretation. Capture success never establishes
model identity, task success, review validity, or acceptance.

The deadline includes setup and subprocess execution as observed by the polling
loop. It does not interrupt a blocked kernel spawn or storage operation. Cleanup
sends SIGKILL to the launched process group and waits up to five additional
seconds for the leader. Same-group descendants are also targeted when the
leader has exited; this is not a guarantee about descendants that escape the
group. External containment and a supervisor remain required. A timeout is not
permission to retry or continue a campaign.

## Failure custody and durability

Raw streams are synced before a receipt is published. Receipt bytes are written
to `.capture.pending`, synced, and linked exclusively to `capture.json`; the
pending name is removed and output/parent directories are synced. A receipt
publication error propagates. On a directory-sync error, the just-published
receipt is removed when the filesystem permits; any cleanup failure is also
an error. Receipt presence alone must not override an observed capture exception.
This is local filesystem durability, not independent custody replication.

Launch, read, write, sync, and cancellation failures propagate. Once launched,
the child group is terminated and the leader reaped before an exception returns,
subject to the stated cleanup deadline. Retained prefixes remain available for
restricted failure inspection. A partial `.capture.pending` is not a completion
record; a directory with no valid final receipt is not an eligible episode.
No exception becomes an empty successful result. No native source is deleted.
Both child pipes are owned before nonblocking setup or selector registration,
so a setup failure closes both as well as terminating/reaping the child.

Under CAPLAB-79, quota overflow, incomplete capture, and storage failures stop
the campaign. The future campaign adapter must enforce that rule and keep the
assigned denominator; this component cannot enforce continuation in a caller
that ignores its result or exception. Receipt/data hashes must be verified again
at any later custody or interpretation boundary.

## Remaining integration and measurements

The stream allowance excludes receipt metadata, filesystem allocation, persisted
sessions/children, diagnostic files, prompts, configuration, and task inventories.
A future authorized manifest must reserve those bytes separately and enforce
combined episode/campaign limits, concurrent-copy allowances, and free-space
reserves. The component adds no numeric study budget.

CAPLAB-84 still needs native adapters that preserve all selected session and
diagnostic surfaces, link them to the launched session, retain before/after
write-set inventories, apply frozen source identities, and stop continuation
on capture failure. CAPLAB-66 still needs valid coder-blinding verification.
Representative repair captures are needed for bytes, latency, redaction cost,
legibility and native compatibility claims. The local synthetic process tests
establish none of those empirical quantities. No historical shakedown budget
is renewed by this component.
