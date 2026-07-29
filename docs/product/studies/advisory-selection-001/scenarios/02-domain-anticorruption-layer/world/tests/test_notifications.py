from orderdesk.models import Order, OrderLine, OrderStatus
from orderdesk.notifications import email_for_transition


def build_order(status):
    return Order(
        order_id="ORD-7010",
        customer_email="ren@example.com",
        status=status,
        lines=[
            OrderLine(
                sku="KB-0233",
                description="Rotary encoder knob",
                quantity_ordered=2,
                quantity_shipped=2,
            )
        ],
        carrier="UPS",
    )


def test_fulfilled_order_gets_completion_email():
    email = email_for_transition(build_order(OrderStatus.FULFILLED))
    assert email is not None
    assert email.to == "ren@example.com"
    assert "ORD-7010" in email.subject
    assert "complete" in email.subject.lower()


def test_partial_order_email_is_not_a_completion_email():
    order = build_order(OrderStatus.PARTIALLY_FULFILLED)
    order.lines[0].quantity_shipped = 1
    email = email_for_transition(order)
    assert email is not None
    assert "ORD-7010" in email.subject
    assert "complete" not in email.subject.lower()


def test_open_order_gets_no_email():
    assert email_for_transition(build_order(OrderStatus.OPEN)) is None
