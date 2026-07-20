# CAPLAB preference-study instrument

This package owns the model-free qualification boundary for
`caplab-preference-001`. The frozen instrument is
[`docs/product/studies/preference-001/instrument.json`](../../../docs/product/studies/preference-001/instrument.json).

`load_instrument` validates the complete design digest, exact task-contract
digests, subject identities, shared harness surface, byte-identical subject
instruction, execution order, reveal map, and zero-call authorization.
`render_task` creates one fresh synthetic repository. `run_canned_attempt`
captures only explicit `canned` inputs and separates mechanical constraint
results from the still-empty human disposition. `build_blinded_packet` omits
subject seals and operational metadata and recursively refuses identity clues
rather than silently redacting them. `assess_study_state` applies the frozen
replacement, invalid-pair, and blinding-breach stop rules.

The model-free instrument module has no model, provider, live harness,
credential, network, subprocess, export, training, or adjudication adapter.
Canned captures are qualification data, not study results or model evidence.

The separately authorized CAPLAB-8 boundary is
[`live.py`](live.py), bound by
[`live-manifest.json`](../../../docs/product/studies/preference-001/live-manifest.json)
and ADR 0037. It validates the zero-call instrument before building the exact
one-trial Harbor command, enforces append-only attempt ordering and campaign
limits, hashes raw custody, and refuses reveal until all six blind dispositions
are frozen. Its task template sets `network_mode = "no-network"`; provider
requests remain in the host-side Harbor agent. A live trial is unavailable
unless the caller invokes the explicit `run` command with the exact committed
manifest, instrument, slot, and attempt kind. The CLI derives prior accounting
from sealed raw-custody observations; an unclassified attempt blocks another
call.
