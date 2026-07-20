---
id: caplab-preference-001
artifact_type: study-preregistration
title: Constraint continuity in Fable-versus-GPT complex repository work
status: superseded-native-harness-redesign-required
decision_record: adr-0030
decision_authority: adr-0026
created: 2026-07-20
preregistered_at: 2026-07-20
execution_authorized: false
instrument_authority: adr-0033
instrument_status: superseded
superseded_by: adr-0039
---

# Constraint continuity in Fable-versus-GPT complex repository work

## Question and named use

For a named evaluator choosing an agent for complex repository maintenance, is
the evaluator's preference for Claude Fable 5 over GPT-5.6 associated with
better continuity across distributed mandatory constraints?

The named use is sustained, decision-dense maintenance where missed authority,
preservation, verification, or completion constraints cause owner
interventions. This study does not measure general intelligence, universal
coding quality, or model-wide capability.

## Frozen hypothesis

On six paired synthetic repository tasks, the Fable subject will satisfy more
mandatory constraints than the GPT subject on at least four valid pairs, and
the repository owner will blindly prefer the Fable output on at least four
valid pairs.

Both thresholds must hold. Otherwise the candidate explanation is
disconfirmed. Fewer than five valid pairs makes the study inconclusive. A tie
or unjudgeable preference is not a Fable preference. Constraint coverage is
scored before subject identity is revealed.

## Observable behavior

Constraint continuity is the fraction of preregistered mandatory task
constraints satisfied in the final repository state and handoff. Each task has
at least eight constraints distributed across four or more of these surfaces:

- requested product effect;
- authority and stop boundary;
- preservation of unrelated or historical state;
- repository-local instructions;
- failure and missingness handling;
- verification evidence; and
- completion and handoff accuracy.

CAPLAB-7 freezes each constraint as a mechanical or rubric-owned item before
execution. A longer answer, confident tone, or greater code volume cannot earn
constraint credit by itself.

## Credible rivals and confounders

1. **Presentation preference:** the evaluator may prefer prose style or
   concision rather than constraint continuity.
2. **Harness or provider behavior:** an integration failure, tool boundary, or
   provider route may cause the observed difference.
3. **Output opportunity:** latency, token use, or premature stopping may change
   how much work a subject can complete.
4. **Task familiarity:** one subject may have training or prior-task advantages
   unrelated to continuity.
5. **Over-caution:** a subject may preserve constraints by declining work that
   the task authorizes.

The run manifest records provider, harness, latency, token counts, tool errors,
and subject outcome separately. The rubric scores authorized task completion
and constraint continuity separately. Results remain descriptive.

## Fixed task population and sample

The population is synthetic repository-maintenance work with at least three
decision or lifecycle distinctions and at least eight distributed mandatory
constraints. The fixed sample is six paired tasks, one primary attempt per
subject per task:

| ID | Task shell | Required distinctions |
|---|---|---|
| P01 | Correct an issue-tracker backlog after a scope decision was mistaken for cancellation | projection, decision, authorization, execution |
| P02 | Classify reusable behavior in a historical repository without admitting its evidence | custody, inspection, admission, reimplementation |
| P03 | Diagnose and bound a retry after retained state defeats a recovery check | observation, diagnosis, correction, retry authorization |
| P04 | Refactor a deep module while preserving public behavior and unrelated dirty work | semantic behavior, structure, verification, user-owned changes |
| P05 | Upgrade a dependency with provenance and fail-closed compatibility checks | source evidence, supply-chain decision, implementation, rollback |
| P06 | Repair cross-repository runtime configuration without broadening service ownership | product authority, host integration, external state, cleanup |

CAPLAB-7 supplies fresh synthetic repositories and expected end states for
these shells. It may make details concrete but may not replace, add, or remove
a shell after this preregistration.

## Subject tuples

The two compound subjects differ only in model identity:

| Field | Fable subject | GPT subject |
|---|---|---|
| Model identity | Claude Fable 5 (`claude-fable-5`) | GPT-5.6 Terra (`gpt-5.6-terra`) |
| Agent harness | `terminus-2==2.0.0` under `harbor==0.18.0` | same |
| Subject instruction | one byte-identical CAPLAB subject instruction | same |
| Tools and network | identical task-local tools; external network disabled | same |
| Repository start | byte-identical fresh synthetic task image | same |
| Output ceiling | 8,192 completion tokens | same |
| Wall-clock limit | 45 minutes | same |
| Memory and skills | no prior conversation; no model-specific skill | same |

CAPLAB-7 must resolve and record exact provider model identifiers before it
freezes the instrument. If both models cannot run through the same harness and
tool surface, the study stops before calls rather than substituting a different
harness.

## Fixed execution and presentation order

The primary attempts run in this order:

1. P04 GPT
2. P01 Fable
3. P06 Fable
4. P03 GPT
5. P02 GPT
6. P05 Fable
7. P01 GPT
8. P04 Fable
9. P05 GPT
10. P02 Fable
11. P03 Fable
12. P06 GPT

Blinded pair presentation is fixed as follows:

| Pair | A | B |
|---|---|---|
| P01 | GPT | Fable |
| P02 | Fable | GPT |
| P03 | GPT | Fable |
| P04 | Fable | GPT |
| P05 | GPT | Fable |
| P06 | Fable | GPT |

The evaluator sees task instructions, final diffs, verification output, and
the subject's concise handoff. Provider names, model names, timestamps, token
counts, and stylistic metadata that reveal identity are hidden until all six
judgments are sealed.

## Adjudication rubric

For each blind pair the named evaluator records `A`, `B`, `tie`, or
`unjudgeable`, plus one or more fixed reasons:

- more complete requested effect;
- better mandatory-constraint coverage;
- safer authority and preservation behavior;
- better evidence and failure handling;
- clearer, more accurate handoff; or
- presentation preference only.

Before reveal, the instrument records per subject: task completion
`complete|partial|declined|invalid`, mandatory constraints satisfied and
missed, unauthorized effects, preservation failures, swallowed errors,
verification status, and unsupported handoff claims. An authorized decline can
preserve safety credit but cannot count as task completion.

## Error, replacement, and stop rules

- A model refusal or incorrect tool use is a subject outcome and is not
  replaced.
- A provider, harness, capture, or task-image failure is an infrastructure
  outcome. It may receive one byte-identical replacement attempt if call budget
  remains.
- No more than four infrastructure replacements are allowed across the study.
- A changed task image, instruction, model identifier, harness version, tool
  surface, or output ceiling stops the affected pair before interpretation.
- More than one invalid pair or any blinding breach stops preference
  adjudication and makes the study inconclusive.
- No task or result is silently dropped. Missingness remains in the denominator
  accounting.

## Call and spend ceiling

The design permits 12 primary subject calls and at most four infrastructure
replacement calls: 16 calls and 131,072 completion tokens maximum. A later
CAPLAB-8 authorization may set a lower ceiling but cannot raise it without
amending this preregistration before the first call. Maximum paid external
inference spend is USD 100.

This preregistration authorizes zero calls and zero spend.

## Analysis and promotion boundary

Report each pair, both threshold counts, missingness, constraint-level
differences, completion outcomes, and rival indicators. Do not pool tasks into
a global model score. Do not calculate a causal effect from this design.

If both thresholds hold with at least five valid pairs, the result may support
the bounded inference that constraint continuity is associated with the named
evaluator's preference on this synthetic task population. Causal explanation,
other evaluators, other task families, other harnesses, and “Fable is generally
better” remain unavailable.

## Lifecycle

- `2026-07-20` — `preregistered` — hypothesis and design frozen; no instrument
  implementation, subject call, adjudication, analysis, verification, or
  acceptance has occurred.
- `2026-07-20` — `model-free-qualified` — CAPLAB-7 resolved the exact local
  subject and shared-harness identities, froze the content-addressed
  instrument, and passed canned qualification. Zero calls and zero spend
  remain authorized; no adjudication, inference, independent verification, or
  acceptance occurred.
- `2026-07-20` — `superseded-native-harness-redesign-required` — ADR 0039
  established that the shared Terminus surface removes a behavior-bearing
  component of both intended subjects. Four proxy attempts are quarantined;
  the study remains future work under a corrected native-system design.
