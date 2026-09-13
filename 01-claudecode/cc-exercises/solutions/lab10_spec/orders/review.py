"""The itemised breakdown a buyer sees before paying.

Reads the cart and reports it. It does not price anything itself: every figure
here comes from `cart`, so the review cannot drift away from what is charged.
That is the whole reason this module has no arithmetic in it.
"""

from .cart import CartError, line_total, shipping, subtotal, total


def review(items, destination="domestic"):
    if not items:
        raise CartError("there is nothing to review")
    lines = [
        {
            "sku": item["sku"],
            "name": item["name"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "line_total": line_total(item),
        }
        for item in items
    ]
    return {
        "lines": lines,
        "subtotal": subtotal(items),
        "shipping": shipping(items, destination),
        "total": total(items, destination),
    }
