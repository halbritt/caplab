import pytest

from edgeagent.telemetry import TelemetryBuffer


def test_take_batch_returns_oldest_first_and_removes_them():
    buffer = TelemetryBuffer(batch_size=2)
    buffer.record({"seq": 1})
    buffer.record({"seq": 2})
    buffer.record({"seq": 3})
    assert buffer.take_batch() == [{"seq": 1}, {"seq": 2}]
    assert len(buffer) == 1


def test_requeue_puts_events_back_at_the_front():
    buffer = TelemetryBuffer(batch_size=2)
    buffer.record({"seq": 1})
    buffer.record({"seq": 2})
    batch = buffer.take_batch()
    buffer.record({"seq": 3})
    buffer.requeue(batch)
    assert buffer.take_batch() == [{"seq": 1}, {"seq": 2}]


def test_capacity_drops_oldest_and_counts_them():
    buffer = TelemetryBuffer(batch_size=10, max_events=3)
    for seq in range(5):
        buffer.record({"seq": seq})
    assert buffer.dropped == 2
    assert buffer.take_batch() == [{"seq": 2}, {"seq": 3}, {"seq": 4}]


def test_batch_size_must_be_at_least_one():
    with pytest.raises(ValueError):
        TelemetryBuffer(batch_size=0)
