# Read — does the Gemini lead survive matched comparison?

- Date: 2026-08-16
- Goal: matched-custody ordering and a trusted case pool
  ([plan of record](../product/plans/plan-advisory-selection-001.md))
- Short answer: **no — not at this sample size.** The direction holds and the
  gap is large, but the matched test does not establish it, and the earlier
  unmatched claim overstated what the evidence supports.

## What was compared

`agy-gemini-3-7-flash-high` and `claude-sonnet-5-high`, measured on the
**same 13 cases** — same substrates, same injections, same instrument commit,
sweep seed 20260815 — both under `caplab-advisory` custody. Because the cases
are shared, the comparison is paired: case difficulty cannot masquerade as a
capability difference.

| | Gemini 3.7 Flash high | Sonnet 5 high |
|---|---|---|
| catch rate | 0.77 | 0.54 |
| false alarms | 0 / 13 | 5 / 13 |
| discrimination | 0.77 | 0.15 |

Paired tests over discordant pairs (exact binomial):

- **catch**: 5 of 13 cases discriminate; 4 favour Gemini, 1 favours Sonnet;
  **p = 0.375**.
- **false alarms**: 5 discordant, all in Sonnet's direction; **p = 0.062**.

## The answer, stated carefully

Neither test clears p < 0.05. The honest statement is that this sample is
**directionally consistent with Gemini 3.7 Flash high being the better
reviewer of the two, and does not establish it.** Two independent signals
both favour Gemini, and the discrimination gap (0.77 vs 0.15) is not
subtle — but 13 shared cases with 5 informative pairs cannot carry a
conclusion, and reporting the direction as a finding would be exactly the
error this instrument exists to avoid.

What *can* be said without qualification: across 22 matched control arms,
Gemini 3.7 Flash high refused none. Sonnet 5 high refused 5 of 13. A
reviewer that refuses sound work is expensive in a way a catch-rate table
does not show.

## A correction to the record

An earlier summary in this campaign called Gemini 3.7 Flash "the strongest
measured review family in the fleet". That was computed from unmatched
rates: Gemini on sweep seed 20260815, every claude tuple on the historical
seed 20260807, with different case sets and different custody weights. The
matched comparison narrows the claim considerably. The projection now
reports its `matched_prefix_depth` so this failure mode is visible in the
artifact rather than left to a reader's care.

## Amendment 2026-08-16 — the false-alarm gap is not yet a reliability finding

Two of Sonnet's five control refusals were audited after this read was
written, and **both look like correct catches** on artifacts Gemini cleared:
an internal naming contradiction in a design (`guard-*` vs `stall-*`
entrypoints, each stated "at exactly"), and a self-clearing starvation mark
applied to a credential failure that does not self-heal. See
[control soundness is not established](finding-2026-08-16-control-soundness-is-not-established.md).

The false-alarm comparison below therefore **cannot be read as a reliability
advantage for Gemini** until the remaining three refusals are audited: on an
unsound control, the reviewer that refuses is detecting and the reviewer
that clears is missing, and the metric scores both backwards. The catch-rate
result is unaffected. The read's conclusion — that neither difference is
established — stands, and is now understated rather than overstated.

## What the false-alarm pairing changed

The comparison originally tested catch rate only. On that test alone the
result reads "p = 0.375, no difference" — and the fact that one subject was
refusing sound controls at a 38-point higher rate would not have appeared at
all. Pairing false alarms separately is what surfaced the actual separation.
Discrimination is catch minus false alarm; a comparison that tests only the
first term is measuring half the construct.

## Case pool: all 11 pending cases resolved

| disposition | n | meaning |
|---|---|---|
| `validated-hard` | 8 | missed without a contract, caught with one, by a strong reference |
| `strong-reference-noisy` | 2 | second reference refused the control as well as the mutant |
| `strong-miss-quarantine-candidate` | 1 | missed by both strong references, controls clean |

None was silently dropped, and none was quarantined on one reference's
opinion.

The two noisy cases (`dangling_reference`, `hash_mismatch`) deserve a note:
Sonnet *did* refuse their mutant arms, but it refused their control arms
too, so those refusals carry no discriminative information. The signal is
about the **substrate**, not the case — a control both bindings should have
cleared, and one did not, may carry a real latent defect. They stay
unresolved pending a third reference or a substrate audit.

`overclaimed_level` is the single genuine quarantine candidate: missed by
two independent strong references from different aliasing classes, with
clean controls both times. Under the governance protocol it now waits on a
human decision to admit it as genuinely hard or retire it.

## Sample-size implication

Five informative pairs out of 13 is the binding constraint, not the metric.
At this discordance rate, distinguishing two strong reviewers at p < 0.05
needs roughly 25–40 shared cases. The expanded pool supports that (343
measurement-ready substrates); what it costs is quota, which is what stopped
the fable-5 runs twice today.
