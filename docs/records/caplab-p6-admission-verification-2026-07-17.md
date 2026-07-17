---
id: caplab-p6-admission-verification-2026-07-17
artifact_type: verification-record
campaign: caplab-study-001-p6-admission
decision: adr-0014
verifier: caplab_p5_adr0012_preflight
verified_at: 2026-07-17
verdict: pass
---

# CAPLAB P6 restricted admission verification

## Verdict and independence

**PASS.** Independent verifier `caplab_p5_adr0012_preflight` did not implement
or execute P6. It ran the installed read-only source and registration checks,
audited the relational links and role boundary directly, and verified the P4
and live-cluster controls. This is technical verification only. It does not
accept CAPLAB or authorize P7, recomputation, a model/provider call, inference,
export, publication, training, or purge.

The root-only independent report SHA-256 is
`00fcc64de6b46d3baa9b3ad037f8f0f4225e53832b1fae965e9532d8199e6f69`.
Its passing evidence-manifest SHA-256 is
`fd0199b1c64f74d6019e98a35704cb37af81c4598703ae6cd3ecc4b58f291045`.

## Verified observations

- CAPLAB was clean at `137d0724ca22956d04d75f41e02e0b36b146e5f6` and the
  Proximal desired-state worktree was clean at
  `2beb093f4c299000cc935c770f884b77a622fe80`.
- The installed package matched the pinned CAPLAB source bytes, excluding only
  interpreter cache files.
- All 681 preservation members and all three selected Git-stage files matched
  their frozen SHA-256 identities after execution.
- The verifier's fresh `source-verify` returned `status=match` for manifest
  `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`
  with exact counts 684/325/20/20/20.
- The verifier's fresh registration check returned `ok=true`; PostgreSQL,
  Garage, and independent `/nvr` status were all `match`.
- Direct SQL found exactly one registration, 684 evidence records, 325 unique
  objects, 20 assignments, 20 attempts, 20 `attempt_number=1` values, 20
  outcomes, and 11 required identity kinds.
- Every disposition was `restricted-admission`. There were zero alternate
  dispositions, locator or byte-count mismatches, link gaps, cross-manifest
  links, or sequence/block/task/condition inconsistencies.
- All 20 attempts retained non-null sealed, start, and finish timestamps from
  their historical records. All 20 outcomes linked to the first attempt and
  recorded no invented human disposition.
- Garage and `/nvr` each contained 326 identities: the 325 reconciled P6 byte
  identities plus the unchanged P4 control.
- P4 retained its exact registration, Garage version identity, 98-byte local
  copy, and content hash
  `87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`.
- The live PostgreSQL data directory, loopback listener, port 5432, postmaster
  PID `2654541`, and start time `2026-07-03 06:16:25.66893+00` were unchanged.
- The writer and reader were disabled during verification. The verifier had
  read-only database and Garage access and no source or custody write access.
  The CLI exposed only `source-verify`, `admit`, and `verify`; static inspection
  found no P7 or broader effect interface.

## Post-verdict closure

The verifier identified one required post-verdict action: disable its temporary
read access before projecting CAPLAB-24 Done. The executor subsequently removed
the verifier key, credential file, PostgreSQL login and sessions, and source
ACL. Writer and reader remain disabled. This closure was executed after the
independent report and is therefore an execution observation, not part of the
verifier's PASS.

## Residual risks

All evidence remains restricted. Exact hashes and automated credential
screening cannot disprove every latent sensitivity or licensing issue. The
registration is append-only; any withdrawal or purge needs a later exact owner
authorization. No evidence may be published, exported, or used for training
under this PASS.

