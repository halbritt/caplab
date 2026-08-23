---
card_id: planning-constructs-v1
artifact_type: capability-card
schema_version: caplab-capability-card/1
card_version: 0.1.0
status: principal-specified
constructs: [planning.finishability/1, planning.defect_discrimination/1]
decision_owner: repository-owner
specified_by: principal
specified_at: 2026-08-23
---

# Planning constructs — two arms, one oracle set

Specified by the Principal, 2026-08-23, recorded verbatim in structure.
Both arms share one mechanical oracle set; planning's structural advantage
over a design instrument is that the outcome half is machine-checkable with
code that exists today.

## Arm 1 — production qualification (`planning.finishability/1`)

A fixed corpus of planning tasks harvested from real campaigns — accepted
design + packet context, replayed exactly as the lanes saw them (the
production ledger holds 300 implementation-plan and 112 work-graph
artifacts). Each tuple produces an implementation plan / work-graph
lowering; a mechanical oracle scores it:

- **lowering legality** — `workgraph.Parse` + `ApplicationIndex` (acyclic,
  deterministic) plus the legality checks packetization already runs
  (production pass rate 0.626: defects are plentiful and real);
- **acceptance-check resolvability** — `Registry.ResolveEntries`; the
  hollow-Verified lesson, mechanized;
- **write-scope reality** — every packet's write_scope prefix denotes in
  the staged tree; every seam its purpose names resolves;
- **finishability proxies** — dependency depth × width (the
  ancestor-cascade cost function), whole-tree-check-unit atomicity (the
  RFC 0010 §5.2 trap: splitting one lint-checked file across dependent
  packets makes intermediates unverifiable), and plan-promise coverage
  (every deliverable the prose claims appears in a packet).

Purpose: directly re-rank the implementation-planning preference list,
which today leads with a tuple measured at 0.207 finishability while its
best alternative is disabled.

## Arm 2 — plan review discrimination (`planning.defect_discrimination/1`)

Matched-pair defect injection into plans; defect classes drawn from
observed production failures, never invented: dangling dependency,
circular depends_on, unresolvable acceptance check,
write-scope-outside-tree, the atomicity split, dropped deliverable,
purpose/scope contradiction, overclaimed level. Controls are real accepted
plans. Purpose: decide who holds the implementation-plan-review gate,
currently allocated on pure priors.

## Scar tissue applied from day one (binding on the implementation)

1. **Audit the controls before scoring anyone** — control-soundness
   oracles run over every control first. (The Sol adjudication found ten
   of twenty controls defective; FA computed over unaudited controls is
   an upper bound wearing a number's clothes.)
2. **Pin the prompt-contract version in every claim** — the v1-changeset
   quarantine cost a cohort its comparability.
3. **Retain substrate bodies in the CAS at registration** — implemented
   2026-08-23 (`caplab.advisory.cas`: write-through loader, hash-verified
   reads, git-history recovery for rewritten repo-docs at their pinned
   commits; **652/652 bodies retained**, 27 MB, zero permanent losses).
4. **Report anchored alongside FA** — fa-rewards-silence: a silent planner
   scores spotless.
5. **Measure the harness axis** — the mounting gradient (gemini +28pts →
   deepseek +9) will matter at least as much for planning, which is
   tool-hungry.

## Placement nuance (Principal, recorded)

Fable's reservation is proposal + design, not planning. CAPLAB advisory
custody measures through the adapter directly, outside
`supported_pass_types`, so the instrument can measure the Fable pair on
planning for information without touching the reservation; extending the
reservation on a good result is a one-line ruling later.

## Implementation phases

- **P0 (done 2026-08-23):** CAS retention + loader fallback.
- **P1:** oracle shim — a Go tool exposing `workgraph.Parse`,
  `ApplicationIndex`, legality checks, and `Registry.ResolveEntries` to
  CAPLAB as one JSON-verdict command (lives in striatum-next `tools/`,
  since the packages are internal).
- **P2:** Arm 1 corpus harvest (task = accepted design + packet context,
  replayed as the lane saw it), oracle scoring, claims.
- **P3:** Arm 2 operators over plan artifacts, controls audited first,
  then the discrimination sweep.
