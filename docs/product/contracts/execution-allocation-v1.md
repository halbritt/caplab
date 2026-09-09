# Proposed allocation across accounts and lanes

`caplab.execution_allocation.plan_execution_allocation` produces a prospective
schedule from declared metadata. It implements one available procedure for
CAPLAB-80's treatment-allocation requirement. Adopting it requires a study
decision that freezes the population, resources, seed, allocation and analysis;
this contract adopts none of those values for the current study.

## Input and procedure

The input has exactly these fields:

| Field | Required value |
| --- | --- |
| `schema_version` | `caplab-execution-allocation-input/1` |
| `seed` | Integer from 0 through 2^64−1; booleans are rejected |
| `cycles` | Positive integer count of complete cycles, at most 10,000 |
| `worlds` | Nonempty list of distinct world aliases |
| `arms` | List of at least two distinct arm aliases |
| `resources` | Nonempty list of objects containing exactly `account` and `lane` |

Names are nonblank strings of at most 128 characters. Each list has at most
10,000 entries. Accounts must be distinct across resources, and lanes must
be distinct across resources. There must be at least as many resources as
arms. Account/lane pairs remain fixed within the plan; they do not establish
equivalence between accounts or separate account effects from lane effects.
Use restricted administration aliases, not credentials or provider account
identifiers. World and resource names are opaque; no named path is opened.

For each world and cycle, let N be the number of resources and A the number
of arms. The planner produces N batches of A proposed slots. Every batch
contains each arm once, on distinct accounts and lanes. Over a complete cycle,
each arm uses each resource exactly once. The total is therefore
`worlds × cycles × resources × arms`, which must not exceed 10,000. No count
is rounded up, and no partial cycle is synthesized. Too few resources or an
excess count raises `ValueError`; this means the supplied plan cannot use this
procedure, not that the study is infeasible.

The planner sorts input names and resource pairs before seeded randomization.
For every world/cycle, it shuffles the arms and resource pairs, then uses each
cyclic rotation once. It shuffles rotations, within-batch launch order and
global batch order. Thus each arm has the same planned exposure to each
resource within each world/cycle, while batch timing and launch position are
randomized. Launch-position counts are not guaranteed equal in a finite plan.
The cyclic construction samples a restricted family of schedules; it is not
uniform randomization over all possible balanced allocations. Any later
randomization-based analysis must use the actual frozen assignment procedure.

The report records the seed, method version, Python implementation/version and
`random.Random` generator. Identical metadata under the same implementation
produces the same report regardless of list ordering. Cross-Python-version
byte identity is not promised; retain the generated plan and exact software
identity. The canonical input hash ignores list order and JSON formatting;
the CLI additionally records the hash of the exact input bytes.

## Example

Save new synthetic metadata as `allocation.json`:

```json
{
  "schema_version": "caplab-execution-allocation-input/1",
  "seed": 37,
  "cycles": 1,
  "worlds": ["synthetic-world"],
  "arms": ["retrieval", "sham", "none"],
  "resources": [
    {"account": "synthetic-account-a", "lane": "synthetic-lane-a"},
    {"account": "synthetic-account-b", "lane": "synthetic-lane-b"},
    {"account": "synthetic-account-c", "lane": "synthetic-lane-c"}
  ]
}
```

```sh
PYTHONPATH=src python3 scripts/execution_allocation.py allocation.json
```

The report has three batches and nine `proposed_slots`. Each slot has a neutral
plan-local ID, world, cycle, arm, account, lane, batch number and launch order.
These IDs do not identify sealed trial assignments and are not globally unique.
The CLI reads at most 1 MiB of input, rejects invalid UTF-8, duplicate JSON keys,
non-JSON constants and invalid metadata, and writes only a JSON report to stdout.
Malformed input exits 2 without a report. Success exits 0. It creates no files.

## Adoption and interpretation

Freeze the seed before allocation; do not search seeds for desirable results.
Keep the selected plan in restricted custody because its rows reveal arms and
administration aliases. The report is not a blinded coder surface. Map aliases
to exact native Bindings and resources in restricted administration custody;
verify that different aliases do not conceal a shared account or service.
Do not infer that subscription and API routes are the same subject.

An executor must separately establish account availability, limits, service
isolation, complete native identity and capture, authorization, and enforcement
of the frozen batch allocation. This helper reserves nothing and launches
nothing. A proposed batch does not establish simultaneous execution; record
actual launch/completion times, account/lane identities, deviations and missing
attempts. Account counts do not establish achievable parallelism. Keep failures
and unavailable captures in the frozen denominators, and do not silently move
failed slots to another account, time window or seed.

Exact planned marginal balance cannot prove lack of interaction effects,
carryover, model drift, interference, differential attrition or treatment
leakage. It supplies no capacity estimate, statistical power, reviewer accuracy,
qualification or study-readiness decision. The report therefore retains
`basis: declared-metadata-only` and `execution_authorized: false`.

The [implementation record](../../records/implementation-2026-09-09-execution-allocation.md)
names the scoped authority, verification and limitations. CAPLAB-80 and
CAPLAB-84 remain incomplete after this planning helper is available.
