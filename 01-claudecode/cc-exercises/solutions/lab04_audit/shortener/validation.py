"""Validation helpers -- the pattern every handler in this app follows.

A validator returns None when the value is acceptable, or a short error
string when it is not. Handlers turn that string into a 400.
"""

MAX_URL = 2048


def validate_code(code):
    if not isinstance(code, str) or len(code) != 7:
        return "code must be 7 characters"
    return None


def validate_url(url):
    """A url must be a string with something in it.

    Typed rather than truthy on purpose: the rule is "a non-empty string",
    and `not url` would also reject 0 and False while letting 123 through
    to crash on .strip().
    """
    if not isinstance(url, str):
        return "url must be a string"
    if not url.strip():
        return "url required"
    if len(url) > MAX_URL:
        return "url is too long"
    return None
