# upmon

A deliberately small HTTP endpoint monitor. One process, one thread, no
dependencies outside the standard library.

- `upmon/probe.py` — the `ProbeJob` model: endpoint, schedule, failure streak.
- `upmon/scheduler.py` — cooperative loop that runs due probes.
- `upmon/prober.py` — the blocking HTTP GET.
- `upmon/runtime.py` + `upmon/control.py` — live updates: `upmonctl` sends
  JSON command lines over the control socket and settings change without a
  restart. The socket transport itself lives in the deployment wrapper; all
  command behavior is in-tree and testable.
- `upmon/status.py` — atomic status-file writer; the dashboard reads this.
- `upmon/config.py` — JSON config loading and operating limits.

Run:

```
python -m upmon /etc/upmon/config.json
```

Test:

```
python -m pytest -q
```

Probe intervals are kept within the supported operating band (5–3600
seconds). The floor exists because probing shared infrastructure faster than
that has triggered upstream rate-limit bans before (INC-2081).
