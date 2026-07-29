# Truncated files after a "successful" mirror run

Our nightly depotsync job mirrors release artifacts into the deploy
tree. Last night the destination volume ran low on space; this morning
three deployed files are truncated stubs of multi-megabyte artifacts,
yet the job printed "sync complete: 42 synced, 0 skipped" and exited 0.
Re-running depotsync after freeing space doesn't repair them — it
reports complete again.

Reproduce: run depotsync with -dest on a nearly full filesystem, free
space, run again.

Expected: a run that couldn't copy an artifact reports failure, and the
next run repairs it. Actual: every run claims success and the damaged
files are never touched again.
