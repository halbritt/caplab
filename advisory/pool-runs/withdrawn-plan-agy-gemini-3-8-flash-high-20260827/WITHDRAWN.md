# Withdrawn after one row — not a measurement

Planning sweep attempt for `agy-gemini-3-8-flash-high`, seed 20260827, pinned
P2b instrument, 2026-09-02. Stopped after the first row returned agy
`status: ERROR` ("Agent execution terminated due to error.", 112 s, exit 1)
under a pass-neutral adapter (`--output-format json`, payload at `/response`,
no schema pin) inside bubblewrap. The same prompt (`pt-f86095a00f0c624f`,
24 KB) through the same adapter OUTSIDE bubblewrap produced a correct
two-packet plan-v2 work graph, rc=0. The failure is the harness meeting the
sandbox on a long prompt, not the model; it was not diagnosed further
because the planning instrument does not rank (P2b record) and the
declaration was then re-shaped to the sibling's review-pinned adapter for the
review sweep, under which a 24 KB prompt succeeds inside bubblewrap (456 s).

Directory renamed off the `plan-` prefix so the board report does not read
one errored row as a subject. Kept as evidence.
