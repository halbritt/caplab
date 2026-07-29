# Nordvik Supply — Availability API (v2)

Vendored from the Nordvik developer portal on 2026-03-11 (portal revision
v2.2). The portal copy is authoritative; this file is kept for offline
reference.

## Base URLs

| environment | base URL |
|---|---|
| production | `https://api.nordviksupply.com/v2` |
| sandbox | `https://sandbox.api.nordviksupply.com/v2` |

The sandbox serves the same release as production (occasionally a few days
ahead of it) with synthetic data, no rate limits, and test API keys.

## Authentication and headers

- Every request must carry a valid key in the `X-Api-Key` header. Requests
  without one receive `401`.
- Every request must set `Accept: application/json`. Requests without an
  `Accept` header are currently served JSON as a courtesy; this behaviour is
  unspecified and may change in any release.

## GET /availability

Returns current availability for one warehouse, paginated.

Query parameters:

| name | required | notes |
|---|---|---|
| `warehouse` | yes | uppercase warehouse code, e.g. `OSL` |
| `page` | no | 1-based, defaults to `1` |

Unrecognised query parameters are rejected with `400`.

### Response body (200)

```json
{
  "items": [ ... ],
  "next_page": 2
}
```

- `next_page` — integer page number, or `null` on the last page. Always
  present.
- `items` — array of item objects:

| field | type | presence |
|---|---|---|
| `sku` | string | always |
| `quantity` | integer | always |
| `unit_price_cents` | integer | always |
| `warehouse` | string | always |
| `discount_pct` | number | optional — omitted when no discount applies |
| `restock_eta` | string, ISO date | optional — omitted when no inbound shipment is booked |

### Compatibility policy (v2)

Within the v2 lifetime:

- Fields may be **added** to item objects and to the top-level response
  object in any release, without notice and without a version bump. Clients
  must ignore fields they do not recognise.
- Optional fields are omitted (not `null`) when they do not apply.
- Documented fields are never removed or type-changed inside v2; that only
  happens with a new major version.
