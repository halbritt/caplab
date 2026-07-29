from meterd.assignment import shard_of


def test_shard_of_is_stable():
    assert shard_of("acme", 8) == shard_of("acme", 8)
    assert shard_of("globex", 8) == shard_of("globex", 8)


def test_shard_of_in_range():
    for name in ["acme", "globex", "initech", "umbrella", "stark-labs", "wayne"]:
        assert 0 <= shard_of(name, 8) < 8


def test_shard_of_spreads_customers():
    shards = {shard_of(f"customer-{i}", 8) for i in range(200)}
    assert shards == set(range(8))
