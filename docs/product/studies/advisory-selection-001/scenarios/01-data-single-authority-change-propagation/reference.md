# Reference repair (one possible shape)

The root problem is in `catalog/service.py`: every mutation performs two
independent durable writes — one to the SQLite store, one to the on-disk
search index. In the threaded storefront, two concurrent edits can land in the
store in one order and in the index in the other; a crash or an index-save
failure between the two writes leaves the index permanently out of step. No
error surfaces, and the divergence survives restarts because both sides are
persistent. The nightly-workaround symptom in TASK.md is exactly this.

A repair that follows the doctrine makes the store the single ordering
authority for catalog facts and turns the index into a follower of the store's
own change stream, instead of a peer written independently.

Concretely:

1. **Atomic change capture.** `CatalogStore` gains an append-only table, e.g.
   `changes(seq INTEGER PRIMARY KEY AUTOINCREMENT, op TEXT, item_id TEXT,
   payload TEXT)`, written **in the same SQLite transaction** as the item row
   for every create/update/delete. A fact cannot land without its entry, and
   `seq` gives all edits one total order. `payload` carries the full new item
   state (empty for deletes), so entries are self-contained and the consumer
   never needs to re-read racing state. The store exposes `changes_since(seq)`.

2. **A projector with a durable cursor.** A small component (e.g.
   `catalog/projector.py`) owns all index mutation. It persists the last `seq`
   it applied (stored inside the index's JSON file), reads newer entries in
   `seq` order, applies each through the index's existing `upsert`/`remove`
   (both safe to re-apply), then advances the cursor. A crash between apply and
   advance merely re-applies a few entries with no ill effect.

3. **Service writes go through one authority only.** `create_item`,
   `update_item`, and `delete_item` no longer call `index.upsert`/`remove`.
   They write through the store (which captures the change atomically) and then
   pump the projector's `catch_up()`. Synchronous catch-up preserves
   read-your-writes, so the existing test suite stays green; the load-bearing
   property is that the index can only learn about edits from the store's
   ordered record of them, never from a second independent write.

4. **Recovery and rebuild collapse into one bootstrap path.** If the index
   file or its cursor is missing (or behind retained history), the projector
   notes the store's current max `seq`, indexes all items from a store
   snapshot, sets the cursor, and follows from there. `maintenance.
   rebuild_index` keeps its signature but becomes a thin wrapper over this
   bootstrap, so startup recovery and the operator command exercise the same
   code.

What this deliberately does **not** do: retry loops or try/except around the
old second write, reordering the two writes, compensating deletes, or a full
reindex after every edit. Those shrink the divergence window without removing
it — two independent writers still exist and can still disagree.
