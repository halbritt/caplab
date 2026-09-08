# Record the advisory-response study selection

Date: 2026-09-08. Baseline: `87e6351`. Primary agent under
[CAPLAB ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Create `docs/decisions/adr-0065-advisory-responsive-study-selection.md` in
ADR 0034's form. Reconcile the current CAPLAB-44 owner redraw and CAPLAB-57
named use with the prospective capability card and admission/code/coverage
contracts. Add the construct to `docs/domain/ubiquitous-language.md`; use that
repository-mandated glossary instead of introducing a second CONTEXT.md.
Link the decision from `docs/decisions/README.md`, `docs/product/README.md`,
and the advisory-selection study README. Complete this record.

These are selection and documentation effects only: zero model calls, zero
spend, no new prompt/fixture/world construction, historical evidence admission,
source copying into custody, scoring, qualification, ranking, placement, or
human-time commitment. No existing study or source artifact is frozen or
amended. Read-only planning records and the explicitly named Pincite ADR are
provenance, not admitted study evidence. Preserve unrelated `docs/designs/`,
sibling worktrees and all runtime state.

After verifying all CAPLAB-72 requirements against the concrete ADR, append
its completion pointer to CAPLAB-72 and mark that planning deliverable Done.
Preserve its original description and unrelated fields. Re-read immediately
before mutation; stop on concurrent change or an uncertain update outcome.
Read back the result. No other issue, closed ticket, comment or external
message is authorized. Keep CAPLAB-44 and the preregistration/instrument gates
open. Remove only named task doctrine scratch after recording its receipt;
retain tracker and verification receipts. Authorization expires at commit.

## Basis and selected distinction

CAPLAB-72 requires a selection ADR and a canonical construct term. Neither
exists in the current decision index/glossary for this study. The existing
`adr-0064-advisory-selection-campaign.md` selects the separate advisory binding
campaign for `review.defect_discrimination/1`; its similar name cannot supply
this missing selection. Preserve that historical record and the separately
numbered AGY pilot ADR without renaming or inferring shared authority.

The current CAPLAB-44 description records the owner's later question: the
real retrieval pipeline versus no packet, with a sham to separate context
exposure. Older ticket summaries still describe forced injection into an
actual-served baseline. Select the current owner question, identify those
different interventions explicitly, and leave the exact instrument and
preregistration unapproved. CAPLAB-57's owner decision supports a foundational
behavioral question, not a reviewer ranking or proven quality benefit.

The decision uses the established card's three clauses, distinguishes a
context sham from validated adjacent non-bearing advice, and preserves
recall as a diagnostic rather than an outcome-selected primary denominator.
It will not mark an incomplete preregistration as preregistered merely to
match the roadmap's intended destination.

## Verification against the deliverable

Created ADR 0065 in ADR 0034's selection form, added the construct to the existing
canonical glossary, and linked the decision from both indexes and the study
README. Domain-modeling uses those repository-mandated paths, not a second
glossary or ADR directory. The first combined patch failed on an unmatched
glossary hunk and created no ADR; the corrected patch applied successfully.

The selected question follows the later redraw recorded in CAPLAB-44; ADR 0026,
not the planning projection, supplies the primary agent's selection authority.
The decision does not accept an executable study. It preserves the distinct
August advisory-binding campaign and does not rename either existing ADR 0064.

`/tmp/caplab-72-selection-verification.json` records checks of all six required
sections and ten explicit requirements: construct/glossary, evidence classes
and custody, authority namespace, zero calls/spend, separate instrument
permission, declared epistemic dependence, constructed-stimulus provenance,
the owner-recorded primary comparison, no recall-selected primary denominator,
and absent preregistration. The exact rational example confirms that N=0.20,
R=0.20 and I=0.80 yield retrieval change 0 and forced-exposure change 0.60.
These are synthetic distinctions, not experimental results.

Initial link verification resolved 105 local links across the six changed
documents. The reserved preregistration file was verified absent. No runtime
or test source changed; the prior 909-test check is not rerun or presented as
validation of this study decision. This turn's verification is requirements,
source/provenance, arithmetic and document checks. No actual stimulus, world,
codebook, coder roster, pairing, blinding procedure, or budget was validated.

Planning and external-decision provenance:

| Source | SHA-256 |
|---|---|
| `/tmp/caplab-selection-44-current.json` | `32e5d84d0924492a930d5dbf5d1269f3bf7e49a539bfb463d3efea7ecb6e8718` |
| `/tmp/caplab-selection-57-comments.json` | `793619418efb82b567055b396438e7de695d6e47a0945bcffd172da4a24f95ac` |
| `/tmp/caplab-selection-72-current.json` | `9ab617a34557b1abaef7646210e08847bac598ced3db642774c2dd6be7b841e2` |
| `/home/halbritt/.local/share/pincite/release/docs/decisions/adr-0026-rubric-provisional-admission.md` | `6e5554d724ab411d9c63de53d21f4e541daf8ef7aaf9959083a3995e1b852609` |

The CAPLAB-57 owner comment is `7b366c16-a160-4e52-9867-3e44c109c311`.
The Pincite source is in release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. These locators preserve inspected
planning/authority context; they are not experimental evidence admission.

## Doctrine receipt and remaining obligations

Validated release retrieval-state gate passed. Final packet
`pkt-50604e2d058a5f6e`, SHA-256
`50604e2d058a5f6ea9163158a62a52ea3b32302fccfffc8520139a8fcadd81a4`;
corpus `corpus-2026-07-12-a11702cc9217`; doctrine
`doctrine-f6bbb5196a3f8bf9`; retriever `retriever-ec995ecdd083b2c8`;
release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
One evidence-gathering pass supplied six typed records: authority, contracts,
domain distinctions, current source, recorded planning history and verification.

Applied `universal-repository-contract-precedence` to select under CAPLAB's
own authority; `universal-evidence-before-intervention` to reconcile actual
current planning sources; `universal-explicit-invariants` to separate retrieval
from forced exposure and capability from uptake; and
`agent-conduct-authority-bounded-action` to preserve the unapproved study and
execution boundaries. The receipt's epistemic dependence is disclosed in the
ADR without asserting that a future instrument is methodologically independent.

| Remaining group | Exact unmet requirements | Classification and reason |
|---|---|---|
| `data-consistency-model-selection` | application scenario and forbidden observations; datastore consistency and isolation guarantees; datastore guarantee; forbidden observation or invariant; latency and availability consequences under partition or failure | Nonmaterial to this selection: no datastore or consistency guarantee selected; tracker mutation uses read-before/read-back and stops on uncertainty. |
| `data-system-of-record-derived-state` | derivation, rebuild, reconciliation, and consumer behavior during lag; measured read benefit plus write, storage, freshness, and consistency costs | Nonmaterial: no new cache or runtime projection is created. Plane is only a completion projection of the durable selection. |
| `implementation-risk-driven-tests` | current suite; defect reproduction when applicable | Nonmaterial: no code behavior changes or defect fix claimed; explicit document requirements and arithmetic are the present verification surface. |
| `operations-untrusted-request-handling` | authentication policy covering internal callers; interpreter boundaries enumerated with their escaping or parameterization mechanism; per-request object authorization checks; trust boundary map | Nonmaterial: no service/authentication interface is created. The sole tracker edit uses a structured JSON payload through the existing CLI, without claiming its global security guarantees. |

## Tracker execution and final disposition

Re-read CAPLAB-72 immediately before mutation and compared the complete issue
data with the fresh baseline. No concurrent change was present. The update
appended the decision pointer and moved only this deliverable from Backlog to
Done. Read-back matched the requested HTML (allowing the API's outer wrapper).
Only `description_html`, `state`, `completed_at`, and `updated_at` changed.
The original description and all unrelated fields were preserved.

Receipts: `/tmp/caplab-72-before-selection-update.json`,
`/tmp/caplab-72-immediate-selection-update.json`,
`/tmp/caplab-72-selection-update.ndjson`,
`/tmp/caplab-72-selection-update-result.json`,
`/tmp/caplab-72-after-selection-update.json`, and
`/tmp/caplab-72-selection-update-verification.json`.

Four doctrine citations classified as `valid-packet-citation`. The twelve
named `/tmp/caplab-72-doctrine-*` scratch files are removed after retaining
this receipt; planning snapshots and verification receipts remain. Final
document checks are retained in `/tmp/caplab-72-selection-final-checks.json`.

This completes the selection ADR, not study acceptance or execution. No other
ticket, historical decision, comment, or external message was changed.
