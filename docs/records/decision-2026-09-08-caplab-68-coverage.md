# Prospective shakedown dimensions and exact coverage planning

Date: 2026-09-08. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `859badd`.

## Authorization before execution

Create `src/caplab/coverage_plan.py`, `scripts/shakedown_coverage.py`,
`tests/test_coverage_plan.py`,
`docs/product/contracts/shakedown-coverage-v1.md`, and this record. Add a
navigation link in `docs/product/README.md`. The planner may read one explicitly
named metadata document and emit a report; it must discover no worlds, read no
candidate bodies and change no custody state. Use only new synthetic metadata
and temporary files for executable checks. Run focused tests and `make check`.

After verification, append a resolution to CAPLAB-68 and mark its specification
item Done. Preserve its original text and unrelated fields; re-read before
writing and stop on concurrent change. No comments or messages are authorized.
Retain source/test/tracker receipts; remove only this task's doctrine scratch
after receipt recording. Authorization expires at commit.

No real candidate selection, sealed-world inspection, historical evidence
admission, model call, shakedown execution, ranking, placement or acceptance is
authorized. Preserve existing codebooks, populations, study arms, manifests,
source bodies, runtime services and `docs/designs/`. Actual dimensions/levels
and candidate classifications must be frozen and verified by an adopting study;
this task selects the prospective required axes and procedure only.

## Selected rule and rationale

Combine CAPLAB-68's build/language/mechanism/harness concerns with CAPLAB-81's
task, concept-category and observability concerns. Name seven required axes
and three specific interaction families in the contract. Their level mappings
must be explicit before selection; no inference from outcome or convenient
candidate availability is permitted. Every candidate still needs individual
world/code validation; structural coverage cannot stand in for it.

Select exact minimum cardinality, breaking ties by the lexicographically
smallest sorted candidate-ID tuple. Freeze IDs before output inspection.
The small planner supports at most 24 candidates, matching the scale the
historical design considered without adopting its count. It exhaustively
searches cardinalities, first including any candidate that is the sole witness
for a required token. It does not silently substitute greedy coverage.
An uncovered requirement is an ordinary infeasible report; malformed input is
an error. Input validation precedes selection, including unknown tokens.

The pure planner returns only declared-metadata coverage and witnesses. Its
remainder is not a seal, and input hashing is not evidence of a prior freeze.
The contract keeps unobserved status, tuning exposure and analysis holdout
separate. It qualifies the old CAPLAB-54 inference that control-only shakedown
can never inflate a result: blinding to contrasts does not remove selection or
design-tuning concerns. No historical comment or study assignment is rewritten.

The seal contract also exposes the headroom-screening conflict: inspecting
unaided scores for every world consumes each world's outcome exposure. Later
unread evaluation episodes do not restore a world's original unobserved
status. An adopting study must name the remaining independent evaluation
boundary and tuning history rather than using `sealed` for both meanings.

Leaving the minimum-cover instruction informal permits post-hoc choices.
Greedy selection can consume more worlds than necessary. A generic scheduling
optimizer or automatic metadata extractor would introduce unrelated policy
and exposure. The selected bounded planner performs only the declared set
operation; proof of real coverage and instrument validity remains external.


## Verification and interpretation limits

Eight focused tests passed in 0.262 seconds. Known minimum cases cover the
largest-first counterexample, equal-size optima without forced candidates,
forced candidates with a remaining tie, a single complete candidate, and 24
sole-witness candidates. Tests verify unchanged inputs, permutation-invariant
selection/witnesses, uncovered-requirement reporting, invalid types/duplicates/
unknown tokens, and the explicit candidate bound. The real CLI runs from a
temporary working directory with Unicode IDs, preserves input bytes, returns
the input SHA256 and creates no files. Its duplicate-key fixture is otherwise
valid, so a permissive JSON parser cannot pass merely through schema rejection.

The documented example was extracted and executed through the actual CLI:
B+C is selected, minimum cardinality is 2, and A remains a candidate. The
receipt `/tmp/caplab-68-coverage-verification.json` records its report, contract
hash and 21 resolved document links. Source example and output remain at
`/tmp/caplab-68-coverage-example.json` and
`/tmp/caplab-68-coverage-example-report.json`.

| CAPLAB-68 requirement | Resolution | Unestablished by this work |
| --- | --- | --- |
| Dimensions declared and justified | Seven named structural axes and three bounded interaction families | Actual population levels and truthful candidate classification |
| Minimum covering rule | Exact minimum size, exact-ID tie break, sole-witness inclusion and coverage witnesses | Instrument adequacy, power or causal identification |
| Seal remainder | Custodian acts under separate authorization; planner returns only candidate remainder | Actual sealing, exclusion history or an analysis holdout |
| Amendment semantics | Separate unobserved and untuned statuses; missing exposure records stay unknown | Any current world's exposure status |

Manual contract challenges include marginal coverage without a required
interaction, a no-change task with an incompatible write-required attempt
gate, absent levels hidden by dropping candidates, all candidates required
by the cover, and headroom screening that consumes outcome exposure. Each
requires its stated resolution; no metadata cover can clear these scientific
or authority gates by itself. The original CAPLAB-54 fixed-versus-held-out
reasoning remains subject to its synthetic-redraw reversal, not silently
adopted by this utility.

