"""Domain objects.

NOTE(mk, 2023-04): these were dataclasses until the CSV importer needed
partially-populated instances. Do not add required fields without checking
`adapters/legacy_csv.py`.
"""


class Party:
    def __init__(self, code, name, vat_number=None, country="ES"):
        self.code = code
        self.name = name
        self.vat_number = vat_number
        self.country = country

    def __repr__(self):
        return f"<Party {self.code} {self.name!r}>"


class LineItem:
    def __init__(self, description, quantity, unit_price_cents, tax_code="S"):
        self.description = description
        self.quantity = quantity
        self.unit_price_cents = unit_price_cents
        self.tax_code = tax_code

    @property
    def net_cents(self):
        return self.quantity * self.unit_price_cents


class Invoice:
    def __init__(self, number, issuer, customer, lines=None, currency="EUR"):
        self.number = number
        self.issuer = issuer
        self.customer = customer
        self.lines = lines or []
        self.currency = currency
        self.status = "draft"

    @property
    def net_cents(self):
        return sum(l.net_cents for l in self.lines)
