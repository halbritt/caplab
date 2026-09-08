# CAPLAB-66: bounded redaction feasibility inspection

## Authorization before custody inspection

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
authorizes a read-only metadata inventory of the immediate children of:

`~/.local/share/caplab/campaigns/advisory-selection-001-ladder-2026-07-29/`

Select one repair episode by the lexicographically first injection-arm slot
name, without consulting its score or outcome. Inspect only that episode's
immediate file names to locate the supplied prompt/packet and retained native
event stream. Record the selected paths before opening their content. Stop
on a symlink, unexpected directory structure, missing inputs, or more than
50 MiB of selected input. Do not follow unrelated sessions or scan the archive
for a more favorable example.

Once its paths are recorded, authorized effects are reading that one episode's
prompt and native event bytes, hashing them before and after inspection, and
creating a private temporary derived redaction artifact, prototype source,
and inspection receipt. This explicitly permits copying only those selected
bytes into the private prototype's derived output. It does not permit copying
historical evidence into the repository, modifying or deleting source custody,
admission, registration, scoring, calibration, model calls, spend, ranking,
placement, or coder exposure. New synthetic counterexamples may be authored
locally to test the prototype's stated mechanism. No tracker changes or
messages are authorized at this stage.

The repository record may retain source locators/hashes, counts, prototype
identity, and bounded findings without reproducing historical content.
Preserve the September 7 instrument disposition, all source artifacts,
unrelated worktrees and untracked designs. Keep the prototype outputs private
and identify cleanup scope; delete only task-owned temporary files after the
needed provenance is retained. This is a feasibility inspection, not a
production redactor or independent acceptance of blinding.

## Question and preservation boundary

CAPLAB-66 requires removing both the served packet and agent restatements,
then mechanically verifying that removal. The existing artifact-rater prompt
omits explicit subject and arm metadata but includes the supplied diff
unchanged. Its test named as a blinded-prompt test checks omitted metadata on
a harmless fixture, not treatment cues embedded in the artifact. No active
transcript redactor was found in src/caplab, scripts, or tests.

Test exact-span removal as a bounded mechanism, including duplicates across
native records. Use explicit synthetic paraphrase witnesses to test whether
a clean exact-match scan can support the broader blinding claim. A negative
result must not be repaired by stripping arbitrary task-relevant content or
relabeling the result as verified. The old episode predates the maximal
capture configuration selected by CAPLAB-79; it cannot validate that future
configuration's complete redaction surface.

## Metadata discovery amendment

The campaign root contains 31 immediate entries, including `attempts/` and
an existing `leakage-probe/`, rather than direct slot directories. No episode
content was opened. Before constructing another prototype, the primary agent
authorizes read-only immediate-child filename inventories of those two exact
subdirectories. Preserve the same single-episode selection rule within
`attempts/`. First inspect whether `leakage-probe/` contains an existing
feasibility report that could change the next action; record any report paths
before opening their bytes. This amendment authorizes metadata discovery only,
not a broader campaign or transcript search. The input-size and symlink stops
remain in force.

## Selected input authorization

The attempts inventory has 591 directories, of which 279 names contain
`--injection--`. The deterministic selected slot is:

`attempts/02-domain-anticorruption-layer--injection--luna-high--t1/`

Within that slot, the primary agent authorizes reading `native.stdout` and
`rollout.jsonl` as the retained native event surfaces. The supplied prompt,
if present, will be located within that exact rollout; do not search other
episodes or the render tree for a replacement. No diff, code judgment, world,
or episode outcome file is opened for this selection.

The existing probe has exactly `leakage-probe/adversarial.patch` and
`leakage-probe/verdict.json`. Read and hash these two files before deciding
whether a new prototype is useful. Their bytes remain unchanged and are not
copied into the repository. A retained verdict without independent evidence
of its execution is not a newly verified model result. The selected native
files and these two probe files are the complete authorized content-read set,
subject to the 50 MiB combined limit and symlink prohibition above.


