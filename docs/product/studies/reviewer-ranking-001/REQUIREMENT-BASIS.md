# Requirement scope for the newsroom development case

Status: source-grounded development interpretations selected by the primary
agent under ADR 0026. These interpretations follow inspection of development
reviewer and assessor outputs. They apply prospectively; neither failed
assessor challenge is rescored. They do not admit a ranking corpus or establish
general scorer validity.

The source requirements below were already present in the exact reviewed
tree, before the reviewer outputs. Their [preserved lineage and verification](../../../records/verification-2026-09-10-reviewer-requirement-provenance.md)
distinguish original source statements from the present investigator's
interpretations. Historical test source supplies specification context only;
no historical test result is newly accepted here.

## HTML collection with optional RSS

At reviewed commit `544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f`, README lines
172-183 promise collection into a retained pool and subsequent pool reads.
Lines 186-187 describe HTML/JSON listing attempts followed by RSS when the
RSS-fallback flag is enabled. Config lines 91-95 describe the fallback transport
separately from harvested-pool consumption.

For the existing controlled scenario, retain the bounded inference: a
configured harvester with working HTML listings and a usable state directory
should still attempt ordinary collection when only optional RSS is disabled.
The existing witness establishes that both harvest and a populated-pool read
instead fail before requests with a missing-directory error. The source gate
attributes that failure to the flag. This requirement interpretation rests on
the documented collection behavior and conditional RSS clause, not on the
implementation's behavior or a test invented after the review.

Do not broaden this into support for every configuration combination. The
original tests exercise healthy listings and harvested reads but do not
explicitly test this disabled-RSS combination. Absence of such a test does not
erase a documented behavioral promise. Reopen the interpretation if an
original support restriction excluding this configuration is found.

## Publisher exclusion

Commit `31725352516d10cc859c1435f3839025087e8fc7` introduced the live-run
wording and lock on September 8. Its CLI comment identifies duplicate
selection and delivery before acknowledgments as the problem. Its original
test calls `run` and `run --dry-run`, requiring the former to refuse a held
lock and allowing the latter to proceed.

Before the harvester was added, commit
`1df624ef0e8dd44ba985219cf3beaed23a1340e1` explicitly described the requirement
as preventing overlapping live publishers per data directory in
`docs/engineering-review.md:219`. That complete file is byte-identical in the
reviewed tree. The reviewed systemd guide's live-run section concerns fetching,
curating and delivering; its separate harvest section says that harvest never
publishes or sends Slack.

Use publisher exclusion as the scope of this cited requirement. A
non-publishing harvester succeeding while a publisher lock is held does not
demonstrate two publishers entering that protected activity. The observed
harvest success and publisher refusal remain distinct facts.

This resolves the scope of the publisher requirement; it does not establish
that all possible concurrent harvest operations are safe or that no separate
shared-state exclusion requirement could exist. An alleged broader requirement
needs its own original basis. Do not infer an incorrect blocker merely from
harvest success or from agreement with a prior primary-agent label.

## Provider interval and HTML pacing

The reviewed README lines 193-195 describe the 65-second interval as persisted
provider state. The corresponding source constant, transactional reservation
method and original concurrent-reservation test identify that mechanism.
They do not establish a universal interval between every HTML listing start.

The original base and change observations both show close initial HTML
dispatch. That is independent evidence against the claim that this change
first introduced the behavior. It cannot decide whether a separate global
HTML pacing requirement exists. Preserve that requirement as unresolved;
failure to establish it is not evidence of an opposite rule.

## Failed refresh versus partial listing availability

The reviewed README lines 197-203 explicitly require a failed refresh to exit
nonzero for retry. Preserve the existing witness's distinct conditions:
healthy collection, healthy empty results, successful fallback, partial RSS
refresh failure, and total failure. A successful HTML sibling does not turn
the observed failed RSS refresh into a successful refresh.

The original partial-listing test permits one blocked subreddit alongside
another successful listing, with RSS fallback absent from its configuration.
It therefore does not override the separate documented failed-refresh rule.
The existing original CLI/HTTP/state witness supplies the partial-RSS-failure
observation; the source test is context, not a new execution or truth oracle.

## Consequence for assessment

An assessment must identify the applicable requirement and preserve its scope,
then compare the reported behavior and causal claim with independent evidence.
It may not require an explicit test for every documented input, broaden a
publisher rule to all collection, or refute an unstated rule by its absence.

The reviewed-tree files, including the complete publisher-specific engineering
review, were available in both frozen assessor inputs. Their historical
lineage is newly inspected here; the publisher wording is not new evidence
added to make a failed run pass. Future validation
must test whether an assessor uses relevant available context correctly,
including on other changes. Exact quotations, valid locators and matching
these interpretations alone remain insufficient for scorer acceptance.
