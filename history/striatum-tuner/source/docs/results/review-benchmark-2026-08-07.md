# Review benchmark — 2026-08-07

Every tuple measured through its own declared `adapter.command`, the way the
Lane Supervisor invokes it. Endpoint lanes take the prompt on stdin and are read
from stdout; harness lanes run in an isolated per-example workspace with the
sealed dispatch bundle materialized into it, and are scored on the output id the
dispatch manifest marks required, read by name.

> **This table cannot rank reviewers, and must not be cited to raise or lower a
> declaration's `quality.classes.review`.** Its ground truth is circular: see
> "Why these numbers are descriptive only" below. What it does report soundly is
> each tuple's *disposition*, plus conformance, latency and cost. For an
> instrument that can license a quality class, see
> `docs/design/REVIEWER_QUALITY_EVAL_2026-08-07.md` and `revbench.py`.

## Why these numbers are descriptive only

`fate` labels a candidate `revised` iff a later version of its identity was
admitted afterwards (`analyze.py:46-57`). In this compiler a refusing review is
what *causes* that later version — a refused gate routes to bounded revision
planning, which builds and admits the successor. So the label is a re-encoding of
the incumbent reviewer's verdict, not an observation about the candidate: across
the 34-example sample the two coincide 32 times, accepting->final 9 of 9.

Scoring a new reviewer against it therefore measures agreement with the incumbent.
Balanced accuracy fixes this corpus's class imbalance but not its circularity.

The two populations below are constants of opposite sign, which is what makes the
circularity visible: every endpoint tuple accepts 80-97% of everything, while the
codex harness refuses 32 of 34. Codex's production reputation of 83.2% fate
agreement is what a constant refuser scores on a two-thirds-`revised` corpus.

**On `balanced acc`, and why raw agreement is kept only for locating old numbers.** The
adjudicated outcomes in this corpus are lopsided and lopsided in a way that tracks
prompt size: of the examples small enough to inline, 9 of 11 ended `final` (accept
was right), while 21 of 23 large ones ended `revised` (refuse was right). A model
that simply always accepts therefore scores 82% on the small group and 9% on the
large one, and neither figure is skill. The 2026-08-07 audit read the first of
those as "codex-class"; DeepSeek V4 Flash reproduces it exactly, at a 94% accept
rate and a balanced accuracy of 0.477 — below chance.

`balanced acc` is the mean of `caught revised` and `passed final`, so any constant
answer scores 0.50 whatever the class mix. Raw agreement is kept in the table only
so older numbers remain locatable; it must not be used to rank.

**Read the `n` column before the scores.** The held-out split's 98 examples are
not one benchmark: 64 of them inline to 8-14MB because a packet change-set review
pins an expanded base repository tree, and 23 more land between 430KB and 1MB. A
one-shot endpoint tuple is measured only on the examples that fit the context
window its own declaration states, and `n` is that count. Harness lanes keep their
declaration's spill transport and see the whole split.

Scores cover rows whose review subject was actually reachable (`subject_visible`).
The 2026-08-07 runs that did not check this are superseded, not amended: see
`docs/audits/OPENROUTER_ADAPTER_INVESTIGATION_2026-08-07.md`.

| tuple | n | balanced acc | caught revised | passed final | accept rate | json valid | raw agree | mean s | $/review |
|---|---|---|---|---|---|---|---|---|---|
| kimi-k3 | 34 | 64% | 29% | 100% | 80% | 88% | 50% | 282.7 | $0.801 |
| codex-sol-max | 34 | 59% | 100% | 18% | 6% | 100% | 74% | 453.4 | — |
| local-qwen | 28 | 53% | 6% | 100% | 96% | 93% | 38% | 206.1 | $0.000 |
| glm | 34 | 52% | 5% | 100% | 97% | 97% | 36% | 153.2 | $0.037 |
| glm | 17 | 50% | 0% | 100% | 100% | 100% | 53% | 38.9 | $0.051 |
| deepseek-v4-flash | 34 | 48% | 5% | 91% | 94% | 97% | 33% | 90.3 | $0.016 |

## Sample and exclusions

| tuple | transport | eligible | over context | subject invisible | errors |
|---|---|---|---|---|---|
| kimi-k3 | fair | 34/98 | 64 | 0 | 3 |
| codex-sol-max | declared | 34/34 | 0 | 0 | 0 |
| local-qwen | fair | 28/98 | 70 | 0 | 2 |
| glm | fair | 34/98 | 64 | 0 | 1 |
| glm | fair | 17/17 | 0 | 0 | 0 |
| deepseek-v4-flash | fair | 34/98 | 64 | 0 | 0 |

## Verdict distribution and routing

### kimi-k3

- run: `bench-kimi-k3-20260807`
- verdicts: `{'accept_with_findings': 24, 'needs_revision': 6, 'None': 4}`
- served by: `{'Fireworks': 30, 'DigitalOcean': 1}`
- mean reasoning tokens: 15,577
- total spend: $24.846 over 31 accounted rows

### codex-sol-max

- run: `bench-codex-sol-max-control-20260807`
- verdicts: `{'needs_revision': 32, 'accept': 1, 'accept_with_findings': 1}`

### local-qwen

- run: `bench-local-qwen-20260807`
- verdicts: `{'accept': 23, 'accept_with_findings': 2, 'None': 2, 'needs_revision': 1}`
- total spend: $0.000 over 28 accounted rows

### glm

- run: `bench-glm-streamlake-1m-20260807`
- verdicts: `{'accept_with_findings': 15, 'accept': 17, 'needs_revision': 1, 'None': 1}`
- served by: `{'StreamLake': 33}`
- mean reasoning tokens: 6,018
- total spend: $1.227 over 33 accounted rows

### glm

- run: `bench-glm-coreweave-262k-20260807`
- verdicts: `{'accept_with_findings': 13, 'accept': 4}`
- served by: `{'CoreWeave': 17}`
- mean reasoning tokens: 5,248
- total spend: $0.865 over 17 accounted rows

### deepseek-v4-flash

- run: `bench-deepseek-v4-flash-20260807`
- verdicts: `{'accept': 20, 'accept_with_findings': 11, 'None': 1, 'needs_revision': 2}`
- served by: `{'StreamLake': 3, 'Venice': 4, 'Parasail': 4, 'DigitalOcean': 4, 'Cloudflare': 3, 'AtlasCloud': 4, 'OpenInference': 2, 'Alibaba': 1, 'Baidu': 4, 'Mancer 2': 2, 'CoreWeave': 2, 'Fireworks': 1}`
- mean reasoning tokens: 2,216
- total spend: $0.545 over 34 accounted rows

## What a score here does and does not license

`fate_agreement` is agreement with the adjudicated outcome of the candidate the
review was about — whether the work was ultimately taken as final or revised. It
is the closest thing here to a review being *right*. `side_match` and `exact`
compare against the frontier reference review's verdict, which is a strong signal
and not ground truth.

Raising a declaration's `quality.classes.review` above `baseline` on this document
means citing it as `benchmark_ref` with `basis: measured`. A tuple whose `n` is
small has earned a small claim; say so in the declaration rather than rounding up.
