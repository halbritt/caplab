# Three tuples on the planning board, one pinned instrument, and why none of it is a ranking

- Date: 2026-09-02. Additions to the P2b board of
  `report-2026-08-27-planning-p2b.md` (Arm 1 of `planning-constructs-v1.md`).
- Principal direction, verbatim: "probably you should sweep fable 5.1 on
  high, yes that's a new tuple"; "GLM-5.3-flash needs testing as well";
  "Gemini-3.8-flash should get a sweep as well"; and, on seeing the board,
  "I'm suspicious of the planning ranking. Why would Terra perform best?"
  followed by "You just basically explained why the planning eval was
  bullshit." The Principal is right about the ordering, and this record
  says so first.
- Same draw as P2b: seed `20260827`, 24 tasks, one per step pass, `plan-v2`,
  `iso-v1` / `design-only`. Run roots `advisory/pool-runs/plan-<subject>-20260827/`.

## Disposition, stated before the numbers

`planning.finishability/1` in the design-only environment **does not rank
tuples**, and the cells below are information, not placement evidence.
Every claim appended today carries a NOT A RANKING note. No quartermaster
objective is installed over the construct and none should be. The reason is
P2b's own finding, now confirmed on eight subjects: the only check that ever
fails is `scope_overlap`, a k-packet graph has k(k−1)/2 pairs that can
collide, and so the rate is close to an inverted proxy for how much a
subject decomposed the step. Across the whole board, **93 of 93 graphs with
five packets or fewer pass every check.** The instrument separates subjects
only on graphs of six packets and up, and a subject that hands the step back
as one packet clears the gate by construction.

## Three tuples minted

