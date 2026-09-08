# Capture native versions inside prepared isolated runtimes

Date: 2026-09-08. Baseline: `93898d8`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `src/caplab/native_version_capture.py`, focused tests, a versioned contract,
this record and a link from the native runtime preparation contract. Implement
version-only native execution using an independently anchored preparation,
canonical native policy, bounded process capture and a fresh no-network bubblewrap
namespace. Mount only explicit system runtime paths, the selected native
installation, a read-only prepared task and the episode's writable runtime.
Pass a fixed outer environment and the canonical inner environment. The executed
argv must be the policy's version command; do not expose a prompt/command override.

Run new synthetic Python executable fixtures and actual installed native
`--version` probes: Codex installation
`/home/halbritt/.npm-global/lib/node_modules/@openai/codex` and Claude binary
`/home/halbritt/.local/share/claude/versions/2.1.265`. Permit bounded hashing of
their entrypoints, read-only mounting and execution through `/usr/bin/bwrap`;
no credentials or existing native homes are mounted or read. Retain new private
probe roots and bounded logs under `/tmp/caplab-version-capture-*`. Allow each
actual harness one initial version probe plus one diagnostic retry only after
an observed, corrected mechanism failure, at most 20 seconds and 64 KiB streams
per probe. No model inference, auth request, network sharing, live study attempt,
historical evidence changes, SDK substitution, tracker write or external message.

Run focused/full checks and make a local commit. Preserve all existing policy,
profiles, capture owners, frozen launchers, `docs/designs/`, worktrees, services
and historical custody. Remove enumerated doctrine scratch after consolidation;
retain probes and logs. Authorization expires at commit. Stop on unexpected
credential requirements, unavailable namespace isolation, a required native
command change, or a need to expand the mounted filesystem beyond the named
installation and explicit system runtime. A successful version response is only
version-observation evidence, not native capture compatibility or a complete Binding.

## Decision

Select an executable version-only integration over another inferred launcher
claim. The current roadmap projection is
`/tmp/caplab-capture-integration-roadmap.json`: CAPLAB-84 and CAPLAB-85 remain
open. Existing native preference containment mounts older shared configuration;
the new prepared runtime is private but has not yet executed installed native
version commands through a production capture API. Keep the old launcher unchanged.
The new API supplies one required preflight observation and cannot execute a
model prompt. Full native episode execution remains a separate integration.

## Implementation and alternatives

The API checks the independent preparation and entrypoint anchors, rebuilds the
canonical invocation, validates disjoint source/output paths and exact prepared
mounts, and seals intent before invoking the existing bounded process capture.
It supports the current `/work` and `/episode` layout. The native executable is
read-only; the task becomes read-only for this probe. The native runtime persists
after exit. The outer environment uses the existing launcher allowlist, while
bubblewrap clears and sets the inner profile environment. The namespace unshares
network and mounts no host home or shared native configuration.

The Codex source is the installed package with `bin/codex.js`; direct inspection
of that entrypoint identified its locally nested platform package. The entire
package is mounted read-only so the existing native launcher can resolve its
own binary. Claude uses its installed executable file. Neither is replaced by a
common provider adapter. Entry hashes are checked before and after execution;
this pins only the entrypoint, not all transitive executable/runtime contents.

The sole selected argv is the canonical version command. Retained prompt bytes
do not reach it. The result binds the sealed intent and process-receipt hash and
preserves raw stdout/stderr, return code, termination and completeness. It never
turns a nonzero, timed-out or byte-limited process into a successful version
assertion. Partial custody remains on errors, with no automatic retry or final
version receipt after a changed entrypoint. Byte limits precede accumulation;
raw version output is not decoded or normalized by the API. Limits are immutable,
and per-call command, environment and result mappings are newly owned. Existing
descriptor and process owners retain their structured cleanup behavior.

Leaving version execution to ad hoc commands supplies no common sealed intent
or bounded capture. Reusing the historical launcher would expose its shared
configuration and persistence assumptions. Building a general native launcher
here would require unresolved account, provider and execution authority. This
version-only preflight is a required native observation with a concrete command
boundary. It does not substitute for the full episode launcher or claim capture
legibility, reviewer discrimination, overall containment, disk quota or a complete
Binding. Those remain open requirements, not inferred consequences of exit zero.

## Verification observations

The first focused run had one failure: its full environment assertion omitted
the `PWD=/work` set by bubblewrap. The namespace had already excluded the
synthetic ambient variable and host home and rejected the task write. The test
was corrected to assert the complete observed environment, including that derived
PWD; no production behavior or authority was broadened. Failure log:
`/tmp/caplab-version-capture-focused.log`. The final focused run passed 13 tests
in 1.991 seconds, exit zero: `/tmp/caplab-version-capture-focused-final.log`.

New executable Python fixtures ran through real bubblewrap. They checked exact
version argv, fixed outer/inner environments, a distinct network namespace,
hidden host home and outer custody, read-only task state and persisted UTF-8
runtime bytes. Other tests covered both file/package layouts, wrong anchors,
unsupported namespace paths, entry/receipt budgets, source/output overlap,
symlinks and executable mode, existing output, post-execution entrypoint change,
timeouts, stream limits, nonzero exit and invalid limit types. These fixtures
test mechanisms and are not relabeled as native harness observations.

The separately authorized actual native probes each ran once, with no retry:

