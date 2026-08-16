from meterflow.pricing import cost_for_units


def test_first_tier_only():
    assert cost_for_units(500.0) == 60.0  # 500 * 0.12


def test_spans_all_tiers():
    # 1000 * 0.12 + 4000 * 0.10 + 5000 * 0.08 = 120 + 400 + 400
    assert cost_for_units(10000.0) == 920.0


def test_exact_tier_ceiling():
    assert cost_for_units(1000.0) == 120.0


def test_zero_units_zero_cost():
    assert cost_for_units(0.0) == 0.0