`claude-fable-5-1-high`, `cc-glm-5-3-flash-high` and
`agy-gemini-3-8-flash-high` were declared in `striatum-next/backends/` at
effort high (the standing sweep cap of 2026-08-21), each `status: disabled`
and `review: baseline` on a declared basis: an unmeasured tuple is not
admitted on the strength of a family name, and nothing transfers across a
model revision or a model tier. Each pin was probe-verified through its own
config dir and the declaration records the evidence that the pin resolves
rather than falling back (an unknown alias errors on all three surfaces:
`claude-code:unrecognized_model`, Z.ai `400 [1214] modelCode: does not
exist`, and the agy sibling's recorded behaviour).

The declarations are **staged but not committed**: striatum's freeze-guard
refused the commit because a packet frontier is live (nine requests, one
live codex lane). The guard's override is `--no-verify`, which is a
Principal act, not mine. They commit when the frontier drains.

Two confounds are on the declarations themselves. `cc-glm-5-3-flash-high`
is not effort-matched to `cc-glm-5-3-max` (high against max), so a
flash-versus-full reading mixes model tier with effort tier. And
`agy-gemini-3-8-flash-high` carries the 3.7 sibling's review-pinned adapter
shape (`--json-schema review-ledger.schema.json`, payload at
`/structured_output`) so that a 3.7-versus-3.8 review is a model
comparison and not an adapter comparison — which is also why it cannot be
measured on planning under its declaration (P2b item 7, unchanged).

## The instrument had drifted, and the board had to be pinned

The first fable launch reported **38** resolvable check sets against the
board's **42**. Since 2026-08-27 the checks registry had moved v37 → v38 and
`~/.local/bin/striatum-plan-oracle` had been rebuilt (sha256 `67ad30b6…`
against the board's `4ff9ed37…`). The run was stopped four rows in and the
drift measured by re-scoring all 148 stored P2b graphs:

| instrument | verdicts differing from the recorded 148 |
|---|---|
| oracle rebuilt at striatum-next `06cd940` + registry v37 | **0** |
| today's oracle + registry v38 | **19**, every one `resolvable_ok` true → false |

The rebuilt binary (`a785e717…`) differs from the board's bytes only in Go
build stamps and reproduces every verdict; it and the v37 registry are kept
in `~/.local/lib/caplab-instruments/plan-p2b-20260827/` with a
`PROVENANCE.md`. `planning_sweep.py` gained `--registry`, `--oracle-dir` and
`--note` so a later subject can be measured on a pinned instrument and say
so on its claim. All three runs below were scored on the pin and report 42
resolvable sets. The four unpinned rows are kept as
`results.unpinned-v38.jsonl` beside an `INSTRUMENT-NOTE.md`, not as
measurement. By evening the live registry was v39.

This is scar tissue 1 firing a second time: unpinned, fable 5.1 would have
been charged for four check sets the registry retired after the board was
measured.

## The board, read with structure beside it

| subject | n | finish | 95% CI | ≤5 pkts | 6+ pkts | share at 6+ | median pkts | 1-packet graphs | scope failures | disjointness | identical-scope dups |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `codex-terra-max` | 24 | 1.00 | [0.86, 1.00] | 16/16 | 8/8 | 0.33 | 4 | 3 | 0 | 1.00 | 3/21 |
| **`claude-fable-5-1-high`** | 24 | 0.96 | [0.80, 0.99] | 13/13 | 10/11 | 0.46 | 5 | 1 | 1 | 1.00 | 2/23 |
| `codex-harm-terra-max` | 24 | 0.96 | [0.80, 0.99] | 16/16 | 7/8 | 0.33 | 5 | 4 | 2 | 1.00 | 2/20 |
| `claude-harm-opus-5-high` | 24 | 0.88 | [0.69, 0.96] | 10/10 | 11/14 | 0.58 | 7 | 1 | 6 | 1.00 | 6/23 |
| **`cc-glm-5-3-flash-high`** | 24 | 0.79 | [0.60, 0.91] | 10/10 | 9/13 | 0.57 | 8 | 1 | 8 (+2 index) | 1.00 | 6/22 |
| `codex-sol-high` | 24 | 0.79 | [0.60, 0.91] | 15/15 | 4/8 | 0.35 | 4 | 5 | 20 | 1.00 | 4/18 |
| `cc-glm-5-3-max` | 24 | 0.75 | [0.55, 0.88] | 12/12 | 6/11 | 0.48 | 5 | 1 | 20 | 0.90 | 9/22 |
| `claude-opus-5-high` | 24 | 0.71 | [0.51, 0.85] | 11/11 | 6/12 | 0.52 | 7 | 1 | 25 | 0.91 | 9/22 |

Yield is 100% for every subject (192 of 192 invocations returned a graph);
parse failures are 1 each for GLM-flash, GLM-max, opus-5 and sol, 0 for the
rest. Scope failures count `scope_overlap` packet pairs; "identical-scope
dups" is graphs in which two packets declared the same write scope, over
graphs of two or more packets; disjointness is the share of packet pairs
whose write scopes do not collide.

**Why Terra sits first.** Two-thirds of its output lives in the region
where nothing can fail, and three of its graphs are a single packet. It is
also 8 of 8 on the large graphs it did produce, so "Terra hides a defect" is
not supported either — the sample is eight. And Terra runs at effort max on a
board where the rest run at high (P2b's ruling 4), so even its decomposition
style is confounded with effort.

**Fable 5.1.** 23 of 24, with ten graphs of eight packets or more — as much
decomposition as the opus tuples — and one collision in the whole sweep.
Disjointness 1.00 and 2 of 23 duplicates are the cleanest on the board. Its
interval clears `claude-opus-5-high`'s and nothing else. Nine minutes for
the sweep; median 41 s per task. There is no Fable 5 row on this board, so
nothing here speaks to 5 → 5.1.

**GLM-5.3-flash.** 19 of 24. It decomposes the most of any subject (median
eight packets, twelve graphs at eight or more) and pays for it in eight
collisions; its 9 of 13 on large graphs sits with the opus tuples. It is the
first subject to fail a check other than `scope_overlap`: two graphs
(`agy-lane-is-robust-b`, `check-registries-portable-b`, eight packets each)
carry a `non_topological_index` — the packet index does not respect the
dependency order — a real defect no environment induces. Its one parse
failure is P2b's verification-only-packet shape again, on the same `2281`
revise task that took down three families before it. Median 218 s per task
against 135 s for GLM-max; the tier is not faster on this work. Read it
beside `cc-glm-5-3-max` (0.75, 20 collisions, 9 of 22 identical scopes) with
the effort confound in view: at the size-normalized level flash is cleaner
than max, and that is the only sentence this instrument licenses.

**Gemini 3.8 Flash: withdrawn after one row.** Under a pass-neutral adapter
(`--output-format json`, payload at `/response`, no schema) agy returned
`status: ERROR` ("Agent execution terminated due to error.", 112 s) inside
bubblewrap. The identical prompt (`pt-f86095a00f0c624f`, 24 KB) through the
identical command outside bubblewrap produced a correct two-packet work
graph. The failure is the harness meeting the sandbox on a long prompt,
not the model; it was not diagnosed further, because nothing on this board
is worth debugging agy-in-bwrap for. The attempt is kept as
`withdrawn-plan-agy-gemini-3-8-flash-high-20260827/` with a note. Under the
sibling's review-pinned shape the same 24 KB prompt succeeds inside
bubblewrap (456 s, structured output extracted), which is the shape the
review sweep uses.

## What was launched instead

Principal-directed, on the instrument that has measured separation
(matched-pair defect injection, synthetic contract, `iso-v1`, seed
`20260819`, 69 pairs): `iso-claude-fable-5-1-high-20260819`,
`iso-cc-glm-5-3-flash-high-20260819` and `iso-agy-gemini-3-8-flash-high-20260819`,
through `scripts/supervise_sweep.py` at two lanes each. Fable spends the
claude window, GLM the Z.ai coding plan, Gemini the Ultra window shared with
live striatum dispatches. Results are a separate record.

## Findings for striatum

- The checks registry moved v37 → v38 → v39 in six days. Anything that scores
  against it must pin it or say which version it scored against.
- agy under a pass-neutral `--output-format json` adapter fails inside
  bubblewrap on a long prompt and succeeds outside it. Whatever the
  production surface does with agy, it is not this shape.
- The verification-only packet the schema cannot express (P2b) has now
  claimed a fourth subject on the same task.
