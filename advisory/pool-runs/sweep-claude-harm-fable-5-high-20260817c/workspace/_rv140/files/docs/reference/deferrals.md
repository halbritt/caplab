# Named Deferrals {#el:deferrals}

Purpose: the standing registry of named deferrals — every capability the
compiler has honestly declined to deliver yet, each bound to the predicate or
decision that makes deferring it sound.

This page is a **projection, never a second truth**. A deferral is *made*
sound by a versioned predicate or an accepted decision clause (the doctrine:
versioned predicates make deferrals legal — an `@1` states its evaluation
bound honestly, and the strengthening registers as a later version,
invalidating nothing). The catalog and the decision records stay normative;
when this page and a predicate disagree, the predicate wins and this page is
the defect. Entries move to [Recently retired](#el:retired) when delivered,
so the subtraction is auditable rather than silent.

Registry-currency enforcement (a check that fails when this page and the
catalog drift) is itself a deferral — see
[self-law as a verification gate](#el:build-flow).

## Store and provenance (RFC 0009 / D0009) {#el:store}

| Deferral | Sound under | Unblocks when / next step |
|---|---|---|
| Cold packs (aged-record archival) | D0009's storage model; RFC 0009 | Named by the Principal when ledger scale demands it; sealing at the RFC 0009 thresholds is already in force. |
| Merkle selective verify | RFC 0009 | A verification need over sealed history narrower than `reconcile --verify`'s full shadow refold. |
| Persisted per-store fold cursor (cold-start is O(tail) today) | D0009.C9's full shape; `instance-store-scales@1` names the bound | The cursor persists across processes, not only within a session's hold. |
| `reconcile --deep` / `--migrate` | RFC 0009; `instance-store-scales@1` | Deep re-verification and store-format migration verbs, named when a migration exists to run. |
| D0009 generated-record deviations (C5's "33" vs the registry's 34; C9's embedded-cursor claim) | Awaiting the clause retrofit (see [Corpus and doctrine](#el:corpus)) | Corrected when the RFC 0002–0011 `## Decision (clauses)` retrofit regenerates D0009. |

## Trust and isolation (RFC 0012 / D0012) {#el:trust}

| Deferral | Sound under | Unblocks when / next step |
|---|---|---|
| Rung-2 uid isolation exercised **as a gate** (the machine-evaluable strengthening of `hostile-lane-contained@1`) | D0012.C6 — the mechanism is delivered; enforcement is privilege-gated and fails closed unprivileged | A host that grants unprivileged user namespaces (this host denies them), or provisioned lane uids exercised under a registered check. |
| Enforced sandbox isolation (network isolation + resource limits) | RFC 0012 rung 2 | OS-enforced confinement of lane runtimes beyond credentials/ownership. |
| Keyed receipt seals (verification receipts/reports carry `v1-hash`, an unkeyed digest) | RFC 0012; the keyed-seal model is in force for submissions (`v1-hmac`) | Extending the seal-key discipline from the submit/admit seam to verification evidence. |
| Rung-3 cross-workstation trust / external chain anchoring | D0012's rung ladder | Exporting ledger head hashes beyond the workstation's write reach (signed remote refs, a transparency log); until then the chain is tamper-evident only within the single-uid trust domain. |

## Work-graph and build flow (RFC 0010 / D0010) {#el:build-flow}

| Deferral | Sound under | Unblocks when / next step |
|---|---|---|
| Dependency-frontier ordering exercised live (multi-packet graphs) | D0010; every live work-graph so far lowered to one packet | The first plan whose honest lowering is a multi-packet graph. |
| Multi-packet integration batches | D0010.C8; `work-graph-integrated@1` records the single-packet grain | Same trigger as frontier ordering; the batch linker's union arithmetic is proven deterministically. |
| Anchored-base v1 bounds: change-set **deletes** over an anchored base; **batch integration** over anchored bases; **binary content** under the expansion gate; a **pure-Go git object reader** | `product-lineage-anchored@1` — each bound is a typed refusal, not a defect | Named later versions of the anchored-body arithmetic; the reader strengthening narrows the world-read surface without changing the shape. |
| Receipt-based RFC 0010 §7.2 shape (sealed link receipts vs the linker failing closed) | RFC 0010 §7.2 | The linker emits sealed receipts instead of refusing; arrives with keyed receipt seals. |
| Packetization must treat a whole-tree-check-unit as atomic | RFC 0010 §5.2 — found 2026-07-04 driving the praxis night-shift-gap-miner | Whole-tree teeth verify each intermediate materialized tree, so splitting one file (which `ruff`/`compileall` check atomically) across additive dependent packets makes intermediate change-sets individually unverifiable even when the final composition is clean. Lowering must keep a whole-tree-checked unit in one packet. The verify-reject→revision routing (driver `6c1acee`) is the companion delivered fix; this is the lowering half. |
| `go test ./...` as a registered verification check | Its environmental blocker fell with `cgroup-supervision-suite@1`; cost-bearing | The Principal's to name — it multiplies every dual-signal run's wall cost. |
| Self-law as a verification gate: a `lint-rfcs` check identity in `policy/checks/` | `truth-surface-hardened@1` delivered the linter as a build tooth only | Registering the check identity so a self-law violation fails verification, not only `make check`. **Registry-currency rules for this page belong here**: an entry naming a target-state or decision that does not exist, or a delivered capability still listed as standing, should fail the same gate. |

## Cross-repository and fleet (RFC 0014 / D0014) {#el:fleet}

| Deferral | Sound under | Unblocks when / next step |
|---|---|---|
| Driver-planner auto-scheduling of attestations through `striatum drive` | D0014's v1 same-workstation flow | Cross-repo pins beyond v1. |
| Cross-repository integration through the live driver session | D0014 | Same family; today's cross-repo passes integrate by operator application, recorded honestly. |
| A live-LLM cross-repository run | D0014 | A fleet pass whose lanes span repositories in one funnel. |
| Accept/reject refusal loudness for a broken `check_registry` declaration | `checks-resolve-to-repo@2` — checks resolution sits in `buildSession`, so the recording path is not gated: the verdict records, the bounded transition is silently skipped (the standing P4 best-effort contract), and the loud refusal arrives on the next session-constructing invocation (`drive`/`status`). No weakened drive can occur — the refusal aborts `buildSession` before any registry load — so only loudness on this verb is deferred, never the refusal's effect. | A design pass choosing between resolving checks before `RecordAcceptance` (gating a ledger append on state it does not consume) or propagating the bounded transition's error after a successful record (a recorded-but-refused exit posture changing the standing bounded-transition contract). The delivered boundary is guarded meanwhile (`internal/cli/checks_registration_resolution_test.go`, the accept/reject boundary guard). |
| Praxis fleet teeth: `pytest` and surface-reachability/denylist-population as registered checks | `reminder-bot-product@2`; the praxis registry ships `ruff` + `compileall` | Hermetic `pytest` needs the venv/deps/service mocks materialized; the surface probe needs a live-service check shape. |
| `reminder-bot-product` re-reading **Verified** | `reminder-bot-product@2` keeps floor-satisfiable conjuncts by design | The live LLM build+verify run is **proven** — praxis carries two compiler-Verified integrated change-sets (the API and CLI frontier lane runtimes). What remains is the predicate strengthening binding the *product* state to a Verified reading over such evidence. |
| ECR lane-attribution independence levelling | `satisfaction-earns-its-force@1` | Exogenous Change Records carrying attribution that the claim-level computation can weigh for independence. |

## Scheduler and capacity (RFC 0008 / D0008) {#el:capacity}

| Deferral | Sound under | Unblocks when / next step |
|---|---|---|
| Pipelines beyond default (divergent + synthesis topologies) | RFC 0008; the catalog's pipeline vocabulary | The first pass honestly needing a non-default topology. |
| Capacity harvest activation | RFC 0008's harvest doctrine | The Principal activates harvesting when idle-capacity spend is wanted. |

## Driver and liveness (RFC 0006 / D0006) {#el:driver}

| Deferral | Sound under | Unblocks when / next step |
|---|---|---|
| Automated tree watching | RFC 0006 | Watching the repository tree for exogenous change. Distinct from the **delivered** durable-wake liveness floor (`liveness-is-the-systems-property@1`, 2026-07-04): the timer wakes the driver; nothing yet watches the tree. |

## Corpus and doctrine {#el:corpus}

| Deferral | Sound under | Unblocks when / next step |
|---|---|---|
| The deletion pass | Named in the Epoch 3 close | A pass whose packet grain is subtraction of dead corpus. |
| The RFC 0002–0011 `## Decision (clauses)` retrofit | The decision-record model arrived after those RFCs | Regenerating the early decisions in clause form; also clears the D0009 generated-record deviations. |

## Recently retired {#el:retired}

Delivered deferrals move here (most recent first) so the list above never
silently shrinks; prune entries once the CHANGELOG has carried them through
a release.

- **Fleet check-registry auto-resolution** — delivered by
  `checks-resolve-to-repo@2` (RQ-6698, 2026-07-04): registration's
  `resolution.check_registry` sibling derives the registry, so a plain
  `striatum -repo <fleet> drive` gates on the fleet repo's own checks with
  no hand-passed `-checks`. Explicit `-checks` overrides; a
  declared-but-unusable path refuses before the registry loads, naming
  repo and path; declaring nothing stays byte-identical to `@1`. Its
  residue is the accept/reject refusal-loudness deferral above.
- **`-checks` resolution relative to `-repo`** — delivered by
  `checks-resolve-to-repo@1` (RQ-5168, 2026-07-04).
- **Git product-ref anchoring at base-composition grain** — delivered by
  `product-lineage-anchored@1` (2026-07-04); its residue is the four
  anchored-base v1 bounds above. The first Verified evolution
  (`evolution-earns-verified@1`, RQ-5203) rode it the same day.
- **The live LLM build+verify run on a fleet repository** — proven on praxis
  (2026-07-03/04): two change-sets built by lanes, dual-signal Verified, and
  batch-integrated (`frontier-api-lane-runtime`, `frontier-cli-lane-runtime`).
- **Fold semantics for `cancel_request` resolutions** — superseded by the
  first-class `cancel` verb, itself lane-built through the funnel (RQ-2044,
  2026-07-04).
- **The standing-timer liveness floor** — delivered by
  `liveness-is-the-systems-property@1` (2026-07-04).
