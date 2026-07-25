---
id: caplab-63-harness-selection-research-2026-07-25
artifact_type: research-record
title: CAPLAB-63 harness selection research — tool-call legibility of Claude Code and Codex CLI
status: complete
created: 2026-07-25
decision_record: null
authority: none
---

# CAPLAB-63 harness selection research

This record establishes facts about the two candidate native agent systems and
presents a comparison. It is **input to an owner decision**. It authorizes
nothing, decides nothing, and runs nothing. No model call was made in producing
it.

## Evidence classes

| Label | Meaning |
|---|---|
| `observed-in-repo` | Derived from CAPLAB's own executed campaigns — repository artifacts or the sealed raw custody trees they reference. Real behavior of these harnesses under CAPLAB conditions. |
| `observed-locally` | Derived by inspecting the installed binaries, `--help` surfaces, config dirs, or on-disk session files on `proximal` on 2026-07-25. |
| `documented` | Vendor documentation fetched 2026-07-25, or a vendor-repo issue surfaced by search. |
| `inferred` | Reasoned from the above; not directly observed. |

## Evidence base

Two CAPLAB campaigns have already executed both harnesses under bubblewrap
containment with `--json` / `stream-json` capture:

- `caplab-review-dissent-001-development-native-r1-2026-07-20` — 16 primary
  slots, 8 Claude Code (`claude-fable-5-max`) and 8 Codex CLI
  (`codex-terra-max`). Raw custody
  `/home/halbritt/.local/share/caplab/campaigns/caplab-review-dissent-001-development-native-r1-2026-07-20`.
  Repository side: `docs/product/studies/review-dissent-001/native-instrument.json`,
  `docs/product/studies/review-dissent-001/campaign-development-native-r1-2026-07-20/result.json`,
  `docs/records/caplab-13-native-execution-2026-07-20.md`, ADRs 0044 / 0045.
- `caplab-preference-001-native-r2-2026-07-20` — 12 primary slots, 6 each. Raw
  custody
  `/home/halbritt/.local/share/caplab/campaigns/caplab-preference-001-native-r2-2026-07-20`.
  Repository side: `docs/product/studies/preference-001/native-instrument.json`,
  `docs/product/studies/preference-001/native-campaign-r2-2026-07-20/`.

That second campaign is the closer analogue to CAPLAB-63: its tasks required
the agent to *edit* a repository world and verify its own work, so its captures
contain real edit/verify sequences.

Every attempt directory holds `launch.json` (exact argv, input tree digest,
observed versions), `native.stdout` (the event stream), `native.stderr`,
`completion.json` (exit code, timing), and `observation.json` (final task tree
digest). The capture and grading code is `src/caplab/review_dissent/native.py`
and `src/caplab/preference/native_live.py`.

## Comparison

