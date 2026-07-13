# Native capture surface — CLI/IO contract

Status: v1, agreed 2026-07-13. Implemented by the striatum-next compiled
command `striatum-workspace-capture` (branch `agent/bench-capture-surface`);
consumed by the books native trial runner
(`doctrine/evaluations/robustness/native/run-native-trial.sh`).

## Boundary

Scenarios, orchestration, verification, and records belong to books.
Constructing the runtime invocation from a backend declaration, running it in
a caller-prepared workspace, and capturing what the run did belong to
striatum. Books never parses backend declarations beyond naming them, never
builds harness argv, and never reimplements capture; the surface never knows
what a task, verifier, or reward is.

The surface deliberately does NOT dispatch through the production
submit/admit seam: `codex-sol-max` forbids the `build` pass type at the
adapter (`internal/backend/llm/adapter.go`), and the benchmark's task shape
is a build. The surface invokes the declared runtime adapter command
directly. Pass-type discipline returns later as the bench's organizing axis;
this bypass is the preregistered bootstrap, not the design.

## Invocation

```
striatum-workspace-capture \
  -declaration <backend.yaml>       # required: declaration to build argv from
  -workspace <dir>                  # required: caller-prepared tree, mutated in place
  -output <dir>                     # required: capture destination, must not exist
  -prompt-file <file>               # required: prompt text, delivered per prompt_mode
  -timeout <seconds>                # default 1800
  -mount <path>                     # optional: bind workspace at <path> in a mount
                                    #   namespace and run with cwd there
  -tmpfs <path>                     # repeatable: tmpfs over <path> in the namespace
  -bind <src>:<dst>[:ro]            # repeatable: extra binds in the namespace
  -netns                            # private network namespace, loopback only
  -netns-egress                     # with -netns: slirp4netns user-mode NAT out
  -runtime-arg <arg>                # repeatable: appended to the declaration's
                                    #   adapter.command before the prompt; every use
                                    #   is recorded in provenance as a deviation
```

From `-declaration` the surface reads only `id`, `adapter.command` (argv
list), and `adapter.prompt_mode`. `prompt_mode: arg` appends the prompt file
content as the final argv element. The declaration file is hashed into
provenance. Model-free fixture declarations use the same schema with
`adapter.command` pointing at a fixture script, so the parity proof exercises
the identical declaration-parsing and execution path.

When `-mount`/`-tmpfs`/`-bind`/`-netns` are present the runtime runs inside
a bubblewrap namespace (`bwrap --bind / / --dev /dev --proc /proc` plus the
requested entries). `-netns` adds a private network namespace: the runtime
maps to uid 0 (as the original containers did), loopback is raised by an
in-namespace init, and the host's sockets are unreachable — which is what
lets the task's fixed service ports (9090/8080) bind regardless of host
state, and shields the loopback probes from the host's ephemeral-port
churn. `-netns-egress` attaches a `slirp4netns` NAT (tap0, DNS proxied at
10.0.2.3 via a resolv.conf bind, host loopback explicitly unreachable) for
runtimes that must reach their vendor endpoint. Without any namespace flag
the runtime runs directly in `-workspace` on the host network.

## Capture output layout

```
<output>/
  workspace/          # full post-run tree copied from -workspace
  manifest-pre.json   # relpath -> sha256 of every workspace file before the run
  manifest-post.json  # same, after
  runtime.log         # runtime stdout+stderr, verbatim (codex: JSONL events)
  provenance.json
```

`provenance.json` fields:

| field | meaning |
|---|---|
| `backend_id` | declaration `id` |
| `declaration_sha256` | hash of the declaration file |
| `prompt_sha256` | hash of the prompt file content |
| `command` | full resolved argv (prompt elided, replaced by its hash) |
| `runtime_args` | the `-runtime-arg` deviations, verbatim |
| `namespace` | the mount/tmpfs/bind spec used, or null |
| `started`, `finished`, `duration_s` | wall clock |
| `exit_code` | runtime exit code, verbatim |
| `timed_out` | bool |
| `token_usage` | parsed from codex `--json` events when present, else null |
| `capture_complete` | true iff workspace copy + manifests succeeded |

## Exit codes

