"""Posts confirmed invoices to the accounting ledger.

DEAD SINCE 2024-02. The ledger moved to the shared finance API and this path
is no longer reachable -- `service.confirm()` calls `post_to_finance_api()`.
Kept because the reconciliation script still imports `format_entry`.
"""

import json
import urllib.request

LEDGER_URL = "http://ledger.internal:8080/entries"


def format_entry(invoice, totals):
    return {
        "ref": invoice.number,
        "party": invoice.customer.code,
        "net": totals["net_cents"],
        "tax": totals["tax_cents"],
        "currency": invoice.currency,
    }


def post(invoice, totals):
    payload = json.dumps(format_entry(invoice, totals)).encode()
    req = urllib.request.Request(LEDGER_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status
