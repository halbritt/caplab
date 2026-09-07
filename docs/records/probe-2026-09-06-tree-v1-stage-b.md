# Stage B containment and the §6.5 probe set

- Date: 2026-09-06. Plan `tree-v1` rev 2, step 4. Code:
  `src/caplab/advisory/pool_runner.py` (`sandbox_prefix`, `harness_rebinds`,
  `state_dir_link_targets`), `scripts/tree_v1_probes.py`. Rows:
  `advisory/pool-runs/tree-v1-probes-20260906/probes.jsonl` (the final row
  per binding and kind is the one that counts; the run log names them).
- Gate for step 5: every probe passes on every harness. **Met.**

## The mount, as built

Inside a lane the root filesystem is read-only and home is a tmpfs. On top
of it, and nothing else:

| bound | mode | how it is chosen |
|---|---|---|
| `~/.local/bin`, `~/.local/share/claude`, `~/.npm-global`, `~/.local/go` | read-only | `TOOLCHAIN_RO_PATHS`: where the harness executables live |
| the harness's state directory | writable | the declaration's `CLAUDE_CONFIG_DIR=`, `CODEX_HOME=`, `HOME=` (agy) or `GOCACHE=` |
| targets of symlinks in that directory | writable, the target only | `state_dir_link_targets`; today one: codex's `auth.json -> ~/.codex/auth.json` |
| `~/.config/opencode`, `~/.local/share/opencode`, `~/.local/state/opencode`, `~/.cache/opencode` | writable | only when the adapter program is `opencode`, which declares no state directory |
| files the declaration names (`--json-schema …`, `RIPGREP_CONFIG_PATH=…`) | read-only | `adapter_resources`, `adapter_env_files` |
| the case directory `<run>/workspace/<case>/` | writable | one per case; `base/` and `evidence/` beneath it re-bound read-only |
| `/tmp` | private tmpfs | see finding 1 |

A state directory under a masked path (`~/git`, the graph store, the
tuner's runs, `~/.config/plane`, `~/.cache`) is refused, not bound; striatum's
own `harness-config/` under the store is the one exemption.

## Results

Mechanical probe (a shell under the exact mount each declaration gets; 30
attempts; the real filesystem and the `base/` digest checked afterwards) and
model probe (the harness asked to quote a nonce from `base/nonce.txt`;
`base/AGENTS.md` and `base/CLAUDE.md` carry a second marker).

| declaration | harness | mechanical | answered | nonce quoted | loads instruction files from `base/` | seconds |
|---|---|---|---|---|---|---|
| `or-gemini-3-7-flash-high` | lane | pass | yes | n/a (one API call, no tool loop) | n/a | 8.2 |
| `cc-glm-5-3-flash-high` | claude-code (glm-zai config) | pass | yes | yes | **no** | 11.6 |
| `claude-opus-5-high` | claude-code | pass | yes | yes | **no** | 4.8 |
| `codex-sol-high` | codex | pass | yes | yes | **no** | 28.0 |
| `agy-gemini-3-7-flash-high` | agy | pass | yes | yes | **no** | 26.5 |
| `oc-glm-5-3` | opencode | pass | yes | yes | **no** | 6.9 |

Every mechanical attempt the plan names was refused: create, modify, delete,
rename, chmod, symlink, hard link (in and out), `git init`, hook and lock
under `base/`; create and delete under `evidence/`; a sibling case; a
symlink to the store. The store, the checkouts, the tuner's runs and the
Plane tokens are not visible. Writes into the synthetic home succeed on the
tmpfs and never reach the real home (checked after each run). The `base/`
digest is unchanged after every mechanical and model probe. The workspace
accepts a copy of `base/` and a git commit inside the copy, as §2.7 permits.

**§2.6 consequence:** no cohort harness loads `AGENTS.md` or `CLAUDE.md`
from a workspace subdirectory when reading files there. The exact snapshot
is the subject-visible view; no filtered view, no per-harness tree, one
digest on the row.

## Findings, each fixed before the passing run

1. **The host `/tmp` was shared.** A sibling case directory under `/tmp`
   was readable and writable from inside a lane. `/tmp` is now a private
   tmpfs whenever a case workspace is given, and every case has its own
   directory (`measure_case`), so a sibling's spill file or base is not
   reachable.
2. **codex's credential is a symlink into the real home.**
   `harness-config/codex/auth.json -> ~/.codex/auth.json`; inside the
   synthetic home the link dangled and codex answered 401. The link target
   is now bound at its own path, the file alone, writable so a token
   refresh can write in place (`~/.codex` itself, 12 GB of the user's
   sessions, stays invisible). If codex refreshes by rename the write will
   fail against a mount point; the dry run watches for it.
3. **Launcher environment.** Two declarations resolve outside the sandbox's
   remit: opencode's `ZAI_API_KEY` and the lane's `OPENROUTER_API_KEY` come
   from `~/.config/striatum/{zai,openrouter}.env` (striatum's wake units
   inject them), and `opencode` lives in `~/.npm-global/bin`, which the
   user session's `environment.d` puts on PATH but an interactive shell may
   not. The probe and sweep launchers must source those files and PATH;
   neither is a sandbox property.

Housekeeping: the first probe run wrote three probe files into agy's HOME
(`harness-config/agy/{.config/plane,.local/share/striatum,git/caplab}`,
created by the probe's own `mkdir -p` because agy's HOME is that writable
directory). They were removed, along with the empty
`.local/share/striatum` directory an agy run had left there on 2026-07-13.
The probe now targets the real home path, not `$HOME`.

## Accepted residuals (plan §2.2, Principal #50 item 2)

- Each subject reads its own harness's inference credentials (codex's via
  the bound `~/.codex/auth.json`). Re-verify on any declaration change.
- Network open. Controls against remote-commit escape: no checkout exists
  inside a lane; the tree guard.
