# Check tool-pair interpretation against one retained Claude repair

Date: 2026-09-08. Baseline: `b994f6e`. Primary-agent authority:
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before discovery

Add this record. Inspect only immediate entry names and file kinds under
`~/.local/share/caplab/campaigns/` (at most 100 entries), then record one exact
repair-campaign root and its slot-selection rule before further discovery.
Prefer the lexicographically first advisory-selection shakedown campaign,
without opening scores or outcomes. Within the chosen campaign, bounded
immediate-child inventories may locate its attempt directories. Record exact
selected paths before opening any historical contents. Stop on symlinks,
ambiguous structure or an absent eligible source rather than searching by outcome.

The intended observation is native tool/request/result structure in one retained
Claude repair. It is not a representative sample, current maximal-capture
verification, coding judgment or harness selection. Before content inspection,
name the exact native stdout and independent session-identity source, with a
combined byte allowance and required source hashes. If independent identity is
absent, record that limitation; never derive an expected ID from the same stdout
merely to make the reporter pass. A filename's model label does not authenticate
the harness or served model.

After that exact source amendment, permit read-only hashing and in-memory
structural inspection, the existing report API/CLI, and private derived reports,
counts, IDs and line/hash references under `/tmp/caplab-claude-tool-pairs-*`.
No transcript text, tool commands, outputs, task prose or credentials may be
copied into a new artifact. No historical commands, native harnesses or models
may execute. No current receipt chain may be fabricated for historical inputs.

Do not admit, register, rewrite, purge, relabel, score or expose this episode to
coders. Preserve historical custody, runtime/tests/contracts, study exclusions,
`docs/designs/`, sibling worktrees, services/timers and tracker state. No spend,
ranking, placement, external message or push. A demonstrated parser defect
requires a subsequent scoped repair authorization before runtime edits.
Consolidate advisory evidence before deleting named scratch, retain source and
inspection provenance, and commit this record locally. Authorization expires
at commit; stop before any broader effect or weakened interpretation boundary.

## Selected campaign metadata scope

The authorized root inventory found 15 directories and no symlinks. Its only
advisory-selection shakedown is
`~/.local/share/caplab/campaigns/advisory-selection-001-shakedown-2026-07-26/`.
Select that exact root. Inspect at most 100 immediate children to locate the
slot container, then at most 200 immediate slot entries in that named container.
Select the lexicographically first slot directory regardless of arm, completion
or outcome. Inspect at most 100 immediate entries of that selected directory.
Do not skip an absent/unusable first slot to obtain a successful example.
This amendment authorizes metadata discovery only; source content paths remain
to be named before reading.

The exact slot container is `attempts/`; it has 96 immediate entries.
The filename-only rule selects `attempts/SC-01-injection-01/`. Inspect only
its immediate file metadata before naming the content-read set.

## Exact content inspection scope

The selected slot has seven immediate entries and no symlinks. Authorize reading
only its `episode.json` (389 bytes) and `native.stdout` (75,994 bytes), with a
combined one-MiB allowance. Hash both before interpretation and retain those
hashes as the inspection anchors, then verify them after inspection. These are
new read-time anchors, not claims of an earlier independent seal.

Inspect only field names, session/episode identifiers, native event kinds,
request/result IDs and scope, source pointers, and exposed lifecycle/outcome
structure. Do not retain task or tool bodies. `episode.json` may supply the
independent session ID if it records one; if not, report its absence before
considering any additional source. Leave diff, prompt, write set and world
contents unopened. No other episode or manifest is in this content-read scope.

## Separate persisted-identity lookup amendment

`episode.json` has no session-ID field. Before calling the tool-pair reporter,
authorize reading the fixed stdout initialization's `cwd` as a lookup hint.
For a short absolute ASCII path, inspect only the corresponding exact
`~/.claude/projects/<sanitized-cwd>/` directory, where non-alphanumeric
characters become hyphens. This is the short-path mapping in the previously
retained official session-reader source
`/tmp/caplab-claude-link-official-sessions.py`; it is a candidate default location,
not proof of the historical effective configuration directory.

Inspect at most 100 immediate entry names/kinds there. Require exactly one
regular non-symlink `.jsonl` file regardless of the ID in stdout before naming
it as an additional content source. No ID-based or newest-file selection,
recursive search, alternate home/configuration discovery or unrelated session
read is authorized. If the directory or unique file is absent, retain the
identity gap and continue only the already-authorized structural observations.
Do not derive the expected root from stdout. Any selected transcript needs an
exact path/hash and combined input allowance before interpretation.

## Observations

The selected stdout has SHA-256
`ed7aceba46ee219a1af3379cf948da4d914b2f05a6ac641f0c76015f152ba997`
and 75,994 bytes. The episode record has SHA-256
`bdfc41e4ffea8783267a1aa2c1652f292699c1ccbbff8e7a8d33dd3612a2f39a`
and 389 bytes. Both hashes remained unchanged. These read-time anchors identify
the inspected bytes; they do not establish an independent historical seal.

The episode record has slot/scenario/arm/trial and execution-summary fields,
but no `session_id`, `sessionId` or `thread_id`. The default project directory
computed from the stdout's exact task cwd was absent:

