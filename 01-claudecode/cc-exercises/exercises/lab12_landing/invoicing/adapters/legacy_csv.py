"""Importer for the 2019 billing export.

The upstream system is gone; only the files remain. Columns are positional
because the header row was optional and about a third of the archive omits it.
"""

import csv

from ..models import Invoice, LineItem, Party

COL_NUMBER, COL_CUSTOMER, COL_DESC, COL_QTY, COL_PRICE, COL_TAX = range(6)


def _looks_like_header(row):
    return row and row[COL_NUMBER].strip().lower() in {"number", "invoice", "invoice_no"}


def load(path, issuer):
    invoices = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.reader(f)):
            if i == 0 and _looks_like_header(row):
                continue
            if not row or not row[COL_NUMBER].strip():
                continue
            number = row[COL_NUMBER].strip()
            inv = invoices.get(number)
            if inv is None:
                # Customer name only -- the archive has no codes or VAT numbers.
                customer = Party(code=f"LEGACY-{number}", name=row[COL_CUSTOMER].strip())
                inv = Invoice(number=number, issuer=issuer, customer=customer)
                invoices[number] = inv
            inv.lines.append(LineItem(
                description=row[COL_DESC].strip(),
                quantity=int(row[COL_QTY]),
                unit_price_cents=int(round(float(row[COL_PRICE]) * 100)),
                tax_code=(row[COL_TAX].strip() or "S"),
            ))
    return list(invoices.values())
