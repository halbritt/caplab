---
id: spec-doctrine-robustness-laboratory
artifact_type: product-spec
title: Doctrine Robustness Laboratory
status: decided
owner: repository-maintainers
created: 2026-07-11
updated: 2026-07-12
supersedes: []
superseded_by: null
decision_owner: repository-maintainer
decision_authority: repository-owner instruction, 2026-07-11
decision_record: owner-selected-in-chat-2026-07-11
related_plans:
  - plan-doctrine-robustness-laboratory-pilot
---

# Doctrine Robustness Laboratory

Status interpretation: the repository owner selected this specification on
2026-07-11 and authorized P1 and P2. The selection uses the existing scenario
compatibility path, designates repository maintainers as human-adjudication and
acceptance owners, and keeps external-subject traces disabled. Selection and P1
authorization do not constitute repository-wide verification or acceptance.

## Decision question and scope

Should this repository add a paired mutation-testing laboratory that evaluates
whether software-engineering agents remain evidence-calibrated,
provenance-aware, and authority-bounded when doctrine or repository evidence is
subtly corrupted?

The proposed product is an evaluation layer under
`doctrine/evaluations/robustness/`. It consumes Pincite doctrine, graph,
conflict, evidence, assertion, packet, and receipt contracts through the
versioned dependency in [`pincite-dependency.json`](../../../pincite-dependency.json).
It does not replace those contracts or add another source of engineering
doctrine.

## Observations and evidence

**Observation:** The repository has replayable authority canaries that hold
evidence constant while changing authorization, and the scenario runner compares
required and forbidden assertion types and retrieval IDs. **Evidence:**
[`doctrine/evaluations/README.md`](../../../doctrine/evaluations/README.md),
[`doctrine/tools/run_scenario.py`](../../../doctrine/tools/run_scenario.py), and
the `authority-present` and `authority-withdrawn` fixtures.

**Observation:** Pincite evidence packets expose activated concepts,
obligations, conflicts, authority constraints, provenance, activation reasons,
and corpus, doctrine, retriever, and packet identities. **Evidence:** the
Pincite `doctrine/runtime/evidence-packet.schema.json` and `doctrine/bin/pincite`
at the dependency recorded in
[`pincite-dependency.json`](../../../pincite-dependency.json).

**Observation:** Assertion and decision-receipt contracts already distinguish
observation, inference, recommendation, decision, authorization, execution,
verification, and acceptance. **Evidence:**
[`ubiquitous_language.md`](../../../ubiquitous_language.md),
plus Pincite's `doctrine/runtime/assertion-artifact.schema.json` and
`doctrine/runtime/decision-receipt.schema.json`.

**Observation:** Current synthetic fixtures establish structural contract
behavior, not natural-language entailment, retrieval quality, or
engineering-judgment quality. Human-adjudicated scenarios remain a separate
acceptance gate. **Evidence:**
[`doctrine/evaluations/README.md`](../../../doctrine/evaluations/README.md) and
the pinned Pincite operationalization contract.

**Observation:** The current gold queue is candidate scaffolding rather than
accepted ground truth. **Evidence:**
[`doctrine/evaluations/gold/README.md`](../../../doctrine/evaluations/gold/README.md)
and its human-disposition artifacts.

## Inference, assumptions, rivals, and uncertainty

**Inference:** The repository can validate individual artifact shape and some
authority transitions, but it cannot yet measure whether an agent notices a
plausible, schema-valid corruption in evidence, provenance, context, or
authority. A paired mutation laboratory would address that gap while reusing
the existing knowledge and runtime models.

Assumptions:

- a useful subset of robustness properties can be expressed as relations
  between a clean control and one mutated variant;
- deterministic structural mutations and human-adjudicated semantic mutations
  can share a case/run/report spine without sharing the same oracle;
- agent outputs can be normalized into existing assertion and optional receipt
  contracts without requiring exact prose;
- canonical doctrine and source artifacts remain immutable experimental inputs.

Credible rivals and uncertainty:

- expanding the existing scenario runner might be sufficient for early
  authority tests, although its current contract lacks seed identity, mutation
  lineage, pair relations, and grading provenance;
- a human scenario suite without mutation machinery may produce useful
  judgment evidence sooner, but it provides weaker causal attribution and
  regression minimization;
- synthetic mutations may measure benchmark recognition rather than behavior
  on real repositories unless later cases retain realistic repository
  contracts and evidence;
- no accepted calibration data yet establishes which semantic oracle fields or
  aggregate measures correlate with trustworthy engineering outcomes.

## Recommendation and alternatives

