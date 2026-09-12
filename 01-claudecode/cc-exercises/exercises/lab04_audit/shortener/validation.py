"""Validation helpers -- the pattern every handler in this app follows.

A validator returns None when the value is acceptable, or a short error
string when it is not. Handlers turn that string into a 400.
"""

MAX_URL = 2048


def validate_code(code):
    if not isinstance(code, str) or len(code) != 7:
        return "code must be 7 characters"
    return None
