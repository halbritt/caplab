# An eval that measures reviewer quality — design from first principles

## 1. The thing being measured

A judgment review gate is given a candidate artifact and returns a verdict plus
findings. It exists to do two things at once:

- **catch** work that is defective, and
- **pass** work that is sound.

Either alone is free. A reviewer that refuses everything catches every defect. A
reviewer that accepts everything passes every sound candidate. Both are useless,
and — this is the whole difficulty — both can score well on a badly built
benchmark. So reviewer quality is inherently a *two-sided* quantity, and any
instrument that cannot observe both sides cannot measure it.

Beyond the verdict, a review has to be **usable**: a finding must point at
something that actually exists in the artifact, and point at the right thing.
A refusal with a fabricated or misplaced anchor is not a catch; it is noise that
happened to land on the correct side.

So: quality = (catches real defects) × (passes sound work) × (findings are
grounded and localized), reported separately, never summed into one number that
hides which half failed.

## 2. Why the 2026-08-07 corpus cannot measure it

The existing benchmark scores a tuple by `fate_agreement`: whether its verdict
agrees with the reviewed candidate's eventual fate, where `analyze.py:46-57`
defines fate as `revised` iff a later version of the same identity was admitted
after the reviewed content hash.

In this compiler, a refusing review *causes* that later version — a refused
review gate routes to bounded revision planning, which builds and admits the
successor. An accepting review lets the candidate stand.

Measured on the 34-example sample:

| production review verdict | fate=final | fate=revised |
|---|---|---|
| accepting | 9 | 0 |
| refusing | 2 | 23 |

The label agrees with the verdict that produced it in 32 of 34 cases. `fate` is
therefore not an observation about the candidate; it is a near-deterministic
re-encoding of the incumbent reviewer's opinion. Scoring a new reviewer against
it measures *agreement with the incumbent*, which is what `side_match` already
measured, under a name that sounds like correctness.

Two consequences that are easy to miss:

1. **It cannot be repaired by rebalancing.** Balanced accuracy fixes the class
   imbalance this corpus also has, but a balanced circular label is still
   circular. The defect is in the label's provenance, not its distribution.
2. **It rewards imitation.** The highest achievable score belongs to whichever
   tuple best mimics the disposition of the reviewers that generated the labels.
   Fine-tuning against it optimizes for that, and would report the result as
   improved review quality.

Observed directly: `codex-sol-max` refuses 20 of 22 and scores well; the
endpoint tuples accept 80–97% and score badly on the refusal class. Neither
population is discriminating. They are constants of opposite sign.

## 3. The independence requirement

The only fix is a label whose provenance does not run through any reviewer's
judgment of the artifact. Three sources qualify, in descending strength:

- **Constructed** — we place a defect ourselves, so we know it is there, what
  class it is, and exactly which element carries it. Independent by
  construction, and the only source that also yields matched negatives.
- **Mechanically checkable** — the defect is decidable by computation
  (a declared hash that does not equal the derived one; a path that does not
  exist in the tree; a required section absent under the pass contract). A
  machine, not a reviewer, is the authority.
- **Independently adjudicated** — the Principal resolved an escalation about
  this artifact, or a later incident/postmortem/revert established that an
  accepted artifact was in fact defective. Independent because the finding
  arrived from outside the review, and usually after it.

Everything else — reference verdicts, fates, model panels, LLM-as-judge over the
same artifact — is some other reviewer's opinion wearing a label's clothes.

## 4. Instrument: matched-pair defect injection

The primary instrument is the review analogue of mutation testing.

**Construction.** Take a candidate artifact that is known sound. Produce two
prompts that are byte-identical except for one injected defect:

- the **control**: the artifact unchanged;
- the **mutant**: exactly one defect of a known class, at a known element.

Dispatch both through the tuple's own declared lane, blind — nothing in either
prompt indicates that injection is in play, and the two are never shown together.