| Installed subject | Captured stdout | Return code | Stderr |
| --- | --- | --- | --- |
| Codex CLI | `codex-cli 0.153.4` followed by LF | 0 | empty |
| Claude Code | `2.1.265 (Claude Code)` followed by LF | 0 | empty |

Both streams completed. The Claude runtime had no regular files after the probe;
Codex left `codex/tmp/arg0/codex-arg05ApJHA/.lock` and four executable symlinks
in its prepared runtime. The complete observed path/type/mode/size/link-target
inventory is `post-probe-runtime-inventory.json` under the retained probe root.
This changes the next integration requirement: version runtimes remain dedicated
probe custody; a future study episode receives a fresh prepared runtime rather
than silently inheriting these startup effects.
Local bubblewrap reports version 0.9.0. These are observations
of these installations in the selected version namespace; no native model
inference, authentication or provider connection was invoked.

Probe script: `/tmp/caplab-version-capture-probe.py`; execution log:
`/tmp/caplab-version-capture-probe.log`; new retained root:
`/tmp/caplab-version-capture-probe-axh3hsz4`. Its `probe.json` records both full
reports, paths and independent input/output hashes. Final version-receipt hashes:
Codex `be908afee2254ef99dee802ca66dfe0566b0f08ef548241dabb63b680f77da71`;
Claude `3d3df8adf4bd4ff639610862077224bb3b705bfc56846507cbfde3bdc6b7723b`.
The entrypoint hashes are respectively
`61b0194f3bb6534439c8d26a3ed57d0805f84b884588b761795323eeb92fcf70`
and `e14738e3a58d1fc6ccc23b9c919451b4846bc27074a3fb48db976a7d595bdeeb`.

`/tmp/caplab-version-capture-source-check.json` records source/test hashes,
Python 3.12.3, direct-import checks and twelve protected-source comparisons to
`93898d8`. No unused direct imports were found. Existing policy, profiles,
capture owners, native launchers and root-linkage code remain unchanged. No
dependency, interpreter, CI, formatter or checker settings changed.

The existing runtime-preparation integration test skips when bubblewrap is
absent. The six new tests that launch it now follow that convention; the seven
validation tests remain enabled. A separate import-time absence probe verified
exactly those six skip flags, retained in
`/tmp/caplab-version-capture-absent-bwrap-check.json`. The resulting focused run
passed 13 tests in 1.066 seconds with no skips on this host:
`/tmp/caplab-version-capture-focused-portability.log`. This repository currently
has no `.github/` workflow tree; no external CI or platform qualification is
inferred from the local run.

An initial full suite passed 1,109 tests in 185.512 seconds, four skips, exit
zero, log `/tmp/caplab-version-capture-make-check.log`. It preceded the six
portability decorators; final suite verification is recorded separately below.

## Advisory doctrine

Release retrieval state passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. The final packet is
`pkt-63a09bb6f0b6ffc7`, SHA-256
`63a09bb6f0b6ffc7f12637b1360890ade4ebb42f85e685b621e847572d328d59`,
using `corpus-2026-07-12-a11702cc9217`, `doctrine-f6bbb5196a3f8bf9` and
`retriever-ec995ecdd083b2c8`. Two evidence-gathering passes supplied and refreshed
five typed records, including the portability check. Four citations classify as
valid: `agent-conduct-authority-bounded-action` for version-only execution,
`python-structured-cleanup` for existing descriptor/process ownership,
`python-text-bytes-boundary` for retaining opaque output bytes, and
`universal-preserve-behavior-by-default` for leaving frozen native launchers and
capture behavior unchanged.

Six unresolved obligations are nonmaterial to the bounded claim:

- `implementation-placement-by-ownership`: `recurring change evidence when available`;
  a required version preflight is implemented without a churn or maintainability
  claim.
- `implementation-repository-language-conformance`: `CI and build matrix` and
  `formatter and static-tool configuration`; local merged-usr Linux is the only
  qualified environment. Existing conditional bubblewrap test practice is followed;
  no external CI qualification or tool configuration change is claimed.
- `python-repository-shaped-idiom`: `formatter linter and type-checker configuration`;
  the new owner composes existing capture APIs and introduces no formatter/checker
  contract.
- `python-runtime-static-boundary`: `annotation maintenance cost` and
  `configured checker and Python version`; executable validation is used rather
  than claiming static proof or annotation savings. The local interpreter is
  observed separately.

## Completion of this implementation scope

Final `make check` passed 1,109 tests in 144.661 seconds with four skips and
exit zero: `/tmp/caplab-version-capture-make-check-final.log`. Source/test hashes
match the final inspection, and twelve protected files were compared again to
`93898d8`. No source or test edits occurred during the final run. Documentation
links resolve, and the API/claim text was checked against the code and probes.

`/tmp/caplab-version-capture-verification.json` consolidates both focused stages,
the dependency-absence check, both full-suite results, final source checks,
actual native probe reports and runtime inventory, doctrine identity, citations
and unmet obligations. It names and hashes exactly eleven doctrine scratch files
removed after consolidation. Probe roots, scripts, raw captures and logs remain.

This completes version-only capture for the verified local namespace. It does
not complete CAPLAB-84, CAPLAB-85 or the larger goal. Full native episode
execution still needs account/configuration/provider and complete executable
bindings, fresh episode state, execution authorization and trial identity,
bounded runtime storage, native event/child linkage, and representative
legibility, cost and blinding evidence. No model attempt, reviewer qualification,
placement decision or independent acceptance is recorded here.
