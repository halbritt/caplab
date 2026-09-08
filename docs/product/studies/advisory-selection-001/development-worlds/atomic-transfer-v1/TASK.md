# Repair retry-safe account transfers

A local ledger moves integer units between accounts. A caller retries a request
after receiving an error or losing its response. The current implementation
sometimes leaves only one side of a transfer recorded or applies a retry twice.
Repair `transfer.py` while preserving the API and schema below.

Implement `transfer(connection, request_id, source, destination, amount)`.
The caller provides a SQLite connection in autocommit mode, with no transaction
already open. Accounts already exist. The schema is:

```sql
CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER NOT NULL);
CREATE TABLE transfers (
    request_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    amount INTEGER NOT NULL
);
```

The function returns `"applied"` for a new successful request and `"replayed"`
for an already recorded request with exactly the same source, destination and
amount. An exact retry makes no database change. A reused request ID with
different parameters raises `ValueError` and changes nothing.

Request ID, source and destination must be nonempty strings. Amount must be a
positive integer, excluding booleans. Source and destination must differ.
Invalid arguments, an unknown account or insufficient source balance raise
`ValueError` and change nothing. A fresh valid transfer subtracts exactly amount
from the source, adds exactly amount to the destination and inserts one matching
transfer record. All other accounts and existing transfer records are unchanged.

Every new transfer is atomic. If a SQLite statement fails **before that statement
executes**, propagate the SQLite error and leave the database as it was before
the call. Close any transaction opened by the function; the connection must
remain usable. The caller may retry with the same request ID after the failure.
That retry must either apply the transfer once or recognize an already committed
identical request. Never report success after a failed statement.

Independent connections to the same database may submit transfers concurrently.
Serialization must preserve these rules: simultaneous withdrawals cannot jointly
spend more than the available balance. Busy/locked errors may propagate as
SQLite errors with no partial transfer; the caller owns retries. Do not retry
indefinitely inside this function.

Assume initial balances are nonnegative integers and all balances/results fit
SQLite's signed 64-bit integer range. Other writers obey this API; external
processes do not alter the schema or delete accounts. Do not change the schema,
add dependencies, perform network operations or modify files outside this task.
The connection remains owned by the caller and must not be closed.

This task does not promise that an error reported after a successful commit
means no transfer occurred. Response loss after commit is handled by the
idempotent request ID. Power loss, disk corruption and SQLite durability settings
are outside this exercise's failure model.
