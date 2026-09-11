# Dedicated editorial routing preserves the publication gate

The fixed sample's ai-newsroom change
`345e9d25caafe3e12578b0e3a27c18ef0d1c38a4` uses its configured dedicated
adversarial reviewer, including after writer fallback. Captured requests use
the dedicated credential. Failed, malformed, rejected or unavailable review
retains the draft and refuses explicit publication in the private database.
Passing review leaves the draft unpublished until that explicit action.

These observations support named routing and publication control properties.
They do not establish editorial quality, whole-change cleanliness, corpus
admission or reviewer performance. Two preparation limitations below prevent
a claim that the full authorized protocol was satisfied.

## Observed outcomes

Two revisions, fourteen conditions and two repetitions produced 56 terminal
source executions in 41.503 seconds: 48 generation/publication executions and
eight config-only executions. Semantic results agree between repetitions.

| Condition | Selected change | Base behavior |
| --- | --- | --- |
| Legacy primary or fallback writer, no dedicated route | Other configured writer route supplies adversarial review; eligible publication succeeds | Same |
| Dedicated primary or fallback writer | Only dedicated adversary is called; eligible publication succeeds | Dedicated config is ignored; legacy adversary is used |
| Dedicated family equals actual primary or fallback writer, including case/space variants | No adversary call; draft retained and publication refused | Legacy distinct-family adversary is used |
| Unknown dedicated reviewer family | No adversary call; publication refused | Legacy adversary is used |
| Unknown actual writer family | No adversary call; publication refused | Same |
| Dedicated HTTP failure, malformed response or explicit rejection | No replacement reviewer; draft retained and publication refused | Dedicated endpoint is unused; legacy review passes |
| Factual rejection | Both review calls remain independent; publication refused | Same, with legacy adversary |
| Dedicated URL-only or model-only configuration | Config loader raises its pair-completeness error; no HTTP or database effect | Unsupported dedicated config is ignored |

The base is `8ea5513fae0d4468d81e0b5c729790eb4035b077`, which predates the
feature. Its lack of dedicated routing is a feature-absence observation, not
a defect against requirements introduced by the change.

The actual writer's route performs factual review. Every invoked adversary
receives exactly the same draft and source packet as the factual critic,
without its verdict. Stored model and configured family match the captured
routes. Malformed review retains its raw response. All refused publication
attempts leave database bytes unchanged. Eligible explicit publication survives
reopen, preserving the draft, source packet and reviews.

## Requirement basis and method

The selected revision's original `docs/publication.md:63-76` requires separate
review reads, actual-writer factual review and unresolved drafts when a
suitable adversary is unavailable. Lines 78-92 specify the dedicated route,
its private credential, exclusivity and a different configured family from
the actual writer even after fallback. Original `newsroom/publication.py`
implements a separate explicit publication gate. These source requirements
and the patch were preserved before execution and before reviewer scoring.

The probe calls the original config loader, `generate_editorial`, HTTP client,
PublicationStore and `publish_editorial`. It neither replaces those functions
nor changes source clocks or validators. All provider routes point to a real
loopback HTTP server inside a network-disabled namespace. Fixed responses
supply a valid draft, passing reviews and named adverse conditions. The
experiment measures the application's handling of those responses; it does
not run a model or measure whether its critique is correct. Configured family
labels are tested as application inputs, not independently verified model
identities. No owner source packet, real credential, external provider,
production database, Slack recipient or served site is used.

## Verification, departures and custody

The [authorization](authorization-2026-09-10-reviewer-editorial-route-witness.md)
permitted one local preflight and 56 source executions. The frozen plan is
`06605291bb9070ae5a3b7f935a8d5dbfb365920d2f083933867f7b89f5b53633`.
Complete regular-file trees preserve 168 source file instances with commit,
tree, blob and content hashes. The captures contain 474 files and 147 local
HTTP exchanges, including one preflight health request. No source slot was
retried. All source/runtime identities and loaded module hashes match.

The separate read-only verifier checks the complete slot set and terminal
process records, capture hashes, original system prompts, actual route/model/
credential combinations, forced response conditions, review input separation,
stored reviews and source packets, publication outcomes and reopened SQLite.
It checks observable effects rather than treating request counts or successful
process exit as a result. Six focused checker tests reject misleading altered
copies while leaving original evidence unchanged.

The source fixture has three distinct URLs and titles but repeats one excerpt.
This misses the authorization's distinct-excerpt preparation criterion. The
captured packet still permits the original draft validator and routing paths
to execute; it cannot support source diversity, corroboration or editorial
quality. The executor also checks process failures and timeouts but does not
itself stop on a recorded unexpected endpoint. The complete captures contain
no unexpected endpoints, so that missing stop did not cause additional
observed effects. Both limitations remain explicit in verification; neither
has been silently repaired or erased through a replay.

The [receipt](../product/studies/reviewer-ranking-001/editorial-route-development-receipt.json)
pins source, methods, captures, verification and checker results. Private
custody is `/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/editorial-route-witness-1`.
No repository runtime code changed. The focused checker and read-only custody
checks passed; the full repository suite was not rerun for this private
experiment and documentation change.

## Effect on the study

Coverage becomes thirteen bounded changes, two base-only trees and seventeen
pending changes, preserving all 32 selections. Admission remains zero. The
named control properties are usable for further case development, subject to
the recorded limitations. Real editorial critique, edited/revised draft paths,
deployed-provider behavior and other patch properties remain untested. Scorer
validation, completion/advisory-burden rules, remaining case truth, comparative
design and held-out native measurements remain necessary for the ranking.
