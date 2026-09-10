# Council provider lifetime witness: bounded development execution

Authority: active reviewer-ranking goal, owner outcome-validity instruction,
and ADR 0026 delegation, exercised by the CAPLAB primary agent. This follows
ADR 0066 and the fixed sample's source-inspection authorization.

Authorize a local behavioral reproduction for sampled Council change
`19fb83494cf3ec8e338d748f566be3df21088a40`. Inspect and materialize tracked
source at the following exact commits from `/home/halbritt/git/council`:

| Role | Commit |
|---|---|
| Original runtime introduction identified by blame | `9c66a76836245fbc8d203812a4a36f475341ce0e` |
| Sampled change's original base | `32c9f09674b27b185abb7498883d9d3495ac4951` |
| Sampled change's resulting tree | `19fb83494cf3ec8e338d748f566be3df21088a40` |

Copy tracked regular-file bytes, with original paths, commit/tree/blob IDs,
content SHA-256 and length manifests, into a fresh owner-only directory under
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/timeout-witness-1`.
Reject unexpected symlinks or object identity mismatches. Source snapshots
remain read-only during execution. Preserve all original repositories.
This explicitly names the historical source-copy effect for local diagnostic
custody only; it admits no experimental evidence and assigns no historical
human judgment. The original-introduction case is a lineage follow-up, not a
replacement for any of the fixed 32 sampled cases.

Construct a CAPLAB witness that invokes the actual exported
`runDeepSeekMemberTurn` function against a local HTTP server. Exercise ordinary
completion, headers followed by delayed body, cancellation during body, and
an already-aborted signal. Retain request counts, header/body/cancellation
times, return status/code, and elapsed time. Freeze the witness before its
first execution. The expected observable is derived from the existing
timeout/cancellation interface and protocol, not from reviewer responses.
The repair author's test remains corroboration, not the sole truth source.

At most 36 diagnostic invocations, at most 15 seconds per process and eight
minutes total. Three repetitions per condition and source version. Use the
installed Node executable and Council's existing TypeScript loader dependencies;
record executable and dependency identities. No downloads or install scripts.
Run under Bubblewrap with a private network namespace, only loopback HTTP,
read-only source/dependency mounts, empty home, cleared environment, private
temporary storage, and synthetic credentials. No external provider, native
reviewer, production service, host timer, host ledger, or paid call is involved.

Stop on source drift, unavailable isolation, malformed witness output, or
unexpected execution effects. Retain failures and incomplete attempts. A
failed diagnostic is not a reviewer miss. Cleanup kills the owned process
group, closes the local server, and removes transient namespace state; preserve
source snapshots, witness, inventories and safe logs for reproducibility.
Authorization expires after this run series, on goal cancellation, or at
2026-09-11T17:25:10Z, whichever occurs first. This authorizes investigation,
not a declaration that a whole patch is clean or that any reviewer ranks higher.
