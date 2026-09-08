# Verify retained native version captures

Date: 2026-09-08. Baseline: `d503033`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `src/caplab/native_version_verify.py`, focused synthetic tests, a versioned
contract, a link from the version-capture contract, and this record. Verify an
independently anchored version bundle through its five retained receipts and
raw streams. Reconstruct the exact canonical version namespace command and
compare recorded paths, environment, limits, identity links and process outcome.
Treat historical source paths as inert strings; never open them during verification.
Preserve completion, nonzero exit, timeout and truncation observations separately
from integrity and positive native identity. Reuse existing byte/receipt/process
verification owners and the canonical version-command builder without changing them.

Use new temporary fixtures and local Python executables under bubblewrap only.
Create a new retained synthetic probe under `/tmp/caplab-version-verify-*`; run
focused and full checks and make a local commit. Write and consolidate advisory
scratch under that prefix, then delete its exact named files. Retain probe and
verification logs. No native version or inference call, native-home/credential
read, historical-capture inspection/copy/admission/rewrite, campaign reseal,
ranking, placement, tracker write, external message, deployment or push is
authorized. Preserve source capture/launcher/policy owners, `docs/designs/`,
sibling worktrees and services. Authorization expires at the local commit.
Stop if verification needs original source access, executing recorded commands,
guessing a version string, or changing a frozen capture schema or producer.

## Decision

The current version producer seals intent and process evidence but has no
consumer that verifies their complete chain. Add a read-only verifier whose
result states integrity and recorded-command agreement, not executable/provider
authentication or full Binding verification. Without this consumer, later
integration would need to trust a final receipt or repeat the same consistency
logic. Parsing version text is a separate decision; this verifier preserves its
bytes and locators without inventing cross-harness normalization.

## Implementation and evidence

`verify_native_version` follows the independently anchored final receipt through
intent, preparation, canonical invocation and process receipts, then checks both
raw streams. All five receipts share one caller allowance. The original source
receipt and process-receipt allowances are also enforced. Combined stream sizes
must fit a separate caller allowance before the payload verifier opens either
file. The existing stable-read and process owners enforce file identity, exact
hash/size and completion consistency.

The verifier rebuilds the canonical version namespace command with the producer's
existing pure builder. Recorded command, environment, purpose, mount layout,
identity links and limit values must agree. Original paths undergo only lexical
checks. The policy is read; no original installation, task or runtime is read.
Both new fixture layouts still verify after those sources are removed. No command
is executed by the verifier. Integrity of a failed probe remains distinct from
a successful version response, native identity and full Binding verification.

Fifteen focused tests passed in 3.778 seconds. Fourteen fixture methods use real
bubblewrap and newly authored Python entrypoints, and are explicitly skipped
where bubblewrap is absent; invalid-input validation runs without it. The tests
exercise both native layouts, non-UTF-8 output, source removal, unchanged custody,
nonzero exit, timeout, byte-limit, missing final publication, receipt/payload
tampering, symlink replacement, exact/one-less byte allowances and re-anchored
semantic contradictions. Re-anchoring changes only new test fixtures; no
historical receipt is resealed.

`make check` completed with exit 0: **1,146 tests, four skipped, 191.289 seconds**.

The retained synthetic probe is
`/tmp/caplab-version-verify-probe-06w_xkh5`. Its new 69-byte Python entrypoints
each emitted 20 stdout bytes, including an invalid UTF-8 byte, and empty stderr.
Both processes exited zero. Reports before and after source removal were equal.

| Fixture layout | Independent version digest | Receipt bytes verified |
|---|---|---|
| Claude | `76163a94f1c73530b1b79a38444cbd1429d1a183b7f8cc7a6e356a3d0390e38c` | 7,480 |
| Codex | `aaf3aab1d06d446564ce43e136b9bcbc22d9f6bafe00ed7ba54034ff2449e55a` | 7,712 |

These are conformance fixtures, not native version or reviewer measurements.
The result reports their intact bytes and recorded command agreement while
leaving `native_identity_verified` and `binding_complete` false. It returns no
version text. Actual version interpretation, installation/runtime authentication,
account identity and capture integration remain separate work.

Thirteen protected files match `d503033` byte-for-byte: native version capture,
invocation/preparation/collection owners, task/process capture and verification,
Codex/Claude linkage, Codex events, the native launcher and native policy. The
new verifier uses the established direct receipt-chain style. It introduces no
generic entity model, strategy layer, external dependency or source-owner
refactor. The shared process checker consumes only the two stream/time fields
already supplied by the immutable version-limit object.

Retained artifacts use `/tmp/caplab-version-verify-`:
`probe.py`, `probe.json`, `probe.log`, `focused.log`, `make-check.log`,
`source-check.json` and `verification.json`. The final manifest records hashes,
terminal test results, advisory identities and exact scratch cleanup. Source
fixtures were removed; probe custody and logs remain. No native harness, account,
credential, historical capture, tracker or service was changed by this work.

## Advisory disposition and completion boundary

The retrieval-state gate passed against
`/home/halbritt/.local/share/pincite/release`, release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`. The initial packet identified obligations;
five typed evidence records supplied the inspected contracts, source, tests and
synthetic runtime observations. Final packet: `pkt-a403e50e06b4924e`, content
SHA-256 `a403e50e06b4924eb5a366c5792476e7e995cecf8b23fba52b68c902b26bb490`.

Applied `universal-repository-contract-precedence` to scoped authorization and
claim ceilings, `universal-evidence-before-intervention` to the missing verifier
and exercised producer bundles, `python-structured-cleanup` to the retained
descriptor owners, and `universal-preserve-behavior-by-default` to unchanged
producers and distinct process outcomes. Four citations classified as valid.

Eighteen generic obligations remain nonmaterial to this implementation:

| Routed concept | Missing requirements | Reason |
|---|---|---|
| `domain-identity-entity` | Expert distinction of sameness over time; identity scenarios; identity source and comparison rules; lifecycle or reference consequences | No entity or identity lifecycle is introduced. Existing hash, tuple and Binding meanings are preserved; the verifier checks the frozen receipt chain. |
| `domain-language-model-loop` | Authoritative examples; authoritative expert examples; feedback from implementation and usage; model expressed in executable behavior; terms whose meanings affect decisions | No domain-language/model revision is claimed. Repository terms govern the result; synthetic conformance does not establish expert validation of a new model. |
| `domain-modeling-investment-gate` | Business differentiation and product lifespan; business-value and expert-access evidence; expert access and feedback cadence; recurring ambiguity, contradiction, or rule defect; team capacity to sustain the model | No domain-modeling investment is proposed. This is a direct verifier for an existing producer contract. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Existing local checks pass and these configurations are unchanged. No expanded platform/tooling guarantee is asserted. |
| `python-repository-shaped-idiom` | Python and dependency version matrix; formatter/linter/type-checker configuration | Uses the existing Python setup and no external dependency or static-checker program. Broader compatibility is unmeasured. |

Eleven named doctrine scratch files are deleted after their hashes and receipt
results are consolidated. Logs and synthetic probe custody remain. The roadmap
was refreshed read-only into `/tmp/caplab-roadmap-after-reroute.json`; this work
does not close the integrated-capture, representative-episode or study-readiness
requirements. No independent acceptance or reviewer capability conclusion is
made. Authorization expires at the local commit containing this record.
