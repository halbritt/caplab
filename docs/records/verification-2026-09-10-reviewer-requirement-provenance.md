# Original requirement lineage narrows the disputed newsroom claims

Read-only source investigation establishes that publisher exclusion predates
the Reddit harvester and is explicitly described as protection against
overlapping live publishers. This context was already included in the failed
assessors' original source trees. The investigation also separates the
documented optional-RSS collection behavior, provider reservation interval
and failed-refresh exit requirement.

The [requirement basis](../product/studies/reviewer-ranking-001/REQUIREMENT-BASIS.md)
records the resulting scopes and rival interpretations. It is a development
interpretation made after seeing prior outputs. The original observations,
expectations and failed results remain unchanged.

| Requirement question | Source evidence | Bounded conclusion |
| --- | --- | --- |
| What does the live-run lock protect? | `3172535` introduces the wording, duplicate-delivery comment and run/preview test. `1df624e` explicitly names live publishers; that document's blob is unchanged at `544f7e3`. | Apply the cited requirement to overlapping publishers. Harvest success alone does not demonstrate its violation or establish the safety of all other concurrency. |
| Does disabling optional RSS eliminate ordinary collection? | The reviewed README promises retained harvest collection and HTML/JSON attempts, with RSS conditional on its flag. Config comments distinguish transport from pool consumption. | The existing healthy-HTML, configured-directory failure contradicts the documented collection promise under the bounded interpretation. An explicit test for every flag combination is not a prerequisite for interpreting that promise. |
| Does the provider interval establish a global HTML rule? | README provider-state language, the reservation constant/method and its original test. | The global HTML requirement remains unresolved. Base observations independently refute first-introduced dispatch, not a possible external requirement. |
| Does permitted partial listing availability override failed-refresh behavior? | The old partial-listing test has no RSS fallback; README separately requires nonzero failed-refresh exit. | Keep listing availability and failed RSS refresh distinct. The existing mixed-failure witness remains the behavioral basis. |

## Preservation and checks

The [authorization](authorization-2026-09-10-reviewer-requirement-provenance.md)
names exactly 16 commit/path pairs at three revisions. Full selected files
remain private in
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/requirement-provenance-1`.
The [receipt](../product/studies/reviewer-ranking-001/requirement-provenance-receipt.json)
retains source commit, tree, parent, recorded commit time, Git blob, path,
byte count and SHA-256 for every file.

Every copied file matches its original Git object. The investigation verifies
all three commits are ancestors of the fixed reviewed source tip. The
publisher-specific engineering-review blob
`15eeabac9eed539a5e14db9f7119484cacb47b46` is identical at `1df624e` and
`544f7e3`; SHA-256 is
`c035256064a36768e176f620cfe5e475f1c1ef61bdf646bc513b0681dd4ee42c`.
Both frozen assessor task inventories and their retained files contain these
same reviewed-tree bytes. Git times and ancestry are provenance observations,
not an independent timestamp attestation.

The verifier also matches 66 original witness files to the hashes in the
frozen assessor input inventory. Verification reproduces byte-for-byte;
SHA-256 is
`651d697356d286dec5f757f31728a9c589a1ff22164eca757a5bf3e0958f95dd`.
The requirement-basis SHA-256 is
`a9d82e47370ee2e0bf57314710df771bed410edebf09e15639908cc0a5413c98`.

The original September 8 engineering review reports many successful checks
and completion judgments. Those claims are not accepted by this investigation.
The document is used to establish the requirement it states. Likewise, source
tests are inspected without executing them or claiming their old results as
new evidence. Existing behavioral witness verification and investigation
records are linked by hash and remain unchanged.

No source project, test suite, service or model was executed. No target
repository was modified. Validation consists of source-object and custody
checks, ancestor checks, and exact matches to prior frozen input inventories.
CAPLAB runtime code and tests are unchanged, so no new full test run is claimed.

## Decision and effect

Under ADR 0026, select the bounded interpretations in the requirement basis
for subsequent development assessments. This selects CAPLAB's treatment of
existing source requirements; it does not create product requirements in
ai-newsroom. Preserve uncertainty about broader configuration restrictions,
other concurrency rules and global HTML pacing. Reopen a conclusion when an
original governing requirement contradicts its scope.

The previous native assessment failed both representation and semantic
checks; the new provenance does not rescind that result. Its publisher-related
output failed to use relevant source context that was already available.
This supports investigating context retrieval and use before changing the
representation again. It does not establish why the model omitted that context
or guarantee that supplying a pointer will correct its judgment.

The Doctrine release gate passed for the previously retained
`pkt-cdafd666a23adaf1` requirement/attribution packet. Its measurement-dimension
and repository-precedence guidance is consistent with this investigation;
the actual requirements and authority come from the original source and
ADR 0026. No model consensus supplies ground truth.

Coverage remains 11 bounded changes, three base-only trees and 18 pending
in the unchanged 32-change sample. No case is admitted, scorer accepted or
ranking produced. The next work remains semantic validation on supported
requirement scopes and other cases, followed by the prospective reviewer
comparison. The goal remains active.
