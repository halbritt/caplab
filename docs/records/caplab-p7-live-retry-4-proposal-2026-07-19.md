---
id: caplab-p7-live-retry-4-proposal-2026-07-19
artifact_type: decision-proposal
assertion_type: recommendation
campaign: caplab-study-001-p7-recompute-2026-07-18
decision_owner: repository-owner
status: awaiting-decision
---

# CAPLAB P7 exact fourth retry proposal

## Decision requested

This proposal binds the repository owner's instruction to `retry again` to the
smallest corrected continuation. It is a recommendation until selected by a
durable decision record; it is not execution, verification, capability
inference, or acceptance.

Approve only this ordered continuation:

1. require the current third-retry evidence manifest, absent campaign state,
   disabled access controls, and all three earlier stopped archives to verify;
2. atomically move `/var/tmp/caplab-p7-execution-2026-07-18` to
   `/var/tmp/caplab-p7-stopped-third-retry-2026-07-19` and seal an archive
   manifest without changing any earlier archive or the preserved symlinked
   runtime;
3. require all four stopped archives to verify, the active evidence and state
   paths to be absent, and every pre-effect control to match;
4. require the prepared fixed runtime for CAPLAB commit
   `bf6de2b24ac61e82107208cdc609c7e534c6eaaa` to have the bound source,
   dependencies, and regular-file interpreter identities;
5. require clean, pushed Proximal commit
   `1b79aa07cc4e44e8fc828449f882c6b62008edb6`, the five installed canonical
   host-file hashes, active expiry timer, and ten-test controller gate;
6. recreate `/var/tmp/caplab-p7-execution-2026-07-18` as `root:root 0700` and
   capture a fresh pre-effect snapshot;
7. install aggregate disablement as the cleanup trap, enable only
   `caplab_reader`, and require the versioned controller's
   `verify --phase ready` result;
8. run the repaired model-free recomputation command exactly twice, require
   exit zero and byte-identical canonical stdout, and retain stderr separately;
9. require the product observation to bind the frozen P6 admission, CAPLAB
   implementation commit, exact 20 outcome identities, byte-identical
   historical comparison, and self-consistent manifest SHA-256; and
10. aggregate-revoke access, verify the disabled phase, require every pre/post
    preservation check, and seal the fresh evidence manifest.

Authorization expires at `2026-07-25T23:59:59Z`. The existing timer begins
aggregate revocation at `2026-07-25T23:50:00Z` and remains the backstop.

## Cause and repair evidence

The stopped third retry is recorded in
[`caplab-p7-live-third-retry-attempt-2026-07-19`](caplab-p7-live-third-retry-attempt-2026-07-19.md).
The prepared
[`runtime custody repair`](caplab-p7-runtime-custody-repair-2026-07-19.md)
changes only venv construction and retains the controller's fail-closed
symlink policy.

The rebuilt interpreter is a regular file with the expected system-Python
identity. Ten controller tests cover the symlink refusal and access lifecycle;
the complete 105-test CAPLAB gate passes. Doctrine packet
`pkt-02f55cfae37b87d6`, content SHA-256
`8786f14e4c714b29c131591613c590945e45843aa11ae5813532eb975b55f48f`,
supports the causal minimal repair and preserves the owner gate.

## Exact identities

| Surface | Identity |
|---|---|
| CAPLAB source | `bf6de2b24ac61e82107208cdc609c7e534c6eaaa` |
| repaired recomputation service | `2e06e26ed0a61caf38a84ff8bfaba76794e1e4c9ae01f410adcbc040a8040854` |
| Proximal desired state | `1b79aa07cc4e44e8fc828449f882c6b62008edb6` |
| P6 admission | `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e` |
| first stopped-attempt archive manifest | `5ad7259eaf6f85d85b2595e559835aebe9cdb134a8d4d4989b6dcd9473da8d5e` |
| stopped-retry archive manifest | `cc0807b93ed9217ad9718b6ace19c2ee485d6a3e5ed40fdb3b041a40804bafca` |
| stopped-second-retry archive manifest | `cc9fc15a80ab9ff59f8192cbf90d859a3ee510ab24d03b2ced7c0dae2f6f9153` |
| stopped-third-retry `SHA256SUMS` | `56b49199a9df5ddc5cfa8f307e7b2bfe81747a52de6a6af4c633adcd191d7eb6` |
| copied runtime Python | `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118` |
| installed source-inventory manifest | `fd32d932f2dd90ef486ec199b8fd9930eb69a11aeea86ed107a77d9cd299f322` |
| wheel | `e67dea2c0aaed8034ca19f549e8ad7c188c1498e898926f2b9a1d49e3c339d53` |
| requirements lock | `b5c05b76c4e383b9bdedb783ed658fe33c368d660a1efe45f80c98e0f8adb3a0` |
| `SOURCE_COMMIT` | `c8b6e84e664ad080915af35416f91fb20b2a59f4cf9eee8d7a6193443215d0a6` |
| `recomputation.toml` | `0e11bb08976526f1217cf9ceef3a39bd6e960b5d8ee8fd84b63f80c0e36ecbca` |
| source-pinned controller | `312d110853d5c540e03c4ea94a72c5c9db402518820cf2c1efa095db22e5df46` |
| expiry service | `a853a0c79e5c89174d4ff65bef77fd553e1a38ebc4f0fec0bb50500d43e183e5` |
| expiry timer | `8e18f83e68d6a558818ec01bf023fc96b557a20af9ef3c3a216ecfd3fcd17941` |

## Preservation and stop conditions

Before the fourth retry, require absent campaign state and no P7 key,
credential, login, session, or reader process. Preserve the PostgreSQL cluster
start identity, complete `caplab_v0` data, P4 control, P6 registration and
timestamps, Garage object count and registered-byte verification, all 326
independent-copy hashes, source custody, earlier runtimes and stopped evidence,
and disabled writer/verifier access.

Stop and aggregate-revoke on repository, commit, runtime custody, install,
timer, clock, role, privilege, credential, session, registration, locator,
byte, cardinality, analysis, canonical-output, replay, or preservation drift.
Do not repair or reinterpret a live discrepancy. Another stop does not
authorize repair or a later retry.

## Authority excluded

Approval does not authorize capability inference, training-candidate or
training-eligibility decisions, export, model/provider calls, training,
publication, Striatum placement, preference work, CAPLAB-33 independent
verification, CAPLAB-34 acceptance, deletion of stopped evidence or earlier
runtimes, or a later retry.
