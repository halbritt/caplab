from app.dispatcher import Outbox, flush
from hookline.delivery import DeliveryError
from hookline.events import Event


class RecordingService:
    def __init__(self, fail_urls=()):
        self.sent = []
        self._fail_urls = set(fail_urls)

    def send(self, event, url, **_options):
        if url in self._fail_urls:
            raise DeliveryError(url, 5, 503)
        self.sent.append(event.id)


def test_flush_sends_all_pending_entries():
    outbox = Outbox()
    first = Event(kind="invoice.paid", data={})
    second = Event(kind="invoice.voided", data={})
    outbox.add(first, "https://one.example/hook")
    outbox.add(second, "https://two.example/hook")
    service = RecordingService()
    assert flush(outbox, service) == 2
    assert service.sent == [first.id, second.id]
    assert outbox.pending() == []


def test_failed_entries_are_parked_not_retried_forever():
    outbox = Outbox()
    outbox.add(Event(kind="invoice.paid", data={}), "https://down.example/hook")
    service = RecordingService(fail_urls={"https://down.example/hook"})
    assert flush(outbox, service) == 0
    assert outbox.pending() == []
