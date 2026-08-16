# Finding — the control arm barely reproduces itself

- Date: 2026-08-16
- Disposition: **the false-alarm axis is not interpretable at one trial per
  case.** This is independent of, and larger than, the control-soundness
  problem recorded the same day.

## The accident that revealed it

A pool run measured `agy-gemini-3-7-flash-high` on 16 cases and showed 50%
false alarms on change-set artifacts against 0% on documents. The obvious
explanation was a profile misfit: the v1 contract asks whether an artifact
"is COMPLETE for its stage" and carries "the sections its stage requires",
and a JSON change set has no sections. A delivery-shaped contract
(`v1-changeset`) was written and the **identical 16 cases** re-run to
confirm.

The re-run did not confirm it. It revealed something else.

## Test-retest, same cases, same subject, same day

Fifteen cases were measured under both runs. Ten of them used an unchanged
prompt in both (the document cases; only change-set cases changed profile).

| quantity | agreement between identical runs |
|---|---|
| mutant verdict | 12/15 — 80% |
| `caught` | 13/15 — 87% |
| **control verdict** | **8/15 — 53%** |
| `false_alarm` | 10/15 — 67% |

Two `broken_internal_crossref` cases flipped from cleared to refused with
**the same profile, the same artifact, and the same prompt**. Nothing about
those cases changed between runs except the sampling of the model's output.

## What this means

**The mutant arm is a reasonably stable measurement; the control arm is
close to a coin flip.** That asymmetry is explicable: a planted defect is a
clear signal, so a reviewer's refusal of the mutant is driven by something
real and reproducible. A sound artifact, by contrast, always contains
arguable imperfections, and whether any given one crosses into "refuse" is a
borderline judgment that resamples differently each run.

Consequences:

1. **A single-trial false-alarm rate does not describe a binding.** At 53%
   control-verdict reproducibility, a 0/13 and a 3/13 are not distinguishable
   observations of different subjects; they are plausibly two draws from the
   same one.
2. **The change-set/document split that prompted this is not established.**
   Fisher's exact on the original 3/6 versus 0/9 gives p = 0.044 — nominally
   significant, and not trustworthy, because it is a single-sample split of a
   quantity whose own test-retest is near chance. The profile-misfit
   hypothesis is neither confirmed nor refuted here.
3. **It reaches back to the matched read.** The Gemini-versus-Sonnet
   false-alarm gap (0 against 5, p = 0.062) rests on one trial per case. It
   now has two independent reasons to be uninterpretable: unaudited control
   soundness, and unmeasured reliability. The catch-rate comparison is less
   affected — catch reproduces at 87% — which is fortunate, since that was
   the headline.
4. **`discrimination = catch − false_alarm` inherits the weaker term.** A
   composite is no more reliable than its noisiest component.

## Corrective

Replicate the arms and report reliability rather than assuming it. The
instrument already treats repeated trials as variance estimation rather than
coverage — "repeated trials estimate variance but do not increase unique-case
coverage" — so this uses existing doctrine rather than new authority.

- Add a `replicates` setting to the pool runner. Each arm is invoked *r*
  times; the row records every verdict, not just a summary, so reliability
  can be recomputed later without paying again.
- Score a case's arm by majority, and record the split so unanimous and
  2-of-3 cases are distinguishable.
- Publish per-run test-retest agreement alongside the rates, so a reader can
  see how much weight the numbers carry.
- Prefer replicates on the **control** arm when budget is tight: it is the
  unreliable one, and it is the term that inverts the metric when wrong.

## What is not claimed

That the subject is defective, or that any binding's published number is
wrong in a known direction. The finding is about what the instrument can
resolve at one trial, not about who wins. Catch-rate results, which carry the
existing conclusions, reproduce at 87% and are not being withdrawn.