| Dimension | Claude Code (`claude -p --output-format stream-json --verbose`) | Codex CLI (`codex exec --json`) |
|---|---|---|
| **1. Tool-call capture** | JSONL on stdout, one event per line. Typed events: `system/init`, `system/thinking_tokens`, `system/model_refusal_fallback`, `assistant`, `user`, `rate_limit_event`, `result`. Every `assistant` and `user` event carries `uuid`, `session_id`, `request_id`, and an ISO-ms `timestamp` — 488 of 1,147 events across all 14 Claude Code episodes in the two campaigns (every `assistant` and `user` event; `system`/`result` events carry `uuid` + `session_id` instead). `observed-in-repo`. A second on-disk transcript exists at `~/.claude/projects/<slug>/<session>.jsonl` unless suppressed. `observed-locally`. Event-type reference is **not** in the docs. `documented` (open vendor issue). | JSONL on stdout, one event per line. Typed events: `thread.started`, `turn.started`, `item.started`, `item.completed`, `turn.completed`. **Zero events carry a timestamp** — 0 of 387 events across all 14 Codex episodes in the two campaigns. `observed-in-repo`. A far richer on-disk rollout exists at `$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl` with per-event timestamps — but CAPLAB's pinned command passes `--ephemeral`, which disables it. `observed-locally` + `documented`. |
| **2. Action-type distinguishability** | EDIT and READ are **structurally typed**: `tool_use` blocks with `name` ∈ {`Read`,`Write`,`Edit`,`Bash`,…} and a structured `input` (`file_path`, `command`). One action per event. Across both campaigns: `Read` 74, `Write` 12, `Edit` 7, `Bash` 65. ~58–59% of actions are typed without any parsing; only VERIFY-vs-shell-READ requires parsing the `Bash` command string. `observed-in-repo`. | EDIT is typed (`file_change` item, per-file `path` + `kind`). **READ and VERIFY are not typed at all** — both collapse into `command_execution` items carrying a single raw shell string. Worse, the strings are heavily compound: **41 of 46** command executions in the preference campaign (89%) chain multiple actions with `&&`, `;`, `\|\|`, or a heredoc, mixing read + test-run + `chmod` in one event. `observed-in-repo`. CAPLAB's own extractor already fell back to substring matching on shell text (`_command_reads` in `src/caplab/review_dissent/native.py:254`), matching markers `cat/sed/head/tail/less/grep/rg/open(`. `observed-in-repo`. |
| **3. Write-set recoverability** | Yes, from `Write`/`Edit` `input.file_path`. Cross-checked against the tree diff (`launch.json.input_tree` vs `observation.json.task_tree`) for all 6 Claude episodes of the preference campaign: **exact match, 0 missed, 0 spurious**. `observed-in-repo`. Structural caveat: a write performed via `Bash` redirection would be invisible; none occurred. `inferred`. | Yes, from `file_change.changes[].path` + `kind` ∈ {`add`,`update`}. Same cross-check over all 6 Codex episodes: **exact match, 0 missed, 0 spurious**. `observed-in-repo`. Same structural caveat, larger surface: Codex does most of its work through shell, so a `>` redirect or `python - <<PY` write bypasses `file_change` entirely. `inferred`. In the on-disk rollout, `patch_apply_end` additionally carries the full post-image content per file. `observed-locally`. |
| **4. Sampling parameter pinning** | `--model <id>` and `--effort {low,medium,high,xhigh,max}` are first-class flags. `--fallback-model`, `--max-budget-usd`, `--tools`, `--system-prompt`, `--session-id <uuid>`, `--settings`, `--setting-sources`, `--bare`, `--safe-mode`, `--strict-mcp-config` pin the surrounding surface. **No `--temperature`, `--top-p`, or `--seed`** — `claude --help` matches none of them. `observed-locally`. | `-m/--model` plus `-c model_reasoning_effort=<level>`; also `-c model_verbosity`, `-c service_tier`, `-p/--profile`, `--ignore-user-config`, `--ignore-rules`, `--strict-config`, `--sandbox`, `--output-schema`. **No temperature / top-p / seed model config.** `observed-locally`. |
| **5. Per-episode subject identity** | **Strong and in-band.** `system/init` reports `model`, `claude_code_version`, `session_id`, `permissionMode`, `tools`, `mcp_servers`, `plugins`, `skills`, `agents`, `memory_paths`, `capabilities`, `output_style`, `apiKeySource`. Every `assistant` event repeats `message.model`. The final `result` event carries `modelUsage` keyed by **exact model string**, plus `total_cost_usd`, `num_turns`, `stop_reason`, `terminal_reason`, `permission_denials`. `observed-in-repo`. `capabilities` is a documented feature-detection array explicitly offered *instead of* comparing version strings. `documented`. | **Weak in-band.** The `exec --json` stream contains **no model id, no CLI version, no effort, no timestamp** — only `thread_id` and a final `turn.completed.usage`. Identity must be taken on faith from the launch command. `observed-in-repo`. The on-disk rollout does carry it: `session_meta.cli_version`, and a `turn_context` per turn with `model`, `reasoning_effort`, `sandbox_policy`, `approval_policy`, `personality`, `comp_hash`, plus `thread_settings_applied`. `observed-locally`. `--ephemeral` throws all of that away. |
| **6. Redaction tractability** | **Trivial under the pinned command.** The injected prompt is not echoed anywhere in the stream — verified over all 16 review-dissent + 12 preference attempts: **0 of 28 streams contain the prompt text or any user-authored text block**. The only `user` events are `tool_result` returns. `observed-in-repo`. Injected instruction *surfaces* leak only as path names in `system/init.memory_paths`/`skills`/`agents`, which is one typed field to drop. `observed-in-repo`. | **Trivial under the pinned command, for the same reason** — same 0-of-28 result; the Codex stream carries no user message either. `observed-in-repo`. If the richer rollout is adopted to fix dimensions 1 and 5, redaction gets harder but stays mechanical: the packet appears verbatim in `event_msg/user_message`, `world_state.state.agents_md.text`, `session_meta.base_instructions.text`, and `response_item` messages with `role: developer`. All typed; all strippable by event type. `observed-locally`. |

