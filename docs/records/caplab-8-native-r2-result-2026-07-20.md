---
id: caplab-8-native-r2-result-2026-07-20
artifact_type: result-record
title: CAPLAB-8 native r2 blind preference result
status: complete
created: 2026-07-20
decision_record: adr-0043
---

# CAPLAB-8 native r2 blind preference result

## Result

All six native r2 pairs were valid. The delegated primary-agent mechanism
froze blind selections `A`, `B`, `A`, `B`, `B`, and `B` for P01 through P06
before reveal. The frozen dispositions have semantic SHA-256
`311e887f1fe99308a190297020e798bd1218e588dcdefdac76dcb17164e7e063`.

Reveal produced these preregistered counts:

| Quantity | Count | Threshold |
|---|---:|---:|
| Valid pairs | 6 | minimum 5 |
| Fable strict constraint-advantage pairs | 0 | minimum 4 |
| Fable blinded-preference pairs | 5 | minimum 4 |

The exact conclusion is **hypothesis disconfirmed**. Fable was blindly
preferred in five of six pairs, but it had no strict mechanical-constraint
advantage because every pair tied on the mechanical count. Both thresholds
were required.

The result has semantic SHA-256
`8b312518d725d308ce24a1c901d64576dddeb35228ac885eb85dfaac4af1347e`.
Its claim ceiling remains a task-conditioned descriptive association on this
synthetic population only. It does not establish a causal mechanism, global
ranking, routing rule, training eligibility, other-evaluator result, or
cross-harness generalization.

## Custody and delegation

The packet manifest has semantic SHA-256
`16ddd4c5e01c4092d58b0f4c85c11e33a2f3d474c677278f73f0ee009ed6f1ef`.
The identity-bearing capture manifest has semantic SHA-256
`4253106bb1af456d6c3e0349a15b20a44cdd847856bf818b3c1c52f9756f8733`
and binds 12 normalized captures. All six blind packet hashes were frozen
before the reveal map was applied.

The preferences are delegated-agent judgments under ADR 0026 and ADR 0043,
not the repository owner's personal judgments. Raw r1 custody, the quarantined
proxy attempts, native r2 streams, observations, and final task trees remain
preserved and outside this result's mutation surface.

## Boundary

This record states the descriptive result. It is not independent verification
or broader CAPLAB acceptance. Technical verification is recorded separately in
[`caplab-8-native-r2-verification-2026-07-20.md`](caplab-8-native-r2-verification-2026-07-20.md).