## Observations

The selected stdout contains 62 JSONL events; its retained rollout contains
137. The rollout has one supplied user prompt with the packet separated from
the task by an explicit delimiter. The packet span is 1,519 UTF-8 bytes,
SHA-256 `6264efef60e181985e472de70ec42540784acb8e0ade90c9474236e949189594`. It occurs twice in the rollout, in the
user response item and an event-message copy, and zero times as a complete
span in stdout. A stdout-only exact-match scan would therefore be clear even
before redaction while another retained surface contains the treatment.

The throwaway prototype recursively replaces the exact packet span in decoded
JSON string values and preserves the task span and JSON structure. It removed
two occurrences from the rollout and none from stdout. Both resulting streams
parse and contain zero complete exact packet spans. Derived JSON is
reserialized and is not byte-identical to raw capture; the raw sources remain
unchanged. The two modified rollout string paths are
`$[6].payload.content[0].text` and `$[7].payload.message` (zero-based arrays).

Two newly authored synthetic witness messages were then subjected to the same
removal and scan. One explicitly attributes a semantic-translation approach
to supplied advisory material; the other explicitly contrasts its extra
guidance with an unaided condition. Both survive while the exact packet scan
passes. They are controlled counterexamples to the scan's sufficiency, not
observed historical agent behavior. No frequency or prevalence is inferred.

The existing `leakage-probe/adversarial.patch` adds design-oriented prose and
a vacuous test while leaving relevant no-op behavior unchanged. Its retained
verdict has all three primary code bits false and SCOPE true. This is an
artifact-judgment probe, not a redaction or coder-blinding receipt. The two
files alone do not establish the rater's identity, execution lineage,
independence, or absence of treatment cues. No scoring was rerun and no new
claim of rater accuracy is made from that verdict.

## Inference and disposition

Exact-span removal is mechanically feasible on these two event surfaces.
A clean exact-match scan does not establish removal of paraphrases, smaller
quotations, cue-bearing paths, comments, or other restatements. This inspection
neither establishes their prevalence in historical episodes nor proves that
all possible redaction methods are infeasible. It specifically rejects using
this tested exact-match mechanism as verification of CAPLAB-66's stronger
requirement.

Metadata omission is likewise narrower than verified blinding. The current
artifact-rater prompt deliberately passes the candidate diff unchanged, so
a synthetic diff containing an explicit treatment cue was passed to
`build_artifact_prompt` and reached the resulting prompt unchanged. The test
`test_prompt_is_blinded_and_schema_is_exact` verifies omission of explicit
metadata on its fixture, not the semantic absence of treatment cues. Existing
continuity agreement is not upgraded to independent accuracy or verified
blinding by that test. The local check decoded the prompt's JSON diff string and verified exact
equality to the supplied synthetic diff; no rater was invoked. Its receipt is
`/tmp/caplab-66-artifact-cue-result.json`. No historical judgment or protocol
was rewritten.

CAPLAB-66 remains open. Before exposing a coded episode, the production design
must define the entire coder-visible surface and establish an adequate
validation method for that surface. The maximal capture design adds further
surfaces not covered by this older episode. More exact-string substitutions
alone cannot discharge the demonstrated counterexample. If proposed removal
would delete evidence needed by a code, the code or study design must be
revisited before freeze; do not silently change the observable or drop an
unfavorable episode. This record supplies no human blinding judgment and no
production redactor.

## Verification and custody

All four selected input files were hashed before and after the prototype run
and were unchanged. Their combined size was 579,194 bytes, below the frozen
50 MiB inspection limit. No other episode content, world, diff, score, or
render input was read. No model or coder was invoked.

