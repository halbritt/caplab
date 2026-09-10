# Buffered exec trace retention, version 1

`buffered_exec_trace(max_bytes=..., quarantine_factory=...)` owns an anonymous
Linux memfd. Its borrowed `path` lets an outside strace process open the buffer
without passing a descriptor into the workload. The buffer itself creates no
durable file. Its lifetime is the context; callers must not reuse its descriptor
or path after exit. A trusted quarantine factory is required.

The caller owns the tracer and workload, caps writes with RLIMIT_FSIZE, bounds
their lifetime, prevents core dumps and swap retention, and stops writers before
calling `retain(path)`. The buffer permits at most 32 MiB, refuses an empty trace
or a trace that reaches its selected limit, and does not itself enforce a live
producer's memory or time limit. Context cleanup closes its descriptor; it does
not stop a producer or promise memory erasure.

Retention has one attempt. It seals writes, growth, shrinkage and further seal
changes, then reads the immutable bytes. It checks the complete raw stream and
each decoded quoted string under the same quarantine policy. The supported
format is strace `-xx`: every quoted string consists only of lowercase `\xNN`
bytes. Non-ASCII raw text, malformed or unterminated quotes, quoted-string
abbreviation and an incomplete final line refuse retention. Arbitrary further
encodings or secrets split across distinct argv/environment strings are outside
this policy. This format check does not establish complete syscall coverage or
successful native execution.

Only after all checks pass does retention exclusively create a mode-0600 trace
under the caller's trusted, stable, private parent, write the unchanged bytes and
fsync the file and directory. Quarantine or input-format refusal creates no
trace. Existing output is never overwritten. An I/O failure can leave a safe
partial file, which has no completed retention receipt and remains unavailable.

The returned `caplab.exec-trace-retention/v1` record names the anonymous source
identity, retained file identity, byte count/hash, limit, decoded-string count
and required kernel seals. Caller-owned guarded publication anchors this record.
It does not authenticate its own origin or select a credential policy.

## Kernel provenance and inspection

`observe_exec_tracer()` accepts the live buffer and emits
`caplab.exec-tracer-observation/v2`, with `trace_storage: sealed-buffer/v1`.
The original tracer, namespace, cgroup, executable and writable-descriptor checks
still apply. The observed peer must neither have the buffer descriptor nor
resolve the supervisor's buffer path to that file. The anonymous file identity
is recorded before native release. No final copied-file identity is invented.

`verify_exec_tracer(..., trace_retention=...)` requires the separately anchored
retention record for v2. It joins the observed anonymous identity to the retained
file's exact inode and bytes and rechecks the encoded-string count/format.
This is recorded custody consistency; it does not independently rerun the
credential owner's secret policy. File-backed v1 observations retain their old
same-inode rule and refuse a supplied buffer-retention link.

## Scripted diagnostic selection

`prepare --trace-profile sealed-buffer/v1` requires routed/v2, cgroup-usage/v1
and supervisor-poll/v1. It creates preparation v7 with an explicit trace profile.
Omission preserves preparations v1-v6 and their existing file-backed behavior.
The worker checks the selection against preparation and keeps the buffer outside
the workload. The 2 MiB strace file ceiling and existing zero-swap/core, process
and cgroup limits remain. After execution and writer shutdown, it retains the
trace and seals `safe-trace-retention.json` before completing capture.

Inspection requires that artifact and a v2 tracer observation for v7. A missing
artifact leaves capture unavailable; changing the profile or joining a different
source or copy is refused. Historical captures are neither migrated nor
retroactively certified by the new profile. Synthetic native diagnostics remain
ineligible for representative repair or reviewer-capability conclusions.
