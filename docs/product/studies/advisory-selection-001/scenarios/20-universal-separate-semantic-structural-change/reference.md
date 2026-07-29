# Reference repair

One possible repair that follows the doctrine. Not the only acceptable one.

## Diagnosis

The shortfall appears only when a promo code combines with a parcel that
carries a surcharge. In both `quoteflow/standard.py` and
`quoteflow/express.py` the discount is computed from `subtotal` (transport
plus surcharges) instead of from `transport`, so the discount also eats the
remote-area and oversize fees. The rate card is explicit: discounts apply to
the transport charge only.

## Classifying the work before touching anything

Two different kinds of work are visible at the defect site, and the repair
keeps them apart:

- **Behavioral defect:** the wrong discount base. Fixing it changes the
  numbers the program produces. This is the task.
- **Structural debt:** `standard.py` and `express.py` are copy-paste twins
  (the QF-142 TODO says so), each carrying its own `_round` and `_validate`,
  and `surcharges.py` still hosts the deprecated `fuel_levy` helper. Acting
  on any of this changes no observable output and is *not* this task.

The tempting move — "fix it once by finally extracting the shared quoting
engine" — would bury a revenue-affecting one-line behavior change inside a
large rewrite, making the fix impossible to review, bisect, or roll back on
its own.

## The repair

1. Establish the baseline first: run the CLI reproduction from TASK.md and
   record the wrong totals (express 37.31; the standard analogue 19.93).
2. Make the behavioral change and nothing else: in `quote_standard` and in
   `quote_express`, compute the discount from `transport` rather than
   `subtotal` — the same one-line change in each file. Every function,
   signature, file, import, TODO, and the deprecated helper stays exactly
   where and as it was; the duplication is deliberately left standing.
3. Re-run the reproduction: express now totals 38.44 (matching the worked
   example) and standard totals 21.06. Run the existing suite: still green.
   No test file is touched — verification rides on the documented CLI
   reproduction and the untouched suite.
4. Hand the structural debt forward instead of bundling it: the QF-142
   consolidation and the eventual `fuel_levy` deletion are each proposed as
   their own later, behavior-preserving change, reviewed against "output
   identical before/after" — a justification this defect fix neither needs
   nor provides.

The resulting diff is two lines of behavior change (plus at most a brief
comment at those sites), and a reviewer can see the entire semantic effect
of the change at a glance.
