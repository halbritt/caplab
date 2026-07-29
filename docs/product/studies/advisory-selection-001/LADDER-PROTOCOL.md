# Ladder walk — protocol, frozen 2026-07-29 before the first episode

## Objective

Find the lowest tuple on the codex ladder at which **statically injected**
doctrine produces a measurable change in agent conduct. Report the boundary, or
report that no boundary exists below the top of the ladder.

## Scope

- **Scenarios (7)**, screened in-band at `sol/high`: anticorruption-layer,
  factory-lifecycle, error-surface-reduction, contract-conformance,
  ephemeral-instance, database-fidelity, separate-semantic-structural.
- **Arms:** `none` | `injection` (static, no retrieval).
- **Ladder:** codex × `gpt-5.6-{luna,terra,sol}` × `{low,medium,high,xhigh}`.
- **Start:** `luna/low`. **k = 5** per cell.

## Detectable effect — computed before the threshold was chosen

Outcome is a fraction of codes satisfied, bounded `[0,1]`, so `Var <= 0.25`
worst case with no estimate required. Per scenario,
`Var(D) = 0.25/5 + 0.25/5 = 0.10`, `SE = 0.316`. Pooling over `S` scenarios
with scenario as a blocking factor:

| surviving scenarios | pooled SE | MDE @ 80% power, alpha .05 two-sided |
|---:|---:|---:|
| 7 | 0.120 | **0.335** |
| 6 | 0.129 | 0.362 |
| 5 | 0.141 | 0.396 |
| 4 | 0.158 | 0.443 |

## Threshold — named by the operator, committed before the first episode

**Pooled Δ ≥ 0.35 counts as a measurable change.**

Derived, not chosen: 0.35 is the detectable effect at the full surviving set
(S=7, k=5). A threshold below the MDE would be unfalsifiable — the design could
not distinguish it from noise.

**The consequence must be stated with every result.** The prior noise band on Δ
was −0.18 to +0.28. Its upper edge sits *below* this MDE. **This design cannot
detect an effect of 0.28.** A pooled Δ under 0.35 therefore means *not
detectable at this power*, never *no effect*. Where fewer than 7 scenarios
survive at a tuple, the MDE rises per the table and is reported for that tuple.

## Stopping rule — AMENDED 2026-07-29, before the first result

**Superseded before any tuple completed.** The original rule ended the ascent
on two consecutive sub-threshold tuples. That is a **data-dependent stopping
rule**: the analysis would depend on what was observed, which is a forking path
and inflates false positives in the direction of the hypothesis.

**Amended rule: walk the full ladder unconditionally.** All 12 tuples, none arm
then injection arm, regardless of observed Δ. There is no early termination.

The threshold is **retained as an interpretation marker, not control flow**.
Pooled Δ ≥ 0.35 marks a tuple as showing a measurable change; the walk does not
branch on it. The boundary is read off the completed surface afterwards, which
also satisfies "do not report a boundary from a single cell" without needing a
confirmation re-run rule.

Termination is therefore: **ladder exhausted, or a hard ceiling** (wall-clock,
episode ceiling, sustained infrastructure failure).

## Ordering

Nominal rung order is **not trusted**. `terra` has previously scored below
`luna` on unaided competence. After each tuple, remaining tuples are re-sorted
by *measured* unaided (none-arm) score, ascending.

## Requalification

The `sol/high` screen does not transfer. At every tuple: run the `none` arm
first, then requalify — **drop scenarios scoring ≤ 0.15 (floor) or ≥ 0.85
(ceiling)** — then run `injection` on survivors only.

**Phase 0 stop:** if fewer than 4 scenarios survive at `luna/low`, halt and
report; the ladder cannot be walked from that rung.

## Evidence discipline

- `make check` green before the first episode and after any config change.
  *(Run 2026-07-29: initially FAILED on dangling scaffold links; fixed; green
  at 230 tests before any episode.)*
- Every episode scored by `caplab-scenario-coder.py`; dispositions by the
  fixture-validated classifier. No manual admission.
- `attempted: false` is **not** a result until the classifier has separated it
  from provider failure. A quota exhaustion previously recorded as a decline
  fabricated a hypothesis-confirming result. Any tuple with an unusual
  non-attempt rate: open the raw streams before interpreting.
- Custody append-only under `~/.local/share/caplab/campaigns/`; model pinned
  per turn; attestation joined by `thread_id`, never by file mtime.
