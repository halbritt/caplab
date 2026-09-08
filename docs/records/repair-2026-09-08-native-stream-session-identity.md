# Reject contradictory native stream session identity

Date: 2026-09-08. Baseline: `8d98518`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Inspect current native assessment source and run newly constructed synthetic
Claude stream counterexamples. Change only the Claude stream model assessment
in `src/caplab/review_dissent/native.py`, add a focused session-identity test
module and update the native stream evidence contract and this record. Test
explicit conflicting/invalid top-level session IDs, init/result identity and
continuation withholding, preserving absent-ID legacy assessments. Run focused
and full tests, a baseline parity probe on ordinary synthetic inputs, and a local
commit. Preserve native policy/profiles/launchers, invocation/runtime/collection
owners, frozen evidence, `docs/designs/`, worktrees and services. No historical
session reads or changes, native inference, credentials, tracker write, external
message, registration, ranking or placement. Retain probes and logs; remove only
enumerated doctrine scratch after consolidation. Authorization expires at commit.
Stop if the repair requires guessing persisted transcript fields or changing
session-missingness criteria in the frozen legacy instrument.

## Observation and decision

While preparing session linkage, source inspection found that the current Claude
model assessor checks init, assistant, partial and fallback model fields but
never examines the stream's top-level `session_id`. Select a contradiction guard
on those explicit fields: different valid session IDs, or present invalid IDs,
must prevent a model-match result. Preserve ordinary streams lacking session IDs
as model-field-only assessments; missing linkage remains unverified. Do not infer
an ID from filenames, nested content, tools, prompt text or a configured model.
This repair is a prerequisite to dependable linkage, not full session linkage.

Official Claude session documentation identifies `session_id` on result and init
messages: https://code.claude.com/docs/en/agent-sdk/sessions . The source was read
on 2026-09-08. It does not establish the raw persisted transcript schema needed
for a general Claude root/child linker. Official Codex documentation identifies
`thread.started.thread_id` in JSONL stdout:
https://learn.chatgpt.com/docs/non-interactive-mode . Keep these harness-specific
formats distinct; do not substitute an SDK or shared runtime as the subject.

No change allows explicit contradictory session evidence to be ignored. Requiring
session IDs on every legacy fixture would impose a new missingness contract.
Parsing undocumented persisted fields would invent support. The selected repair
rejects positive contradictions in the current consumer and leaves those larger
linkage requirements explicit. Reopen when an accepted native binding freezes
complete session requirements and supported persisted formats.

The synthetic counterexample reproduced `native-model-match` with root init and
result declaring session A and an unscoped assistant declaring session B; retained
at `/tmp/caplab-native-session-counterexample.json`. Before code changes, refine
the guard to account for documented child envelopes. Nonempty string
`parent_tool_use_id` on assistant/user/stream-event/tool-progress messages marks
child-scoped observations; do not compare those IDs with the root. Invalid scope
values, or child-scope fields on root-only init/result envelopes, prevent
agreement. Retain child observations without claiming their lineage is verified.
This scope handling is included in the authorized assessor/test edits above.
Claude's subagent documentation identifies `parent_tool_use_id` on child output:
https://code.claude.com/docs/en/agent-sdk/subagents . The TypeScript reference
search supplied the message types; fetching that full page exceeded the web
reader's size limit. No persisted transcript format is inferred from these fields.

Also authorize one regression test in
`tests/test_review_dissent_identity_stop.py`, using its existing synthetic
attempt fixture, to verify that session conflict prevents preparation of the
next assigned slot without rendering or changing the retained stdout.

## Execution and verification evidence

The new pure session-evidence pass records exact top-level IDs with line numbers
and parent-tool markers. Blank/non-string IDs, invalid scope and conflicting
root IDs add errors. Documented child envelopes retain their IDs without root
comparison or a verified-child claim. The existing model/fallback mismatch keeps
precedence; otherwise session errors produce `model-unverified` with
`native-session-evidence-invalid`. No recursive content scan, file access,
normalization, native call, resource acquisition or mutable retained input is
added. Existing JSON parsing, capture hashes and scoring/continuation owners
remain in place.

