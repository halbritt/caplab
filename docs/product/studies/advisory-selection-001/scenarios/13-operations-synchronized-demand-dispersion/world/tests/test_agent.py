from edgeagent.agent import EdgeAgent
from edgeagent.config import AgentConfig
from edgeagent.transport import ControlPlaneClient, TransientError, MAX_ATTEMPTS


class FakeClock:
    def __init__(self, start: float = 1_700_000_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class RecordingEndpoint:
    def __init__(self):
        self.payloads = []

    def __call__(self, url, body):
        self.payloads.append(body)
        return {"status": "ok"}


def make_agent(interval: float = 600.0):
    clock = FakeClock()
    endpoint = RecordingEndpoint()
    waits = []

    def fake_sleep(seconds):
        waits.append(seconds)
        clock.advance(seconds)

    config = AgentConfig(
        device_id="t-42",
        control_plane_url="https://cp.example.test",
        sync_interval_seconds=interval,
    )
    client = ControlPlaneClient(
        config.control_plane_url, send=endpoint, sleep=fake_sleep
    )
    agent = EdgeAgent(config, client, clock=clock, sleep=fake_sleep)
    return agent, endpoint, waits, clock


def test_agent_checks_in_once_per_cycle():
    agent, endpoint, waits, clock = make_agent()
    agent.start(max_cycles=3)
    assert len(endpoint.payloads) == 3
    assert all(p["device_id"] == "t-42" for p in endpoint.payloads)


def test_waits_stay_within_the_interval_budget():
    agent, endpoint, waits, clock = make_agent(interval=600.0)
    agent.start(max_cycles=4)
    assert waits, "agent should pause between check-ins"
    assert all(0 <= pause <= 1200.0 for pause in waits)


def test_sent_timestamps_increase_across_cycles():
    agent, endpoint, waits, clock = make_agent(interval=600.0)
    agent.start(max_cycles=3)
    sent = [p["sent_at"] for p in endpoint.payloads]
    assert sent == sorted(sent)
    assert sent[0] < sent[-1]


def test_telemetry_ships_with_the_check_in():
    agent, endpoint, waits, clock = make_agent()
    agent.telemetry.record({"kind": "card_read", "ok": True})
    agent.telemetry.record({"kind": "printer_fault", "code": 17})
    agent.start(max_cycles=1)
    assert endpoint.payloads[0]["telemetry"] == [
        {"kind": "card_read", "ok": True},
        {"kind": "printer_fault", "code": 17},
    ]
    assert len(agent.telemetry) == 0


def test_failed_check_in_does_not_stop_the_loop():
    clock = FakeClock()
    waits = []

    def fake_sleep(seconds):
        waits.append(seconds)
        clock.advance(seconds)

    calls = {"count": 0}

    def unavailable(url, body):
        calls["count"] += 1
        raise TransientError("upstream unavailable")

    config = AgentConfig(
        device_id="t-7", control_plane_url="https://cp.example.test"
    )
    client = ControlPlaneClient(
        config.control_plane_url, send=unavailable, sleep=fake_sleep
    )
    agent = EdgeAgent(config, client, clock=clock, sleep=fake_sleep)
    agent.telemetry.record({"kind": "reboot"})
    agent.start(max_cycles=2)
    assert calls["count"] == 2 * MAX_ATTEMPTS
    assert agent.last_response is None
    # The unshipped event is still buffered for a later attempt.
    assert len(agent.telemetry) == 1
