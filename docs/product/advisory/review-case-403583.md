# Case 403583: a refused change set with a reproduced dispatch failure

**Status: inspection evidence; this brief records no correctness ruling.** This brief
helps an authorized adjudicator assess one finding in review run403588. It is
not a blinded assessment packet, a formal Striatum adjudication-preparation
dossier, or an admitted criterion case.

The task was to review the `driver-live-binding` change set for
`capability-aware-placement-e`. The original candidate attempted to connect
scheduling evidence to the driver. Review403588 returned `needs_revision`;
finding RV-001 said that creating a scheduling-context record would fail
because its type was missing from the runtime registry.

**What is now verified:** the unchanged historical integration test fails on
the original candidate's first `drive` call with that exact registry error.
The same test passes on the later candidate. Both source versions and all
fixture inputs were checked by hash. This is a reproducible finding-level
observation, not a correctness label for either whole candidate.

## The decision still needed

Does this demonstrated failure qualify as a blocking defect on the original
reviewed surface under its assigned contract? The contract permits refusal
for a violated accepted predicate/decision or demonstrated harm on the changed
surface. Findings outside that boundary belong under `accept_with_findings`.
The ruling must identify which condition applies and why; this brief leaves
that judgment unassigned.

The original review's own retained prompt has been recovered and hash-verified.
It names version403583, adversarial posture v1, and contract v2. It asks for
independent inspection of the candidate against the expanded materialized base
and the exact origin Work Graph. Its instructions are not inferred from the
later review. See the [context extraction record](../../records/preparation-2026-09-08-production-review-case.md).

## Evidence to inspect

| Evidence | What it supports | Limit |
| --- | --- | --- |
| [Native integration comparison](../../records/inspection-2026-09-08-historical-dispatch-spine.md) | Original fixture fails with CLI exit 3 and the named context-registry error; the later fixture passes. | One deterministic local scenario under Go 1.23.4; no production input replay or model execution. |
| [Native append probe](../../records/inspection-2026-09-08-context-reference-runtime.md) | The compiled registry refuses context v1 before its admission callback and leaves the ledger unchanged. | Direct append is not the later candidate's guarded caller path. |
| [Expanded-base correction](../../records/inspection-2026-09-08-production-review-403617-scope.md) | Both candidates' declared result hashes match the correctly expanded base. | Earlier claims of invalid result hashes were withdrawn and must not count as defects. |
| [Original finding inspection](../../records/inspection-2026-09-08-production-refusal-403588.md) | Locates RV-001 and the other recorded findings in the original review. | Its old hash inference is corrected above. RV-003's context lookup remains unexecuted. |

The later source adds a guard for unsupported record types and changes other
driver behavior. A passing revision does not isolate that guard as the unique
cause, establish a gold-clear case, or adjudicate the later accepting review.
The test asserts fixture gates, staleness, revalidation, five satisfied requests,
and agreement of specified semantic projections across two clocks. It does not
cover every live scheduling path or every review finding.

## Exact subjects and private custody

Review subject identity:
`striatum-next/passes/capability-aware-placement-e/packets/driver-live-binding/change-set`.

| Pin | SHA-256 |
| --- | --- |
| Original change-set version403583 | `73f1d90d74e7f227a86c6891dd8127d8343dc32649ffa5ab21f8fbf1eb53970d` |
| Original expanded result | `3f42e27856fe40ec536517a0ba99dd1dd8c60e2b1c66dff991ccc9f945fcb546` |
| Later change-set version403612 | `579a65bf2ad7656c6c08d21b8f11d46a6ef137f84c4d638d0c9a60d7ff469ea3` |
| Later expanded result | `7204392c1424dfe7d4514fb7798baeac368a5b444207257f796e9f8d306269cd` |
| Original review body | `1acb1fa16516bae47073312d9270657084de5fe3064bef9e9d9388ddb2dd9bed` |
| Original launched prompt | `1a51075027b4c3680dc4a31464f5cca2eb0a1330e23178da11e3068a7632440d` |
| Review contract | `649545a930c199f16c441194f4851fed27f504c682740a17884eec54e3560f1d` |

On the inspection host, full original prompt and contract are under
`/tmp/caplab-review-case-context-dnr6p_oo/`; native test source, commands and
receipts are under `/tmp/caplab-dispatch-spine-probe-ybahiehe/`. The linked
records identify remaining source custody. These private temporary locations
must be available and hash-checked before relying on the underlying evidence;
this brief is not a self-contained portable evidence bundle.

## Population and unresolved requirements

This case was selected as the sole refusal among 42 reviews in a fixed ledger
window. That selection supports investigation, not an accuracy or prevalence
estimate. The ledger's backend label has not been established as an exact
CAPLAB Binding. Later revision, acceptance, cancellation or application is not
independent truth about this review.

No ruling, adjudicator identity, delegation scope or gold-outcome ledger event
has been recorded for this case by this work. Any future adjudication must name
the exact subject, reviewed contract, evidence and limits, distinguish the
finding from the whole verdict, and retain unresolved findings. The
[confirmed review disposition](../../records/report-2026-09-07-review-instrument-disposition.md)
still parks criterion replay until the required independent incident-level
outcomes exist. Preparing this brief does not advance those counts.
