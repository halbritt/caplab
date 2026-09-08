# Adjacent placebo selection, version 1

Status: prospective rule, selected by
[the CAPLAB-61 decision](../../records/decision-2026-09-08-caplab-61-placebo-selection.md).
It defines a reproducible candidate order and a separately witnessed semantic
eligibility decision. It does not validate any actual pairing, change an
existing study's arms, or authorize model calls.

## What the comparison can mean

An adjacent-wrong concept is plausible guidance for the task's general area,
but its decision rule is not called for by the particular defect and world.
Following it may change conduct without adding value. An unrelated random
concept can be easy to reject; rejecting it alone would leave the harder
discrimination unmeasured. These are design motivations, not observed effects
of a selected pair.

Version 1 selects **adjacent-wrong only** for this placebo rule. It does not
add a random-wrong arm. A random-wrong floor check would need its own question,
assignment, denominator, analysis and authorization; do not pool it with the
adjacent-wrong comparison or add it merely to improve an apparent score.

This concept-selection rule does not specify a treatment dose. CAPLAB-84's
shakedown description uses retrieval, injection, a real packet borrowed from
another scenario as sham, and none. That sham is not automatically an
adjacent-wrong treatment: its whole packet can contain relevant guidance.
An adopting study must explicitly choose its arm/control mapping, serving
operation, packet composition and contrasts before freeze. Changing a borrowed
packet into a selected single-concept substitution is a design amendment,
not an implementation detail. This rule does not reopen a closed ladder or
renew a historical shakedown budget.

## 1. Freeze the nomination inputs

Before subject outputs exist, the custodian records:

- the world/task/acceptance-contract and bearing-concept identities;
- the validated corpus release commit and index SHA-256;
- the source artifact path and raw
  `routing.activate_for_tasks` set for every concept;
- the pinned always-load set and any additional concept exclusions mandated
  by the study's serving operation, such as concepts already present in the
  arm-invariant packet;
- this rule version and the identities of the generator and pairing reviewer.

The category is the concept's `artifact_path` in the pinned index, such as
`concepts/performance.yaml`. It is an editorial grouping, not proof of semantic
similarity. Preserve exact original task strings as a set: no case folding,
stemming, alias expansion, embeddings, or later vocabulary substitutions.
Duplicate source concept IDs, missing category fields, unknown excluded IDs,
or malformed task lists block nomination. An absent raw task list is an empty
set and receives no overlap credit.

Task authors remain blind to retrieval terms and routing metadata when the
task-authoring contract requires it. The analyst/custodian's metadata inventory
is not part of the task or coder prompt. Pin original concept-file hashes and
source locators when materializing the chosen concept's text, under the
[code-authoring procedure](behavior-code-authoring-v1.md).

## 2. Generate and order every candidate

The bearing concept must exist and must not be an always-load concept under
this rule. Form the candidate pool from all other concepts in the **same
artifact file**, excluding the always-load set and the study's frozen
additional exclusions. Do not choose a different category after inspecting
subject behavior.

For bearing task set A and candidate task set B, use the nomination key
`J = |A intersection B| / |A union B|`. Define J as zero when the union is
empty. Sort by decreasing J, then increasing exact concept ID. Compare the
rational values by integer cross-products or an exact rational type, not
rounded displayed decimals. Record numerator and denominator for each row.
Do not use source-file order, database iteration order, a retriever's current
top-N truncation, or a random tie-break.

Retain the **entire ordered candidate list**, including zero-overlap
candidates. Zero overlap is a disclosed weak nomination signal; it is not a
semantic rejection or permission to call a category peer adjacent. There is
no automatic cross-category fallback. A category with no eligible candidate
has no nomination under this version.

This is overlap of declared task metadata, not measured co-activation on real
queries. The compiled `routes` table expands to broad task families and is
not the input to J. On the inspected release, `repository-assessment` routes
to 222 of 227 concepts. Using that common route as adjacency would obscure
the distinction the rule needs.

## 3. Validate eligibility without subject outcomes

For each candidate, the pairing reviewer records three separate findings:

