# Verify published evidence before calibration evaluation

## Decision and authorization

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
selects a prospective evaluation-boundary repair. Evaluation and cached-score
reuse must verify slot, scenario, model, effort, diff, and exact code shape
against the requested entry. New hash-linked publications must match their
supporting validated record and preserved source evidence. Legacy publications
may be read only when their original acceptance or recovery receipt and raw
capture establish the same judgment; absent proof is a refusal, not an
unverified score. Verification is read-only and never repairs or republishes
evidence as a side effect.

New CLI calibration results retain the manifest hash and hashes of the
published judgments and their supporting evidence. The pure numerical
`evaluate_calibration` function and its frozen gates remain unchanged. These
checks establish input identity and provenance, not correctness of the old
reference judgments or qualification of a reviewer.

Authorized effects are source changes, newly authored disposable fixtures,
tests, and this record. Do not evaluate, rewrite, admit, recover, revoke, or
rescore historical evidence under this authorization. No model calls, spend,
ranking, placement, or tracker writes are authorized. Stop if verification
requires those effects. Preserve the closed public ladder boundary. Revert
the source commit to undo this repair; dispose only of task-owned fixtures and
doctrine inputs. Verify wrong-rater and changed-evidence counterexamples,
matching evidence, legacy proof, result provenance, and the full suite.

## Observation and selected repair

At parent `943bb71`, `command_evaluate` reads only each publication's judgment
mapping, then labels the result with command-line model and effort. It ignores
the publication's subject identity, scenario, diff, and record link. Cached
reuse checks some identity fields and the new record hash but does not rerun
the preserved-evidence checks used for publication. Thus evaluation can use
another rater's answers or changed evidence under a plausible result label.

The existing publication verifier will expose its read-only result separately
from its write operation. A shared published-judgment reader will serve both
evaluation and cached reuse. Legacy receipt verification will use retained
files, not a live source lookup. Missing or contradictory proof stops before
statistics or any new native call. Leaving the evaluator unchanged, or merely
adding output labels, would leave the identity gap intact.

## Verification

The four initial disposable regressions failed seven assertions at the parent:
wrong rater identity, contradictory publication fields, changed native capture
in evaluation and cache, and missing supporting record. The focused suite now
passes 64 tests, including 15 new evaluation-boundary tests. Evidence is in
`/tmp/caplab-evaluation-red.log` and `/tmp/caplab-evaluation-focused.log`.

The tests exercise verified output with exact input hashes, original legacy
acceptance and recovery receipts, receipt contradictions, missing proof,
removed new-format record links, conflicting record identity despite a matching
record hash, duplicate JSON keys, attempt path traversal, changed supporting
files, byte-preserving reads, idempotent evaluation, and refusal to overwrite a
result after manifest bytes change. A fake native process authors the fixtures;
read checks prohibit native calls and live source lookup. The pure numerical
evaluator remains unchanged. Full `make check` passed 823 tests with 4 skips in 119.549 seconds; see
`/tmp/caplab-evaluation-make-check.log`. `git diff --check` also passed.

New CLI output is `caplab-rater-calibration-result/2`, with a
`caplab-calibration-inputs/1` provenance object. The pure numerical function
still returns its existing version 1 object. Existing result files are never
silently replaced. New publications must match the complete verified candidate
and record link; legacy records require original acceptance or a matching
recovery receipt plus retained source files. A legacy publication without this
proof is refused. No historical compatibility rate was measured.

These are consistency checks on retained evidence, not signatures, proof of
provider identity, proof that capture is complete, validation of old reference
judgments, or independent reviewer qualification. Model and effort identity
do not establish every dimension of a sealed Binding. No historical mismatch,
independent review, or study acceptance is claimed.


## Advisory doctrine receipt

The source-based decision is bounded by the repository authorization above.
The shared read-only verifier belongs in the existing artifact-rater CLI:
publication, cached reuse, and evaluation depend on the same validated evidence.
Its callers borrow parsed records; it returns a new publication dictionary and
does not mutate shared inputs. Legacy format policy stays explicit. A general
validation framework or numerical recalibration would exceed this repair.

The applied advisory concepts are `universal-evidence-before-intervention`,
`implementation-placement-by-ownership`, `python-mutable-ownership`,
`agent-conduct-authority-bounded-action`,
`universal-repository-contract-precedence`, and
`universal-preserve-behavior-by-default`. The evidence-backed packet is
`pkt-e44f37a96d362fb4`, content SHA-256
`e44f37a96d362fb48997a78f46a967b4925ad773ec6190bb0b6387f6682f5acb`.
Release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8` identify the advisory source.
The packet's execute ceiling does not create authorization. Source, repository
contract, and test evidence discharged the material obligations for this local
repair. Citation consumption is recorded in the local Pincite trace.

The following remaining obligations are nonmaterial to this bounded decision;
they do not support broader claims. Every missing requirement from the final
packet is retained below.

| Concept | Missing requirements | Nonmaterial rationale |
| --- | --- | --- |
| `data-dedup-key-identity-completeness` | an explicit enumeration of the record's identity dimensions matched against the key's columns; logical-identity definition of the affected record; the conflict-handling semantics at that key - abort update or silent drop | No database key or deduplication policy changes. Published field equality is tested directly. |
| `data-ingest-population-scoping` | a dry-run enumeration with counts compared against expectation; the discovery pattern shown to match the specification's depth and class constraints; the input population specification; the specified input population stated precisely | No traversal-based import or backfill. Evaluation reads the explicit manifest entries; population selection is unchanged. |
| `implementation-config-reference-validation` | a load-time or gate check resolving every reference against them; a named-identifier failure on mismatch; the consumer's defined identifier and enum sets | No new symbolic configuration registry. Fixed evidence formats and identities are checked directly and covered by mismatch tests. |
| `implementation-placement-by-ownership` | recurring change evidence when available | Current publication and evaluation callers demonstrate the shared rule; no longitudinal co-change claim is needed. |
| `implementation-rank-before-truncate` | the match-text composition enumerated field by field; the scan shown to score the full bounded set before truncation; the selection contract stated; the selection contract stated - relevance-ordered top-N versus first-N | No ranking, top-N selection, or match-text search is performed. |
| `operations-gate-authoritative-signal` | eval-versus-serving configuration parity; inventory of gates and the signals they observe; proof the check reads that signal rather than a derived view; the authoritative signal named for each gate | No operational gate or serving-parity claim is added. This repair verifies retained input consistency; the numerical gates remain unchanged and provider completeness is explicitly unproved. |
| `operations-symptom-cause-monitoring` | current page inventory classified symptom-versus-cause; golden-signal coverage with the error definition stated; the service's user-visible failure modes | No monitoring or paging behavior changes and no service health claim is made. |
| `task:defect-repair` | evidence-incidents; evidence-runtime-observation | The defect is demonstrated by local counterexamples. No production incident or live runtime observation is claimed or required. |
