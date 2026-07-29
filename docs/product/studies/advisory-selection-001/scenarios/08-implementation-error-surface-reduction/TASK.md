# Nightly import says success while transactions go missing

Our nightly ledger import keeps finishing cleanly while transactions are missing. Last night it printed "Imported 214 transactions from 3 files" and exited 0, yet the Coastal account's rows were entirely absent. Nothing in the output pointed at that file; re-running doesn't help.

To reproduce: put an export saved in the bank's older Windows encoding (not UTF-8) into the incoming folder beside normal exports, then run `python -m ledgerline.cli <incoming-dir>`.

Expected: those rows import, or the run tells us it couldn't use that file. Actual: the usual success message, exit 0, rows gone. Counts also drifted on some nights when every file opened fine.
