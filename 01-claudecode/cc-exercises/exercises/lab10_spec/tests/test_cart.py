import pytest

from orders.cart import CartError, line_total, shipping, subtotal, total

BOOK = {"sku": "bk-1", "name": "Solaris", "unit_price": 12.99, "quantity": 2}
PEN = {"sku": "pn-9", "name": "Pen", "unit_price": 1.25, "quantity": 3}
NAIL = {"sku": "nl-2", "name": "Nail", "unit_price": 0.125, "quantity": 1}


def test_line_total_rounds_at_the_line():
    assert line_total(BOOK) == 25.98


def test_a_line_needs_a_quantity():
    with pytest.raises(CartError):
        line_total({"unit_price": 1.0, "quantity": 0})


def test_subtotal_is_the_sum_of_the_printed_lines():
    """Three half-cent lines. Round at the end instead of at the line and this
    is off by two cents -- which is the whole reason the rule exists."""
    nails = [dict(NAIL), dict(NAIL), dict(NAIL)]
    assert subtotal(nails) == round(sum(line_total(n) for n in nails), 2)


def test_small_orders_pay_domestic_shipping():
    assert shipping([PEN], "domestic") == 4.95


def test_shipping_is_free_over_the_threshold():
    assert shipping([{"unit_price": 50.0, "quantity": 1}], "domestic") == 0.0


def test_total_adds_shipping_to_the_subtotal():
    assert total([PEN]) == round(subtotal([PEN]) + 4.95, 2)
