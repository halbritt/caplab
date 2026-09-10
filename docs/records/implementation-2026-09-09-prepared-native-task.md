# Connect prepared task inputs to native capture

Baseline `c09e1fb`. The previous goal turn completed the overlap comparison.
The current native diagnostic prepares an empty `/work`; task-input
materialization is exercised only through a separate fixture. CAPLAB-84 needs
prepared repair tasks linked to their actual pre-release inventory.

Under ADR 0026, authorize an optional anchored task input for the existing
scripted native diagnostic. Its fixed prompt, supplied tool call and offline
transport remain a diagnostic, not a model-generated repair. Retain the empty
task mode and its existing preparation format. A preparation carrying an input
uses a new version and requires its exact custody path, input hash and bounded
metadata allowance. Reject partial CLI options, custody overlap, changed input,
insufficient diagnostic capture allowance, and a pre-existing diagnostic
`capture-witness.txt` path before execution consumption.

Integrate materialization into the actual authenticated mount handoff, after
mount identity/containment checks and before the before snapshot or release.
Reuse the existing task-input verifier and descriptor materializer. Compare
the captured before content to the prepared input and seal their linkage in
the guarded handoff before acknowledging the child. Verification must require
the preparation's exact input selection, the before anchor, content identity,
materialization counts and destination identity. A matching final copy cannot
repair a mismatched starting task. The diagnostic must leave initial task
contents unchanged while adding only its reserved witness; compare that
observable effect without counting directory timestamp changes as task edits.

Authorize source changes in the task-input/capture helpers, shared mount and
native custody readers, scripted diagnostic preparation/runner/inspection/CLI,
focused tests and their existing fixture helpers, this record and associated
contracts. Use new synthetic task bytes only: non-ASCII/binary files, a nested
directory and literal symlink, plus refusal controls. No historical world or
capture copy, admission, rewrite or purge; no native/model call, spend, provider
access, human judgment, tracker write, message, deployment or push. Private
records use `/tmp/caplab-prepared-native-task-*`. Preserve `docs/designs/`, other
worktrees, services and historical attempt receipts.

Verify the real shared handoff with an isolated fixed Python producer, keeping
it blocked until prepared bytes and the before snapshot agree. Verify input
drift and invalid selections before one-shot consumption, mismatched before
content/identity and materialization metadata, quarantine refusal and no
release on failure. Use the existing synthetic installation for preparation
tests; it is never executable. Run focused tests, the required full suite and
source/doc checks, then commit this scope locally. Do not infer actual native
compatibility for the new mode from the synthetic controls. A later exact
authorization must name any installed-native attempt and its prepared input.

All source/custody ancestry remains caller-owned and stable. Preserve partial
effects and propagate failures; do not acknowledge, reset an allowance, or
erase partial evidence to retry. Stop on unexpected writes, custody ambiguity,
unexplained disagreement, or a required change to the fixed native protocol.
Authorization expires at the verified local commit. Task/world truth,
representative population, independent validation, coder accuracy, blinding,
serving parity and study eligibility remain separate requirements.

Leaving the disconnected fixture unchanged would not exercise the actual
release path. Copying files before establishing mount identity would weaken
custody. A general provider-enabled runner introduces different execution and
containment requirements. Select the integrated prepared-input path, with
bounded local verification and explicit remaining native validation.

## Implementation and local checks

Preparation now supports an anchored task selection in schema v2 while keeping
the original empty-task schema v1. The first test refused the missing API;
after implementation it verified preparation from retained input after original
source removal, then demonstrated refusal before consumption when its payload
changed. A later preparation control found that a read-only task root and an
excessive declared input allowance were still accepted. Preparation now refuses
both: the fixed witness requires writable task root, and input-declared limits
are checked before payload reads. Actual retained counts separately reserve
space for both task copies and the witness.

