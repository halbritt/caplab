---
id: adr-0064
artifact_type: architecture-decision-record
title: Bounded native-AGY Gemini 3.7 Flash Revbench pilot
status: authorized
decision_owner: repository-owner
decision_authority: repository-owner-directive-2026-08-15-you-do-it
created: 2026-08-15
decided_at: 2026-08-15
supersedes: []
superseded_by: null
affected_contexts:
  - binding-qualification
  - revbench
related_specs: []
related_plans: []
---

# Bounded native-AGY Gemini 3.7 Flash Revbench pilot

## Context

The repository owner asked what CAPLAB could assess for Gemini 3.7 Flash
through AGY. The recommended first effect was a small matched Revbench campaign
at AGY low, medium, and high effort. The owner then directed: “you do it.” That
direction authorizes this bounded implementation and execution. It does not
delegate qualification or acceptance authority.

ADR 0039 makes the native harness part of the subject. ADR 0063 supports only
the sealed Codex Terra profile and requires reopening before adding a tuple,
provider, harness, credential method, or tool surface. AGY cannot inherit that
profile's empty-root, anonymous-credential, or provider-custody claims. AGY
1.1.13 is a dynamically linked executable that uses the owner's signed-in
global session. Its observed configuration has telemetry enabled, includes two
model-invocable skills, and permits conversation persistence. The direct
provider request identity and server-side retry behavior are unavailable.

One exploratory command combined `--disable-slash-commands` with `/model`.
That turned the slash command into a literal prompt and caused one unintended
15,999-token model call in AGY conversation
`226088f2-aa57-47ee-bf62-360b4e57d3e9`. It is preserved as preflight residue,
is not a Revbench attempt, and is excluded from every pilot denominator.

## 2026-08-15 observation correction

The first scorer implementation graded the JSON envelope's free-text
`response` field. AGY's headless structured-output contract instead identifies
`structured_output` as the parsed schema result and `json_schema` as the
enforced schema. The repository owner rejected the resulting “incomplete”
interpretation. Inspection of the retained raw envelopes confirmed that all
twelve `structured_output` values match the echoed frozen schema and carry the
correct verdict and anchor. The incomplete interpretation is withdrawn as an
apparatus defect, not a subject observation.

The repair validates the echoed schema and grades only `structured_output`.
It preserves the original observation and emits a content-identified
`observation-correction.json` that names what it supersedes. Correction uses
the existing raw custody and makes no model call. The source execution remains
immutable.

## Decision and authorization

Add these exact native subjects to a pilot contract that binds and preserves
the canonical `native-agent-systems.json` policy:

- `agy-gemini-3-7-flash-low`;
- `agy-gemini-3-7-flash-medium`; and
- `agy-gemini-3-7-flash-high`.

Every subject uses AGY 1.1.13 and executable SHA-256
`416b197e4b38c797c8661098f0af2bb4e1323ffe3c286d5e9b6408cf7d7ee920`.
The logical command pins the matching model selector and effort, plan mode,
AGY terminal sandbox, JSON output, the exact response schema, a two-minute
print timeout, and one print prompt. Slash-command disabling is omitted because
it conflicts with plan mode and caused the preflight error above.

Authorize one sequential pilot over the repository-owned two-case synthetic
integer-minimum population. Each binding receives the same two clean/mutant
pairs, for four calls per binding and twelve model calls total. There are no
retries. A persistent authorization record must bind the frozen plan, call
limit, and validity interval before the first planned call.

The pilot tool must:

1. verify the canonical subject policy, AGY bytes/version, model catalog,
   imported-plugin state, relevant configuration, and skill surface without a
   model call;
2. record a durable exclusive intent before every provider-capable process;
3. run in an empty per-attempt directory with a minimal named environment;
4. preserve bounded raw stdout, stderr, exit state, duration, conversation ID,
   and reported token usage, then grade the validated `structured_output`
   field against the echoed `json_schema`;
5. refuse replay after an intent without a durable completion;
6. stop the campaign on infrastructure failure or runtime-surface drift; and
7. score each effort separately with paired catch, false-alarm,
   discrimination, exact-anchor, and conformance metrics while keeping missing,
   subject-failure, and infrastructure-failure counts visible.

The output is a `caplab-revbench-agy-pilot-observation/1` engineering artifact.
It is deliberately not admitted to the public qualification schema catalog and
must not be called a CAPLAB Measurement. This keeps the custody and provider
limitations visible instead of weakening the existing live contract.

## Limits and stop conditions

The two-case corpus is an adapter and response-discipline shakedown. It does
not establish broad coding, repository navigation, tool use, long-context,
multimodal, performance, cost, or general review capability. Effort bindings
must not be pooled.

Stop before another model call on executable/version drift, missing model IDs,
imported plugins, relevant configuration or skill drift, expired or mismatched
authority, output limits, timeout, nonzero exit, malformed transport, or an
uncertain prior intent. A terminal schema-invalid response is a subject failure
and does not authorize a retry. A fresh replication requires a new plan and
authorization.

Execution, green checks, and favorable metrics do not qualify, select, enable,
deploy, accept, or rank any binding. A future CAPLAB Measurement requires a
separate decision that addresses AGY credential administration, conversation
custody, provider receipt semantics, runtime sealing, and replay guarantees.

## Verification

Standing model-free tests cover exact subject mapping, late-selector refusal,
command safety flags, strict AGY envelope derivation, failure classification,
paired metric partitioning, and one-shot attempt claims. The live pilot itself
is the end-to-end endpoint check. Verification does not constitute acceptance.

## Doctrine receipt

Design used advisory Pincite packet `pkt-3b142c64df04ff22` (content SHA-256
`3b142c64df04ff22a566cd991ec4cf86e9ddd708d348752b2bc833feeeb5f447`),
from corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, and retriever
`retriever-ec995ecdd083b2c8`. Repository contracts and the owner's direction,
not doctrine, supply decision and execution authority. Performance and
representative-baseline obligations remain nonmaterial because this pilot
makes no performance or population-generalization claim; the exact calls,
usage, and durations remain observations for later study design.
