# Exact native session lookup, version 1

Status: implemented in the artifact-rater and closed ladder lookup helpers.
Decision and verification:
[repair receipt](../../records/repair-2026-09-08-native-session-lookup.md).

`caplab.artifact_rater.find_rollout(sessions_root, thread_id,
timeout_seconds=10.0)` locates one candidate for subsequent preservation and
attestation. It enumerates filenames and filesystem metadata; it does not read
rollout bodies, select a model, launch a process, or admit evidence.

## Discovery contract

The caller supplies an absolute resolved search root. The two existing script
wrappers retain their home-based `.codex/sessions` root. That is not a claim of
isolated runtime capture: future CAPLAB-79 adapters must supply the exact
isolated episode runtime and satisfy its separate capture requirements.

A supported filename has the shape
`rollout-YYYY-MM-DDTHH-MM-SS-<thread-id>.jsonl`. The complete ID after that
fixed-width timestamp prefix must equal the requested ID. Timestamp text is
not parsed as an event time or used to rank candidates. This is CAPLAB's
versioned discovery grammar, not proof that every native release uses it.
Unrecognized names remain unavailable; there is no substring or newest-file
fallback. Validate the selected native version before an authorized campaign.

Requested IDs are literal ASCII components: one alphanumeric character followed
by zero or more alphanumeric, underscore or hyphen characters. No glob syntax,
path separators, whitespace, case folding or Unicode normalization is allowed.
Unsupported IDs fail before traversal. This identifier grammar is a lookup
boundary, not a complete provider-identity schema.

The search must find exactly one regular non-symlink candidate. Two paths with
the same complete ID are ambiguous even when their names, dates, sizes, or bytes
might suggest an ordering. The helper does not open them to resolve the tie.
A matching directory or FIFO is an error. A linked search root, linked ancestor,
or linked descendant directory is an error; traversal cannot silently skip a
possible second candidate and then claim uniqueness. Unrelated file symlinks
are not followed. An enumeration or candidate-metadata error prevents return.

No-match searches may wait for a newly created candidate. The default remains
ten seconds; an explicit zero permits one immediate scan. Negative, Boolean,
non-numeric and non-finite deadlines are rejected. Polling uses a monotonic
clock and sleeps at most the remaining time. The deadline bounds repeated
waiting; it cannot interrupt a blocked filesystem operation or make directory
enumeration an atomic snapshot.

The shared helper raises `CalibrationError`. The artifact-rater wrapper keeps
that error; the ladder wrapper translates it to `NativeSubjectError`. Neither
wrapper chooses a candidate or retries after ambiguity. The ladder's `run`
entry point remains unconditionally closed before effects.

## What a returned path does not establish

A filename match is not a content identity. The existing
`preserve_rollout_attestation` path must retain bytes before interpreting them,
verify the retained hash, and check session metadata against the stdout thread
ID and complete turn-context model/effort observations. Those checks remain
unchanged. A matching filename with another session's body must fail there.
Already retained recovery evidence keeps its existing hash and identity checks;
this repair does not rewrite past captures or apply new discovery retroactively.

Uniqueness is only the result of this directory observation. A file can change,
a new duplicate can appear, or a path can be replaced after lookup. Lookup
neither locks the native runtime nor proves stable source bytes. CAPLAB-79's
future recorder still needs stable capture/sealing, complete session/child
linkage, quotas, diagnostics, task inventories and native configuration checks.
Directory traversal may reveal other filenames under the supplied root; the
caller must have authority to enumerate that root. No actual home session tree
was scanned to verify this repair.

This policy supports trustworthy linkage but establishes no reviewer accuracy,
quality effect, qualification, routing order, or independent acceptance.
