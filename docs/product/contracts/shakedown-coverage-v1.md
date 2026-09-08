# Shakedown structural coverage, version 1

Status: prospective rule selected in the
[CAPLAB-68 decision](../../records/decision-2026-09-08-caplab-68-coverage.md).
An adopting study must freeze its level definitions, candidate metadata and
exposure rules before selecting the shakedown set. This rule selects no current
worlds and authorizes no model call, exposure, seal or execution.

## Declare the axes before selecting worlds

The custodian records each required axis, its levels and assignment rules,
source/version for every assignment, and a coverage requirement for each level
in the intended population. A singleton level is still declared. Any
not-applicable level needs a reason; an unknown value is unresolved, not an
automatic not-applicable classification.

| Required axis | What the levels distinguish | Why coverage matters |
| --- | --- | --- |
| Language/runtime family | Task language and materially different execution runtime | Parsing, compilation and runtime-dependent observations |
| Build/check system | Build and acceptance-check path, including required services | Buildability and verifier integration |
| Task role | Repair, extension, review, or justified no-change, when present | Different observable outputs, attempt rules and scope boundaries |
| Defect/conduct mechanism | Task-specification mechanism, such as error propagation or state transition | Different ways the instrument can misread conduct; broad concept categories alone are insufficient |
| Concept category | Frozen corpus category mapping with its source identity | Variation in the guidance/code-authoring surface; category is not semantic validity |
| Observation/scoring path | Artifact versus event sequence, and mechanical versus judgment scoring | Capture availability, redaction and code-application failures |
| Native execution path | Harness launch/capture path and materially different service-isolation profile | Harness-specific capture, containment and shared-service behavior |

Declare the following interaction families as well: language/runtime ×
build/check system; observation/scoring × native execution path; task role ×
observation/scoring. Require each combination present in the intended population,
not the impossible full Cartesian product. Document absent combinations from
the population specification before selection. Marginal coverage alone can
miss an interaction: each scorer and harness can appear somewhere while one
scorer/harness pairing remains untested.

Levels describe structural paths, not individual world IDs or observed scores.
Do not merge levels to obtain a smaller shakedown set after inspecting candidate
coverage. Other interactions require a prospectively named failure mechanism
and explicit adoption. This is not a demand for every possible factor crossing.
Each world's code predicates, reference, oracle, task and visibility still need
their individual validation under the
[code-authoring](behavior-code-authoring-v1.md) and
[admission](advisory-study-admission-v1.md) contracts.

The mapping must expose design conflicts. For example, a justified no-change
task cannot be declared measurable under an unchanged gate that treats every
no-write response as unscorable. Resolve that construct/attempt contract before
selection; coverage cannot fix it. Actual accounts and lanes require their own
authorized runtime checks even when they share one structural profile. This
does not authorize adding harnesses or pooling distinct Bindings.

## Freeze the expected coverage universe

Before observing subject outputs, record:

1. Intended population and candidate inventory identities, level definitions,
   all marginal/interaction requirements, and the source mapping from each
   requirement ID to its meaning. Requirements come from the population
   specification, not whichever candidates survived inspection.
2. Each candidate's immutable ID and structural requirement IDs, its validated
   construction/codebook references, eligibility and prior exposure. Keep
   excluded or unresolved candidates in the selection dossier with reasons;
   do not feed them to the selector as eligible or silently erase their strata.
3. The selection algorithm/version, tie rule, metadata verifier, observer
   context, intended control condition, amendment policy and round cap. Freeze
   a protected witness of these identities before selecting or exposing worlds.

The full dossier retains this evidence. The planner below accepts only its
requirements and eligible-candidate projection. It does not verify metadata
truth, excluded candidates, the prior freeze or authority. A hash of its input
identifies bytes; it does not prove those bytes were declared prospectively.

## Minimum-cover rule

Choose the smallest number of eligible candidates whose union covers every
declared requirement. If several sets have that size, choose the
lexicographically smallest sorted tuple of exact candidate IDs, ordered by
Unicode code points without case folding or normalization. IDs must be frozen
before outcome inspection so they cannot serve as a hidden tie preference.

Keep every candidate that is the sole witness for any required token: every
valid cover must include it. Search the remaining combinations in increasing
cardinality and exact-ID order. The first complete cover is minimum. Adding
the same forced IDs to equal-sized candidate tuples preserves their lexical
order. Do not substitute a largest-first greedy result and call it minimum.

For example, requirements `1` through `6` have candidates A = {1,2,3,4},
B = {1,2,5}, C = {3,4,6}. Largest-first selection takes all three, but B+C
cover everything with two. No single candidate covers all six, so two is
provably minimal. This is synthetic set arithmetic, not an admitted scenario.

