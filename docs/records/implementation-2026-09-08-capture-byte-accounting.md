# Account for retained capture bytes by surface

## Authorization before implementation

Under ADR 0026 and the continuing CAPLAB improvement goal, the primary agent
authorizes a prospective read-only accounting API and CLI in CAPLAB, focused
tests, a contract guide, and this record. CAPLAB-79's capture decision requires
per-surface bytes for CAPLAB-84 budget measurement. Existing verifiers check
bundle totals but supply no combined surface accounting.

The report must verify independently anchored task and native-collection
bundles through their existing verification owners, check the recorded task
roots agree, then report logical file bytes and symlink-target bytes separately
for before/after inventories, stdout/stderr, and each selected native location.
Missing locations remain unavailable; retained empty locations have zero
bytes. Duplicate retained content counts at each retained occurrence. Receipt
bytes remain separate from payload accounting. Neither measure is allocated
disk usage, runtime peak usage, native execution linkage, or capture overhead.

Preserve existing collector, verifier, linker, policy, and frozen-study behavior
and output contracts. Use new trusted local Python fixtures, including binary
content, symlinks, missing/empty locations, failed or bounded processes, corrupt
custody, and unrelated bundles. No native harness, model call, network access
by a fixture, historical evidence processing, registration, scoring, tracker
mutation, deployment, or human-time commitment is authorized. Use temporary
test directories only; retain command logs and a synthetic CLI example under
`/tmp/caplab-capture-accounting-*`. Preserve unrelated workspace and services.

Stop on an unexplained integrity failure or a need to weaken the existing
verification contract. Run focused checks and the repository's required suite,
review units and limits against the guide, and verify source preservation.
This authorization expires at the implementation commit or a failed bounded
implementation. It does not authorize a live campaign or independent acceptance.

## Implementation and bounded evidence

Baseline: `634bfd1`. The new `caplab.capture_accounting` module composes the
existing task and native-collection verifiers without changing their contracts.
A bounded anchored metadata reread supplies surface detail; the caller retains
the same quiescent-custody requirement as the existing linkers. The CLI
`scripts/capture_bytes.py` requires both independent receipt anchors and an
explicit receipt allowance, and emits no report on verification failure.

This is a new reporting behavior, not a capture repair or performance
optimization. Leaving the existing totals alone would leave the required
per-surface accounting to ad hoc scripts. Summing directory sizes would count
unreferenced files and would not verify the recorded evidence. Altering each
collector's receipt would change existing capture contracts unnecessarily.
The selected projection owns accounting only and leaves capture/verification
policy with its existing owners.

Both native layouts were exercised using newly authored binary files and a
trusted Python process, without starting either native harness. The example
deliberately exits 7 after adding a five-byte task file. The before and after
snapshots retain identical two-byte files twice each; native session custody
also retains two copies. The resulting 22 regular-file payload bytes plus
three symlink-target bytes give 25 logical payload bytes. Content equality
does not erase retained occurrences. Receipt bytes are measured separately;
symlink targets are already encoded inside those receipts and cannot be added
again as physical storage. This example is not a native cost estimate.

The retained CLI example is `/tmp/caplab-capture-accounting-probe-zfarkh0t/`,
with its fixture custody, `command.json`, `report.json`, and empty `stderr.log`.
The command exited zero and its output has the expected 25-byte logical total.
The example reports a nonzero process return code and unavailable native
completeness. The fixture's configuration identifies a planned tuple, not an
observed model. No source evidence from a historical campaign was processed.

Four new test methods cover both layouts, duplicate/binary content and
symlinks, source removal, byte-limited streams, missing versus empty locations,
wrong anchors, unrelated task roots, corrupt task and native bytes, receipt
limits, exact API/CLI agreement, and no CLI output on failure. The first
focused run exposed an incorrectly named diagnostic location in the new test;
the assertion was corrected to the existing plan's `diagnostic_search_root`.
No production behavior was relaxed. Final focused verification passed 29
tests in 5.606 seconds, including both existing verifier suites, in
`/tmp/caplab-capture-accounting-focused-complete.log`.

Per-surface observations include failed processes and bounded stream prefixes,
but attempts lacking final receipts cannot be verified by this API. They remain
unavailable, not zero-cost. Peak runtime storage, incremental capture overhead,
redaction time, and manual work remain unmeasured. CAPLAB-84 still requires
representative native repair measurements, failure accounting, and integration;
CAPLAB-66 still requires blinding validation. No roadmap item is closed here.

## Final verification and advisory receipt

`make check` passed 1,178 tests in 154.193 seconds with four existing skips;
the process exited zero. Log: `/tmp/caplab-capture-accounting-make-check.log`.
The skipped campaign/PostgreSQL integration checks remain unverified here.
The eight protected source and policy hashes in
`/tmp/caplab-capture-accounting-sources.json` remain unchanged. The documentation
guard checked the CLI arguments, linked contract paths, accounting units,
missingness semantics and claim boundaries against source and tests. The code
guard checked error propagation, reuse of verification owners, resource cleanup,
and the absence of mock success paths or unverified-total fallback behavior.

Advisory packet `pkt-e194cfba4229e0f6`, content SHA-256
`e194cfba4229e0f659c5c17dab0915ae4905e338cacd2b7116133f76c564d18f`, used validated
release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`, and
retriever `retriever-ec995ecdd083b2c8`. The release gate verified its index
checksum and committed retrieval sources, with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.

Applied guidance: `universal-repository-contract-precedence`,
`universal-evidence-before-intervention`, `universal-preserve-behavior-by-default`,
and `agent-conduct-authority-bounded-action`. Four structured concept citations
were classified successfully. Five typed observations retain source, contract,
authorization, decision and focused-execution provenance. CAPLAB's delegation
and capture requirements own this implementation; the advisory does not grant
execution authority or independent acceptance.

The packet's 33 remaining mechanical obligations are nonmaterial to the bounded
recommendation for these reasons. Each exact requirement and classification
is retained in `/tmp/caplab-capture-accounting-verification.json`.

| Obligation group | Scope reason |
| --- | --- |
| Recurring change evidence | This implements an explicit accounting requirement; it claims no recurring co-change or architectural debt. |
| Language conformance and repository idiom | No dependency, interpreter requirement, formatter, static checker or existing public API changed. Local neighboring APIs and the existing build command govern this addition; no broader toolchain comparison is claimed. |
| Mutable ownership | The new API receives paths, digests and an integer; decoded receipts are locally owned. No shared mutable argument graph, concurrency mechanism or new identity policy is introduced. |
| Runtime/static boundary | All counted metadata passes the existing runtime verifiers. No static typing guarantee or newly discovered defect class is claimed. The new failure paths are exercised by corrupt and mismatched bundles. |
| Text/bytes boundary | The projection counts verified lengths without decoding or normalizing payloads. Existing verifier decoding policy is preserved; binary payloads are exercised. No new text transformation or general encoding round-trip claim is made. |
| No-change procedure | The explicit capture requirement and alternatives are recorded above. This is no performance, maintenance-cost, security or dependency audit, and there is no quantified operational saving claim. |

The verification manifest retains advisory identities, typed observations and
citation results, all input/output hashes, command-log hashes and the synthetic
probe inventory. After consolidation, only the eleven specifically named
advisory scratch files are removed. The pre-execution authorization, frozen
pre-verification decision, source snapshot, all test logs, and example custody
remain available. Unrelated `docs/designs/` remains untouched. No model spend,
tracker changes, registered evidence admission or human judgment occurred.
