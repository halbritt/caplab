# Bounded process streams, version 1

Status: implemented component; native campaign integration unverified.
Owner: CAPLAB. Decision and verification:
[implementation receipt](../../records/implementation-2026-09-08-bounded-process-capture.md).

This component implements the stdout/stderr part of
[CAPLAB-79's prospective capture design](../../records/decision-2026-09-08-caplab-79-capture-design.md).
It does not implement the entire episode recorder or authorize a launch.
Existing frozen native runners do not call it. CAPLAB-84 remains open.

## Interface and owner responsibilities

`caplab.process_capture.capture_process(command, *, cwd, environment,
output_dir, max_stream_bytes, timeout_seconds)` launches one argument-vector
command, with stdin closed and an explicit environment. The caller must supply
an absolute working directory, a fresh absolute output directory under a
trusted resolved parent, a positive integer combined stream limit, and a
positive finite timeout. There are no inherited-environment, byte-budget,
working-directory, shell, or timeout defaults. Empty argument values are
permitted; the executable argument must be nonempty.

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
