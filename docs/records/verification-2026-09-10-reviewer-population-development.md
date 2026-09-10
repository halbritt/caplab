# Reviewer ranking: population reconnaissance

Scope: ADR 0066 development step, tracked in CAPLAB-87. This verifies a
population census and a fixed feasibility selection. It does not verify an
instrument, adjudicate a case, or establish a reviewer ordering.

## Observations

The window is `[2026-08-11T00:00:00Z, 2026-09-10T17:25:10Z)`, bounded at
the new goal's creation time. Source tips are fixed in
`docs/product/studies/reviewer-ranking-001/census-sources.json`.

| Repository | Mainline commits | Included code changes | Median changed code lines |
|---|---:|---:|---:|
| ai-newsroom | 24 | 22 | 228.5 |
| caplab | 281 | 194 | 223 |
| council | 191 | 163 | 98 |
| striatum-next | 280 | 228 | 127 |
| Total | 776 | 607 | Not pooled |

The code paths cover Python, Go, TypeScript, JavaScript, Shell and C. The
counts are changes, not independent defect incidents. The implementation
retains all 776 rows and reasons for code-suffix/prefix exclusions. Merge
changes are measured against their first parent; side-branch commits are not
also counted. Root commits have no base and are explicitly ineligible.

Independent `git rev-list --first-parent --timestamp` enumeration matched
all four in-window commit sets. A complete census rerun after disabling
Git replace-object interpretation reproduced the same content hash:
`8cc0c04a3e40a5acff17d211b89123f0aae151f74742c91eaf92d5255ba338e3`.
The source-tip pins ignore later branch movement and uncommitted files.

The fixed feasibility sample has 32 changes: two per repository and each
of four code-line-size strata. Its content hash is
`2ec503f325733145ef600731d950a956949c629ec6cd23235731e71e952f287e`.
Every stratum retains selected counts and the IDs not selected. No candidate
was chosen using a commit message, reviewer outcome, defect label, or test
availability. No replacement is permitted for an unverifiable selected case.

Full metadata artifacts are retained in owner-only storage under
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/`.
The tracked [development receipt](../product/studies/reviewer-ranking-001/development-receipt.json)
contains source pins, selected case identities, byte counts, raw-file hashes,
and content hashes. Those local hashes support integrity checking; they are
not an independent temporal seal or experimental admission.

## Initial feasibility observations

After selection, source inspection was separately authorized in
`authorization-2026-09-10-reviewer-feasibility-inspection.md`.

| Sampled change | Observed code delta | Outcome evidence still needed |
|---|---|---|
| ai-newsroom `566e5af24c0a7a7a00e04326de75bf613dedeb6d` | Header markup and related CSS styling change together. | Browser/DOM behavior and pre-existing functional/accessibility requirements. An aesthetic preference is not a defect oracle. |
| caplab `b359e30393265a9e36a6de21a9ef0833fd54e0fd` | Leaderboard renderer adds model and harness identity; a generated HTML artifact changes with it. | Identity-source contract and a reproducible check of rendered values. Existing scores in the HTML are historical material, not new ranking evidence. |
| council `c1526c8552ccfa6236c01988aa141d0705eb5d7f` | Effort parsing replaces a permissive fallback with an exhaustive-driver error path. | Valid-driver domain and observable parsing behavior; type checking alone cannot label the whole patch clean. |

All three remain **unadjudicated**. No target code or target test was run.
Diff SHA-256 values in the same row order are:

- `be75635f82a2143a7abc1dbfcb7e00c449e8f35f476713223b44dbb4e0fe4e14`
- `4082ac3d8be0bf095702bde7f925beaceac6c911dfebda29b198a86cd9475082`
- `a616affbc50f80aaad2f0fde01190782d03eca1e43281f3b6d47a0fba28314dc`

Reproduce each using `git --no-replace-objects -C SOURCE diff --no-ext-diff
--no-textconv --no-renames BASE COMMIT --`, with BASE and SOURCE from the
development receipt/full sample. No diff bytes were copied into a dataset.

The initial suffix frame omits pure CSS/HTML changes. Its retained exclusions
contain 17 CAPLAB commits with frontend-only changes; none were found in the
other three repositories by the `.css/.html/.scss/.vue/.svelte` path scan.
That is an observed coverage gap, not a reason to discard the original
selection or assert frontend review is unimportant. Determine which are
generated outputs versus authored source, and amend/extend the population
with a retained selection history before claiming coverage of frontend work.
The mixed ai-newsroom sample already requires its CSS context even though
eligibility was triggered by its Python file. Source suffixes do not define
the full behavior that a reviewer must understand.

## Verification

Ten focused tests pass. They exercise real Git repositories, exact pinning
despite dirty worktrees/later commits/replacement refs, nonmonotonic commit
dates, first-parent merge accounting, deletions, unusual filenames, excluded
history, duplicate-source rejection, census corruption, complete sample
accounting, and retention of large/non-text strata.

The first repository-wide run used `make`'s Python environment without the
pinned WebSocket test dependency: 1,484 tests ran without failure, with seven skips. That
was insufficient to claim the previously established coverage. A second
`CAPLAB_TEST_WEBSOCKETS_ROOT=/tmp/caplab-native-transport-deps/websockets make check`
run completed with **1,515 tests, four skips, no failures**, in 231.092 seconds.
The terminal result is recorded in
`/tmp/caplab-ranking-development-pinned-check.log`. Raw and canonical hashes
of both durable metadata artifacts were independently rechecked against the
tracked receipt; the complete census rerun is byte-identical.

## Doctrine obligation disposition

The evidence-backed packet in ADR 0066 used inspected repository authority,
the accepted qualification boundary, and the recorded operator validity
failure. Its four cited concepts passed `pincite-citations` verification.

| Obligation group | Disposition |
|---|---|
| Explicit task authority, decision owner, repository contracts | Satisfied by the owner goal, correction, ADR 0026, AGENTS.md, and the confirmed instrument disposition. |
| Affected state, invariants, caller needs, preservation, reversibility | Material to development; addressed by the standalone read-only Git census, exact tip/window/path policy, exclusive output creation, retained exclusions, scoped authorization, and real-repository tests. |
| Alternatives, bounded question, evidence connecting action to problem | Material; ADR 0066 selects reconnaissance because the prior instrument separated artificial non-production defects. It rejects treating the advisory study or another model's judgments as ranking truth. |
| Population validity, independent truth, scoring accuracy, prospective comparison | Material to the study and still missing. This record supports investigation only. No doctrine-backed conclusion that the instrument or ranking is valid is issued. |
| Datastore consistency, transaction guarantees, idempotent effects, caching, architecture restructuring | Nonmaterial to this read-only metadata census: it executes no target runtime and changes no target storage semantics. Reassess if subsequent work touches those boundaries. |

## Next required work

Assess the fixed sample's original requirements, change context, independent
witness possibilities, and clean-control limits. Retain every case's
disposition and the population coverage gap. Then build and challenge outcome
scoring on actual cases. Native calls and ranking remain downstream of that
validity work; producing this census is not completion of the owner goal.
