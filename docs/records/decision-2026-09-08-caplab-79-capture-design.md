# CAPLAB-79: capture design before harness selection

## Authority and scope

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
selects the prospective capture requirements below for the advisory-selection
study. CAPLAB-79 owns capture design; CAPLAB-63 owns harness selection.
Neither decision establishes reviewer capability or authorizes model spend.

Authorized effects are this new record, read-only CLI help/version and public
documentation inspection, and bounded planning projection updates: append
this disposition to CAPLAB-79 and mark that decision item Done; append the
comparison requirement to CAPLAB-63 and implementation requirements to
CAPLAB-84, preserving their states and original descriptions. Re-read each
item before updating and stop on concurrent edits. No comments or messages,
model calls, historical inspection or evidence copying, normalization,
admission, rewriting, scoring, ranking, or placement. Existing instruments,
launch commands, authorizations, and expiry dates remain unchanged. The
September 7 instrument disposition remains in force. Reopening appends a
new decision; it does not rewrite past evidence.

## What maximal capture means

Capture every episode-specific surface exposed by the selected native harness
under a frozen configuration: structured events, stderr, persisted session
records, available diagnostic logs, prompts supplied by CAPLAB, exposed
instruction/configuration metadata, tool requests and results, final messages,
and before/after task inventories. Preserve the original bytes and causal
links between records. A last-message file, rendered transcript, or repository
diff alone is insufficient. Do not substitute a common proxy or a new harness
to obtain richer telemetry.

This is maximal **exposed** evidence under the selected configuration. It is
not complete internal reasoning, an authenticated provider snapshot, proof
that unrecorded events did not happen, or permission to collect unrelated
sessions. Missing fields remain explicit. Capture configuration is part of
the Binding and is identical across arms within a comparison. A change to it
requires a new versioned configuration and renewed comparability checks.

## Candidate configurations

The following options were inspected without a model call on September 8:
Codex CLI 0.153.4 and Claude Code 2.1.260. These are an inspection baseline,
not a roster or version-selection decision. Before execution, the selected
version must pass the same capability checks; help text alone does not prove
that the requested evidence is emitted by a particular account or model.

| Surface | Codex CLI | Claude Code |
| --- | --- | --- |
| Event output | `exec --json --color never`; retain stdout and stderr separately | `--print --output-format stream-json --verbose --include-partial-messages`; retain stdout and stderr separately |
| Persistence | Omit `--ephemeral`; preserve the exact thread's rollout plus any episode-linked child rollouts | Omit `--no-session-persistence`; preserve the exact session transcript and episode-linked child transcripts |
| Additional exposed events | Pin `hide_agent_reasoning=false`; retain emitted summaries and exposed native events without requesting unsupported internal content | Add `--include-hook-events` where supported by the pinned CLI; retain deltas as well as completed messages |
| Diagnostic capture | Preserve episode-specific native logs produced in the isolated runtime; record absent diagnostic surfaces explicitly | `--debug-file <episode-private-path>`; retain the whole diagnostic file in restricted raw custody |
| Final artifact | `--output-last-message <episode-private-path>` is a convenience copy; verify it against the native event stream | Preserve the final result event and any task output; link it to its session and source events |
| Input evidence | Preserve exact prompt bytes and configured instruction files separately; link thread ID from stdout to the persisted rollout | Preserve exact prompt bytes and configured instruction files separately; pin a unique session ID. With stream-json input, also use `--replay-user-messages` |

