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

---

# Amendments — recorded 2026-07-30, before any further episode

All three were issued by the repository owner on stated methodological grounds.
Amendments 1 and 3 are corrections to gate design and executability; amendment
2 is a post-data efficiency change that does **not** move the frozen threshold.

## Amendment 1 — requalification is ceiling-only

**Pre-data rationale, on gate asymmetry — not on the observed result.** A
ceiling mechanically truncates positive Δ; a floor does not. A scenario at 0.07
has only headroom. The floor gate was therefore asymmetric *against* the
hypothesis, and at `luna/low` it removed the two lowest-scoring scenarios at
precisely the rung where a low-capability-benefits-more effect would be
largest.

**New gate: drop only scenarios scoring ≥ 0.85 in the none arm.** No floor
drop. Phase-0 minimum survivor count unchanged at 4.

**Retroactive:** run the injection arm at `luna/low` for `factory-lifecycle`
and `ephemeral-instance`, and reissue the `luna/low` contrast over all 7
scenarios. Both the amended 7-scenario pooled Δ and the original 5-scenario
figure are reported.

## Amendment 2 — adaptive k

**Rationale.** Observed within-cell variance was 0.0081 against a 0.25
worst-case bound; four of five survivors scored identically on all five trials.
Replicates beyond the point of agreement are copies.

**The observed MDE of 0.072 is ≈ 0.33/5 — one code flipping in one scenario.
That is the quantisation floor, not achieved precision.** This instrument
resolves exactly one quantity: *how many scenarios flip a code*. Power is
governed by scenario count, not by k.

**Procedure per cell:** run k=2. If both trials agree exactly, stop at 2. If
they disagree, extend to k=5. Record realised k per cell; recompute pooled SE
and tuple MDE from realised k.

**The frozen threshold of 0.35 stays fixed at its pre-data derivation and does
not move with realised k.** Operative bar remains `max(0.35, tuple MDE)`. Any Δ
clearing the empirical MDE but not the frozen threshold is flagged, never
silently dropped.

## Amendment 3 — tuple order is randomised and frozen

The prior instruction to re-sort remaining tuples by measured none-arm score is
**not executable**: unrun tuples have no measured score. With the stopping rule
removed, order carries no analytic weight.

Order of the remaining 11 tuples drawn at random with a recorded seed and
frozen now, so provider drift spreads across the ladder as noise rather than
stacking on one end. Sorting by measured unaided difficulty happens at the
**end**, for analysis only.

## Framing — the injection arm is an upper bound

Stated before results are in. Injection packets are hand-built from concept
fields and verified to contain their target. **No deployed path produces this
stimulus.** Every Δ measured here is therefore a ceiling on what any real
delivery mechanism could achieve.

**Consequence, claimable without further work:** if the ladder comes back flat,
the corpus is inert *under ideal delivery*, and retrieval repair is moot
regardless of how good retrieval could be made. That is a stronger conclusion
than the objective nominally claims.

---

# Amendment 4 — rater replacement, authorized 2026-07-31

The original artifact rater, Claude Sonnet at high effort, reached an external
monthly spend ceiling after the subject episodes had run. The repository owner
authorized a rater change and continuation of the ladder on 2026-07-31.

This amendment changes the rater, not the subject, scenarios, arms, outcome
codes, threshold, or stopping rule.

## Continuity calibration

The replacement is selected by a blinded continuity calibration against 42
existing Claude-rated behavioral attempts: six attempts from each scenario.
Selection uses seed `20260731`. Within each scenario, attempts are grouped by
their original primary-code score, each group is ordered by the SHA-256 of
`<seed>:<slot>`, and groups are sampled in ascending-score round-robin order.
Infrastructure dispositions, behavioral non-attempts, malformed judgments, and
empty diffs are ineligible.

The replacement sees only the frozen code definitions and candidate diff. It
does not receive the subject model, effort, arm, slot, prior judgment, or
scenario result. The native Codex CLI runs from an empty directory, ignores
user configuration and execution rules, uses a read-only sandbox, and enforces
an exact JSON output schema.

A candidate passes only if all of these gates pass on the frozen panel:

- at least 90% agreement over all primary-code bits;
- at least 80% primary-code agreement in every scenario;
- at least 85% agreement on originally positive primary-code decisions; and
- at least 85% agreement on originally negative primary-code decisions.

`SCOPE` agreement is recorded but is not part of these gates. Agreement with
the old rater measures continuity, not truth.

## Candidate order

Candidate search is ordered and stops at the first tuple that passes every
gate:

1. `gpt-5.6-luna/high`
2. `gpt-5.6-sol/high`
3. `gpt-5.6-terra/high`
4. `gpt-5.6-luna/xhigh`
5. `gpt-5.6-sol/xhigh`
6. `gpt-5.6-terra/xhigh`

The accepted candidate is not selected by ranking observed agreement. If no
candidate passes, scoring stops for a new owner decision.

## Rerating and custody

Once a candidate passes, it rates every score-eligible behavioral attempt,
including attempts already rated by Claude. Behavioral non-attempts receive a
mechanical primary score of zero after disposition validation. Infrastructure
episodes remain excluded. The final analysis must not mix Claude and
replacement-rater judgments.

Claude judgments remain immutable audit evidence. Replacement prompts, schemas,
event streams, raw final messages, parsed judgments, CLI version, model,
effort, thread identifier, hashes, and failures are stored in a separate
append-only namespace under the campaign root. Empty objects, missing keys,
extra keys, non-Boolean values, nonzero exits, and unattested model or effort
are failures, never zero scores.

The replacement uses the same model family as the subjects. This is a disclosed
instrument limitation. Blinding removes tuple and arm identity from the prompt,
but it does not remove model-family effects.
