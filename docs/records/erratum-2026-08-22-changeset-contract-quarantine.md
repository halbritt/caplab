# Erratum — the v1 change-set contract is quarantined

- Date: 2026-08-22. Principal accepted the four-part correction this day.
- Trigger: infra postmortem
  `~/git/infra/hosts/proximal/postmortems/2026-08-21-oom-rg-store-grep.md`
  (host OOM, four ~84 GB `rg` kills). Its Cause B is this instrument: the
  eval it cites is the codex-sol-high sweep of 2026-08-21.

## The defect

`REVIEW_PROMPT_V1_CHANGESET` inlined a change set's files but passed its
base as a bare content hash, materialized no base blob, and then demanded
the subject verify anchoring and hash integrity. With no lookup primitive,
the only way to comply was a recursive grep of the host's 361 GB store.
Subjects did exactly that (codex observed directly; agy per the
postmortem), which:

1. exhausted host memory (the greps were repeatedly OOM-killed), and
2. contaminated the measurement: on change-set cases, catch partly measures
   store-forensics affordance (a resolved base allows diffing the mutant
   against the shipped original — a blinding leak), and false alarms partly
   measure grep failure (an unverifiable base read as broken anchoring).

## Exposure

20 of 57 breadth cases (35%) per subject at seed 20260819 ran the v1
change-set contract, plus the change-set share of 20260817, the 20260820
replay, and the change-set anchor cases. All synthetic-contract claims are
touched; dispatch-instrument claims (20260815, historical-seed) are not.

The false-alarm pattern fits the mechanism: codex-sol-high's control
refusals split 8 on change-set controls (35% of cases) versus 4 on prose
(65% of cases), and its change-set catch sat at ceiling (20/20) against
35/37 on prose.

## Re-scored contrasts (prose-contract cases only, n=37)

| contrast | full-set | prose-only | verdict change |
|---|---|---|---|
| sol-high vs flash-high (20260819) | 8–1, p=0.039 | 6–1, **p=0.125** | **RETRACTED as established** |
| sol-high vs flash-medium (20260819) | 15–1, p=0.001 | 11–1, p=0.006 | holds |
| flash-high vs flash-medium (20260817) | 11–1, p=0.006 | 9–1, p=0.021 | holds |
| flash-high vs flash-medium (20260819) | 7–0, p=0.016 | 5–0, p=0.062 | weakens to marginal |

The flash effort separation's strongest evidence was never the per-seed
sign test but the targeted per-cell reproduction, and that survives: all
six clean-contract cells reproduced in direction. The cross-family claim
"sol leads flash-high" does **not** survive and is withdrawn to "not
established"; sol's lead over flash-medium stands on clean cases.

## Corrections applied

1. **Contract v2** (`REVIEW_PROMPT_V2_CHANGESET`, now the routed profile):
   states the base tree is not available, forbids searching the filesystem
   or any store, scopes hash verification to content present in the set,
   and keeps the base *declaration* reviewable (so `base_dropped` stays
   detectable). Deviation from the postmortem's literal "materialize the
   base": the base is a striatum repo-state tree hash the empty exchange
   CAS cannot resolve (striatum's follow-up #2); materialization is
   infeasible on this box until that lands, and scope-out achieves both
   goals (no greps, no unverifiable demands) honestly. If the CAS is
   populated, a future profile may materialize instead.
2. **Operator restriction**: `hash_mismatch` no longer plants defects on
   base-object hashes — an operator may only plant what the contract lets
   a subject honestly find.
3. **Promotion quarantine** (`QUARANTINED_PROFILES = {"v1-changeset"}`):
   any cell measured under the contaminated contract in any sweep is
   withheld until it reproduces entirely under a clean profile. Effect:
   the promoted corpus goes **7 → 6** (`qs-aae295d9adf3871e`/`base_dropped`
   demoted — its control-soundness adjudication stands; the cell's
   *measurement* is what is tainted), and 10 quarantined cells are now
   itemized, including two flash separators and four sol-pair separators.
4. **v1-changeset is retired from routing** — no future sweep can emit it,
   which is the freeze in structural form. v1-changeset and v2-changeset
   numbers do not compare; claims carry the per-row profile.

## What this does NOT change

The six promoted prose cells; the control adjudications of 2026-08-21; the
dispatch-instrument claims; sol-high's prose-case performance (35/37 catch,
4 false alarms — still the best absolute catch measured). The existing
ledger claims are append-only and stay, now to be read with this erratum;
whether to derive superseding prose-only claims is a follow-up decision.

Amended records: `report-2026-08-21-sol-high-cross-family.md`,
`results-2026-08-22-comprehensive-bindings.md`,
`report-2026-08-20-targeted-reproduction.md`,
`adjudication-dossiers-2026-08-21-promotion-queue.md`.
