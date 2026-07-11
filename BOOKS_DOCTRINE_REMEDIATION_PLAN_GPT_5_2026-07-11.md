# Books Doctrine Remediation Plan

> Execution update (2026-07-11): Sections 0–8 preserve the plan-time evidence,
> priorities, and acceptance criteria. They are historical inputs rather than a
> statement that the original failures remain present. Section 9 records the
> implemented state and the deliberately unclaimed human-calibration work.

## 0. Source review

This plan consumes the read-only review performed against committed `main` at
`f68be70485bff424c597c4ea0224930bb3684233` on 2026-07-11. The review covered
the generated corpus, source provenance, concept ontology, canonical graph,
routing index, runtime schemas, conversion pipeline, and evaluation harness.
The repository had one concurrent, uncommitted change in
`doctrine/evaluations/entailment/results.jsonl`; this campaign must preserve and
exclude that file from its write and commit scope.

The review is current at plan creation. Structural validation passed, but the
review demonstrated runtime contract failures that existing tests did not
detect.

## 1. Executive summary

- Treat the doctrine corpus as publishable reference material but the current
  packet and receipt runtime as experimental until the P0 gates pass.
- Repair authority lineage first so structurally valid artifacts cannot claim
  ungrounded recommendation, authorization, execution, or acceptance.
- Replace incompatible free-text role/task routing with controlled registries
  and prevent activation signals from satisfying evidence obligations.
- Make evidence packets question-sensitive, budgeted, content-addressed, and
  capable of preserving claim-level provenance and every activated doctrine
  layer.
- Separate generated routing adjacency from evidence-backed semantic graph
  edges and make graph projection checks detect updates and deletions.
- Make exact source identity, chapter coverage, and locator uniqueness part of
  the normal repository release gate.
- Invalidate partial-conversion caches when converter or pipeline identity
  changes.
- Strengthen entailment judgment identity and handle truncated source sections
  as insufficient context rather than negative evidence.
- Defer broad manual repair of all converted tables and links; prioritize
  defects intersecting cited doctrine sections.

## 2. Disagreements and scope decisions

The review findings were current at plan creation. This campaign does not
attempt to repair all
1,600-plus table warnings in one campaign: most do not affect cited doctrine,
and bulk conversion cleanup would introduce unrelated uncertainty. It instead
adds severity-aware quality reporting and creates an auditable queue for cited
sections.

The graph remains repository-native YAML. No graph database or specialized
infrastructure is warranted. Generated routing adjacency will be retained as a
separate projection rather than deleted because it is useful for retrieval,
but it must not masquerade as source-supported semantic doctrine.

## 3. P0 — blocking

### P0-AUTHORITY-LINEAGE

- **source:** Runtime authority and receipt review findings.
- **what:** Enforce evidence resolution and legal predecessor chains for every
  assertion and receipt status, including owner, scope, verification, and
  acceptance requirements.
- **why:** The current schemas accept ownerless acceptance and evidence-free
  recommendation or authorization.
- **touches:** `doctrine/runtime/`, `doctrine/tools/validate_assertions.py`, new
  receipt validation code, runtime tests and fixtures.
- **effort:** 1–2 days.
- **depends on:** none.
- **acceptance:** Negative fixtures for every prohibited promotion fail with a
  stable diagnostic; all valid authority canaries pass.

### P0-ROUTING-CONTRACT

- **source:** Routing vocabulary and missing-layer findings.
- **what:** Introduce canonical role/task registries and make packet assembly
  activate concepts, procedures, lenses, prohibitions, evidence obligations,
  conflicts, authority constraints, and change-type doctrine.
- **why:** Most specialist concept task tags cannot match the runtime task IDs,
  and several promised doctrine layers never reach packets.
- **touches:** `doctrine/routing-index.yaml`, routing builder, packet assembler,
  packet schema, routing tests.
- **effort:** 2–3 days.
- **depends on:** none.
- **acceptance:** Every role/task reference resolves; representative specialist
  scenarios activate the expected records; no undocumented role is rejected.

### P0-EVIDENCE-SEPARATION

- **source:** Free-text signal self-attestation finding.
- **what:** Separate activation signals from typed evidence records and preserve
  an explicit obligation-to-evidence mapping in packets.