If a required level has no eligible witness, selection is infeasible. Report
the missing requirements and resolve the population or instrument through a
new prospective decision. Do not drop the level or open extra sealed material
merely to force a cover. If the minimum uses every candidate, there is no
remainder to seal. An amendment must explicitly resolve any conflict with
the planned holdout size; a requested seal fraction does not override coverage.

## Read-only planner

`scripts/shakedown_coverage.py` reads one UTF-8 JSON file and prints a report.
The input has exactly three fields:

| Field | Contract |
| --- | --- |
| `schema_version` | `caplab-shakedown-coverage-input/1` |
| `requirements` | Non-empty list of distinct, non-blank string IDs for all declared coverage obligations |
| `candidates` | Object with 1–24 distinct non-blank candidate IDs, each mapping to a non-empty list of distinct declared requirement IDs |

IDs are opaque metadata, never file paths to open. Unknown requirement IDs,
duplicate list entries, unknown fields, invalid types, duplicate JSON object
keys, non-finite JSON values and invalid UTF-8 are rejected before selection.
The 24-candidate bound limits the exact combinatorial search; it does not
choose a study size or assert a wall-clock bound. Larger plans need an explicit
tooling change, not a silent heuristic fallback. Requirement count is not a
sample-size or power calculation.

Save this new synthetic example as `coverage.json`:

```json
{
  "schema_version": "caplab-shakedown-coverage-input/1",
  "requirements": ["1", "2", "3", "4", "5", "6"],
  "candidates": {
    "A": ["1", "2", "3", "4"],
    "B": ["1", "2", "5"],
    "C": ["3", "4", "6"]
  }
}
```

From the repository root:

```sh
PYTHONPATH=src python3 scripts/shakedown_coverage.py coverage.json
```

The `caplab-shakedown-coverage-report/1` result selects B and C, reports
`minimum_cardinality: 2`, leaves A in `candidate_remainder`, and identifies
selected witnesses for every requirement. It also records the exact input
SHA256 and `basis: declared-metadata-only`. `status: covered` means only that
the supplied token sets cover the supplied universe.

Valid input with an uncovered requirement returns
`status: uncovered-requirements`, lists `requirements_without_candidate`, and
leaves selection, cardinality and remainder null. It exits 0 because this is a
completed feasibility calculation. Malformed input exits 2 with no report on
stdout. Neither exit 0 nor `covered` is an instrument-readiness decision.
The CLI creates no files and reads no world, reference, model output or corpus.

## Exposure, amendments and the seal

The custodian separately decides and records the selected world's exposure and
the remainder's seal under the study's authority. `candidate_remainder` is not
evidence that those worlds are sealed. A shakedown coverage set is not a random
sample and does not define an analysis-level holdout or a generalization claim.
Do not count shakedown episodes as fresh study episodes merely because the
same control condition will appear later.

Track at least two distinct properties per world: **unobserved**, meaning no
pre-study inspection of its subject outputs or outcome-derived summaries,
and **untuned-against**, meaning its applicable design/parameters have not been
adjusted using observed subject behavior. Record recipients and uses, including
coding or analysis by another agent; missing exposure records mean unknown,
not unobserved. World/task/report content and subject outcomes are different
visibility surfaces and must each be accounted for. A revised file or new hash
does not erase prior exposure to its predecessor or related design.

Measuring headroom on a would-be remainder world consumes outcome exposure,
even if only aggregates reach the designer. Later unread episodes can form a
new evaluation set under a declared design; they do not restore that world's
original unobserved status. Reconcile headroom requirements and the intended
holdout claim explicitly rather than reporting a seal that the workflow broke.

A uniform amendment based on unsealed observations can leave the remainder's
episode outputs unobserved while destroying its untuned status. Record which
observations motivated the amendment and which shared rules/worlds changed.
Control-only shakedown and an observer separate from the preregistration author
limit contrast exposure; they do not prove absence of selection bias or
inflation from tuning. Report feasibility verdicts to the designer under the
frozen information partition, retaining the underlying restricted evidence.

Classify findings by their actual effects: a repair preserving frozen subject
behavior and measurement definitions may be an instrument fix; changed
allocation, coder instructions, dose or analysis parameters require an
amendment; a task that cannot elicit the intended construct requires redesign.
Do not label a behavior-changing harness repair “no amendment” merely because
it fixes a bug. Freeze the amendment round cap before outputs; no cap is chosen
by this planner. Exceeding it invokes the study's precommitted redesign/stop
rule, not another favorable adjustment.

Actual headroom, code validity, blinding, accuracy, containment, native identity,
service isolation and uncertainty remain separate gates. The applicable
[capability card](../capability-cards/caplab-advisory-selection-001-advisory-responsive-approach-selection.md)
continues to govern interpretation. This rule validates no current candidate,
renews no historical shakedown authorization and makes no reviewer ranking.
