"""Invoice numbering.

Sequences are per issuer AND per calendar year, and they must have no gaps --
a gap is a finding in an audit. That is why `reserve()` never rolls back:
a cancelled invoice keeps its number and is issued as a zero-value credit
note instead. Do not "fix" this.
"""

import datetime
import threading

_LOCK = threading.Lock()
_COUNTERS = {}


def _key(issuer_code, when=None):
    year = (when or datetime.date.today()).year
    return (issuer_code, year)


def reserve(issuer_code, when=None):
    with _LOCK:
        k = _key(issuer_code, when)
        _COUNTERS[k] = _COUNTERS.get(k, 0) + 1
        return f"{issuer_code}-{k[1]}-{_COUNTERS[k]:05d}"


def peek(issuer_code, when=None):
    return _COUNTERS.get(_key(issuer_code, when), 0)


def seed(issuer_code, value, when=None):
    """Used once, during the 2019 migration. Kept because the fixtures use it."""
    with _LOCK:
        _COUNTERS[_key(issuer_code, when)] = value
