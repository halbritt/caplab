# Finding for striatum: production prose reviews are world-blind

- Date: 2026-09-06. From the tree-v1 coverage report
  (`coverage-2026-09-06-tree-v1-bases.md`); plan §2.3 amendment names this
  record.

**Observation.** In the production ledger (373,371 events), 8,220 `review`
runs were opened. 6,053 carry four input pins — the change set, the
product-artifact as `base`, a `materialized_base` whole tree, and one more —
the anchored-base era. 1,919 carry exactly one pin: the reviewed artifact.
Every review of a design, implementation plan or proposal is one-pin. No
repository tree, no base, no referenced exchange object is pinned for a
prose review; the reviewer sees the artifact alone.

**Observation.** Under CAPLAB's `iso-v1` — the artifact alone, the review
preamble telling the reviewer to judge only what is presented — the
`codex-sol-high` binding refused 18 of 18 sound exchange-prose controls, all
on the ground that a referenced document (RFC, decision, escalation, receipt,
execution contract, ADR) was not reachable from the artifact. Before
isolation it cleared 16 of 18 of the same controls by resolving those
references against the live checkout it was mounted in — a tree production
never gives it.

**Inference.** A verification-oriented reviewer placed on a one-pin prose
review lane will refuse most sound artifacts, because the lane gives it
nothing to verify against. That is a property of the lane's pinned set, not
of the reviewer and not of CAPLAB's instrument. Whether striatum wants prose
reviews to carry a base (the repository tree the artifact was written
against, and the exchange objects it names) is a lane-design decision for
striatum. Until it is taken, CAPLAB's production-faithful measurement of
prose review treats refusals on unpinned references as false alarms, because
that is what they are in the lane as designed.

**Not claimed.** Nothing here says Sol is a poor reviewer, or that a
world-blind prose lane is wrong. It says the two are mismatched today, and
that the mismatch is visible in the ledger.