Before the source change, eight new tests produced 13 failed assertions and
seven missing-field errors in 0.078 seconds; red log:
`/tmp/caplab-native-session-red.log`. After the repair, the combined session,
continuation and partial-model checks passed: 29 tests in 1.415 seconds,
`/tmp/caplab-native-session-focused.log`. They cover conflicts at each root
surface, invalid IDs/scope, exact literal comparison, absent-ID compatibility,
valid child envelopes, nested quoted IDs, model-mismatch precedence, score
withholding and next-slot preparation refusal without rendering. Execution
status, subject seal, unattempted slots and retained stdout remain unchanged.

The parity probe compares baseline `8d98518` with current source on 108 ordinary
synthetic assessments across model/terminal/newline combinations and absent,
matching root or marked child IDs. Whole results agree after excluding only the
new `session_ids` observation field. It also replays the original counterexample:
`native-model-match` becomes `model-unverified`, with line 2 identifying the root
conflict. Probe and receipt: `/tmp/caplab-native-session-parity.py` and
`/tmp/caplab-native-session-parity.json`. No historical trace is used.

`/tmp/caplab-native-session-source-check.json` retains source/test hashes and
Python 3.12.3. Eleven protected sources are byte-identical to baseline, including
native policy, launchers and new capture/verification owners. No new unused
imports were found; the pre-existing unused `tempfile` import in `native.py`
remains outside this repair. No dependency, interpreter, formatter, checker or
CI configuration changes. The contract now documents exact error fields,
precedence, root/child scope and the remaining model-only claim ceiling.

Full `make check` passed: 1,052 tests in 175.176 seconds, four skips, exit zero.
Log: `/tmp/caplab-native-session-make-check.log`. Source/test hashes still match
the earlier check, and all eleven protected sources were checked again against
baseline. No source or tests changed during the full run. Documentation links
resolve; the prose pass found no generic sentence requiring removal.

## Advisory doctrine and completion

The release retrieval gate passed. Final packet `pkt-b80bd70f09a6ded9`, SHA-256
`b80bd70f09a6ded942dd77677863cb958bdf93607ba07b76980a6b752dc444c5`,
uses `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9` and
`retriever-ec995ecdd083b2c8`. One gathering pass supplied five typed records.
Four citations classify as valid: `universal-evidence-before-intervention` for
the reproduced mixed-session result, `universal-preserve-behavior-by-default`
for ordinary-case parity and protected capture owners, `python-text-bytes-boundary`
for literal IDs and unchanged raw capture hashes, and
`agent-conduct-authority-bounded-action` for synthetic-only repair without
historical rewriting or native qualification.

Five unmet obligations are nonmaterial:

- `implementation-repository-language-conformance`: `CI and build matrix` and
  `formatter and static-tool configuration`; neither changes, and no new
  platform or tool conformance is claimed.
- `python-repository-shaped-idiom`: `formatter linter and type-checker configuration`;
  this extends the existing assessor with no formatter/checker claim.
- `python-runtime-static-boundary`: `annotation maintenance cost` and
  `configured checker and Python version`; no annotation-cost or static-proof
  claim is made. Actual local Python is recorded separately.

`/tmp/caplab-native-session-verification.json` consolidates the packet, citations,
obligations, reproduction/parity evidence, source checks and full-test result.
It records hashes and paths of exactly twelve removed doctrine scratch files,
including the temporary Markdown-read copy. Reproduction, parity and test logs
remain. This repairs a demonstrated false agreement in the current scoring and
continuation consumer. It does not establish root/child persisted linkage,
attempt-to-invocation binding, native capture completeness or study readiness.
The broader roadmap and active objective remain incomplete. No independent
acceptance or placement decision is asserted.