`~/.claude/projects/-home-halbritt--local-share-caplab-campaigns-advisory-selection-001-shakedown-2026-07-26-attempts-SC-01-injection-01-world/`

No other project or configuration directory was searched. This observation
cannot establish that persistence was disabled or that no transcript exists
elsewhere. It does establish that the authorized sources did not supply an
independent expected session ID. The tool-pair API and CLI were therefore not
called. No same-stream expected ID, substitute episode or new historical
capture receipt was used to obtain a passing report.

Strict UTF-8, unique-key JSON inspection of the fixed stdout found 78
newline-terminated event records. Each top-level session ID was the same
observed value, `e00a7640-edb0-4856-9470-ec8c960561bf`; all 78 lacked a non-null
parent scope. Agreement within this one stream is an observation, not the
missing independent session anchor or proof of no child activity.

| Observed event/block class | Count |
| --- | --- |
| System initialization | 1 |
| Rate-limit event | 1 |
| System `thinking_tokens` events | 34 |
| Assistant messages | 26 |
| User messages | 15 |
| Result with subtype `success` | 1 |
| Assistant `tool_use` blocks | 15 |
| User `tool_result` blocks | 15 |

Tool-use names were Bash (6), Read (5), Edit (3) and Write (1). Other assistant
blocks were seven thinking blocks and four text blocks. These are distinct
record/block units. Equal request/result counts do not establish unique
associations, execution success, complete capture or readable coding evidence.
A successful result subtype likewise supplies no task-correctness judgment.
No command string, tool result text, task prose or historical score was copied.

The current pure reporter explicitly retains unfamiliar events as unclassified
source references. The observed `thinking_tokens` and `rate_limit_event` kinds
fall outside its specialized tool/outcome branches. That is not evidence of
lost tool requests or a Claude capability deficit. Neither unclassified-event
counts nor raw tool-name counts provide a cross-harness legibility comparison.
No semantic claim about the rate-limit event's cause or effect is made.

## Verification and interpretation

`/tmp/caplab-claude-tool-pairs-structural.py` performed the bounded inspection.
Its structural report at `/tmp/caplab-claude-tool-pairs-structural/report.json`
has SHA-256
`7e2451c5f6f3f5c8a1dfa379b240cacbaa92782ceb0fb2f8c7f71ab9648f4e96`.
It retains all 78 exact line/byte/hash references and the source pointers for
content-block types, tool IDs/names and reported error flags. It contains no
pairing status or substituted independent-identity claim. The source spans
sum to the entire 75,994-byte stdout. The summary is
`/tmp/caplab-claude-tool-pairs-result.json`.

This supplies structural observations and a concrete identity-source gap for
one filename-selected historical repair. It does not verify native tool-pair
compatibility, current maximal-capture emission, semantic coding legibility,
harness/model identity, blinding or reviewer quality. No parser defect was
established, so runtime/tests/contracts remain unchanged. Synthetic fixtures
remain the Claude reporter's standing compatibility evidence until an exact
independently anchored native input can be inspected.

The next admissible compatibility check needs a separately retained configured
session or persisted transcript identity together with the stdout. That is an
input requirement, not a reason to relax the reporter or infer missing identity
from its own input. The historical shakedown still cannot become current study
evidence through this inspection. CAPLAB-63, CAPLAB-66 and CAPLAB-84 remain open.

## Advisory disposition and closure

The validated Pincite release is `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`. Final packet:
`pkt-38c6d81e8ca4e0e6`; content SHA-256:
`38c6d81e8ca4e0e6bf88e22cfcd1bd067702b1609d4fbd35ace077977b4a8a24`. Applied repository-contract precedence,
evidence before intervention, explicit invariants and authority-bounded action.
The packet's execute ceiling does not supply authority or fill the missing
independent session evidence.

Thirty generic obligations remain nonmaterial to the narrow structural/gap
finding: no causal repair or production incident is claimed; no co-change,
generation, version-trend or standing-suite adequacy assessment is made; no
asynchronous mechanism or module interface is changed; no representative cost,
architecture benefit or broad latent-risk audit is asserted. Formal procedure
exports and an exhaustive repository-contract audit are not part of this
single-source inspection. Each obligation has an individual rationale in
`/tmp/caplab-claude-tool-pairs-verification.json`. The broader compatibility
claim is explicitly withheld because its session-identity prerequisite is absent.

The consolidated verification artifact pins source identities, all three
metadata discovery steps, the exact default-path lookup, structural/reference
checks, advisory packets and citation classifications, and the completed record.
Nine named advisory scratch files are removed after their content is retained
there. No source or derived structural report is removed. Source content hashes
are checked again before closure; no transcript body is included in the new
repository record or copied into advisory artifacts.

Only this record is committed locally. Runtime and tests are unchanged, so the
repository suite was not rerun. No live attempt, tracker update, code judgment,
harness selection, independent acceptance or roadmap completion occurred.
The source-inspection authorization expires at commit. The active CAPLAB goal
remains incomplete, with a concrete next requirement for independently anchored
native captures rather than a relaxed identity check.
