# Test the historical context-reference finding against native ledger semantics

Date: 2026-09-08. Baseline: `434f674`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before inspection

Follow up only finding RV-003 in production review403588, as identified by
[the refusal inspection](inspection-2026-09-08-production-refusal-403588.md).
Its conditional array-index observation has not executed the native function.
The subsequent [expanded-base correction](inspection-2026-09-08-production-review-403617-scope.md)
verified candidate identities; the withdrawn result-hash claim is not a defect.

Authorize read-only inspection of provenance metadata and exact canonical
candidate outputs in `/tmp/caplab-review-403617-1ohklahf/`, and the original
review body and candidate bodies in `/tmp/caplab-refusal-403588-rdioq9hr/`.
Require candidate canonical hashes
`3f42e27856fe40ec536517a0ba99dd1dd8c60e2b1c66dff991ccc9f945fcb546` (403583) and
`7204392c1424dfe7d4514fb7798baeac368a5b444207257f796e9f8d306269cd` (403612),
and review hash `1acb1fa16516bae47073312d9270657084de5fe3064bef9e9d9388ddb2dd9bed`.
Inspect ledger and scheduler source contained in these fixed trees to identify
real inputs, dependencies, side effects and an isolated executable witness.
No historical source mutation or candidate substitution. Limit each canonical
input to 32 MiB; refuse missing, symlinked, nonregular or changed inputs.

Before any historical code execution or materialization, add an amendment
naming exact source paths, permitted copies, command, isolation and bounds.
Initial authority permits source inspection and private metadata/scripts under
`/tmp/caplab-context-reference-*`, and this record only. No code changes to
CAPLAB or Striatum, production execution, native/model calls, evidence admission,
correctness labels, scores, ranking, replay, tracker writes or external messages.
Preserve source custody, `docs/designs/`, sibling worktrees, services and timers.
Verify source hashes before and after work. Consolidate advisory evidence before
removing only named scratch. Commit this record locally; authority expires at
commit or a bounded failure requiring broader effects.

## Claim ceiling

A newly authored native runtime witness can establish behavior under named
inputs. It cannot establish that production took that path, adjudicate the
whole review, generalize across reviewers or unpark criterion replay. Keep the
original and later candidate identities distinct; a subsequent edit is not the
truth oracle. Use the actual ledger implementation to check sequence semantics.

## Execution amendment: test the prerequisite before the lookup

Source inspection shows `ensureSchedulingDecisionContext` calls
`Graph.AppendRecordIf` for `scheduling_decision_context` v1 with writer `driver`.
That method checks the compiled runtime registry before its admission callback.
The context type was not found in the original compiled registry. This is the
prerequisite named by RV-001 in the same already identified review, not a new
case selected from outcomes. Extend the question to whether native append
reaches its callback and creates the record required by RV-003. Do not bypass
registration, replace registry state or inject fabricated ledger records to
force the later lookup. If append refuses, record that first boundary and leave
the RV-003 runtime claim unresolved.

Authorize materializing unchanged `go.mod`, `go.sum`, and non-test `.go` files
under `internal/` from each of the two fixed canonical trees into separate new
private `/tmp/caplab-context-reference-*` source roots. Preserve source-tree and
per-file hashes; no repository checkout or historical test mutation. Add one
newly authored Go test in `internal/store/` to each copy. It must initialize a
fresh native Graph Store, verify actual snapshot sequence numbering, validate a
new synthetic context payload with the native schema validator, call the real
`AppendRecordIf` with native type/version/writer, and observe callback invocation,
error and before/after ledger records. This is a newly authored diagnostic,
not a historical production input or a claim to run the whole candidate.

For each candidate, run only `go test -mod=readonly -count=1 -run
^TestCAPLABContextAppendBoundary$ -v ./internal/store` under a separate Bubblewrap
namespace with no network, clear environment, no credentials or production
store mounts, read-only source and toolchain, and only the two exact cached
module versions declared in go.mod (compress v1.17.11 and yaml.v3 v3.0.1).
Use fresh private output/cache roots, private tmpfs, CGO disabled, local toolchain,
GOPROXY/GOSUMDB off, at most two Go worker processes, 120 seconds and 256 KiB per
stream. Retain command/environment and bounded process receipts. A failed build
is a failed probe, not evidence of the context behavior. Stop on missing module,
namespace failure, changed source hash or an unexpected fixture failure.

Retain source copies, exact witness, provenance, stream outputs and receipts.
No native dispatch, model launch, production mutation, source repair, independent
review adjudication or experimental admission is authorized by this amendment.

## Observed native prerequisite result

