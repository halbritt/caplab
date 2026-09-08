# CAPLAB-86: superseded absent-base review repair

## Decision and authorization

On 2026-09-08 the primary agent, exercising the planning and decision
delegation in ADR 0026 under the active CAPLAB improvement goal, selects
**superseded** for CAPLAB-86. The item proposed materializing the base blob
to prevent the v1 change-set contract from inducing host-wide store searches.
The Principal-accepted August correction replaced that contract; the
September tree environment subsequently supplied available bases and made
unavailable bases explicit. Reimplementing the original proposal would
duplicate or contradict those accepted changes.

This is a planning disposition based on current source and local technical
verification. It is not independent acceptance of the implementation, a
reviewer qualification, or a decision to run a study.

Authorized effects: add this record; set only CAPLAB-86's Plane state to
Cancelled (the existing terminal state for a superseded item); append a
supersession note pointing here while preserving the original description.
Re-read the issue before mutation and stop on a conflicting concurrent edit.
Verify the state and complete description after the update. No comments or
messages to other people, other tracker changes, runtime changes, model
calls, sweeps, historical evidence admission or rewriting, ranking, or
placement are authorized. The no-spend and placement-frozen disposition of
2026-09-07 remains in force. Reopen this item with a contrary current-state
finding; a reversal appends a new disposition rather than erasing this one.

## Requirement reconciliation

The source under review is CAPLAB commit `09230fa`. The live Plane snapshot
is `/tmp/caplab-roadmap-20260908-evaluation-followup.json`; CAPLAB-86 was
Backlog. The original title and problem remain preserved in Plane.

| Requirement or failure | Current evidence | Disposition |
| --- | --- | --- |
| A reviewer must not be required to retrieve a base that was never supplied. | `calibrate.profile_for_artifact` routes change sets to `v2-changeset` outside tree mode and `v3-changeset` inside it. v2 scopes absent-base verification out and forbids store searches. | Original v1 routing is superseded. |
| Supply the base when the review contract requires it. | `pool_runner.measure_case` materializes a registry-selected base into the case workspace before invocation, renders its location and extent in preamble v3, and verifies its manifest before and after attempts. | Implemented for the tree runner's available registered bases. |
| Do not invent a base or score an uncheckable planted defect. | `materialize.BASE_SOURCES` distinguishes whole, partial, none-by-design, and lost bases. Base-dependent operators with lost bases return `unscorable_missing_base` before invocation; missing registry records also refuse. | Missingness remains explicit; universal base recoverability is not claimed. |
| A diligent reviewer must not need or be able to grep the host's store. | The tree prompt points at the supplied workspace. `pool_runner.sandbox_prefix` masks home and binds only the case workspace and declared harness resources. The local Stage B probe confirms the store and checkouts are invisible. | Current contained runner addresses the original host-search mechanism. |
| Old contaminated observations must not silently become new clean evidence. | `QUARANTINED_PROFILES` retains `v1-changeset`; discrimination tests refuse its promotion despite apparent repeated success. | Historical rows and the retired prompt remain interpretable; none were rescored here. |

The governing sequence is the Principal-accepted
[August erratum](erratum-2026-08-22-changeset-contract-quarantine.md),
the [tree environment plan, revision 2](../product/plans/plan-tree-v1-review-environment.md),
the [Stage B probe report](probe-2026-09-06-tree-v1-stage-b.md), and the
[September review disposition](report-2026-09-07-review-instrument-disposition.md).
These earlier records were read as evidence and were not modified. Their
historical model-probe results are not presented as fresh measurements.

## Verification and limits

Current verification ran:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3 -m unittest \
  test_advisory_materialize test_advisory_tree_v1 \
  test_advisory_pool_runner test_advisory_calibrate \
  test_advisory_discrimination -v
```

All 116 tests passed in 5.510 seconds with no skips; log:
`/tmp/caplab-86-verification.log`. Assertions were inspected, including the
real local `StageBContainmentTest.test_lane_sees_a_synthetic_home_and_writes_do_not_reach_it`
probe and the materialization, missing-base, routing, and quarantine tests.
Other runner tests use local echo adapters; they do not establish native
model behavior. The suite also read one existing stored product to verify its
hash; it did not register, alter, score, or copy historical campaign evidence.
No source or test implementation changed in this disposition.

This closure does not declare the entire advisory calibration surface ready.
`calibrate.local_review` and `adapter_review` remain legacy direct transports;
they do not provision the tree runner's materialized workspace. The retired
v1 prompt remains addressable as a Python constant for historical
interpretation. Future execution through these entry points requires its own
containment and contract disposition. The current no-spend restriction is
unchanged. No claim is made that every repository base can be recovered,
that host OOM is impossible from all causes, or that the benchmark has
independent production gold or discriminating reviewer rankings.

## Advisory doctrine

Validated release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8` supplied packet
`pkt-5b515e5978521fec`, content SHA-256
`5b515e5978521fec1e5ad0efd6aef9e724a15512522734db899e384423c595b8`. Typed source, contract, and local test
observations support the bounded reconciliation. The execute ceiling is
advisory; authority comes from ADR 0026 and the active goal.

Applied concepts: `universal-evidence-before-intervention`,
`universal-repository-contract-precedence`,
`agent-conduct-authority-bounded-action`, and `universal-no-change-option`.
No new source repair is warranted for the original routing failure given the
accepted correction and current verification. The general refactoring and
architecture alternatives were not selected.

All remaining packet obligations are nonmaterial to this planning disposition:

| Concept | Missing requirements | Reason |
| --- | --- | --- |
| debugging-causal-repair | causal explanation; failing reproduction before repair; first divergence | No new defect repair is selected. The accepted erratum states the historical cause; the unsafe host search was not repeated to recreate an OOM. |
| operations-contract-conformance-testing | consumer-owned contract tests with a run cadence; request-side and response-side suites separated from live dependencies; shared specification as oracle; the shared specification as the test oracle | This disposition adds no cross-service behavior or live-serving conformance claim. Current CAPLAB paths were checked locally. |
| task:repository-assessment | evidence-co-change; evidence-generated-artifacts; evidence-version-history | No architectural hotspot, generated-code metric, or historical churn inference is made. Current implementation and accepted decisions suffice for this specific item. |
| testing-deterministic-async-observation | repeated or adversarial scheduling results | No scheduling or concurrency behavior changes. Verification observed completed process handles and terminal test output. |

Citation consumption is recorded in the local Pincite trace.

## Planning projection execution

CAPLAB-86 (`795ac6ad-fba9-4ef2-92a4-630c7ea908d8`) was changed from Backlog
to Cancelled with the supersession note appended. Read-back verified the
expected state, the exact submitted description inside Plane's added outer
`div`, preservation of the original description bytes inside that wrapper,
and unchanged title, priority, assignees, labels, parent, project, and issue
number. The original description SHA-256 was
`52950b8c58785389478c6c1e12c2d11847372df2fbaad673f61d030b14d4362c`;
the resulting stored description SHA-256 is
`c8e797710aac119ec3d8618e1ca787874c35e1c8c3b9447cf05843cf864bee66`.
Evidence: `/tmp/caplab-86-before-update.json`,
`/tmp/caplab-86-update-scoped-result.json`, and
`/tmp/caplab-86-after-update.json`. The first CLI request omitted the project
required for UUID bulk updates and failed without mutation; the explicit
project retry succeeded. The live issue was compared with the earlier
snapshot and showed no conflicting edit. No other item was changed.
A fresh list read (`/tmp/caplab-roadmap-after-86.json`) shows 20 open
items. The broader goal remains incomplete.
