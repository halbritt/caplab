---
id: caplab-8-native-r2-execution-2026-07-20
artifact_type: execution-record
title: CAPLAB-8 native r2 execution
status: executed-awaiting-normalization
created: 2026-07-20
decision_record: adr-0042
---

# CAPLAB-8 native r2 execution

## Executed campaign

Campaign `caplab-preference-001-native-r2-2026-07-20` executed all 12 frozen
primary slots under manifest SHA-256
`c6c6eb3e8b9801cc52150edb5fe1b609e2d1724ffc846268421f4330536526b9`.
All 12 attempts completed: six `claude-fable-5-max` through Claude Code and six
`codex-terra-max` through Codex CLI. No replacement was used. Cumulative trial
time was 1,311.331228 seconds. The raw custody tree contains 115 files and has
tree SHA-256
`f990811b8204840351ec9123ab5fb1025fcd2e9f9764720ad709abf839d510a8`.

Raw custody remains at
`/home/halbritt/.local/share/caplab/campaigns/caplab-preference-001-native-r2-2026-07-20`.
The ledger independently derives `complete=true`, `next_slot_index=12`,
`replacement_count=0`, and no stop reason.

## Observation lineage

| Attempt | Tuple | Observation SHA-256 |
|---|---|---|
| `a01-s01-primary` | `claude-fable-5-max` | `15e7262c3569a978c3c47853832807b33b14d780cec617bba7206be39dd18a65` |
| `a02-s02-primary` | `codex-terra-max` | `c8193e0e6ce035be7f66c0bef48f84d65df09819c9429d1c12fb23cc454b71d4` |
| `a03-s03-primary` | `claude-fable-5-max` | `bcc55eda33d35e4b3e5a44578f29a6a4a6c9c3327c86326c202d6e02e0541b13` |
| `a04-s04-primary` | `codex-terra-max` | `a9fe62004bcfab9e53cbae2b5a1afe1cf884a8afdeb915b47767319e2726cc90` |
| `a05-s05-primary` | `codex-terra-max` | `a03c128864456c3ff252ad78a444935ad090185e783ca494f8dd800c752eac2f` |
| `a06-s06-primary` | `claude-fable-5-max` | `5787672bfdce8a0a17632b122e91be825f0bd9319c2e40c3b946bd31fc150fdb` |
| `a07-s07-primary` | `claude-fable-5-max` | `b78730ccfce2c6b7c31fce1df4436ee4ef79ac2f00b5390d105f28fc0bcfab90` |
| `a08-s08-primary` | `codex-terra-max` | `a348f4292b56077e6dba860b380e2d4fa7b9898fef42db3653a30d5d3865ad22` |
| `a09-s09-primary` | `codex-terra-max` | `01b3babd7f295cfb6df08ce9e4a1844fccfb21b7ec6cb18fbfab70379091d27d` |
| `a10-s10-primary` | `claude-fable-5-max` | `9457b4f4abf4d9419a109d6f53f4927dfd18a5fbbfd4eba0c0a78baf02dc535c` |
| `a11-s11-primary` | `claude-fable-5-max` | `247d37133c6f80baabe812b436db3ea7628f7e36ce4fc0934dc1cd4fb90ba6e0` |
| `a12-s12-primary` | `codex-terra-max` | `ab5fe3a8d0d3d12dd5f25969639b65d07b39a161e48ff7b697fcc38c10490520` |

## Boundary

This record proves execution and captured custody, not scoring, preference,
inference, independent verification, or CAPLAB acceptance. Native
normalization and blind-packet code is implemented model-free under source
SHA-256
`494257688cd03710c33cafda60ce687e4eed65701ba68293c5903705797de8fb`,
but no normalized campaign artifact or disposition is authorized by this
record. A separate durable decision must bind that effect and delegation scope.