Both fixed canonical trees passed their required hash checks. Each diagnostic
source root contains 173 unchanged files selected by the amendment, plus the
same newly authored test. The test uses the real Graph Store, SCF encoder,
context-schema validator, runtime registry and append method. It neither mocks
these boundaries nor imports the historical tests.

Both isolated commands exited zero with complete streams, 583 stdout bytes and
empty stderr. The tests completed in 0.003 seconds each; their enclosing build
and capture processes took approximately 6.54 and 6.57 seconds. A passing
witness means the observation completed, not that the candidate is correct.

For both original403583 and later403612:

- A newly initialized native ledger contained one `graph_genesis` record at
  sequence zero. This directly verifies native initial numbering rather than
  adopting the older one-based test fixture.
- The new synthetic context payload passed the native v1 schema validator.
  Its request/environment/policy pins are placeholders, not admitted artifacts
  or a production run. This is sufficient to isolate the earlier registry
  check, not to prove a valid full scheduling context.
- `AppendRecordIf` returned
  `records: park schema_newer_than_reader for scheduling_decision_context: reader v0, record v1`.
- Its admission callback was not called. The native snapshot still contained
  one record. No context record was appended and no context lookup ran.

The error exactly matches the registry error quoted by RV-001 in the
hash-identified review body. This verifies that particular append-boundary
claim under the named native implementation and synthetic input. It does not
verify the review's claimed end-to-end test result, all-live-runs impact,
permanence, other record variants, other findings or overall verdict.

## Source distinction and inference limits

The later source contains `liveSchedulingRecordsSupported`, which checks both
context v1 and scheduling-decision v6 writability. Its
`ensureSchedulingDecisionContext` returns `(0, nil)` before snapshot/fold/append
when those checks fail. The original function lacks that guard. These are
source observations; this inspection did not execute the guard or a dispatch
recovery session. Identical direct-append errors therefore do not show that the
later dispatch still takes the failing path or that review403617 missed it.

The actual runtime prerequisite refuses before the proposed RV-003 lookup
witness can be assembled through native admission. Do not bypass the registry
to present a fabricated normal execution. The conditional `contextRef-1`
observation remains unresolved as a full runtime finding. This inspection
changes the next action: any broader reproduction must model the original
activation and the later guard separately, with a real admitted run and frozen
policy context. It must also preserve the already corrected expanded-base
identity rather than reintroduce the withdrawn hash claim.

## Custody and verification

Private custody is `/tmp/caplab-context-reference-probe-0akyzavs/`.
`sources.json` maps both canonical inputs to every unchanged materialized
file. Each candidate directory contains `source/`, `command.json`, output/cache
and `capture/` with exact streams and process receipt. Both stdout digests are
`28c030ae7f148f243734b14bdece1f940c018d8019db2dc664f9d0cb3e359dd3`.
The newly authored witness is `/tmp/caplab-context-reference-witness_test.go`;
preparation and execution scripts are `/tmp/caplab-context-reference-prepare.py`
and `/tmp/caplab-context-reference-run.py`.

Both historical canonical hashes and the retained review-body hash are checked
again at closure. All copied historical source files must still match their
manifest entries, and both witness copies must match the retained witness.
Capture stream lengths and hashes, CLI return codes and local record links are
checked. No full CAPLAB suite is rerun for this record-only repository change.
No historical evidence is registered, labeled gold, scored or admitted to a
replay. The review-validation floor and broader roadmap remain incomplete.

## Delegated disposition and advisory closure

Retain this boundary observation and defer the context-reference execution
claim. No CAPLAB or Striatum runtime change is selected. Ignoring the preceding
native refusal would omit relevant evidence; bypassing it would change the
historical subject. A larger dispatch fixture requires separately named run,
policy and activation evidence and an expanded execution authorization.

The Pincite retrieval gate passed against release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-ec00f13a9b675691` narrows the question to the observed prerequisite and the
unresolved lookup. Four typed records supply authority, unchanged source,
native witness and runtime observations. Four consumed citations classify as
valid: repository-contract precedence, evidence before intervention, explicit
invariants and authority-bounded action.

`/tmp/caplab-context-reference-verification.json` consolidates packet identity,
content hash, corpus/doctrine/retriever versions, source locators, evidence and
citation classifications. Thirty remaining generic obligations are retained
individually as nonmaterial with rationales for this bounded observation; they
do not support a repair, a full-dispatch causal claim, wider conformance,
architecture assessment or reviewer correctness judgment. Ten named advisory
scratch files are consolidated before removal. Diagnostic custody and scripts
remain. The initial source display ran beyond the end of a file and raised
`IndexError`; that display error executed no historical code and supplied no
runtime result. The later bounded native probes completed normally.

Local integration consumes the authorization. This is verified inspection
progress, not independent acceptance, a new gold incident or goal completion.
