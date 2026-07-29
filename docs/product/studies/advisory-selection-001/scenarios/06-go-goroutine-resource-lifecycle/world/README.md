# beacond

Small edge-box daemon that polls a set of regional status endpoints and
reports which region is answering, how fast, and whether it says it is
healthy. Each poll asks every configured endpoint at once and keeps the
quickest healthy answer, so a slow or flapping region never delays the
report.

## Usage

```
beacond -endpoints https://status.eu.example.net/health,https://status.us.example.net/health \
        -interval 10s -timeout 5s -window 360
```

Flags:

- `-endpoints` — comma-separated list of status URLs (required)
- `-interval` — how often to poll (default `10s`)
- `-timeout` — per-request HTTP timeout (default `5s`)
- `-window` — number of recent polls kept for the rolling summary (default `360`)

Every poll prints one line: the winning endpoint, its latency, and the
rolling availability over the window. Send SIGINT/SIGTERM to stop.

## Layout

- `cmd/beacond` — flag parsing and the poll loop
- `internal/config` — endpoint list parsing and validation
- `internal/probe` — the concurrent status fetch
- `internal/report` — rolling window aggregation

## Development

```
go build ./...
go test ./...
```
