# Distinguish effective native launch configuration from its prepared base

Baseline `881624e`. Primary agent under ADR 0026 and the continuing CAPLAB goal.
Live Plane still contains 86 items, 12 open; CAPLAB-84 is In Progress. The
successful local scripted diagnostic used the canonical native tuple and capture
profile but added three fixed Codex settings and two environment entries before
exec. Treating the base preparation hash as the effective launch identity would
omit behavior-bearing configuration. Private guard evidence already preserves
those additions; reusable configuration and inspection do not yet represent them.

## Decision and prospective authorization

Authorize `caplab.native_launch_configuration`, its tests and contract, a bounded
integration in the optional traced startup probe, this record and private
artifacts under `/tmp/caplab-launch-link-*`. Preserve canonical invocation and
runtime-preparation schemas and all public root-link ceilings.

Define two closed launch profiles: exact canonical-native/v1 and the already
observed codex-scripted-local/v1 diagnostic. The latter permits only the fixed
loopback chat/responses endpoints, update-check disabling, loopback refresh URL
and exact diagnostic RUST_LOG string used in the verified local exchange. Its
sole variable is an integer port in 1..65535; it supports only native Codex and
remains explicitly a scripted protocol diagnostic. No arbitrary argv, environment,
model, effort, sandbox, proxy or endpoint override is introduced.

Build and content-identify the effective command, environment and cwd separately
from the independently anchored canonical invocation. Rebuild both before trace
inspection; reject rehashed edits, mismatched base/launch/trace anchors, unsupported
profiles and invalid contexts. Use the existing exact exec inspector with the
caller-authenticated PID. Report agreement with the effective configuration and
whether that configuration also equals the canonical invocation; no complete
Binding, provider identity, capture completeness or study eligibility follows.

Use TDD and synthetic traces for configuration/anchor refusal cases. Permit
read-only validation against the previously retained local scripted diagnostic
under `/tmp/caplab-native-exec-handoff-run`, its original guard observation and
sealed manifest. Do not copy, rewrite, reclassify, register or admit those source
artifacts, or claim the new configuration record existed before that attempt.
This is a current verifier compatibility check of diagnostic bytes, not a new
measurement or retrospective authorization. No new installed native agent,
provider/model call, credential access or spending is authorized.

Run focused and full repository checks, preserve source/artifact identities and
failure receipts, and commit locally. No tracker write, message, deployment,
push, historical research evidence effect or independent acceptance. Preserve
unrelated designs, worktrees and services. Authorization expires at local commit.

An arbitrary amendment mechanism would permit silent effective-subject changes.
Rewriting the canonical profile would change existing preparation identities.
The closed launch profiles represent the two configurations already needed by
current callers without making a diagnostic a study subject. Native adoption
and root-to-launch evidence composition remain subsequent integration work.

## Implementation and bounded verification

The builder reuses canonical invocation validation, copies the rebuilt argv and
environment, applies only the closed profile and hashes the complete resulting
configuration. The trace checker verifies independent base, launch and trace
anchors, rebuilds the selected profile and rejects rehashed deviations before
calling the existing exact exec parser. Its report names argv/environment
agreement precisely and keeps actual cwd linkage separate and false.

New traced startup selections now contain the canonical effective configuration
within the sealed selection. Before execution the supervisor checks that selection
against intent and compares exact serialized configuration with a fresh rebuild;
this preserves distinctions such as boolean versus integer values. Post-exit
inspection verifies the effective configuration and reuses its nested exec
result. Older selections retain the existing direct exec check. Neither normal
startup commands nor canonical invocation/preparation identities change.

Eight new tests first established canonical ownership and exact values, then
the distinct fixed local profile, then trace inspection. The missing API,
unsupported initial local profile and absent trace API each failed before their
implementation. Further cases verify both canonical harnesses, valid endpoint
boundaries, invalid/ambiguous ports, wrong anchors/PIDs/limits, rehashed command,
environment, cwd and metadata edits, and refusal to use canonical configuration
for a diagnostic trace. The combined configuration, exact-exec and live tracer
suite passes all 22 tests. Synthetic trace tests establish parsing and refusal,
not actual native execution.

The read-only native compatibility check verifies the original diagnostic's
sealed manifest hash, then its selection, authenticated guard and trace hashes.
The new local-profile output agrees exactly with the guard's original pre-exec
argv, environment and cwd. Its configuration SHA-256 is
`075cdb711217234a8428bcad4a2bbd6f6d80cdaaa752a9670ac208900f4db65a`.
The existing native trace matches the independently authenticated PID at line 5.
The checker refuses both canonical configuration and a changed fixture port.
Original artifacts remain unchanged, and no native attempt ran. The result
explicitly states that the newly generated configuration record did not exist
before the original run; no prospective Binding or authorization is inferred.

Compatibility source/result:
`/tmp/caplab-launch-link-retained-check.py` and
`/tmp/caplab-launch-link-retained-result.json`. During review the initial result
flag was narrowed from overall launch-configuration agreement to
`entrypoint_argv_environment_agree`, because actual cwd is not observed by
execve. The original compatibility result is retained, focused checks passed
again, and the full suite was repeated for the final source version.

## Advisory and claim limits

The Doctrine gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`
at release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Initial packet
`pkt-72ce64107a98fb91` and five typed evidence records produced
`pkt-f46f7cfe1c83f0ca`, SHA-256
`f46f7cfe1c83f0ca3616706077e06156ff5b3d6f3a9c01a1f54c637bd96cb6bb`.
Both Markdown packets were read. Versions remain corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, schema `evidence-packet/3`.

All 25 unmet obligations remain visible. Eighteen concern unchanged
deduplication (3), ingest populations (4), asynchronous UI (4), declarative
references (3) and ranking (4); they are nonmaterial to this closed launch
configuration boundary, and those paths are not certified here. Three external
capability obligations and one evaluation/serving-parity obligation remain
material to provider integration and study readiness, which are withheld.
Three monitoring obligations are nonmaterial because no service or paging
policy changed.

Applied guidance is repository-contract precedence, evidence before
intervention, separation of semantic and structural work, preservation of
default behavior and authority-bounded action. In particular, the retrospective
compatibility check is not a new execution or a prospective configuration seal.
Future native adoption must freeze and seal this effective configuration before
release, link actual cwd and installed executable provenance, and join that
evidence to captured root/session artifacts. Representative repair measurements
and the wider CAPLAB roadmap remain incomplete.

## Final repository verification

The final `make check` passed 1,359 tests in 173.167 seconds, with four skips.
All eight new configuration tests ran. The preceding version also passed 1,359
tests in 163.721 seconds; its log is retained separately because the result name
changed afterward. The final log is `/tmp/caplab-launch-link-make-check.log`.
No runtime or test source changed after the final run. Ruff F and diff checks
pass. This verifies the component and existing suite, not live adoption of the
new startup-selection field. No installed native attempt was authorized here.

## Final custody

Private manifest `/tmp/caplab-launch-link-verification.json`, SHA-256
`5ebcf9cb5f72dbb43ba8c7276f520a9bd383edea8efa79c7cf05fd6a335d191c`,
retains 12 source identities, 22 artifact hashes and 11 embedded advisory
scratch files removed after verification. Seven preserved runtime sources
match baseline committed bytes. All artifact, source, evidence-provenance and
embedded-byte hashes passed. The original native diagnostic manifest, guard
and trace anchors were checked again without mutation. Five citation
observations classified as valid packet citations.

No new native attempt, model spend, tracker write, message, push or historical
research evidence effect occurred. This local commit closes the implementation
authorization and leaves the broader CAPLAB goal active.
