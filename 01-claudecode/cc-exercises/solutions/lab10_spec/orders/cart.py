"""A cart and its totals.

NOTE(pn, 2025-08): line totals are rounded to the cent at the line, not at the
end. Finance reconciles against the line, so the sum of the printed lines has
to equal the printed total exactly -- do not move the rounding.
"""


class CartError(ValueError):
    """Raised when a cart cannot be priced."""


def line_total(item):
    if item["quantity"] < 1:
        raise CartError("a line needs at least one of something")
    return round(item["unit_price"] * item["quantity"], 2)


def subtotal(items):
    return round(sum(line_total(item) for item in items), 2)


def shipping(items, destination):
    if not items:
        return 0.0
    return 0.0 if subtotal(items) >= 50 else (4.95 if destination == "domestic" else 12.50)


def total(items, destination="domestic"):
    return round(subtotal(items) + shipping(items, destination), 2)
