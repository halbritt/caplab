# Agent instructions

Before interpreting research material, changing runtime behavior, constructing
prompts, reviewing evidence, or recording decisions, read and follow
[`docs/domain/ubiquitous-language.md`](docs/domain/ubiquitous-language.md).

CAPLAB is a standalone product and repository. Do not place CAPLAB runtime code
or product authority in `books`, Pincite, Doctrine, Striatum, or Proximal.
Those systems may supply source evidence, advisory guidance, downstream
requirements, or host integration without owning CAPLAB's product decisions.

`history/ethogram/` preserves the tracked tree and ancestry of the former
repository identity. Treat it as historical custody, not as an active Python
package root, CI surface, or source of CAPLAB product authority. Preserve uses
of “Ethogram” that identify historical decisions, artifacts, branches, or
provenance; do not revive it as the active repository identity.

Keep observations, inferences, recommendations, decisions, authorization,
execution, verification, and acceptance distinct. Plane is a planning
projection. A model or agent may record human-owned judgment only when the
human has explicitly delegated that authority and the record names the source
and scope of delegation.

For comparative tests of agentic models, treat `(native harness, model,
effort/configuration)` as the subject identity. The native harness is a
behavior-bearing component under test. Do not substitute OpenRouter,
Harbor/Terminus, a generic SDK, or another shared proxy for Claude Code, Codex
CLI, or another model's native harness unless a repository-owner decision
explicitly names that proxy configuration as the subject or authorizes the
specific exception. Enforce `docs/product/contracts/native-agent-systems.json`
before preparing a live attempt.

Historical evidence must not be copied, admitted, registered, rewritten, or
purged unless the active authorization names that effect. Preserve source
commit, path, content hash, and custody provenance for imported governing
records.

## Parallel work: one worktree per branch

When more than one agent works this repo at once, do not share a working
directory — give each unit of work its own git worktree. A branch can be
checked out in only one worktree at a time, so concurrent edits to shared
files (Makefile, configs, generated/golden files) become impossible.

- One worktree per branch, one agent per worktree; name the dir after the branch.
- Siblings, not nested: create worktrees OUTSIDE this checkout
  (`../caplab-wt/<branch>`), never inside it — recursive globs, file-count/hash
  gates, and IDE indexers must not scan across worktrees.
- Lifecycle: `git worktree add ../caplab-wt/<branch> -b <branch>` /
  `git worktree list` / `git worktree remove <path>` after merge /
  `git worktree prune`. Agents with worktree isolation get this for free.
- Shared object store and build caches are fine; worktrees do NOT isolate
  ports, databases, or local services — coordinate those separately.
- Regenerate, don't merge, generated artifacts (golden files, compiled
  indexes): merge the source change, then regenerate once on the merged tree.