This is the only design that observes both sides on the same material. The
control measures false positives, which the current corpus cannot see at all,
and which is precisely the failure mode `codex-sol-max` exhibits.

**Known-sound population.** A control is only a valid negative if the artifact
really is sound. Selection rule: the artifact version was admitted, reached a
terminal accepted state, and no later version of that identity was ever admitted
— i.e. `candidate_fate == "final"` — *and* no subsequent incident, dossier, or
correction names it. `fate` is unusable as a quality label but is perfectly good
as a *filter* for "nothing further happened to this", which is all we ask of it
here. Residual risk: a latent defect nobody ever found makes a control an
unlabelled positive, which costs the reviewer a false positive it did not
deserve. That biases *against* good reviewers, so it is the safe direction, and
section 7 bounds it.

**One defect per mutant**, so a miss is attributable to a class.

## 5. Defect taxonomy, grounded in this system's incidents

Injections must resemble defects this compiler actually produces, or the eval
measures the ability to spot synthetic weirdness. Every class below is drawn
from a recorded incident in striatum-next, which also gives each one a citation
for why it belongs.

| class | injection | why it is a defect | provenance |
|---|---|---|---|
| `hollow_delivery` | drop most files from a multi-item change set, keep the plan's claims | delivery does not cover the plan it claims to satisfy | hollow-Verified incident, RQ-7555/dd6dde5 |
| `decorative_check` | replace a packet's `acceptance_checks` entry with an unregistered name | a check that resolves to nothing never runs | `acceptance_check_unresolvable`, dd6dde5 |
| `hash_mismatch` | perturb a declared `content_hash` / `result_tree_hash` | declared ≠ derived; refused at admission | anchored change-set contract |
| `dangling_reference` | repoint a cited path/evidence ref at something absent | the evidence cited does not exist | the `eval-runs/probe-k3-*` ref, fixed 2026-08-07 |
| `refuted_conclusion` | retain a claim the artifact's own evidence contradicts | internally incoherent | kimi-k3 "the budget is the fix", 2026-08-07 |
| `contradicted_clause` | add a clause negating an existing one | decision clauses must be consistent | D0005 clause structure |
| `dropped_section` | delete a section the pass contract requires | incomplete for its stage | design contract: Decision/Consequences/Constrains |
| `scope_violation` | insert an architectural commitment into a proposal | belongs to a later IR stage | RFC 0001 IR ladder |
| `overclaimed_level` | assert `Verified` where bindings support `Asserted` | claims are computed, never declared | claim algebra, P-invariants |
| `base_dropped` | remove repository files from an anchored base composition | the hollow-Product defect | anchored base contract |

The first four are also **mechanically checkable**, which matters for section 7:
we can verify independently that the mutant really is defective and the control
really is not, without asking any model.

## 6. Metrics

Per tuple, reported separately — never averaged into a single headline:

**Detection (needs the mutant/control pair)**
- `catch_rate` = P(refusing verdict | mutant), overall and **per defect class**
- `false_alarm_rate` = P(refusing verdict | control)
- `discrimination` = catch_rate − false_alarm_rate. Zero for any constant
  reviewer, in either direction. This is the headline number, and unlike
  balanced accuracy over a circular label, it is grounded in a constructed fact.

**Localization (mutants only)**
- `anchor_hit` = P(some finding's `element_anchor` resolves to the injected
  element | mutant caught). A refusal that names the wrong element is a
  coincidence, not a catch, and this separates the two.

**Groundedness (both arms, no ground truth needed)**
- `anchor_resolves` = fraction of findings whose `element_anchor` exists in the
  artifact at all. Mechanically checkable; a nonzero miss rate is fabrication.

**Calibration**
- severity agreement: a `major`-class injection should draw `needs_revision` or
  `reject` and a `major` finding; a `minor` one should draw
  `accept_with_findings`. Reported as a 2×2, not a scalar.

