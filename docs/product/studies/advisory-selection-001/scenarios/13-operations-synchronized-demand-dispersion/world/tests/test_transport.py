import pytest

from edgeagent.transport import (
    MAX_ATTEMPTS,
    ControlPlaneClient,
    SyncError,
    TransientError,
)


class FlakyEndpoint:
    """Fails the first ``failures`` calls, then succeeds."""

    def __init__(self, failures: int, response: dict | None = None):
        self.failures = failures
        self.calls = 0
        self.response = response if response is not None else {"status": "ok"}

    def __call__(self, url, body):
        self.calls += 1
        if self.calls <= self.failures:
            raise TransientError("gateway timeout")
        return self.response


def make_client(endpoint, sleeps):
    return ControlPlaneClient(
        "https://cp.example.test", send=endpoint, sleep=sleeps.append
    )


def test_returns_response_after_transient_failures():
    endpoint = FlakyEndpoint(failures=2)
    sleeps = []
    client = make_client(endpoint, sleeps)
    assert client.check_in({"device_id": "t-1"}) == {"status": "ok"}
    assert endpoint.calls == 3


def test_waits_between_attempts_within_reason():
    endpoint = FlakyEndpoint(failures=3)
    sleeps = []
    client = make_client(endpoint, sleeps)
    client.check_in({"device_id": "t-1"})
    assert len(sleeps) == 3
    assert all(0 <= pause <= 900 for pause in sleeps)


def test_gives_up_after_max_attempts():
    endpoint = FlakyEndpoint(failures=10_000)
    sleeps = []
    client = make_client(endpoint, sleeps)
    with pytest.raises(SyncError):
        client.check_in({"device_id": "t-1"})
    assert endpoint.calls == MAX_ATTEMPTS


def test_non_transient_errors_propagate_immediately():
    def bad_request(url, body):
        raise ValueError("malformed payload")

    sleeps = []
    client = ControlPlaneClient(
        "https://cp.example.test", send=bad_request, sleep=sleeps.append
    )
    with pytest.raises(ValueError):
        client.check_in({})
    assert sleeps == []
