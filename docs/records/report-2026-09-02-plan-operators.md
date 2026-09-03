# Plan-defect operators: nine classes, audited before anyone is scored

- Date: 2026-09-02. Phase P3 of `planning-constructs-v1.md`, first half —
  the operators and the control audit that Arm 2 and the ranking memo's
  judge calibration both stand on. Principal-directed: "start on the
  operators."
- Code: `src/caplab/advisory/plan_operators.py`,
  `tests/test_advisory_plan_operators.py` (11 tests),
  `scripts/plan_operator_audit.py`. Audit output:
  `advisory/pool-runs/plan-operators-audit-20260902/` (per-mutant rows and
  a summary), scored on the pinned P2b instrument (oracle `a785e717…`,
  registry v37).

## The operators

Work graphs are JSON, so every operator is a structural edit with a
mechanical checker, and every injection records two facts the review
operators never needed: which oracle verdict the defect flips, if any, and
whether it changes the packet count.

| class | card defect | oracle sees it | packet Δ |
|---|---|---|---|
| `dangling_dependency` | dangling dependency | legality (`dangling_dependency`) | 0 |
| `circular_depends_on` | circular `depends_on` | application index | 0 |
| `unresolvable_acceptance_check` | unresolvable acceptance check | resolvability | 0 |
| `write_scope_outside_tree` | write-scope outside tree | only with `-tree` | 0 |
| `atomicity_split` | the atomicity split | no | **+1** |
| `dropped_deliverable` | dropped deliverable | no | 0 |
| `purpose_scope_contradiction` | purpose/scope contradiction | no | 0 |
| `overclaimed_verification` | overclaimed level (work-graph analogue) | no | 0 |
| `merge_independent_packets` | — (size probe from the ranking memo) | no | **−1** |

Six of nine are oracle-silent by construction, and that is the design: a
dropped deliverable or a swapped purpose parses, orders and resolves
exactly as its control did. Those are the defects a mechanical gate cannot
see and a plan reviewer has to. The two size-changing operators are the
probes the ranking memo asks for — a judge that prefers the larger graph on
a split pair and the smaller on a merge pair is scoring packet count.

The card's "overclaimed level" is a prose-plan defect; its work-graph
analogue here cuts a packet's acceptance checks to one while its purpose
asserts full verification. The name says what it does.

## The audit

Scar tissue 1, applied to the operators as well as the controls. Every
candidate control is scored by the pinned oracle and kept only if every
mechanical check passes. Every operator is then applied to every sound
control and must satisfy three things: the checker fires on the mutant and
not on the control; an oracle-visible class flips exactly the verdict it
owes; an oracle-silent class leaves parse, index and legality as the control
had them.

Population: the 192 graphs the 20260827 planning sweep produced (eight
planners, one contract). **164 are sound controls**; the 28 excluded are
the scope-overlap and parse failures the board already reports.

| operator | applied | not applicable | checker ok | oracle contract | admissible |
|---|---|---|---|---|---|
| `dangling_dependency` | 164 | 0 | 164 | flipped 164/164 | 164 |
| `unresolvable_acceptance_check` | 164 | 0 | 164 | flipped 164/164 | 164 |
| `write_scope_outside_tree` | 164 | 0 | 164 | stayed legal 164/164 | 164 |
| `purpose_scope_contradiction` | 145 | 19 | 145 | stayed legal 145/145 | 145 |
| `circular_depends_on` | 144 | 20 | 144 | flipped 144/144 | 144 |
| `atomicity_split` | 133 | 31 | 133 | stayed legal 133/133 | 133 |
| `dropped_deliverable` | 133 | 31 | 133 | stayed legal 133/133 | 133 |
| `overclaimed_verification` | 130 | 34 | 130 | stayed legal 130/130 | 130 |
| `merge_independent_packets` | 66 | 98 | 66 | stayed legal 66/66 | 66 |

1,243 admissible mutants over 164 controls. "Not applicable" is the
operator declining a graph that lacks what it needs — no dependency edge to
close, one output where two are required, no independent pair — and is
recorded per graph, not silently skipped.

**The audit earned its place twice before the table looked like this.** The
first pass found `atomicity_split` tripping the oracle on 62 of 133 graphs
and `merge_independent_packets` on 9 of 66 — both classes that promise to
stay legal. Neither was the plan's fault. The split's tail packet repeated
an input the original already read, which the parser rejects, and it was
left parallel to the original's dependents, so a dependent that legally
shared the original's scope now overlapped the tail's. The merge gave the
survivor dependencies that sat after it in the authored index. The fixes are
in the operators (dedupe, rewire dependents onto the tail, re-derive a
topological index that keeps the authored order where dependencies allow),
and the audit now reports zero silent trips. A judge shown either of those
first-pass mutants would have been asked to prefer a control over a graph
the oracle itself rejects — the pair would have measured nothing.

## What is missing: real accepted plans as controls

The card's controls are "real accepted plans," and none are available
today. The exchange spool that held 121 work-graph submissions on
2026-08-27 has since been pruned to 479 submissions with **no work-graph
bodies**; the 68 production identities in the calibration file do not
resolve to objects in the graph store by name. The audit ran on the sweep's
graphs, which are synthetic controls — sound under the oracle, produced
under one contract, but not accepted by anyone. Recovering the production
bodies (the graph store's `refs/products` are the likely path) is the next
piece of this work, and until it lands, any Arm 2 sweep or judge calibration
on these controls must say "synthetic controls" on the claim.

## Next

- Recover production work-graph bodies from the graph store; re-run the
  audit over them as the second population.
- Judge calibration (ranking memo, layer 1): control/mutant pairs from this
  audit to two independent-family judges, both orders, catch and
  false-alarm per judge and per class, with the two size probes read
  separately.
- Then the first pairwise ranking over the 164 sound graphs, at no planner
  spend.
