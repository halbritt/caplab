---
id: caplab-p6-admission-execution-2026-07-17
artifact_type: execution-record
campaign: caplab-study-001-p6-admission
decision: adr-0014
executor: primary-agent
executed_at: 2026-07-17
status: complete
---

# CAPLAB P6 restricted admission execution

## Authority and boundary

The repository owner delegated CAPLAB decision authority and explicitly
authorized the restated P5-then-P6 boundary. ADR 0014 records that authority,
the exact Study 001 source set, the `2026-07-24T23:59:59Z` expiry, and the hard
stop before P7. This execution registered historical bytes and links only. It
performed no recomputation, model or provider call, inference, export,
publication, training action, purge, or acceptance.

The CAPLAB implementation commit was
`137d0724ca22956d04d75f41e02e0b36b146e5f6`. The separate Proximal desired-state
commit was `2beb093f4c299000cc935c770f884b77a622fe80`.

## Pre-effect observations

- CAPLAB and the P6 Proximal worktrees were clean at their exact pins.
- All 681 preservation-manifest entries passed SHA-256 verification. The
  manifest-file SHA-256 was
  `081a14d9b4f2872a2d8058f1b0896a7d0e4fd954f164b8c46d2d768558a0d50c`.
- The preregistration, result record, and result CSV read from their exact Git
  commits matched the three ADR-selected SHA-256 identities.
- The live PostgreSQL cluster remained `/var/lib/postgresql/17/main`, listening
  only on loopback port 5432, with start time
  `2026-07-03 06:16:25.66893+00`. Port 55435 had no listener.
- P4 retained its one registration and 98-byte independent copy with content
  SHA-256
  `87fcfd5dbd6607da7899181ddd707b697cd4fa503c5e8cff8e169b5472172d92`.
- The P6 relational tables and registration were absent. Writer, reader, and
  verifier PostgreSQL roles were `NOLOGIN` with no password.

## Execution effects

Migration `0003_study_admission.sql`, SHA-256
`34d3c484d23dca5b2a4ebf0dcbd5cc4597e40fb5e240e86b91dcfeef3f2c2974`,
was applied once under runtime commit `137d0724ca22956d04d75f41e02e0b36b146e5f6`.
It added only append-only Study 001 registration, object, evidence-record,
identity, assignment, attempt, and outcome tables. The writer received
`SELECT, INSERT`; reader and verifier received `SELECT`; none received update
or delete authority.

The exact CAPLAB commit was installed in a separate P6 environment. Three
selected Git blobs were extracted from their commits into a restricted,
non-worktree stage. Read-only ACLs on the unchanged preservation root allowed
only the temporary writer and independent verifier to perform the source
checks. The historical checkout was not modified or used as runtime input.

The temporary writer's source verification produced registration manifest
SHA-256
`d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`
with this exact summary:

| Layer | Count |
|---|---:|
| Evidence records | 684 |
| Unique content identities | 325 |
| Trial assignments | 20 |
| First attempts | 20 |
| Mechanical outcomes | 20 |
| Named identity kinds | 11 |

All 684 records have disposition `restricted-admission`. The 681 preservation
members, governing manifest, and two later Git result records are separately
accounted for. The preregistration Git provenance is attached to its already
preserved record rather than inventing a 685th record.

Each unique byte identity was read from the selected source, written or
matched at its content-derived Garage key and independent `/nvr` key, and read
back by SHA-256. The complete source inventory was rebuilt before the manifest
freeze. PostgreSQL then froze one registration with 684 evidence rows, 325
object identities, and exact 20/20/20 relational links. Parsed decimal JSON
lexemes are represented as strings in typed identity projections to avoid
ambiguous floating-point identities; the authoritative historical JSON bytes
remain unchanged and registered by hash.

The same admission command was replayed. It returned
`idempotent_replay=true`, added no registration or audit event, and left the
independent-copy inventory hash unchanged at
`af03a7492c4006e984062de349657002e5142426494c02fee886857afe6f8387`.

## Revocation and final observations

The writer key, credential file, PostgreSQL login, sessions, and preservation
ACL were removed before independent verification. After the independent PASS,
the verifier key, credential file, PostgreSQL login, sessions, and preservation
ACL were also removed. Reader access was never enabled. All three PostgreSQL
roles are now `NOLOGIN` with no password and have zero active sessions.

Final PostgreSQL cardinalities remain 1 registration, 684 evidence records,
325 unique objects, 20 assignments, 20 first attempts, and 20 outcomes. Garage
and `/nvr` each contain the 325 P6 identities plus the unchanged P4 control.
The full preservation manifest passed again. PostgreSQL and Garage remain
active; the live PostgreSQL start identity and P4 registration are unchanged.

## Evidence and verification handoff

Root-custodied execution evidence is under
`/var/tmp/caplab-p6-execution.PZsK9Rnd`. Its 50-file SHA-256 manifest is
`9b1aae3deaeeebad7553192d493da2bcb7315517e5a3050e87ce9c6be2dcd1ef`.
It contains no retained Garage secret. Independent verification is recorded
separately; execution does not verify or accept itself.

