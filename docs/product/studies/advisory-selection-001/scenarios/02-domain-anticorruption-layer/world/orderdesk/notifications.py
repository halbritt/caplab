"""Customer-facing email templates."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Order, OrderStatus

# MERC carrier codes -> what we show customers
CARRIER_NAMES = {
    "FDX": "FedEx",
    "UPS": "UPS",
    "USPS": "USPS",
    "LTL": "pallet freight",
}


@dataclass
class Email:
    to: str
    subject: str
    body: str


def completion_email(order: Order) -> Email:
    carrier = CARRIER_NAMES.get(order.carrier or "", "our carrier")
    lines = "\n".join(
        f"  - {line.quantity_shipped} x {line.description}" for line in order.lines
    )
    return Email(
        to=order.customer_email,
        subject=f"Your order {order.order_id} is complete",
        body=(
            f"Good news — your order {order.order_id} has shipped in full via "
            f"{carrier}:\n{lines}\n\nThanks for shopping with KeebSupply."
        ),
    )


def partial_shipment_email(order: Order) -> Email:
    carrier = CARRIER_NAMES.get(order.carrier or "", "our carrier")
    shipped = "\n".join(
        f"  - {line.quantity_shipped} x {line.description}"
        for line in order.lines
        if line.quantity_shipped
    )
    outstanding = "\n".join(
        f"  - {line.outstanding} x {line.description}"
        for line in order.lines
        if line.outstanding
    )
    return Email(
        to=order.customer_email,
        subject=f"Part of your order {order.order_id} has shipped",
        body=(
            f"Part of your order {order.order_id} is on its way via {carrier}:\n"
            f"{shipped}\n\nStill outstanding:\n{outstanding}\n\n"
            "We'll be in touch about the rest."
        ),
    )


def email_for_transition(order: Order) -> Email | None:
    """The email to send when an order has just entered its current status."""
    if order.status is OrderStatus.FULFILLED:
        return completion_email(order)
    if order.status is OrderStatus.PARTIALLY_FULFILLED:
        return partial_shipment_email(order)
    return None
