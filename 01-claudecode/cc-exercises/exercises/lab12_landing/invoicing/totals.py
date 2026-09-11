"""Invoice arithmetic. The only module allowed to decide what an invoice costs."""

from .rates import is_exempt, rate_for, round_half_up, tax_for


def tax_summary(invoice):
    """Group lines by tax treatment. Exempt and zero-rated stay separate."""
    buckets = {}
    for line in invoice.lines:
        key = ("E", None) if is_exempt(line.tax_code) else (line.tax_code, rate_for(line.tax_code))
        entry = buckets.setdefault(key, {"net_cents": 0, "tax_cents": 0})
        entry["net_cents"] += line.net_cents
    for (code, _rate), entry in buckets.items():
        entry["tax_cents"] = tax_for(entry["net_cents"], code)
    return buckets


def totals(invoice):
    summary = tax_summary(invoice)
    net = sum(e["net_cents"] for e in summary.values())
    tax = sum(e["tax_cents"] for e in summary.values())
    return {"net_cents": net, "tax_cents": tax, "gross_cents": net + tax}


def apply_discount(invoice, percent):
    """Discount is applied per line BEFORE tax, never to the gross.

    Getting this backwards changes the tax owed, which is why it lives here
    and not in the API layer.
    """
    if not 0 <= percent <= 100:
        raise ValueError("discount out of range")
    for line in invoice.lines:
        line.unit_price_cents = round_half_up(line.unit_price_cents * (1 - percent / 100))
    return invoice