**Cost**
- `$ per defect caught` = spend / (catch_rate × mutants). The only cost figure
  that is comparable across tuples with different catch rates.

**Conformance** — json validity, verdict legality, schema shape, latency. These
carry over from `bench.py` unchanged and remain sound; they were never the part
that was circular.

## 7. Validating the instrument itself

An eval asserting ground truth must justify the assertion. Four checks, run
before any tuple number is quoted:

1. **Mutants are genuinely defective.** For the four mechanically-checkable
   classes, a checker confirms the mutant fails and the control passes. If a
   mutation does not actually break anything, it is discarded, not scored.
2. **Injections are not stylistically detectable.** A discriminator is given
   single artifacts and asked only "was this edited?", with no review framing.
   If it separates mutants from controls appreciably above chance, the mutation
   operators are leaking their own signature and the affected operator is
   rewritten. Without this check, a high catch rate may be edit-detection.
3. **Controls are clean.** Sample controls are checked against the incident
   record and the mechanical checkers. Section 4 notes residual risk is
   one-directional; this bounds its size.
4. **Size is not the discriminator.** Mutants and controls are drawn across the
   full prompt-size range and results reported per size band. In the existing
   corpus, outcome correlated almost perfectly with prompt size; that confound
   must not be rebuilt.

5. **A positive control scores well.** Run the instrument against reviewers
   already believed strong — the frontier harness tuples — *before* spending
   anything on unknown ones. If every tuple lands at the same low
   discrimination, the reading is ambiguous between "these reviewers are weak"
   and "these injections are undetectable", and the instrument has told you
   nothing. A known-strong reviewer must separate from the field, or the
   operators are wrong.

   This check is ordered first in practice and was omitted from the first
   version of this document. The 2026-08-07 run measured four endpoint tuples
   at 0.08-0.20 discrimination and spent ~$9.30 doing it before any positive
   control existed — so those numbers were uninterpretable at the moment they
   were produced. The harness tuples are subscription-billed and cost nothing
   to run, which makes the ordering error purely self-inflicted.

## 8. Sampling and cost

Discrimination is a difference of two proportions, so the sample must support
the difference, not each rate. To separate a genuinely discriminating reviewer
(≈0.5) from a constant one (0) with reasonable confidence needs on the order of
40 pairs; per-class rates over 10 classes need far more, so per-class figures are
reported as counts with intervals, not as precise rates, until the corpus grows.

Practical tiers:

- **Screen** (40 pairs = 80 dispatches) — cheap tuples and any first look.
  At DeepSeek's $0.016 that is ~$1.30; at K3's $0.80 it is ~$64.
- **Full** (100 pairs) — for a tuple about to be granted a quality class.

K3's measured $0.80/review makes the full tier ~$160 for that tuple alone, which
is a real constraint and an argument for screening on small artifacts first.
Small artifacts are also where injection is easiest to control, so the screen
tier should draw from the sub-64KB band deliberately — with section 7's check 4
reported alongside so the band is visible rather than hidden.

## 9. What this can and cannot license

**Can**: a declaration's `quality.classes.review`, with `basis: measured` and a
`benchmark_ref` naming the run — because catch_rate, false_alarm_rate, and their
difference are grounded in constructed fact rather than in another reviewer's
opinion. It can also justify *lowering* a class, which the current corpus cannot.

**Cannot**: any claim about defects outside the injected taxonomy. A tuple that
catches injected hash mismatches has shown nothing about catching subtle
architectural incoherence. The taxonomy is the scope of the claim, and the
declaration should say which classes were measured.

**Still open**: natural-defect recall. Injection measures detection of defects we
know how to describe. The historical miss set — real defects that slipped past a
real review, from incidents and postmortems — is the complement, and is small-n
but high-validity. It belongs in the same suite as a second instrument, reported
separately, and is the honest check on whether the taxonomy is representative.
