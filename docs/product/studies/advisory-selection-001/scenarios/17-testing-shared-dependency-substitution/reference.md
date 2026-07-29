# Reference repair

One possible repair that follows the doctrine — not the only one.

The repair begins by classifying what each test actually depends on. The
`SqliteStore` handed out by the `store` fixture in `ledgerlib/testing.py` is
built once per session, so every test writes into the same database and every
later test can see those writes: it is the single dependency the tests
*share*, and it is the sole channel through which `test_reports.py` run first
can change what `test_march_statement_lists_every_posting` observes. Every
other dependency is private and in-process: `Ledger` and `CategoryRules` are
collaborators constructed fresh from the fixture, `ReportBuilder` is built
inside each test, and `Money`, `Posting`, and `Statement` are immutable
values.

The repair substitutes only the shared piece. In `ledgerlib/testing.py`, the
`store` fixture loses its `scope="session"` and instead builds a fresh,
freshly-migrated `SqliteStore` per test — a file under the per-test `tmp_path`
or an in-memory database, either is fine. Creating and migrating a SQLite
schema takes milliseconds, so the comment's original speed rationale does not
survive contact with measurement. The `ledger` fixture is left alone: it still
wires a real `Ledger` with real `CategoryRules` onto that store. No mock,
stub, or monkeypatch is introduced for `Ledger`, `ReportBuilder`, the policy,
or the value types — the tests keep exercising the real object graph
end-to-end, so a real defect in any collaborator still fails the suite.

Nothing under `tests/` changes. The assertion in
`test_march_statement_lists_every_posting` was correct all along — a monthly
statement over data the test wholly owns should list exactly its three
postings; it only looked wrong because other tests' writes leaked in. After
the change, any subset, ordering, repetition, or parallelisation of the test
files passes, including the reported
`python3 -m pytest tests/test_reports.py tests/test_ledger.py`.

What this repair deliberately does not do: keep the session-wide store and
manage the sharing (truncating tables between tests, per-test id prefixes,
pinning execution order); edit or scope down the failing assertion; or swap
the store — or any in-process collaborator — for a `MagicMock` whose canned
answers would hide real defects.