## Claude Code — detail

**Pinned command in both campaigns** (`docs/product/studies/review-dissent-001/native-instrument.json`,
`agent_systems.fable.command`):

```
/usr/bin/env CLAUDE_CONFIG_DIR=… claude -p --model claude-fable-5 --effort max \
  --output-format stream-json --verbose --no-session-persistence --dangerously-skip-permissions
```

Installed on `proximal` today: `claude --version` → `2.1.220 (Claude Code)`;
the campaigns ran `2.1.215`. `observed-locally`.

**Tool-call shape.** From
`.../attempts/a03-s03-primary/native.stdout`, a `Read` call is one event:

```json
{"type":"assistant","message":{"model":"claude-fable-5","content":[
  {"type":"tool_use","id":"toolu_016z…","name":"Read","input":{"file_path":"/work/TASK.md"}}]},
 "session_id":"b0c1158a-…","uuid":"bbff31d2-…","timestamp":"2026-07-20T22:46:22.848Z",
 "request_id":"req_011CdE82M2LjxQ2mJcCyLxFU"}
```

and its result comes back as a `user` event with a structured `tool_use_result`
(`{"file":{"filePath":…,"numLines":…,"totalLines":…}}`), not just text.

**Observed edit/verify interleaving.** Preference attempt `a06-s06-primary`
(task: repair `src/formatter.py`), reconstructed purely from the stream in
event order with timestamps:

```
 1 22:06:30.696 Bash   find /work -type f | head -100
 2 22:06:32.647 Read   /work/.caplab-task.json
 3 22:06:32.652 Read   /work/AGENTS.md
 4 22:06:33.118 Read   /work/OWNER-NOTE.txt
 5 22:06:33.424 Read   /work/src/formatter.py
 6 22:07:14.662 Bash   sha256sum … && python3 --version
 7 22:07:22.661 Write  /work/src/formatter.py
 8 22:07:33.978 Bash   python3 - <<'EOF' … (behavioral probe)
 9 22:07:36.543 Bash   sha256sum … && find /work …
10 22:07:41.825 Bash   rm -rf /work/src/__pycache__ && find /work -mindepth 1 | sort
```

The EDIT (event 7) and the READs are exact; the interleaving code would only
need to classify events 1, 6, 8, 9, 10 as verification-or-not.

**Silent-substitution surfacing — an actual incident.** In review-dissent
attempt `a02-s02-primary` (slot 2, cell `r04`, nominal subject
`claude-fable-5-max`), the stream contains:

```json
{"type":"system","subtype":"model_refusal_fallback","trigger":"refusal","direction":"retry",
 "original_model":"claude-fable-5","fallback_model":"claude-opus-4-8",
 "api_refusal_category":"cyber", …}
```

and that episode's `result.modelUsage` lists `claude-opus-4-8` and
`claude-haiku-4-5-20251001` — **no `claude-fable-5` at all**. One of the eight
"Fable" episodes in CAPLAB's executed calibration was in fact produced by a
different model. `observed-in-repo`.

Two consequences worth carrying into CAPLAB-63:

1. The harness *did* surface the substitution, in-band, in a typed event. This
   is exactly the threat model CAPLAB-63 names, and the capture format caught
   it.
2. CAPLAB's pipeline did **not** notice. `subject_seal` in
   `build_native_review_capture` (`src/caplab/review_dissent/native.py:391`) is
   computed from the *instrument's* declared `model_id`, never from the
   observed stream, and `grep -rn 'opus-4-8\|model_refusal_fallback\|modelUsage'
   docs/ src/ tests/` returns nothing. The substitution is unrecorded in every
   CAPLAB record and ADR. `observed-in-repo`.

Also note every Claude episode's `modelUsage` includes
`claude-haiku-4-5-20251001` (652 in / 13 out tokens, identical across
episodes) — an auxiliary model call inside the harness. The per-episode subject
is a *model set*, not a single id.

**Sources.** `claude --help` (2026-07-25); vendor doc
<https://code.claude.com/docs/en/headless> (fetched 2026-07-25) for `system/init`
fields, `capabilities`, `--include-partial-messages`, `--forward-subagent-text`,
`system/api_retry`, and `--bare`; search surfaced
<https://github.com/anthropics/claude-code/issues/24596> — "CLI `--output-format
stream-json` lacks event type reference" — i.e. the schema is de-facto, not
contractual.

## Codex CLI — detail

**Pinned command in both campaigns**
(`agent_systems.gpt.command`):

```
/usr/bin/env CODEX_HOME=… codex exec -m gpt-5.6-terra -c model_reasoning_effort=max \
  --sandbox workspace-write --skip-git-repo-check --ephemeral --json
