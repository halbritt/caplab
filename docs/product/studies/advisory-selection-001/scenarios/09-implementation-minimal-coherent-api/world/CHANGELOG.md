# Changelog

## 0.4.1
- Signature header renamed to `X-Hookline-Signature` (was `X-Hook-Signature`).

## 0.4.0
- Retry handling extracted from `DeliveryService` into `hookline.retry.RetryPolicy`.
- Added exponential backoff with a cap and optional jitter.

## 0.3.2
- Request timeout applied per attempt instead of per delivery.

## 0.3.0
- Payloads are HMAC-signed; subscribers verify before trusting a delivery.
