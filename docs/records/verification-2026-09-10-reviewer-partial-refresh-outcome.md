# Original execution confirms the partial-refresh reviewer finding

The structured native review's sole blocker is confirmed for the tested
scenario: a partial RSS refresh failure returns success from the original
harvester despite recording the provider as unavailable. Independent
execution replaces the reviewer's patched-function demonstration as the
behavioral evidence. The prior unresolved assessment remains unchanged;
this record adds the new evidence and assessment.

## Outcomes and controls

All six conditions ran twice through the original CLI, configuration loader,
HTML/JSON transports, RSS provider, candidate persistence and exit handling.
Each execution began with an empty data directory in a separate network
namespace. Original HTTPS requests reached a controlled TLS endpoint; no
source functions, constants, clocks or retry delays were replaced.

| Endpoint condition | Exit | Provider status | Retained candidates | Interpretation |
| --- | ---: | --- | ---: | --- |
| Both HTML listings healthy | 0 | live | 2 | Successful collection control. |
| Both HTML listings valid and empty | 0 | live | 0 | Healthy quiet-day control. |
| One HTML listing healthy, other HTML/JSON blocked, RSS succeeds | 0 | live | 2 | Original RSS parsing restores the blocked source and saves a feed snapshot. |
| One HTML listing healthy, other HTML/JSON blocked, RSS fails | 0 | unavailable | 1 | Failed refresh is reported as success while available candidates remain. |
| One HTML listing valid and empty, other HTML/JSON blocked, RSS fails | 0 | unavailable | 0 | Empty partial failure is also reported as success. |
| Both HTML/JSON listings blocked, RSS fails | 1 | unavailable | 0 | Total failure is correctly exposed to the caller. |

Both repetitions agree on every listed outcome. Partial failures also write
a new harvest timestamp; total failure does not. Failed RSS scenarios have
no usable cached feed. The successful RSS control retains the expected feed
body hash and candidate, so an invalid fixture or broken parser cannot explain
the contrasting failure results. Every endpoint request, status, body length
and response hash matches the frozen scenario. SQLite read-back matches the
captured observations. Logs explicitly describe the failed RSS recovery.

## Requirement and attribution

The reviewed change's original README, lines 193–201, promises a nonzero exit
after failed refresh so systemd retries. Its new harvester service specifies
`Restart=on-failure`. The tested request is an actual failed RSS refresh with
no cache, within that documented provider-state scope.

The newly added provider writes `last_status=unavailable` and raises
`SourceUnavailable` without setting its `degraded` flag. The new fallback
handler catches that exception. With only some listings blocked, execution
continues to save candidates and return from `harvest`. The new CLI returns
1 only for an escaping exception or a degraded provider, and therefore
returns 0 in this path. The finding's reported source locations cover the
catch, exit handling and requirement; the independent investigation also
identifies the provider-state transition.

The base already tolerated partial HTML/JSON failures. It had no RSS provider
module, `_fetch_rss`, `harvest` method, `cmd_harvest` or harvester service.
The defect is attributable to the new refresh/status/retry behavior and
contract. This does not recast all inherited partial-listing tolerance as a
new defect. Base absence and changed definitions are preserved with source
hashes in the assessment.

Exit 0 does not activate the supplied `Restart=on-failure` policy. This is a
policy inference from the observed status and original service file. No
systemd instance was started, and no live restart, future timer firing,
provider prevalence or actual production data loss is claimed.

The reported `block` effect is explicit and concerns a confirmed
change-attributable defect in these conditions. It is not an independently
refuted blocker. Severity weighting and comparison policy remain unfrozen;
no ranking score or rate is computed. The assessment is an evidence-backed
primary-agent development inference, not acceptance of a semantic scorer or
an independent verdict on the investigator.

## Custody and checks

The [authorization](authorization-2026-09-10-reviewer-partial-refresh-witness.md)
permitted exact read-only source reuse, two inherited synthetic HTML fixtures,
new endpoint inputs and twelve bounded executions. Private custody is
`~/.local/share/caplab/reviewer-ranking-001/development/partial-refresh-witness-1`.
The [receipt](../product/studies/reviewer-ranking-001/partial-refresh-development-receipt.json)
contains the full finding, prior-assessment link, source comparison,
verification and file/capture hashes.

| Identity | SHA-256 |
| --- | --- |
| Frozen plan | `2e0637d3e047442ecb5e54a894266d89f11c0b80097b2aff6bb8d3df9ae42518` |
| Execution verification | `c47aa1c4cd661fd1388fc2e31f35a295dc02b64ec0b6061e274af5cd2434df28` |
| New finding assessment | `92996a7e9b55d38a204253bf4d49a5018910d453ae48de452edb88142ddbe63e` |
| Unchanged prior unresolved assessment | `7c432dbc8a7e2f85e2b938b7a5335b2cfeb6d90e98dd995542789803b2fb2381` |
| Native final report | `ad47259eb3ab98374b03ac07635dfa8f59ffa62d99716441fa4dd755dcd92e84` |

Twelve executions completed in 57.42 seconds, with 62 real local HTTPS
requests and 60 captured files. The receipt identifies 83 additional input,
process and assessment files. All 188 original base/change source files
retain their pinned identities; only the changed tree was executed here.
Original source is read-only, and fixture configuration is a separately
identified input overlay. Network access is confined to private loopback.

Four focused verifier tests pass. They reject wrong or missing endpoint
evidence, failed controls and cached substitutes for no-cache failure, while
allowing either a success or failure exit to be represented as the observed
outcome. The full repository check passed: 1,550 tests in 246.380 seconds,
seven skipped. The completed output is retained as `repository-check.log`
in the witness custody root, separately from the execution receipt.

## Consequence for the ranking work

This closes the specific new-finding investigation from the preceding native
review. It shows why findings outside an initial answer key must be preserved
and independently investigated. One reported defect now has an original-code
witness; the known deadline and optional-RSS defects remain absent from that
review's final report.

This is one additional failure family on an already investigated change.
Coverage remains seven bounded change investigations, three base-tree-only
investigations and twenty-two pending, with zero admitted cases. Next work
must expand the fixed sample and prospective scoring evidence. Repeating
this development review again would not establish broader reviewer ability.
The full reviewer-ranking goal remains active.
