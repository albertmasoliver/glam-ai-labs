# Triage of the subagent's report

5 findings, split out of `report.txt`. Mark every one, and say why. A finding you
did not triage is a finding you did not verify, and verification is the cost
that delegating does not remove.

## Finding 1

> `invoicing/totals.py::apply_discount` has no test anywhere. It mutates
> `line.unit_price_cents` in place (`invoicing/totals.py:33`), so a caller that
> applies the same discount twice compounds it silently.

**Verdict:** accept

**Because:** both halves check out -- `grep -rn apply_discount` finds one
definition and no caller in `tests/`, and the loop really does assign back onto
the line. This is the one to write first.

## Finding 2

> `tax_summary` keeps exempt lines in a separate bucket from zero-rated ones
> (`invoicing/totals.py:10`), and nothing asserts it. `tests/test_totals.py`
> covers only the `S` and `SR` codes.

**Verdict:** accept

**Because:** `rates.py` says in its own docstring that exempt is not zero-rated
and that callers who look only at the number get it wrong, and the two tests in
`tests/test_totals.py` never construct an `E` or a `Z` line.

## Finding 3

> `invoicing/totals.py` never looks at `invoice.currency`, so a JPY invoice is
> reported a hundred times too large. There is no test for a non-EUR invoice.

**Verdict:** reject

**Because:** the first sentence is true and the conclusion drawn from it is not.
`totals()` is supposed to stay in minor units -- `service.render()` divides by
`10 ** minor_units(invoice.currency)` at `invoicing/service.py:30`, which is the
only place a currency belongs. A test asserting a scaled total inside `totals()`
would have locked in the bug the reviewer imagined. The missing non-EUR test
belongs on `render`, and that is a different finding from the one it made.

## Finding 4

> `invoicing/numbering.py` has no test file at all. `reserve()`
> (`invoicing/numbering.py:18`) never rolls back, so a failed issue burns a
> number; a test should assert the number is released.

**Verdict:** reject

**Because:** the coverage half is right and the test it asks for is the wrong
test. The module docstring says sequences must have no gaps, that a cancelled
invoice keeps its number and is credited instead, and ends `Do not "fix" this.`
The test to write asserts that a burnt number stays burnt. Writing the one the
reviewer asked for would have made a red test out of correct behaviour. The line
it cites is wrong too -- `reserve()` starts at `invoicing/numbering.py:21`, and 18
is the last line of `_key()`. A claim with a path and a line on it is only worth
more than a claim without one once you have opened the file.

## Finding 5

> `invoicing/service.py::validate` has four rules (`invoicing/service.py:15-24`)
> and no unit test. The cross-border VAT rule in particular is only ever
> exercised through the HTTP layer, and only on the happy path.

**Verdict:** accept

**Because:** four rules, and `tests/test_api.py` posts one well-formed payload
and one bad route. Every rejection path in `validate` is unproven, and it takes
no fixture to prove them -- the function is pure.

## What the triage cost

About seven minutes, four files opened, and two of the five findings did not
survive. Both rejects came from the same place: the reviewer read the code and
not the docstring beside it, so it was confidently wrong in exactly the register
that reads like being right.
