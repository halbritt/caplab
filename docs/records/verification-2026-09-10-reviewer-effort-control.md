# Effort parsing across a real configuration change

The fixed feasibility sample includes Council change
`c1526c8552ccfa6236c01988aa141d0705eb5d7f`, whose base is
`c60cb4694a97b0f3151fdc48abfbea2e631ac1fb`. Only `src/v3/config.ts` changes:
the final effort-parser fallback becomes an explicit exhaustive-driver error.
This was a selected real change, not a manufactured clean patch.

The corrected local investigation found identical public member-pinning
parser outcomes on both revisions: **44 accepted inputs and 91 rejected inputs
per revision**, with all rejections at the effort field. Accepted inputs retain
the supplied effort value or its absence. TypeScript 5.9.3 reported no compiler
diagnostics on either configuration module and identified the new fallback's
argument type as `never`.

These observations support preservation of the tested effort-handling
properties. They are a valid-change control candidate, not an admitted clean
case, a whole-patch clean label or a reviewer score.

## Method and independent limits

The probe imports each exact source revision and calls the exported
`parseMemberPinningInput`; it does not extract or rewrite the implementation.
The cases cover all six supported drivers, all three agy model tiers, both
opencode provider branches, omitted/null effort, named effort levels and
malformed values. Fifteen inputs across nine driver/model variants give 135
observations per revision. These are repeated probes of one change, not 270
independent review cases.

Case inputs and expected acceptance categories were frozen before execution.
The categories describe the existing parser branches; they are not independent
proof that those product choices are ideal. Differential comparison asks
whether the change preserves behavior. The separately implemented TypeScript
checker examines the unreachable fallback using the actual module and imports.
Both public callers validate the driver against six names before calling the
effort parser; that source observation explains the exhaustiveness result.
The configuration-file caller itself was not executed by this probe.

Source inventories confirm that all other tracked files are byte-identical
between these revisions. Both snapshots and all installed dependency entries
were rechecked after execution. Each process ran in a fresh network-disabled
Bubblewrap namespace with read-only source/dependencies, an empty home and
private temporary storage. No provider, reviewer or real credential was used.
The compiler analysis and observed parser calls have different failure modes,
but neither supplies a universal proof of repository correctness.

## Preserved failed preparation

The first frozen batch used `launch_argv: ["fixture"]`. The public parser
requires an absolute first argument, so only two inputs were accepted; valid
native/session effort cases were masked by the fixture's path error. Both
revisions agreed, but agreement alone failed the frozen positive-control
criteria. That batch remains in `effort-control-1` custody.

The separately authorized second batch changes that fixture field to
`/usr/bin/true`. It satisfies every expected category. Its 91 rejections per
revision are specifically effort-validation failures, so a different malformed
field cannot stand in for the property under investigation. Both processes
exited normally within their 45-second limits. No failed slot was replayed.

## Custody and next use

The two owner-private custody roots are beneath
`~/.local/share/caplab/reviewer-ranking-001/development/`, named
`effort-control-1` and `effort-control-2`. Each preserves exact source snapshots,
runner, probe, cases, dependency inventory, plan and per-process launch,
stdout/stderr and completion records. The corrected batch additionally retains
the offline verification result. The
[receipt](../product/studies/reviewer-ranking-001/effort-control-development-receipt.json)
anchors the important files, source identities and failed/corrected outcomes.

Before this supports reviewer comparison, the task still needs blinded
findings, accurate attribution/refutation and coverage of any new alleged
change-attributable defect. A new substantiated finding would reopen the
control's status. This case is development-exposed and cannot be held out.
