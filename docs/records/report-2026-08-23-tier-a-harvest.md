# Tier A: six new constructs from the production ledger

- Date: 2026-08-23. Phase 1 of the capability-measurement program
  (Principal-directed: "Begin Tier A").
- 72 claims ledgered and ingested, custody `striatum-production`, every
  label mechanical or a closure outcome — no model judgment in the loop.
  Reproducible via `caplab.advisory.build_corpus.tier_a_claims` (tested);
  ledger dump sha-pinned, >200k guard enforced.

## Constructs and headlines

| construct | subjects (n≥10) | best | worst |
|---|---|---|---|
| planning.delivery/1 | 7 | claude-code 100% (n=53) | agy 69% (n=16) |
| design.delivery/1 | 7 | claude-opus-5-high 100% (n=13) | claude-harm-fable-5-max 57% (n=23) |
| proposal.delivery/1 | 7 | claude-sonnet-5-high 100% (n=13) | **claude-fable-5-max 3% (n=31)** |
| review_pass.delivery/1 | 20 | agy-flash-medium 100% (n=25) | **claude-harm-fable-5-high 9% (n=1,115)** |
| packetization.legality/1 | 1 (local) | 63% (n=115) | — |
| integration.checks/1 | 1 (local) | 71% (n=72) | — |

Verification, intent-capture, packetization, and integration run on the
deterministic `local` backend in production — a single subject is the
honest answer for those, not a gap.

Two operational findings surfaced by delivery rates alone:
`claude-harm-fable-5-high` closed only 9% of 1,115 review pass runs
`submitted` (the submitted_partial/timeout pathology at scale — an
operations problem wearing a capability construct's clothes, and the claim
notes say so), and `claude-fable-5-max` delivered 3% of its 31 proposal
runs — consistent with the Principal's standing no-max guidance.

## Withdrawn before commit: receipt compliance

`harness.receipt_compliance/1` collapsed to one subject at the global rate
(70,046 results all attributed to `local`) — the attribution through
receipt gates is unproven, so the claim was removed rather than shipped.
The function stays, marked unvalidated; correct attribution of receipt
checks to the receipted run's backend is a follow-up.

## Tier B framing (recorded for the plan)

Per the Principal (2026-08-23): review/acceptance verdicts are produced by
review passes on lanes emitting Review Ledgers with closed verdicts
(accept / accept_with_findings / needs_revision / reject), and
**independence is enforced at placement — the reviewer's aliasing class
must exclude the producer's** (a Gemini-built design is never judged by
Gemini). Tier B constructs will therefore be framed as *acceptance by
independent-family review* — a legitimate, model-relative label, treated
with the vindication method, never as gold.
