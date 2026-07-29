from orderdesk.models import Order, OrderLine, OrderStatus
from orderdesk.store import OrderStore
from orderdesk.sync import apply_feed


def rec(**overrides):
    base = {
        "ord_ref": "ORD-9001",
        "sku": "KB-0100",
        "qty_ord": 3,
        "qty_shp": 0,
        "stat_cd": "O",
        "dispo": "",
        "carrier_cd": "",
        "upd_ts": "2026-07-27 09:15:00",
    }
    base.update(overrides)
    return base


def make_store():
    order = Order(
        order_id="ORD-9001",
        customer_email="pat@example.com",
        lines=[
            OrderLine(
                sku="KB-0100",
                description="Test switch pack",
                quantity_ordered=3,
            )
        ],
    )
    return order, OrderStore([order])


def test_open_record_keeps_order_open():
    order, store = make_store()
    result = apply_feed([rec()], store)
    assert order.status is OrderStatus.OPEN
    assert result == []


def test_picking_marks_in_progress():
    order, store = make_store()
    apply_feed([rec(stat_cd="P")], store)
    assert order.status is OrderStatus.IN_PROGRESS


def test_closed_complete_marks_fulfilled_and_notifies():
    order, store = make_store()
    result = apply_feed(
        [rec(stat_cd="C", qty_shp=3, dispo="OK", carrier_cd="UPS")], store
    )
    assert order.status is OrderStatus.FULFILLED
    assert order in result


def test_notification_only_on_transition():
    order, store = make_store()
    feed = [rec(stat_cd="C", qty_shp=3, dispo="OK")]
    first = apply_feed(feed, store)
    second = apply_feed(feed, store)
    assert order in first
    assert second == []


def test_line_quantities_updated():
    order, store = make_store()
    apply_feed([rec(stat_cd="P", qty_shp=2)], store)
    assert order.lines[0].quantity_shipped == 2


def test_unknown_orders_are_ignored():
    order, store = make_store()
    result = apply_feed([rec(ord_ref="WEB-0000", stat_cd="C", qty_shp=3, dispo="OK")], store)
    assert order.status is OrderStatus.OPEN
    assert result == []
