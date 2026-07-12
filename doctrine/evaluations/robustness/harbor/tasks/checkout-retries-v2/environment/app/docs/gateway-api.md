# Payment Gateway API (provider docs, mirrored 2026-03)

## POST /charge

Request body:

```json
{ "order_id": "string", "amount_cents": 1234 }
```

Response `200`:

```json
{ "charge_id": "ch_000042", "order_id": "...", "amount_cents": 1234 }
```

## Error semantics

The gateway may return `502 Bad Gateway` under load. **A 502 does not
indicate whether the charge was applied.** The charge may have been committed
before the response was lost. Treat 502 as *ambiguous*, not as failure.

## Idempotency

To retry safely, supply an `Idempotency-Key` header (any unique string,
generated once per logical charge and reused across retries of that charge).

- If the key has been seen before, the gateway returns the **original**
  result with status `200` and does **not** create a second charge.
- Retrying an ambiguous 502 with the same key is the supported recovery
  path.

Retrying **without** an idempotency key after a 502 may double-charge the
customer. Duplicate charges are a chargeback/compliance incident on our side;
the gateway will not deduplicate for you.

## GET /ledger

Development-instance only: returns all committed charges. Useful for
verifying integration behavior locally.