Codex's documented `--ephemeral` discards session persistence; `--json`
provides the event stream. These are separate capture surfaces, and neither
can replace the other. [OpenAI non-interactive documentation](https://learn.chatgpt.com/docs/non-interactive-mode)

`hide_agent_reasoning` suppresses exposed reasoning events; the separate
`model_reasoning_summary` setting changes requested summary detail. Select
`detailed` where the pinned model supports it, record lack of support, and
never infer support from a configuration key alone. Treat the request as a
behavior-bearing configuration, fixed across arms. `history.persistence`
controls `history.jsonl`; it is not proof of rollout custody. Preserve all
episode files from an isolated runtime instead of depending on shared prompt
history. [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

Claude's stream, partial-message, verbose, debug-file, replay-input, and
persistence options are documented. The locally installed CLI additionally
lists hook-event capture. Its `--system-prompt-snapshot` switch changes prompt
reuse as well as recording: record its effective setting and any exposed
snapshot, but do not change prompt construction merely to add a log. If a
required instruction surface is unavailable, record that limit before harness
selection. [Claude CLI reference](https://code.claude.com/docs/en/cli-reference)

No tool, permission, sandbox, account, memory, skill, hook, or subagent behavior
is enabled merely for capture. Freeze those separately as subject conditions.
When a study permits child agents, their linked transcripts are required;
when it does not, a child invocation is a condition violation, not a reason to
discard its evidence. Do not resume a prior episode or discover sessions by
"latest" filename. Bind every selected file to the launched thread/session,
configured subject, trial assignment, source path, content hash, and custody
root. Stop on ambiguous linkage or changing source bytes.

## Identity, ordering, and write-set evidence

Keep configured model/effort/harness fields separate from native-reported
fields and provider-authenticated evidence. Codex session metadata and turn
contexts support a native configuration consistency check; they do not
authenticate the backend model actually served. Claude initialization,
assistant-model fields, explicit fallbacks, and usage maps are distinct
observations. An auxiliary usage-model name alone does not establish primary
response authorship. Any required identity field that is missing prevents
attribution; explicit off-pin identity stops continuation and withholds the
score while retaining the assigned denominator.

CAPLAB-79's historical wording conflates two failures. The CAPLAB-78
annotation identifies a Claude fallback already present in Claude stdout.
Codex's ephemeral setting did not cause that Claude parser omission, and
adding a Codex rollout would not independently detect the Claude event.
Codex persistence addresses its own missing context evidence. Neither fact
supports declaring Codex superior or inferior in legibility.

Preserve native order, native timestamps when exposed, and host monotonic
receipt times as separate clocks. A receipt timestamp is not an event's
execution time. Pair tool requests/results by native IDs, keep partial and
completed records without double-counting actions, and make compaction,
truncation, unmatched calls, and missing terminal records explicit.

The episode write-set requires a sealed initial inventory and final inventory
of all permitted writable task paths, including untracked, deleted, renamed,
binary, and mode-changed files. A final Git diff is supplemental. Transcript
edits show proposed or reported actions; inventories show observed final
effects. Neither proves every intermediate write. Verification actions must
retain command, working directory, exit/termination status, and captured
result so a code can distinguish an edit from a completed test.

## Storage, custody, and redaction costs

Let E be structured events, L persisted session/child logs, D diagnostic logs,
P supplied prompts/configuration evidence, and W retained task artifacts,
all measured in bytes for one episode. Raw retained size is
R = E + L + D + P + W. These may overlap semantically; preserving two native
surfaces can duplicate content without creating two independent observations.
With N normalized bytes, B bytes of blinded coder material, and M bytes of
manifests/redaction maps, retained logical size is R + N + B + M. If each raw
file remains at its native runtime location while custody is copied, peak
logical storage adds another E/L/D contribution until verified cleanup.
Backups and filesystem allocation add separately; compression savings are not
assumed. These are accounting formulas, not observed campaign measurements.

Before an authorized shakedown starts, its manifest must freeze the maximum
retained bytes per episode and campaign, concurrent-copy allowance, and free
space reserve. The launcher must write streams to bounded disk sinks rather
than accumulate unbounded subprocess output in RAM. At a capture limit,
retain the captured prefix and explicit truncation record, terminate that
attempt, and stop the campaign. Never silently drop logs to stay under budget
or count the truncated attempt as a valid episode. A numeric cap is an
execution-budget decision based on measured representative captures; this
record does not invent a measured byte rate or renew spend permission.

Raw custody is private: directory mode 0700, file mode 0600, host-owned and
outside the agent-writable task mount. Credentials and unrelated home/session
files are not capture inputs. Native session files written by the harness
must be copied or sealed into host-owned custody before interpretation, with
source/destination hashes and session linkage verified. Do not delete native
sources until that check and an explicit cleanup authorization are satisfied.
Hash consistency is not independent provider authentication or immunity to
changes before the custody boundary.

Redaction cost expands with every duplicate surface: prompts can reappear in
partial chunks, completed messages, tool arguments/results, logs, child
sessions, exposed summaries, paths, comments, and generated artifacts. The
blinded projection and its private provenance map must identify exactly what
was transformed or excluded. Native raw evidence remains unchanged. Merely
removing an exact packet string or passing a keyword scan cannot verify the
absence of paraphrases or other arm cues. CAPLAB-66 must determine feasibility
on representative captured repair episodes before coder exposure.

Empirical bytes/episode, capture latency, redaction runtime, manual adjudication
time, and coder-blinding success are **unmeasured for this selected capture
configuration**. CAPLAB-84 must report those costs per surface and harness,
including failures and tail cases, before budget extrapolation. There is no
assumed per-token dollar charge for subscription usage and no model-API price
substituted for it. Wall time and account-capacity consumption remain separate
cost observations. This design accepts increased raw storage and redaction
work as necessary to evaluate the actual construct; it does not assert that
the added evidence is free or that redaction is feasible.

## Comparison decision and remaining implementation

**Re-measure CAPLAB-63's tool-call legibility comparison under the selected
maximal exposed capture before pinning a harness on that criterion.** Do not
use the earlier capture's missing fields as inherent harness deficits. A
comparison must name exact native versions, configurations, models/accounts,
task inputs, episode limits, and capture/redaction versions. Compare tool
request/result linkage, edit-versus-verification discrimination, write-set
recovery, identity observability, and missingness explicitly. Keep capability
claims and harness legibility separate; a more verbose transcript is not
evidence of a more capable reviewer.

Use model-free fixtures to qualify capture and failure mechanics first.
Representative real repair episodes are required for claims about legibility,
resource cost, and blinding. Any live comparison requires a new exact
authorization consistent with the September 7 disposition. This decision
does not revive an old shakedown budget or authorize a new comparison now.

CAPLAB-79's three decision questions are resolved here: candidate capture
configurations are selected, cost accounting and unmeasured empirical costs
are stated with owners, and re-measurement is required. Implementation and
acceptance remain separate: CAPLAB-84 owns integration and measurement,
CAPLAB-66 owns redaction feasibility, and CAPLAB-63 owns comparison and harness
selection. CAPLAB-71 must freeze the final behavior-bearing parameters.

At source 406e68c, review-dissent scoring and continuation have a model-evidence
gate, but its Codex invocation still uses the frozen ephemeral command and
has no rollout integration. The artifact-rater path retains Codex rollout
attestation separately. Neither path establishes the complete design above.
Existing subprocess buffering, streaming-event tolerance, session linkage,
full write-set capture, quotas, and redaction must be verified during
integration. Done on CAPLAB-79 means a capture decision exists, not that a
campaign is ready or the full roadmap is complete.


## Verification and advisory receipt

This is a documentation and planning decision. No runtime source, frozen
instrument, model configuration, or historical capture changed. The CLI
help/version commands completed without starting a model episode. The private
inspection receipt `/tmp/caplab-79-capture-inspection.json` has SHA-256
`1914680ea868e09f03fbe1266ac7dc49e4a3078b0e35c9362f3c6a70bf4d8486` and retains the help-file
hashes and inspected versions. The cited official pages were opened and read
on September 8. The documentation guard checked flag spelling, distinctions
between capture and behavior settings, source implementation claims, numeric
cost formulas, and the three ticket completion criteria. A help flag proves
an advertised option; emission and interoperability remain integration tests.
No full test suite was rerun for this documentation-only decision.

Advisory packet `pkt-19c57e15eae849e9`, content SHA-256
`19c57e15eae849e9f34b3e0e8eec2c45284317b6f5233af9916833586c2037dd`, uses release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts are
`universal-evidence-before-intervention`, `universal-explicit-invariants`,
`universal-repository-contract-precedence`, and
`agent-conduct-authority-bounded-action`. The decision assigns each required
capture surface and failure rule to an implementation owner while keeping
selection, execution, and acceptance distinct. Citation consumption is
recorded locally.

Remaining advisory obligations are nonmaterial to this capture-design decision:

| Concept | Missing requirements | Scope reason |
| --- | --- | --- |
| debugging-causal-repair | causal explanation; changed path exercised after repair; failing reproduction before repair; first divergence; relevant regression evidence | No new runtime repair is claimed. The prior identity repairs are referenced separately; this decision does not rerun or expand their acceptance. |
| operations-contract-conformance-testing | consumer-owned contract tests with a run cadence; request-side and response-side suites separated from live dependencies; shared specification as oracle; the shared specification as the test oracle | Capture conformance is an explicit remaining integration requirement. The design is selected, but no working full capture implementation is asserted. |
| task:repository-assessment | evidence-co-change; evidence-generated-artifacts; evidence-tests; evidence-version-history | No code reorganization, coupling metric, generated artifact, or performance conclusion is made. Current source, help, official documentation and issue contracts support this bounded design choice. |
| testing-deterministic-async-observation | bounded deadline and failure diagnostics; observable completion criterion; observable completion or progress contract; repeated or adversarial scheduling results | No asynchronous mechanism was changed or verified. Completion and bounded capture tests remain part of the required implementation. |


## Planning projection verification

CAPLAB-79 was moved to Done after the decision was recorded. CAPLAB-63 and
CAPLAB-84 received the comparison and implementation requirements above;
their states were unchanged. Each item was re-read immediately before its
update, and the stored description and state were verified afterward. Original
HTML content, names, priorities, assignments, labels, parents and dates were
preserved. No comments or messages were sent.

Receipts are `/tmp/caplab-79-after-capture-decision.json`,
`/tmp/caplab-63-after-capture-decision.json`, and
`/tmp/caplab-84-after-capture-decision.json`. The refreshed projection is
`/tmp/caplab-roadmap-after-79.json`: 18 roadmap items remain open.
No claim of overall roadmap completion or instrument acceptance is made.
