# Inspect review403617's assigned scope and retained response

## Authorization before source inspection

Under ADR 0026 and the continuing CAPLAB improvement request, the primary agent
authorizes bounded report-only inspection of review run403617, which cleared
candidate403612. The fixed canary report at
`/tmp/caplab-production-followup-tyk04scp/report/report.json`, SHA-256
`f39441c9c42264abc8566e9e068c7480e5cb6dfd23cced8e9ae96c3e06498f19`, supplies the
selection and exact locators. This is follow-up to the strict-application
conflict verified at `da412bc`, not a representative reviewer sample.

From object store
`/home/halbritt/.local/share/striatum/graphs/019f22ef-0cb4-780f-9b82-b210bab24325`,
read and copy only these four exact historical objects to new private
`/tmp/caplab-review-403617-*` custody:

- Review body: `ebacbf869ec84bf90c30e3257e8e5dca0b1f64f532b585ddfe65c9046a0ca00a`.
- Recorded review contract: `649545a930c199f16c441194f4851fed27f504c682740a17884eec54e3560f1d`.
- Retained launched prompt: `6a616fdcde5b3997bb8224a5c96605224b7b55ed4fe7f32494ed0235f740097a`.
- Runtime diagnostic: `60c7ad6a1a08edc9c47563129c2d6a9716710e46af963c493d1f9119be7c7c99`.

Reuse the bounded extraction procedure from the earlier refusal inspection.
Require no-follow regular-file sources, at most one MiB compressed and five
MiB decompressed per object, a five-second decoder deadline, successful decoder
exit and content-hash agreement. Preserve missing inputs as unavailable and
do not substitute other objects. Stop on ambiguous/corrupt input or a bound
failure. Retain exact source paths, compressed/content hashes, command receipts
and source preservation checks. This explicitly authorizes these historical
copying effects and no historical source mutation or evidence admission.

Inspect instructions concerning review scope, artifact/hash checks and assumed
prior verification; compare them with the retained review and diagnostic. The
repository record may retain bounded observations and locators but not full
historical prompts, artifact bodies, or credentials. No candidate execution,
model call, correctness label, scoring, ranking, tracker change, or external
message. Read the prior native-hash verification and its comparison receipt
as supporting provenance without modifying them. Authorization expires at this
inspection's commit or bounded failure. Preserve unrelated workspace state.

### Expanded-base verification and correction authorization

The hash-verified launched prompt explicitly distinguishes the anchored base
pin `54a9eb7e972708b2631daac63ac447d477770040f86f1d020c67e2e356d02c02` from
expanded materialized base
`489e0195467def35acacce33914612d6c756d547a256984ba6eea268fa99150d` and records
`base_mode: anchored-expanded`. The previous arithmetic check used the anchored
representation as the overlay input. Its failure cannot establish invalidity
under the actual expanded-base workflow.

Authorize copying that one exact expanded-base object from the same store,
with eight-MiB compressed, 64-MiB decompressed and ten-second decoder limits.
Verify its hash and the existing canary's base link for both reviewed versions.
Use the existing CAPLAB arithmetic and unchanged four historical Go source files
from commit `80db8bb3894b78ddc3ea41c40ae2a799c349f269` to compare both overlays
on this expanded base, while keeping the original anchored hash as the pin
passed to strict application. Read the historical driver's expansion call site
at that commit to verify this distinction. Preserve earlier checker outputs.

One new private diagnostic command may compile and run those pure arithmetic
packages with the same no-network/read-only-input isolation, 60-second deadline
and 256-KiB stream cap as the previous check. It executes no reviewed dispatch
code. Retain exact command/source/output provenance. This authorizes the new
source copies and derived canonical outputs, not a modified candidate or hash.

Authorize adding explicit correction notices to
`inspection-2026-09-08-production-refusal-403588.md` and
`verification-2026-09-08-refusal-403588-native-hashes.md`, preserving their prior
text and raw evidence. The notices must withdraw any inference of invalid
candidate hashes unsupported by the expanded-base calculation. No correctness
label or experimental admission follows from a successful hash check.

