# Compare the refusal reconstruction with historical Go arithmetic

> **Correction:** The invalid-candidate-hash inference below is withdrawn.
> This check applied overlays to the compact anchored representation, while the
> historical driver and review contract use the expanded materialized tree and
> retain the compact hash only as the base pin. The corrected Go and Python
> calculations match both declared result hashes; strict application succeeds.
> See [the expanded-base verification](inspection-2026-09-08-production-review-403617-scope.md).
> The original observations remain below to preserve how this error arose.

## Authorization before execution

Under ADR 0026 and the continuing CAPLAB improvement request, the primary agent
authorizes one bounded comparison against Striatum's historical pure change-set
implementation. This follows the unresolved discrepancy recorded at `95e5005`;
it does not authorize running the reviewed dispatch code or adjudicating a
review verdict.

Copy exactly these four source files from `/home/halbritt/git/striatum-next`
commit `80db8bb3894b78ddc3ea41c40ae2a799c349f269` into a new private directory
under `/tmp/caplab-refusal-native-*`:

- `internal/changeset/changeset.go`
- `internal/workgraph/workgraph.go`
- `internal/scf/implementation.go`
- `internal/scf/value.go`

Record source Git blob IDs, paths, byte lengths and SHA-256 hashes. Retain exact
bytes, including the embedded SCF source. Add a local Go module declaration and
a small diagnostic command that calls the unchanged parsing, overlay, hash and
strict application functions. No historical source edits or other source copies.

Read the seven previously retained hash-verified input objects under
`/tmp/caplab-refusal-403588-rdioq9hr/`: observed product, four ancestor overlays,
and original/later candidates. Verify their content hashes against the prior
source receipts before execution. The reviewed application source is input data
to this arithmetic check, never an executed package. Allow newly rendered
canonical product bytes in private diagnostic custody; that exact derived
historical-evidence copying effect is authorized. No experimental admission,
correctness label, model call, ranking, tracker change or external message.

Use installed Go 1.23.4 from `/home/halbritt/.local/go`, with network disabled,
source/input/Go installation mounted read-only, isolated temporary/cache output,
explicit environment, and no host credential/home mount. The fixed command may
compile and execute the pure arithmetic checker once with a 60-second process
deadline and 256-KiB combined stream limit. No dependency fetch, unrelated tests,
services or candidate execution. Stop on missing source, input mismatch,
unexpected dependency, build failure, truncation or timeout. Retain failed
output rather than changing source or silently retrying.

Verify exit status, source preservation, canonical hashes, composed-base match,
and strict application results for both candidates. Compare the actual Go
results with the retained CAPLAB calculations. Do not fix a result hash to
make a candidate pass. This authorization expires at the comparison commit or
bounded failure; preserve unrelated workspace files and services.

## Result

The historical Go implementation agrees with CAPLAB on both candidate results.
Both candidates' declared bases match the composed base, but their declared
result hashes differ from the computed results. The historical `changeset.Apply`
rejects each candidate with one `apply_failure` for that mismatch.

| Candidate | Computed result, identical in Go and Python | Declared result |
| --- | --- | --- |
| Original403583 | `fb0334ceeae392315b2be45e167741a6f258df5a6739c4da0ba5af469757b786` | `3f42e27856fe40ec536517a0ba99dd1dd8c60e2b1c66dff991ccc9f945fcb546` |
| Later403612 | `658a4b5ffd8aa6fdf59676202a64197aa2356d766b1670a821549101027080ed` | `7204392c1424dfe7d4514fb7798baeac368a5b444207257f796e9f8d306269cd` |

Both computations use composed base
`54a9eb7e972708b2631daac63ac447d477770040f86f1d020c67e2e356d02c02`.
The canonical product bytes agree byte-for-byte, not merely by hash: 665,076
bytes for the original and 671,668 for the later candidate. None of the four
ancestor overlays or either candidate modifies any of the four historical
implementation files used by the checker. The observed product has no overlay
files of its own. The selected anchor implementation therefore remains the
implementation in those composed source trees for these packages.

This resolves the prior record's Go-versus-CAPLAB arithmetic uncertainty for
these exact inputs. Their declared result hashes are inconsistent with strict
application under the inspected historical implementation. This finding is
separate from review403588's recorded indexing concern: that review did not
identify this result-hash mismatch. A later admission is therefore insufficient
even to establish that this later candidate satisfies strict application.

The checker did not run the dispatch code, reconstruct the historical provider
environment, reproduce the indexing failure end to end, or determine whether
the live system tried to apply either candidate. It does not establish the
correctness of the refusal as a whole, the quality of a reviewer, or the validity
of other candidate fields. No result hash was repaired or substituted, and no
candidate is admitted as an executable benchmark instance by this record.

## Execution and verification

Private custody: `/tmp/caplab-refusal-native-_8e_p1bj/`. `sources.json` binds
each exact historical file by Git blob ID, SHA-256 and length. `source/` contains
those unchanged files, a local module declaration, and `cmd/check/main.go`.
The checker uses the real historical parser and arithmetic functions; no
substitute implementation or mocked package is used. The module only compiles
the copied packages and their standard-library dependencies, rather than the
reviewed application. It follows the previously selected comparison procedure;
no new engineering design or production behavior change is selected here.

`command.json` records the complete bubblewrap invocation and explicit
environment. The namespace disabled network access, mounted source, inputs and
the Go installation read-only, omitted host home/credentials, and confined
writes to temporary/cache/output paths. `capture/capture.json` records the
60-second deadline, 262,144-byte stream cap, and successful termination. The
command exited zero with complete streams: 1,236 stdout bytes and zero stderr
bytes, from `2026-09-09T01:12:12.766317+00:00` to
`2026-09-09T01:12:16.300348+00:00` (September 8 in the owner's timezone).

`capture/native.stdout` retains both strict application conflicts and computed
hashes. `output/original-canonical.json` and `output/later-canonical.json` retain
the rendered product bytes. `comparison.json` records the byte-for-byte Python
comparison, package non-modification checks, and installed Go executable hash
and observed version. The full Go installation is not independently content
pinned by that executable hash; it is a compiler observation for this run.

All seven input content hashes were rechecked and the four copied historical
sources remained unchanged. The stream lengths and hashes were checked against
the capture receipt. `verification.json` inventories source, checker, command,
capture, comparison and canonical-output bytes. Build cache files remain
private local execution byproducts, not evidence of a valid benchmark case.
No task-owned or historical custody was deleted.

The full CAPLAB suite was not rerun because no runtime code changed. The relevant
verification is the completed historical Go comparison and exact-byte agreement.
This is additional inspection evidence for the report-only production canary;
the gold-outcome threshold and placement remain unchanged. A correct-review
label still requires its own independent outcome basis and authorized
adjudication. The wider measurement goal remains active.
