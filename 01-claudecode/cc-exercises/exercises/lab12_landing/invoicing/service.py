"""Application service. The entry point every caller should use."""

import json
import urllib.request

from . import config
from .rates import minor_units
from .totals import totals


class InvoiceError(Exception):
    pass


def validate(invoice):
    problems = []
    if not invoice.lines:
        problems.append("invoice has no lines")
    if invoice.customer.country != "ES" and not invoice.customer.vat_number:
        problems.append("cross-border customer needs a VAT number")
    if any(l.quantity <= 0 for l in invoice.lines):
        problems.append("line with non-positive quantity")
    if invoice.currency not in ("EUR", "USD", "JPY", "CLF"):
        problems.append(f"unsupported currency {invoice.currency}")
    return problems


def render(invoice):
    t = totals(invoice)
    scale = 10 ** minor_units(invoice.currency)
    return {
        "number": invoice.number,
        "customer": invoice.customer.name,
        "currency": invoice.currency,
        "net": t["net_cents"] / scale,
        "tax": t["tax_cents"] / scale,
        "gross": t["gross_cents"] / scale,
        "status": invoice.status,
    }


def post_to_finance_api(invoice, dry_run=None):
    if config.get("dry_run", dry_run):
        return {"posted": False, "reason": "dry_run"}
    payload = json.dumps(render(invoice)).encode()
    url = config.get("finance_api") + "/invoices"
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return {"posted": True, "status": resp.status}


def confirm(invoice, dry_run=None):
    problems = validate(invoice)
    if problems:
        raise InvoiceError("; ".join(problems))
    result = post_to_finance_api(invoice, dry_run=dry_run)
    if result.get("posted"):
        invoice.status = "confirmed"
    return result