## Corrected result: both declared hashes match

The previous invalid-result-hash conclusion was wrong. It compared the result
of an overlay on a compact anchored product with a hash naming an expanded
materialized result. Go and Python agreed because both were given the same
wrong representation for this comparison. That agreement did not validate
the comparison's premise.

The retained launched prompt names:

- `base_mode: anchored-expanded`.
- Base pin `54a9eb7e972708b2631daac63ac447d477770040f86f1d020c67e2e356d02c02`,
  represented as an anchored product body at `inputs/00-base-pin`.
- Materialized overlay base
  `489e0195467def35acacce33914612d6c756d547a256984ba6eea268fa99150d`,
  staged at `inputs/01-base`.
- An explicit instruction that unequal hashes are expected for those different
  representations, and that the compact product must not be the application tree.

The exact historical driver source in `internal/driver/workgraph.go` expands
an anchored product before calling `changeset.Apply(applied, baseHash, cs)`;
`baseHash` remains the compact anchored pin. `Apply` does not itself perform
that expansion. The earlier diagnostic copied the pure arithmetic packages
but omitted this behavior of their caller.

The expanded object was recovered and verified: 20,218,259 bytes, matching
the materialized-base hash. Both canary rows, runs403588 and403617, name this
same materialized base. Applying the original and later overlays to it yields:

| Candidate | Computed and declared result | Canonical bytes | Historical strict application |
| --- | --- | ---: | --- |
| Original403583 | `3f42e27856fe40ec536517a0ba99dd1dd8c60e2b1c66dff991ccc9f945fcb546` | 20,265,256 | No conflicts |
| Later403612 | `7204392c1424dfe7d4514fb7798baeac368a5b444207257f796e9f8d306269cd` | 20,271,848 | No conflicts |

Python and the unchanged historical Go arithmetic produce identical canonical
bytes. The Go comparison exited zero with complete streams, 1,122 stdout bytes
and no stderr, within the same isolated 60-second/256-KiB bounds. Neither
candidate body nor declared hash was modified. This verifies the hash relation
against the retained materialized base; it does not independently re-expand
every Git source file, establish candidate runtime correctness or accept a review.

Prominent correction notices were added to both earlier records under the
explicit authorization above. Their original text and raw diagnostic custody
remain unchanged beneath those notices. The earlier result-hash mismatch must
not be harvested as a production defect or a reviewer miss.

## Review scope and response observations

The review contract was recovered as 3,272 UTF-8 bytes. It permits a non-clearing
verdict only for a predicate-blocking defect, violated in-force decision or
demonstrated harm on the changed surface, with an anchored rationale. Other
findings require `accept_with_findings`. The 69,091-byte launched prompt asks
the reviewer to independently inspect the candidate overlay against the
materialized base and says a false derivation/match is a candidate defect.
For this candidate the supplied mechanical context reports a successful result
derivation and match; the corrected comparison here independently agrees.

The retained 1,234-byte review accepts candidate403612 with no findings or
dissent. Its summary claims the implementation satisfies stage requirements and
preserves the shadow-only activation boundary. Those remain reviewer judgments,
not conclusions adopted by this inspection.

The 5,430-byte runtime diagnostic records `SUCCESS`, duration 962.327814227
seconds and `num_turns: 1`. Its response text repeatedly says tests were started
and that it is waiting, then supplies the accepting review. The retained object
does not supply the underlying test command result or exit status, so this
inspection does not treat that prose or success status as proof tests passed.
It also does not infer that tests failed or never ran. The counter field does
not independently count the model's native tool turns.

All five newly read source objects were hash-verified and preserved. Custody
is `/tmp/caplab-review-403617-1ohklahf/`: decoder inputs, bounded receipts and
source hashes; `expanded-python-comparison.json`; and `go/` with the unchanged
historical source copies, diagnostic command, isolated execution receipt and
canonical outputs. Final `verification.json` retains exact provenance and
the correction checks. No full CAPLAB suite ran because no runtime source
changed. This source inspection provides no new correctness label, gold outcome,
placement decision, or native dispatch reproduction. The broader goal remains
active.