**Recommendation:** Add a repository-native Doctrine Robustness Laboratory with
clean/mutated pairs, one declared mutation per case, relational oracles,
content-addressed run records, separate deterministic and human adjudication,
and matched clean controls that penalize over-refusal.

Alternatives:

1. **No change.** Continue with scenario and entailment fixtures. Prefer this if
   maintainers do not intend to compare or regression-test agent judgment.
2. **Extend only `run_scenario.py`.** Suitable for additional deterministic
   authority and retrieval fixtures, but insufficient once pair identity,
   semantic mutations, subject isolation, and human adjudication are required.
3. **Build a prose benchmark with a model judge.** Faster to demonstrate, but
   weak in provenance, replayability, and oracle independence; model output
   would remain screening evidence rather than acceptance.
4. **Mutate canonical doctrine in a worktree.** Rejected for the pilot because
   projector or repair behavior can erase the experimental condition and the
   blast radius obscures a single causal variable. The laboratory should
   materialize isolated inputs instead.
5. **Fine-tune first.** Rejected because model weights are not an inspectable
   provenance surface and the repository lacks an accepted evaluation gate.

## Product contract

### Users

- doctrine maintainers evaluating schema, graph, routing, or procedure changes;
- agent and skill authors comparing prompts, models, tools, and policies;
- human adjudicators deciding whether a semantic mutation exposes a real
  judgment failure;
- repository maintainers deciding whether an agent is ready for a larger
  authority ceiling.

### Primary use cases

1. Prove that a deterministic runtime contract rejects a declared structural
   mutation and remains stable on the clean control.
2. Determine whether an agent notices a schema-valid semantic corruption and
   selects a safe response without refusing the clean case.
3. Compare two subject versions against the same content-addressed case suite.
4. Minimize a real agent failure into a replayable regression canary.
5. Identify doctrine, mutation families, or authority transitions that lack an
   effective evaluation.

### Inputs

- a versioned robustness case referencing canonical artifact IDs and hashes;
- one controlled mutation operator and its parameters;
- a trusted subject adapter and complete subject configuration;
- clean and mutant oracle requirements kept unavailable to the subject;
- optional human adjudication for semantic outcomes.

### Outputs

- clean and mutant input identities and their exact declared delta;
- clean and mutant subject-output identities;
- criterion-level deterministic observations;
- a typed pair delta over meaningful fields rather than exact prose;
- separate mechanical and human-adjudication status;
- a content-addressed report and suite-coverage projection;
- diagnostics sufficient to reproduce or invalidate the case.

### Refusal and invalidation behavior

The laboratory must refuse or invalidate a run when:

- the clean seed is stale or fails its baseline contract;
- the mutation touches undeclared selectors or changes more than its declared
  causal variable;
- schema or cross-reference validation fails unexpectedly;
- the subject can read the oracle;
- required subject, runner, corpus, doctrine, or mutation identity is missing;
- a semantic result is represented as human-accepted without a human-owned
  adjudication record.

An invalid case is not a survived mutation, and a model-judged result is not a
human disposition.

## Conceptual model

The laboratory applies mutation testing to engineering judgment rather than to
application source code:

```text
canonical seed + case + operator
              |
        isolated compiler
          /           \
 clean input           mutant input
          \           /
          trusted subject adapter
          /           \
 clean output          mutant output
          \           /
      relational and structural grader
              |
      screening observations
              |
    human adjudication when required
              |
       report and coverage projection
```

A mutation is killed only when the subject handles the mutant appropriately
and remains useful on the matched clean control. Refusing both branches does not
demonstrate robustness.

## Architecture

### 1. Operator registry

A curated registry defines stable mutation IDs and versions, applicable
artifact kinds, allowed selectors, preconditions, postconditions, whether the
mutant should remain schema-valid, and its expected detection boundary:

- `structural`: schemas or deterministic validators can decide it;
- `metamorphic`: a deterministic relation between clean and mutant outputs can
  decide it;
- `human-semantic`: repository meaning or proportional judgment requires a
  human disposition; model judgment may only screen.

Operators target canonical IDs and structured fields rather than line numbers.
Version 1 permits one operator per case and no arbitrary patch or shell-command
DSL.

### 2. Case compiler

The compiler resolves the clean seed, verifies content identity, creates an
isolated temporary workspace, applies the declared operator, records every
changed selector and before/after value, and validates the clean and mutant
according to their declared expected validity.

The compiler never modifies canonical doctrine, generated corpus files, graph
artifacts, or human adjudications. Identical inputs produce byte-identical
compiled manifests.

### 3. Subject adapters

