---
id: caplab-p7-live-retry-2-proposal-2026-07-19
artifact_type: decision-proposal
assertion_type: recommendation
campaign: caplab-study-001-p7-recompute-2026-07-18
decision_owner: repository-owner
status: awaiting-decision
---

# CAPLAB P7 exact second retry proposal

## Decision requested

The repository owner must approve or decline this exact second retry. This
proposal is a recommendation, not a decision, authorization, execution record,
verification result, capability inference, or acceptance record.

Approve only this ordered continuation:

1. require the current stopped-retry manifest and disabled state to verify;
2. atomically move `/var/tmp/caplab-p7-execution-2026-07-18` to
   `/var/tmp/caplab-p7-stopped-retry-2026-07-19`, move the disabled state into
   that archive as `access-state-disabled-live.json`, and seal an archive
   manifest without changing the first stopped-attempt archive;
3. require both stopped archives to verify, the active evidence and state paths
   to be absent, and every pre-effect control to match;
4. install only the controller from clean, pushed Proximal commit
   `031d20cceefa1f7f4bf5db9386d89383d763edf0`, leaving the frozen CAPLAB
   source, configuration, units, timer, P6 identity, and expiry unchanged;
5. recreate `/var/tmp/caplab-p7-execution-2026-07-18` as `root:root 0700` and
   capture a fresh pre-effect snapshot;
6. install aggregate disablement as the cleanup trap, enable only
   `caplab_reader`, and require the versioned controller's
   `verify --phase ready` result without adding a separate password-storage
   assertion;
7. run the frozen model-free recomputation command exactly twice, require exit
   zero and byte-identical canonical stdout, and retain stderr separately;
8. require the product-generated observation to bind the frozen P6 admission,
   frozen implementation commit, exact 20 outcome identities, byte-identical
   historical comparison, and self-consistent manifest SHA-256; and
9. aggregate-revoke access, verify the disabled phase, require every pre/post
   preservation check, and seal the fresh evidence manifest.

Authorization would expire at `2026-07-25T23:59:59Z`. The existing timer begins
aggregate revocation at `2026-07-25T23:50:00Z` and remains the backstop.

## Cause and repair evidence

The stopped retry is recorded in
[`caplab-p7-live-retry-attempt-2026-07-19`](caplab-p7-live-retry-attempt-2026-07-19.md).
The retry passed the selected controller's ready verification. It stopped only
because an added shell assertion treated one PostgreSQL storage representation
as the security contract.

The repaired controller owns the complete PostgreSQL readiness boundary. Its
query returns booleans and counts rather than stored password values. It accepts
only an absent password or PostgreSQL's unusable `*` marker for exactly the
reader, writer, and verifier roles. It rejects missing roles, usable passwords,
writer or verifier login, reader or writer/verifier sessions, effective reader
write authority in `caplab_v0`, inherited writer or verifier membership,
database or schema creation authority, and non-loopback listening.

The regression test failed before the repair and passes after it. All nine P7
lifecycle tests, Ruff, controller help, systemd calendar and unit verification,
diff hygiene, and the live read-only query pass. The live query returned the
disabled-state boundary `f|f|f|t|0|0|0|t`; it emitted no stored password value.
Doctrine packet `pkt-e8b0978f6a99d580`, content SHA-256
`e8b0978f6a99d580010e4cb0a9d9e759c78b928988bda883f9fb1f76eec53eeb`,
supports the causal repair and retains the owner gate.

## Exact identities

| Surface | Identity |
|---|---|
| CAPLAB source | `04ed8213ec7741d76d8bb9f9b6f972ebb4deaf3e` |
| Proximal desired state | `031d20cceefa1f7f4bf5db9386d89383d763edf0` |
| P6 admission | `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e` |
| first stopped-attempt archive manifest | `5ad7259eaf6f85d85b2595e559835aebe9cdb134a8d4d4989b6dcd9473da8d5e` |
| stopped-retry `SHA256SUMS` | `c46bb43a6165da15e49524ddc4dd0f931eaa91af19bde7782ea3d0a3cbe515b7` |
| regular runtime Python | `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118` |
| requirements lock | `b5c05b76c4e383b9bdedb783ed658fe33c368d660a1efe45f80c98e0f8adb3a0` |
| `SOURCE_COMMIT` | `250a15ec2b8faccde513bb3c944a178b1faef0b0698f04933f79c93714ca1540` |
| `recomputation.toml` | `c1cd92cabcd341e20682b055e1df7b8e965f87f522dd4ba7871dbb42e7001e56` |
| repaired controller | `8f5b2378a772f1c5c1fd28031e0c9ac9a96b84f90c0270d2c48d85ce3be7d076` |
| expiry service | `a853a0c79e5c89174d4ff65bef77fd553e1a38ebc4f0fec0bb50500d43e183e5` |
| expiry timer | `8e18f83e68d6a558818ec01bf023fc96b557a20af9ef3c3a216ecfd3fcd17941` |

## Preservation and stop conditions

Before the second retry, require the live state to remain disabled with no P7
key, credential, login, session, or reader process. Preserve the PostgreSQL
cluster start identity, complete `caplab_v0` data, P4 control, P6 registration
and timestamps, Garage object count and registered byte verification, all 326
independent-copy hashes, source custody, and disabled writer/verifier access.

Stop and aggregate-revoke on repository, commit, install, timer, clock, role,
privilege, credential, session, registration, locator, byte, cardinality,
analysis, canonical-output, replay, or preservation drift. Do not add an
unversioned readiness assertion. Another stop does not authorize repair or a
further retry.

## Authority excluded

Approval would not authorize capability inference, training-candidate or
training-eligibility decisions, export, model/provider calls, training,
publication, Striatum placement, preference work, CAPLAB-33 independent
verification, CAPLAB-34 acceptance, deletion of stopped evidence, or a later
retry. Those remain separate checkpoints and owner gates.

