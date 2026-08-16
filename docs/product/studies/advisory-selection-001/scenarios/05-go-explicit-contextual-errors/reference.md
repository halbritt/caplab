# Reference repair (one possible good repair, not the only one)

All the damage lives in `internal/syncer/syncer.go`, in `syncEntry`'s two
log-and-return-nil sites and in what they leave on disk. The rest of the
repository already shows the house convention — `manifest` and `store` add
operation context with `fmt.Errorf("...: %w", err)`, and `store` exports
`ErrNotFound` precisely so callers can test for it with `errors.Is`. A repair
that follows the doctrine brings the syncer up to that convention instead of
patching the one visible symptom.

**Copy failures propagate, once, with cause and context.** The
`io.Copy` failure path stops returning `nil`. It returns an error that says
which entry and operation failed and wraps the underlying error
(`fmt.Errorf("copy %s: %w", e.Name, err)`), so `errors.Is`/`errors.As` still
reach the root cause (e.g. `ENOSPC`). The `log.Printf` at that site is
deleted rather than kept alongside the return: the caller that owns the
decision — `main`, which already prints `Run`'s error and exits 1 — is the
single reporter. The failed entry is no longer counted as synced, and the run
exits non-zero. The bare `return err` sites (`os.MkdirAll`, `os.Create`) gain
the same contextual wrapping. An equally good variant collects per-entry
errors (e.g. `errors.Join`) and finishes the loop before failing, as long as
the run still returns a non-nil error.

**Open failures are classified, not blanket-skipped.** The comment at the
first swallow site records real intent — optional extras must not stop the
run — but the code discards *every* open error. The repair skips only when
`e.Optional && errors.Is(err, store.ErrNotFound)`, counting the entry as
skipped (not synced); any other open failure, including a missing *required*
object, propagates with entry context wrapping the cause. This keeps the
existing optional-entry test green while ending the misleading success for
required entries. Deciding by error identity — never by matching message
text — is what the store's sentinel exists for. (`syncEntry` can return a
small status alongside the error so `Run` counts skips correctly.)

**Failure leaves nothing that lies to the next run.** Today a failed copy
abandons a partial file at the final destination path, and the incremental
`os.Stat` check then treats the damaged file as done forever — that is why
re-runs never repair anything. The repair writes to a temporary name in the
destination directory and renames into place only after the copy *and* the
`Close` both succeed (a close error on the write path is a real write
failure and is checked, not discarded). On any failure the temp file is
closed and removed — e.g. via a deferred cleanup — so the entry's final path
stays absent and the next run retries it. Removing the file at the final
path on the error path is an acceptable alternative; deleting the
incremental skip so every run recopies everything is not.

The incremental-skip behaviour, the optional-entry semantics, and all three
existing test files are unchanged; `go build ./... && go test ./...` stays
green.
