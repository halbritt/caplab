# ADR 0064 — Advisory selection campaign

- Status: **accepted** — halbritt (Principal), 2026-08-16, interactive
  session ("Accept as written")
- Date: 2026-08-15 (drafted during the endorsed AFK campaign)
- Deciders: halbritt (Principal)
- Plan of record: [`plan-advisory-selection-001`](../product/plans/plan-advisory-selection-001.md)

## Context

Binding selection evidence was needed by consumers beyond striatum (council,
UIPass), the striatum bootstrap-qualification pin (expires 2026-09-21) is
licensing declared quality classes without releases, and the only fleet-wide
review evidence was the striatum-tuner 2026-08 sweep held as non-qualifying
source custody. The Principal resolved fourteen design decisions in the
2026-08-15 grilling session and endorsed a three-tier AFK campaign.

## Decision (as endorsed and executed)

1. **Advisory track, separate from qualification.** `caplab.advisory`
   produces scored advisory claims (`caplab-advisory-export/1`) for the
   review construct `review.defect_discrimination/1`. It creates no
   Measurement, no qualification Claim, and cannot feed the qualification
   ledger. ADR 0062's boundary is unchanged.
2. **Quartermaster registry.** A new repository (`halbritt/quartermaster`)
   stores binding projections (deterministic extraction from striatum-next
   `backends/` at a pinned commit), ingested scored claims, and
   availability/quota/cost observations, and evaluates consumer-owned
   objective specs into derived, never-stored rankings. Roles and ranking
   objectives remain consumer-owned.
3. **Seed admission.** The completed matched-pair runs of the tuner sweep
   are admitted as `historical-seed` custody claims, scored by CAPLAB's own
   scorer with anchored detection recomputed from retained arms on the
   corrected anchor path only. Consumers weight this custody class down via
   objectives (the example spec uses 0.8).
4. **Advisory-grade execution profile v0.** CAPLAB-directed runs execute the
   pinned tuner instrument through subjects' declared adapter commands, with
   receipts, completed-run markers, and a hard pair-budget refusal. Endorsed
   Tier 2 scope: `agy-gemini-3-7-flash-{low,medium,high}`, ≤21 pairs each,
   ~$10 cap; claude/codex runtimes are supervised-only.
5. **Corpus expansion under governance.** Substrate registry (587 substrates:
   387 fate-final exchange subjects + owned-repo documents), sealed/open
   hash partition, class-balanced per-sweep sampling, five CAPLAB-authored
   operators, and the case-admission protocol: mechanical gate, then
   weak-reference calibration (local model), then strong-reference
   validation where a case every strong reference misses quarantines the
   case, not the binding (Principal rule, 2026-08-15).

## Explicitly not decided or performed

No D0019 qualification release, no bootstrap-pin displacement or renewal, no
striatum policy or backend edit, no fine-tuning, no training rows, no
enabled timers or daemons, no claude/codex live runs. Each needs its own
authority.

## Reopening conditions

Quartermaster growing an opinionated ranking of its own; any consumer
treating an advisory projection as qualification; the sealed partition being
sampled by an advisory sweep; custody classes beyond the closed set; or the
bootstrap-pin deadline forcing a qualification-grade follow-on.