The shared authenticated mount handoff calls the new prepared-task helper
after source/namespace checks. The helper materializes, captures, and compares;
the handoff guards and seals the link before acknowledgment. The worker's
selection and the inspector both bind the exact preparation's input selection.
The inspector checks initial content separately from final overlap and requires
only the fixed witness addition. Existing empty-input behavior stays explicit.

Fourteen focused tests passed in 3.171 seconds, including five new methods.
The real isolated Python producer reads the binary payload and symlink after
release and adds one witness. The initially expected entry count of five was
an arithmetic mistake: before contains root, directory, file and link (four),
and after adds the fifth entry. That assertion was corrected to the declared
fixture population. Wrong input anchors and quarantined content leave the
child unreleased, with no handoff or completed attempt receipt. Descriptor
counts return to their starting population. Constructed link mutations reject
changed anchors, destination, counts and truth flags; a separately valid input
cannot match the verified before capture from another task. Tests use real
files and processes, without mocking internal helpers.

Ruff F and diff checks passed. New code and the existing formatted diagnostic
files use Ruff formatting; the two shared probe files keep their surrounding
style. The full suite is running against these final runtime/test bytes.

## Preparation for a native integration observation

Authorize creating new synthetic source at
`/tmp/caplab-prepared-native-task-source`, containing exactly a root directory,
`README.txt`, directory `input`, file `input/payload.bin`, and symlink `link`
with literal target `input/payload.bin`. The text identifies a fixed capture
diagnostic and contains no task instructions or private data. Retain its
inventory and payloads at `/tmp/caplab-prepared-native-task-input`, with input
allowances 65,536 bytes and 100 entries; then remove only that new source tree.
Retain the input anchor and source file definitions in the private preparation
record. These are constructed diagnostic bytes, not an authored study world.

Prepare fresh diagnostic custody at `/tmp/caplab-prepared-native-task-native`
using that input and the current installed source at
`/home/halbritt/.npm-global/lib/node_modules/@openai/codex`, with
`/tmp/caplab-native-transport-deps/websockets`. Enforce the native-agent contract,
source profile and current installation/dependency/runtime hashes. Preparation
is read-only with respect to those installed inputs and launches no native
process. It does not authorize execution. Stop on a changed or unsupported
installation, mismatched source or task input, or an existing output path.

The first preparation succeeded with input SHA-256
`dd279ca91ed9cd58993694252f047efc9695bb90cccb4fe41d56f48cc4abf5fa`
and preparation SHA-256
`3d1792b5036da0ce73e9e30fdf1d023c01ed670747909dc8a744e7bd4fa556ba`.
It was not consumed or executed. Subsequent review found the fixed metadata
allowance was checked after the input read. A test using an excessive allowance
and absent custody reached the filesystem before refusal. The fixed allowance
now checks before custody is opened; 15 focused tests pass. This changes a
pinned source, so the earlier preparation is ineligible for execution.
Preserve it unchanged. Authorize a fresh preparation with the same exact input
at `/tmp/caplab-prepared-native-task-native-final`, under the preceding
preparation-only scope. Re-run the full suite on the corrected final source
before any execution authorization; retain both test logs.

## One native integration attempt: conditional authorization

Under ADR 0026, authorize exactly one installed-native attempt only after the
final full suite returns exit zero and the preflight pins still match. This
supersedes the earlier no-native-call ceiling solely for the effect below.
The first full run passed 1,449 tests with four skips in 247.071 seconds, but
it began before the metadata-order repair and is not the final-source gate.
The corrected focused suite passes 15 tests, including refusal when two input
copies plus the witness would exceed the task budget.

The only permitted execution root is
`/tmp/caplab-prepared-native-task-native-final`, preparation SHA-256
`8fcb59b44e3247a20d45a52292af8ed5c5ac213985e0812722f5b77866e42a80`.
Its task input is `/tmp/caplab-prepared-native-task-input`, input SHA-256
`dd279ca91ed9cd58993694252f047efc9695bb90cccb4fe41d56f48cc4abf5fa`,
content SHA-256
`38b4154ce1b93bce5a44476ee4c7cd2ba7473ca7343835c65f610044f9195925`:
85 retained bytes across five entries before execution. The earlier preparation
remains unconsumed and is not authorized. This scope expires after the one
consumption, verified cleanup and local commit; failure grants no replacement.

