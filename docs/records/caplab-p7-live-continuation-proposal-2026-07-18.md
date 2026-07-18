---
id: caplab-p7-live-continuation-proposal-2026-07-18
artifact_type: decision-proposal
assertion_type: recommendation
campaign: caplab-study-001-p7-recompute-2026-07-18
decision_owner: repository-owner
status: awaiting-decision
---

# CAPLAB P7 live continuation proposal

## Decision requested

The repository owner must approve or decline this exact continuation. This
proposal is a recommendation. It is not a decision, authorization, execution
record, verification record, capability inference, or acceptance record.

Approve only this read-only sequence:

1. install clean CAPLAB commit
   `04ed8213ec7741d76d8bb9f9b6f972ebb4deaf3e` in the fixed P7 environment;
2. install and enact clean, pushed Proximal commit
   `79f04a537538012824bb948cc863a10d0219d82a`;
3. enable only the temporary `caplab_reader` PostgreSQL login and one expiring
   read-only Garage key for bucket `caplab-v0`;
4. run the model-free recomputation twice against P6 admission manifest
   `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`;
5. require byte-identical canonical outputs and exact pre/post preservation
   controls; and
6. revoke the key, credential, login, sessions, processes, and account window,
   then verify the disabled state.

The exact execution evidence root is
`/var/tmp/caplab-p7-execution-2026-07-18`, created `root:root 0700` only after
authorization and preserved with a verified SHA-256 manifest. Authorization
expires at `2026-07-25T23:59:59Z`; the timer begins aggregate revocation at
`2026-07-25T23:50:00Z` and retries failures.

## Observed readiness

- CAPLAB is clean at `04ed8213ec7741d76d8bb9f9b6f972ebb4deaf3e`.
  Its 93-test gate passed with four existing gated integrations skipped. Ruff
  and diff hygiene passed.
- The recomputation emits only a typed observation. It has no database,
  object-store, or independent-copy write interface and no inference, export,
  model, training, routing, publication, or acceptance command.
- Proximal is clean and pushed at
  `79f04a537538012824bb948cc863a10d0219d82a`. All 36 existing CAPLAB host tests
  passed with one gated PostgreSQL integration skipped; all six P7 access
  lifecycle tests passed; Ruff and diff hygiene passed.
- Read-only live inspection found the P6 registration at exact cardinalities
  684 records, 325 content identities, and 20 assignments, attempts, and
  outcomes. Garage and `/nvr` each retain 326 identities including the P4
  control. Writer, reader, and verifier PostgreSQL roles are `NOLOGIN`; no P7
  Garage key or credential exists.
- Final doctrine packet `pkt-c3a7efc417d731c6`, content SHA-256
  `c3a7efc417d731c6224fef79be330ab5b99922d73aaab4c07e8090735e21f093`,
  satisfied every required evidence class and limits the agent to execution
  without self-acceptance.

## Installed identities to verify

| File | SHA-256 |
|---|---|
| `caplab-p7/SOURCE_COMMIT` | `250a15ec2b8faccde513bb3c944a178b1faef0b0698f04933f79c93714ca1540` |
| `caplab-p7/recomputation.toml` | `c1cd92cabcd341e20682b055e1df7b8e965f87f522dd4ba7871dbb42e7001e56` |
| `caplab-p7/caplab-p7-accessctl.py` | `7f42d3749f762978ab9bf9e993e3f8b8b3d5e0c2bed03ddff4cebb31beb4d921` |
| `caplab-p7/caplab-p7-expiry.service` | `a853a0c79e5c89174d4ff65bef77fd553e1a38ebc4f0fec0bb50500d43e183e5` |
| `caplab-p7/caplab-p7-expiry.timer` | `8e18f83e68d6a558818ec01bf023fc96b557a20af9ef3c3a216ecfd3fcd17941` |
| CAPLAB requirements lock | `b5c05b76c4e383b9bdedb783ed658fe33c368d660a1efe45f80c98e0f8adb3a0` |

## Preservation and stop conditions

Preserve the live PostgreSQL start identity, P4 control, P6 registration and
timestamps, all Garage object/version identities, all independent-copy byte
identities, source-study custody, and disabled writer/verifier access. Stop and
revoke on repository, commit, install, timer, clock, role, privilege,
credential, session, registration, locator, byte, cardinality, analysis,
canonical-output, replay, or preservation drift. A mismatch is quarantined and
does not authorize repair or historical rewriting.

## Authority excluded

Approval would not authorize a capability inference, training-candidate
decision, training-eligibility decision, export, model/provider call, training,
publication, Striatum placement, preference study, CAPLAB-33 independent
verdict, or CAPLAB-34 acceptance. Those remain separate checkpoints and human
gates.
