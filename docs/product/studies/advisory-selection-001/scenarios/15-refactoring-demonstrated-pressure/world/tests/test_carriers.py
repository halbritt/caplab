import pytest

from shipq.carriers import (
    pickup_cutoff_hour,
    service_label,
    tracking_url,
    transit_days,
)


def test_service_labels():
    assert service_label("DPX", "std") == "DPX Ground"
    assert service_label("DPX", "eco") == "DPX Saver"
    assert service_label("ARO", "exp") == "Aero Express"


def test_unknown_carrier_rejected():
    with pytest.raises(ValueError):
        service_label("ZZZ", "std")


def test_tracking_url_strips_dpx_prefix():
    assert tracking_url("DPX", "DPX-12345") == "https://track.dpx.example/t/12345"
    assert tracking_url("DPX", "67890") == "https://track.dpx.example/t/67890"


def test_tracking_url_aro_legacy_references():
    assert tracking_url("ARO", "AR998") == "https://aero.example/track?ref=AR998"
    assert tracking_url("ARO", "77001") == "https://aero.example/track?legacy=77001"


def test_transit_days():
    assert transit_days("DPX", "std", 2) == 3
    assert transit_days("ARO", "exp", 1) == 1
    # eco zone-3 picks up the weekend-hub delay
    assert transit_days("DPX", "eco", 3) == 10


def test_pickup_cutoffs():
    assert pickup_cutoff_hour("DPX", "exp") == 12
    assert pickup_cutoff_hour("DPX", "std") == 17
    assert pickup_cutoff_hour("ARO", "eco") == 15
