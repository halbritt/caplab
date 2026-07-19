---
id: caplab-p7-live-retry-3-proposal-2026-07-19
artifact_type: decision-proposal
assertion_type: recommendation
campaign: caplab-study-001-p7-recompute-2026-07-18
decision_owner: repository-owner
status: awaiting-decision
---

# CAPLAB P7 exact third retry proposal

## Decision requested

The repository owner must approve or decline this exact third retry. This
proposal is a recommendation, not a decision, authorization, execution record,
verification result, capability inference, or acceptance record.

Approve only this ordered continuation:

1. require the current second-retry evidence manifest and disabled state to
   verify, along with both earlier stopped-attempt archives;
2. atomically move `/var/tmp/caplab-p7-execution-2026-07-18` to
   `/var/tmp/caplab-p7-stopped-second-retry-2026-07-19`, move the disabled state
   into that archive as `access-state-disabled-live.json`, and seal an archive
   manifest without changing either earlier archive;
3. require all three stopped archives to verify, the active evidence and state
   paths to be absent, and every pre-effect control to match;
4. install clean, pushed CAPLAB commit
   `bf6de2b24ac61e82107208cdc609c7e534c6eaaa` in its distinct fixed runtime,
   retaining the earlier runtime unchanged;
5. install the five canonical host files from clean, pushed Proximal commit
   `c5bb1efa1402010a57ccc7034f3555b14830bc1c`, reload systemd, and require the
   installed source pin, configuration, controller, units, timer, and runtime
   hashes to match;
6. recreate `/var/tmp/caplab-p7-execution-2026-07-18` as `root:root 0700` and
   capture a fresh pre-effect snapshot;
7. install aggregate disablement as the cleanup trap, enable only
   `caplab_reader`, and require the versioned controller's
   `verify --phase ready` result;
8. run the newly pinned model-free recomputation command exactly twice, require
   exit zero and byte-identical canonical stdout, and retain stderr separately;
9. require the product-generated observation to bind the frozen P6 admission,
   CAPLAB implementation commit, exact 20 outcome identities, byte-identical
   historical comparison, and self-consistent manifest SHA-256; and
10. aggregate-revoke access, verify the disabled phase, require every pre/post
    preservation check, and seal the fresh evidence manifest.

Authorization would expire at `2026-07-25T23:59:59Z`. The existing timer begins
aggregate revocation at `2026-07-25T23:50:00Z` and remains the backstop.

## Cause and repair evidence

The stopped second retry is recorded in
[`caplab-p7-live-second-retry-attempt-2026-07-19`](caplab-p7-live-second-retry-attempt-2026-07-19.md).
The prepared
[`JSON-decimal identity repair`](caplab-p7-json-decimal-repair-2026-07-19.md)
aligns recomputation with admission's existing decimal-token policy at the
immutable-byte boundary. It does not weaken identity-safe canonicalization or
change historical evidence.

The public regression reproduced the live failure before the repair and passed
after it. The complete 105-test CAPLAB gate and nine-test Proximal controller
suite pass. Doctrine packet `pkt-7f0f29d6d5486b26`, content SHA-256
`dc8c419ca1d8de7db545dc0735991c57cbb174ff9d8563cc1dd9262d6095cff8`,
supports the causal minimal repair and preserves the owner gate.

## Exact identities

| Surface | Identity |
|---|---|
| CAPLAB source | `bf6de2b24ac61e82107208cdc609c7e534c6eaaa` |
| repaired recomputation service | `2e06e26ed0a61caf38a84ff8bfaba76794e1e4c9ae01f410adcbc040a8040854` |
| Proximal desired state | `c5bb1efa1402010a57ccc7034f3555b14830bc1c` |
| P6 admission | `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e` |
| first stopped-attempt archive manifest | `5ad7259eaf6f85b2595e559835aebe9cdb134a8d4d4989b6dcd9473da8d5e` |
| stopped-retry archive manifest | `cc0807b93ed9217ad9718b6ace19c2ee485d6a3e5ed40fdb3b041a40804bafca` |
| stopped-second-retry `SHA256SUMS` | `b0d1b0269ea9b167e3e2ccdbe19dfca6e43e2707c2970a2c9880d0565a497cd6` |
| regular runtime Python | `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118` |
| requirements lock | `b5c05b76c4e383b9bdedb783ed658fe33c368d660a1efe45f80c98e0f8adb3a0` |
| `SOURCE_COMMIT` | `c8b6e84e664ad080915af35416f91fb20b2a59f4cf9eee8d7a6193443215d0a6` |
| `recomputation.toml` | `0e11bb08976526f1217cf9ceef3a39bd6e960b5d8ee8fd84b63f80c0e36ecbca` |
| source-pinned controller | `312d110853d5c540e03c4ea94a72c5c9db402518820cf2c1efa095db22e5df46` |
| expiry service | `a853a0c79e5c89174d4ff65bef77fd553e1a38ebc4f0fec0bb50500d43e183e5` |
| expiry timer | `8e18f83e68d6a558818ec01bf023fc96b557a20af9ef3c3a216ecfd3fcd17941` |

## Preservation and stop conditions

Before the third retry, require the live state to remain disabled with no P7
key, credential, login, session, or reader process. Preserve the PostgreSQL
cluster start identity, complete `caplab_v0` data, P4 control, P6 registration
and timestamps, Garage object count and registered-byte verification, all 326
independent-copy hashes, source custody, earlier runtimes and stopped evidence,
and disabled writer/verifier access.

Stop and aggregate-revoke on repository, commit, install, timer, clock, role,
privilege, credential, session, registration, locator, byte, cardinality,
analysis, canonical-output, replay, or preservation drift. Do not repair or
reinterpret a live discrepancy. Another stop does not authorize repair or a
later retry.

## Authority excluded

Approval would not authorize capability inference, training-candidate or
training-eligibility decisions, export, model/provider calls, training,
publication, Striatum placement, preference work, CAPLAB-33 independent
verification, CAPLAB-34 acceptance, deletion of stopped evidence or earlier
runtimes, or a later retry. Those remain separate checkpoints and owner gates.
