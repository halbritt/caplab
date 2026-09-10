# Copy raw Git blobs for the pool transport witness

Under ADR 0026, authorize a separate `pool-transport-witness-2` private
development custody beside the first attempt. All source revisions, paths,
runtime, conditions, execution limits, isolation and expiry in the
[first authorization](authorization-2026-09-10-reviewer-pool-transport-witness.md)
continue to apply. Preserve the first directory and its failure record.

First preparation stopped at `src/caplab/_source_commit.txt`: historical
`.gitattributes` specifies `export-subst`, so `git archive` returned the
expanded commit ID instead of the tracked blob's literal bytes. The blob
check rejected it before writing that file. No witness executed.

Materialize the exact authorized tracked files with `git cat-file blob`
using each `ls-tree` object ID. Verify its Git blob and SHA-256 before writing.
Do not substitute an expanded archive identity for original source bytes.
Keep the probe, receiver, conditions and fixture bodies identical to the
first preparation. Freeze the corrected runner and new plan before execution.
Two executions per revision remain authorized, each limited to 60 seconds,
360 seconds total, expiring 2026-09-11T00:00:00Z. No historical source change,
native reviewer call, corpus admission or ranking is authorized.