```

Installed today: `codex --version` → `codex-cli 0.145.0`; the campaigns ran
`0.144.6`. `observed-locally`.

**Tool-call shape.** From `.../attempts/a01-s01-primary/native.stdout`:

```json
{"type":"item.completed","item":{"id":"item_4","type":"command_execution",
 "command":"/bin/bash -lc \"PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider && printf '\\n--- hidden workspace entries ---\\n' && find . -maxdepth 3 -type f … && ls -la . src tests\"",
 "aggregated_output":"/bin/bash: line 1: pytest: command not found\n","exit_code":127,"status":"failed"}}
```

That single event is a test run, a directory listing, and a metadata dump. It
is the modal shape, not an outlier: 41 of 46 command executions in the
preference campaign are compound. Writing a binary code for "interleaves
verification between edits rather than batching" against this surface means
writing a shell parser and then defending its classification of every compound
command — and the code's reliability becomes the parser's reliability.

Codex is not uniformly untyped: `file_change`, `web_search`, `todo_list`, and
`agent_message` are typed items. The gap is specifically **file reads and
verification actions**, which are precisely the two classes the interleaving
code needs.

The write-set item is clean:

```json
{"type":"item.completed","item":{"type":"file_change","status":"completed",
 "changes":[{"path":"/work/scripts/apply-parserlib-upgrade.sh","kind":"add"},…]}}
