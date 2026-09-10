# Selected launcher satisfies its named dispatch properties

Original execution of CAPLAB change
`51a7698535f065604337f5c1d54f20267e8be2a0` establishes environment export,
tool-path selection, argument preservation, output-directory creation and
failure propagation for the tested launcher scenarios. This expands the
fixed sample's bounded behavioral coverage from seven changes to eight,
including its previously uncovered CAPLAB 0–20-line stratum.

These are named clean-control properties. The original supervisor and models
were not executed, and the result is neither a whole-change clean label nor
a reviewer score.

## Original behavior

The selected change adds an 18-line shell launcher. Its requirement already
appears in parent `170fdf488df959ac503d5d419924caf5fec7bd8a`:
`docs/records/probe-2026-09-06-tree-v1-stage-b.md`, finding 3, requires loading
the two lane environment files and adding the npm tool directory to `PATH`.
That record is byte-identical in parent and change. The launcher is absent
from the parent, so there is no base implementation to execute.

The witness executes the exact original launcher in isolated namespaces.
Synthetic environment files assign values without `export`; inherited
synthetic values make missing-file behavior observable. Two recording
executables compete on `PATH`. The selected recorder captures its arguments,
exported environment and output-directory existence, then returns a specified
exit status. It never runs its supervisor argument.

| Condition | Observed result in both repetitions |
| --- | --- |
| Both environment files | Both assigned values exported; intended tool directory takes precedence. |
| Neither file | Both inherited values preserved; dispatch succeeds. |
| Only zai | Assigned zai value and inherited OpenRouter value reach the child. |
| Only openrouter | Inherited zai value and assigned OpenRouter value reach the child. |
| Malformed environment file | Exit 2 before dispatch and before creating the sweep output directory. |
| Downstream exit 17 | Original launcher returns 17 unchanged. |
| Repository path and argument containing spaces | Supervisor path, output path and spaced argument retain their exact boundaries. |
| Missing backend argument | Exit 1 before dispatch and sweep output-directory creation. |

All successful dispatches use source-relative `PYTHONPATH`, the expected
supervisor/backend/output arguments and unchanged remaining arguments. The
output directory exists before dispatch. Sixteen executions completed in
1.90 seconds; all named properties hold and repetitions agree.

## Evidence and limits

The [authorization](authorization-2026-09-10-reviewer-launcher-witness.md)
names the exact three source imports: launcher, supervisor and historical
requirement record. Git blob, commit, parent, tree, path, mode and SHA-256
provenance are retained. The historical record supplies that launcher's
requirement; its earlier probe claims create no current evidence admission
or CAPLAB authority.

Private custody is
`~/.local/share/caplab/reviewer-ranking-001/development/launcher-witness-1`.
The [receipt](../product/studies/reviewer-ranking-001/launcher-development-receipt.json)
identifies 120 source/input/process/assessment files and 60 captured files.
It includes the complete verification and bounded property assessment.

| Identity | SHA-256 |
| --- | --- |
| Frozen plan | `aac4636cbc3fb0c6e1ee5752a37b7aef70140bd14d62a23a41d370f76d5a363f` |
| Verification | `b6af11d30805bd576cf87875ce76066aea6ce6e0a4afc6ba3f6d1e986cdb3244` |
| Assessment | `6e2d9d701812eec5bba480a3dc238c4dcce0ca65ff8e9c6f524f3c2e78a939c5` |

The original shell file, fixtures and runtime remain pinned and read-only.
There is no external network or access to real credentials. Only private
capture and output directories are writable. The recorder is a downstream
process fixture, not a replacement reviewer whose behavior could support
ranking. This checks the launch interface; it does not establish supervisor
semantics, live provider readiness, arbitrary environment-file behavior or
model performance.

Four focused verifier tests pass. They catch missing exports, argument
splitting, wrong executable selection, swallowed failure, missing output
directories and dispatch after rejected input. The full repository check
passed: 1,554 tests in 215.121 seconds, seven skipped. Its output is retained
as `repository-check.log` in the custody root, separately from the execution
receipt. Launcher witness verification reproduces and all 120 receipt files
and 60 captured files match their hashes.

The updated fixed-sample projection contains eight bounded change
investigations, three base-tree-only investigations and twenty-one pending,
with zero admitted cases. The sample and all other memberships are unchanged.
This is one newly covered change, not sixteen independent cases. Additional
case coverage, prospective scorer challenges and held-out comparisons remain
required before a reviewer ranking is defensible. The goal remains active.
