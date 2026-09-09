# Inspect the recorded finding in production review 403588

## Authorization before source inspection

Under ADR 0026 and the continuing CAPLAB improvement request, the primary agent
authorizes bounded report-only inspection of the sole refusal in the fixed
production window recorded at `634bfd1`. The selection rule is the only
refusal among the 42 review runs opened after sequence 403343 in the retained
snapshot through 408812; it is not a representative reviewer sample.

Verify the report at
`/tmp/caplab-production-followup-tyk04scp/report/report.json` against SHA-256
`f39441c9c42264abc8566e9e068c7480e5cb6dfd23cced8e9ae96c3e06498f19`.
Read the exact review body for run403588, SHA-256
`1acb1fa16516bae47073312d9270657084de5fe3064bef9e9d9388ddb2dd9bed`, and the
reviewed change-set body at version403583, SHA-256
`73f1d90d74e7f227a86c6891dd8127d8343dc32649ffa5ab21f8fbf1eb53970d`.
Read the later admitted same-identity version403612, SHA-256
`579a65bf2ad7656c6c08d21b8f11d46a6ef137f84c4d638d0c9a60d7ff469ea3`,
only to distinguish its contents from the original candidate, not as truth.
Source object store:
`/home/halbritt/.local/share/striatum/graphs/019f22ef-0cb4-780f-9b82-b210bab24325`.

These exact historical objects may be copied into a new private local
`/tmp/caplab-refusal-403588-*` directory with source paths and hashes retained.
Permit at most one MiB compressed and five MiB decompressed per object; stop
on an unexpected format, hash mismatch, missing source, or limit failure.
Retain the extraction procedure and its bounded output receipts. No source
mutation, experimental admission, correctness label, scoring, ranking, model
call, external request or other repository change is authorized. The
repository record may retain locators and bounded observations without copying
the historical artifact bodies into the repository.

Inspect whether the review supplies an executable defect claim or a different
kind of objection. Any subsequent historical tree materialization or defect
execution requires a further exact authorization after the source is known.
Preserve source custody, unrelated worktrees, services, and untracked designs.
This read authorization expires at this inspection's commit or bounded failure.

### Extraction correction

The first extraction stopped before launching a decoder because the local
script supplied `max_wall_seconds`; the existing capture API requires
`timeout_seconds`. Only the review's compressed payload was copied; no final
body or capture receipt was produced. Preserve that script and payload.
The delegate authorizes one corrected extraction of the same three exact
objects, using new capture directories under `fixed/` and the same bounds.
Do not overwrite an existing compressed copy; require identical bytes before
reusing it. No source or inspection scope is broadened by this correction.

### Declared base inspection

All three corrected extractions completed with matching hashes. The original
and later change sets name the same observed product and four ordered ancestor
overlays. To determine whether exact historical execution can be reconstructed,
authorize reading and locally retaining these five explicitly declared objects
from the same object store, with unchanged source provenance:

- Observed product: `a7c4dc978d9dd3307682c73f4c2268d128643a0ad6830650e80fe6a1f6207e99`.
- Ancestor403092: `d67ec12a4d307bca658c9f217bbd3c0e3d36bde71a28a8e503c0b2e63863e2b2`.
- Ancestor403256: `bae441d4e555e36f5496dde58aa221a86547d41080eb6d2d6fd8bfa7ce3aa11d`.
- Ancestor403407: `fadf5eca7277d2973fca15a48b779a563c656807e7a790c5f7676cfd7f205862`.
- Ancestor403491: `4ee88b62a505b2f1c6dcf9bc666b65403d55b631508bbc6320b7dd53c6bcbeeb`.

Use separate `base-inputs/` capture directories, with at most eight MiB compressed,
64 MiB decompressed, and ten seconds per object. This amendment permits source
inspection and copying only; it does not authorize historical code execution,
qualify the materializer, admit a defect, or infer a reviewer correctness label.
Stop on a missing/ambiguous base or failed content verification. The original
five-MiB bounds remain the limits for the three review/change-set objects.

## Verified source observations

Custody is `/tmp/caplab-refusal-403588-rdioq9hr/`. The corrected decoder runs
all exited zero with complete bounded captures and matching content hashes.
The review contains 6,699 bytes; original change set 108,208; later change set
114,800. The five base inputs contain 197, 139,297, 70,822, 227,097 and 126,010
bytes respectively. `sources.json` and `base-sources.json` retain exact source
object paths, compressed-byte hashes, content hashes, lengths and extraction
receipts. Source object bytes were checked unchanged after extraction.

The review contains three major findings and one minor test-coverage finding.
They concern record registration, ledger-prefix construction, a context lookup,
and integration coverage. These severities and claims are the reviewer's
recorded judgments; this inspection does not adopt them as labels.

Finding RV-003 names `internal/driver/scheduler_telemetry.go`. In the original
retained file, line693 selects `all[contextRef-1]`; line694 rejects when the
selected record's sequence differs from `contextRef`. Under a contiguous
zero-based ledger, entry index `i` has sequence `i`, so a positive reference
selects its predecessor and fails that equality check. Arithmetic witnesses
for references 1, 2 and 10 are retained in `source-inspection.json`. They
evaluate that expression under the stated prefix assumption; they do not
execute the historical Go function or demonstrate its complete runtime path.

