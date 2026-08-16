import pytest

from hookline.delivery import DeliveryError, DeliveryService
from hookline.events import Event
from hookline.signing import verify_signature
from hookline.transport import Response

SECRET = b"test-secret"


class ScriptedTransport:
    """Returns queued responses in order; records every call."""

    def __init__(self, statuses):
        self._statuses = list(statuses)
        self.calls = []

    def post(self, url, body, headers, timeout):
        self.calls.append(
            {"url": url, "body": body, "headers": headers, "timeout": timeout}
        )
        return Response(self._statuses.pop(0))


def make_service(transport):
    return DeliveryService(transport, signing_secret=SECRET, sleep=lambda s: None)


def make_event():
    return Event(kind="invoice.paid", data={"invoice": "inv_042", "amount_cents": 1250})


def test_successful_delivery_posts_once_and_signs_body():
    transport = ScriptedTransport([200])
    response = make_service(transport).send(make_event(), "https://partner.example/hooks")
    assert response.status == 200
    assert len(transport.calls) == 1
    call = transport.calls[0]
    assert call["headers"]["X-Hookline-Event"] == "invoice.paid"
    assert verify_signature(SECRET, call["body"], call["headers"]["X-Hookline-Signature"])


def test_server_errors_are_retried_until_success():
    transport = ScriptedTransport([503, 503, 200])
    response = make_service(transport).send(make_event(), "https://partner.example/hooks")
    assert response.status == 200
    assert len(transport.calls) == 3


def test_gives_up_after_default_attempts():
    transport = ScriptedTransport([503] * 5)
    with pytest.raises(DeliveryError) as excinfo:
        make_service(transport).send(make_event(), "https://partner.example/hooks")
    assert len(transport.calls) == 5
    assert excinfo.value.last_status == 503


def test_client_errors_are_not_retried():
    transport = ScriptedTransport([404])
    response = make_service(transport).send(make_event(), "https://partner.example/hooks")
    assert response.status == 404
    assert len(transport.calls) == 1


def test_max_attempts_can_be_lowered():
    transport = ScriptedTransport([503] * 2)
    with pytest.raises(DeliveryError):
        make_service(transport).send(
            make_event(), "https://partner.example/hooks", max_attempts=2
        )
    assert len(transport.calls) == 2
