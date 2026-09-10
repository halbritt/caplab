# Correct the build observation in graph-witness authorization

The [second authorization](authorization-2026-09-10-reviewer-scheduler-graph-witness-2.md)
incorrectly states that the failed first compilation produced an output
binary. A direct listing of `scheduler-graph-witness-1/builds/base/` shows an
empty directory. No output binary was produced and none is reused.

This corrects the observation only. The frozen authorization's effect,
source, witness, criteria, isolation and limits remain unchanged. Preserve
its original bytes and this correction separately.
