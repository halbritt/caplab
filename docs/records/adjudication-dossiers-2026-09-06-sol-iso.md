# Control-soundness audit — Sol's isolation refusals

- Date: 2026-09-06. Trigger: `codex-sol-high` refused 65 of 69 controls on
  the `iso-v1` sweep. Standard as on 2026-08-23 and 2026-09-04: each refusal
  is evaluated against the artifact's own content; allegations that depend
  on out-of-set material are recorded, never scored; a rerunnable oracle per
  control (`advisory/checks/verify-control-<substrate>.py`, exit 0 =
  defective) is the verdict.
- Of the 65: 48 were already adjudicated (19 defective, 29 sound) by the
  earlier audits and were recognized by scoring after the key fix of
  2026-09-04. Seventeen were fresh. All seventeen are settled below;
  records 57–71 in the ledger.

## Settled by oracle — 17 controls

**Defective (1):** `qs-415d0b9333fe336f` — the architecture-lint entrypoint
test packet. `doc.go` claims the package "exercises the real, registered
entrypoint as a subprocess ... so drift here is drift in what actually
runs", and the helper comment claims to run "the check's exact registered
argv"; `goToolchain` substitutes a PATH `go` whenever the registered argv[0]
is absent, so an unresolvable registered check cannot fail the suite. The
hollow-verification pattern. Sol was right.

**Sound (16):** every one refused on the same ground — a referenced
document, ADR, contract, receipt or hash is "not included in or reachable
from the artifact". Out-of-contract by the standard; the in-set claims each
allegation touched were checked and hold:

- reference-only refusals: `41241900` (RFC and concept links),
  `e7003896` (q3 execution contract, ADRs), `af300e90` (escalations 2646/2686,
  the 2026-07-09 wedge), `810276f0` (relative links), `8582be8e` (q5
  contract, ADR 0059), `961371a1` (abbreviated hashes in a verification
  table), `40be7cf1` (a 3 KB explanation's completeness), `4298b567`
  (evidence behind a 0/18 result; seed and population are stated),
  `7dabe689` (references plus one reading of "before the first host
  effect"), `81f5ccd5` (whether ownership-bounded categories are an "exact"
  scope), `514df336` (a design that says it defers retry limits, does).
- the three that alleged an in-set inconsistency, each answered by the text:
  `5f841949` (a proposal's frontmatter records the later disposition and the
  record that made it; the body is the proposal as written), `5de685af`
  (an ADR's Status interpretation records a selection made after the owner
  response the Observations describe, and says so), `d05784fe` (a design
  names "the registered go-test check id" by role and states it invents no
  mechanics — distinguished from the qs-ccfd2a5f ruling, where a plan named
  literal ids it never explained; **flagged** in case the Principal extends
  that ruling to role-named checks).

## The cohort effect

Excluding the 19 defective controls, Sol refused 34 of 38 sound controls:
false alarm 0.895, catch 0.912, catch − FA 0.018, audit status
`established`. Every other binding's number is unchanged by this audit
(the sixteen new sound records concern controls only Sol refused).

## Owed

- The Principal's view on `qs-d05784fe3c3b3ac2` if role-named checks are to
  be held to the ccfd standard; the record flips to defective and Sol's FA
  falls by one pair.
