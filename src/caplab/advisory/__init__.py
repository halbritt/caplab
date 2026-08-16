"""CAPLAB advisory scored claims.

This package is the advisory measurement track created by the
advisory-selection-001 plan of record. It scores review-family constructs
from matched-pair defect-injection evidence and emits **scored advisory
claims** for consumption by the quartermaster registry.

Boundary: everything here is advisory. It is deliberately outside
`caplab.qualification` — it produces no Measurement, no qualification Claim,
and no qualified/unqualified decision, and its export is a separate document
kind (`caplab-advisory-export/1`) so no consumer can mistake a scored
advisory claim for governed qualification evidence. Custody provenance is
explicit on every claim: `historical-seed` for evidence admitted from the
striatum-tuner 2026-08 sweep, `caplab-advisory` for CAPLAB-directed
advisory-grade executions.
"""
