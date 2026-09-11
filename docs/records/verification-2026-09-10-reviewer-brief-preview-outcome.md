# Brief previews match live deduplication without changing history

The fixed sample's newsroom change
`00efadb0c5bdd2fc6d939793e7d372bf3c69ea73` restores preview/live agreement for
the tested brief selections. Its base prints both near-duplicate briefs while
live mode delivers only the first. The changed revision selects one in both
modes, records simulated choices in the disposable store, and leaves original
preview history byte-identical. Distinct content remains eligible.

This supplies change-relevant evidence for a case previously executed only
as another witness's base. It is a candidate clean control for the named
properties, not a whole-patch clean label or an admitted reviewer case.

## Observed outcomes

The original brief orchestration ran at the base and selected change, in
preview and live modes, for five conditions, twice each. All 40 executions
completed in 150.729 seconds. Semantic results agree between repetitions.

| Condition | Base preview / live selections | Changed preview / live selections | Other observed result |
| --- | --- | --- | --- |
| Near-identical titles at different URLs | 2 / 1 | 1 / 1 | Second brief is filtered after the first simulated selection |
| Equivalent URLs with tracking, scheme and host variants | 2 / 1 | 1 / 1 | Same normalized story is suppressed |
| Distinct content query identifiers | 2 / 2 | 2 / 2 | Both distinct stories remain eligible |
| Explicit empty curator selection | 0 / 0 | 0 / 0 | Successful skip; no invented disposition or delivery |
| Second curator request fails after first choice | 1 / 1 | 1 / 1 | Failure remains explicit; only the first choice is retained |

Every preview makes zero Slack delivery requests and leaves its original
database bytes unchanged, including the failure condition. Its temporary
snapshot is removed on context exit. Every observed live history addition
matches an acknowledged local fixture delivery. The changed preview's returned
selection list and simulated `presented` rows agree with its rendered output.
In the base, nonempty previews print choices but return an empty delivered
list and add no simulated rows. Rendered output, rather than that empty
metadata list, establishes what the operator actually sees.

Four direct checks of the original URL partition helper cover exact matching,
tracking-equivalent matching, case-sensitive content values and a different
content identifier. Both versions preserve distinct identifiers; only the
change recognizes the equivalent URL in this helper. These are bounded helper
inputs. They do not establish that every URL variation is emitted by the
normal curator or that the complete main-digest caller was executed.

## Requirements, mechanism and scope

The original README describes temporary preview history, preservation of the
next live run's candidates and feedback, and a full pipeline preview that
prints instead of posting. Its member-brief contract requires avoiding main
pick duplicates and distinguishes an empty quality-gate result from failure.
The original brief orchestration docstring says previewing whether the gate
lets a story through is the purpose of dry-run briefs. These statements and
the existing live dedup behavior predate this investigation and any reviewer
output about the case.

The original store filters normalized URL identity and recent near-duplicate
titles. The base preview does not record its first choice, so the next brief
sees older history than the corresponding live run. The patch records the
simulated choice in the already isolated preview store and normalizes its
in-memory URL sets. The observed duplicate suppression and preserved original
history follow that changed path. The observations do not rely on a fix title,
historical test success, keyword matching or an agent's label.

The witness invokes unchanged `_run_briefs`, `preview_config`, gathering,
curator transport and validation, rendering, Slack transport and SQLite.
Shared-pool Article objects are supplied as inputs. Actual arXiv requests
receive a valid empty feed, and the configured chat endpoint returns controlled
valid selections, empty selections or a second-request error. Source clocks,
rate limiting, HTTP functions, deduplication and validation are not patched.
Real HTTP bodies and SQLite files establish the effects.

These are external service fixtures in a network-disabled namespace. They
test the original application as a consumer of provider responses; they do
not measure model editorial judgment. No actual model, Slack recipient, owner
history, production service or external provider was contacted. The complete
main-digest path, final `scored` bookkeeping in its caller, upstream discovery,
feedback integration, delivery rejection and operational rollback guidance
remain outside this witness. Other defects in the selected change remain
possible and must not be suppressed by a clean label.

## Preparation, verification and custody

The [first authorization](authorization-2026-09-10-reviewer-brief-preview-witness.md)
froze the source, inputs, criteria and execution allowance. Its preflight
failed to bind private port 443 before importing newsroom source. The executor
omitted the namespace UID/GID mapping from the previously successful HTTPS
setup. The [second authorization](authorization-2026-09-10-reviewer-brief-preview-witness-2.md)
permits a new attempt using that established mapping and only the private bind
capability. All source and witness bytes remain identical. The first attempt's
failure and unused source-execution slots remain preserved and closed.

The complete regular-file trees retain 140 file instances with commit, tree,
blob and content-hash provenance. All 146 copies into the second attempt
match their source bytes. The final plan hash is
`7d2fa9fe622375b8211b37818e2a2d4d0b645aba9bcf0ccec169f229e7ac86c5`.
Forty source executions plus the successful preflight retain 362 capture
files and 169 local HTTP exchanges, including the one health request.
Loaded module hashes match the exact source snapshots. Each process has a
terminal completion receipt; no source execution was retried.

The separate verifier checks complete assignments, native process completion,
source/runtime identity, capture membership, original and active SQLite rows,
history byte hashes, actual rendered links, provider response conditions and
acknowledged delivery bodies. It compares preview/live selections independently
of the source's returned list. Failed expected properties remain explicit for
the base and are not apparatus failures.

Five checker tests protect against hiding rendered duplicates behind empty
return metadata, accepting changed preview history, overlooking preview
delivery, collapsing distinct content identifiers, and calling a fixture's
successful empty response the intended transport failure. The last test first
failed, showing a missing response-condition check. The verifier was strengthened;
all five tests pass and the outcome observations are unchanged. The original
verification, failed test and strengthened verification are all retained.

Final verification SHA-256:
`dfdb817d944d09c9a48998d73d82404b604100d8250e6e7470364adfe4c39274`.
The [receipt](../product/studies/reviewer-ranking-001/brief-preview-development-receipt.json)
pins both attempts and their source, methods, observations and checks. Private
custody is `reviewer-ranking-001/development/brief-preview-witness-2` under
`/home/halbritt/.local/share/caplab`. No repository runtime code changed; the
full repository suite was not rerun for private witness and document changes.

## Effect on the study

Coverage is now twelve bounded changes, two base-only trees and eighteen
pending changes, with all 32 fixed selections preserved. Case admission
remains zero. Repetitions estimate consistency for this one real change and
do not create additional incidents. This evidence supplies specific properties
against which future reviewer claims can be checked. Scorer generalization,
advisory-burden/completion rules, remaining case truth, comparative design and
held-out native measurements are still required for the ranking.
