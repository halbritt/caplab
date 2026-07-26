# Post-mortem — advisory-selection-001 design, 2026-07-14..26

Written at the repository owner's direction after the owner characterised the
work as sloppy. Scope: the primary agent's conduct in charting and executing
the CAPLAB-44 map. This is an assessment of process, not of the study.

## Summary

The study reached a working instrument and produced real findings. It got
there through roughly two weeks of design built on a substrate that stopped
being justified partway through, and it accumulated nine defects along the
way — several of which would have been expensive if they had survived into
execution. Most were caught by finally running something cheap.

## Defects, by severity

### 1. Built on a substrate that stopped being justified (highest cost)

CAPLAB-57 reframed the study from **instrumental** (pricing Pincite's routing
bug) to **foundational** (testing whether serving doctrine changes behavior at
all). The 11 real-commit rows existed *only* to serve the instrumental framing:
they were ground-truthed pairs, which mattered when the claim had to be about
those specific routing misses.

After that reframing I continued building on them for several more sessions —
eligibility cascade, hunk-scoped partial application, test-hunk classes,
re-root, residue scanning, contested-target adjudication, concept-concentration
arithmetic. All of it machinery for extracting ground truth the new question
did not need. The owner had to stop the work and say the study had gone awry.

**I recorded the decision that invalidated the substrate and did not propagate
it.** That is the central failure; most of the wasted effort descends from it.

### 2. Statistical error that would have produced an underpowered study

I derived `k` from `MDE = 1.96 × SE` and described the result as adequate.
That is the "95% CI excludes zero" condition — approximately **50% power**.
80% power requires `MDE = 2.8016 × SE`, which is **2.04× the sample size**.
Two k tables shipped at half the required power before I caught it.

Uncaught, this produces the worst available outcome: a completed, expensive
study with a null result that cannot be distinguished from insufficient power.

### 3. Cost anchor wrong by ~11×

I priced the native study from ADR-0038's ceiling ($25 for 16 episodes →
$1.56/episode → $7.80 after a repair multiplier). ADR-0038 authorized an
**`openrouter/*` proxy route** and its own front matter records that ADR-0039
withdrew it as proxy substitution. I had read ADR-0039. I used the number
anyway.

Measured actual: **$0.69/episode**. The error inflated the projected study cost
from ~$600 to $3,300–$11,100 and made feasibility look marginal when it was not.

### 4. Stop condition that would have aborted 100% of episodes

I wrote "stop on any model other than the pinned one in the stream" without
ever looking at a captured stream. Every episode legitimately shows
`claude-haiku-4-5-20251001` in `modelUsage` — 19 output tokens, zero assistant
turns, an auxiliary call. A second trap sits underneath: assistant turns report
`claude-opus-5` while usage reports `claude-opus-5[1m]`, so a naive comparison
false-positives too.

### 5. Headroom asserted rather than measured

CAPLAB-81 permitted a scenario to establish headroom by *citing* the target
concept's `common_failure_modes` entry. That catalogue records what
practitioners get wrong, not what a current model gets wrong. First contact
with data: SC-01 scored **1.00 in all four arms** — completely saturated — and
SC-02's no-doctrine arm scored 0.79. The criterion failed on its first test.

### 6. Containment defect

`run_episode.sh` passed the ambient environment to every subject episode,
including `OPENROUTER_API_KEY`, `STRIATUM_MCP_TOKEN`, `FOAM_API`. No episode
used them (verified), but ADR-0039 treats proxy *availability* as the thing to
contain.

### 7. Model never pinned

The runner omitted `--model` and inherited the session default. Uniform in
practice; not pinned in fact, which ADR-0060 requires.

### 8. Credential printed to a transcript

`env | grep` dumped a live key value where names would have answered the
question.

### 9. Stated intent read as completed work

A turn ended with "Next I build the three scenario worlds and run the
shakedown." Nothing ran between turns. The owner asked "how did it go?" of work
that had not started.

## Root causes

### A. Designing without cheap verification

Defects 2, 3, 4, 5 and the whole of §1 share one shape: **something plausible
was written down and frozen when a cheap check was available and not run.**

- The retrieval measurement that invalidated the arm design took **five
  minutes** and the binary had been on disk the entire time.
- The real per-episode cost was sitting in raw custody at
  `~/.local/share/caplab/campaigns/` and needed one `jq`.
- The stop condition needed one captured stream to falsify.
- Headroom needed one unassisted episode.

None of these required authorization. All were available from the first session.

### B. Optimising the artifact instead of the question

The real-commit substrate was chosen because it yielded *defensible ground
truth* — a property of the artifact. It cost population size, tractability, and
ultimately relevance. The same instinct produced 17-of-18 tickets typed HITL
when the repository's own ADR-0026 delegates those decisions to me, blocking
edges wired on topical affinity rather than dependency, and sequential
execution where the design's own drift argument prefers parallel. The owner
pushed back on this three separate times before I named it.

Rigorous-looking machinery is not the same as a design that answers the
question.

### C. Not separating intent from completion

Defect 9, and the general habit of describing planned work in a register that
reads as done.

## Preventive measures

These are mechanisms, not intentions. Each is checkable.

1. **No parameter is frozen on assertion where a zero-cost measurement
   exists.** Applies to headroom, cost, recall, spontaneous rate, and any stop
   condition expressible against a captured artifact. If the measurement is
   cheap and the answer is unknown, run it before writing the number down.

2. **Provenance check on every cited figure.** Before using a number from a
   record, read that record's `status` field. ADR-0038 said `withdrawn` in its
   own front matter.

3. **Statistical constants carry their meaning inline.** Write `2.8016
   (80% power)` or `1.96 (CI excludes zero, ≈50% power)` — never a bare
   multiplier. The error in defect 2 is invisible as `1.96` and obvious as
   `≈50% power`.

4. **A question-change triggers same-session re-derivation.** When any
   resolution changes the study's question, claim, or population, every open
   downstream ticket is re-justified against the new question or ruled out of
   scope **in that session**. Not deferred.

5. **Validate a stop condition against a real artifact before freezing it.**
   A stop condition that has never been evaluated against a captured stream is
   a guess.

6. **Default to the delegation the repository already grants.** ADR-0026 makes
   the primary agent the decision mechanism. A ticket is HITL only under
   ADR-0026's own interrupt test: authority the delegate lacks, an externally
   irreversible effect, or ambiguity not safely narrowable.

7. **Blocking edges express dependency, not affinity.** If ticket B can be
   resolved without ticket A's answer, there is no edge.

8. **Secrets are matched by name, never printed by value.**

9. **Turn boundaries state ran / did not run explicitly.** No forward-looking
   sentence may be the last word on work status.

## What the shakedown demonstrates about all of this

Every defect in §2–§5 was caught within hours of running something, after weeks
of not running anything. The instrument cost **$66** and about an hour. The
strongest single argument for measure 1 is that this pilot invalidated four
frozen design decisions for roughly one percent of the study's projected cost.

The corrective is not more care in design. It is running the cheap thing first.
