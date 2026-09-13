import pytest

from orders.cart import CartError
from orders.review import review

BOOK = {"sku": "bk-1", "name": "Solaris", "unit_price": 12.99, "quantity": 2}
PEN = {"sku": "pn-9", "name": "Pen", "unit_price": 1.25, "quantity": 3}


def test_one_row_per_cart_line():
    assert len(review([BOOK, PEN])["lines"]) == 2


def test_printed_lines_sum_to_the_printed_subtotal():
    seen = review([BOOK, PEN])
    assert round(sum(row["line_total"] for row in seen["lines"]), 2) == seen["subtotal"]


def test_shipping_is_shown_as_its_own_figure():
    seen = review([PEN])
    assert seen["shipping"] == 4.95
    assert seen["total"] == round(seen["subtotal"] + seen["shipping"], 2)


def test_an_empty_cart_has_nothing_to_review():
    with pytest.raises(CartError):
        review([])
