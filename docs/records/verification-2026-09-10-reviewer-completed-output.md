# First completed native review and independent behavior check

Output-probe-3 produced a complete final review in **474.97 seconds**, using
Codex CLI 0.153.4, reported model `gpt-5.6-terra`, effort `max`. The final file
matches the last completed native agent message byte-for-byte. The root
rollout and stdout agree on the thread identity and reported configuration.
All 83 capture files passed the selected privacy guard and their retained
hashes were rechecked. Both task source inventories still match their plans.
The original authentication cache and pinned native package are unchanged.
The native stream reports 7,609,789 input tokens, including 7,356,416 cached
input tokens, and 20,076 output tokens. These are cumulative reported usage,
not unique task size or a dollar-cost calculation.

This is unscored development evidence. It is not a comparative measurement,
complete Binding qualification or a reviewer ranking.

## What the review actually reported

The final review reports one finding about topic creation. It supplies the
affected service locations, one DeepSeek member, no credential seeds, an empty
selected root, a root-entry limit of 1, and an observed 422
`credential_scope_conflict` response. It attributes the response to a bounded
scan whose error is converted into a credential-conflict error.

The final review does **not** report the previously verified provider
timeout/cancellation defect. No keyword count or intermediate reasoning has
been converted into detection credit. The newly reported issue is preserved
even though it was absent from the original known-outcome witness.

## Independent reproduction of the new finding's behavior

The local witness was written after reading the final finding, but its
configuration comes from the original protocol example, not from the
reviewer's reproduction script. It imports the exact original source and
uses the public configuration parser, service initialization, topic creation
and credential-root validator. Only the root-entry bound changes between
conditions; other limits retain the protocol defaults. There is one empty
selected root, no credential seeds and a synthetic API-key environment value.

| Condition | Direct validator | Topic creation |
| --- | --- | --- |
| Entry limit 1, three fresh runs | `capture_limit_exceeded` | 422 `credential_scope_conflict`, all three |
| Entry limit 100000, three fresh runs | Empty credential identities | Topic created, all three |

All configurations parsed successfully. Each observation records an empty
credential-source list and empty selected root. All six processes exited
normally in network-disabled namespaces, with no provider request. Source and
dependency hashes were rechecked. The service/runtime-pinning implementation
is part of the original change and absent from its first-parent source tree.

The behavior and error conversion are therefore corroborated. The finding's
broader interpretation needs qualification: the original protocol also requires
protection of Council-home inodes, even when there are no credential seeds
(`PROTOCOL-v3.md`, the paragraph beginning “Before each native view capture”).
An accepted limit value does not guarantee that a later scan fits within it.
Zero credential seeds alone therefore does not establish that scanning should
be skipped or that topic creation must succeed with this bound.

The observable issue is that a scan-limit failure is presented as a conflict
with a configured credential source. Whether that error classification is an
actionable contract violation, and its severity, must be resolved separately
from confirming the failure occurred. No whole-finding true/false label or
ranking credit is assigned here. This distinction prevents a mechanically
reproduced failure from automatically becoming a confirmed product defect.

## Administration and remaining validity work

The corrected guard's version 3 preserves ordinary `password` category and
`groups` field-name text while protecting private values and credential bytes.
It retains all 163 authorized task files; version 2 rejects six of those same
files. The full repository suite passed **1,522 tests with four skips**.
The old profiles and the two failed native attempts are preserved.

The third task disables apps, plugins, remote plugins and skill search. Its
recorded tool activity includes 58 completed shell commands and one reported
edit to a temporary TypeScript-loader file. The reviewer attempted the project's test command,
found dependencies absent, and explored a globally installed TypeScript
compiler under `/lib/node_modules/openclaw`. That extra runtime was not pinned
as a project dependency before execution. The final review states the missing
test/dependency coverage. Future comparisons need a prepared, pinned project
test environment and complete accounting of meaningful tool access; this
probe cannot silently become a comparison trial.

The output now contains a concrete finding whose factual claims can be checked.
Next work is a scoring procedure that distinguishes attribution, observed
behavior, requirement violation and severity, then challenges that procedure
on correct findings, wrong claims, duplicates and unresolved reports. The
[effort-control candidate](verification-2026-09-10-reviewer-effort-control.md)
adds real valid-change preservation evidence for that work. Broader case
coverage and held-out comparisons remain required.

## Custody

The [development receipt](../product/studies/reviewer-ranking-001/completed-output-development-receipt.json)
anchors the native plan/runner/capture/final/verification and the independent
witness inputs, source provenance, six process records and verification.
Owner-private roots are `output-probe-3` and `topic-credential-witness-1` beneath
`~/.local/share/caplab/reviewer-ranking-001/development/`. Source and native raw
content remain there; neither is registered as study evidence. No Council
checkout was changed and no further reviewer invocation follows from these
consumed authorizations.
