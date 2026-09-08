# Restricted admission contract for prospective advisory studies

Date: 2026-09-08. Decision mechanism: primary agent under
[CAPLAB ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).
Baseline: `3282c80`.

## Authorization before execution

Create `docs/product/contracts/advisory-study-admission-v1.md`, link it from
`docs/product/README.md` and the advisory-selection study README, and complete
this record. Use the current repository contracts, admission/registration
source and read-only CAPLAB-44, 53 and 69 issue/comment snapshots as decision
provenance. Verify requirement coverage, local links and concrete failure-case
dispositions. This is a prospective specification, not an executable admission
implementation or evidence-set authorization.

After verification, append a resolution to CAPLAB-69 and mark that
specification item Done. Preserve its original description and unrelated
fields. Re-read before updating and stop on concurrent change. No external
comments or messages are authorized. This authorization expires at commit.
Remove only this task's doctrine scratch after recording receipts; retain
source and verification snapshots.

No historical artifact bodies, live CAS objects, sealed scenarios or raw
campaign outputs may be inspected, copied, admitted, rewritten or purged.
Do not invoke admission commands, storage services, model calls, harvesting,
scoring, ranking or placement. Preserve current runtime APIs, study artifacts,
expired authorizations and `docs/designs/`. No scientific acceptance, source
classification decision in Pincite, or existing evidence admission is created.

## Decision and reconciliation

CAPLAB-69's question is what a selection ADR must name, not an authorization
to import a particular source set. Select a manifest-bound restricted
admission contract with separate assertion class, access restriction and
permitted use. A content object and an assertion about its meaning are not the
same record. For a mixed replay table, computed retrieval observations and
inferred target labels retain their distinct classes even when stored together.

CAPLAB-44's synthetic redraw supersedes the real-commit sampling substrate and
its hunk cascade for the destination study. Preserve the historical branch as
a conditional contract, not a new import: replay observations and exact
commits/trees require itemized authorization; judgment JSONL remains inference
for sampling only. Current authored scenarios instead need a reproducible
construction record with a complete visibility/withholding inventory. The
generic requirement for procedural provenance survives the substrate change.

The existing `caplab.admission` surface implements only the selected Study 001
set. Qualification registration rejects historical custody through its generic
path. Advisory CAS retention verifies bytes but supplies neither source-set
authorization nor scientific eligibility. None is renamed or represented as
a general advisory-study admission service. An adopting study must supply and
verify its own authorized implementation before it can admit evidence.

Keep source classification with Pincite. CAPLAB can exclude a candidate and
record a finding without deciding that Pincite's label is false. Sending that
finding requires separate authorization. The designer's doctrine receipt
discloses exposure; an arm-invariant design input does not establish absence
of design-selection bias. No historical comment is rewritten to conceal this
qualification.

Leaving the specification open would preserve the obsolete substrate wording
and the gap between byte retention and admission. Adapting the Study 001 writer
now would require a selected source set and a wider execution contract.
Treating all stored bytes as observations would promote inferred labels into
truth. The selected specification resolves the design question while keeping
implementation, exact evidence selection and admission verification separate.


## Requirement coverage and contract challenge review

| CAPLAB-69 requirement | Resolution |
| --- | --- |
| Artifacts and assertion classes | Matrix distinguishes replay computation from inferred labels, primary artifact bytes from truth, and judgment JSONL as sampling-only inference |
| Source commit, path, hash and provenance | Per-item source inventory plus transformation input/output identities; explicit newly-authored alternative without fictitious commit |
| Construction record and withheld hunks | Ordered procedure and complete visibility inventory; exact hunk identities for a separately authorized historical branch; explicit not-applicable reason plus withheld files for authored worlds |
| Restricted admission pattern | Exact source-set authorization, restricted destinations, both copies reconciled, append-only metadata, separate verification and eligibility |
| Reporting back to Pincite | CAPLAB finding with source identities, rivals and bounded exclusion; Pincite retains classification authority; sending requires separate authorization |
| Compatibility with synthetic redraw | Old real-commit branch is conditional documentation, not the current population or a new import authorization |

Manual challenge cases were reviewed against the proposed contract:

| Case | Required disposition and reason |
| --- | --- |
| A replay row is reproducible but its target label came from an agent | Admit computed retrieval facts only under their authorized use; preserve target label as inference |
| A judgment JSONL object is hash-perfect | Custody may be verified; sampling-only restriction survives and the label cannot become oracle truth |
| A valid CAS object has no admission authorization | Stop before registration; storage availability is insufficient |
| Two source records share identical bytes but different provenance/use | Deduplicate bytes only; preserve both metadata records and their restrictions |
| An authored world has no Git commit | Record new authorship and exact inputs/bytes; no invented commit |
| A withheld oracle appears at a second subject-visible path | Fail visibility verification; listing one withheld path does not prevent alternate exposure |
| Reconstruction uses an undeclared dependency or changes bytes | Stop; any normalization must have been frozen, not invented after comparison |
| Only one of two required copies survives | Admission remains incomplete; no success based on the good copy alone |
| An interrupted write is resumed with a changed class or source hash | Require a new decision; do not reuse the old operation identity |
| Code derivation fails on a Pincite-labelled candidate | CAPLAB may exclude it; source-label falsity remains an unestablished inference |
| An author declares doctrine exposure arm-invariant | Record exposure and remaining design-bias concern; no claim that the instrument cannot be biased |
| The Study 001 admission command is available | Do not use it as an arbitrary advisory-study admission implementation |

These are reviewed specification dispositions, not executions of an admission
service or empirical acceptance checks. No runtime or test source changed.
The full runtime suite was not rerun; its prior success cannot validate a new
contract that has no general implementation yet.

