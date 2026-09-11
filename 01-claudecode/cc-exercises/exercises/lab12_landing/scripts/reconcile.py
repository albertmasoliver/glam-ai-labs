#!/usr/bin/env python3
"""Nightly reconciliation. Run by cron; nobody has read it since 2024."""

import sys

from invoicing.adapters.ledger import format_entry
from invoicing.adapters.legacy_csv import load
from invoicing.models import Party
from invoicing.totals import totals

ISSUER = Party(code="ACME", name="Acme Iberia SL", vat_number="ESB00000000")


def main(path):
    mismatches = 0
    for invoice in load(path, ISSUER):
        entry = format_entry(invoice, totals(invoice))
        if entry["net"] + entry["tax"] <= 0:
            print(f"suspect {entry['ref']}: {entry}")
            mismatches += 1
    print(f"{mismatches} suspect entries")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
