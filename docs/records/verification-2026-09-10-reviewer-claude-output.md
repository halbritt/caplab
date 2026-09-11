# Native Claude review produces independently inspectable findings

One native Claude Code 2.1.268 / `claude-fable-5` / configured max-effort
review completed on the existing newsroom development change. It found the
independently verified optional-RSS configuration defect and reported three
additional advisory concerns. Those concerns receive separate assessments;
valid JSON and successful execution do not make them correct findings.

| Reported finding | Reported stance/effect | Independent development assessment |
| --- | --- | --- |
| Optional RSS disables harvest storage and pool reads | Asserted / advise | Confirmed introduced configuration defect. The existing original-path witness has healthy HTML, disabled-RSS and populated-pool controls; source locations identify the exact constructor gate and affected entry points. |
| Curation traces accumulate without a retention bound | Asserted / advise | Per-run directory creation and repeated prompt storage are visible in source. No independent retention requirement or bounded capacity expectation has been established. Operational defect status remains unresolved. |
| HTTP error body details disappear from curation errors | Asserted / advise | The base/current source contrast confirms removal of the error-body excerpt. No new original HTTP execution was performed here. The required diagnostic/privacy tradeoff is unresolved, as the reviewer itself acknowledges. |
| Oneshot failure restart requires systemd v250 | Uncertain / advise | The version cutoff is refuted by upstream v244 source and documentation. Target deployment version and relevance of older-host compatibility remain unverified. This advisory concern is not an incorrect blocker. |

All four complete findings, their explicit qualifications, source locations,
content hashes and occurrence IDs are preserved in the
[receipt](../product/studies/reviewer-ranking-001/claude-output-development-receipt.json).
The previously verified 180-second active-response deadline violation and
partial-RSS-refresh success-exit defect are absent from the final findings.
This is a bounded inspection of one report, not a recall rate or comparative
ordering. All four effects are advisory; a false-blocker rate is not inferred.

## Independent basis

The optional-RSS finding refers to the exact constructor and entry points in
`newsroom/sources/reddit.py`, with configuration context. The prior original
[behavioral witness](verification-2026-09-10-reviewer-newsroom-natural-findings.md)
and claim investigation were hash-checked unchanged. They establish that a
working HTML source and an already populated pool both fail when only the
optional RSS flag is disabled. The reviewer's own reproduction does not supply
the independent truth basis.

The trace module creates a fresh directory in `capture`, writes the candidate
packet and serializes each attempt's request. Its source contains no pruning.
The README promises private incident-recovery records but names no retention
period. That observation alone cannot establish an actionable retention defect.
Similarly, the original HTTP handler included an error-body excerpt and the
new handler preserves only the status code. The README excludes API keys and
provider reasoning from records but does not require raw error bodies. Preserve
the observed source change separately from its unresolved operational judgment.

The official [v243 validation predicate](https://github.com/systemd/systemd/blob/efb536d0cbe2e58f80e501d19999928c75e08f6a/src/core/service.c#L581)
rejects non-no restart settings for oneshot services. The
[v244 predicate](https://github.com/systemd/systemd/blob/db9c5ae73e23d816e2df2a3e10a9a2a60b5b3ed7/src/core/service.c#L577)
explicitly permits failure restart, and its
[manual](https://github.com/systemd/systemd/blob/db9c5ae73e23d816e2df2a3e10a9a2a60b5b3ed7/man/systemd.service.xml#L1333)
excludes always and on-success. This is a concrete pre-v250 counterexample.
The [reference authorization](authorization-2026-09-10-reviewer-claude-finding-references.md)
permits these three exact file imports. Their tag objects, resolved commits,
Git blob identities, paths, retrieval times and byte hashes are retained in
`references/manifest.json`. No systemd service or target host was executed.

## Native administration

The [authorization](authorization-2026-09-10-reviewer-claude-output.md) names
one exposed development review with the same prompt and report schema as the
prior Codex finding-unit administration. Exact original base
`1bfe5a656bcb2c663891afd5f980211a3ef144a8` and change
`544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f` supply 188 source-file instances.
Dependencies and original readiness receipts were copied with provenance and
verified unchanged. Prior reviews and known witnesses were outside the mounts.
No review witness or suspect-location list was supplied in the prompt.

The native process completed with exit 0 after 790.171 seconds. Nine capture
files were retained without quarantine or omission. Native stdout and the
persisted session agree on the generated session ID and `claude-fable-5`
review-response model. There are 25 paired native tool requests/results. The
successful terminal record supplies the report through `/structured_output`;
its exact source line and stream hash bind the derived JSON report.
Max effort is configured explicitly; an observed effort value is unavailable.
This is native-reported identity agreement, not provider attestation or full
Binding verification.

The native usage report also includes `claude-haiku-4-5-20251001`. The debug
record identifies that request as `generate_session_title`. It is native
auxiliary title generation, with no reported reviewer-model substitution.
Keep this behavior in the harness configuration and cost accounting. Native
reported total cost is $6.445459, including $0.001475 for the title model;
these are reported usage costs, not a provider invoice.

Safe mode, empty setting sources, strict empty MCP configuration and the
Bash/Read/Grep/Glob tool set remain explicit administration choices. The native
system prompt was retained. The report's phrase "No network access" is not an
observation of containment: the namespace shared network for provider access,
while the task prohibited external research and exposed no web tool. No kernel
endpoint allowlist or complete process/network trace is claimed. Native
self-reported limitations remain preserved with this correction.

## Verification and consequence

The credential [preflight and adapter checks](verification-2026-09-10-reviewer-claude-preflight.md)
preceded the real attempt. Only the access token was delivered; real home,
configuration and refresh credentials were not mounted. The four new synthetic
credential tests pass. Full `make check`: 1,564 tests in 204.677 seconds, seven
skips. The independently inspectable behavioral evidence above, not those
repository tests, supports the finding assessment.

The verifier was frozen while the native review remained live, before final
report inspection. Reverification reproduces exactly. Private custody is
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/claude-output-1`.
The receipt pins 28 supporting/process/reference/assessment files plus all
nine native capture entries; source and dependency inventories are pinned in
the plan.

- Plan SHA-256: `27065c942e333605c27ca821c7567c8aa38d1f5135d280a2f2e0dfcaf4ad0725`.
- Verification SHA-256: `1a030c04afb09e5475a8dc605f10eb2caa6a039b2a8ab80f608b348c8a66350d`.
- Final report SHA-256: `40fc1ea84cc5e78a7c4bc056179be3ef83f63f93e836d65fcf63bcdf133dfd45`.
- Assessment SHA-256: `e994cb6c4cb1c0ab82c8fa9993edf34d16f6399fbb5533e00bc2da097021b7f1`.

This closes the first Claude native development administration and adds a
natural uncertain/advisory report with a refuted factual premise for later
scorer challenges. It does not establish comparable performance against Codex.
Case coverage remains 11 bounded changes, three base-only trees and 18 pending
in the unchanged 32-change sample. No case is admitted, no scoring rule is
accepted and no ranking or qualification follows. The goal remains active.
