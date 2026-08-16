# Scenario authoring prompt

One scenario per concept. Give this to a fresh agent with a **redacted concept
record** inlined (see *Information partition*). Generated per-concept prompts
live in `scenarios/<NN>-<concept-id>/PROMPT.md`.

---

## Task

Build one self-contained scenario that puts a coding agent in a situation where
the concept below is the correct approach, and where a competent agent might
plausibly get it wrong.

You are not testing whether an agent can read doctrine. You are building a
situation in which following that doctrine produces a materially different
repair than not following it.

## Information partition — read this first

You have been given the concept's **title, claim, decision_rule,
why_it_matters, common_failure_modes, counterexamples**.

You have **deliberately not** been given its `retrieval_terms` or `routing`
fields, and you must not go looking for them in the corpus.

Part 1 of this study measures whether Pincite's retrieval finds this concept
from your task text. If you write the task using the concept's retrieval
vocabulary, that measurement becomes circular — it would report that retrieval
finds words that were handed to it. Write from the **situation**, never from
the concept's own language.

## Deliverables

Produce five artifacts in the scenario directory.

### 1. `world/` — the repository

- Small and self-contained. A handful of source files. Python unless the
  concept is language-specific.
- **It must build, and its tests must pass.** The defect is latent, not
  failing. A red test tells the agent where to look and destroys the scenario.
- Realistic shape: plausible module names, plausible surrounding code. Not a
  puzzle, not a toy with one obvious flaw.
- Include at least one existing test, so test-tampering is observable.

### 2. `TASK.md` — the symptom

- **Consumer register.** What a user, operator, or colleague would report.
- **60–120 words.** Richness is held constant across scenarios by construction;
  a longer task is a stronger hint and would confound the comparison.
- State: observed symptom, how to reproduce, expected versus actual.
- **Never state:** the cause, a suggested fix, the concept's name, or any
  design vocabulary. "Records are missing and nothing appears in the logs" is
  right. "Errors are being swallowed without an explicit failure policy" is not.

### 3. `reference.md` — a solution exhibiting the lesson

Prose, not a patch. What a repair that follows this doctrine actually does to
this code. It anchors the codes and must be one *possible* good repair, not the
only one.

### 4. `codes.json` — 2–4 binary behavioural codes

Each code needs:

- **`positive`** — the observable that must hold.
- **`negative_space`** — what does *not* count. This carries most of the
  discriminative weight. State the tempting near-miss explicitly.
- **`kind`** — prefer `artifact` (diff, write-set) over `transcript`
  (action sequence). Transcript codes vary with harness and confound
  cross-harness comparison.

**Hard rule: no code may be satisfied by the untouched `world/`.** A predicate
that fires on the pristine tree measures nothing. This is checked mechanically
and the scenario is rejected if it fails.

Include a **scope** code: the agent must not edit tests. Agents modify tests to
ratify their own shortcut — one observed episode added a test asserting that
logging is correct failure handling.

### 5. `headroom.json` — leave empty

Headroom is **measured**, not asserted, by running the unaided arm separately.
Do not claim it.

## What makes a scenario fail

These are measured outcomes from prior scenarios, not hypotheticals.

| failure | what happened |
|---|---|
| **Ceiling** | A duplicated-constant scenario scored **0.94–1.00 unaided at every rung** of a 12-rung ladder. The model consolidates duplicated constants on its own. No doctrine can add anything. |
| **Floor** | A failure-policy scenario scored **0.00–0.22 unaided everywhere**. No tuple solved it. Equally uninformative. |
| **Asserted headroom** | Headroom was previously established by citing the concept's `common_failure_modes`. That catalogue records what *practitioners* get wrong, not what current models get wrong. It failed on first contact with data. |
| **Predicate fires on parent** | Three of seven codes were satisfied by the untouched world — `raise\b` matched a pre-existing raise, `exc` matched the substring in `Exception`. Reported arm means were artifacts. |

Aim for a repair a competent agent gets **partly** right unaided: it fixes the
symptom but misses the lesson. That is where doctrine can show an effect.

## Acceptance

A scenario is admitted only when:

1. `world/` builds and its tests pass with the defect latent.
2. No code fires on the untouched `world/`.
3. Every code is satisfied by `reference.md`'s repair.
4. `TASK.md` is 60–120 words and names no cause, fix, or design term.
5. Measured unaided score lands in **[0.25, 0.75]** — measured later, not by you.
