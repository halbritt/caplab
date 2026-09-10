# Verify the selected Reddit harvest recovery boundary

Under ADR 0026 and the active reviewer-ranking goal, authorize private
development custody at
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/reddit-recovery-witness-1`.
Copy exact tracked `newsroom/`, `config/`, `README.md` and `pyproject.toml`
blobs from ai-newsroom base `1bfe5a656bcb2c663891afd5f980211a3ef144a8`
and selected change `544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f`. Pin full
commit/tree/path/blob/SHA-256 provenance. Preserve original source unchanged.
The new `reddit_state.py` is absent at the base; do not invent a passing base
implementation or score unsupported base calls as failures.

Execute the changed revision's original `RedditAdapter.harvest`, provider
state, original urllib feed reader, Atom parser, candidate persistence and
harvested-pool `fetch`. Use the original `listings_blocked` method to select
the supported RSS fallback path. Use a disposable SQLite provider database.
All runtime deadlines and constants remain unchanged: in particular,
`RECOVERY_SECONDS=180`, normal feed socket timeout and request pacing. Do not
patch time, sleep, network functions, source methods or response validation.

Create a test-only TLS certificate for `www.reddit.com`. Bind that host to
loopback via private hosts/NSS files inside an unshared network namespace.
Serve only `/r/MachineLearning/hot/.rss?limit=25` on private port 443. The
server returns a valid Atom document with one in-window, one stale and one
future post. All content is synthetic. No Reddit, model, Slack or other
external service may be reached; no real credentials or user home are used.

Freeze two conditions: an ordinary immediate complete response and a response
that emits one leading whitespace byte per second for 190 seconds before the
same complete Atom document. Whitespace is valid before the document element.
Record real monotonic start/end times and every emission; verify the feed
remains syntactically valid and byte gaps stay below the unchanged socket
timeout. A refresh exceeding the stated 180-second recovery budget is not a
bounded success. Allow a two-second observation tolerance; that tolerance
does not redefine the source budget. After successful harvest, reopen the
original provider through a fresh adapter and verify the filtered candidate
pool survives without another HTTP request.

Run each condition twice, each in fresh private custody, with a 215-second
outer process limit. Total execution limit: 500 seconds. Python 3.12, OpenSSL,
runtime files, witness bytes and source are pinned. Pin criteria before
execution. Capture endpoint receipts, original outputs, database contents,
process status and all failures. The preserved test key belongs only to this
local fixture. Stop on fixture/source/runtime drift, setup failure, unexpected
effects or limits; kill only owned process groups on timeout. Source/runtime
mounts are read-only; only private capture/home and local TLS state are writable.
Expiry: 2026-09-11T00:00:00Z or consumption.

This tests one part of a large selected change. Curation fallback, trace
privacy, Twitter credit handling, timers and all other changed behavior remain
outside this witness. It grants no whole-patch clean label, case admission,
native reviewer score, ranking acceptance, real queue write or source-repo edit.