Trusted adapters invoke known repository tools or an external agent through a
closed protocol. Initial deterministic adapters should wrap existing tools:

- scenario runner;
- assertion validator;
- evidence-packet assembler;
- doctrine or graph validator.

An external-agent adapter is added only after deterministic case, identity, and
oracle boundaries are stable. Case files cannot contain arbitrary commands.
Network-backed subjects remain outside the default release gate.

### 4. Pair grader

The grader evaluates clean requirements, mutant requirements, cross-variant
relations, authority transitions, output containment, and neutral-control
stability. It compares selected semantic fields such as:

- activated concept, procedure, conflict, and prohibition IDs;
- evidence-obligation states and matched evidence IDs;
- assertion types and dependency lineage;
- authority ceiling and scope;
- diagnostics and refusal reasons;
- corpus, doctrine, retriever, runner, and subject identities.

Exact prose is not an oracle.

### 5. Human adjudication

Human-owned records decide semantic cases that deterministic contracts cannot
settle. Each record binds case and run identity, clean and mutant output hashes,
reviewed evidence, criterion-level rationale, uncertainty, time, and optional
supersession.

Suggested dispositions are:

- `expected-response-observed`;
- `expected-response-not-observed`;
- `equivalent-mutation`;
- `invalid-baseline`;
- `invalid-mutation`;
- `indeterminate`.

Machine tools may prepare a queue or screening observation but cannot write a
human disposition.

### 6. Catalog and coverage projection

Deterministic generated artifacts index cases and report coverage across
mutation families, detection boundaries, concepts, conflicts, source
formulations, roles, tasks, languages, risks, authority transitions, and
outcome direction. Coverage is an inventory of exercised surfaces, not proof of
quality.

## Proposed repository layout

```text
doctrine/evaluations/robustness/
  README.md
  operator.schema.json
  operators.yaml
  case.schema.json
  result.schema.json
  human-adjudications.schema.json
  cases/
  catalog.json
  coverage.json
  human-adjudications.json

doctrine/tools/
  build_robustness_suite.py
  run_robustness_case.py

tests/
  test_robustness_lab.py
```

Curated files are `operators.yaml` and case definitions. Catalog and coverage
are deterministic projections. Human adjudications are human-owned and must
never be generated or overwritten. Clean and mutated materializations are
temporary rather than checked in. External-agent outputs go to an explicitly
selected output location until retention policy is decided.

## Artifact and identity contracts

### Operator

An operator records:

- stable ID and version;
- family and target artifact kinds;
- implementation identity;
- allowed selectors;
- preconditions and postconditions;
- expected mutant validity;
- detection boundary and default oracle class.

### Case

A case records:

- stable ID, schema version, status, and rationale;
- subject adapter and contract version;
- clean seed locator, selector, schema, target hash, and container hash;
- controls such as role, task, question, evidence, authority, language, risk,
  and budget;
- operator ID, version, parameters, and expected input validity;
- clean, mutant, and pair-relative oracle requirements;
- comparison projection and expected detection boundary;
- referenced concept, formulation, edge, conflict, source-locator, and optional
  gold-candidate IDs.

### Result

A result records:

- case ID and case-content hash;
- suite, operator, runner, and subject versions;
- clean and mutant input/output hashes and schema versions;
- exact mutation-delta hash and changed selectors;
- corpus, doctrine, retriever, packet, and tool identities where applicable;
- criterion-level expected and actual values;
- typed pair delta;
- separate deterministic, screening, and human-adjudication states;
- run and result content identities.

Core identities are content-derived. Timestamps may support audit but do not
participate in deterministic case, run, or result identity.

Changed target content makes a case stale; it does not silently rebaseline.

## Mutation taxonomy

The complete product may support these families:

| Family | Examples | Primary question |
|---|---|---|
| claim state | observation promoted to diagnosis; recommendation promoted to authorization | Does the subject preserve assertion boundaries? |
| provenance | source locator swap; direct support mislabeled; provenance edge removed | Does the subject reject or qualify unsupported claims? |
| authority | authority withdrawal; narrowed scope; access presented as permission | Does the subject stop at the granted level? |
| evidence | signal substituted for evidence; forged `satisfies`; correlation presented as causation | Does the subject calibrate claims to evidence? |
| conflict | one position removed; hidden assumptions erased; contested conflict marked resolved | Does the subject preserve material disagreement? |
| temporal | withdrawn guidance made current; historical replay receives future knowledge | Does the subject respect time and supersession? |
| applicability | Python guidance applied to Go; service doctrine applied to a library | Does the subject enforce context and exclusions? |
| neutral control | irrelevant evidence or non-semantic ordering changes | Does the subject remain stable when meaning does not change? |

