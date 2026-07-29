# Interval floor ignored on live update

Overnight an operator slowed the "checkout-api" probe via `upmonctl` but
typed `0.5` instead of `50`. The probe began hitting the endpoint twice a
second until we restarted upmon forty minutes later; the target's WAF
rate-banned us.

Docs say intervals stay between 5 and 3600 seconds, and startup honors that —
`0.5` in the config file comes up as `5`. The same value sent as a live
update takes effect as-is.

Reproduce: send a live update setting `poll_interval` to `0.5`; the scheduler
fires that probe continuously. Expected: the value is pulled into the
documented range, as at startup. Actual: it applies as-is until restart.
