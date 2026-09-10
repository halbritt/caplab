# Publication evidence survives the real RSS producer boundary

The selected newsroom repair
`e4d5293910614ead24a9f7599f7d12050d5c64cf` preserves publication dates emitted
by the real `blogwatcher` binary and excludes known stale/future candidates.
Its base `00efadb0c5bdd2fc6d939793e7d372bf3c69ea73` discards those dates,
allowing the stale and future RSS entries through the original `fetch` CLI.
The repair also preserves the meaning of timezone-aware timestamps in curator
input. These outcomes come from original production functions and a local
feed, not historical test assertions or a handcrafted producer listing.

## Observations and controls

Each revision ran twice in a separate namespace and disposable home. The
installed producer scanned the same seven-entry RSS feed, stored all seven
articles and printed their actual listing. Five AI articles have known days,
one AI article is undated, and one article is a non-AI control. The two
yesterday entries have different exact feed timestamps but the same displayed
calendar date. Consumer evidence begins at that displayed precision.

| Property | Base | Repair |
| --- | --- | --- |
| Known dates survive the RSS parser | All five AI dates become unknown | All five dates retained; no invented instant |
| RSS/CLI candidate set for 24 hours | Six AI entries, including stale and future days | Four: today, both yesterday entries and undated |
| Undated article | Retained with unknown time | Same |
| Non-AI control | Excluded | Same |
| Date precision visible in original curator prompt | Known dates absent | Correct article lines show calendar date and unavailable time |
| Known future timestamp in `_drop_stale` | Retained | Excluded |
| Stale, in-window and equivalent-offset instant controls | Correctly filtered | Same |
| `07:00-07:00` displayed to curator | Rendered as `07:00Z`, seven hours early | Rendered as `07:00-07:00`, correct instant |
| Default history directory | Private home path | Same |
| Tilde XDG and explicit history paths | Literal `~` beneath working directory | Expanded beneath private home |
| Producer unread queue after preview | All seven entries unchanged | Same |

Both repetitions agree on every assessed property. The original parser,
`RssAdapter.fetch`, `_drop_stale`, `Article.as_candidate_line`, curator prompt
renderer and `cli.main` execute without patching. The CLI loads the original
configuration and runs `fetch --source rss --window 24`; no editor or Slack
endpoint is called. The original producer's before/after unread listings are
byte-identical.

The early-yesterday feed timestamp is more than 24 hours old at execution,
but the producer exposes only its date. Keeping it as a candidate is therefore
an uncertainty-preserving result, not proof that its publication instant is
inside the window. No midnight is invented. The undated article also remains
a candidate without a freshness assertion.

## Independent expected behavior

The pre-change README defines a daily news digest; `SourceAdapter.fetch`
takes a lookback window and owns filtering/normalization. The source's
displayed calendar date is inspectable evidence of publication precision.
The time-window checks use independently recorded before/after clock bounds
and inputs far from uncertain boundaries. Timestamp verification parses both
the source aware datetime and the displayed timestamp into instants: the
base's seven-hour error is arithmetic, not an interpretation of wording.

The path checks establish actual directory selection and creation under the
new documented expansion behavior. A predating promise that every configured
tilde path would expand has not been established; do not promote that
compatibility contrast into a separately adjudicated historical defect.

The real installed producer is `blogwatcher` 0.0.2. Its build metadata reports
revision `e1cfbce03e8c89155163f1cf11c6c6a24f658d81` and `vcs.modified=true`.
The executable is content-pinned, but its source is not represented as a
verified clean upstream build or the exact historically deployed binary.
This witness proves the observed producer/consumer combination. No claim is
made about every producer version or whether an editor follows the prompt.

## Execution and custody

The [authorization](authorization-2026-09-10-reviewer-publication-witness.md)
names exact historical copies, the installed producer, local feed/database,
original consumers, path checks and time limits. Raw Git blobs preserve 70
original source/configuration files across two revisions. Runtime, source and
fixture hashes were checked before and after execution. Python 3.12.3 and the
installed producer run in network-isolated namespaces with read-only source;
the only HTTP requests are local GETs for the frozen feed. The real home,
queue and newsroom services are never mounted.

Four executions completed in 3.40 seconds and retained 116 capture files,
including the disposable producer databases, feed-request receipts, original
CLI output, candidate prompts, clock bounds and process statuses. No setup
retry or criteria revision was needed. Criteria were frozen before execution;
the separate checker was subsequently written against those criteria and
preserved output.

Private custody is
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/publication-witness-1`.
The [receipt](../product/studies/reviewer-ranking-001/publication-development-receipt.json)
pins source selection, source/runtime identities, complete capture inventories
and verification. Plan SHA-256:
`d369323f22ce23d1d0f8eb1d419fdc9cd53fd8c01f8a7b2f7871518fbbd5fd65`.
Verification SHA-256:
`3e6af4c4ae78959a918aed7434c4332b5b8a53d0947c7263ef42ce6dc9857a32`.

Five new checker tests challenge wrong timezone meaning, absent dates,
future instants, ambiguous clock boundaries, invented midnight and date
evidence attached to the wrong article. All five pass.
`make check` passes: 1,531 tests in 220.20 seconds, with seven skips. All 64
publication receipt hashes and all coverage-projection receipt links were
rechecked before landing.

## What this changes for reviewer ranking

The exact sampled repair's base, tree and changed blobs match the reproduced
feasibility selection. Its base is also a separately selected change, but
these RSS observations do not verify that base commit's brief-preview change.
The new [coverage projection](../product/studies/reviewer-ranking-001/FEASIBILITY.md)
keeps that distinction: six of 32 selected changes have bounded
change-relevant behavioral evidence, two trees ran only as other cases'
bases, and 24 changes have no established behavioral witness. All remain in
the sample; none is replaced by an easier change.

The tested repair passes the named properties. That supports a bounded valid-
change control candidate, not a claim that the entire patch has no defects.
New findings still require independent investigation. Case admission,
unseen-review scoring, remaining sample coverage and held-out native
comparisons remain open. No reviewer ranking is accepted.