| Input under the named campaign root | SHA-256 |
| --- | --- |
| `attempts/02-domain-anticorruption-layer--injection--luna-high--t1/native.stdout` | `e415659c43e55c517818d9e0e4841dfa853db1a1197485bb4ba7bbc1354d7cba` |
| `attempts/02-domain-anticorruption-layer--injection--luna-high--t1/rollout.jsonl` | `a04b81c3466261ee88fb5bd7da68266a5c0f38479fbd74ac8eff436e3393eea1` |
| `leakage-probe/adversarial.patch` | `dc27c05739ef1f313f6b9e1c5c4ee50b8f69e1183a84ae96ce2d58054e82466d` |
| `leakage-probe/verdict.json` | `ec6ce1be992fed25bbdb838d370a2c6cc2163fc36be008ad6a1c2786b810bad5` |

The retained private prototype is `/tmp/caplab-66-redaction-probe.py`,
SHA-256 `d5874ddb4dc026858c7a73e0b15bc6a61ffba79831efb39ebbad722a30edd800`. The machine-readable receipt is
`/tmp/caplab-66-probe-result.json`, SHA-256
`44d9a4fb01328d37d33599f1e5bc400dc1c57e5ffd283e64bc3f969c5aa9747e`;
its log is `/tmp/caplab-66-probe.log`. The receipt retains source hashes,
changed paths, counts and synthetic-test results, not historical prose.
The private derived transcript copies under `/tmp/caplab-66-derived/` are
removed after recording these results; they were never exposed as blinded
coder material. Prototype source and receipts remain for reproducibility.
No runtime code changed, so no full repository suite was rerun.

## Authorized planning annotation

After recording the observations above, the primary agent authorizes one
append-only description update to CAPLAB-66 pointing to this record and its
bounded negative result. Preserve the original description, Ready state and
all other issue fields. Re-read before mutation and stop on a concurrent
edit; verify the stored annotation. Do not close or supersede the issue.
No comments or messages are authorized.


## Advisory receipt

Packet `pkt-f1bd3dc4b06cb6f2`, content SHA-256
`f1bd3dc4b06cb6f2b3d0b95a6e0ba5e52376f609e0ada573c11c9e4e249592e1`, uses release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts are
`universal-evidence-before-intervention`, `universal-explicit-invariants`,
`universal-repository-contract-precedence`, and
`agent-conduct-authority-bounded-action`. Repository authority governs the
bounded inspection; a weaker exact-match observation must not become the
stronger blinding judgment. Citation consumption is recorded locally.

All remaining advisory obligations are nonmaterial to this bounded negative
feasibility result:

| Concept | Missing requirements | Reason |
| --- | --- | --- |
| debugging-causal-repair | causal explanation; changed path exercised after repair; failing reproduction before repair; first divergence; relevant regression evidence | No production repair is claimed. The prototype and synthetic witnesses establish a specific insufficiency, not the cause or prevalence of historical coder bias. |
| operations-contract-conformance-testing | consumer-owned contract tests with a run cadence; request-side and response-side suites separated from live dependencies; shared specification as oracle; the shared specification as the test oracle | No production redactor or native-harness conformance is asserted. This is a throwaway, single-episode feasibility probe with explicit counterexamples. |
| task:repository-assessment | evidence-co-change; evidence-generated-artifacts; evidence-tests; evidence-version-history | No architecture/coupling or standing-suite adequacy claim is made. The preserved prototype receipts report the actual local checks; they are not qualification of a production test suite. |
| testing-deterministic-async-observation | bounded deadline and failure diagnostics; observable completion criterion; observable completion or progress contract; repeated or adversarial scheduling results | The prototype is synchronous and reads fixed retained files. No asynchronous capture mechanism or scheduling guarantee is tested. |


## Planning projection verification

The CAPLAB-66 description was annotated and re-read successfully. Its original
HTML and state, title, priority, assignments, labels, parent, dates and other
checked fields were unchanged. The stored receipt is
`/tmp/caplab-66-after-probe-note.json`. The issue remains open. No other tracker
item or runtime source changed. `git diff --check` passed; unrelated untracked
`docs/designs/` content was preserved.
