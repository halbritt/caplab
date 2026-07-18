---
id: caplab-p7-live-attempt-2026-07-18
artifact_type: execution-record
assertion_type: observation
campaign: caplab-study-001-p7-recompute-2026-07-18
authorization: adr-0017
status: stopped
---

# CAPLAB P7 stopped live attempt

## Scope

ADR 0017 authorized one execution of the exact P7 continuation. The executor
installed the frozen CAPLAB runtime, Proximal controller, configuration, and
expiry timer; captured the pre-effect controls; and attempted to enable the
temporary reader. This record states observed execution and cleanup facts. It
is not an independent verdict, capability inference, retry authorization, or
acceptance record.

## Observations

- The frozen CAPLAB commit
  `04ed8213ec7741d76d8bb9f9b6f972ebb4deaf3e` passed its 93-test gate with
  four explicitly gated integrations skipped. Its 54 installed package files
  matched the frozen Git bytes.
- The exact Proximal files from
  `79f04a537538012824bb948cc863a10d0219d82a` were installed, and the expiry
  timer was enabled and active. A regular, root-custodied copy of the system
  Python binary was required because the controller correctly rejects a
  symlinked interpreter path.
- Two preparation attempts stopped before reader enablement: one malformed
  shell wrapper and one symlinked-interpreter refusal. Direct checks after
  each found no P7 key, credential, state, login, session, or reader process.
- The next attempt created one expiring read-only Garage key and enabled only
  `caplab_reader`. Ready verification then stopped with `Garage key bucket
  authority is wrong` before either recomputation command ran.
- Garage 2.3.0 returns `id` and `localAliases` identity metadata in each bucket
  grant. The installed controller compared the complete response with a mock
  object that omitted those fields. The observed permissions remained exactly
  owner false, read true, and write false; the failure was response-shape
  incompatibility, not widened authority.
- The installed cleanup trap completed aggregate disablement. The retained
  state is `disabled`; the P7 key and credential are absent; the reader is
  `NOLOGIN`; and reader sessions and processes are zero.
- The normalized whole-schema dump, PostgreSQL cluster identity, P4 and P6
  controls, Garage bucket summary, and all 326 independent-copy hashes match
  their pre-effect observations. No recomputation output exists.

## Evidence custody

The 54-file root-owned evidence set remains at
`/var/tmp/caplab-p7-execution-2026-07-18`. Its `SHA256SUMS` file has SHA-256
`6292d169cb5ccd9f37b69514be35b2a50395cd6b51be9f37721a788d0831aa61`
and passed verification. It contains no retained Garage secret and does not
contain a recomputation result.

## Result and boundary

**Execution result:** stopped before P7 recomputation. CAPLAB-25 remains open.
ADR 0017 is consumed: it authorized no changed controller, recovery action, or
second execution.

The causal controller repair is prepared in pushed Proximal commit
`8c45e62a22cf5c7e566df2d4510b49742f39b6ac`. Seven lifecycle tests pass,
including exact Garage 2.3 response acceptance and rejection of write
authority or a local alias. Installing that commit or retrying live execution
requires a new exact owner decision.

