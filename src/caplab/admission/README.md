# Study evidence admission

This package implements only ADR 0014 Stage B / CAPLAB-24. It verifies the
exact Study 001 preservation manifest and three selected Git records, assigns
all 684 records the `restricted-admission` disposition, and links the 20
historical first attempts to their frozen assignments and mechanical outcomes.

`source-verify` performs no write. `admit` content-addresses unique bytes into
Garage and the independent `/nvr` copy, rebuilds the source inventory, verifies
both stores, then freezes one append-only PostgreSQL manifest. `verify` reads
that frozen manifest and reconciles both byte stores. The writer, reader, and
verifier role boundary is enforced by the CLI, PostgreSQL grants, Garage keys,
and filesystem permissions.

The command surface intentionally contains no result recomputation, provider,
model, inference, export, publication, training, purge, or acceptance action.
P7 and later checkpoints remain unavailable.
