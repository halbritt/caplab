---
id: caplab-p7-runtime-custody-repair-2026-07-19
artifact_type: implementation-record
assertion_type: observation
campaign: caplab-study-001-p7-recompute-2026-07-18
authorization: adr-0016-stage-a
status: prepared
---

# CAPLAB P7 regular-file runtime custody repair

## Scope

ADR 0016 Stage A permits model-free P7 host-surface preparation. This record
describes the narrow correction after ADR 0021 stopped before access creation.
It is not live execution, independent verification, a capability inference,
retry authorization, or acceptance.

## Repair

The stopped runtime was preserved at
`/opt/caplab/p7/bf6de2b24ac61e82107208cdc609c7e534c6eaaa-symlink-stopped-20260719`.
The same clean CAPLAB commit was rebuilt with
`/usr/bin/python3 -m venv --copies` and atomically installed at the fixed source
path. Its `bin/python` is now a regular, non-symlinked `root:caplab` mode-0750
file with SHA-256
`1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118`,
matching `/usr/bin/python3`.

The dependency lock and CAPLAB package were installed without changing source
identity. The wheel has SHA-256
`e67dea2c0aaed8034ca19f549e8ad7c188c1498e898926f2b9a1d49e3c339d53`.
The sorted installed CAPLAB source inventory has manifest SHA-256
`fd32d932f2dd90ef486ec199b8fd9930eb69a11aeea86ed107a77d9cd299f322`.
Package imports, command help, and the frozen 105-test CAPLAB gate pass.

## Desired-state guard

Clean, pushed Proximal commit
`1b79aa07cc4e44e8fc828449f882c6b62008edb6` requires `venv --copies`, a
regular-file `lstat` check, and a stop before enablement on custody drift. A
tenth lifecycle test proves a symlinked interpreter is refused before Garage
key creation. All ten controller tests, Ruff, systemd verification, and diff
hygiene pass. The controller's symlink refusal was retained unchanged.

## Guidance and boundary

Doctrine packet `pkt-02f55cfae37b87d6`, content SHA-256
`8786f14e4c714b29c131591613c590945e45843aa11ae5813532eb975b55f48f`,
supports changing the causal construction step, retaining the safety check,
and pairing the next resource acquisition with mandatory cleanup. It does not
authorize live execution.

No Garage key, credential, login, session, process, database row, evidence
object, or campaign state was created by this repair. Another live attempt
requires the repository owner's fresh retry instruction to be bound to exact
identities and stop conditions.
