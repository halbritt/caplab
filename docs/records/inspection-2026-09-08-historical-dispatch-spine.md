# Inspect historical dispatch integration after the registry finding

Date: 2026-09-08. Baseline: `e1a487d`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before source inspection

Follow [the native prerequisite inspection](inspection-2026-09-08-context-reference-runtime.md).
Read the same two exact canonical candidate objects in
`/tmp/caplab-review-403617-1ohklahf/go/output/`: original403583,
SHA-256 `3f42e27856fe40ec536517a0ba99dd1dd8c60e2b1c66dff991ccc9f945fcb546`,
and later403612,
SHA-256 `7204392c1424dfe7d4514fb7798baeac368a5b444207257f796e9f8d306269cd`.
Read the prior candidate-source manifest and hash-identified copies in
`/tmp/caplab-context-reference-probe-0akyzavs/` as supporting locators.

Inspect the unchanged driver activation path, the existing historical
`TestV0SpineFixtureEndToEnd` test named in RV-001, and its fixture/dependency
requirements. At most 32 MiB per canonical object, no-follow regular files,
exact hashes required. Initial authority permits read-only source inspection,
private metadata/scripts under `/tmp/caplab-dispatch-spine-*`, and this record.
Do not materialize additional historical content or execute it until an
amendment names the sources, exact command, isolation, bounds and stop conditions.

No source mutation, candidate substitution, model/provider call, production
store access, native agent invocation, evidence admission, gold label, reviewer
score, tracker change, external message, push or service/timer change. Preserve
historical custody, untracked `docs/designs/`, and sibling worktrees. Verify
historical source hashes before and after. Consolidate advisory evidence before
removing only named scratch. Commit locally; authority expires at commit or a
bounded failure requiring broader effects.

## Question and ceiling

Can the unchanged historical integration test distinguish the original
candidate's dispatch failure from the later candidate's guarded behavior?
Read the actual test and fixture before interpreting what it covers. A passing
fixture would establish only its own named scenario, not production recovery,
all review findings, independent adjudication, acceptance or qualification.

## Execution amendment

The existing test registers a deterministic `fixture-transform` implementation
with the native local backend and creates fresh repository and data roots with
`t.TempDir`. Its fixture backend directory declares only local tools. Its
`TestMain` disables wake timers and harvesting; the package initializer creates
only a temporary wake-stamp directory. The test's acceptance action belongs to
its fictional fixture Principal and is not a CAPLAB or production judgment.

Authorize materializing every text file in each exact canonical candidate
object into separate fresh private `/tmp/caplab-dispatch-spine-*` roots. This
permits complete historical content copies solely for the named integration
fixture, retaining canonical and per-file hashes; reject unsafe paths and
non-string entries. Preserve all file bytes, including test, catalog, policy,
decision and fixture dependencies. The product format supplies content, not
original filesystem modes; restore ordinary files, not executable scripts.
No historical source or test edits are authorized.

Run only `go test -p=2 -mod=readonly -count=1 -run
^TestV0SpineFixtureEndToEnd$ -v ./internal/cli` for each candidate. Use a fresh
Bubblewrap namespace, no network, clear environment, read-only source/toolchain,
private tmpfs and output/cache, CGO disabled, local toolchain, GOPROXY/GOSUMDB
off, and the same exact cached compress v1.17.11 and yaml.v3 v3.0.1 modules.
Disable wake timers and harvesting explicitly as well as through TestMain.
Mount no credentials, production store, native model binaries or live repo.
Allow 180 seconds per command, 256 KiB per stream and at most two Go workers.
Retain exact commands/environment, stream bytes and process receipts.

A test assertion failure is an observed outcome, not grounds to patch the test;
run the other fixed candidate for comparison. Stop on missing dependencies,
compile errors, namespace failure, unexpected outside-fixture effects or bounds.
Do not retry a terminal command without a new scoped amendment. The two
candidates have multiple source changes, so a before/after difference alone
cannot identify the guard as the unique causal change.

## Native integration results

Both complete canonical candidates were hash-verified and materialized as
1,560 unchanged files each. The two source trees differ in five files: runtime
`scheduler_telemetry.go` and `scheduling_preview.go`, plus three driver test
files. The selected CLI test, its TestMain, catalogs, fixture data and policies
are byte-identical. In particular, `internal/cli/spine_e2e_test.go` has SHA-256
`764397eebaaeba93a912ed63b3bb3259de09dd16aa40e511a0f24c2a65e34a16` in both.

