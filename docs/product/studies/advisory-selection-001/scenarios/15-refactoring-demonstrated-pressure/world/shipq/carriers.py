"""Carrier metadata: service labels, tracking links, transit estimates.

TODO(jk, 2024-08): could collapse this dispatch into per-carrier classes.
"""


def service_label(carrier, service):
    if carrier == "DPX":
        if service == "std":
            return "DPX Ground"
        elif service == "exp":
            return "DPX Priority"
        elif service == "eco":
            return "DPX Saver"
        else:
            raise ValueError("unknown DPX service: %s" % service)
    elif carrier == "ARO":
        if service == "std":
            return "Aero Standard"
        elif service == "exp":
            return "Aero Express"
        elif service == "eco":
            return "Aero Economy"
        else:
            raise ValueError("unknown ARO service: %s" % service)
    else:
        raise ValueError("unknown carrier: %s" % carrier)


def tracking_url(carrier, tracking_no):
    if carrier == "DPX":
        # DPX references are digits only; strip the optional "DPX-" prefix.
        if tracking_no.startswith("DPX-"):
            tracking_no = tracking_no[4:]
        return "https://track.dpx.example/t/" + tracking_no
    elif carrier == "ARO":
        if tracking_no.startswith("AR"):
            return "https://aero.example/track?ref=%s" % tracking_no
        else:
            # pre-2023 references go through the legacy redirector
            return "https://aero.example/track?legacy=%s" % tracking_no
    else:
        raise ValueError("unknown carrier: %s" % carrier)


_DPX_TRANSIT = {
    ("std", 1): 2, ("std", 2): 3, ("std", 3): 5,
    ("exp", 1): 1, ("exp", 2): 1, ("exp", 3): 2,
    ("eco", 1): 4, ("eco", 2): 6, ("eco", 3): 8,
}

_ARO_TRANSIT = {
    ("std", 1): 3, ("std", 2): 4, ("std", 3): 6,
    ("exp", 1): 1, ("exp", 2): 2, ("exp", 3): 3,
    ("eco", 1): 5, ("eco", 2): 7, ("eco", 3): 9,
}


def transit_days(carrier, service, zone):
    if carrier == "DPX":
        if (service, zone) in _DPX_TRANSIT:
            days = _DPX_TRANSIT[(service, zone)]
            if service == "eco" and zone == 3:
                days = days + 2  # eco zone-3 routes through the weekend hub
            return days
        raise ValueError("no DPX transit entry for %s zone %s" % (service, zone))
    elif carrier == "ARO":
        if (service, zone) in _ARO_TRANSIT:
            return _ARO_TRANSIT[(service, zone)]
        raise ValueError("no ARO transit entry for %s zone %s" % (service, zone))
    else:
        raise ValueError("unknown carrier: %s" % carrier)


def pickup_cutoff_hour(carrier, service):
    # local depot cutoffs; confirmed with ops 2024-07
    if carrier == "DPX":
        if service == "exp":
            return 12
        return 17
    elif carrier == "ARO":
        if service == "exp":
            return 11
        elif service == "eco":
            return 15
        return 16
    else:
        raise ValueError("unknown carrier: %s" % carrier)
