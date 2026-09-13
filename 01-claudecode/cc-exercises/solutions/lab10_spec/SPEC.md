# The slice

**One sentence:** show an itemised review of the cart -- one row per line, with
shipping and total as separate figures -- before the buyer reaches payment.

**Left in the backlog:** progress indicator, save cart for later, discount codes,
email confirmation, analytics tracking, multiple payment methods, mobile responsive
design.

## Postconditions

What must be true after, each with the test that proves it.

- The review shows one row per cart line, in cart order.
  `tests/test_review.py::test_one_row_per_cart_line`
- The rows the buyer reads add up to the subtotal the buyer reads.
  `tests/test_review.py::test_printed_lines_sum_to_the_printed_subtotal`
- Shipping appears as its own figure and the total is the sum of the two.
  `tests/test_review.py::test_shipping_is_shown_as_its_own_figure`
- Reviewing an empty cart is refused rather than shown as a zero order.
  `tests/test_review.py::test_an_empty_cart_has_nothing_to_review`

## Preconditions

What must already be true for this to make sense. Prose; nothing to run.

- The cart is priced by `orders.cart`, and it is the only thing that prices.
- A destination is known by the time the review is built, because shipping depends
  on it.

## Invariants

What must not change. These are the existing tests you are promising to keep green.

- Rounding stays at the line, so finance keeps reconciling against the printed rows.
  `tests/test_cart.py::test_line_total_rounds_at_the_line`
- The subtotal remains the sum of the printed lines and not a separate calculation.
  `tests/test_cart.py::test_subtotal_is_the_sum_of_the_printed_lines`
- The free-shipping threshold is untouched.
  `tests/test_cart.py::test_shipping_is_free_over_the_threshold`

## Negative criteria

What must explicitly not happen. Prose.

- No new arithmetic in the review. Every figure is read from `cart`.
- No change to any price, threshold or rounding rule.
- No payment code. This slice stops at the page before it.
- No new dependency.
