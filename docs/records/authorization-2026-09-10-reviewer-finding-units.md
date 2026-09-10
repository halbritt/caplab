# Preserve findings and acceptance effects as separate reported units

Under ADR 0026 and the active reviewer-ranking goal, authorize a versioned
native report contract and a bounded administration experiment. The preceding
natural review had three findings but no explicit blocking/advisory stance.
The old aggregate interpreter can attach another finding's location to a
target claim and incorrectly grant introduced-defect credit.

Correct that old helper conservatively: when aggregate locations cannot be
assigned to one claim, causal attribution remains unresolved. Preserve its
prior frozen calibration documents, outputs, assessor and verification; do
not rewrite or re-score historical custody. Add a regression showing the
observed cross-finding failure before changing the helper.

Implement `caplab.native-code-review-report/v1`. Each reviewer-authored
finding contains its own claim, trigger, expected behavior, observed or
predicted behavior, change attribution, evidence, locations, reported stance
and acceptance effect. `block` means the reviewer recommends withholding
acceptance pending resolution; `advise` means it does not; `undetermined`
records that the reviewer has not decided. Reported certainty or a severity
word does not substitute for that explicit effect. Preserve limitations.

Parsing and source-location checks establish representation only. They must
not label findings true, refuted, inherited or clean. Preserve wrong and
missing locations without borrowing a location from another finding. Retain
all findings, including exact duplicates; do not create defect credit by
counting rows. Unknown or conflicting stances remain available for later
assessment. Reject malformed/ambiguous JSON without treating it as clearance.

Authorize one native development review in private
`reviewer-ranking-001/development/finding-units-review-1` custody. Reuse the
hash-checked full newsroom task, dependencies and original suite-readiness
observations from `newsroom-natural-output-2`: exact base
`1bfe5a656bcb2c663891afd5f980211a3ef144a8` and change
`544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f`. Copy their original provenance and
test outputs without rerunning or relabeling them. The prior review and all
known witnesses remain outside the subject mount.

Change only the task's final-report instructions and add the native CLI's
`--output-schema` input. The installed CLI help confirms that option. The
schema constrains representation, not the permitted defect vocabulary or
answer. Keep ordinary free-text explanations in every finding and require
no minimum number. Preserve full first-pass review scope, native Codex CLI
0.153.4 / `codex-terra-max`, the same tools and filesystem containment,
credential-private-text/v4, readable-rollout projection, fifteen-minute
outer limit and twelve-minute investigation stop. Freeze the new prompt,
schema, runner and support hashes before execution. One ten-second native
version preflight and one outer reviewer invocation are authorized.

Apply all source, credential, exposure and cleanup boundaries of the
[preceding native authorization](authorization-2026-09-10-reviewer-newsroom-natural-output-2.md).
Network access is for the native provider; no real target services or other
repositories may be used. There is no hard dollar cap. Stop on drift, unsafe
input/capture, native identity mismatch, schema administration failure or
deadline. Preserve failures and safe capture; no automatic retry.

This is a new development administration on an already exposed case. It is
not an independent case, a paired performance comparison, a held-out result
or scorer acceptance. A valid structured report is not a successful review.
The experiment must inspect actual claims and keep their truth assessment
separate. Expiry is consumption or 2026-09-11T00:00:00Z. No corpus admission,
qualification, ranking, original-code repair or operational placement is
authorized by this record.
