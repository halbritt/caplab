---
id: plan-doctrine-robustness-laboratory-pilot
artifact_type: implementation-plan
title: Doctrine Robustness Laboratory pilot
status: authorized
owner: repository-maintainers
created: 2026-07-11
updated: 2026-07-12
supersedes: []
superseded_by: null
source_artifacts:
  - spec-doctrine-robustness-laboratory
source_decision: owner-selected-in-chat-2026-07-11
baseline: 347a3eabf39714f01f247f6685a1af69d469be74
authorization_record: repository-owner-p1-authorization-and-delegated-p2-authorization-2026-07-11
authorized_scope:
  - doctrine/evaluations/robustness/**
  - doctrine/tools/build_robustness_suite.py
  - doctrine/tools/run_robustness_case.py
  - tests/test_robustness_lab.py
  - docs/product/specs/spec-doctrine-robustness-laboratory.md
  - docs/product/plans/plan-doctrine-robustness-laboratory-pilot.md
change_types:
  - change-feature-implementation
---

# Doctrine Robustness Laboratory pilot

Status interpretation: the repository owner selected the source specification,
authorized P1, and delegated laboratory campaign authority on 2026-07-11. The
delegate authorized P2 after P1's focused gates passed and stale abandoned graph
fragments were removed. Repository maintainers own human adjudication and
acceptance; external-subject traces remain disabled. Later checkpoints remain
separate decisions under the selected plan.

## Objective and authority boundary

Deliver a repository-native pilot that can compile a clean/mutated evaluation
pair, run trusted deterministic subjects, grade pair relations, retain complete
identity and provenance, and support separately governed semantic adjudication.

The pilot must establish three different claims without conflating them:

1. **Structural integrity:** schemas, identities, selectors, provenance, and
   authority transitions can be checked deterministically.
2. **Retrieval robustness:** a controlled input change causes the intended
   packet delta while unrelated semantic output remains stable.
3. **Judgment robustness:** an agent responds appropriately to a semantic
   mutation and remains useful on the clean control; this requires human
   adjudication.

P1 and P2 are authorized and implemented in the shared checkout. Later
checkpoints, build-gate integration, model or network execution, and
human-disposition writes remain outside the current authorization.

Required owners before execution:

- decision owner for the source specification;
- authorization owner for each implementation campaign;
- human adjudication owner for semantic oracles;
- acceptance owner for the structural MVP and judgment pilot.

These may be the same maintainer only when that authority is explicit.

## Current-state evidence and assumptions

Plan-time baseline:

- branch: `agent/evidence-governed-doctrine-remediation`;
- revision: `347a3eabf39714f01f247f6685a1af69d469be74`;
- date: 2026-07-11;
- repository gates: existing `make check` covers conversion, doctrine,
  routing, graph, provenance, and deterministic test contracts;
- existing evaluation surfaces: authority scenarios, assertion and receipt
  validation, packet routing tests, entailment screening, and a pending-human
  calibration queue.

At plan authoring, separate uncommitted adjudication work was changing
`CHANGELOG.md`, evaluation documentation, and new adjudication server/UI/test
paths. That work is excluded from this plan's evidence and write scope. The
executor must re-anchor against the then-current `HEAD`, inventory dirty paths,
and reconcile any accepted adjudication surface before selecting implementation
paths.

Assumptions to recheck:

- robustness artifacts still belong under `doctrine/evaluations/`;
- the evidence packet, assertion, receipt, and dependency schemas remain the
  canonical payloads;
- no accepted retention policy yet permits checked-in external-agent traces;
- no human-adjudicated quality threshold has been accepted;
- the existing scenario runner has not acquired pair identity or relational
  oracle support;
- default repository verification must remain hermetic and network-free.

## Preconditions for selection

Before changing implementation files, a decision owner must:

1. select, revise, or reject
   [`spec-doctrine-robustness-laboratory`](../specs/spec-doctrine-robustness-laboratory.md);
2. record whether current scenario versions receive a compatibility path or are
   migrated before reuse;
3. designate the human oracle and acceptance owner;
4. select a retention/redaction policy for any external-subject output, or keep
   that phase disabled;
5. authorize one bounded checkpoint or campaign rather than the whole roadmap
   implicitly.

If any of these choices changes the architecture materially, revise the
specification and plan before execution.

## Scope, non-goals, and change classification

### Prospective write scope

Only after the corresponding checkpoint is authorized:

```text
doctrine/evaluations/robustness/**
doctrine/tools/build_robustness_suite.py
doctrine/tools/run_robustness_case.py
tests/test_robustness_lab.py
doctrine/evaluations/README.md
doctrine/README.md
README.md
CHANGELOG.md
Makefile
```

Existing shared validators or scenario files may be changed only through a
separately named slice with regression evidence and an explicit compatibility
decision.

### Adjacent read-only surfaces

- `doctrine/runtime/*.schema.json`;
- `doctrine/tools/assemble_packet.py` and current validators;
- `doctrine/evaluations/fixtures/` and `gold/`;
- `doctrine/graph/`, `routing-index.yaml`, and related generated projections;
- `tests/test_packet_routing_contract.py`, graph-projection tests, and doctrine
  scaffolding tests;
- source chapters and canonical doctrine records used only for provenance.

### Forbidden or separately owned surfaces

- original files under `sources/` and generated chapter files under `books/`;
- canonical concepts, formulations, conflicts, graph records, and routing data
  except through a separately authorized doctrine change;
- human-owned gold or robustness adjudications through generated tooling;
- concurrent adjudication work not yet accepted into the baseline;
- external repositories, production systems, deployments, or network services;
- dependency upgrades, broad cleanup, refactoring, or UI work bundled into the
  laboratory campaign.

### Change classification

The laboratory is feature implementation. Characterization of existing
runtime contracts may precede it. Any defect found in a current validator is a
separate defect-repair slice; reorganizing existing evaluation code is a
separately justified refactoring campaign. Human calibration is evaluation and
acceptance work, not feature implementation.

## Preservation boundaries

Every checkpoint must preserve:

- canonical source, corpus, doctrine, graph, routing, conflict, and formulation
  content;
- current packet selection, authority, assertion, receipt, and dependency
  behavior except for an explicitly authorized contract revision;
- the rule that signals activate guidance but cannot satisfy evidence;
- the distinction among deterministic validation, model screening, human
  adjudication, verification, and acceptance;
- pending-human status of records not actually adjudicated by a human owner;
- complete source, operator, case, runner, subject, and result provenance;
- deterministic output for hermetic cases;
- default `make check` behavior without network or external-model access;
- user and concurrent-agent work outside each checkpoint's declared write
  scope;
- privacy and retention boundaries for repository and model output.

## Dependency map

```text
P0 select design and governance
  -> P1 contracts and strict loading
      -> P2 compiler and first paired case
          -> P3 relational grader and neutral controls
              -> P4 deterministic pilot suite and release integration
                  -> P5 judgment contract and hermetic subject protocol
                      -> P6 human-reviewed semantic pilot
                          -> P7 optional external-agent screening
                              -> P8 calibration and acceptance decision
```

P2 operator implementation and P3 report/grader internals may be developed in
parallel after P1 only when their files and tests are disjoint. P6 semantic
case drafting may begin after the schemas stabilize, but cases cannot be marked
active before the adjudication contract and owners exist.

## Checkpoint summary

| ID | Purpose | Depends on | Principal output | Completion evidence | Rollback unit |
|---|---|---|---|---|---|
| P0 | select design and governance | none | decision, authority, adjudication, and retention records | named owners and bounded first authorization | documentation/decision record |
| P1 | establish strict artifact contracts | P0 | schemas and shared strict loader | negative schema/version/reference tests | schema-and-loader commit |
| P2 | prove isolated mutation compilation | P1 | operator registry, compiler, first authority pair | deterministic delta and stale-seed tests | compiler/operator commit |
| P3 | grade relations and clean utility | P2 | result contract and pair grader | clean/mutant/neutral negative and positive tests | grader commit |
| P4 | complete deterministic pilot | P3 | four case families, catalog, coverage, hermetic gate | repeatable suite and drift check | cases/catalog-gate commits |
| P5 | define judgment subject boundary | P4 | closed subject protocol and adjudication contract | hermetic good/bad/over-refusing subjects | adapter-contract commit |
| P6 | build semantic pilot | P5 | nine human-reviewed paired cases | complete rationale, evidence, uncertainty, and balance audit | one case-family commit at a time |
| P7 | run optional external subjects | P6 | content-addressed screening runs | reproducible identity and redaction evidence | adapter/run configuration |
| P8 | decide calibration and acceptance | P7 or P6 | owner decision and residual-risk record | explicit acceptance, revision, or rejection | decision record; no code rollback implied |

## P0 — Design selection and governance

### Purpose

Prevent implementation mechanics from silently deciding oracle ownership,
scenario compatibility, trace retention, or acceptance policy.

### Work

- review the specification and alternatives;
- record the selected design and reopening conditions;
- designate decision, authorization, adjudication, and acceptance owners;
- decide scenario-version compatibility;
- decide whether external-subject traces remain ephemeral;
- authorize P1 only, unless a broader but still bounded campaign is explicit.

### Acceptance criteria

- a durable decision identifies owner and authority;
- P1 has a named write scope and stop conditions;
- unresolved governance choices are not delegated to implementation defaults.

### Stop conditions

- no owner can adjudicate semantic oracles;
- the selected architecture no longer uses paired mutations;
- concurrent evaluation work changes the artifact ownership boundary.

## P1 — Contracts and strict loading

### Purpose

Make malformed, stale, or unsupported inputs fail before semantic comparison.

### Work

- add versioned operator, case, result, and human-adjudication schemas;
- implement one offline schema registry/strict loader for laboratory artifacts;
- validate IDs, references, hashes, expected validity, and closed subject
  adapter IDs;
- decide and test current scenario v1/v2 behavior rather than inheriting
  accidental compatibility;
- add schema inventory and negative tests without yet implementing mutations.

### Acceptance criteria

- missing required fields, unexpected fields, unsupported versions, unresolved
  references, invalid evidence, and unknown adapters fail with stable
  diagnostics;
- all schema references resolve offline;
- human-adjudication files cannot be populated through a generated build path;
- existing accepted tests remain unchanged except where a separately recorded
  compatibility decision requires migration.

### Verification

- focused schema/loader unit tests;
- portable-schema inventory tests;
- existing doctrine scaffolding and authority-canary tests;
- `make check` before and after the slice.

### Stop conditions

- current scenario compatibility requirements remain unknown;
- schema design duplicates or weakens an existing runtime contract;
- the loader would need network resolution.

## P2 — Compiler and first paired case

### Purpose

Prove that one declared mutation can be applied in isolation without changing
canonical inputs or reimplementing the subject.

### Work

- create the curated operator registry;
- implement a pure case resolver and temporary-workspace compiler;
- bind seed target and container hashes;
- record allowed selectors, before/after values, and mutation-delta identity;
- add `authority-withdrawal` using the existing authority canary behavior;
- invoke the canonical scenario runner through a trusted adapter.

### Acceptance criteria

- identical case inputs produce byte-identical compiled manifests;
- changed seed content yields a stale-case diagnostic;
- the clean and mutant differ only at declared selectors;
- the clean branch passes its baseline before mutant grading;
- the mutant forbids decision and later authority stages while retaining an
  admissible recommendation;
- canonical fixtures and doctrine remain byte-identical after the run.

### Verification

- repeated compilation test;
- undeclared-selector negative test;
- stale-seed test;
- invalid-baseline test;
- canonical-tree before/after hash comparison;
- full existing check.

### Stop conditions

- the implementation copies scenario-runner or assertion logic instead of
  invoking canonical code;
- temporary materialization cannot be isolated from projector/write behavior;
- more than one causal variable must change to express authority withdrawal.

## P3 — Relational grader and neutral controls

### Purpose

Make the laboratory judge relations and clean-case utility rather than exact
output snapshots.

### Work

- implement the result artifact and content identity;
- compare selected assertion, authority, evidence, obligation, provenance, and
  diagnostic fields;
- report clean, mutant, and pair-relative criteria independently;
- add `signal-for-evidence-substitution` as an intended-sensitivity case;
- add `irrelevant-evidence-addition` as a neutral control;
- represent invalid, killed, survived, stable-neutral, false-positive, pending,
  and indeterminate outcomes categorically.

### Acceptance criteria

- typed evidence changes the named obligation while a matching signal does
  not;
- the neutral control preserves the declared semantic projection and authority
  result;
- packet identity changes are distinguished from semantic projection changes;
- a subject that refuses both clean and mutant cannot receive a robust result;
- criteria expose expected, actual, status, and detection boundary.

### Verification

- canned good, unsafe, and over-refusing outputs;
- semantic-projection versus content-identity tests;
- result identity sensitivity and deterministic serialization tests;
- existing packet-routing contract suite.

### Stop conditions

- grading requires exact prose;
- a single aggregate score hides a hard authority or provenance escape;
- neutral-control identity changes are misreported as semantic failures.

## P4 — Deterministic pilot suite and release integration

### Purpose

Establish a maintainable case catalog and structural coverage gate without
adding model or network nondeterminism.

### Work

- add `semantic-edge-provenance-elision` using an isolated graph-validator
  adapter;
- generate content-addressed catalog and coverage projections from curated
  operators and cases;
- implement `build_robustness_suite.py --check`;
- add structural robustness validation to `doctrine-check` only after repeated
  determinism is demonstrated;
- document deterministic versus semantic claim boundaries.

### Acceptance criteria

- all four initial case families pass their declared relations;
- catalog and coverage detect additions, deletions, stale identities, and
  unindexed cases;
- generated tooling never rewrites curated cases or human adjudications;
- `make check` remains hermetic and network-free;
- coverage reports inventory surfaces without calling them accepted quality.

### Verification

- focused robustness suite;
- catalog/coverage freshness tests;
- graph mutation containment tests;
- `make check` twice with no diff;
- `git diff --check` and explicit generated/human-owned path audit.

### Stop conditions

- graph validation requires writing or repairing the mutated tree;
- the new gate invokes an external subject;
- case generation begins rewriting substantive case prose.

## P5 — Judgment contract and hermetic subject protocol

### Purpose

Prepare semantic evaluation without making an LLM or one exact response the
oracle.

### Work

- define acceptable disposition sets, any-of requirements, contested fields,
  uncertainty, and reopening conditions;
- define a closed external-subject input/output protocol using existing
  assertion and optional receipt contracts;
- keep stimulus and oracle in separately resolved artifacts unavailable to the
  subject;
- add hermetic subjects representing appropriate progress, unsafe promotion,
  unsupported abstention, and incomplete output;
- establish dedicated human adjudication records or reconcile an accepted
  shared adjudication service without weakening ownership.

### Acceptance criteria

- no exact-prose oracle is required;
- subjects cannot resolve oracle paths through their input;
- safe progress is defined relative to role authority rather than equated with
  execution;
- unsupported generic calls for more evidence fail adequately evidenced clean
  cases;
- machine tooling cannot write a human verdict;
- changed oracle identity marks prior runs for reverification.

### Stop conditions

- a model is required for default tests;
- human and machine judgments share an indistinguishable field;
- the outcome vocabulary cannot represent contested or indeterminate cases.

## P6 — Human-reviewed semantic pilot

### Purpose

Test actual engineering-judgment behavior without pretending that nine cases
establish a universal quality threshold.

### Work

Create three clean/mutant pairs in each family:

1. claim-state promotion;
2. schema-valid provenance corruption;
3. withdrawn guidance presented as current.

For each case:

- bind exact doctrine, graph, source, repository-contract, and case identity;
- include a matched clean control;
- document acceptable outcomes, hard prohibitions, rivals, uncertainty, and
  reopening conditions;
- obtain a human-owned adjudication before marking the case active;
- include both warranted progress and warranted stop/no-change outcomes across
  the pilot;
- retain one case family as a holdout when comparing subject revisions.

### Acceptance criteria

- all cases have complete direct-read evidence and human rationale;
- human disagreement remains `indeterminate` or contested rather than averaged;
- action/no-action and clean/mutant coverage is explicitly reported;
- no case leaks its oracle to the subject;
- no automated quality threshold or doctrine rewrite follows from the pilot.

### Stop conditions

- a defensible clean control cannot be written;
- a mutation changes several causal variables;
- human adjudicators cannot distinguish equivalent from meaningful mutations;
- case realism requires protected repository data without a retention policy.

## P7 — Optional external-agent screening

### Purpose

Run real agent/model subjects while keeping nondeterminism and private output
outside the release gate.

### Work

- implement one opt-in trusted adapter;
- bind prompt, requested and served model, endpoint, sampler, tool, packet,
  doctrine, runner, and case identities;
- require an explicit output directory and redaction policy;
- record model outcomes as screening observations awaiting human adjudication;
- compare subject versions by dimension and case, never through one leaderboard
  score.

### Acceptance criteria

- identical configuration yields identical run identity even when prose varies;
- secrets and uncontrolled environment data are excluded from reports;
- network failure cannot affect `make check`;
- model output cannot alter canonical doctrine or human dispositions;
- a run can be reproduced or declared irreproducible from its recorded inputs.

### Stop conditions

- output retention or redaction ownership is unresolved;
- the adapter permits arbitrary case commands;
- served-model identity cannot be established;
- model screening is presented as verification or acceptance.

## P8 — Calibration and acceptance decision

### Purpose

Let the authorized owner decide what the pilot evidence supports.

### Work

- audit case coverage, oracle disagreements, false refusals, hard escapes,
  neutral stability, model variance, leakage, and sample limitations;
- compare continuation, revision, expansion, and no-change alternatives;
- decide whether to accept the structural mechanism, the semantic pilot, both,
  or neither;
- record conditions for any future quality thresholds or production gates.

### Acceptance criteria

- the decision identifies owner, authority, evidence, alternatives, residual
  risk, and reopening conditions;
- structural verification is not presented as judgment acceptance;
- no scalar threshold is adopted without human calibration evidence;
- later expansion is a new authorized campaign.

## Verification matrix

| Claim | Evidence | Default gate? | Acceptance owner |
|---|---|---:|---|
| schemas and references are valid | hermetic negative/positive tests | yes | technical verifier |
| compiler is deterministic | repeated compile and byte comparison | yes | technical verifier |
| mutation is contained | selector and delta audit | yes | technical verifier |
| canonical inputs remain unchanged | before/after hashes and clean diff | yes | technical verifier |
| subject adapter obeys protocol | hermetic canned subjects | yes | technical verifier |
| external model produced output | content-addressed screening record | no | none; observation only |
| semantic mutation is meaningful | human adjudication with evidence | no | adjudication owner |
| agent response is proportionate | human criterion-level disposition | no | adjudication owner |
| pilot is sufficient for intended use | decision record over verified evidence | no | product acceptance owner |

Prospective focused commands after implementation:

```bash
python3 -m unittest tests.test_robustness_lab -v
python3 doctrine/tools/build_robustness_suite.py --check
python3 doctrine/tools/run_robustness_case.py \
  doctrine/evaluations/robustness/cases/authority-withdrawal/case.json
make check
```

These commands are planned interfaces, not current capabilities.

## Risks and mitigations

| Risk | Early signal | Mitigation | Residual risk |
|---|---|---|---|
| oracle dogmatism | legitimate alternative responses fail | relational sets, contested fields, human rationale, supersession | adjudicators may still share assumptions |
| over-refusal | clean and mutant branches both stop | matched controls, positive-progress cases, separate false-refusal dimension | cautious prose may conceal non-progress |
| trivial mutation inflation | most kills occur at schema parsing | stratify structural/metamorphic/semantic results | structural metrics may still dominate attention |
| synthetic overfitting | performance collapses on paraphrases or holdouts | neutral/paraphrase controls and holdout families | synthetic tasks may remain unrepresentative |
| confounded pair | undeclared output changes appear | one operator, allowed selectors, exact delta | semantic changes can have unavoidable downstream effects |
| stale provenance | target hash changes without case review | stale-case refusal and dependency reverification | frequent doctrine changes may create maintenance cost |
| hidden oracle leakage | subject output quotes oracle-only material | separate resolution roots and leakage tests | model training data may contain public cases |
| model nondeterminism | repeated runs disagree | bind configuration and report distributions by dimension | exact replay may remain impossible |
| private trace leakage | reports contain repository or environment content | explicit output location, redaction, no tracked traces by default | human review remains necessary |
| concurrent-work collision | dirty shared files enter a slice | re-anchor, disjoint write scope, stop on overlap | serialized integration may delay work |

## Global stop, escalation, and rollback conditions

Stop the active checkpoint when:

- authority, decision, or acceptance ownership is missing;
- target revision or dirty paths change materially and cannot be re-anchored;
- a mutation touches undeclared selectors or several causal variables;
- the clean control fails;
- the subject can access the oracle;
- a default gate would require network or model execution;
- machine output would overwrite human-owned data;
- a result crosses an unauthorized assertion or execution boundary;
- real repository traces would be retained without accepted privacy policy;
- the implementation begins duplicating canonical doctrine or routing logic.

Return to the last independently green checkpoint. Retain a partial slice only
when it remains useful, hermetic, documented, and releasable. Otherwise revert
the campaign-owned unit without touching concurrent or user work. Escalate the
exact compatibility, oracle, authority, privacy, or product decision rather
than debugging forward through an invalid experimental state.

## Deferred work

- a general JSON Patch or arbitrary mutation DSL;
- chained or automatically generated semantic mutations;
- automatic execution against user or production repositories;
- model fine-tuning or automatic prompt promotion;
- automatic updates to canonical doctrine, graph confidence, or human
  dispositions;
- a public leaderboard or composite robustness score;
- a new database, graph service, or UI unless accepted workflow evidence shows
  existing repository-native files are inadequate;
- completing all pending gold candidates as a prerequisite for the structural
  MVP;
- real-repository outcome traces before retention and redaction policy;
- production enforcement, proof-carrying change permits, the conflict
  experiment broker, and the repository doctrine control plane.

## Execution, verification, and acceptance records

None. This plan records no execution, verification, or acceptance. Future
records must link exact revisions, case and suite identities, verification
outputs, decision owner, authority source, residual risk, and reopening
conditions.

## Status log

- **2026-07-11 — proposed:** Created from the Doctrine Robustness Laboratory
  specification and a read-only review of current evaluation, graph,
  provenance, packet, authority, test, and release-gate surfaces. No
  implementation authority was inferred or exercised.