## Decision-source custody

Plane is a planning projection. Its original descriptions and decision comment
remain unchanged. The following local JSON snapshots identify the exact
provenance inspected, not admitted empirical evidence:

| Snapshot | Source identity | SHA256 |
| --- | --- | --- |
| `/tmp/caplab-44-contract-current.json` | ba2f099f-bc7f-48c4-9518-2710e20bac88 | `0b3c82eb5d78438c74c164e4ee90a04d74cb22a3ab2895eeea801aa3ded893d5` |
| `/tmp/caplab-53-contract-current.json` | c25ad293-719c-44c1-b05f-6b48c3b7fa14 | `58afff91852fa8ebf3baf2dbea91a541f9c023f469c63d23f35ecc8a369abec7` |
| `/tmp/caplab-53-contract-comments.json` | ce70653f-5c28-45af-8292-490bd72326b1 | `18dfbec9f7083385b65b623ff2bfcd5dd56b320ad57050fb2aa8e7201a8b7efa` |
| `/tmp/caplab-69-contract-current.json` | 007d718b-a3de-4fc2-9e7e-14a250bed325 | `ec9e9e8528a8bc8bbad537dc82b3524785b9b48f8cadee06bb94f874b1123824` |

Repository source paths below were read at baseline `3282c80`.

| Path | SHA256 |
| --- | --- |
| `docs/domain/ubiquitous-language.md` | `a89fcdeafbfd7f4ebc0ea0f3ab6afd531c6894d5e7c517bc8fb436e316ab2375` |
| `docs/decisions/adr-0014-caplab-p5-purge-and-p6-admission.md` | `0c5b97bdd4b78237bd809a99c714f127e28a66887dfd0928c06379b5934ee567` |
| `src/caplab/admission/README.md` | `f18a55b2ea389360eb67023e1fa6997885f7c2d050d51c6391244695b47ee6cb` |
| `src/caplab/qualification/ledger.py` | `8f68a3939c3cd688d2ebd569339c8e1ce09deb387efd636b6176a9f616c4921f` |

## Advisory doctrine receipt

Release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` passed the retrieval-state
gate. Corpus `corpus-2026-07-12-a11702cc9217`; doctrine
`doctrine-f6bbb5196a3f8bf9`; retriever
`retriever-ec995ecdd083b2c8`. Final packet `pkt-15e6ffb4c184d674`,
content SHA256 `15e6ffb4c184d674700a5cf658a68d2789f9c00b9d2846780f61b74fc956a17c`.
One typed-evidence gathering pass; execute ceiling bounded by CAPLAB ADR 0026
and this document-only authorization.

Applied `universal-explicit-invariants` for class/use and custody requirements,
`universal-repository-contract-precedence` for the synthetic redraw,
`data-system-of-record-derived-state` for separating source evidence and planning
projection, and `agent-conduct-authority-bounded-action` for keeping source
selection, admission and acceptance distinct. Doctrine advised the design; its
receipt is not scientific validation or authority over Pincite.

The following omissions are nonmaterial to specifying this contract. They
remain unresolved where the implementation claim would require them:

| Concept | Remaining requirements | Scope disposition |
| --- | --- | --- |
| `data-consistency-model-selection` | application scenario and forbidden observations; datastore consistency and isolation guarantees; datastore guarantee; forbidden observation or invariant; latency and availability consequences under partition or failure | No datastore is selected and no consistency guarantee is claimed. An implementation must supply that evidence before admission execution. |
| `data-end-to-end-request-idempotence` | atomic deduplication or uniqueness enforcement; atomic durable effect boundary; external-effect and retry behavior; identity generation and propagation path; retention period and collision semantics; stable intent identity | Recovery identity and conflict requirements are specified, not implemented. Atomic enforcement and fault verification remain implementation requirements; the single planning update is re-read and verified without blind retry. |
| `data-system-of-record-derived-state` | complete mutation-path and data-authority inventory; derivation, rebuild, reconciliation, and consumer behavior during lag; measured read benefit plus write, storage, freshness, and consistency costs | The scoped mutation inventory is the new contract, record, two navigation entries and one planning item. No new derived-store implementation, lag behavior or measured read benefit is claimed. |
| `data-transaction-guarantee-verification` | application invariants and anomaly analysis; concurrency and fault tests at the relied-upon boundary; datastore guarantee and configuration; explicit application invariants; vendor or protocol guarantee for the exact configuration | No transaction guarantee is relied upon to claim actual admission. These implementation obligations remain material before executing a general admission service. |


## Verification and planning projection

The local document receipt `/tmp/caplab-69-contract-verification.json` records
32 resolved links, six requirement resolutions, twelve manual challenge cases
and the contract hash. `git diff --check` passed. Four recorded doctrine
citations classified as `valid-packet-citation`; this task's temporary packet,
evidence and citation files were removed after recording this receipt.
Source, document and tracker receipts remain.

CAPLAB-69 was re-read immediately before updating and matched the complete
pre-update snapshot. Read-back verified the exact appended description, Done
state and newly set completion time. Only `updated_at`, `description_html`,
`completed_at` and `state` changed; original text and unrelated fields were
preserved, including the preceding CAS isolation disclosure. No comments or
messages were sent.

Tracker receipts: `/tmp/caplab-69-before-contract-update.json`,
`/tmp/caplab-69-immediate-contract-update.json`,
`/tmp/caplab-69-contract-update.ndjson`,
`/tmp/caplab-69-contract-update-result.json`, and
`/tmp/caplab-69-after-contract-update.json`. The subsequent full roadmap read,
`/tmp/caplab-roadmap-after-69-contract.json`, contains 14 open items. Neither
that count nor this item's completion proves a study or the product complete.
