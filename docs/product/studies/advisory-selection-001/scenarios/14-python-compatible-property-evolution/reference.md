# Reference repair

The interval field now has an earned rule: the 5–3600 s operating band must
hold no matter how a value reaches a job — construction from the config file,
an operator update through the control socket, or any future code path. The
pristine tree enforces it only inside `ProbeJob.__init__`, so plain assignment
— which is exactly what `RuntimeController.apply_update` does via `setattr` —
walks straight past it.

A repair that follows the doctrine evolves the field in place rather than
patching the one call site that got caught:

- In `upmon/probe.py`, `poll_interval` becomes a property on `ProbeJob`. The
  setter applies `clamp_interval` and stores to a non-public backing slot
  (e.g. `self._poll_interval`); the getter just returns the stored float — no
  I/O, no logging, no recomputation on access. `__init__` now assigns through
  the property, so startup and runtime mutation share one rule and the inline
  `clamp_interval(...)` call in the constructor disappears.

- Because the runtime path mutates jobs with ordinary `setattr`, it inherits
  enforcement with no change of its own: no special-case branch in
  `apply_update`, no re-check in `control.py`, no new `set_poll_interval()`
  method that callers would have to remember to use. Every existing caller
  keeps reading and writing `job.poll_interval` with plain attribute syntax.

- Compatibility is verified, not assumed. `snapshot()` previously mirrored
  `vars(self)`, which would now leak `_poll_interval` into the status file
  and control-socket replies and drop the public key. The repair rewrites
  `snapshot()` as an explicit mapping emitting exactly the pre-change keys
  (`name`, `url`, `poll_interval`, `timeout`, `retries`, `enabled`,
  `consecutive_failures`), so the dashboard, `upmonctl`, and the status file
  see an identical shape. The existing snapshot-keys test stays green
  untouched, confirming the serialization contract survived.

- The change stops where the rule stops. `timeout`, `retries`, `enabled`,
  `url`, and `name` remain plain attributes: none of them has a demonstrated
  invariant yet, so none grows accessor machinery "for symmetry".

All existing tests pass without modification.
