# Webhook retries arrive as one instant burst

Yesterday a partner's webhook endpoint had an outage, and their rate limiter
banned our sender IP mid-incident. Their access logs show why: every delivery
attempt for an event landed within the same tenth of a second. The dispatcher
asks for five attempts with a couple of seconds between them, so the attempts
should have been spread out, not fired back-to-back.

To reproduce: point the dispatcher at any endpoint returning 503 and watch the
attempt timestamps arrive as one burst. Our own logs show nothing unusual — the
delivery just reports failed. Please make the sender behave the way the
dispatcher asks.
