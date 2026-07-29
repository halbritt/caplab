# Statement total doesn't match the raw export

Finance flagged customer C042's June statement. The raw June export
(`data/june_events.jsonl`) sums to exactly 10000.0 units for C042, but the
generated statement reports 10240.0 units and bills accordingly:

    python3 -m meterflow statement data/june_events.jsonl --customer C042 --month 2026-06

Expected: the statement's total units equal the sum of C042's quantities in
the file. Actual: it comes out 240.0 units high. Customer C017 in the same
file reconciles exactly. Support says a handful of other accounts have also
billed high on recent statements by varying amounts, while most reconcile to
the unit. Please work out what is going on and fix it.