```

**The rollout file is much better than the stream.** With `--ephemeral`
dropped, Codex writes
`$CODEX_HOME/sessions/YYYY/MM/DD/rollout-<ts>-<uuid>.jsonl`. Inspected locally
(`/home/halbritt/.codex/sessions/2026/07/24/rollout-2026-07-24T15-22-10-….jsonl`,
5,623 events): every line carries an ISO-ms `timestamp`; `session_meta` carries
`session_id`, `cli_version`, `cwd`, `originator`, `model_provider`, and the full
`base_instructions`; a `turn_context` per turn carries `model`,
`reasoning_effort`, `sandbox_policy`, `approval_policy`, `personality`;
`response_item` entries are typed `function_call` (with `name` and JSON
`arguments`), `custom_tool_call` (`name` ∈ {`exec`,`apply_patch`}),
`reasoning`, `message`; `event_msg/patch_apply_end` carries per-file `changes`
with post-image content; `event_msg/token_count` carries usage and rate limits.
`observed-locally`.

This closes dimensions 1 and 5 for Codex almost entirely. It does **not** close
dimension 2: the underlying tool is still `exec_command` / `exec` with a shell
string, so reads and verifications remain untyped. `observed-locally`.

Caveat: that rollout is from the *current* `0.145.0` interactive TUI, whose tool
surface (`exec_command`, `wait`, `write_stdin`, custom `exec`, `apply_patch`,
`tool_search_call`) differs from what `codex exec 0.144.6` emitted. Harness tool
surface drifts across minor versions. `observed-locally`.

**Sources.** `codex --help`, `codex exec --help` (2026-07-25); vendor doc
<https://learn.chatgpt.com/docs/non-interactive-mode> (fetched 2026-07-25, via
308 from `developers.openai.com/codex/noninteractive`) — confirms the event-type
list, `--output-schema`, `--output-last-message`, `--ephemeral`, and shows no
timestamps in its sample stream; the doc does **not** declare the schema stable
or versioned, and does not mention model identity in the stream. Config-key
inventory taken from strings in
`…/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex`:
`model_reasoning_effort`, `model_reasoning_summary`, `model_verbosity`,
`service_tier`. (`temperature` also appears in that binary but in an MCP
JSON-RPC sampling struct alongside `systemPrompt`/`maxTokens`/`stopSequences`,
not as a model-request config key — `inferred`.) Codex lifecycle hooks
including `PostToolUse` with `tool_name`/`tool_input`/`tool_response` are
documented at <https://developers.openai.com/codex/hooks> (surfaced by search,
not fetched — `documented`, weak).

## Cross-cutting facts that constrain the design

- **Contract compatibility.** `docs/product/contracts/native-agent-systems.json`
  pins both tuples and validates the launch argv as an *ordered subsequence* of
  `required_command_tokens` (`_ordered_subsequence`,
  `src/caplab/subject_identity.py:34`). Adding capture flags is therefore
  contract-legal for either candidate. Choosing one harness pins the model too:
  the contract has no `claude-code` + `gpt-*` or `codex` + `claude-*` cell, and
  ADR 0039 forbids reaching a model through anything but its native harness. A
  single-harness campaign is a single-model campaign. `observed-in-repo`.
- **Neither harness exposes temperature, top-p, or seed.** Episodes are
  irreducibly stochastic under both. Replication is resampling, not
  reproduction. This is symmetric and does not discriminate. `observed-locally`.
- **Per-episode version recording is currently fake.** CAPLAB probes
  `claude --version` / `codex --version` once at campaign preflight
  (`preflight_native_runtime`, `src/caplab/preference/native_live.py:440`) and
  copies the same `observed_versions` dict into every `launch.json` — verified
  identical across all 16 and all 12 launches. Nothing in the current design
  would detect a mid-campaign harness upgrade, let alone a silent model
  rotation. `observed-in-repo`.
- **The severity-enum failure was not a harness failure.** All 16 reviews wrote
  an artifact; all 16 used ordinary severity vocabulary (`high` 9, `info` 17,
  `low` 9, `medium` 3, `error` 2, `major` 2, `minor` 2) because the prompt named
  a `severity` field without stating its enum
  (`docs/records/caplab-13-native-result-2026-07-20.md`). Both harnesses failed
  identically. The lesson for CAPLAB-63 is about elicitation contracts, not
  harness choice — but it is a strong argument for preferring artifact-shaped
  codes and for stating every closed vocabulary in the packet. `observed-in-repo`.

## Gaps

These are unestablished. Each is a design risk if the campaign proceeds without
closing it.

1. **No capture guarantee under `Bash`/shell writes.** Both harnesses' write-set
   evidence held 12/12 in the preference campaign, but neither *structurally*
   prevents an agent from writing through the shell, which would bypass
   `Write`/`Edit` and `file_change` alike. Not established because no observed
   episode did it, and defect-repair worlds are likelier to provoke it (`sed -i`,
   `patch`, `python - <<PY`). **To establish:** a deliberate probe episode with
   a prompt that induces shell writes, on each harness, comparing stream write-set
   to tree diff. Cheap; costs 2 episodes.
2. **Codex rollout capture is untested under CAPLAB containment.** The rollout
   file solves Codex's timestamp and identity problems on paper, but CAPLAB has
   never captured one: the pinned command passes `--ephemeral`, and the sandbox
   mounts `CODEX_HOME` as an in-container `--dir` that does not persist to the
   host. **To establish:** bind a per-attempt host directory as
   `$CODEX_HOME/sessions`, drop `--ephemeral`, run one episode, confirm the file
   lands in custody and that `turn_context.model` matches the launch argv.
3. **Codex `--json` schema stability is undeclared.** The vendor doc lists event
   types but never says the schema is versioned or stable, and the local tool
   surface already changed between `0.144.6` and `0.145.0`. Claude Code's is
   equally undeclared (open issue #24596) but has a first-party SDK type
   reference behind it and a `capabilities` feature-detection array. **To
   establish for either:** pin the exact harness version for the campaign, hash
   the binary, and add a pre-execution schema assertion that fails closed on an
   unexpected event type.
4. **No mechanical detection of silent model rotation exists in CAPLAB today.**
   Claude Code emits the evidence; CAPLAB ignores it. Codex emits none in the
   `exec --json` stream at all. **To establish:** derive the per-episode subject
   identity *from the capture* (Claude Code: `system/init.model` +
   `claude_code_version` + the `result.modelUsage` key set + absence of
   `model_refusal_fallback`; Codex: `turn_context.model` from a non-ephemeral
   rollout) and fail the episode when it disagrees with the manifest. This is
   the single highest-value change and it is only cheap on Claude Code.
5. **Reliability of an interleaving code was not measured on either harness.**
   No blind coder has coded these transcripts. The claim that Claude Code's
   surface is codeable and Codex's is not is an argument from structure, not a
   measured inter-coder agreement. **To establish:** double-code ~10 archived
   episodes per harness from the two existing campaigns (zero new model calls —
   the transcripts are already in custody) and report agreement per harness.
   This is the cheapest and most decision-relevant unblocking experiment
   available.
6. **Effort-level comparability is not established** and cannot be. `--effort
   max` and `-c model_reasoning_effort=max` share a label, not a definition.
   Irrelevant to a single-harness campaign; noted so it is not silently assumed
   if a second arm is ever added.
7. **Doctrine-packet delivery channel is unspecified.** The 0-of-28 redaction
   result holds for a packet delivered as the *prompt argument*. A packet
   delivered as `CLAUDE.md`/`AGENTS.md`, a skill, or `--append-system-prompt`
   has a different leak profile — notably Codex's rollout embeds `AGENTS.md`
   verbatim in `world_state`. **To establish:** fix the delivery channel first,
   then re-run the echo check on one episode.

## Recommendation

**Claude Code, as input to the owner decision.** Weighted by the stated
criterion — tool-call legibility for transcript-shaped codes — the two surfaces
are not close.

The reasoning, in priority order:

1. **Action-type distinguishability is the crux, and only Claude Code types the
   actions.** Claude Code emits one action per event with a tool `name` and a
   structured `input`; EDIT and READ need no parsing at all, and only the `Bash`
   subset needs classification. Codex emits reads and verifications as raw shell
   strings, 89% of them compound — a single event routinely contains a read, a
   test run, and a filesystem mutation. An interleaving code on Codex is a code
   on a shell parser's output, and its errors are not random with respect to the
   conditions under test: a doctrine packet that changes how the agent batches
   shell work changes parser accuracy at the same time it changes the behavior
   being measured. That is confounding, not noise.
2. **Sequencing evidence exists on one side and not the other.** Claude Code
   timestamps every tool call and tool result to the millisecond (488 of 1,147
   events, 14 episodes). Codex's
   `exec --json` timestamps nothing (0 of 387 events, 14 episodes). Order is still recoverable from stream
   position, so this is not fatal — but any code touching latency, batching
   duration, or think-then-act gaps is simply unavailable on Codex without
   switching to the rollout file, which CAPLAB has never captured.
3. **The silent-rotation threat model is already realized, and Claude Code is
   the harness that showed it.** Slot 2 of the executed calibration ran on
   `claude-opus-4-8` while its record says `claude-fable-5`. The stream said so
   in a typed event and in `result.modelUsage`; CAPLAB did not read it. On
   Codex's `exec --json` there would have been nothing to read. For a campaign
   whose named threat is a version string that does not change while behavior
   does, in-band per-episode model attestation is close to decisive.

Dimensions 3 (write-set) and 6 (redaction) came out **even** — both harnesses
recovered the write-set exactly 12/12, and neither echoes the injected prompt in
0 of 28 captures. Dimension 4 is even and weak for both: no temperature, top-p,
or seed on either. So the decision rests on dimensions 1, 2, and 5, and all
three favor Claude Code.

**Conditions attached to the recommendation.** If Claude Code is pinned, the
campaign should also: derive per-episode subject identity from `system/init`
plus `result.modelUsage` and fail closed on disagreement or on any
`model_refusal_fallback`; drop `--no-session-persistence` (or add
`--include-hook-events`) so a second independent transcript exists; and prefer
artifact-shaped codes for everything except the one unavoidably
transcript-shaped family.

**What would change this recommendation:**

- **Gap 5 comes back the other way.** If double-coding archived transcripts
  shows acceptable inter-coder agreement on Codex, the structural argument loses
  most of its force and the choice reverts to other grounds. This is measurable
  today at zero model cost and should be run before the decision is taken.
- **Gap 2 closes and the codes are re-scoped.** A working non-ephemeral Codex
  rollout capture would erase Codex's timestamp and identity deficits (1 and 5)
  entirely, leaving only dimension 2. If the transcript-shaped code family can
  be narrowed to something the rollout's typed `function_call` / `apply_patch` /
  `patch_apply_end` items answer directly — for example "did any edit occur
  before any file was read" — Codex becomes viable.
- **The subject of interest is `gpt-5.6-terra`.** ADR 0039 makes harness and
  model inseparable. If the research question is about the GPT model, this
  recommendation is void: the harness follows the model, and the design must
  instead absorb Codex's legibility cost by leaning harder on artifact-shaped
  codes.
- **Prior CAPLAB evidence is to be reused as a baseline.** Both existing native
  campaigns ran both harnesses; if comparability with those captures matters
  more than legibility, that is a different weighting than the one this ticket
  specifies.

This record makes no decision and confers no authority. It is input to
CAPLAB-63's owner.