| Question | Required evidence |
|---|---|
| Is it plausibly adjacent? | The shared task/domain feature that makes the advice credible here, and the specific distinction an attentive agent would need to notice. Category or J alone is insufficient. |
| Is it non-bearing? | The candidate's decision-rule conditions, whether each holds in the frozen world, why the conduct is unnecessary or misdirected for the defect, and credible rival interpretations. “Not in the reference patch” alone is insufficient. |
| Is its conduct observable and feasible? | P-codes derived from that rule; negative parent/reference witnesses and a positive enactment witness within the task's permission boundary, following the code-authoring procedure. An always-false detector is ineligible. |

The mechanical B/P orthogonality check precedes the CAPLAB-70 judgment:
P-codes must be false on parent and reference. A positive fails the proposed
pairing and requires diagnosis. Two negative results establish only those
witnesses, so they cannot settle the non-bearing judgment. Likewise,
P-conduct may be an incorrect or out-of-scope repair attempt; correctness and
scope remain separately recorded rather than used to discard that behavior.

The reviewer must not inspect subject outputs, arm effects, model rankings,
or coder agreement results to decide eligibility. Provide the necessary world,
task and concept rules; keep numerical nomination ranks and candidate order
out of the review packet where practical. Record the actual context and any
prior exposure instead of asserting independent judgment from a fresh chat.
Human-owned judgments name the human or the explicit source and scope of any
delegation; no owner spot-check is inferred from an agent's software test.

Every examined candidate receives one of three dispositions with reasons and
evidence locators: **eligible**, **ineligible**, or **unresolved**. Uncertainty
about non-bearing is unresolved. Missing witnesses are unresolved until the
check can be completed; a demonstrated contradictory witness is ineligible.
Preserve dissent and reopened judgments.

## 4. Select the first eligible candidate, with no skipped uncertainty

The custodian walks the frozen order. Skip only candidates already recorded
ineligible. Select the first eligible candidate **only if every preceding
candidate is ineligible**. An unresolved predecessor blocks selection; it
cannot be skipped to obtain a more convenient pair. For example, an order
`A, B, C` with dispositions `ineligible, eligible, unresolved` selects B;
`unresolved, eligible, ineligible` selects nothing.

If all candidates are ineligible, record **no eligible pairing**. If review
is unfinished, record **pairing unresolved**. Neither status silently removes
the world, substitutes a random placebo, expands the candidate pool, or
authorizes more review time. The study's authorized selection/amendment process
must resolve feasibility before a required world can enter a frozen design.

Once a concept is selected, inspect the **actual serving artifact**. Pin its
bytes, codebook, placement and dose, and account for every other changed
concept or packet field. A selected concept inside a larger borrowed packet
does not make that entire packet non-bearing. If the claimed contrast requires
non-bearing incremental content, all such content requires that assessment;
otherwise state the broader packet intervention and narrow the claim.

## 5. Preserve the selection receipt

Record source identities and hashes, the full candidate order, exclusions with
reasons, exact overlap numerators/denominators, every predecessor's disposition,
the chosen concept or explicit failure state, witness locators, reviewer and
decision authority, actual packet hash, and the freeze witness before subject
outputs exist. The metadata order and semantic decisions must be reproducible
from their respective records; the algorithm does not turn judgment into a
mechanical fact.

A changed corpus, category, task metadata, common packet, world, permission
boundary, or codebook requires reassessment and an explicit new frozen version.
Later contradictory evidence reopens the pairing; preserve the original
record and apply the preregistered stop/amendment rule. Never search for a
replacement using which placebo produced a favorable contrast.

## Evidence and limits of this version

The metadata-only prototype on the release named in the decision record found
227 concepts in 14 category files and six always-load concepts. All 221
remaining concepts have same-category candidates; only 154 have a candidate
with positive raw-task overlap. Thus 67 bearings rely entirely on category
membership and stable tie-breaking at nomination. They still require the same
semantic adjacency check; the rule does not claim equal placebo difficulty.

Reversing source record order produced identical rankings. A synthetic equal
ratio case used concept-ID ordering, zero overlap stayed last, and excluding
every peer produced an empty candidate list. These checks verify enumeration
and ordering only. No world-specific pairing, blinded reviewer judgment,
negative-space validation, treatment effect or independent acceptance was
established by this prototype. CAPLAB-70 retains the actual pairing judgment;
CAPLAB-71 retains difficulty and pooling parameters.
