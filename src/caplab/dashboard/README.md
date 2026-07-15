# Study-results dashboard

This package serves sanitized, checked-in CAPLAB study projections for local
review. It has no mutation endpoint and does not read PostgreSQL, Garage,
`/nvr`, or historical attempt storage. The server validates every projection
at startup and fails closed on schema drift, non-canonical JSON, prohibited
private content, or inconsistent aggregate counts.

Study 001's projection was imported from `halbritt/books` commit
`e4636d2628adbbfca953734d4dc7cdfa91d72b04`. Its source binding is recorded in
`docs/manifests/dashboard-study-001-source.json`. The historical source files
were not admitted or copied into CAPLAB, so the old source-reading projector is
not part of this package. CAPLAB-native admission and recomputation remain P6
and P7 work.

Run locally from the repository root:

```bash
PYTHONPATH=src python3 -m caplab.dashboard.server \
  --bind 127.0.0.1 \
  --port 3021
```

Only `GET` and `HEAD` are allowed. The listener accepts literal loopback
addresses only.
