from hookline.retry import RetryPolicy


def test_delays_grow_exponentially():
    policy = RetryPolicy(max_attempts=4, backoff=0.5, multiplier=2.0)
    assert [policy.delay_before(n) for n in (2, 3, 4)] == [0.5, 1.0, 2.0]


def test_cap_limits_delay():
    policy = RetryPolicy(backoff=10.0, multiplier=3.0, cap=15.0)
    assert policy.delay_before(4) == 15.0


def test_jitter_stays_within_bound():
    policy = RetryPolicy(backoff=1.0, jitter=0.25)
    delay = policy.delay_before(2)
    assert 1.0 <= delay <= 1.25
