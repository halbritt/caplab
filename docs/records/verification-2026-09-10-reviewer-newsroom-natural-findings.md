# A natural reviewer finding confirmed beyond the initial answer key

The prospective native review of newsroom change
`544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f` reported three defects. Original-code
investigation confirms one new configuration defect, refutes the application
of a publisher-lock requirement to the harvester, and leaves the third claim
unresolved. The review did not report the independently known recovery-deadline
defect. No precision, recall, false-blocker rate or ranking is computed.

## Findings and their independent basis

| Natural finding | Original-code observation | Development assessment |
| --- | --- | --- |
| Harvested mode incorrectly requires optional RSS | Healthy HTML harvest stores three candidates; a fresh adapter reads them. Disabling only `rss_fallback` makes both harvest and pool fetch fail before HTTP despite the supplied directory and valid pool. | Confirmed introduced configuration defect. |
| Harvest must refuse while `run.lock` is held | Under a separately held kernel lock, original harvest returns 0 and stores candidates, `run` returns 2 before HTTP, and pool fetch returns 0 without HTTP. | The cited publisher-exclusion requirement does not require a non-publishing harvester to refuse. This contract application is refuted; the reported concurrent behavior is real. |
| HTML/JSON listings bypass the new 65-second interval | Three real HTTPS listing requests arrive within 0.012 seconds in every execution. The base already dispatches them this way. No pacing reservation appears after HTML harvest. | Requirement scope and change attribution remain unresolved. Existing concurrent mechanics do not settle whether their use violates a newly broader promise. |

The first finding concerns a configuration that the documentation describes
as supported: the harvester tries HTML/JSON, then optional RSS when enabled.
The new module also calls RSS an optional fallback. The newly added constructor
creates `RedditState` only when both a directory and RSS fallback are enabled;
the new harvest and pool paths then reject the absent state. A working HTML
endpoint and already populated pool distinguish that coupling from a missing
directory, unavailable provider or unsupported feed. This defect was outside
the initial answer key and remains a candidate family for later admission.

The lock requirement predates the reviewed change. Its README wording is
unchanged across base and change, and the unchanged engineering-review
requirement explicitly says that locking prevents overlapping live publishers.
The systemd documentation describes the fetch/curate/deliver `run` workflow.
The harvester is explicitly independent and performs no publication or
delivery. The original `run` control correctly refuses under the held lock.
This refutes the finding's application of that particular requirement. It
does not establish universal safety of concurrent harvests or negate their
observed ability to run under the lock.

The pacing observation is real, including at the network boundary. The
transport helpers and listing executor statement are AST-identical in the
base and change. The new README's minimum-interval language appears in the
provider-state and feed-cache discussion; whether it promises to pace the
existing HTML/JSON path is not independently settled. Preserve that disputed
scope and the verified inherited mechanics separately. No inference is made
about actual Reddit 429 incidence.

All three complete findings, their byte offsets and the final review hash are
retained in `claim-investigation.json`. Their interpretation is attributed
to the primary agent and grounded in the named source and execution evidence.
It is not an independent verdict on the investigator or acceptance of a
general semantic scorer. The known 180-second active-body family is absent
from these three findings; the 65-second inter-request claim is a different
scenario. Shared timing vocabulary earns no credit.

## Prospective review and task readiness

The reviewer received the complete original change, base, diff, documentation
and tests. Neither the deadline witness nor hidden assessment obligations were
mounted. The original suites passed in isolated, network-free preparation:
594 base tests and 623 change tests. These are readiness observations, not
truth labels. The copied dependencies, Python runtime and 188 original
source files were pinned before execution and checked afterward.

The native review used Codex CLI 0.153.4, `gpt-5.6-terra`, effort `max`, with a
900-second outer limit and a twelve-minute investigation stop. It completed
in 464.94 seconds. All 76 captured files are retained; one rollout omits 56
opaque encrypted-reasoning fields under the existing hash-receipted projection.
Readable capture is complete. The final text equals the last native agent
message, and native metadata and turn contexts agree on identity. The native
package and owner auth cache remain unchanged.

The recorded tools are shell executions against the supplied task and local
runtime, including source inspection, systemd syntax checks and changed-path
tests. They include the reviewer's unsuccessful test command that overwrote
`PYTHONPATH`, followed by a successful command using the provided environment.
No recorded command searches the web, opens hidden study custody, inspects
authentication or invokes a target service. This is a recorded-tool audit,
not a complete kernel network/process trace. The native reviewer's own
patched-function demonstrations are preserved but do not supply the
independent outcome basis used above.

## Source preflight failure and correction

