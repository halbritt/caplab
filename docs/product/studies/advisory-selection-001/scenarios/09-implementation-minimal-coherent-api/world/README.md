# hookline

Outbound webhook delivery for internal services. Signs each payload,
POSTs it to the subscriber's endpoint, and retries transient failures.

## Usage

```python
from hookline.delivery import DeliveryService
from hookline.events import Event
from hookline.transport import HttpTransport

service = DeliveryService(HttpTransport(), signing_secret=b"...")
event = Event(kind="invoice.paid", data={"invoice": "inv_042"})
service.send(event, "https://partner.example/hooks", backoff=2.0, max_attempts=5)
```

Delivery options are passed as keyword arguments on `send`.

## Layout

- `hookline/` — the library (delivery, retry, signing, transport, events)
- `app/` — the outbox dispatcher that production runs on a timer
- `scripts/` — operator tooling (`python -m scripts.replay` re-sends one event)
- `tests/` — pytest suite
