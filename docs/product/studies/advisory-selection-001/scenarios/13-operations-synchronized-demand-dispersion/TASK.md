# Control plane tips over on the ten-minute marks

Since the terminal fleet passed four thousand devices, the control-plane API
falls over briefly every ten minutes, exactly at :00, :10, :20. The gateway
shows a burst of check-in requests landing in the same second, then a few
seconds of 503s and timeouts, then near-idle until the next mark. Errors drag
on after each burst, and last Tuesday's fleet-wide power cycle left the API
unreachable for four minutes. Reproduce: watch the gateway across any
ten-minute boundary, or power-cycle a rack. Expected: average traffic is
tiny, so the API should stay responsive. Actual: brief outages every ten
minutes, worse after restarts.
