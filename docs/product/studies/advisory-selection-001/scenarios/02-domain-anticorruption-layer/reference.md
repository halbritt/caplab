# Reference repair

One possible good repair, not the only one. What matters is where knowledge of
the MERC wire vocabulary ends up after the change, not the exact file names.

## Diagnosis

OrderDesk has its own meaningful vocabulary — `OrderStatus` with distinct
`FULFILLED`, `PARTIALLY_FULFILLED`, and `CANCELLED` states, unit quantities,
customer-facing carrier names. The MERC feed speaks a different language with
different semantics: per `docs/merc_feed_notes.md`, `stat_cd == "C"` means only
"the warehouse stopped working this record" — shipped complete, shipped short,
or cancelled, with `dispo` carrying the distinction. The codebase currently
interprets the raw wire fields directly, in multiple independent places:
`sync._status_from_feed` equates `C` with `FULFILLED`, `reports.summarize`
counts `C` as a completed line, `sync.apply_feed` copies `carrier_cd` raw onto
`Order.carrier`, and `notifications.CARRIER_NAMES` keeps a MERC code table to
undo that at render time. The short-ship bug is one visible consequence of that
scattered, wrong equation; the two interpretation sites can also drift apart.

## Repair

1. **One translation point at the boundary.** Add a module such as
   `orderdesk/warehouse_feed.py` whose job is to turn each raw MERC record into
   a value expressed in OrderDesk's own terms — e.g. a frozen `ShipmentLine`
   dataclass with `order_id`, `sku`, `quantity_ordered`, `quantity_shipped`, a
   local stage (waiting / picking / closed), and, for closed records, an
   explicit outcome (shipped in full / shipped short / cancelled) derived from
   `stat_cd` + `dispo` + the quantities. The carrier comes out already as the
   customer-facing name. Unrecognised `stat_cd` or `dispo` values fail loudly
   here rather than being guessed at downstream. All knowledge of MERC's codes
   lives in this module (plus the transport docstring in `merc_client.py`).

2. **Consumers speak only local vocabulary.** `apply_feed` keeps its signature
   (raw records in, store updated, notifiable orders out) but calls the
   translator first and then reasons over translated values: every line shipped
   in full → `FULFILLED` (completion email); closed with a shortfall →
   `PARTIALLY_FULFILLED` (partial-shipment email, not the completion email);
   every line cancelled → `CANCELLED`. `reports.summarize` also translates
   first and derives `completed_lines` from the translated outcome, keeping its
   existing keys (it may add short-shipped/cancelled counts). `notifications`
   drops `CARRIER_NAMES`; `Order.carrier` now already holds a display name.
   After the change, `stat_cd`, `dispo`, `qty_ord`, `qty_shp`, `carrier_cd`,
   and code letters like `SS`/`CX` appear nowhere in sync, reports,
   notifications, models, or store.

3. **Deliberately narrow.** Translate only the fields OrderDesk actually
   consumes. No general mirror of MERC's schema, no write-back path to MERC,
   no new intermediate schema both sides have to track. `upd_ts` stays unused.

The existing tests are untouched and stay green: they drive the entry points
with raw feed fixtures, which is exactly the boundary the translator now sits
behind.

## Outcome on the reported symptom

ORD-1042 (closed, 4 of 12, `dispo` `SS`) syncs to `partially_fulfilled`,
receives the partial-shipment email instead of the completion email, and the
nightly summary stops counting it as a completed line. ORD-1044's cancelled
record (`C`/`CX`, nothing shipped) likewise stops reading as a completed
shipment.
