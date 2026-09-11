# Proposition assessment exposes citation and requirement errors

The v2 native assessment completed and failed its frozen development challenge.
It retained all 13 finding occurrences and produced 50 separate propositions,
but five findings fail representation checks. Content inspection also finds
unsupported citation explanations and inconsistent treatment of requirements.
No scorer, reviewer score or ranking is accepted.

The [implementation](../../scripts/reviewer_proposition_assessment.py) preserves
the complete original findings and report limitations, binds propositions to
quoted source fields, and binds evidence locators to the frozen task inventory.
It keeps author stance, empirical status and duplicate identity separate.
Equivalent patch and source citations are permitted. Passing these checks
never sets semantic support, decomposition completeness or ranking eligibility
to true.

| Observation | Result and consequence |
| --- | --- |
| Original occurrences and reported judgments | All 13 survive, including the uncertain advisory concern, withdrawn report and duplicate link. |
| Representation checks | Eight findings pass; five fail. This is not semantic accuracy. |
| HTTP diagnostic finding | One quotation drops the original ellipsis; another quotes text from the wrong original field. The underlying source behavior remains inspectable. |
| Natural systemd concern | The false universal version premise and unknown host remain separate, but the required change-attribution component is omitted. |
| Exact-v244 variant | Its rejection predicate is correctly contradicted by original source, but the applicability proposition marked contradicted has only a context citation. |
| Partial-refresh finding and withdrawn variant | Both cite lines 31-42 of a 41-line observation file. Their paths exist; the ranges are invalid. |
| Semantic citation inspection | Several resolving ranges do not contain the facts their explanations claim. Literal validity would have missed these errors. |

## What the evidence supports

The original optional-RSS behavior remains reproduced: with the directory
configured, disabling the flag prevents both harvest and populated-pool reads.
The assessor supports that behavior and its source attribution but withholds
the requirement in all three occurrences. It demands an explicit contract
or test for the joint flag combination. README lines 172-203 instead describe
retained harvest storage, HTML/JSON first, and RSS only when enabled; config
lines 91-95 describe transport fallback separately from pool consumption.
Those passages support the earlier bounded requirement inference without an
exhaustive truth table of configurations. They do not establish support for
every imaginable configuration. The disagreement concerns requirement
interpretation, not a changed observation. Primary-agent expectations are not
an independently adjudicated gold standard, so expectation agreement alone
cannot settle this dispute or become an accuracy score.

The new lock variant demonstrates a different problem. Its held-lock harvest
succeeds while `run` returns 2, as the original witness records. The assessor
extends the README's live-run wording to all live collection operations. Its
cited section concerns the full fetching/curating/delivering run; the separate
harvest section explicitly excludes publication, and the original lock comment
identifies duplicate delivery as its purpose. A quotation about a live run
does not by itself establish the variant's all-collection requirement. The
earlier narrower publisher interpretation and this broader interpretation
must be reconciled against complete original requirement context before that
row can carry semantic-accuracy or false-blocker credit. The behavior of the
implementation cannot decide its own requirement.

The HTML variant correctly identifies close dispatch in both base and change,
refuting the claim that this change first introduced it. But it also marks a
global HTML pacing requirement contradicted because the cited documentation
describes provider-state pacing. That citation does not establish an opposite
requirement. The global requirement remains unresolved on this evidence.
This is the precise missing-evidence-versus-refutation distinction the frozen
contract required.

The trace assessment preserves the narrower per-capture writes, contradicts
the every-daily-run overstatement using the early return, and leaves retention
policy and long-running host impact unresolved. The HTTP assessment preserves
the source-level removal and unresolved diagnostic obligation. The systemd
assessment retains the v244 counterexample, v243 behavior and unknown target
host. These are useful component distinctions despite the failed contract.
Keyword-only text creates no defect proposition. Reversed-RSS controls refute
the reversed condition. Withdrawal and duplication remain separate from truth.

## Evidence-reference defects