The original `TestDriverEvidenceProjectionProducesStrictV6Decision` fixture
does assign sequence1 to `graph_genesis`. Its inspected body tests evidence
binding and scheduler evaluation; that fixture alone is not evidence of a
full live-dispatch test. The later source replaces the index expression with
`schedulingRecordAt(all, contextRef)`. This corroborates the specific source
relationship and records a subsequent edit, without proving that the later
candidate works or that the refusal as a whole was correct.

## Reconstruction discrepancy: no historical execution

The observed product names Git commit
`80db8bb3894b78ddc3ea41c40ae2a799c349f269`, tree
`8e674b28321617d327e26db3c329b88d907cd015`. The tree identity was checked in
the Striatum repository. No historical worktree was created or code executed.

Applying the four declared ancestor overlays through CAPLAB's existing
`apply_overlay` and `tree_hash` functions yields the declared composed-base
hash `54a9eb7e972708b2631daac63ac447d477770040f86f1d020c67e2e356d02c02`.
However, overlaying either candidate onto that base yields a different hash
from the candidate's `result_tree_hash`:

| Candidate | CAPLAB-computed overlay result | Declared result |
| --- | --- | --- |
| 403583 | `fb0334ceeae392315b2be45e167741a6f258df5a6739c4da0ba5af469757b786` | `3f42e27856fe40ec536517a0ba99dd1dd8c60e2b1c66dff991ccc9f945fcb546` |
| 403612 | `658a4b5ffd8aa6fdf59676202a64197aa2356d766b1670a821549101027080ed` | `7204392c1424dfe7d4514fb7798baeac368a5b444207257f796e9f8d306269cd` |

`compose.py` repeats the calculation from hash-checked retained bodies.
Its `composition-recheck.json` agrees with the initial
`composition-inspection.json`. `implementation-provenance.json` binds CAPLAB's
materializer source and the historical Striatum change-set implementation.
The latter defines `Apply` with a result-tree hash comparison; `ApplyOverlay`
alone explicitly omits that check. Inspecting the source is not a Go execution
or a cross-language conformance test.

The discrepancy remains unexplained. It could concern these recorded result
hashes or a mismatch between CAPLAB's reproduction and the historical native
semantics. Matching the composed base does not disambiguate those explanations
for the candidate results. Do not silently replace the declared hashes, claim
an exact executable reconstruction, or describe this as a confirmed Striatum
materialization defect. The next bounded investigation must compare the exact
historical Go implementation's results before any candidate execution.

## Disposition and limits

Retain this as source-inspection evidence and an unresolved reconstruction
discrepancy. The actual code provides more than the downstream revision link
alone, but no independent runtime reproduction or adjudicated outcome has been
established. The selected report uses a ledger backend label, not an exact
verified CAPLAB Binding. This refusal-selected single case supplies no reviewer
accuracy rate or prevalence estimate, and does not unpark criterion replay or
change placement. No historical evidence was admitted or labeled as gold.

No CAPLAB runtime code changed. Relevant verification was bounded extraction,
content/source hash checks, exact-source inspection and repeatable overlay
arithmetic; the full suite was not rerun. Skipping the base/result checks and
executing a plausible reconstructed tree would weaken the evidence identity.
Stopping at the revision link would miss both the concrete source claim and
the reconstruction discrepancy. The bounded inspection preserves these two
findings separately for the next investigation.

## Advisory and final custody receipt

The narrowed disposition was checked against evidence-backed advisory packet
`pkt-1a34480873565861`, content SHA-256
`1a34480873565861ffa1cfc692989681aed2992651b8a585cebf68d4eddc9c94`.
Release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` passed the retrieval
state gate: corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`, source
fingerprint `ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Five valid concept citations cover evidence before intervention, repository
precedence, explicit invariants, preservation and bounded authority. This
supports withholding an unsupported execution claim; it supplies no independent
defect truth or CAPLAB execution authority.

The packet's 46 remaining generic obligations are nonmaterial to this narrowed
source-inspection disposition. Index workload/storage advice concerns database
index design, not the array-coordinate expression under inspection. The
failure-policy, exception and cleanup obligations do not support a new runtime
implementation or repair claim here. Async scheduling/race evidence, co-change,
generated-artifact and version-history metrics, architecture/ownership changes,
and quantified no-change cost analyses are outside this inspection. All exact
requirements and their scope classifications are retained in `verification.json`.
The historical executable reconstruction is still a material missing condition
for the stronger runtime claim, which this record explicitly withholds.

`verification.json` in the private custody directory consolidates source and
derived-file hashes, typed observation provenance, packet identities and
citation classification. All eight compressed source objects were checked
unchanged again at close. Extraction scripts, copied objects, capture receipts,
source inspection and both composition calculations are retained. Only the
eleven named advisory scratch files are removed after consolidation. The
initial extraction error and corrected extraction remain distinguishable.
No source-body or runtime mutation, evidence registration, tracker change,
model execution, or independent acceptance occurred.
