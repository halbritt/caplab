from upmon.probe import ProbeJob
from upmon.scheduler import Scheduler


class FakeClock:
    def __init__(self, start=100.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def _make(names_intervals):
    return [
        ProbeJob(name, f"https://{name}.example/health", poll_interval=interval)
        for name, interval in names_intervals
    ]


def test_everything_due_on_first_pass():
    clock = FakeClock()
    ran_urls = []

    def prober(job):
        ran_urls.append(job.name)
        return True

    sched = Scheduler(_make([("edge", 30), ("db", 60)]), prober, clock=clock)
    assert sched.run_pending() == ["edge", "db"]
    assert ran_urls == ["edge", "db"]


def test_jobs_wait_out_their_interval():
    clock = FakeClock()
    sched = Scheduler(_make([("edge", 30)]), lambda job: True, clock=clock)
    sched.run_pending()
    clock.advance(10)
    assert sched.run_pending() == []
    clock.advance(25)
    assert sched.run_pending() == ["edge"]


def test_disabled_jobs_are_skipped():
    jobs = _make([("edge", 30)])
    jobs[0].enabled = False
    sched = Scheduler(jobs, lambda job: True, clock=FakeClock())
    assert sched.run_pending() == []


def test_failed_probes_feed_the_streak():
    jobs = _make([("edge", 30)])
    sched = Scheduler(jobs, lambda job: False, clock=FakeClock())
    sched.run_pending()
    assert jobs[0].consecutive_failures == 1
