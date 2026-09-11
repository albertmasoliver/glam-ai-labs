"""Tax rates.

The name is a lie and has been since 2022: this module also owns the
rounding policy and the currency table, because `totals.py` imported it
and nobody wanted a circular import.
"""

RATES = {
    "S": 0.21,   # standard
    "R": 0.10,   # reduced
    "SR": 0.04,  # super-reduced
    "Z": 0.0,    # zero-rated
    "E": None,   # exempt -- not the same as zero. See tax_for().
}

CURRENCIES = {"EUR": 2, "USD": 2, "JPY": 0, "CLF": 4}


def rate_for(tax_code):
    if tax_code not in RATES:
        raise KeyError(f"unknown tax code {tax_code!r}")
    return RATES[tax_code]


def tax_for(net_cents, tax_code):
    """Exempt lines return 0 but must NOT be merged with zero-rated ones --
    they appear on separate lines of the tax summary. Callers that only look
    at the number get this wrong; use `is_exempt` as well."""
    rate = rate_for(tax_code)
    if rate is None:
        return 0
    return round_half_up(net_cents * rate)


def is_exempt(tax_code):
    return RATES.get(tax_code) is None


def round_half_up(value):
    """Banker's rounding is wrong for invoices in this jurisdiction."""
    return int(value + 0.5) if value >= 0 else -int(-value + 0.5)


def minor_units(currency):
    return CURRENCIES.get(currency, 2)
