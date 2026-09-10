# Verify a selected launcher's environment and dispatch contract

Under ADR 0026 and the active reviewer-ranking goal, authorize a bounded
investigation of selected CAPLAB change
`51a7698535f065604337f5c1d54f20267e8be2a0` in private custody
`reviewer-ranking-001/development/launcher-witness-1`.

Import exactly the original `scripts/launch_tree_v1_sweep.sh`,
`scripts/supervise_sweep.py` and
`docs/records/probe-2026-09-06-tree-v1-stage-b.md` from that commit. Preserve
commit, parent, tree, Git blob, path, mode and content hash. The last file is
an imported governing record for the historical launcher's requirement only;
it supplies no current CAPLAB authority or accepted reviewer evidence. Verify
that it is unchanged in the parent and that the launcher is new. Do not copy
old sweep outputs, credentials, declarations or other historical evidence.

Execute the original shell launcher in private network-free namespaces with
synthetic homes and environment files. Replace the downstream `python3`
endpoint with an explicitly identified recorder that captures argv, selected
environment variables and output-directory existence, then returns a fixed
status. The original supervisor file is retained read-only but must not be
executed. This is a launcher dispatch witness, not a model, supervisor or
sandbox capability measurement.

Freeze and run these eight conditions twice: both environment files; neither;
only zai; only openrouter; malformed environment file; downstream exit 17;
repository path with a space and spaced arguments; missing required backend.
Use only clearly synthetic key values. Check exported values, tool-path
precedence, exact argument preservation, source-relative paths, directory
creation, and status propagation. Failure before dispatch must leave no
recorder output. Preserve observations if a proposed control fails; do not
label the entire change clean from these named properties alone.

Each execution has a ten-second limit, the sequence a five-minute limit.
Expiry is consumption or 2026-09-11T00:00:00Z. Source and fixture mounts are
read-only; capture and the new output directory are the only durable writable
mounts. No native model, provider, queue, service, original repository writes
or real credentials are permitted. Stop on identity drift, timeout, or an
unexpected wrapper failure; retain failures without automatic retry.

Register no cases or measurements and change no ranking. Update the fixed
sample's coverage only if original dispatch behavior is established. The
read-only source comparison and bounded executions are authorized; source
mutation and historical sweep reassessment are not. Reuse the validated
doctrine guidance on measuring the claimed outcome and preserving distinct
authority levels; broader ranking validity remains unproven.
