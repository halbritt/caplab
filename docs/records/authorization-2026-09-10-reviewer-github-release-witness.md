# GitHub release preservation witness

Under ADR 0026, the primary agent authorizes local development evidence for
the fixed sample's ai-newsroom repair
`c04f6c8b3af6bef8876330f37d02c42effd12908`, its first-parent base
`33881f4a341681fb3b29f6cfd87bdb08e1de9134`, and the original adapter introduction
`e7672756e15b45e68e7f0725b54247cc3e93b89a`. Copy their complete regular-file
trees with commit/tree/blob/hash provenance into private custody
`reviewer-ranking-001/development/github-release-witness-1`. Also preserve
the introduction parent's README and source-adapter contract, naming commit
`fd4c031e7d7735ab5103cc0bf23987bf9090491a`, paths and content hashes.
These copies are development custody, not historical evidence admission.

Freeze a probe, fixtures and criteria before calling the public `fetch()`
method. Use a local HTTPS server in a network-disabled namespace, with a
generated certificate for `api.github.com` and a private hosts mapping.
Do not replace the adapter's HTTP functions or parsing. Supply no real token,
owner state or production-service mount. Record the server's requests and
responses as well as the actual returned articles and private state writes.

Authorize one 12-second TLS/environment preflight and 36 new source executions:
three exact revisions, four conditions, three repetitions. Conditions are
ordinary quota, low quota with an eligible release, low quota with a draft,
and low quota with an empty release list. Each process has a 12-second limit;
total process time is at most 180 seconds. Stop after preflight failure or
input drift. A consumed slot cannot be replayed. Expiry is consumption or
2026-09-11T00:00:00Z. Preserve every result and failed criterion.

The behavior of interest is preservation of a successfully fetched, eligible
release despite a low remaining request quota. Ordinary quota must exercise
the same path successfully; draft and empty controls must not invent releases.
Pausing subsequent requests is compatible with preserving the current body.
Record the localized source change responsible for loss. Repetitions are
observations of one family, not independent defects. No reviewer call, source
repair, clean-label acceptance or ranking is authorized by this record.
