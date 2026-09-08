# Review task snapshot exemptions

The canned and native review-dissent captures compare task file contents to
detect unauthorized changes. Output and generated metadata exceptions apply
to **exact task-relative paths**, not every matching basename:

| Capture path | Excluded root paths |
|---|---|
| Canned (`grade_canned_review`) | `REVIEW.json`, `.caplab-review-task.json` |
| Native (`build_native_review_capture`) | `REVIEW.json`, `.caplab-review-task.json`, `.caplab-native-review-task.json` |

For example, the subject's root `REVIEW.json` does not change the task snapshot.
Adding `src/REVIEW.json` does. Nested files with any of these names remain
ordinary task inputs: unchanged content is preserved, while additions, edits
and deletions affect the snapshot. Binary content is hashed as bytes. Symlinks
are rejected even at otherwise excluded paths; an exception never permits
following a link to another file.

Canned capture compares the rendered before and after snapshots. Native
capture compares the expected task bytes with the observed final snapshot.
For mechanically eligible completed reviews, the existing rule assigns score
zero when task preservation fails. This repair changes only which paths are exempt;
status handling, scoring rules, capture schemas and ordinary byte hashes stay
unchanged. See the [repair record](../../records/repair-2026-09-08-review-output-exemptions.md)
for the reproduction and verification.

These content snapshots are not CAPLAB-79's complete write-set inventory.
They do not observe every intermediate write, file modes, empty directories,
special-file state, or an atomic view of a changing tree. Root metadata remains
excluded from these content comparisons; that exclusion does not authenticate
its contents. Capture integration must separately verify required task seals.
The [prospective capture design](../../records/decision-2026-09-08-caplab-79-capture-design.md)
still requires before/after inventories and retained native evidence.

No historical captures are rescored by this repair, and no instrument or
campaign manifest is resealed. New execution remains subject to its source
identity, authorization and eligibility checks. Synthetic preservation results
do not qualify a reviewer or authorize a ranking or deployment decision.