- `0` — runtime ran and capture is complete, regardless of the runtime's own
  exit code (which is data, in provenance). A failed agent is a valid trial
  observation; a failed capture is not.
- `1` — usage or declaration error, nothing ran.
- `2` — runtime failed to launch.
- `3` — timeout: the runtime was killed; capture still attempted,
  `timed_out: true`.
- `4` — capture failed after the run; workspace is intact for manual salvage.

## What the books runner does with it (informative)

Per trial (`doctrine/tools/run_checkout_native.py`): materialize the task's
`environment/app` into a fresh workspace with uniform file metadata; verify
the corpus against the task's pinned `surface-corpus.manifest.json`; invoke
the surface with `-mount /app`, `-netns` (plus `-netns-egress` for
vendor-endpoint runtimes), `-tmpfs /tmp`, `-tmpfs /home/halbritt/git`,
`-bind <pinned corpus>:/home/halbritt/git/books:ro` (restoring the
container's baked knowledge surface at its path and masking the real repo,
which contains this bench's own sources), and
`-bind <trial runtime dir>:/var/tmp/.bench-runtime:ro` (fixture scripts);
then run the task's pristine `tests/test.sh` against `<output>/workspace`
via `CHECKOUT_APP_DIR`/`CHECKOUT_VERIFIER_LOGS`, itself wrapped in a
loopback-only namespace for the same port-determinism reasons. The
agent-phase `gateway_access.log` needs no plumbing: the gateway's default
path is `/app/gateway_access.log`, which is inside the bound workspace.

The model-free parity gate is
`harbor/tasks/checkout-retries-refs/run-native-matrix.sh`: all nine
reference cells must reproduce the pair record's reward matrix through this
seam before any model condition runs (proven 2026-07-13: 9/9).

## Known deviations from the container condition (preregister with any run)

- The runtime's shell reaches the outside network through slirp NAT when
  `-netns-egress` is set (codex needs its vendor endpoint, and its
  `workspace-write` sandbox needs `sandbox_workspace_write.network_access=true`
  as a `-runtime-arg` so agent commands can use the private loopback); the
  container had pod-local networking with no egress. Host loopback services
  are unreachable in both.
- Reads outside `/app` see the host filesystem except the masked paths above,
  where the container saw a minimal image. Out-of-workspace reads are
  auditable post hoc in `runtime.log`.
- `--ignore-user-config` is passed as a `-runtime-arg` so the shared
  `CODEX_HOME` user config (including its enabled plugins and memories)
  cannot leak into the trial; auth still resolves through `CODEX_HOME`.
- Sequential trials only: the shared `CODEX_HOME` has a known auth-refresh
  race under concurrency (striatum-next BUG-2026-07-12), and capacity is a
  shared rolling window with production striatum lanes.

## Sandbox hardening state (from the 2026-07-13 adversarial review)

The surface confines the runtime with a private user + network + PID
namespace: the PID namespace makes the timeout kill hermetic (a detached
grandchild cannot outlive it), the capture refuses to follow a swapped
symlink out of the workspace (`O_NOFOLLOW`), and `-clean-env` withholds the
operator's environment from a runtime that has egress so ambient secrets
never reach the model (the declaration's own `env` prefix still delivers
what the harness needs, e.g. `CODEX_HOME`). The model-free fixture path runs
`-netns` **without** `-egress`, so its namespace has only private loopback —
no route off-box at all.

Two gaps remain and are **required to close before the egress/real-model
run** (they do not affect the fixture parity path, which has no egress):

- **Host-LAN reach under egress.** `slirp4netns --disable-host-loopback`
  blocks the host's `127.0.0.1` but not services bound to its LAN/tailscale
  addresses; the real-model run must add an in-namespace firewall (or a
  slirp outbound restriction) dropping traffic to the host's non-loopback
  addresses. Not an answer-leak for this task (the corpus/verifier are
  filesystem-masked), but an isolation gap.
- **Confining root.** With codex's own sandbox bypassed (required — see the
  preregistration's sandbox-architecture findings), the real run must not
  use `--bind / /`; it must bind only the toolchain (ro), the workspace
  (rw), the pinned corpus (ro), and codex's auth, masking everything else
  (notably the reference solutions under `/var/tmp` and the host's
  credentials), and re-pass the parity matrix through that root.
