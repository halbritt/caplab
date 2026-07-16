# CAPLAB-23/P5 independent verification record

Result: **FAIL** for CAPLAB-23/P5.

Verification completed at `2026-07-16T19:14:03Z` by the fresh independent
verifier `/root/caplab_p5_independent_verifier`.

This record verifies only campaign `caplab-p5-recovery-2026-07-16` against
ADR 0009 and assignment v6. It is not CAPLAB acceptance and grants no authority
for CAPLAB-24/P6, CAPLAB-25/P7, another live P5 attempt, evidence admission,
model calls, training, export, or publication.

## Frozen criteria and evidence

The verifier used:

- CAPLAB commit `c82b5512661c537db06f725af70198eccc818358`;
- Proximal host-surface commit
  `0263aff7bc3bf34bff28be008fa9f370a7065ed4`;
- authorization expiry `2026-07-23T23:59:59Z`;
- operation `op-p5-recovery-0001`;
- request SHA-256
  `4164a5d4febd4f429158d5917a15ae303392ecf1d9d6a57e84ae9a731282b229`;
- content SHA-256
  `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`;
- object and local-copy key
  `objects/sha256/a1/a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`;
- manifest SHA-256
  `77acb678e5fa2d99374ba5a2e5841a043d904333a7718612fd3b0153a057f1b4`;
- authorization-document SHA-256
  `e8cd172af19cb631ba6814a3fd57c7b91f381cd799de862d9bd277b6ef68d34f`;
- pre-effect rollback backup
  `20260712-010203F_20260716-013021D`; and
- selected isolated restore target `/var/tmp/caplab-p5-pgrestore`, port
  `55435`.

All five root-only execution manifests matched their recorded manifest hashes,
and `sha256sum -c SHA256SUMS` verified every listed artifact:

| Execution root suffix | `SHA256SUMS` SHA-256 |
|---|---|
| `20260716T184952Z` | `3b06e1db6588b62cb77ce2afd004a639b9d29cd99f1dc172078a3cb9a3e43900` |
| `20260716T185245Z` | `db6b8aeed897b3e04306ba90b7b4c6623ccce8866d5082671a791910ed813999` |
| `20260716T185843Z` | `2d633326d83bb7c000c8ccefe3fb1d4e70667195c9cc13b5ed78b4b08ec5570b` |
| `20260716T190335Z` | `c8c9393661f5d3b7485048d7192d30ff4a423056fa98b4b910e8407751bce30b` |
| `20260716T190544Z` | `2c25fd8a5a99a6c975562c16c9b482dc3f3316fa9da52de57707994fc622237f` |

The final root preserves sanitized command descriptions, stdout, structured
stderr, and direct numeric `.rc` files for every recorded command.

## Stopped-attempt observations

The verifier independently confirmed:

1. root `184952Z` stopped at Git trust before bootstrap and retained no P5
   role, migration, or data effect;
2. root `185245Z` stopped before migration or credentials because installed
   paths were not traversable, then removed the empty temporary identities;
3. root `185843Z` stopped at a pre-registration local-copy mode refusal,
   retained P5 counts `0|0|0`, disabled access, and preserved P4 identities;
   and
4. root `190335Z` stopped in disabled-retry preflight before any new bootstrap
   or data effect.

These roots support the recorded fail-closed boundaries. They are not
successful P5 executions.

## Final execution observations

**Observation:** host retry preflight, bootstrap, and ready verification
returned direct status `0`. P5 inventory was empty before registration and P4
control was present.

**Observation:** wrong-role registration returned `ConfigurationError` with
direct status `2`. Invalid and ambiguous attempts were recorded as separate
typed observations without subject-outcome fields.

**Observation:** the controlled interruption returned direct status `4` after
both byte copies were verified. Inventory then identified the incomplete
request and exact unreferenced object and copy. The changed request was refused
with status `2`; an identical interrupted replay again returned status `4`,
supporting byte reuse under the same identities.

**Observation:** the next identical replay durably finalized the exact P5
registration but returned direct status `2`:

`MetadataMismatch: migration runtime commit differs from provenance`.

Duplicate replay and verifier calls returned the same refusal.

The live migration ledger contains:

- `0001_runtime_core.sql`, hash
  `7e075ccb2263f7926fa6b221d46ea908aba6f51a54aee412703657665ca3533b`,
  runtime commit `405efb136b221d1270578417c64b3f7878383f32`; and
- `0002_p5_recovery_custody.sql`, hash
  `c3c69be60c33d56c70eb4a02f273f13b95da778c14c079cdf447772a94a0eb2b`,
  runtime commit `c82b5512661c537db06f725af70198eccc818358`.

**Inference:** the evidence supports the execution record's diagnosis that an
all-migration-rows-equal provenance assertion rejected a legitimate
forward-only mixed-commit ledger. Byte corruption, locator drift, and
migration-file hash drift are contradicted by the retained observations. This
diagnosis does not authorize repair or another campaign.

## Live quarantine observations

PostgreSQL contains the unchanged P4 registration and the exact P5
registration. No custody request, purge tombstone, or current P5 custody
dependency exists. The invalid and ambiguous observations remain.

The live `/nvr` hashes are:

- P4:
  `87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`;
- P5:
  `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d`.

Garage inspection reports both objects complete, non-uploading, non-aborted,
and not delete markers. The preserved direct S3 read before disablement
recorded the P5 Garage SHA-256 as the frozen content hash.

The live P4 operation, request, content, locators, manifest, identity layers,
Garage object, and local copy equal the pre-effect control.

`/usr/local/libexec/caplab-p5-hostctl verify --phase disabled` passes. No P5
Garage key alias or credential directory exists. `caplab_p5_operator`,
`caplab_p5_verifier`, and `caplab_custodian` are `NOLOGIN`; the two operating
system accounts are locked, use `/usr/sbin/nologin`, and own no observed
process. The expiry timer is inactive and disabled.

The shared `objects/sha256` directory remains `caplab_writer:caplab` mode
`0750` with no named ACL. The exact `a1` prefix is `root:caplab` mode `0750`;
the quarantined P5 file remains mode `0440`.

The live lifecycle record is byte-identical to
`disabled-quarantine-state.json`, SHA-256
`908dc8ba1f091a973b17e0dae2facc4bc09a46c4e0ace85206f4f3d16e174be4`,
and records phase `disabled`.

The cleanup plan has SHA-256
`571bb610ba4a92612958b18e0dc0ff8811ad870c53794d070f509b095df89cf2`,
status `quarantine-required`, authorizes no deletion, and retains the exact P5
identities. The isolated restore is absent and port `55435` is not listening
because no restore was performed.

## Supported criteria

Independent evidence supports:

- the frozen commits, authority, identities, hashes, verifier assignment, and
  execution-root manifests;
- the fail-closed boundaries and residual states of all four earlier attempts;
- host readiness, role refusal, typed invalid/ambiguous observations,
  controlled interruption, orphan inventory, changed-request refusal, and byte
  reuse on identical replay;
- the exact P5 registration and good P5 bytes at quarantine;
- unchanged P4 control; and
- correct stop, non-applying cleanup plan, evidence preservation, access
  revocation, and exact-prefix custody.

## Mandatory unmet or contradicted criteria

1. Completed registration verification failed with `MetadataMismatch`.
2. Completed duplicate replay did not return a successful idempotent result.
3. Missing and altered Garage recovery drills were not executed.
4. Missing and altered `/nvr` recovery drills were not executed.
5. The non-destructive Restic repository check was not executed.
6. No exact post-registration pgBackRest backup was created.
7. No isolated PostgreSQL restore was performed or verified.
8. The dependency-refusing purge rehearsal was not performed.
9. Byte staging/removal and guarded database purge were not performed.
10. No purge tombstone exists.
11. Final absence and clean completion are contradicted by the retained
    quarantined P5 database and byte state.

## Verification result

**FAIL for CAPLAB-23/P5.** Mandatory ADR 0009 registration-verification,
recovery, backup, isolated-restore, dependency, purge, tombstone, and
final-absence criteria are unmet or contradicted. The executor correctly
stopped, disabled access, preserved good bytes and evidence, and quarantined
the P5 state; those safe stop actions do not convert the partial campaign into
a pass.

The verifier explicitly refuses to accept CAPLAB or authorize CAPLAB-24/P6.
