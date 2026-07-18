---
id: caplab-p7-live-retry-proposal-2026-07-18
artifact_type: decision-proposal
assertion_type: recommendation
campaign: caplab-study-001-p7-recompute-2026-07-18
decision_owner: repository-owner
status: awaiting-decision
---

# CAPLAB P7 exact live retry proposal

## Decision requested

The repository owner must approve or decline this exact retry. This proposal
is a recommendation, not a decision, authorization, execution record,
verification result, capability inference, or acceptance record.

Approve only this ordered continuation:

1. preserve the stopped attempt by atomically moving
   `/var/tmp/caplab-p7-execution-2026-07-18` to
   `/var/tmp/caplab-p7-failed-attempts-2026-07-18` and moving the disabled
   state file into that archive as `access-state-disabled-live.json`;
2. require the archive manifest to remain valid, the original evidence path
   and campaign state path to be absent, and every pre-effect control to match;
3. install only the corrected controller from clean, pushed Proximal commit
   `8c45e62a22cf5c7e566df2d4510b49742f39b6ac`, leaving the frozen CAPLAB
   source, configuration, units, timer, P6 identity, and expiry unchanged;
4. recreate `/var/tmp/caplab-p7-execution-2026-07-18` as `root:root 0700` and
   capture a fresh pre-effect snapshot;
5. enable only `caplab_reader` with one expiring Garage read-only key, require
   corrected ready verification, and run the exact model-free recomputation
   twice;
6. require canonical, self-consistent, byte-identical observations bound to
   the frozen P6 admission and 20 outcome identities; and
7. aggregate-revoke access, verify the disabled phase, require all pre/post
   preservation checks, and seal the retry evidence manifest.

Authorization would expire at `2026-07-25T23:59:59Z`. The existing timer
begins aggregate revocation at `2026-07-25T23:50:00Z` and remains the backstop.

## Cause and repair evidence

The stopped execution is recorded in
[`caplab-p7-live-attempt-2026-07-18`](caplab-p7-live-attempt-2026-07-18.md).
Garage 2.3.0 includes the exact bucket field set `globalAliases`, `id`,
`localAliases`, and `permissions`. The former controller rejected the real
response because its test double omitted `id` and `localAliases`.

The corrected controller accepts exactly one bucket object with exactly those
four fields, the target global alias, a nonempty bucket identity, no local
aliases, and owner false/read true/write false. It still rejects extra
buckets, extra or absent fields, wrong aliases, a local alias, write or owner
authority, global bucket-creation authority, an expired key, or an expiry past
the authorization deadline. This is a defect repair, not an authority
expansion.

The regression test failed before the repair and passes after it. All seven P7
lifecycle tests, Ruff, and diff hygiene pass. Doctrine packet
`pkt-eef95fdfa4256fa1`, content SHA-256
`eef95fdfa4256fa1f12553cedc3d88e595b3573c878613b777554330bde6f8d3`,
supports the causal minimal repair and preserves the owner decision boundary.

## Exact identities

| Surface | Identity |
|---|---|
| CAPLAB source | `04ed8213ec7741d76d8bb9f9b6f972ebb4deaf3e` |
| Proximal desired state | `8c45e62a22cf5c7e566df2d4510b49742f39b6ac` |
| P6 admission | `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e` |
| stopped-attempt `SHA256SUMS` | `6292d169cb5ccd9f37b69514be35b2a50395cd6b51be9f37721a788d0831aa61` |
| regular runtime Python | `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118` |
| requirements lock | `b5c05b76c4e383b9bdedb783ed658fe33c368d660a1efe45f80c98e0f8adb3a0` |
| `SOURCE_COMMIT` | `250a15ec2b8faccde513bb3c944a178b1faef0b0698f04933f79c93714ca1540` |
| `recomputation.toml` | `c1cd92cabcd341e20682b055e1df7b8e965f87f522dd4ba7871dbb42e7001e56` |
| corrected controller | `7497d3cf12fd6b6d91dbb0e14cd8fe852fd162f055d7974377871338e3c79607` |
| expiry service | `a853a0c79e5c89174d4ff65bef77fd553e1a38ebc4f0fec0bb50500d43e183e5` |
| expiry timer | `8e18f83e68d6a558818ec01bf023fc96b557a20af9ef3c3a216ecfd3fcd17941` |

## Preservation and stop conditions

Before the retry, require the live state to remain disabled with no P7 key,
credential, login, session, or reader process. Preserve the PostgreSQL cluster
start identity, complete `caplab_v0` data, P4 control, P6 registration and
timestamps, Garage object count and registered byte verification, all 326
independent-copy hashes, source custody, and disabled writer/verifier access.

Stop and aggregate-revoke on repository, commit, install, timer, clock, role,
privilege, credential, session, registration, locator, byte, cardinality,
analysis, canonical-output, replay, or preservation drift. Another stop does
not authorize repair or a further retry.

## Authority excluded

Approval would not authorize capability inference, training-candidate or
training-eligibility decisions, export, model/provider calls, training,
publication, Striatum placement, preference work, CAPLAB-33 independent
verification, CAPLAB-34 acceptance, deletion of stopped-attempt evidence, or a
later retry. Those remain separate checkpoints and owner gates.