The partial-refresh attribution cites patch lines 724-759 as containing the
failure-catching branch. That range ends at the branch header, before the
catch. Other supplied source establishes the mechanism, but the frozen
citation does not. The optional-RSS patch range contains the constructor gate,
while its explanation additionally claims the harvested entry points, which
occur later. The HTTP removal range does not include the added trace plumbing
claimed in the same explanation.

Four propositions cite inventory lines 1-3 for the absence of host, retention
or HTTP-body experiments. Those specific statements occur on lines 4-5.
The inspector correctly reports those ranges as existing; content inspection
finds that their explanations are unsupported by the cited range. No locator
or quotation was silently repaired, and no expected assessment was revised.

## Execution and verification

The [authorization](authorization-2026-09-10-reviewer-proposition-assessor.md)
names the new private root, exact evidence-copy effects, two authored variants,
one native attempt and its limits. The five natural findings and six prior
authored occurrences are unchanged; two additional authored occurrences form
nine documents. All are development material on the same exposed source change.
No original project or witness was executed in this assessment.

The small wrapper reuses the unchanged bounded executor. Both files, the
effective prompt/schema, fixture, support code and native package are pinned.
The original v1 experiment remains unchanged. The new verifier and semantic
expectations were frozen while the native PID was confirmed live, before its
final output was available.

Codex CLI 0.153.4 / `gpt-5.6-terra` / observed max effort completed with exit 0
in 452.973 seconds. Native stream/session/final identities agree. Seventy-six
files were captured, with receipts for 33 omitted opaque reasoning fields.
The 18 recorded commands inspect local source/evidence. No original-project
execution or external research command appears, and the recorded session has
no model-reroute event. Provider networking was shared; provider attestation
and complete kernel process/network tracing are not claimed. The native PID
is gone and the exact volatile runtime path has been removed.

Private custody:
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/proposition-assessor-1`.
The [receipt](../product/studies/reviewer-ranking-001/proposition-assessor-development-receipt.json)
pins the source-copy provenance, fixture, expected semantics, native capture,
frozen verification, content audit and repository test log. Verification
reproduces byte-for-byte. The development inspector uses the repository test
extra, with observed jsonschema 4.26.0.

The receipt covers 23 supporting files and all 76 capture entries.
Verification SHA-256:
`19391e839021d6cdab50fcb1d26b02eb7feab7e843edf568b1f6caf13f0de792`.
Content-audit SHA-256:
`5fc8bf4cf511587b8a659f6d055bcd96efd8f9654eab46419429188c78d0d7e2`.

Full `make check`: 1,571 tests in 207.875 seconds, seven skips. Five new tests
exercise stance/uncertainty preservation, equivalent source/patch locators,
evidence drift, omitted components, quote binding, duplicate/withdrawn
occurrences, and an authentic but irrelevant citation that must not establish
semantic truth. Test success is separate from the failed native challenge.

## Decision and remaining work

Under ADR 0026, retain v2 as an unaccepted development representation and
preserve this failure. Before another semantic-accuracy claim, resolve the
disputed requirement scope from complete original context and provenance.
Do not manufacture a historical requirement to force an expected result.
A future attempt may receive deterministic representation diagnostics under
a new authorization, but correcting locators alone cannot validate its
requirement judgments. Preserve the original and any corrected attempts
separately. No additional schema expansion is selected here.

The existing Doctrine packet `pkt-cdafd666a23adaf1` supports separating
measurement dimensions and preserving observations from judgments. Its
validated release gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`.
Repository requirements and ADR 0026 supply authority. Broad runtime
observability and architecture obligations are outside this development
change; semantic improvement remains unproven rather than inferred from the
new format or green tests.

Coverage stays 11 bounded changes, three base-only trees and 18 pending in the
unchanged 32-change sample, with zero admissions. Scorer validation, corpus
admission and the prospective held-out reviewer comparison remain unfinished.
The goal remains active.