The [first preparation](authorization-2026-09-10-reviewer-newsroom-natural-output.md)
launched no model. Credential-private-text/v3 rejected ordinary `user_id`
parameters in six original source files because that public field name also
occurred as a token claim key. Its source, plan, runner, readiness and failure
remain unchanged in `newsroom-natural-output-1` custody.

The [corrected authorization](authorization-2026-09-10-reviewer-newsroom-natural-output-2.md)
introduces v4 without changing v1-v3. It recognizes only a nonempty string
`user_id` key directly under the authentication claim; its value remains
private. OpenAI's original [token parser](https://github.com/openai/codex/blob/main/codex-rs/login/src/token_data.rs)
declares this public alias. Equal text at private occurrences, token material,
unknown paths and malformed shapes remain guarded. There is no global string
allowlist or source redaction.

The new regression first failed because v4 did not exist. Thirteen credential
tests now pass, including private-value, private-occurrence, malformed-shape,
split-stream and unchanged-old-profile controls. A real-task comparison checks
all 191 supplied files: v3 rejects six; v4 retains all bytes unchanged. The
second preparation reuses the original successful test-readiness evidence;
it does not rerun or relabel those observations.

## Independent execution, custody and limits

The [finding-witness authorization](authorization-2026-09-10-reviewer-newsroom-findings-witness.md)
names the subsequent six model-free executions. The investigator had seen
the natural output; original requirements and real endpoint/database outcomes
supply the independent basis. Frozen valid HTML listings reach unchanged
urllib, parsers, executor, adapters and CLI functions over local HTTPS.
No source clocks, functions or loaders are stubbed. Test configuration is an
explicit read-only input mount. An independent descriptor retains the actual
kernel lock throughout the CLI controls.

Two repetitions of each condition agree semantically. Six executions finish
in 4.32 seconds and preserve 30 capture files, including the original SQLite
databases, CLI output and actual request timestamps. No real Reddit, model,
Slack or deployment call occurs in these witnesses. Three checker tests reject
empty listing controls and ineffective lock controls, and ensure that disabled-
RSS outcomes are observed rather than assumed defective.

Private custody roots are under
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/`:
`newsroom-natural-output-1`, `newsroom-natural-output-2` and
`newsroom-findings-witness-1`.
The [native receipt](../product/studies/reviewer-ranking-001/natural-output-development-receipt.json)
pins preparation, complete capture, the failed preparation and native identity.
Administration SHA-256:
`f0ee550e86fc87044a2b1741904adfba1ccb6916c875268c63dd9f29deaaba57`.
The [finding receipt](../product/studies/reviewer-ranking-001/natural-findings-development-receipt.json)
pins source lineage, original requirement context, independent execution and
the full claim investigation. Witness verification SHA-256:
`d101743663feb7eec75928ace7fdc8aa4728395ccb25a859be5a341e4a056b7c`.
Claim investigation SHA-256:
`e582d9ca56ff52deecf46f68eb6133a12aeed46b7a41e3dc11cd28ca08e86acb`.

`make check` passes: 1,540 tests in 197.31 seconds, with seven skips.
Both verifications reproduce exactly. All 95 receipt artifact hashes, all
native capture entries and all 32 coverage identities were rechecked; each
finding's byte range binds its complete text to the retained native review.
These checks do not accept a semantic scorer or the ranking instrument.

The existing doctrine packet `pkt-cdafd666a23adaf1` remains applicable to
separating claim attribution, observed behavior and requirement violation.
The release gate passed for corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Repository requirements govern these assessments. General semantic validity,
coverage and ranking acceptance remain material, unmet obligations.

## Consequences for a defensible ranking

The answer key must remain open to new verified findings. Reproducing a
reviewer's claimed behavior is insufficient when its normative scope or
attribution is wrong or unresolved. This natural review also supplies no
explicit blocking/advisory disposition. A future frozen administration must
elicit that distinction before it can measure incorrect blockers; it cannot
be invented after seeing a result.

The current closed-hypothesis interpreter is not accepted for natural reviews
containing several findings. Each finding needs its own claim, trigger,
location and evidence relationship, with unresolved cases preserved. Neither
matching keywords nor borrowing a location from another finding establishes
correct attribution. Prospective scoring challenges remain necessary.

Coverage remains seven of 32 selected changes with bounded change-specific
witnesses. The new base listing execution changes one selected row from
pending to baseline-only: three now have only baseline-witness evidence and
22 remain pending. Its separate Particle change is still unverified. Multiple
findings within this one newsroom change do not add independent sampled cases.
No case is admitted, no reviewer ranking is accepted, and the goal remains
active.