The pilot begins with deterministic operators already grounded in repository
contracts before attempting semantic source mutations.

## Pairing and oracle rules

1. The clean seed passes its own schema and subject-specific gates before the
   mutant is graded. Otherwise the result is `invalid-baseline`.
2. One operator controls one intended causal variable. Every changed selector
   is recorded.
3. Clean and mutant branches use identical subject and runner versions and
   identical controls except for the declared mutation.
4. Cases declare whether the mutant is expected to remain schema-valid.
   Rejecting malformed input measures contract resilience, not judgment.
5. Evidence is bound by content and provenance, not ID alone.
6. Oracles use acceptable outcome sets and relational invariants, not one
   canonical answer.
7. Hard safety rules remain separate from contestable judgment.
8. Neutral controls test false positives and over-refusal.
9. A subject never receives the oracle or hidden grading manifest.
10. Changed oracles cause reverification and retain supersession history.

## Grading model

Version 1 emits categorical case outcomes rather than one composite score:

- `invalid-baseline`;
- `invalid-mutation`;
- `killed-deterministically`;
- `survived-deterministically`;
- `neutral-control-stable`;
- `neutral-control-false-positive`;
- `pending-human`;
- `adjudicated-robust`;
- `adjudicated-not-robust`;
- `indeterminate`.

Reports preserve independent dimensions:

- schema and lineage integrity;
- clean-control utility;
- intended sensitivity;
- evidence calibration;
- conflict handling;
- authority discipline;
- provenance correctness;
- action calibration and false refusal;
- unrelated-output containment;
- human-adjudication coverage.

Authority escape, provenance escape, and stale identity remain explicit hard
failures rather than being averaged away. Aggregate thresholds remain
unaccepted until calibrated against human-adjudicated cases.

## Deterministic and human boundaries

Deterministic validation can establish:

- schema conformance, known references, and content identity;
- that an operator touched only declared selectors;
- graph provenance and routing/semantic separation invariants;
- packet prerequisite closure and safety-kernel presence;
- that a signal did not discharge an evidence obligation;
- assertion lineage and authorization-scope containment;
- repeated-run determinism and neutral-control stability.

Human adjudication is required to establish:

- whether a passage supports a paraphrased claim;
- whether a schema-valid mutation changes meaning;
- whether evidence genuinely satisfies an obligation;
- whether conflict selection fits repository conditions;
- whether abstention, escalation, no change, or action is proportionate;
- whether evaluation evidence is sufficient for product acceptance.

Model judgments may screen the human-required group but remain observations of
model output.

## Initial case families

The structural spine should begin with cases already represented by repository
contracts:

1. `authority-withdrawal`: clean authority permits decision/authorization;
   mutant authority stops at recommendation.
2. `signal-for-evidence-substitution`: a matching free-text signal must not
   satisfy an obligation; valid typed evidence may satisfy it.
3. `irrelevant-evidence-addition`: a neutral control preserves the selected
   semantic projection and authority outcome.
4. `semantic-edge-provenance-elision`: the graph validator rejects provenance
   that no longer supports the declared relationship.

The first semantic pilot then adds three paired cases in each of three
families:

- claim-state promotion;
- schema-valid provenance corruption;
- withdrawn guidance presented as current.

Those nine cases require human-reviewed oracles. Their purpose is to establish
the judgment-evaluation workflow, not a universal sample-size or quality
threshold.

## Constraints and preservation boundaries

- Canonical source, chapter, doctrine, graph, conflict, routing, and human-owned
  adjudication artifacts are immutable inputs during a run.
- Existing evidence-packet, assertion, receipt, and dependency contracts remain
  canonical payloads; laboratory metadata does not force unrelated schema
  revisions.
- Repository contracts and actual human authority continue to outrank doctrine
  and laboratory expectations.
- The default repository gate remains hermetic and network-free.
- Structural results cannot be represented as proof of engineering judgment.
- Screening output cannot become a human disposition or automatically modify
  doctrine.
- The laboratory must measure false refusal as well as unsafe action.
- No arbitrary command from a case file may execute.
- Real repository traces are not retained until redaction, privacy, and
  retention policy is accepted.

## Failure modes and mitigations

### Oracle dogmatism

An incorrect oracle can encode one contestable interpretation as truth.
Mitigations are relational expectations, acceptable outcome sets, explicit
contested fields, source and repository evidence, human rationale, uncertainty,
and supersession.

### Over-refusal

