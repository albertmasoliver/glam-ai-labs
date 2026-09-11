from invoicing.models import Invoice, LineItem, Party
from invoicing.totals import totals

ISSUER = Party("ACME", "Acme Iberia SL", "ESB00000000")
CUSTOMER = Party("C1", "Cliente Uno")


def _invoice(*lines):
    return Invoice("F-001", ISSUER, CUSTOMER, list(lines))


def test_single_standard_line():
    inv = _invoice(LineItem("widget", 2, 1000, "S"))
    assert totals(inv) == {"net_cents": 2000, "tax_cents": 420, "gross_cents": 2420}


def test_mixed_rates_are_grouped():
    inv = _invoice(LineItem("widget", 1, 1000, "S"), LineItem("book", 1, 1000, "SR"))
    t = totals(inv)
    assert t["net_cents"] == 2000
    assert t["tax_cents"] == 210 + 40
