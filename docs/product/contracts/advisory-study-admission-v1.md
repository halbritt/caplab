# Restricted advisory-study evidence admission, version 1

Status: prospective contract selected in the
[CAPLAB-69 decision](../../records/decision-2026-09-08-caplab-69-admission-contract.md).
A future study must adopt this version and name its exact source set. This
document authorizes no source read, evidence copy, registration or study run.
It specifies requirements; it does not claim an implemented generic admission
command or establish that any existing collection passed them.

## Keep three classifications separate

**Assertion class** says whether a claim is an observation, inference,
recommendation, decision, authorization, execution, verification or acceptance,
under [CAPLAB's language](../../domain/ubiquitous-language.md).
**Access disposition** controls who may read or disclose bytes.
**Permitted use** states what a study may rely on them for. Admission preserves
these distinctions; `restricted-admission` is not a truth or eligibility label.

An artifact's existence and exact bytes can be observed without accepting its
claims. A model-authored label remains an inference after hashing, copying,
registration, repetition or agreement by another model. Split mixed documents
at the assertion level: keep the original bytes, identify the fields/rows used,
and assign each asserted meaning its class and allowed use.

| Material | Assertion class and possible use | Required limitation |
| --- | --- | --- |
| Deterministic replay rows | Observed output of a named retrieval procedure; may support retrieval facts after reproducibility verification | Target relevance labels embedded in the same table remain inferences; a hit on an invalid target does not establish relevance |
| Exact defect commit and parent tree | Primary artifact observations for a specifically authorized historical branch | The bytes do not independently prove defect presence, target bearing or repair correctness |
| Historical agent judgment JSONL | Inference; sampling-frame use only | Explicitly non-load-bearing for truth, oracle validity, eligibility or capability claims |
| Authored task/world/reference/oracle | Constructed artifact observations with procedural provenance | Author assertions of headroom, realism, bearing or correctness require their own validation; authorship is not production evidence |
| Mechanical check output | Observation of the named check on exact inputs | Supports only the checked property; a green test does not accept the world or study |
| Code, pairing or accuracy judgment | Inference or a separately authorized decision, with author and exposure | Mechanical negative witnesses do not alone establish semantic non-bearing or judge independence |
| Native capture and derived score | Capture is an observation with completeness/identity limits; score is a derivation with its own method and inputs | A score cannot repair missing capture, unauthorized execution or an unidentified Binding |
| Selection/authorization/verification record | Its named assertion type and owner | A planning state or executor's success report cannot substitute for the required authorization or independent verification |

The current advisory-selection destination uses authored scenarios. The old
replay/real-commit branch above is conditional documentation, not a selected
population or permission to inspect it. Do not import the old sampling frame
merely to populate a new manifest.

## What the selection ADR and admission authorization must name

The selection ADR identifies the study question, card and preregistration
versions, evidence classes, permitted uses and exclusions. Its admission
authorization binds a frozen manifest of exact items, not an open directory,
glob, moving branch or “latest” result. Selection alone may leave execution
unauthorized; every material admission effect needs explicit permission.

| Required field group | Content |
| --- | --- |
| Authority | CAPLAB decision owner; delegation source/scope; exact allowed reads, copies and registrations; start/expiry or consumption rule; executor and verifier; stop and recovery conditions |
| Source inventory | Stable record ID; source system/repository and full commit where applicable; exact path or immutable locator; byte length and SHA256; assertion-class map; permitted use; access disposition |
| Provenance | Origin/producer and method/version; input identities; capture time and prior exposure where relevant; transformation chain; construction-record identity for generated worlds |
| Destination | Named custody domain and restricted roots; exact object and independent-copy locators; metadata namespace; writer/reader/verifier roles; immutable manifest identity |
| Admission criteria | Expected item counts and complete membership; source/hash checks; required copy reconciliation; class/use validation; scope, visibility and construction checks; required review judgments |
| Exclusions | Unselected attempts and revisions, excluded worlds, inferred labels prohibited as truth, unavailable captures, and any forbidden training/export/publication use |
| Recovery | How to recognize a prior effect after interruption; conditions for byte-identical resumption; conflicts that require stopping; authority required for any correction or purge |

For an authored item without a source commit, record `not applicable: newly
authored` and pin the exact authored bytes, authoring record and tool/version.
Do not invent a commit or use an all-zero placeholder. For external source
material, preserve the original commit/path/hash even when a later derived
copy has a different location. Every transformation retains both input and
output identities; redacted output is a new artifact, not the original.

Content deduplication may share bytes across source records. It must preserve
each source record, class and permitted use. A manifest hash stored only beside
a mutable manifest does not witness when it was frozen; retain a protected
prior record of that identity. No required field may be silently inferred
from filenames, storage presence or a Plane status.

## Construction record for a world

Each world has one versioned construction record with these fields:

- `world_id` and construction-record version; author/builder identity, source
  authority, timestamps and prior exposure to subject outputs.
- Exact input identities: authored files or selected commit/parent, task,
  reference, oracle, guidance source and dependency/toolchain inputs.
- Ordered procedure with executable/tool versions, commands or authored
  transformations, parameters, randomness seed where used, and all external
  inputs. A citation or prose assertion of reproducibility is insufficient.
- A complete output inventory of normalized relative paths, file types,
  executable modes, byte lengths and hashes. Reject escapes, ambiguous paths
  and undeclared links rather than following them outside the sealed world.
- The exact subject-visible subset and the separately held verifier material,
  with a reason for each withheld item. No broad recursive copy is a substitute
  for this inventory. The task must not expose references, oracles, codes,
  arm metadata or withheld judgments through another path or embedded content.
- For partial historical application: source diff identity and exact retained
  and withheld hunk identities, including verifier-owned test hunks. For fully
  authored construction: `withheld_hunks: not applicable: authored world`,
  while retaining the file-level withheld inventory. An empty list must not
  falsely assert that no material was withheld.
- Output tree identity with its defined hashing method; build/check commands,
  exit status and output identities; observed nondeterminism or missing inputs;
  reconstruction comparison and discrepancies.
- Freeze witness, seal location, access/exposure record, admission disposition
  and decision locator. State separately whether evaluation outputs remain
  unobserved and whether the design has been tuned against related outputs.

A verifier reconstructs the candidate in an isolated location under explicit
authority and compares the complete inventory to the proposed world identity.
Byte differences or undeclared inputs stop admission. If reproducibility
requires normalization, freeze that procedure and retain original and normalized
identities before selecting the world; do not invent a normalization after a
failed comparison. Rebuilding matching bytes verifies construction, not
headroom, oracle truth, non-bearing, blinding or real-world representativeness.

Code/pairing validation follows the explicitly adopted
[code-authoring](behavior-code-authoring-v1.md) and
[adjacent-placebo](adjacent-placebo-selection-v1.md) contracts. Their validation
records are separate inputs to eligibility. Admission to restricted custody
may preserve a failed candidate for audit without admitting it to analysis.

## Admission sequence and failure disposition

1. Verify exact, current authority and the frozen item inventory before any
   effect. A prepared dossier is not registered evidence. Missing authority or
   an unresolved identity stops before copying or registration.
2. Verify source bytes, procedural provenance, assertion classes and permitted
   uses. Record missing, conflicting or excluded items explicitly; never shrink
   the denominator to the files that happen to be available.
3. Copy only authorized bytes into the named restricted custody destinations.
   Require create-only or verified identical reuse. A conflict stops; it never
   authorizes overwrite, deletion, automatic historical repair or reclassification.
4. Reconcile the source manifest, metadata and both named byte copies. Record
   exact hashes, counts, discrepancies, operations completed and pending work.
   A partial write or uncertain acknowledgment is not a completed admission.
5. Freeze the append-only admission record only after the required checks pass.
   A separate verifier records the defined verification result and its scope;
   an executor cannot supply an independent verdict for its own work.
6. Apply study eligibility separately, using the frozen criteria and authorized
   decision mechanism. Registration, scientific eligibility, study execution,
   capability inference and acceptance remain distinct. A later correction is
   an appended record with scope and authority, not a rewritten history.

On interruption, inspect the exact prior operation and reconcile retained
bytes before an authorized resume. Reuse only identical effects in the same
scope; changed bytes, destinations, classes or uses require a new decision.
Do not solve an incomplete admission by creating a fresh identity that hides
the partial operation. This is a required recovery contract, not a claim that
the existing runtime implements it for arbitrary advisory evidence.

## Findings and product ownership

For a failed candidate, CAPLAB records the exact source identities, check or
judgment, expected and observed result, uncertainty, rival explanations, and
the bounded study disposition. A failure to derive a code can mean an
unsuitable operationalization; it does not by itself refute Pincite's label.
Any report back to Pincite is a finding for its adjudication, sent only under
separate authorization. CAPLAB owns its study decisions; Pincite owns its
source classifications and product policy.

Retain the design author's doctrine packet identity and receipt as advisory
provenance. Keep that author's context outside subject/coder inputs. This
separation limits direct exposure; it does not prove the design is free from
selection or framing bias. Record that remaining concern and its review basis.

## Existing implementation boundary

[`caplab.admission`](../../../src/caplab/admission/README.md) is restricted to
the Study 001 selection under ADR 0014. It is not this contract's general
implementation. The generic qualification registration path refuses historical
custody, and [advisory CAS retention](../../records/repair-2026-09-08-advisory-cas-retention.md)
establishes only its bounded byte-storage property. Do not bypass those
boundaries or reinterpret their receipts as this study's admission record.

CAPLAB-69 completes the specification of what must be named. The selection
ADR, preregistration, exact manifest, authorized implementation, construction
verification, evidence admission and eligibility judgments remain separate
work. No current candidate or study is admitted by this contract.
