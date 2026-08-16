# MERC shipment feed — field notes

Working notes on the distributor's MERC warehouse feed, collected from the
vendor integration sheet (rev 14) and two support calls. The vendor sheet
is terse; the clarifications below came from the calls.

## Fields

| field | meaning |
|---|---|
| `ord_ref` | order reference; matches our `order_id` |
| `sku` | item code, same catalogue as ours |
| `qty_ord` | units ordered |
| `qty_shp` | units shipped so far (cumulative) |
| `stat_cd` | record stage: `O`, `P`, `C` (see below) |
| `dispo` | disposition, set when a record is closed (see below) |
| `carrier_cd` | carrier code: `FDX`, `UPS`, `USPS`, `LTL` |
| `upd_ts` | last update, **warehouse local time (US/Central), not UTC** |

## `stat_cd`

`O` = open (not yet picked). `P` = picking/packing. `C` = closed.

**Closed means the warehouse has stopped working the record — for any
reason.** Confirmed on the 2026-06-19 support call: a record goes to `C`
when it ships complete, when it ships short and the remainder is written
off, and when it is cancelled after allocation. The `dispo` field says
which:

| `dispo` | set when |
|---|---|
| `OK` (empty on some older drops) | shipped complete |
| `SS` | short shipped — the remainder will **not** ship |
| `CX` | cancelled after allocation; anything picked was restocked |

## Quirks

- Records for orders from other sales channels appear in the same drop;
  `ord_ref`s we don't recognise should be skipped.
- The drop is a full snapshot, not a delta; a record keeps appearing in
  every file until the vendor archives it (roughly 30 days after close).
- `carrier_cd` is often blank until the first carton is manifested.
