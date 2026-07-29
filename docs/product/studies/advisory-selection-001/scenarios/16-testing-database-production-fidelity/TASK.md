# Scan events vanish after being recorded

Operators report parcel scans disappearing. Recording one looks successful — it prints the new event id and exits zero:

```
python -m trackd register PKG-1042 --carrier orion --origin reno-dc
python -m trackd scan PKG-1042 in_transit "Reno sort hub"
python -m trackd status PKG-1042
```

Expected: status shows `in_transit`. Actual: the shipment still shows `registered`, and `history` prints nothing. Registrations persist fine; only scans are lost. No errors in the journal. It reproduces on the gateway and locally. Yet the whole test suite passes, scan tests included. Please figure out what is going on and make sure this cannot slip past us again.
