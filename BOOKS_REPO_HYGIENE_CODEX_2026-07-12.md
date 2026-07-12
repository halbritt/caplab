# Books repository hygiene audit

## Audit basis

Target: `/home/halbritt/git/books` on
`agent/evidence-governed-doctrine-remediation` at `e1f850d`. The checkout was
dirty. The active external-model sweep owns
`doctrine/evaluations/entailment/results.jsonl`; this audit did not edit, stage,
truncate, regenerate, or validate that file. Inspection covered tracked and
untracked paths, product documentation, robustness code and tests, graph work
fragments, references to those fragments, and generated Python caches. Source
books, converted books, Git internals, and sweep content were not inspected for
hygiene.

## Executive summary

- Three tracked graph fragments contained edges already present in the canonical
  graph with newer human-audited formulation identities.
- The fragments caused deterministic merge collisions and were deleted after
  record-by-record comparison with the canonical graph.
- The robustness implementation, tests, and product documents form one coherent
  uncommitted change set.
- Product lifecycle metadata used two noncanonical status values and is now
  aligned with the documented `decided` and `authorized` states.
- Evaluation and changelog prose incorrectly described the laboratory as
  proposed and unimplemented; those claims now match P1 and P2.
- Python bytecode caches are ignored generated output and require no tracked
  cleanup.
- The external-model sweep remains outside this cleanup.

## Cleanup plan

| ID | Classification | Path | Evidence and action | Verification | Rollback unit |
|---|---|---|---|---|---|
| H1 | SAFE_TO_EXECUTE | `doctrine/_work/graph-fragments/*-edges.yaml` | Canonical edges contain the same semantics with updated audited provenance; delete the three stale inputs. | `python3 doctrine/tools/merge_graph_fragments.py --check` | Restore the three files. |
| H2 | SAFE_TO_EXECUTE | `docs/product/**`, evaluation README, changelog | Lifecycle values and capability claims disagreed with the implemented P1/P2 code; update metadata and prose. | Product-document checks, local links, documented CLI invocation | Revert these documentation paths. |
| H3 | SAFE_TO_EXECUTE | `doctrine/evaluations/robustness/README.md` | The implemented directory lacked local ownership and run instructions; add a concise contract README. | Run the documented command and focused tests. | Delete the README. |
| H4 | OUT_OF_SCOPE | `doctrine/evaluations/entailment/results.jsonl` | Active external-model sweep output. No action. | Sweep owner verification | None. |

## Executed changes

- Deleted the three stale tracked graph fragments.
- Corrected product lifecycle metadata and current-capability documentation.
- Added the robustness directory README.
- Preserved the active sweep output.

## Deferred decisions

- Commit and push policy was not granted. The cleanup remains uncommitted.
- P3 and later laboratory checkpoints remain separate authorization decisions.

## Verified clean

- No untracked editor backups or temporary files were found.
- Python cache directories contain ignored bytecode only.
- No live loader depends on a specific fragment filename; the merger consumes
  whatever `*-edges.yaml` files remain in the work directory.

## Residual risk and follow-ups

Repository-wide verification can change while the external-model sweep appends
results. Focused robustness, authority, graph-fragment, documentation, and link
checks should be run against a stable snapshot. The sweep owner must validate
and decide retention for its result records independently.
