# Inspect tool-pair compatibility on one retained native repair

Date: 2026-09-08. Baseline: `ae749e3`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before source inspection

Inspect exactly the following two files under
`~/.local/share/caplab/campaigns/advisory-selection-001-ladder-2026-07-29/attempts/02-domain-anticorruption-layer--injection--luna-high--t1/`:

| File | Required SHA-256 |
| --- | --- |
| `native.stdout` | `e415659c43e55c517818d9e0e4841dfa853db1a1197485bb4ba7bbc1354d7cba` |
| `rollout.jsonl` | `a04b81c3466261ee88fb5bd7da68266a5c0f38479fbd74ac8eff436e3393eea1` |

These identities come from the earlier
[CAPLAB-66 inspection](inspection-2026-09-08-caplab-66-redaction-feasibility.md),
which selected this slot lexicographically without consulting outcomes. Reuse
that fixed selection; do not search for another example based on parser results.
The current authorization permits read-only hashing and bounded in-memory
parsing of these two files, with a one-MiB combined limit. Refuse symlinks,
changed bytes, unexpected file kinds, absent files or missing/ambiguous root
metadata. Use root ID metadata from the separately hash-identified rollout,
not a root chosen from stdout to make its check pass.

Run the current pure report API and raw-file CLI against the fixed stdout
identity. Inspect source event types, IDs, scope fields, native lifecycle and
outcome fields, and exact line/byte references. Retain only structural metadata,
hashes, counts, report output, inspection scripts and verification receipts in
private `/tmp/caplab-real-tool-pairs-*` custody. This explicitly permits a
derived structural report, not copying historical task text, command bodies,
tool outputs or transcript bytes into another artifact. Record observations in
this file only; runtime/tests/contracts remain unchanged unless a subsequent
bounded repair authorization names those effects.

Do not execute captured commands, models or native harnesses. Do not fabricate
current task-capture receipts for the old files, admit or register the episode,
score it, expose it to coders, rewrite/purge historical custody, change study
exclusions, update Plane, send messages, push or change services. Preserve
unrelated `docs/designs/`, worktrees and timers. Hash both sources before and
after inspection. Consolidate advisory evidence before deleting only named
advisory scratch, and commit this record locally; authorization expires at
commit. Stop rather than loosening format or identity checks to get a report.

## Question and claim ceiling

Determine whether the implemented event associations and their provenance
match the exposed structure in this one retained repair. It predates the new
maximal capture profile and the task-capture receipt chain. Compatibility here
does not establish current-version native emission, complete tool activity,
representative coding legibility, blinding, work correctness, reviewer value,
or the newer capture-backed inspection's historical applicability.

## Observations

Both fixed source hashes matched before and after inspection. Stdout contains
165,148 bytes and 62 JSONL events; rollout contains 412,488 bytes and 137
records. The rollout's unique first `session_meta.payload.id` supplies expected
root `019fb170-2db1-7160-826d-7f342f37407a`, which matches stdout initialization.
This cross-file agreement does not independently authenticate the historical
producer, model or harness version.

The report contains 26 paired groups: 21 command-execution items and five
file-change items. There are 26 starts and 26 completions, with no supported
updates, ambiguous groups, unmatched groups or unclassified events in this
stdout. The remaining events are seven agent messages, thread initialization,
turn start and a turn-completed record. No message bodies were retained in the
derived report.

The inspection checked all 62 event byte spans and hashes against the fixed
stdout and all 52 group references against source item IDs, event kinds,
pointers and selected native outcome fields. Direct source lifecycle totals
match report totals. The existing raw-file CLI exited zero with complete
streams, empty stderr and JSON equal to the pure API report. The process
receipt describes this inspection CLI, not the historical native attempt.
No current task-attempt receipt was created for historical files.

The exact inspection script is `/tmp/caplab-real-tool-pairs-inspect.py`;
its result is `/tmp/caplab-real-tool-pairs-result.json`. Report and CLI custody
are retained under `/tmp/caplab-real-tool-pairs-inspection-8audl1xt/`.
`report.json` has SHA-256
`1aba2ea9bd3fad7f045649feca3c94915bab548303225557aeed589cd64c4985`.
The CLI stdout has the same digest. Only structural metadata and its inspection
receipt were derived; source files remain at their original locations.

## Inference and delegated decision

The current reporter is compatible with the exposed event structure of this
one fixed historical Codex-format repair. No parser repair is indicated by
these checks. Keep runtime, tests and contracts unchanged; record the bounded
observation rather than add a historical fixture or select another source.
The alternatives would require new authority and evidence: changing the parser
without a reproduced discrepancy has no demonstrated benefit, while broader
native coverage requires a separately selected and authorized read or run.

This is not a claim about current native versions, other captures, Claude
compatibility, completeness, command success, independent test outcomes,
representative coding reliability or reviewer capability. The report retains
`capture_complete` and `work_correctness` as null and
`native_execution_linked` as false. A paired group establishes observed IDs
and ordering only. The historical episode remains outside study admission;
CAPLAB-63, CAPLAB-77 and CAPLAB-84 remain incomplete.

## Advisory closure and verification

Pincite's retrieval-state gate passed against release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-c76e171e2422e21f` has content hash
`c76e171e2422e21f084b14d25e7cbace39393ad77a8e94ab2626d1275cc85fad`.
Four typed observations establish scoped authority, current source structure,
inspection results and applicable instructions. Four consumed citations
classified as valid: repository-contract precedence, evidence before
intervention, explicit invariants and authority-bounded action.

Thirty-two remaining generic obligations are retained individually as
nonmaterial with rationales in
`/tmp/caplab-real-tool-pairs-verification.json`. These do not support broader
claims about repair causality, architecture, recurring service conformance,
scheduling robustness or overall repository health. The receipt preserves the
packet, evidence, source locators, versions and citation classifications.
Ten named advisory scratch files are consolidated there before removal.
Authorization and observation snapshots, inspection script, report, result and
CLI custody remain separately inspectable.

Verification checks source identity preservation, report/CLI agreement,
retained CLI stream hashes, repository source identity and local record links.
This documentation-only inspection does not rerun the full test suite or
claim new regression coverage. Local integration consumes this authorization;
verification is not independent acceptance or roadmap completion.
