"""Manually re-send one failed delivery.

Usage: python -m scripts.replay <url> <kind> <json-data>
"""

from __future__ import annotations

import json
import os
import sys

from hookline.delivery import DeliveryService
from hookline.events import Event
from hookline.transport import HttpTransport


def main(argv: list[str]) -> None:
    url, kind, raw = argv[1], argv[2], argv[3]
    secret = os.environ.get("HOOKLINE_SECRET", "").encode()
    service = DeliveryService(HttpTransport(), signing_secret=secret)
    event = Event(kind=kind, data=json.loads(raw))
    response = service.send(event, url, max_attempts=3, backoff=0.5)
    print(f"delivered {event.id}: status {response.status}")


if __name__ == "__main__":
    main(sys.argv)