An agent could pass unsafe-action tests by refusing every branch. Mitigations
are matched clean controls, action/no-action pairs, separate false-refusal
reporting, and a requirement that escalation name a concrete evidence or
authority gap.

### Trivial structural mutants

A high mutation-kill rate can be dominated by malformed files rejected by
schemas. Reports therefore separate structural, metamorphic, and semantic
boundaries and never publish one undifferentiated score.

### Synthetic overfitting

Agents may recognize fixture wording rather than generalize. Mitigations are
paraphrase and neutral controls, hidden oracles, withheld case families,
cross-language variants, and later repository-derived cases.

### Confounded pairs

Changing several dimensions destroys causal attribution. The compiler enforces
allowed selectors and records the exact delta; ambiguous cases are invalid.

### Data leakage and retention

External subjects may expose repository or model data. The default runner is
local and hermetic; external outputs require an explicit destination and future
retention policy.

### Doctrine self-confirmation

Cases built only from doctrine may prove that doctrine agrees with itself.
Semantic cases must incorporate repository contracts, runtime evidence, or
independently reviewed source support.

## Security, privacy, and operational behavior

- Adapters are registered trusted code; cases contain data, not commands.
- Temporary workspaces are isolated and removed after compilation unless an
  explicit debugging retention option is authorized.
- Logs and reports record hashes and bounded diagnostics instead of full private
  repository content where possible.
- Secrets, credentials, environment contents, and arbitrary model prompts are
  excluded from checked-in artifacts.
- Network or external-model runs are opt-in and cannot enter `make check`.
- Human adjudication files are append-only or superseded, never generated.

## Verification and acceptance criteria

### Structural MVP

The structural MVP is technically verified when:

- case, operator, result, and adjudication schemas reject malformed and unknown
  versions;
- the compiler produces byte-identical manifests for identical inputs;
- changed seed content makes a case stale rather than silently rebaselining;
- every mutant records exactly its allowed selectors and delta hash;
- the four initial deterministic case families pass their relational oracles;
- clean-baseline failure, neutral-control false positives, and undeclared
  mutation changes are demonstrated by negative tests;
- canonical and human-owned artifacts remain unchanged;
- structural catalog and coverage checks run hermetically under `make check`.

These criteria verify the laboratory mechanism, not agent judgment.

### Judgment pilot

The judgment pilot is eligible for owner acceptance when:

- the nine semantic paired cases have human-owned oracle dispositions with
  rationale, reviewed evidence, uncertainty, and content identity;
- cases include both warranted progress and warranted stop/no-change outcomes;
- at least one external subject adapter produces complete, reproducible run
  identity without entering the default release gate;
- reports separate unsafe action, false refusal, provenance, authority,
  evidence, conflict, and clean-control behavior;
- a changed oracle or doctrine dependency causes explicit reverification;
- maintainers review residual sample, realism, and leakage risks rather than
  inferring acceptance from an aggregate score.

Acceptance belongs to the designated repository owner and is not supplied by
this specification.

## Rollout, reversal, and reopening

The implementation begins with one deterministic authority-withdrawal pair and
adds other operators only after the compiler and relational grader are stable.
Generated catalog checks join `make check` only after repeatability is proven.
External agents and semantic oracles remain optional until human governance and
retention rules exist.

The laboratory is removable without changing canonical doctrine because its
schemas, cases, tools, and reports form a separate evaluation layer. A broken
operator or case is disabled or superseded without rewriting prior results.

Reopen this design if:

- existing scenario contracts can express the required pair identity and
  oracle relations without a parallel case model;
- human adjudication demonstrates that categorical outcomes are insufficient;
- subject adapters require capabilities that cannot be safely represented by a
  closed registry;
- realistic cases cannot be constructed without retaining protected repository
  data;
- paired mutations fail to predict failures seen in real engineering work.

## Unresolved questions

1. Who owns semantic oracle adjudication and product acceptance?
2. Should existing scenario v1 inputs receive an explicit compatibility path or
   be migrated to the current scenario schema before laboratory work?
3. What external-subject command protocol is narrow enough to remain safe and
   portable?
4. Which reports may be checked in, and what redaction and retention policy
   applies to external-agent output?
5. Should semantic cases share the existing gold-adjudication surface or use a
   dedicated robustness disposition contract? This specification recommends a
   dedicated contract because the questions and verdicts differ.
6. What evidence and sample are sufficient for maintainers to accept a future
   quality threshold? No threshold is proposed here.

## Decision and authorization record

No decision selects this specification. No implementation authorization has
been granted. The related implementation plan remains a proposed delivery
artifact until a decision owner selects this design and separately authorizes a
bounded campaign.
