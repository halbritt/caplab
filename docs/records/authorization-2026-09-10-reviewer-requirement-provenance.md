# Preserve original requirement context and lineage

Under ADR 0026 and the reviewer-ranking goal, the primary agent authorizes
read-only requirement investigation and exact source copies into private
`reviewer-ranking-001/development/requirement-provenance-1`.

The source repository is `/home/halbritt/git/ai-newsroom`. Permit these exact
commit/path pairs, including their Git blob, tree, parent, commit-time and
content-hash provenance:

- `31725352516d10cc859c1435f3839025087e8fc7`: `README.md`,
  `systemd/README.md`, `docs/engineering-review.md`, `newsroom/cli.py`,
  `tests/test_cli.py`.
- `1df624ef0e8dd44ba985219cf3beaed23a1340e1`:
  `docs/engineering-review.md`.
- `544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f`: `README.md`,
  `config/sources.toml`, `systemd/README.md`, `docs/engineering-review.md`,
  `newsroom/cli.py`, `newsroom/sources/reddit.py`,
  `newsroom/sources/reddit_state.py`, `tests/test_cli.py`,
  `tests/test_reddit.py`, `tests/test_reddit_state.py`.

Retain derived requirement interpretations with precise original context,
scope, rival interpretations and limits. Link to existing independently
executed witnesses by their immutable hashes; do not copy or modify their
outputs. Read source tests as historical specifications, without promoting
their contents or old reported results into new execution evidence.

This permits source-content preservation and a new development requirement
basis, not historical evidence admission, rewriting failed assessor criteria,
product-requirement changes in ai-newsroom, or acceptance of the original
engineering review's completion claims. Preserve complete selected files
privately; committed CAPLAB records may retain their provenance and the bounded
requirement conclusions. No source-tree edits, runtime execution, service
access, model calls, external transmission of copied source files or deletion
is authorized. Stop copying on commit/path/object mismatch or an unexpected
file type. The authorization expires when this preservation is verified or
2026-09-11T04:00:00Z.