Subject configuration is the source-verified Codex 0.153.4 Linux x64 native
harness, configured `gpt-5.6-terra`, effort `max`, summary `detailed`, and
`codex-scripted-local/v1`, with native binary SHA-256
`56ef98ab4032d317ab26e9b5e5a175650717351edb16ed9cde0cb6d1734d62da`.
Use the unchanged fixed prompt/tool/responses and fabricated authentication.
Retain actual request identities separately. This is an offline native tool
and capture experiment, with zero provider/model calls and zero spend. It is
not a served-model Binding or a study trial. The primary agent sees all
constructed input and diagnostic output; no blinding or untouched holdout claim.

Keep the prepared 30/45/90/100-second native/capture/unit/outer deadlines,
256/512-MiB workload/unit memory, zero swap, 128/192 tasks, bounded streams,
1-MiB/1,000-entry combined task capture, 8-MiB native collection,
40-MiB/2,000-entry full-mount retention, and 2-MiB trace limit. Keep all existing
network/mount/device/capability, trace, source-prepared child, quarantine and
one-shot checks. No service other than the newly owned diagnostic unit may be
started, stopped or changed; remove only its owned cgroup/unit resources.

Verify preparation/consumption/result anchors, actual prepared-before content
and source descriptor, unchanged initial files plus exactly one witness,
task/native/full-mount agreement, actual request configuration, trace and
kernel-observed child linkage, retained resource/termination outcomes and unit
removal. Preserve all raw results, including the previously classified possible
missing WebSocket close frame. That error keeps attempt failure even when the
bounded observation verifies; do not change criteria to clear it. Stop on any
other unexplained failure, input drift, identity contradiction, quarantine or
containment failure, quota termination, or incomplete cleanup. No retry,
historical admission, scoring, coder exposure or roadmap closure follows.

## Final tests and installed-native observation

The final full suite returned exit zero: 1,450 tests in 194.175 seconds, four
skips, no failures. The final focused suite passed 15 tests in 3.072 seconds.
All 166 preflight source/test/contract pins matched before launch and again
afterward; the preparation's runtime, native installation, dependency and task
input checks also passed. No runtime or test edit followed the final full run.

The one authorized attempt consumed its allowance and executed. The CLI exited
1 and preserved result SHA-256
`b4962c230711862d160f2852b8cd9d6574d0da862c4dccd719f7ae1ff78d9488`.
The inspector exited zero with `status: verified-observation`, output SHA-256
`52837b76c9300fa7ef7508cc765a903b5ce2f5befcf8df9b5fba5ced07f51b38`.
These are different outcomes: native shutdown was normal, but the fixture
retained `ConnectionClosedError: no close frame received or sent`, bootstrap
exit 1 and `native_attempt_succeeded: false`. No success flag or criterion was
changed to hide that error. No second attempt is authorized.

The native run's before inventory has SHA-256
`7fae7bf875adf81c1527927f2e6548f07a787caea2da951353fa73623bc82590`.
Its five entries agree with the selected input and materialization identity.
The only task change is addition of `capture-witness.txt`; all six final task
entries agree with retained `/work`. The selected native diagnostic directory,
final-message file and session tree have counts 1, 1 and 5, agreeing with their
retained `/episode` subtrees. Raw protocol, request configuration, source-prepared
child configuration, kernel child observation, execution linkage and final
message checks passed in the existing integrated inspector.

The trace retains 1,384,289 bytes, SHA-256
`f891c09bea1eb532d545515b0408a2421c678a6618d2b8d6185c01920f51842f`.
Full mount retention contains 3,082,547 bytes across 135 entries. Inspection
scanned 127 files and 4,779 decoded trace strings under the existing quarantine
method. The child-observation pause was 188.167755 ms; the complete handshake
was 199.84058 ms. These are diagnostic observations, not incremental capture
overhead or representative repair costs.

