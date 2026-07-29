"""Apply a MERC shipment feed to the order store."""

from __future__ import annotations

import sys
from collections import defaultdict

from . import merc_client, notifications
from .models import OrderStatus
from .store import OrderStore

DEFAULT_STORE = "data/orders.json"


def apply_feed(records, store) -> list:
    """Update orders from MERC shipment lines.

    Returns the orders whose status change warrants a customer email.
    """
    by_order = defaultdict(list)
    for rec in records:
        by_order[rec["ord_ref"]].append(rec)

    notify = []
    for order_id, recs in by_order.items():
        order = store.get(order_id)
        if order is None:
            continue  # the drop includes other sales channels' orders
        for rec in recs:
            line = order.line_for(rec["sku"])
            if line is not None:
                line.quantity_shipped = rec["qty_shp"]
        if recs[-1].get("carrier_cd"):
            order.carrier = recs[-1]["carrier_cd"]
        new_status = _status_from_feed(recs)
        if new_status is not None and new_status != order.status:
            order.status = new_status
            if new_status is OrderStatus.FULFILLED:
                notify.append(order)
    return notify


def _status_from_feed(recs) -> OrderStatus | None:
    codes = {rec["stat_cd"] for rec in recs}
    if codes == {"C"}:
        # MERC closes a record once the shipment is done.
        return OrderStatus.FULFILLED
    if "P" in codes:
        return OrderStatus.IN_PROGRESS
    if codes == {"O"}:
        return OrderStatus.OPEN
    return None


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: python3 -m orderdesk.sync FEED_FILE [STORE_FILE]")
        raise SystemExit(2)
    feed_path = argv[0]
    store_path = argv[1] if len(argv) > 1 else DEFAULT_STORE

    records = merc_client.fetch_feed(feed_path)
    store = OrderStore.load(store_path)
    notify = apply_feed(records, store)
    store.save(store_path)

    for order in store.all():
        print(f"{order.order_id}  {order.status.value}")
    for order in notify:
        email = notifications.email_for_transition(order)
        if email is not None:
            print(f"queued: {email.subject!r} -> {email.to}")


if __name__ == "__main__":
    main()