This adds a local pure function and read-only CLI using the repository's
strict JSON reader and unittest convention. No existing runtime path imports
the new planner; no campaign semantics, persisted schema or source custody
changes. The 24-candidate cap bounds the enumeration population, not elapsed
time. For larger inputs, a later change must preserve exactness or explicitly
change the contract; no optimization performance claim is made here.

## Decision-source provenance

The following Plane snapshots preserve descriptions and comments as planning
and decision provenance, not admitted empirical evidence. SHA256 identifies
the exact local envelope; source record IDs are retained inside it.

| Snapshot | Source IDs | SHA256 |
| --- | --- | --- |
| `/tmp/caplab-54-coverage-current.json` | 9bb87947-7076-4a86-90ac-bfceb9a7c462 | `ac1dc393c12b9b95ba1922f0c90e88bb28ba2e9b26666fcd1013f6cbf6aff4f1` |
| `/tmp/caplab-54-coverage-comments.json` | 7a0f285d-179c-4f01-90cc-1727ee888702, df3d3f97-83a2-4fc9-bc0b-77833eba6533 | `d2bb935ed5986a870e249d18ef04d723cc0bf8a8e9aa99a92e6083820e8b24cf` |
| `/tmp/caplab-68-coverage-current.json` | 6228a4ad-1305-45e4-a03b-bc6706d220f4 | `4397483332be22137c1ce77bb3533b301ba437e985a30093137ddef054495c6b` |
| `/tmp/caplab-68-coverage-comments.json` | no comments | `b295b980ae401e301c184e546feacfdb42c38f795088dec11bfd44d2557590fa` |
| `/tmp/caplab-81-coverage-current.json` | 672c0dd2-20af-4a9c-9f7d-9235e2f1e476 | `b5d399fee50331c111d010057e3f4cde5753d3663dc2bc18e7671918bbda1001` |
| `/tmp/caplab-81-coverage-comments.json` | ae63b877-a7e9-4425-926d-998c899b0d25 | `8b468cd5bdfeda7488b78e5d4045f3c567a16c36d0b096931f4dad21072458f9` |

## Advisory doctrine receipt

Release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` passed the retrieval-state
gate. Corpus `corpus-2026-07-12-a11702cc9217`; doctrine
`doctrine-f6bbb5196a3f8bf9`; retriever
`retriever-ec995ecdd083b2c8`. Final packet `pkt-1dc5eb323f4dff1f`,
content SHA256 `1dc5eb323f4dff1f1adb5055489ee6f095ee0f3e3d56bf3c144ffd4c03f6950f`.
One typed-evidence gathering pass; execute ceiling bounded by ADR 0026 and
this record.

Applied `testing-coverage-is-not-adequacy` to avoid treating coverage as
scientific validation; `implementation-normal-result-or-exception` for a
normal infeasibility result; `python-text-bytes-boundary` for exact UTF-8 ingress
and input hashing; and `agent-conduct-authority-bounded-action` to separate
planning, actual selection, exposure, execution and acceptance.

Remaining obligations are nonmaterial to the bounded implementation claim:

| Concept | Remaining requirements | Scope disposition |
| --- | --- | --- |
| `implementation-normal-result-or-exception` | frequency and caller handling | No existing production caller or frequency claim. The new CLI explicitly handles infeasibility as a normal result and malformed input as an error. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | No root .github workflow was present; Makefile defines the exercised unittest gate. No CI matrix, formatter or static-analysis success is claimed. |
| `implementation-risk-driven-tests` | defect reproduction when applicable | This is a new planner, not a repair of an existing executable. Known minimum examples and failure cases supply the behavioral oracle. |
| `python-repository-shaped-idiom` | Python and dependency version matrix; formatter linter and type-checker configuration | The project requires Python >=3.12; new code uses the standard library and the repository strict parser. Only the local interpreter/suite is verified; no wider interpreter or formatter matrix claim. |


## Final verification and planning projection

The final `make check` run passed 897 tests with four skips in 122.004 seconds
on Python 3.12.3. No source or test changes followed it. The first full run
also passed; the second was required after strengthening the duplicate-key
fixture so rejection could not be explained by an unrelated schema error.
Logs: `/tmp/caplab-68-coverage-focused.log`,
`/tmp/caplab-68-coverage-make-check.log`, and
`/tmp/caplab-68-coverage-final-make-check.log`. This is execution verification,
not independent acceptance or a scientific-validity assessment.

`git diff --check` passed. Four doctrine citations classified as
`valid-packet-citation`; the task's temporary packet, evidence and citation
scratch files were removed after recording the receipt. Source, example,
verification and tracker receipts remain.

CAPLAB-68 was re-read immediately before updating and matched the complete
pre-update snapshot. Read-back verified the exact appended description, Done
state and newly set completion time. Only `updated_at`, `description_html`,
`completed_at` and `state` changed. Original text and unrelated fields were
preserved; no comments or messages were sent. Receipts:
`/tmp/caplab-68-before-coverage-update.json`,
`/tmp/caplab-68-immediate-coverage-update.json`,
`/tmp/caplab-68-coverage-update.ndjson`,
`/tmp/caplab-68-coverage-update-result.json`, and
`/tmp/caplab-68-after-coverage-update.json`.
The subsequent roadmap read `/tmp/caplab-roadmap-after-68.json` contains 13
open items; the overall objective remains incomplete.
