# Fixed-sample behavioral coverage

Seven of the 32 selected changes have bounded, change-relevant behavioral witnesses. Two further selected trees ran as bases for other witnesses; their own changes remain unverified. The remaining 23 changes have no established behavioral witness. No case is admitted for reviewer scoring.

This projection keeps every selected change in the denominator. A witness may cover only part of a change. Repeated executions, ancestor investigations and passing tests do not increase the count of independently covered changes.

| Repository | Size stratum | Selected commit | Evidence status |
| --- | --- | --- | --- |
| ai-newsroom | 0-20 | `566e5af24c0a` | No change-specific behavioral witness established. |
| ai-newsroom | 0-20 | `c7535007644f` | No change-specific behavioral witness established. |
| ai-newsroom | 101-500 | `c04f6c8b3af6` | [Release response preservation](../../../records/verification-2026-09-10-reviewer-github-release-outcome.md) |
| ai-newsroom | 101-500 | `e4d529391061` | [Publication precision and window behavior](../../../records/verification-2026-09-10-reviewer-publication-outcome.md) |
| ai-newsroom | 21-100 | `00efadb0c5bd` | Executed as another case base; this change remains unverified. |
| ai-newsroom | 21-100 | `345e9d25caaf` | No change-specific behavioral witness established. |
| ai-newsroom | 501+ | `544f7e3c43ea` | [Reddit recovery deadline, filtering and pool reopen](../../../records/verification-2026-09-10-reviewer-reddit-recovery-outcome.md); other components unverified. |
| ai-newsroom | 501+ | `1bfe5a656bcb` | No change-specific behavioral witness established. |
| caplab | 0-20 | `b359e3039326` | No change-specific behavioral witness established. |
| caplab | 0-20 | `51a7698535f0` | No change-specific behavioral witness established. |
| caplab | 101-500 | `c8f097a0934b` | [Prompt delivery and response validity](../../../records/verification-2026-09-10-reviewer-pool-transport-outcome.md) |
| caplab | 101-500 | `b8c68924f1df` | No change-specific behavioral witness established. |
| caplab | 21-100 | `9fa844d3a02d` | No change-specific behavioral witness established. |
| caplab | 21-100 | `f2d2a3b21fff` | No change-specific behavioral witness established. |
| caplab | 501+ | `a8d5094908c9` | No change-specific behavioral witness established. |
| caplab | 501+ | `c4c8e2417e12` | No change-specific behavioral witness established. |
| council | 0-20 | `c1526c8552cc` | [Parser preservation and unreachable fallback](../../../records/verification-2026-09-10-reviewer-effort-control.md) |
| council | 0-20 | `8a0fd3efc816` | No change-specific behavioral witness established. |
| council | 101-500 | `348304bce370` | No change-specific behavioral witness established. |
| council | 101-500 | `19fb83494cf3` | [Provider timeout and cancellation](../../../records/verification-2026-09-10-reviewer-timeout-outcome.md) |
| council | 21-100 | `32c9f09674b2` | Executed as another case base; this change remains unverified. |
| council | 21-100 | `ea09c00acbc0` | No change-specific behavioral witness established. |
| council | 501+ | `9ca876645f8b` | No change-specific behavioral witness established. |
| council | 501+ | `06e453664391` | No change-specific behavioral witness established. |
| striatum-next | 0-20 | `98759de9d5f1` | No change-specific behavioral witness established. |
| striatum-next | 0-20 | `ff6444d62331` | No change-specific behavioral witness established. |
| striatum-next | 101-500 | `83083103119e` | No change-specific behavioral witness established. |
| striatum-next | 101-500 | `b9325d547fa8` | [Decision input provenance and graph admission](../../../records/verification-2026-09-10-reviewer-scheduler-graph-outcome.md) |
| striatum-next | 21-100 | `f6bcad95edc3` | No change-specific behavioral witness established. |
| striatum-next | 21-100 | `3470918aa26b` | No change-specific behavioral witness established. |
| striatum-next | 501+ | `9dbe944b6310` | No change-specific behavioral witness established. |
| striatum-next | 501+ | `8d3e71bddca2` | No change-specific behavioral witness established. |

The [JSON projection](feasibility-coverage.json) retains full commit/base/tree identities and receipt hashes. Its source is the unchanged content-checked feasibility selection. This table is planning state and grants no evidence admission or ranking acceptance.
