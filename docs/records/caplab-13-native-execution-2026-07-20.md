---
id: caplab-13-native-execution-2026-07-20
artifact_type: execution-record
title: CAPLAB-13 native development execution
status: executed
created: 2026-07-20
decision_record: adr-0044
---

# CAPLAB-13 native development execution

## Executed campaign

Campaign `caplab-review-dissent-001-development-native-r1-2026-07-20`
executed all 16 frozen primary slots under manifest semantic SHA-256
`b6d810ea4ee1ec55cb2f3d69646e18dc1fe34fd9d596cee940c162e367b10446`.
Eight attempts used `claude-fable-5-max` through Claude Code and eight used
`codex-terra-max` through Codex CLI. There were no infrastructure failures and
no replacements. Cumulative trial time was 1,517.353334 seconds.

Both native harnesses passed the exact no-inference version and authentication
preflight before launch. The campaign ledger derives `complete=true`,
`next_slot_index=16`, `replacement_count=0`, and no stop reason.

## Observation lineage

| Attempt | Cell | Tuple | Status | Observation SHA-256 |
|---|---|---|---|---|
| 1 | `r03` | `codex-terra-max` | invalid | `1277afb52316f6afbf14b8bf1a834c3792ba7eb55d26f94795cfbdc68f6a0c81` |
| 2 | `r04` | `claude-fable-5-max` | invalid | `7dcf0a1d48d3482e22b8e27f5df2d27451703607c56f7f3765b1c640cb916f48` |
| 3 | `r07` | `claude-fable-5-max` | invalid | `5113aa15d93392711b9062cda4356408b08eef1558ac2ceee4a6316ced6403e4` |
| 4 | `r08` | `codex-terra-max` | invalid | `293daa097685e7866cda2344fb6f4c76ace16d574cf91e774504317e4fdb1e01` |
| 5 | `r02` | `codex-terra-max` | invalid | `9c577ad33c22e31ab6716edf8157487b769338c8d05a8eede6cb01a7b04fd085` |
| 6 | `r01` | `claude-fable-5-max` | invalid | `62e1500aa7ad39cd95fbcf5f47c5c6fd37da0b0db7f3bbe9d85db253262d1f8c` |
| 7 | `r06` | `claude-fable-5-max` | invalid | `92a8b16a62ede00c535f0be592136983e96d74d6feb821eb52948e1a450ffbba` |
| 8 | `r05` | `codex-terra-max` | invalid | `782d8b2f9674280de7d4f01bf7d80ec8c3a22b6f524d329e2a5cd14f309e7dee` |
| 9 | `r04` | `codex-terra-max` | invalid | `b279cb282d549162921dce7f3e607f801ffd462210983575cfbd08c053fb80ff` |
| 10 | `r03` | `claude-fable-5-max` | invalid | `effbeecda58264cdb8f2233f3f9b02cce54dcf393a778384abd36c4254038c96` |
| 11 | `r08` | `claude-fable-5-max` | invalid | `29d5e9cb6e6a2cdaf92dba6e054ae4068698998b17ee7dc295a645f97d9eb6e7` |
| 12 | `r07` | `codex-terra-max` | invalid | `a0a8a6f3ef34e596a51b4a18209ef137074a0008d612ba63f8d1b149161382c3` |
| 13 | `r01` | `codex-terra-max` | invalid | `d441fc9b18a1477bc93f760c7efca09a92cd5bd51c807226640df33a34434b2e` |
| 14 | `r02` | `claude-fable-5-max` | invalid | `4a41035d2e1978d6fe4d685706957b9d9f6cef0382296dd1b8616900b88e2492` |
| 15 | `r05` | `claude-fable-5-max` | invalid | `0ea776d44f7dfb40cc8add4b802b1e6b3d56f957132b1ddf280e57596c9ea154` |
| 16 | `r06` | `codex-terra-max` | invalid | `71eef0affa7566d42ccc60ce179d9b8358be336cbddb1762c0f04e8bcab83761` |

Every harness returned a review artifact. `invalid` is a subject outcome: each
review used severity values outside the exact frozen `critical` or
`noncritical` enum. It is not an infrastructure failure and no slot was
replayed.

## Custody boundary

Raw custody remains at
`/home/halbritt/.local/share/caplab/campaigns/caplab-review-dissent-001-development-native-r1-2026-07-20`.
After authorized additive normalization it contains 239 files with tree
SHA-256
`8999e7423accb3cfc99c33a8cfa0cdd92ec431c004a1b9f22914a3f32edb0f67`.
Held-out content was not opened.

This record proves native execution and custody. It does not rescue invalid
reviews, compare subjects, authorize a rerun, supply verification, or accept
CAPLAB.
