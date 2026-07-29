# Reference repair (one possible doctrine-following solution)

## What is actually wrong

`DeliveryService.send(event, url, **options)` promises nothing: it accepts any
keyword and forwards the bag to `RetryPolicy.from_options`, which reads
loosely-namespaced keys (`retry_backoff`, `retry_multiplier`, `retry_jitter`,
`retry_cap`) plus un-namespaced `max_attempts` and `timeout`. When retry
handling was extracted in 0.4.0, the option keys drifted, but every caller —
`app/dispatcher.py`, `scripts/replay.py`, and the README example — still passes
`backoff=`. Nothing rejects the stale spelling, so it is silently dropped and
the policy falls back to a zero-second default: five attempts in one burst.
The suite stays green because each layer is tested against its own private
assumption; the mismatch lives in the unstated seam between them.

## The repair

**Inventory the real consumers first.** The dispatcher, the replay script, and
the README use exactly three capabilities: number of attempts, spacing between
attempts, and per-request timeout. Nobody sets multiplier, jitter, or cap.

**Close the surface to that inventory.** Replace the open `**options` mapping
with an explicit keyword-only signature sized to demonstrated use, e.g.
`send(event, url, *, max_attempts=5, backoff_seconds=1.0, timeout_seconds=5.0)`.
Delete `RetryPolicy.from_options` and its dict lookups; `send` constructs
`RetryPolicy(max_attempts=..., backoff=...)` directly. Multiplier, jitter, and
cap remain internal defaults of `RetryPolicy` — real complexity hidden behind
the boundary, not knobs leaked through it. With an explicit signature, any
stale or misspelled option name now fails immediately with a `TypeError`
instead of silently reverting to defaults — the whole class of this bug, not
just yesterday's instance, becomes impossible to hit quietly.

**State the meaning callers depend on.** Give `send` a docstring that carries
the non-obvious obligations: spacing and timeout are in seconds; spacing grows
exponentially between attempts; only 5xx responses and transport failures are
retried (4xx is returned as-is); when attempts are exhausted it raises
`DeliveryError` carrying the attempt count and last status; the event is not
mutated. Update `app/dispatcher.py`, `scripts/replay.py`, and the README to the
new names — `backoff_seconds=2.0` in the dispatcher — so intent and behavior
agree everywhere.

No test file changes. The existing suite passes as-is: it exercises defaults,
`max_attempts`, and policy math, none of which change meaning.

## Acceptable variations

Keeping the name `backoff` but documenting its unit, or accepting one frozen
options dataclass with exactly these fields, are equally good. What is
essential: the entry point declares a closed, explicit set of options limited
to what real callers use; unknown names fail loudly; and the units, retry
conditions, and terminal failure behavior are stated at the definition, with
all in-repo callers made consistent. Merely translating `backoff` to
`retry_backoff` somewhere — while `send` keeps accepting and dropping arbitrary
keywords — fixes the symptom and repeats the defect.