- **why:** A caller can currently remove a proof obligation by repeating its
  wording as a signal.
- **touches:** packet assembler, evidence packet schema, runtime evidence schema,
  tests and documentation.
- **effort:** 1–2 days.
- **depends on:** P0-ROUTING-CONTRACT.
- **acceptance:** Signals can nominate doctrine but never satisfy evidence;
  only a valid evidence record can discharge a matching obligation.

### P0-PACKET-IDENTITY-AND-BUDGET

- **source:** Question-insensitivity, packet-size, and stale-identity findings.
- **what:** Use the question in explainable selection, enforce a retrieval
  budget, serialize retrieval context and activation reasons, and content-address
  doctrine and packet output.
- **why:** Current packets are oversized, invariant to the question, and can
  retain identifiers after decision-bearing doctrine changes.
- **touches:** packet assembler, routing metadata, packet schema and tests.
- **effort:** 2–3 days.
- **depends on:** P0-ROUTING-CONTRACT, P0-EVIDENCE-SEPARATION.
- **acceptance:** Distinct questions produce explainably distinct candidates;
  packets obey the requested budget; changing doctrine changes doctrine and
  packet identity; identical inputs remain byte-deterministic.

## 4. P1 — serious

### P1-GRAPH-SEMANTICS

- **source:** Graph-edge provenance and projection-drift findings.
- **what:** Separate routing adjacency from semantic edges, require auditable
  synthesis fields, and make projection checks fully deterministic.
- **why:** Most current edges cite only one endpoint and overstate semantic
  support; stale projected content passes `--check`.
- **touches:** graph schema, graph projector, routing projection, graph data and
  tests.
- **effort:** 2–4 days.
- **depends on:** none.
- **acceptance:** Semantic edges meet endpoint/rationale rules; routing links are
  explicitly non-semantic; mutations, deletions, and additions all fail check.

### P1-CONFLICT-AND-FORMULATION-PROVENANCE

- **source:** Flattened source assumptions and missing graph conflicts.
- **what:** Add position-specific conflict support and source-specific
  formulation conditions, then graph every material conflict.
- **why:** Canonical conditions are currently presented as author conditions,
  and 22 of 25 conflicts are not graph-reachable.
- **touches:** formulations, conflicts, graph edges/schema, canonicalization
  records and validation.
- **effort:** 3–5 days.
- **depends on:** P1-GRAPH-SEMANTICS.
- **acceptance:** Every conflict is graph- and route-reachable; every position
  has attributed support; synthesized mappings distinguish premises and rivals.

### P1-PROVENANCE-RELEASE-GATE

- **source:** Source hash, chapter coverage, locator ambiguity, and Make gate
  findings.
- **what:** Verify source binaries and `source.json`, compute exact chapter
  coverage, reject ambiguous locators, and include doctrine integrity in
  `make check`.
- **why:** Current provenance is intact but the normal gate does not prove it.
- **touches:** doctrine validator, release scripts, `Makefile`, schemas and tests.
- **effort:** 2–3 days.
- **depends on:** P1-GRAPH-SEMANTICS.
- **acceptance:** Tampered source, missing chapter, duplicate locator, or stale
  graph fails `make check`; the current repository passes.

### P1-CONVERTER-CACHE-FINGERPRINT

- **source:** Partial conversion cache reproduction.
- **what:** Include converter, helper, options, environment, and pipeline-stage
  identity in raw-output cache validation and provide an explicit fresh mode.
- **why:** Partial rebuilds can publish old converter output under new pipeline
  provenance.
- **touches:** `scripts/convert-books`, conversion tests and documentation.
- **effort:** 1–2 days.
- **depends on:** none.
- **acceptance:** A changed conversion fingerprint forces reconversion; unchanged
  fingerprints safely reuse validated output.

### P1-ENTAILMENT-IDENTITY

- **source:** Entailment resume-key and truncation findings.
- **what:** Key judgments on the complete target and model configuration, retain
  per-model results, verify quotes, and represent truncated context as
  insufficient.
- **why:** Changed claims or models can reuse stale judgments, and truncation can
  create false negative screening results.
- **touches:** entailment tool, result schema, summary logic and hermetic tests.
- **effort:** 1–2 days.
- **depends on:** none.
- **acceptance:** Model/prompt/claim changes produce distinct keys; truncated
  judgments cannot become unsupported verdicts without full-context review.

