# Link a captured Codex root to retained rollout evidence

Date: 2026-09-08. Baseline: `9688cc4`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Extract the existing rollout byte interpretation from `artifact_rater.py` into
a pure callable in that same module, preserving its file API and observations.
Add `src/caplab/codex_capture_link.py`, focused tests, a versioned contract and
this record; link the native collection verification contract. First check the
extraction against baseline behavior and existing rollout tests; then implement
and verify linkage. Use only new synthetic task captures, prepared runtimes and
collections, including mismatched IDs/models/efforts, ambiguous filenames,
missing and tampered evidence, partial/failed processes and bounded-read cases.
Run a local Python producer, focused/full tests and a local commit. Preserve
all other sources, native policy/profiles, launchers, historical evidence,
`docs/designs/`, worktrees and services. No native inference, credential access,
registration, ranking, placement, tracker write or external message. Retain
probes/logs; remove enumerated doctrine scratch after consolidation. Authorization
expires at commit. Stop if linkage requires historical native home reads, a
new native-format assumption, or treating matching metadata as launch authority.

## Decision and claim boundary

Select read-only Codex root linkage over independently anchored task and native
collection bundles. Verify both bundles, reread linked metadata under a budget,
require the same recorded task root, derive the thread from captured stdout and
select exactly one retained rollout with that exact filename ID using the existing
lookup pattern. The filename selects a candidate only. Its bounded retained bytes
must attest the same session/CLI and consistent turn-context model/effort using
the existing parser, then agree with the canonical invocation's model/effort.
Retain both anchors and the selected stdout/rollout hashes in the link report.

The task capture's process command may be an outer containment command; no current
adapter binds that command to the invocation. The report must explicitly leave
executed-invocation binding false. Likewise, ID agreement does not prove provider
identity, genuine native emission, exhaustive capture, task success or eligibility.
Report process completion separately and count other retained session files as
unlinked; do not claim child lineage. Claude requires its own persisted-format
contract and must fail this Codex-only API, not pass through a shared proxy.

No change leaves verified custody unconnected to root observations. Selecting by
filename alone misses forged or mismatched body identity. Reopening the mutable
runtime forfeits the retained-byte boundary. Copying the attestation parser risks
divergent tuple rules; a pure extraction gives this bounded reader the same rules
while preserving existing callers. This is a behavior-preserving extraction
checkpoint followed by a new linkage feature, not a native execution campaign.

## Extraction checkpoint and execution evidence

The file attestor now calls `attest_rollout_capture` with its already-read bytes
and locator. The parser body is unchanged except that it returns the supplied
locator; the new function does not open it. Before implementing linkage, 26
existing artifact/rollout tests passed in 0.151 seconds. A 22-case baseline probe
preserved complete results and error type/text across session/model/newline and
malformed-byte cases. Evidence: `/tmp/caplab-codex-link-extraction-tests.log`,
`/tmp/caplab-codex-link-extraction-parity.py` and its `.json` receipt. This closes
the behavior-preserving extraction checkpoint separately from the new consumer.

Seventeen linkage tests passed in 2.876 seconds:
`/tmp/caplab-codex-link-focused.log`. They use real local Python process capture
and new synthetic native-format bytes, not native inference. Tests cover source
deletion/read-only inspection, exact and ambiguous candidates, body-ID mismatch,
model and effort mismatch, absent turn context, partial rollout, ambiguous stdout,
bad anchors, payload corruption and mutation after initial bundle verification,
combined identity limits, differing recorded task roots, wrong harness, nonzero
exit and timeout. Other session files remain unparsed and unlinked. Success never
sets executed-invocation binding, child linkage or native completeness true.

The retained end-to-end probe runs a Python producer that writes a synthetic
rollout and diagnostic and emits thread events, then captures task state,
collects runtime output and invokes the linker. Files:
`/tmp/caplab-codex-link-probe.py`, `/tmp/caplab-codex-link-probe.json`.
Root: `/tmp/caplab-codex-link-probe-zqpktazg`. Independently stored attempt hash:
`521be596550e94bc099ec69b037176e422a59580e6dc356a1a94a70b2a4eae01`;
collection hash:
`c7d4618978218e71dba89a4ca263b28b68139825e9aa8a0f02e516a346c2ce22`.
The report links 259 identity bytes, checks 11,212 bundle receipt bytes and rereads
10,014 metadata bytes. It reports `synthetic-root`, CLI `mechanics-only`, configured
model/effort agreement and exit zero, while explicitly leaving execution binding
false and completeness null. These synthetic observations establish mechanics,
not that Codex emitted them or that any reviewer capability was measured.

`/tmp/caplab-codex-link-source-check.json` records source/test hashes, Python
3.12.3, direct-import checks and twelve protected-source comparisons. No unused
direct imports were found. Existing policy/profiles, native runtime, collection,
task/process verification, launchers and Claude assessment are unchanged. No
dependency, interpreter, formatter, checker or CI settings changed. Documentation
links resolve. API and claim-boundary text was checked against the implementation
and tests; the prose review found no generic sentence requiring removal.

Full `make check` passed: 1,069 tests in 179.666 seconds, four skips, exit zero.
Log: `/tmp/caplab-codex-link-make-check.log`. Source/test hashes still match the
recorded check, and all twelve protected sources were compared again to baseline.
No source or tests changed during the full run.

## Advisory doctrine and completion

Final packet `pkt-7b779ef070f89205`, content SHA-256
`7b779ef070f892057ed8afb97a1b792c0e98036e3b065400e766f697f931cc32`,
uses `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9` and
`retriever-ec995ecdd083b2c8` after the release retrieval gate passed. The question
nominated no precise concept; baseline, routed, prerequisite and kernel guidance
remained advisory. One evidence-gathering pass supplied five typed records.
Four citations classify as valid: `universal-separate-semantic-structural-change`
for the extraction checkpoint before new linkage, `universal-preserve-behavior-by-default`
for whole-result/error parity, `python-structured-cleanup` for bounded read
ownership, and `agent-conduct-authority-bounded-action` for root observation
agreement without native execution or eligibility authority.

Six unmet obligations are nonmaterial:

- `implementation-placement-by-ownership`: `recurring change evidence when available`;
  a new consumer of an accepted custody contract requires this integration,
  with no historical churn or maintainability claim.
- `implementation-repository-language-conformance`: `CI and build matrix` and
  `formatter and static-tool configuration`; no such change or new platform/tool
  qualification is claimed.
- `python-repository-shaped-idiom`: `formatter linter and type-checker configuration`;
  the integration uses current capture owners with no formatter/checker claim.
- `python-runtime-static-boundary`: `annotation maintenance cost` and
  `configured checker and Python version`; no annotation-cost or static-proof
  claim is made. The tested local Python version is recorded separately.

`/tmp/caplab-codex-link-verification.json` consolidates packet identity, citations,
obligations, extraction parity, source checks, the retained producer probe and
test results. It records hashes and paths of exactly eleven removed doctrine
scratch files. All execution/parity logs, probes and new synthetic custody remain.

This implements Codex root linkage within the documented observation ceiling.
CAPLAB-84 and the broader objective remain incomplete: Claude persisted linkage,
child lineage, actual invocation binding, native adapter/containment verification
and study readiness are still required. No model inference, independent
acceptance, qualification or placement decision is recorded.
