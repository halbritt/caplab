# Reference repair (one possible good repair, not the only one)

The repair treats the digest as a *view for a reader with a fixed budget*,
rendered over an event log that stays exactly as it is.

**Name the consumer and the budget.** `digest.py` gains an explicit cap —
e.g. `MAX_ENTRIES = 20` — with a comment saying whose budget it encodes:
the on-call reader gets one screen, readable in under a minute. The cap
is a deliberate module-level decision, not an incidental slice buried in
a loop.

**Rank by decision-relevance, not arrival.** Reportable events are
grouped and the groups ordered with `crit` entries first, then `warn`;
within a severity class, ordering is by something decision-useful
(occurrence count or recency), never by when the event happened to land
in the log. The db-01 backup failure is now the first content line of
the digest regardless of when it occurred.

**Deduplicate repeated reasons.** Events sharing the same
`(host, check, status)` collapse into one entry carrying an occurrence
count and a first-seen/last-seen span, plus the latest message — e.g.
`[WARN] storage-03 io_latency — 720x between 20:00 and 07:59: p99 read
latency 480ms...`. One flapping check is one line, however long it
flapped.

**Bound the total and signpost the overflow.** If there are more groups
than the cap, the digest ends with an explicit omission line stating how
many groups (and how many underlying events) were left out and where the
complete record lives — the event-log path, which `cli.py` now passes
into `render_digest` so the pointer is concrete. Nothing is silently
cut.

**Leave the canonical data alone.** `eventlog.py` is untouched: every
event is still appended and retained, `prune` remains the only sanctioned
rewrite, and rendering never writes back, marks events as reported, or
compacts the JSONL. The unbounded log is the archive; the digest is the
budgeted brief that points at it.

**Tests untouched.** The existing suite passes unmodified: the digest
still carries the date header, still says "All clear" when there is
nothing reportable, still names the affected hosts and checks, and still
omits healthy results.
