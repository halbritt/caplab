# A scheduler repair that is not a clean control

The fixed feasibility sample contains Striatum-next repair
`b9325d547fa8fc4f8df38ddef274ca9eae6a95f4`. An independent local witness
reproduces its schema-version repair and an input-provenance gap that the
successful record encoding does not catch. This adds a Go failure family to
reviewer development evidence. It prevents treating this sampled repair as
a verified clean control merely because the version selectors now agree.

## Observed behavior and meaning

The motivating scenario prefers a supervised remote backend. An active,
candidate-specific exhaustion observation excludes that backend, so placement
selects the eligible unsupervised local fallback. The same input without the
observation selects the remote backend. This is a substantive placement
effect, not a response-format or keyword check.

| Revision | Predicted envelope / evaluation | Original record encoder and decoder | Active observation in input preimage |
| --- | --- | --- | --- |
| Precursor `58ff7ce58e58` | v5 / v5 | Encoder refuses local binding's missing v5 fields | Present |
| Partial repair `147775a0047a` | v5 / v2 | Encoder refuses v2 preimage under v5 envelope | Absent |
| Sampled base `0a7aa730f164` | v5 / v2 | Same refusal | Absent |
| Sampled repair `b9325d547fa8` | v2 / v2 | Both accept the record | Absent |

The omission in the emitter already exists in the partial repair and sampled
base. The sampled repair changes the predictor so the incomplete v2 preimage
can pass the record boundary under its predicted envelope. This distinction
matters for change attribution: do not describe the omission itself as newly
introduced by this last patch. Likewise, the precursor already had an
unencodable local-placement path; the intermediate version mismatch is not
the first failure of the overall scenario.

In the repaired revision, removing the absent observation changes the
selected backend from `local` to `remote`. The observation therefore affected
placement but is missing from the claimed complete input preimage. The
witness demonstrates this counterfactual directly through the original
`Evaluate` function. It does not implement a general record-to-input replay,
run a live Driver, append to a production graph, or establish that the
surrounding ledger cannot reconstruct the missing observation.

This supports an actionable review concern at the record/placement boundary:
the schema correction must also preserve the inputs that explain fallback.
The complete live admission and recovery path still needs reproduction before
using this case for a broader operational-failure label or reviewer score.

## Independent expected behavior

The governing requirement predates these repairs. At precursor commit
`58ff7ce58e58b0cd5ea7719c5826fa3716bfbb68`,
`decisions/D0008-scheduler-and-capacity-policy.md` names deterministic placement
over content-addressed inputs in C1 and complete decision input/output
preimages in C11. That decision file's last change is
`1364e55a6a21db9536233159219c3d14aaa0d069`, dated 2026-07-11.

The original versioned record schema and separately implemented record
encoder/decoder supply the shape check. The author of this CAPLAB witness
inspected the repair diff and historical tests for interface shape; neither
the patch title nor its diagnostic tests supplies an empirical verdict. No
target test is imported or executed. The probe calls original production
packages with newly authored inputs and records all results before CAPLAB
assesses them.

Static consumer inspection further bounds the result. The Driver predicts
the envelope before its append callback, evaluates inside it and rejects
version disagreement. It supplies active observations separately from the
capacity snapshot. Its recognized-exhaustion records put candidate identity
inside a nested payload; the shared quota snapshot fold reads top-level
backend/pool fields. The v5 decision fold checks exact active observation
inputs; the v2 path does not run that check. This supports the relevance of
the missing field, but source inspection is not a live graph execution.
Commit/path/blob/SHA-256 locators for these observations are retained in
`source-inspection.json` and the committed receipt.

## Controls and execution

Each of four revisions was compiled once and executed twice, returning seven
frozen conditions per execution: 56 diagnostic observations in one family.
Both executions for each revision returned byte-identical observation output.
Repetitions and related revisions are not independent defects or case counts.

All valid conditions selected the independently expected backend or capacity
deferral. Ordinary local placement and expired observations produce valid v2
records throughout. Supervised failover and all-supervised exhaustion produce
valid v5 records that retain the exact active observation preimages. Malformed
observations are rejected. An unrelated active observation is also omitted
from the local v2 record, but removing it does not change that selection; the
checker does not inflate that case into the stronger causal finding.

The [first authorization](authorization-2026-09-10-reviewer-scheduler-witness.md)
and [dependency correction](authorization-2026-09-10-reviewer-scheduler-witness-2.md)
name the exact source and execution effects. The first preparation failed
all four module checks because its isolated mount omitted yaml.v3's pinned
transitive `check.v1` dependency. No scheduler compiled or ran in that attempt.
Its records remain unchanged.

The corrected attempt used the same witness and criteria. Go 1.23.4 verified
all three cached modules before each compilation; downloads and automatic
toolchain changes were disabled. Each build and executable ran in a separate
network namespace with read-only source/dependency mounts and an empty home.
The corrected build/execution campaign completed in 6.97 seconds. No provider,
credential, live ledger, service or timer was used.

The materialized source inventories contain 5,090 regular files across the
four revisions. Their membership and hashes were rechecked; no extra source
file or materialized symlink was present. Each original `CLAUDE.md` symlink
was preserved as metadata, as authorized. Toolchain, dependency, witness and
source hashes remained unchanged.

## Custody and limits

Private roots are
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/scheduler-witness-1`
and `scheduler-witness-2`. The
[development receipt](../product/studies/reviewer-ranking-001/scheduler-development-receipt.json)
pins source requirements, results and both preparations. Corrected plan
SHA-256: `5da0a78a262415eacdfd9cfb82cc7629f4d88b6b2491403a138f2bdbfd8eb50a`.
Verification SHA-256:
`fa0497396d21e47f6284d0a2284ad09fe1fd529ed1cb44d5e6151677162ccca0`.

Four new checker tests cover encoder/decoder failure, the conditions required
to establish an omitted causal input, expiry and malformed-input rejection.
All 35 focused reviewer-development checks pass. `make check` passes:
1,516 tests run in 205.63 seconds, with seven skips.

The sample's exact base, tree and changed blobs were rechecked. Two other
selected changes were inspected only: CAPLAB's transport/pair-validity repair
`c8f097a0934b` and ai-newsroom's publication-date repair `e4d529391061`.
Their behavioral reproduction remains open. No easier changes replaced them.

The evidence-backed doctrine packet `pkt-cdafd666a23adaf1` remains applicable
to separating reproduced behavior, requirement violation and unresolved
attribution. Its release-state gate passed again. Applied repository contract
precedence, evidence before intervention and measurement on the claimed
dimension. Live graph behavior, broad scorer validity and representative
ranking evidence remain material, unmet obligations; this record accepts
none of those outcomes.
