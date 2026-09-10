# Reproduce the selected publication-date and history-path repair

Under ADR 0026 and the active reviewer-ranking goal, authorize private
development custody at
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/publication-witness-1`.
Copy exact tracked `newsroom/`, `config/`, `README.md` and `pyproject.toml`
blobs from ai-newsroom base `00efadb0c5bdd2fc6d939793e7d372bf3c69ea73`
and sampled repair `e4d5293910614ead24a9f7599f7d12050d5c64cf`. Preserve
commit/tree/path/Git-blob/SHA-256 provenance and original bytes. This is a
private development copy, not historical evidence admission or relabeling.

Use the installed `/usr/local/bin/blogwatcher` binary, frozen by content hash,
to add and scan one new local RSS feed into a disposable home/database in
each execution. Record its version and complete Go build metadata, including
its reported modified source state; do not claim it is a verified historical
or clean upstream build. Serve only the frozen feed inside the same isolated
network namespace. No live queue, blog, network service or user home may be
read or changed. Keep all database and endpoint data in the new custody.

Exercise original `RssAdapter.fetch`, parsing, candidate rendering,
`_drop_stale`, curator prompt rendering and `cli.main` with `fetch --source
rss --window 24`. No model, editor endpoint, Slack call or acknowledgment is
authorized. The feed has seven entries: four known publication days (today,
yesterday, a stale day and a future day), a second yesterday entry with a
different exact time, an undated article and a non-AI control. Their publisher
timestamps are fixture inputs; use the real producer's displayed precision
as the consumer's information boundary. Do not replace producer output or
patch the original parser, clock, filters or candidate renderer.

Also exercise four individually recorded instant-window inputs (stale,
inside, future and an equivalent non-UTC representation), two equivalent
timezone-aware candidate timestamps, and the default/XDG/NEWSROOM_DATA_DIR
history paths with new private directories. Freeze inputs, expected
properties and uncertainty before execution. A date-only value cannot become
an invented instant; unknown time remains unknown, and a 24-hour window must
exclude known instants or whole days outside it. A known source date must
survive the parser and remain available to the curator. Treat genuine
producer/consumer incompatibilities separately from setup failures.

Use Python 3.12 with pinned executable/standard-library files and the pinned
blogwatcher binary. Two executions per source revision; 60 seconds each,
240 seconds total. Inner external commands are bounded to 15 seconds.
Execution requires UTC date 2026-09-10 and expires at 2026-09-11T00:00:00Z
or consumption. Source/runtime/fixture drift, failed setup, unexpected
external effects or the stated bounds stop the attempt; preserve failures.
Mount source and dependencies read-only, clear environment and isolate
networking. Only the private home, history paths, captures and local HTTP
fixture may change. Retain raw producer output, original result/prompt bytes,
database files, HTTP receipts and process status. No target-repository code,
service, timer, corpus, reviewer score or ranking acceptance may change.
