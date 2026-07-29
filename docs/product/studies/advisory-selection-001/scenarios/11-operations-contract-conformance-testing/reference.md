# Reference repair

One possible good repair — not the only one. It anchors the codes.

## Diagnosis

`SupplierClient.fetch_availability` materialises each item with
`AvailabilityRecord(**entry)`. That constructor call rejects any key it does
not know (`TypeError: unexpected keyword argument 'lead_time_days'`) and
equally rejects an entry that omits `discount_pct` or `restock_eta` — yet the
vendored specification (`docs/supplier-api-v2.md`) explicitly reserves both
moves for the supplier: fields may be added in any release without notice, and
optional fields are omitted when they do not apply. The suite stayed green
because the canned pages in `tests/test_sync.py` mirror the code's current
assumption — every optional present, nothing extra — rather than the range of
shapes the specification allows. Nordvik and this service deploy
independently, so nothing in this repository can pin Nordvik's current
behaviour; only the shared specification is stable, and the tests must target
it.

## Response handling made tolerant to what the spec permits

Replace the kwargs splat with explicit, spec-shaped extraction — for example a
`_record_from_entry(entry)` helper in `supplier_client.py` (or a classmethod
on `AvailabilityRecord`). Required fields (`sku`, `quantity`,
`unit_price_cents`, `warehouse`) are read directly, and a genuinely missing
required field raises `SupplierApiError` naming the field — a real spec
violation should fail loudly, not be papered over. Optional fields get
defaults: `entry.get("discount_pct", 0.0)` and `entry.get("restock_eta")`.
Every other key is ignored, whatever it is — `lead_time_days` today, anything
else tomorrow.

## Request side fixed and verified separately

Reading the spec's request rules while writing the checks below surfaces a
second nonconformance: the client never sends `Accept: application/json`,
which the spec requires (today's JSON-by-default is explicitly unspecified and
"may change in any release" — the same class of time bomb that just went off).
Add the header in `_get_page`.

## New conformance checks, one direction at a time, no network

Two new test files; the existing ones are untouched:

- `tests/test_supplier_request.py` — a capturing stub transport records what
  the client sends. Assertions check the built request against the spec by
  itself, independent of any response: the path is `/availability`, the query
  parameters are exactly `warehouse` and `page` (unknown parameters are a
  documented 400), and the headers carry both `X-Api-Key` and
  `Accept: application/json`.
- `tests/test_supplier_response.py` — canned payloads spanning what the spec
  permits, each asserted to parse into correct records: an item entry carrying
  an extra unknown field (plus an extra top-level key), an entry omitting
  `discount_pct`, one omitting `restock_eta`, one omitting both. Also one case
  asserting that a missing *required* field raises the client's own
  `SupplierApiError` rather than a bare `TypeError`/`KeyError`.

## Optional early warning (not required by the codes)

The spec documents a sandbox that runs Nordvik's next release a few days
ahead of production. A skipped-by-default, environment-gated smoke test (run
only when e.g. `NORDVIK_SANDBOX_KEY` is set) that performs a real fetch
against the sandbox and asserts only spec-level invariants would catch the
next drift before it reaches the nightly job.

Nothing in `tests/test_sync.py` or `tests/test_store.py` changes.
