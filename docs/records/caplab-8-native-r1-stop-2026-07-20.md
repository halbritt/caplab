---
id: caplab-8-native-r1-stop-2026-07-20
artifact_type: execution-record
title: CAPLAB-8 native r1 containment-authentication stop
status: stopped
created: 2026-07-20
decision_record: adr-0042
---

# CAPLAB-8 native r1 containment-authentication stop

## Observation

Campaign `caplab-preference-001-native-r1-2026-07-20` executed two primary
attempts under manifest SHA-256
`a1891ec8cb324bf89765f5e3f851efabca27978fc67dd8250f1c2cbdaf6ba942`:

| Attempt | Slot | Tuple | Status | Duration | Observation SHA-256 |
|---|---:|---|---|---:|---|
| `a01-s01-primary` | 0 | `claude-fable-5-max` | `completed` | 67.361265 s | `363c3d044658611d04903ec584f20d01d886a167d6cb967808963a6c8f076688` |
| `a02-s02-primary` | 1 | `codex-terra-max` | `provider_failure` | 16.095716 s | `9183084399431e2bb74e41897aa982fb3948923804a4a97329a0f91afa6e1242` |

The Codex attempt received HTTP 401 responses because the Striatum Codex
configuration's `auth.json` is a symlink to a credential file outside the
task namespace. The r1 containment correctly hid that external target but its
version-only preflight did not test authenticated native state. No proxy was
used and no subject output from r1 is admitted into the r2 campaign.

## Disposition

Stop r1 before its authorized replacement. Preserve its raw custody unchanged
at
`/home/halbritt/.local/share/caplab/campaigns/caplab-preference-001-native-r1-2026-07-20`.
The completed Fable attempt remains a valid observation of stopped execution,
but it is outside the r2 study denominator because r2 uses a corrected
containment source and a new manifest. ADR 0042 authorizes r2 from slot zero.

This stop does not cancel CAPLAB-8 or future work. It authorizes no inference,
adjudication, export, training use, independent verdict, or acceptance.
