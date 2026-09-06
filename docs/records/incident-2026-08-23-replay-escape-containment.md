# Incident — a replayed build case escaped an agy lane into the live tree

- Date: 2026-08-23. Postmortem by the detecting session:
  `/tmp/scheduler-overwrite-postmortem-2026-08-23.md` (striatum-side).
  This record is CAPLAB's: the generating process was ours.
- What happened: at 17:56:20Z the CAPLAB remeasurement sweep
  (`remeasure-agy-flash-high-20260823`, agy harness,
  `--dangerously-skip-permissions`, 4 lanes) replayed a change-set case
  (`c70d14e4ac76d99c`, packet `scheduler-qualification-withholding-network`)
  and the lane wrote the case's delivery — byte-identical — into the live
  `~/git/striatum-next` checkout: three scheduler files regressed to
  pre-RFC-0019 content. Found by `git status` ~40 minutes later, stashed as
  evidence, restored; never committed. A sibling case 26 seconds later
  named a file carrying uncommitted repair work and did not escape.
- This is the second occurrence: `stash@{2}` records the same shape on
  2026-08-19 05:12Z (the seed-20260819 flash sweeps ran that day). The
  class went unexamined then; it does not now.

## Why it happened — CAPLAB's side

The review contract presents a change set whose files name live
repository paths, to an agentic harness with full filesystem access as
the login user, on the host that holds the live checkout. The measured
model did what the artifact suggested — applied it. The v2 contract
forbade *searching* the filesystem (the OOM fix) but said nothing about
*writing*. No mechanism on the CAPLAB side noticed a live-tree write.
Sandbox posture is a per-harness fact: codex declares
`--sandbox workspace-write`; agy has no equivalent and neither did the
sweep wrap it in one.

## Durable fixes (landed this record)

1. **Filesystem containment, default-on.** Every adapter invocation now
   runs under bubblewrap (`pool_runner.sandbox_argv`): root read-only,
   the user's home writable (harness configs, caches, opencode's db),
   **`~/git` bound read-only on top**, only the case workspace re-bound
   writable, `/tmp` shared, `--die-with-parent`. Verified live: agy,
   codex (its own nested sandbox survives), claude-code, opencode, and the
   stdin lane all answer inside it, and a write into the live checkout
   fails with `Read-only file system`. Every row records `sandbox: bwrap`;
   `CAPLAB_NO_SANDBOX=1` opts out explicitly, never silently.
2. **The contract says so too.** A `REVIEW ONLY` preamble (version 1,
   recorded on every row) now heads every review contract: no creating,
   modifying, or writing files, no state-changing commands, the artifact
   is not to be materialized. The sandbox is the containment; the
   preamble makes a violation a measured contract breach rather than an
   accident — a subject that writes anyway is now saying something about
   itself.
3. **Notice, don't find.** The supervisor snapshots tracked modifications
   in `~/git/striatum-next` and `~/git/caplab` before each attempt and
   compares after; any change stops the run (exit 7) and leaves the tree
   untouched as evidence (`caplab.advisory.treeguard`).

## Comparability note

Rows before 2026-08-23 carry no preamble and ran unsandboxed
(`sandbox`/`review_preamble` absent). Sandboxing cannot change a
review verdict; the preamble adds 60 words to the prompt and could in
principle shift emission style. Sweeps comparing across the boundary
should say so. Both remeasurement runs of 2026-08-23 predate these
changes and are unaffected in content.

## Offered to striatum

The postmortem's §7 options are the Principal's. From CAPLAB's side: the
agy declaration could state its sandbox posture (none) as a capability
fact, and `live-tree-matches-head` on a cadence would have cut the
40-minute window to seconds for everyone, not only for CAPLAB sweeps.

## Amendment 2026-09-06 — what the sandbox actually contained

Council plan `tree-v1` revision 2 (§0, §2.2) found that the containment this
record describes was narrower than its words. Between 2026-08-23 and the
Stage A amendment of 2026-09-06, `pool_runner.sandbox_argv` bound `/`
read-only, then the whole home directory writable, then a tmpfs over `~/git`.
Every lane could therefore read and write `~/.local/share/striatum` (the graph
store, exchange, keys and deploys — ~134 GB), `~/.local/share/striatum-tuner`,
`~/.cache` (~73 GB), and `~/.config/plane` (API tokens). `treeguard` watched
tracked files in two git checkouts and nothing else. The plan of 2026-09-06
revision 1 asserted that "the store stays masked"; it did not. Stage A masks
those paths with tmpfs and re-binds only the harness's own config directory
(and `~/.cache/go-build` for agy) writable; Stage B replaces home with an
allowlisted synthetic home before any model process runs. Both are recorded
in the tree-v1 plan and verified by the probes it specifies.