| Candidate | Native command outcome | Observed fixture result |
| --- | --- | --- |
| Original403583 | Exit 1; complete streams; 341 stdout bytes; empty stderr | First fixture run stops at its first `drive`: CLI exit 3 instead of 0, reporting `driver: dispatch recovery parked: records: park schema_newer_than_reader for scheduling_decision_context: reader v0, record v1`. |
| Later403612 | Exit 0; complete streams; 146 stdout bytes; empty stderr | `TestV0SpineFixtureEndToEnd` passes unchanged. |

The original test reports 0.080 seconds; its enclosing isolated build/capture
lasted about 10.63 seconds. The later test completes both differently clocked
fixture runs; the enclosing command lasted about 11.10 seconds. No timeout,
stream truncation, compile failure or retry occurred.

For the passing candidate, the unchanged test compares semantic projections
from both runs after explicitly removing specified timing/runtime-occurrence
fields. It checks passing check and fixture-acceptance gates, a nonempty
staleness wave, supersede and re-stamp head movements, admitted observation and
review-ledger artifacts, and five requests with five satisfactions. It deletes
and rebuilds each fixture's derived state before reading its ledger. These
assertions exercise a real local dispatch/admission/recovery path. The local
transform is deterministic fixture code; no model-generated work is involved.

## Inference and delegated disposition

RV-001's named integration failure is now reproduced on the exact original
source content under the recorded local toolchain and fixture environment.
The same unchanged test passes on the exact later candidate. This extends the
previous direct-append probe to the driver/CLI path actually named by the
review. It is stronger than inferring correctness from a revision link or a
reported successful wrapper exit.

The later candidate includes the record-support guard inspected previously,
but also changes other driver behavior. This paired comparison does not isolate
that guard as the unique cause. It does not test every dispatch mode, prove
production's historical inputs matched the fixture, establish all-live-runs
impact, validate every finding or independently adjudicate either review.
In particular, it does not exercise RV-003's lookup after registration succeeds.
A passing fixture is not a gold-clear label for a whole candidate.

Retain this as reproducible, version-specific integration evidence. Do not
repair or replace either candidate, change the test to make it pass, admit it
as criterion truth, score a reviewer, or unpark replay. Keeping only the prior
append result would leave the caller behavior untested; rewriting the registry
would alter the historical subject. Further causal attribution would require a
separately named counterfactual, and any gold judgment requires independent
adjudication under the governing review-validation contract.

## Custody and verification

Private custody is `/tmp/caplab-dispatch-spine-probe-ybahiehe/`, with complete
source copies and per-file provenance in `sources.json`, exact commands in each
candidate directory, and bounded stream/process receipts under `capture/`.
The original stdout SHA-256 is
`d0ff54d392e82d7a48cd17a02517ca99f58a3bfebe83b6d2e15e386fa6990f82`;
the later stdout SHA-256 is
`05857a06659f02c288aa75059182a6d0e89e61f5631b1fea5f6fe524352f7b08`.
Preparation and execution scripts are `/tmp/caplab-dispatch-spine-prepare.py`
and `/tmp/caplab-dispatch-spine-run.py`. The fixture cleans its own temporary
stores; source copies, build cache and captured output remain. No raw fixture
ledger is claimed as retained after that cleanup.

Closure verifies both original canonical hashes, all 3,120 copied files,
stream lengths and hashes, exact test outcomes, identical fixture inputs and
record links. Current toolchain metadata is retained separately from historical
source identity. CAPLAB runtime/tests are unchanged, so its full suite is not
rerun. The broader roadmap and independent reviewer-validation requirements
remain incomplete.

## Advisory closure and local integration

Pincite's retrieval-state gate passed against release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-942237462ce5befe` incorporates four typed observations covering authority,
source distinctions, the unchanged test and captured runtime outcomes. Four
consumed citations classified as valid: bounded authority, repository-contract
precedence, evidence before intervention and explicit invariants.

`/tmp/caplab-dispatch-spine-verification.json` retains the packet content hash,
corpus/doctrine/retriever versions, locators, typed evidence and citation
classification. Twenty-eight remaining generic obligations are individually
classified as nonmaterial with rationales for this bounded comparison. They
cannot support a unique-cause claim, broad regression coverage, architecture
judgment, representative workload inference or independent review adjudication.
Ten named advisory scratch files are consolidated there before removal; exact
source, command, output, authorization and verification artifacts remain.

The existing test was inspected for real boundary coverage and its limitations;
no duplicate CAPLAB regression test or modified historical oracle was added.
Local integration records verified evidence and consumes the bounded
authorization. It does not accept the candidate or complete the broader goal.
