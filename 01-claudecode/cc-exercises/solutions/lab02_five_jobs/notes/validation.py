"""Validation helpers -- the pattern every handler in this app follows.

A validator returns None when the value is acceptable, or a short error
string when it is not. Handlers turn that string into a 400 and never
build the message themselves.
"""

MAX_BODY = 10_000


def validate_body(body):
    if body is not None and len(body) > MAX_BODY:
        return "body is too long"
    return None


def validate_title(title):
    if title is None or not str(title).strip():
        return "title is required"
    return None
