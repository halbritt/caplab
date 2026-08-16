# Reference repair

One possible repair that follows the doctrine — not the only acceptable one.
The codes anchor to the properties exhibited here, not to these exact names.

## Why not just patch the arithmetic

The wrong figures come from about fifteen lines buried in
`generate_statements()` in `meterflow/statement.py` — a 150-line function that
also loads the tariff, parses the vendor export, handles meter rollover,
applies the plan discount and fuel surcharge, renders regulator-approved
wording, writes the statement files and summary, and updates module state the
ops dashboard scrapes. The only existing coverage is `test_smoke.py`, which
never crosses the third rate step. There is no way to call the charge
computation on its own, so nothing protects the other behaviors (rollover,
zero usage, ebill discount, statement layout, summary format) while that
function is being changed.

## Step 1 — pin the outside first

Before touching `statement.py`, add a new `characterization/` directory (a new
top-level directory; no `tests/` directory is created and `test_smoke.py` is
not touched) holding a broad black-box suite that drives the generator through
its real entry point — `python -m meterflow.cli` via subprocess, or
`generate_statements()` directly — on its own small fixture tariff and
readings files. Every run writes only into pytest-provided temp directories
and passes an explicit statement date (`--as-of` / `as_of=`), so the suite is
reproducible on any day and machine and leaves nothing behind in the repo. It
captures full statement text and totals for the paths that matter: usage
inside the first step, usage exactly at a cap, two-step usage, the reported
above-250 case, an ebill-discount account, a zero-usage account, and a meter
rollover. Initially the above-250 expectation pins the current *wrong* output
— at this stage the suite records what the code does today, not what it
should do.

## Step 2 — label the suite as temporary scaffolding

A `characterization/README.md` (or module docstring) states plainly: these
whole-run checks exist to make the current rework of `statement.py` safe to
attempt; they are slow, sensitive to cosmetic layout changes, and bad at
pointing to a culprit when they fail; once the billing rules have direct
fast tests, delete them — keeping only the one or two that pin the statement
file format that ops tooling and the regulator wording depend on.

## Step 3 — cut the first seam under the net

With the broad suite green, move the charge computation — tier blocks,
energy, discount, surcharge, tax, total — out of `generate_statements()` into
a new `meterflow/billing.py` as a pure function (tariff dict, usage, plan in;
line items and totals out; no file or console I/O). `generate_statements()`
delegates to it. The broad suite still passes byte-for-byte, defect included:
the restructuring changed no behavior.

## Step 4 — fix narrowly, update exactly one pin

Correct the block quantity in `billing.py`: a fully-crossed middle tier bills
`cap - previous_cap` kWh, not `cap`. Add `test_billing.py` at the repo root
(alongside `test_smoke.py`; still no `tests/` directory) with fast in-memory
cases: usage at each boundary, multi-tier usage such as 312 kWh, discount
rounding, rollover usage, zero usage. Then update the single characterization
expectation this fix consciously changes — the above-250 statement, now
$63.42 with rate lines summing to 312 kWh. Every other pinned output is
unchanged, which is the evidence that the fix's blast radius was confined.

## Step 5 — retire on the stated schedule

Apply (or restate in the README) the retirement rule from step 2: with
`test_billing.py` covering the rules directly, the broad suite shrinks to the
statement-format check(s) that have lasting contract value; the rest is
deleted rather than maintained forever.
