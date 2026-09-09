# Require entrypoint termination in new traced startup captures

Baseline `b83fe58`. The primary agent acts under ADR 0026 and the continuing
CAPLAB goal. The preceding turn was progress: it committed the reusable
termination inspector and sealed its verification. Current startup inspection
still calls the exec-only launch checker, and selected entrypoint termination
is unavailable in its report. A wrapper return code cannot fill that gap.

## Decision and prospective authorization

Extend inspect_native_launch_trace with an explicit boolean
require_termination, default false for existing callers. Validate its type;
when true, compose the existing termination inspector after the same launch
hash/profile validation. Return a versioned launch report with the entrypoint
termination observation, preserving the nested exec report and all current
configuration/capture/eligibility limits. Zero exit does not prove task success
or termination of a native child. Reuse parsing and stable reads; no private
copy of the terminal grammar.

New traced startup selections must seal entrypoint_termination_required=true.
Check that exact value before launching. During retained inspection, absence
of the field preserves the older exec-only interpretation; malformed supplied
values must fail. A required termination without a launch configuration must
fail, rather than taking the older direct-exec path. Keep selection-to-intent
hash verification before using the requirement. Extract the existing execution
inspection block as one script function so fresh sealed synthetic selections
can exercise the actual caller without constructing unrelated capture stores
or launching installed agents. Verify preserved legacy behavior before adding
the selection's new behavior. This extraction and adoption are separate
checkpoints in the same bounded change.

Authorize changes only to native_launch_configuration.py, the startup probe,
its launch contract, existing launch tests, a new startup-execution test file
and this record. Retain new synthetic fixture, source, advisory, test and live
Plane-read evidence under /tmp/caplab-launch-outcome-*. Use TDD, real local
files and existing bounded real-process controls; run focused and full checks.
Read-only application to already sealed native diagnostic traces is permitted
only as a new inspection with original manifest/source/hash provenance. Do not
copy, rewrite or change the disposition of their historical artifacts.

Preserve old selection/report interpretations, exec-only behavior, native
invocations and launch profiles, tracer checks, resource/custody controls,
full-capture limits, unrelated docs/designs, worktrees and services. No native
agent attempt, provider execution, real credentials, model spend, tracker
write, message, deployment, push or independent acceptance. Missing terminal
evidence prevents the stronger report without retry or exec-only fallback.
Owned read descriptors and temporary fixtures must close on failure. Stop on
unexplained regressions or source drift. Authorization expires at local commit.

Leaving the caller unchanged preserves the demonstrated missing result;
requiring termination from all historical selections changes their frozen
criteria. The prospective selection requirement resolves both concerns. The
selected work is entrypoint-outcome integration, not complete native capture,
native-binary identification or CAPLAB-84 completion. Representative repair
measurements and the wider roadmap remain required.

## Refinement from the first caller controls

The first required-selection test passed after adoption, but omission of the
trace anchor still returned an empty result before consulting the selection.
Authorize moving selection/intent validation ahead of the trace-presence
branch. Every valid startup root already contains these sealed selections.
Missing or corrupt selection/intent files now fail even for an untraced report;
valid older selections retain their exec-only or empty execution result.
No missing selection may be interpreted as an implicit legacy exemption.
The startup script's existing require raises RuntimeError; public launch
validation continues to raise ValueError/capture subclasses. Preserve both
conventions and propagate them without fallback.

## Implementation and observed checks

The first regression reproduced the missing require_termination input. The
implemented true branch selects inspect_exec_termination after the existing
launch validation, returns native-launch-exec-link/v2 and retains the same
nested exec report. The default false branch keeps v1. A subsequent control
exposed seven non-boolean inputs that silently selected or skipped checks;
explicit boolean validation now refuses all seven. Both canonical harness
configurations and the closed Codex local profile retain nonzero/signal
outcomes and refuse missing, duplicate or other-PID terminal evidence. Wrong
configuration/trace anchors and rehashed profile changes remain refused.

The script extraction passed 21 launch, tracer and legacy-selection tests
before the new selection behavior was added. The next caller regression
reproduced the missing outcome; then the fallback control reproduced seven
requirements being ignored when a selection lacked launch configuration.
Finally, removing the trace anchor exposed the early-return bypass described
above. The final caller validates sealed selection custody and the requirement
before deciding whether execution evidence is available. Existing collection,
accounting, resource and tracer checks remain in their original ownership.
The producer seals true in new traced selections and requires it before child
launch. It does not change the native invocation, profile, trace command,
resource limits, network setup, mount topology or output collection.

