# Reject ambiguous JSON in production review reports

Date: 2026-09-08. Baseline: `fa43c50`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Reproduce ambiguous JSON interpretation using newly constructed temporary
ledger, report, and review-body bytes. Patch all store-object access during
these probes; no live store or historical evidence body may be read. Repair
`scripts/review_criterion_ledger_pass.py` and `scripts/review_canary.py` to
reject duplicate object keys and non-JSON numeric constants and require UTF-8
at their JSON read boundaries, using the existing strict parser. Preserve
ordinary valid-input semantics and the latest-body/gate precedence rules.

Update `tests/test_review_canary.py`, the production-review report guide, and
this record. Version new report interpretation explicitly; retain support
for verified historical report prefixes without claiming identical report
calculations. Verify synthetic failure cases before and after the repair,
valid-input preservation, focused tests and `make check`. No campaign, model
spend, ranking, placement, admission, source-store mutation, or historical
report regeneration is authorized. No tracker update, comment, or external
message is part of this repair. Preserve `docs/designs/`, sibling worktrees,
and unrelated state. Remove only this task's named doctrine scratch after
recording its receipt; retain verification logs. Authorization expires at commit.

## Observation and selected response

The shared criterion reader currently uses permissive `json.loads` for ledger
events and review bodies. The canary uses it for its baseline report and the
baseline export's terminal record. A repeated key can silently replace a
verdict, an event linkage, or a follow-up cutoff. A content hash identifies
those bytes but does not establish a unique interpretation.

Select fail-closed JSON decoding at those four boundaries. An ambiguous
review body remains an explicit invalid-body observation; a separately
recorded review gate can still supply the existing labeled fallback. An
ambiguous ledger or baseline fails before report output. Preserve original
bytes and existing reports; do not infer that a historical campaign contained
this defect without inspecting it under separate authority.

No change leaves an observed parser choice masquerading as an unambiguous
review observation. Adding a second bespoke parser duplicates existing
repository behavior. A full event-schema validator is a different change;
this repair makes no claim to validate every event field or reference.

## Execution and verification

Reused `caplab.codex_events.parse_native_json` at all four read boundaries,
with explicit UTF-8 decoding. The body boundary preserves its `invalid-json`
status and hash/event locators. It supplies no verdict and cannot inherit an
older body verdict; the separately labeled gate fallback is unchanged.
Ledger and baseline errors reach the CLI before output-directory creation.
No new dependency, permissive fallback, normalization, store mutation, or
scoring/placement rule was introduced.

New canary reports use `caplab-review-canary/4` and declare
`json_interpretation: utf8-unique-object-keys-no-non-json-constants/1`.
The baseline reader accepts versions 1 through 4 subject to current decoding
and prefix verification. Version migration can change interpretation of
ambiguous source bytes; it does not rewrite historical reports. Ordinary
latest-body/gate selection and ledger-sequence downstream ordering retain
their existing versioned rules.

Before repair, the synthetic body
`{"verdict":"reject","verdict":"accept","findings":[]}` produced a
parsed-object observation with verdict accept. This was observed with
store-object access patched to supply only those newly authored bytes:
`/tmp/caplab-review-json-before.json`.

Five new regression tests exercised 26 failing subcases before the repair;
`/tmp/caplab-review-json-red.log` records them. Cases include opposite verdict
orders, duplicate equal values, escaped-equivalent keys, nested duplicates,
NaN/Infinity tokens, UTF-16 and invalid UTF-8 bodies, preceding valid bodies,
gate fallback versus unknown decisions, duplicate ledger fields, duplicate
baseline cutoffs, and a duplicate terminal sequence with a matching source
hash. CLI checks confirm no report directory on ambiguous ledger/baseline
input. A positive case preserves composed/decomposed accented text, CJK, and
emoji exactly. Existing CLI coverage now asserts version 4 and its policy.

The retained probe `/tmp/caplab-review-json-valid-probe.py` constructs four
new synthetic runs with closed/open, known/unknown, body/gate disagreement,
Unicode, and downstream-event cases. Its before/after canonical JSON files
are byte-identical after excluding only the report version/policy additions
and the temporary source path. This comparison covers the criterion summary,
per-run observations, strata, and canary report; it is not a historical-data
parity claim. The probe patches all body-store reads.

| Verification | Observed result | Receipt |
|---|---|---|
| Focused suite | 28 tests passed, 0.546 seconds | `/tmp/caplab-review-json-focused-final.log` |
| Full repository check | 902 tests passed, four skipped, 124.971 seconds | `/tmp/caplab-review-json-make-check.log` |
| Valid synthetic input | Byte-identical retained comparison | `/tmp/caplab-review-json-valid-before.json`, `/tmp/caplab-review-json-valid-after.json` |
| Source guard | Both changed scripts parse; every direct import is referenced | Python AST/name inspection |

Checks used Python 3.12.3 and the repository Makefile's unittest command.
No production or test source changed after the full check began. Source review
confirmed four read replacements, preserved exception/fallback ownership,
and no unused imports or speculative abstraction. The full suite is evidence
for its exercised cases, not deployment or independent acceptance.

## Limits

This is JSON decoding discipline, not complete Striatum event-schema or
reference validation. It rejects duplicate names and the literal non-JSON
constants; it does not establish bounds or finiteness for every otherwise
valid JSON number. It does not verify that an event's semantic claim is true,
that a review is correct, or that backend labels identify exact Bindings.
Actual historical incidence remains unknown; no live export or store was
inspected and no historical report was regenerated for this repair.

## Doctrine receipt

The release retrieval-state gate passed. Release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`.

Final packet `pkt-fa47117b4660d970`, SHA-256
`fa47117b4660d9709dab0c5ff70f23b5d729dc2b553e783b7e6c5bf8585a49d3`.
One evidence-gathering pass supplied six typed records for authority,
contracts, source structure, synthetic reproduction/parity, tests, and
observed toolchain/text boundaries.

Applied `universal-repository-contract-precedence` to preserve report-only
and historical-custody limits; `universal-evidence-before-intervention` to
scope the fix to reproduced decoding behavior; `python-text-bytes-boundary`
to decode explicit UTF-8 without normalization; and
`python-runtime-static-boundary` to enforce unique interpretation during
reads rather than trusting hashes or annotations as validation.

All remaining obligations are nonmaterial to this bounded decoding repair:

| Group | Exact unmet requirements | Classification and reason |
|---|---|---|
| `data-event-time-semantics` | observed delay and out-of-order distribution | Nonmaterial: no ordering, lateness, or observation-window rule changes; existing sequence-order tests and valid-input parity pass. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI, formatting, or static-tool guarantee claimed; the inspected local Makefile check passes. |
| `python-mutable-ownership` | concurrency; lifetime and size | Nonmaterial: no concurrency or lifetime policy changes; new decoding objects remain under existing reader ownership. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no formatter or checker rule is changed or claimed; syntax/import checks and executable tests cover this repair. |
| `python-runtime-static-boundary` | annotation maintenance cost; checker and trust-boundary evidence; configured checker and Python version | Nonmaterial: no annotation or static-proof claim is added; observed Python3.12.3 and runtime failure tests support the narrower claim. |

Citation classification and final diff/link checks precede commit. Only the
named `/tmp/caplab-review-json-doctrine-*` scratch files are removed after
retaining this receipt. Verification logs and synthetic comparison artifacts
remain. No tracker field, comment, or external message was changed.

Final verification: 4 local document links resolve; four doctrine citations
classified as `valid-packet-citation`. Receipt:
`/tmp/caplab-review-json-verification.json`.
