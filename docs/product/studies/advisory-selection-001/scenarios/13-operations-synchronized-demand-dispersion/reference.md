# Reference repair

The three reported symptoms — the on-the-mark collapse, errors that outlast
each burst, and the four-minute outage after a fleet restart — are one defect
seen three times: every terminal is engineered to do the same thing at the
same instant. A repair that follows the doctrine treats each synchronized
stimulus in the agent and de-synchronizes it, rather than patching the single
most visible one.

**1. Break the shared wall-clock schedule** (`edgeagent/scheduler.py` /
`agent.py`). `next_sync_time` currently snaps every device to the same
interval boundary. The repair replaces alignment with a randomized schedule —
for example `now + interval * uniform(0.8, 1.2)` — or keeps boundaries but
adds a stable per-device offset (hash of `device_id` mapped into
`[0, interval)`), so that four thousand devices with the same interval no
longer target the same second. The dashboard-bucketing rationale in the module
docstring is handled server-side by bucketing on arrival time; it does not
require clients to arrive together. Results stay inside the
`(now, now + 2*interval]` budget the existing scheduler tests assert.

**2. De-synchronize retries** (`edgeagent/transport.py`). The fixed
`RETRY_DELAY_SECONDS = 5.0` pause means every device that failed in the same
burst retries in the same later second — this is why errors "drag on after
each burst": each wave of retries re-creates the load that caused the
failures. The repair makes the delay grow across attempts (e.g. doubling from
a small base, capped around a minute) and draws each pause randomly (e.g.
uniformly between half and the full current ceiling), so a blip decays instead
of echoing. `MAX_ATTEMPTS` stays as is.

**3. Spread the boot check-in** (`edgeagent/agent.py`). `start()` checks in
immediately, so a rack power-cycle (or fleet-wide restart) reconnects
every terminal in the same second. The repair sleeps a random, bounded amount
before the first check-in — e.g. uniform over `[0, min(interval, 120 s)]` —
so a restarted fleet re-arrives across a window while a single fresh terminal
still gets its config promptly. (Injecting an `rng` alongside the existing
`clock`/`sleep` injection keeps this testable.)

Equally important is what the repair does **not** do: it does not merely
lengthen the interval or raise a constant (a longer synchronized period is
still synchronized), does not bolt on server capacity or caching (out of scope
of this repo, and no steady-state provisioning survives an organization that
points its whole fleet at one second), does not delete the immediate boot
check-in (all devices would then just meet at the next boundary), and does not
touch anything under `tests/` — the existing suite asserts bounds, not exact
instants, and passes unchanged.