All 42 focused tests pass. Nine new methods cover launch requirement/anchor
semantics and the actual script execution-inspection function using fresh
local files; existing authenticated real-child controls exercise the reused
termination and tracer inspectors. There are no mocked collaborators or model
outputs. Test Guard found no internal-call assertions. These tests do not run
the complete installed-native startup workflow or prove the native child's
outcome. That limitation remains explicit rather than replacing it with the
entrypoint's result.

Read-only application of the strengthened launch checker to the original close,
WebSocket and shutdown traces yields entrypoint exit zero, SIGKILL and SIGKILL,
respectively; their wrapper receipts all remain one. Each application verifies
the original manifest/artifact hashes, selection-to-intent hash, retained launch
file and guard anchors before inspection. v1 and v2 nested exec observations
agree. These new reports live in /tmp/caplab-launch-outcome-application.json;
they do not amend original selections or failed dispositions and are not a new
native attempt or full startup-custody verification.

The source check records 13 baseline/current source identities. The launch
builder AST, startup constants and four unrelated startup functions are
unchanged. The exec/termination parser and tracer implementation match b83fe58.
The live Plane refresh retains 86 items, 12 open, with CAPLAB-84 In Progress.
Ruff F and diff checks pass. Docs Guard checked the optional boolean, v1/v2
report fields, per-read allowance, exception conventions, compatibility
branches and relative links against current source. No broader capture,
study, serving-parity or acceptance claim follows from this integration.

The full make check completed successfully: 1,390 tests in 170.184 seconds,
four skips. No runtime or test source changed after that run began. The
contract's relative links resolve. The full-suite log and baseline/current
source records retain the verification scope and reproducible code identities.

## Advisory review and scope of conclusions

The retrieval-state gate passes for release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-2974be663cab5b0c` and final packet
`pkt-549b3239512fd3be` were read. Final content SHA-256 is
`549b3239512fd3beaa3ab6cccc5fcf331ba7c5a39a742ab28fc6cec0d68f75ed`.
Five evidence records retain authority, reproductions, source, tests and
runtime observations with content hashes and locators.

Selected guidance is repository-contract precedence, evidence before
intervention, authority-bounded action, preservation by default and separation
of semantic and structural changes. The extraction checkpoint concentrates
existing selection/inspection knowledge; the subsequent semantic checkpoint
adds the required observation and closes the reproduced fallback paths.
Existing valid legacy results remain protected, while the explicitly recorded
refinement rejects missing selection custody. No opportunistic refactor of
resource, capture or native-administration code is selected.

The final packet retains 28 unmet obligations. Eighteen generic requirements
about deduplication, bulk discovery, asynchronous UI states, symbolic config
references and ranked truncation are nonmaterial to this bounded change: it
introduces none of those mechanisms. Existing launch profiles are rebuilt by
the unchanged builder, and the added requirement has an explicitly checked
boolean domain. Three service-monitoring obligations are nonmaterial because
no monitor or paging policy changes. The three external-capability and four
authoritative-gate obligations are material to complete native startup and
serving parity; those conclusions are withheld. The present claim is verified
caller behavior and compatibility with retained native traces. It is not
independent acceptance, complete capture, model quality or representative
repair measurement.

Private manifest `/tmp/caplab-launch-outcome-verification.json`, SHA-256
`373c080800dfbebce85139fcfdf8b9820cdd4823d501671b951ca1722bdf0b59`,
seals 22 retained artifacts, 13 baseline/current source records and five
implementation/test/contract files. Eleven advisory scratch files were embedded,
hash-verified and removed. All five used concepts classified as valid packet
citations. The sealer rechecked the three original native diagnostic manifests
and every artifact they list; no original record was rewritten.

This local commit completes the scoped entrypoint-termination adoption and
expires its authorization. The next capture gap is independently linking the
native child binary's identity, parentage and terminal outcome through the
public path. Full native capture verification and representative repair
measurements remain necessary; CAPLAB-84 and the broader goal stay open.