## 5. P2 — smell and follow-up

### P2-CORPUS-QUALITY-STATUS

- **what:** Separate conversion, structural integrity, content quality, and human
  review status; expose complete severity counts and cited-section warnings.
- **why:** A single `success` value hides material conversion debt.
- **touches:** converter validation records and generated indexes.
- **effort:** 2–3 days.
- **depends on:** P1-PROVENANCE-RELEASE-GATE.
- **acceptance:** Every book exposes quality counts and cited-section impact;
  important warnings cannot disappear after the first three entries.

### P2-BIBLIOGRAPHIC-MANIFEST

- **what:** Create one canonical title and creator-role manifest and generate
  public catalogs from it while preserving raw extracted metadata.
- **why:** Author roles and normalized titles currently disagree across files.
- **touches:** source registry, generated metadata/index builders, root README.
- **effort:** 1–2 days.
- **depends on:** P1-PROVENANCE-RELEASE-GATE.
- **acceptance:** Catalog, source registry, and generated book metadata agree on
  normalized bibliographic fields and explicit creator roles.

### P2-EVALUATION-CALIBRATION

- **what:** Build a human-adjudicated, stratified gold set for entailment,
  retrieval, authority, abstention, and no-change outcomes.
- **why:** Structural tests and a 12-record model pilot do not establish agent
  judgment quality.
- **touches:** `doctrine/evaluations/` and evaluation documentation.
- **effort:** several days plus human adjudication.
- **depends on:** all P0 items, P1-ENTAILMENT-IDENTITY.
- **acceptance:** Every source, relationship class, role, risk class, and material
  authority transition is represented with a human disposition.

## 6. Dependency map

Authority enforcement and graph semantics can proceed independently. Routing
normalization precedes evidence separation and packet budgeting. Graph semantics
precedes the combined provenance release gate. Entailment and converter cache
work are independent. Broad evaluation follows stable runtime contracts.

- P0-ROUTING-CONTRACT → P0-EVIDENCE-SEPARATION → P0-PACKET-IDENTITY-AND-BUDGET
- P1-GRAPH-SEMANTICS → P1-CONFLICT-AND-FORMULATION-PROVENANCE
- P1-GRAPH-SEMANTICS → P1-PROVENANCE-RELEASE-GATE
- P0 items + P1-ENTAILMENT-IDENTITY → P2-EVALUATION-CALIBRATION

## 7. Deferred indefinitely

- A specialized graph database: YAML plus deterministic indexes remains adequate.
- Bulk rewriting of every generated table or degraded link without citation or
  retrieval impact: retain the warning and repair by demonstrated value.
- Automatic doctrine mutation from model entailment judgments: model output
  remains screening evidence requiring adjudication.

## 8. Open questions

No question blocks the P0 or P1 implementation. Retrieval budget calibration and
human evaluation sample size remain empirical follow-ups; initial defaults must
be explicit and revisable rather than presented as validated thresholds.

## 9. Execution status — 2026-07-11

Implemented and covered by repository gates:

- all P0 authority-lineage, routing-contract, evidence-separation, packet
  identity, question sensitivity, and compact-budget work;
- P1 semantic/routing graph separation, position-specific conflict provenance,
  explicit formulation-context attribution, exact source/chapter/locator
  release gates, converter-cache identity, and entailment-identity work;
- P2 corpus-quality state separation and the canonical bibliographic manifest;
- a deterministic 99-candidate calibration queue covering every planned axis.

The calibration queue is complete as scaffolding, not as a gold set. All 99
candidates are `pending-human`; 62 require a concrete human-authored scenario
before adjudication and 37 permit direct evidence review. Human dispositions,
retrieval-quality acceptance, and empirical tuning of the 5,000-unit relative
routing budget remain deliberately unclaimed. Catalog warning intersection is
currently chapter-level because existing warning findings do not carry heading
locators; section-level attribution remains unavailable rather than inferred.
Projected formulation context now records whether conditions and caveats are
source-specific, canonical mapping/policy, or conflict-position context;
canonical applicability is never silently attributed to a source. Curated
formulations retain the source-specific contexts already mined; source-specific
conditions have not been independently populated for every generated
source-support projection, and this plan does not claim otherwise.