The owned unit
`caplab-scripted-native-6b0c2b010355496f969d5a2b5fbacd78.service`
returned `LoadState=not-found` and `ActiveState=inactive`; the inspector verified
its cgroup absent. The stale earlier preparation remains unconsumed. The exact
postflight checks are retained in `/tmp/caplab-prepared-native-task-postflight.json`.
Input custody and all execution evidence remain intact. No study population,
repair oracle, coder exposure, serving-model identity or independent acceptance
was established. The roadmap and full reviewer-capability goal remain open.

## Advisory review and preservation

The Doctrine retrieval gate verified release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` and source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-d03ab60fdd20f07e` was reassembled once with five typed
evidence records. Final packet `pkt-a9ac9ae8d6fa1f82`, content SHA-256
`a9ac9ae8d6fa1f822252af2ed0fe7d4c01c105d068a00af2821db64fc3ff4efd`,
uses corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
All 32 evidence provenance references matched their bytes. The record at
advisory time is retained separately before these final additions.

Applied representation fit to explicit selection/link records, repository
precedence to authority and capture requirements, structured cleanup to borrowed
descriptors and blocked work, literal text/bytes handling to content comparison,
local reasoning to the shared prepared-task helper, runtime validation to
receipt fields and allowances, and bounded authority to the one native attempt.
All seven concept citations classified as valid in both initial and final
packets. The five retrieved conflicts resolve to one helper for input/before
linkage, unchanged adjacent structure, explicit runtime checks, existing
repository style and a versioned optional mode. No general scheduler, new
provider transport or study architecture was introduced.

Nine generic obligations remain nonmaterial to this scoped conclusion:

- `CI and build matrix` and `Python and dependency version matrix`: current
  interpreter, pinned installed runtime and full repository tests were checked;
  no cross-platform or cross-version compatibility is claimed.
- `formatter and static-tool configuration` and `formatter linter and
  type-checker configuration`: tooling is unchanged; Ruff F and formatting
  checks support only the stated local checks, not an expanded toolchain audit.
- `workload evidence for optimization`: this is an integration feature, with
  no speed, capacity or representative overhead claim.
- `annotation maintenance cost`, `checker and trust-boundary evidence`, and
  `configured checker and Python version`: this change introduces no annotation
  scheme or static-checker guarantee. Runtime field checks, real filesystem and
  handoff tests, and the native observation support the named input/linkage
  properties; no static proof of those properties is claimed.
- `latent security, safety, data, durability, and compatibility check`: the
  bounded review covers release ordering, input drift, resource allowances,
  quarantine, descriptor ownership and preserved partial failures. It is not
  an exhaustive repository-wide risk audit.

The code/test guard found no mocked internal implementation or manufactured
model result. The fixed native response fixture remains explicitly synthetic.
The docs guard checked caller names, schema/result fields, limits and all seven
local documentation links. The remaining empirical requirements are unchanged:
representative repair tasks, real serving configuration, full exposed capture
validation, redaction and coding accuracy must precede study use. The completed
feature and native observation do not supply those missing measurements.

The final private manifest is
`/tmp/caplab-prepared-native-task-verification.json`, SHA-256
`4368e0576b1d225d62ec2e4a0ef016d7fb4fe774f9092dca8789d042edb36b34`.
It records 179 artifacts, 25 directories, 166 source/test/contract pins and four
runtime pins. All retained hashes and modes matched. Thirteen advisory packet,
evidence and citation files were embedded byte-for-byte, verified, then removed
by exact path. Input custody, both preparations, native capture, logs,
preflight/postflight observations and record snapshots remain retained. The
completed native allowance stays consumed; the stale preparation grants no
attempt. This implementation scope expires at the local commit.
