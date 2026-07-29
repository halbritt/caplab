# Reference repair

One good repair — not the only one — makes `Prober.Fastest`
(`internal/probe/probe.go`) accountable for everything it starts: each
goroutine it launches and each HTTP response those goroutines cause to
exist gets a definite terminator, on every path.

1. **Cancel the losers.** Derive a cancellable context at the top of
   `Fastest` — `raceCtx, cancel := context.WithCancel(ctx)` — and
   `defer cancel()`. Every return path (winner found, decode failure,
   all endpoints failed) now tears down whatever is still in flight
   instead of letting losing requests run to completion against a poll
   that has already moved on.

2. **Bind requests to that context.** Build each request with
   `http.NewRequestWithContext(raceCtx, http.MethodGet, ep, nil)` and
   `p.client.Do` instead of `p.client.Get`, so the cancel actually
   reaches the transport and aborts straggling dials and reads. This
   also finally honors the `ctx` parameter the function accepts and
   ignores today.

3. **Close what you open, where you open it.** Move body handling into
   the goroutine that obtained the response: immediately after `Do`
   succeeds, `defer resp.Body.Close()`; decode the small status
   document right there and send a decoded `Status` (or error) over the
   channel — never a live `*http.Response`. The opener then closes its
   body on success, on non-200 (previously never closed), on decode
   failure, and on cancellation alike; nothing downstream inherits an
   open body it can forget.

4. **Let abandoned senders finish.** Buffer the channel to
   `len(endpoints)` (or have each send `select` on `raceCtx.Done()`),
   so a goroutine whose answer is no longer wanted can still deliver
   and exit rather than blocking forever on an unbuffered send — the
   direct source of the per-poll goroutine and connection growth.

Caller-visible behavior is unchanged: the first healthy 200 wins, and
when every endpoint fails the per-endpoint errors are still joined into
one. Adding a `sync.WaitGroup` to make completion observable is a
reasonable extra but not required once sends cannot block and stragglers
are cancelled promptly. No test files change; `go build ./... &&
go test ./...` stays green.
